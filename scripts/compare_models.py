#!/usr/bin/env python3
"""
Honest head-to-head: existing build_forecast vs new short-horizon model vs
naive-drift vs flat baseline. Runs on synthetic GARCH series with known
parameters and reports the same walk-forward metrics for each.

Output: vault/market-map/short_horizon_compare.json (gitignored).
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import server as fb_server  # type: ignore
import short_horizon_model as shm  # type: ignore


def existing_model_predict(closes, horizon: int = 5):
  """Wrap build_forecast so it returns the same .expected_return_pct shape as
  the new model. Window-time quote pattern from feedback_backtest_anchor."""
  if len(closes) < 25:
    class Z: expected_return_pct = 0.0
    return Z()
  fake_quote = {
    "regularMarketPrice": closes[-1],
    "regularMarketPreviousClose": closes[-2],
    "regularMarketChangePercent": (closes[-1] / closes[-2] - 1) * 100,
    "fullExchangeName": "Synthetic",
    "trailingPE": 20.0,
    "marketCap": 1_000_000_000,
  }
  fake_summary = {"_volumeHistory": []}
  try:
    f = fb_server.build_forecast("SYNTH", fake_quote, fake_summary, list(closes),
                                 stress="base", horizon=horizon, news_count=0)
    er = float(f.get("expectedReturn") or 0.0)
    class P:
      expected_return_pct = er
    return P()
  except Exception as e:
    class P: expected_return_pct = 0.0
    return P()


def main():
  scenarios = [
    ("trend_up",    {"mu_per_day": 0.0012, "base_vol": 0.011}),
    ("trend_down",  {"mu_per_day": -0.0008, "base_vol": 0.012}),
    ("calm_drift",  {"mu_per_day": 0.0003, "base_vol": 0.008}),
    ("choppy",      {"mu_per_day": 0.0000, "base_vol": 0.020}),
    ("regime_flip", {"mu_per_day": 0.0010, "base_vol": 0.012,
                     "regime_breaks": [(300, -0.0010)]}),
  ]
  horizons = [1, 5, 10]

  results = {}
  seeds = 8
  for name, params in scenarios:
    seed_base = abs(hash(name)) % 10_000
    per_h = {}
    for h in horizons:
      m_new, m_old, m_naive, m_flat = [], [], [], []
      hit_new, hit_old = [], []
      ic_new, ic_old = [], []
      for s in range(seeds):
        closes = shm.generate_garch_series(n=600, seed=seed_base + s, **params)
        r_new   = shm.walk_forward_backtest(closes, horizon=h, predict_fn=shm.predict)
        r_old   = shm.walk_forward_backtest(closes, horizon=h, predict_fn=existing_model_predict)
        r_naive = shm.walk_forward_backtest(closes, horizon=h, predict_fn=shm.predict_naive_drift)
        r_flat  = shm.walk_forward_backtest(closes, horizon=h, predict_fn=shm.predict_flat)
        m_new.append(r_new["mae_pp"]);   m_old.append(r_old["mae_pp"])
        m_naive.append(r_naive["mae_pp"]); m_flat.append(r_flat["mae_pp"])
        hit_new.append(r_new["hit_rate_pct"]); hit_old.append(r_old["hit_rate_pct"])
        ic_new.append(r_new["ic"]); ic_old.append(r_old["ic"])
      per_h[f"h={h}"] = {
        "mae_pp": {
          "new_model":        round(statistics.fmean(m_new), 3),
          "existing_model":   round(statistics.fmean(m_old), 3),
          "naive_drift":      round(statistics.fmean(m_naive), 3),
          "flat":             round(statistics.fmean(m_flat), 3),
        },
        "hit_rate_pct": {
          "new_model":      round(statistics.fmean(hit_new), 2),
          "existing_model": round(statistics.fmean(hit_old), 2),
        },
        "ic": {
          "new_model":      round(statistics.fmean(ic_new), 3),
          "existing_model": round(statistics.fmean(ic_old), 3),
        },
      }
    results[name] = per_h

  summary = {"per_scenario": results, "seeds_per_scenario": seeds, "samples_per_seed": 600}
  os.makedirs("vault/market-map", exist_ok=True)
  with open("vault/market-map/short_horizon_compare.json", "w") as f:
    json.dump(summary, f, indent=2)

  # Pretty print
  print(f'{"scenario":13s} {"h":>3s} {"mae_new":>8s} {"mae_old":>8s} {"mae_naive":>9s} {"mae_flat":>8s} {"hit_new":>8s} {"hit_old":>8s} {"ic_new":>7s} {"ic_old":>7s}')
  for sc, hs in results.items():
    for h, row in hs.items():
      print(f'{sc:13s} {h:>3s} '
            f'{row["mae_pp"]["new_model"]:>8.3f} '
            f'{row["mae_pp"]["existing_model"]:>8.3f} '
            f'{row["mae_pp"]["naive_drift"]:>9.3f} '
            f'{row["mae_pp"]["flat"]:>8.3f} '
            f'{row["hit_rate_pct"]["new_model"]:>8.2f} '
            f'{row["hit_rate_pct"]["existing_model"]:>8.2f} '
            f'{row["ic"]["new_model"]:>7.3f} '
            f'{row["ic"]["existing_model"]:>7.3f}')


if __name__ == "__main__":
  main()
