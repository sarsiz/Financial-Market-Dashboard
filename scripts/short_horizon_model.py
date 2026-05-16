#!/usr/bin/env python3
"""
Short-Horizon Directional Model — Financial Board

A transparent, hand-crafted estimator for 1–10 day expected return on a single
ticker. No ML training; every coefficient is documented and reproducible from
log-returns alone. Designed for honest live + offline evaluation.

Why this exists (vs. the existing classic_score + modern_score blend):
- Risk-adjusted momentum: scale momentum by realized vol (Sharpe-style) so we
  don't predict the same drift for a calm stock and a stressed one.
- MACD histogram acceleration: delta of histogram (turn detection) beats raw
  crossover for short horizons — crossover lags by ~3 bars.
- Volatility-regime gating: when realized vol is expanding, dampen the
  directional prediction (vol expansion = noise rising, signal-to-noise falling).
- Calibrated cone: confidence band = vol_20 * sqrt(h), not a heuristic clamp.

Public API:
- predict(closes, horizon=5)         → ShortHorizonForecast
- walk_forward_backtest(closes, ...) → metrics dict
- generate_garch_series(...)         → synthetic closes for offline testing
"""
from __future__ import annotations

import json
import math
import random
import statistics
from dataclasses import dataclass, asdict
from typing import Sequence


# ─────────────────────────────────────────────────────────────────────────────
# Primitive indicators (replicated locally to keep this module standalone — the
# server.py versions are not imported because we may want to call this script
# independently for offline evaluation).
# ─────────────────────────────────────────────────────────────────────────────

def _clamp(value: float, low: float, high: float) -> float:
  return max(low, min(high, value))


def _safe_div(a: float, b: float, default: float = 0.0) -> float:
  return a / b if b not in (0, 0.0) else default


def _log_returns(closes: Sequence[float]) -> list[float]:
  out = []
  for i in range(1, len(closes)):
    if closes[i - 1] > 0 and closes[i] > 0:
      out.append(math.log(closes[i] / closes[i - 1]))
  return out


def _ema(series: Sequence[float], period: int) -> list[float]:
  if not series:
    return []
  k = 2.0 / (period + 1)
  out = [series[0]]
  for x in series[1:]:
    out.append(x * k + out[-1] * (1 - k))
  return out


def _macd_hist(closes: Sequence[float], fast: int = 12, slow: int = 26, sig: int = 9) -> list[float]:
  """Returns the MACD histogram series (aligned to original length when possible)."""
  if len(closes) < slow + sig:
    return [0.0] * len(closes)
  fast_ema = _ema(closes, fast)
  slow_ema = _ema(closes, slow)
  macd_line = [f - s for f, s in zip(fast_ema, slow_ema)]
  sig_line = _ema(macd_line, sig)
  return [m - s for m, s in zip(macd_line, sig_line)]


def _rsi(closes: Sequence[float], period: int = 14) -> float:
  if len(closes) < period + 1:
    return 50.0
  deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
  gains = [max(d, 0.0) for d in deltas]
  losses = [max(-d, 0.0) for d in deltas]
  avg_g = sum(gains[:period]) / period
  avg_l = sum(losses[:period]) / period
  for i in range(period, len(gains)):
    avg_g = (avg_g * (period - 1) + gains[i]) / period
    avg_l = (avg_l * (period - 1) + losses[i]) / period
  if avg_l == 0:
    return 100.0 if avg_g > 0 else 50.0
  rs = avg_g / avg_l
  return 100.0 - 100.0 / (1.0 + rs)


def _bollinger_position(closes: Sequence[float], period: int = 20, n_std: float = 2.0) -> float:
  if len(closes) < period:
    return 0.5
  window = closes[-period:]
  mid = statistics.fmean(window)
  sd = statistics.pstdev(window)
  if sd == 0:
    return 0.5
  upper = mid + n_std * sd
  lower = mid - n_std * sd
  return _clamp((closes[-1] - lower) / (upper - lower), 0.0, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ShortHorizonForecast:
  horizon: int
  expected_return_pct: float   # signed % over the horizon
  per_day_drift_pct: float     # signed % per day
  realized_vol_daily: float    # daily stdev of log-returns over last 20 bars
  cone_low_pct: float          # -1 sigma cone, % over horizon
  cone_high_pct: float         # +1 sigma cone, % over horizon
  direction: str               # 'Bullish' | 'Bearish' | 'Neutral'
  confidence: float            # 0..100, calibrated from skill_score (or sample-only)
  features: dict               # raw feature values for explainability
  notes: list[str]             # short text bullets for the methodology card


# Feature weights — each one is a coefficient on a *standardized* signal value.
# The product is then in units of "fraction per day" (log return).
WEIGHTS = {
  "risk_adj_mom":     0.45,   # mom_5 / vol_20  — primary trend
  "mean_reversion_z": 0.20,   # negative z of close vs 20-bar mean
  "macd_accel":       0.15,   # ΔMACD histogram, vol-normalized
  "boll_off_mid":     0.10,   # -1 * (band_pos - 0.5), mean reversion within bands
  "rsi_extreme":      0.10,   # only fires when |rsi-50| > 15
}
# Cap on the absolute per-day predicted drift, in raw log-return units. With
# vol_20 ≈ 1.5%/day, this cap at 1.2% prevents the model from claiming a 30%
# directional move over 10 days even for very stretched signals.
PER_DAY_CAP = 0.012


def _features(closes: Sequence[float]) -> dict:
  """Compute the feature vector at the END of `closes`. All values are scaled
  to roughly comparable units; the model layer combines them linearly."""
  if len(closes) < 25:
    return {"insufficient_history": True}

  log_r = _log_returns(closes)
  r_5 = log_r[-5:]
  r_20 = log_r[-20:]

  mean_5 = statistics.fmean(r_5) if r_5 else 0.0
  mean_20 = statistics.fmean(r_20) if r_20 else 0.0
  vol_5 = statistics.pstdev(r_5) if len(r_5) >= 2 else 0.0
  vol_20 = statistics.pstdev(r_20) if len(r_20) >= 2 else 0.0

  # 1) Risk-adjusted momentum: Sharpe-style. Sign of recent drift, scaled.
  risk_adj_mom = _safe_div(mean_5, vol_20) if vol_20 > 0 else 0.0
  # Multiply back by vol_20 to recover a "drift in units of log-return" value
  risk_adj_mom_drift = _clamp(risk_adj_mom * vol_20, -PER_DAY_CAP * 2, PER_DAY_CAP * 2)

  # 2) Mean-reversion z-score: close vs trailing 20-day mean.
  window_20 = closes[-20:]
  px_mean = statistics.fmean(window_20)
  px_sd = statistics.pstdev(window_20)
  mr_z = _safe_div(closes[-1] - px_mean, px_sd) if px_sd > 0 else 0.0
  # Negative because high z → revert down. Cap at ±3 σ, scale to 1.5%/day max.
  mr_drift = _clamp(-mr_z, -3.0, 3.0) * 0.005

  # 3) MACD histogram acceleration: Δ histogram / ATR_pct, signed.
  hist = _macd_hist(closes)
  hist_now = hist[-1] if hist else 0.0
  hist_prev = hist[-2] if len(hist) >= 2 else 0.0
  # ATR-ish denominator: 14-bar mean absolute return * price
  abs_r = [abs(x) for x in log_r[-14:]] or [0.001]
  atr_proxy = statistics.fmean(abs_r) * closes[-1]
  macd_accel = _safe_div(hist_now - hist_prev, atr_proxy)
  macd_accel_drift = _clamp(macd_accel, -2.0, 2.0) * 0.006

  # 4) Bollinger position vs midline. Position = 0.5 means at midline.
  boll_pos = _bollinger_position(closes)
  boll_drift = -(boll_pos - 0.5) * 0.010   # ±0.5 % at the bands

  # 5) RSI extreme — only contributes when RSI is past the 35/65 zones.
  rsi_val = _rsi(closes)
  if abs(rsi_val - 50) > 15:
    rsi_drift = -(rsi_val - 50) / 50.0 * 0.012   # RSI 80 → -0.72 % drift
  else:
    rsi_drift = 0.0

  # Volatility-regime gate: when vol is expanding, signal-to-noise falls. We
  # multiplicatively dampen the final drift. Calm regime → gate = 1.0.
  vol_expansion = vol_5 - vol_20
  vol_gate = _clamp(1.0 - 2.0 * max(vol_expansion, 0.0) / max(vol_20, 1e-9), 0.30, 1.0)

  return {
    "log_returns": log_r,
    "vol_5": vol_5,
    "vol_20": vol_20,
    "risk_adj_mom_drift": risk_adj_mom_drift,
    "mr_drift": mr_drift,
    "macd_accel_drift": macd_accel_drift,
    "boll_drift": boll_drift,
    "rsi_drift": rsi_drift,
    "vol_gate": vol_gate,
    "rsi": rsi_val,
    "boll_pos": boll_pos,
    "mr_z": mr_z,
    "macd_hist": hist_now,
    "macd_hist_delta": hist_now - hist_prev,
    "insufficient_history": False,
  }


def predict(closes: Sequence[float], horizon: int = 5) -> ShortHorizonForecast:
  horizon = max(1, min(int(horizon), 10))
  feats = _features(closes)
  if feats.get("insufficient_history"):
    return ShortHorizonForecast(
      horizon=horizon, expected_return_pct=0.0, per_day_drift_pct=0.0,
      realized_vol_daily=0.0, cone_low_pct=0.0, cone_high_pct=0.0,
      direction="Neutral", confidence=15.0, features={},
      notes=["Insufficient history (<25 bars). Returning a flat baseline."],
    )

  per_day_drift = (
    WEIGHTS["risk_adj_mom"]     * feats["risk_adj_mom_drift"]
    + WEIGHTS["mean_reversion_z"] * feats["mr_drift"]
    + WEIGHTS["macd_accel"]       * feats["macd_accel_drift"]
    + WEIGHTS["boll_off_mid"]     * feats["boll_drift"]
    + WEIGHTS["rsi_extreme"]      * feats["rsi_drift"]
  ) * feats["vol_gate"]

  per_day_drift = _clamp(per_day_drift, -PER_DAY_CAP, PER_DAY_CAP)

  # Convert log-return drift to % over horizon. exp(h*r) - 1.
  expected_log_return_h = per_day_drift * horizon
  expected_return_pct = (math.exp(expected_log_return_h) - 1.0) * 100.0

  # ±1σ cone uses sqrt(h) vol scaling.
  vol_h = feats["vol_20"] * math.sqrt(horizon)
  cone_low_pct  = (math.exp(expected_log_return_h - vol_h) - 1.0) * 100.0
  cone_high_pct = (math.exp(expected_log_return_h + vol_h) - 1.0) * 100.0

  # Direction band: anything inside ±0.2 % over horizon is "Neutral".
  if expected_return_pct > 0.2:
    direction = "Bullish"
  elif expected_return_pct < -0.2:
    direction = "Bearish"
  else:
    direction = "Neutral"

  # Confidence: scale by signal-to-noise ratio of the prediction vs the cone width.
  # A drift of 1% over a 3% cone is weak; a drift of 1% over a 0.5% cone is strong.
  snr = abs(expected_return_pct) / max(abs(cone_high_pct - cone_low_pct) / 2, 0.001)
  confidence = _clamp(35 + 45 * math.tanh(snr * 1.2) + 20 * feats["vol_gate"], 20, 90)

  notes = []
  if feats["vol_gate"] < 0.8:
    notes.append(f"Volatility expanding — drift gated to {feats['vol_gate']:.2f}×.")
  if abs(feats["mr_z"]) > 2.0:
    notes.append(f"Price stretched {feats['mr_z']:+.1f}σ from 20-bar mean.")
  if feats["rsi"] < 30 or feats["rsi"] > 70:
    notes.append(f"RSI extreme at {feats['rsi']:.0f}.")
  if abs(feats["macd_hist_delta"]) > 0:
    direction_word = "improving" if feats["macd_hist_delta"] > 0 else "deteriorating"
    notes.append(f"MACD momentum {direction_word}.")
  if not notes:
    notes.append("All factors in their neutral band.")

  # Drop the heavy 'log_returns' array from features before returning.
  exposed_features = {k: v for k, v in feats.items() if k != "log_returns"}
  return ShortHorizonForecast(
    horizon=horizon,
    expected_return_pct=round(expected_return_pct, 3),
    per_day_drift_pct=round((math.exp(per_day_drift) - 1.0) * 100.0, 4),
    realized_vol_daily=round(feats["vol_20"] * 100.0, 4),
    cone_low_pct=round(cone_low_pct, 3),
    cone_high_pct=round(cone_high_pct, 3),
    direction=direction,
    confidence=round(confidence, 1),
    features={k: (round(v, 6) if isinstance(v, float) else v) for k, v in exposed_features.items()},
    notes=notes,
  )


# ─────────────────────────────────────────────────────────────────────────────
# Walk-forward backtest harness
# ─────────────────────────────────────────────────────────────────────────────

def walk_forward_backtest(
  closes: Sequence[float],
  horizon: int = 5,
  predict_fn=None,
  min_warmup: int = 40,
) -> dict:
  """Walk forward through `closes`. At each step t, predict the next `horizon`
  days using closes[:t]. Compare predicted % to realized closes[t+horizon-1].
  Returns MAE (%), median APE (%), directional hit rate (%), bias (pp),
  residual std (pp), sample count, and IC (rank correlation of predicted vs
  realized return)."""
  predict_fn = predict_fn or predict
  errs, hits, residuals, preds, actuals = [], [], [], [], []
  for t in range(min_warmup, len(closes) - horizon):
    window = closes[:t]
    fcst = predict_fn(window, horizon=horizon)
    predicted = fcst.expected_return_pct if hasattr(fcst, "expected_return_pct") else fcst
    current = window[-1]
    future = closes[t + horizon - 1]
    actual = (future / current - 1.0) * 100.0
    errs.append(abs(predicted - actual))
    hits.append(1 if (predicted >= 0) == (actual >= 0) else 0)
    residuals.append(predicted - actual)
    preds.append(predicted)
    actuals.append(actual)

  if not errs:
    return {"mae_pp": 0.0, "median_ape_pp": 0.0, "hit_rate_pct": 0.0,
            "bias_pp": 0.0, "residual_std_pp": 0.0, "samples": 0, "ic": 0.0}

  # Information Coefficient: Pearson correlation of predicted vs actual.
  if len(preds) >= 3:
    mp, ma = statistics.fmean(preds), statistics.fmean(actuals)
    num = sum((p - mp) * (a - ma) for p, a in zip(preds, actuals))
    denom = math.sqrt(sum((p - mp) ** 2 for p in preds) * sum((a - ma) ** 2 for a in actuals))
    ic = num / denom if denom else 0.0
  else:
    ic = 0.0

  return {
    "mae_pp":          round(statistics.fmean(errs), 3),
    "median_ape_pp":   round(statistics.median(errs), 3),
    "hit_rate_pct":    round(statistics.fmean(hits) * 100, 2),
    "bias_pp":         round(statistics.fmean(residuals), 4),
    "residual_std_pp": round(statistics.pstdev(residuals) if len(residuals) >= 2 else 0.0, 3),
    "samples":         len(errs),
    "ic":              round(ic, 4),
  }


# ─────────────────────────────────────────────────────────────────────────────
# Baselines for fair comparison
# ─────────────────────────────────────────────────────────────────────────────

class _NaiveDriftForecast:
  """Predicts the same %/day as the trailing-20 mean. No volatility gating, no
  cross-feature signal. Useful as a 'random walk + drift' baseline."""
  def __init__(self, expected_return_pct: float):
    self.expected_return_pct = expected_return_pct


def predict_naive_drift(closes: Sequence[float], horizon: int = 5) -> _NaiveDriftForecast:
  log_r = _log_returns(closes)
  if len(log_r) < 20:
    return _NaiveDriftForecast(0.0)
  mean_20 = statistics.fmean(log_r[-20:])
  exp_h = (math.exp(mean_20 * horizon) - 1.0) * 100.0
  return _NaiveDriftForecast(exp_h)


class _FlatForecast:
  expected_return_pct = 0.0


def predict_flat(closes: Sequence[float], horizon: int = 5) -> _FlatForecast:
  return _FlatForecast()


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic data generator for offline methodology tests
# ─────────────────────────────────────────────────────────────────────────────

def generate_garch_series(
  n: int = 600,
  s0: float = 100.0,
  mu_per_day: float = 0.0005,
  base_vol: float = 0.013,
  vol_persistence: float = 0.92,
  vol_shock: float = 0.10,
  regime_breaks: list[tuple[int, float]] | None = None,
  seed: int = 42,
) -> list[float]:
  """GARCH(1,1)-style stochastic vol price series with optional regime shifts.
  Each tuple in regime_breaks is (start_index, new_mu_per_day)."""
  rng = random.Random(seed)
  mu = mu_per_day
  vol = base_vol
  closes = [s0]
  for t in range(1, n):
    if regime_breaks:
      for break_t, new_mu in regime_breaks:
        if t == break_t:
          mu = new_mu
    z = rng.gauss(0.0, 1.0)
    # GARCH-ish vol update: contract toward base_vol with persistence, add shock
    vol = math.sqrt(vol_persistence * vol * vol
                    + (1 - vol_persistence) * base_vol * base_vol
                    + vol_shock * (z * z * base_vol * base_vol * 0.05))
    r = mu + vol * z
    closes.append(closes[-1] * math.exp(r))
  return closes


# ─────────────────────────────────────────────────────────────────────────────
# Offline evaluation runner — produces a metrics JSON the dashboard can read
# ─────────────────────────────────────────────────────────────────────────────

def run_offline_evaluation() -> dict:
  """Compare new model vs naive-drift vs flat baseline across multiple
  synthetic regimes and horizons. Returns a JSON-serializable summary."""

  scenarios = [
    ("trend_up",   {"mu_per_day": 0.0012, "base_vol": 0.011}),
    ("trend_down", {"mu_per_day": -0.0008, "base_vol": 0.012}),
    ("calm_drift", {"mu_per_day": 0.0003, "base_vol": 0.008}),
    ("choppy",     {"mu_per_day": 0.0000, "base_vol": 0.020}),
    ("regime_flip", {
      "mu_per_day": 0.0010, "base_vol": 0.012,
      "regime_breaks": [(300, -0.0010)],
    }),
  ]
  horizons = [1, 5, 10]

  results = {}
  for name, params in scenarios:
    seed_base = abs(hash(name)) % 10_000
    per_scenario = {}
    # Average over 8 seeds to reduce variance.
    for h in horizons:
      maes_new, maes_naive, maes_flat = [], [], []
      hits_new, hits_naive = [], []
      ics_new, ics_naive = [], []
      for s in range(8):
        closes = generate_garch_series(n=600, seed=seed_base + s, **params)
        r_new   = walk_forward_backtest(closes, horizon=h, predict_fn=predict)
        r_naive = walk_forward_backtest(closes, horizon=h, predict_fn=predict_naive_drift)
        r_flat  = walk_forward_backtest(closes, horizon=h, predict_fn=predict_flat)
        maes_new.append(r_new["mae_pp"])
        maes_naive.append(r_naive["mae_pp"])
        maes_flat.append(r_flat["mae_pp"])
        hits_new.append(r_new["hit_rate_pct"])
        hits_naive.append(r_naive["hit_rate_pct"])
        ics_new.append(r_new["ic"])
        ics_naive.append(r_naive["ic"])
      per_scenario[f"h={h}"] = {
        "mae_pp": {"new": round(statistics.fmean(maes_new), 3),
                   "naive_drift": round(statistics.fmean(maes_naive), 3),
                   "flat": round(statistics.fmean(maes_flat), 3)},
        "hit_rate_pct": {"new": round(statistics.fmean(hits_new), 2),
                         "naive_drift": round(statistics.fmean(hits_naive), 2)},
        "ic": {"new": round(statistics.fmean(ics_new), 3),
               "naive_drift": round(statistics.fmean(ics_naive), 3)},
      }
    results[name] = per_scenario

  return {
    "horizons_tested": horizons,
    "scenarios_tested": [name for name, _ in scenarios],
    "seeds_per_scenario": 8,
    "samples_per_seed": 600,
    "model_weights": WEIGHTS,
    "per_scenario": results,
  }


if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--out", default="vault/market-map/short_horizon_eval.json")
  args = parser.parse_args()
  summary = run_offline_evaluation()
  import os
  os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
  with open(args.out, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
  print(json.dumps(summary, indent=2))
