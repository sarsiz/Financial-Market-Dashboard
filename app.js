const STORAGE_KEYS = {
  watchlist: "financial-board-fullstack-watchlist",
  activeTicker: "financial-board-fullstack-active",
  recentTickers: "financial-board-recent-tickers",
  chartRange: "financial-board-chart-range",
  chartFeatures: "financial-board-chart-features",
  eventCategory: "financial-board-event-category",
};

const RESEARCH_REFERENCES = [
  {
    title: "Chronos: Learning the Language of Time Series",
    year: 2024,
    why: "Sequence-style forecasting influences the rolling multi-horizon path and uncertainty-aware framing.",
    url: "https://arxiv.org/abs/2403.07815",
  },
  {
    title: "TimesFM",
    year: 2024,
    why: "Decoder-style time-series reasoning informs the cross-horizon scenario lab and trend extraction.",
    url: "https://arxiv.org/abs/2310.10688",
  },
  {
    title: "A Time Series is Worth 64 Words",
    year: 2023,
    why: "Patch-based representations inspire the smoother momentum and volatility features used in the factor map.",
    url: "https://arxiv.org/abs/2211.14730",
  },
  {
    title: "Moirai 2.0",
    year: 2025,
    why: "Universal forecasting and quantile-style thinking motivate the validation panel and regime sensitivity.",
    url: "https://arxiv.org/abs/2511.11698",
  },
];

const ACADEMY_CONTENT = [
  {
    title: "Forecast score",
    body:
      "This board blends multiple signals instead of pretending one formula can solve markets. Momentum, macro regime, event load, valuation, and volatility all compete for weight.",
  },
  {
    title: "Urgent banner",
    body:
      "The top banner is for catalysts that can override slow-moving models, such as market-wide shocks, earnings headlines, or major repricing in rates and commodities.",
  },
  {
    title: "Validation panel",
    body:
      "The model lab shows how the current methodology would have behaved on recent history. That keeps us honest about error, drift, and scenario sensitivity.",
  },
  {
    title: "Market coverage",
    body:
      "Symbols can be searched globally. US names work directly, and exchanges like NSE are normalized through market suffixes such as .NS before the backend fetches live data.",
  },
];

const GLOSSARY = [
  {
    term: "Sharpe Ratio",
    body: "Risk-adjusted return measured as excess return per unit of volatility. Useful, but it can hide tail risk when returns are smoothed.",
  },
  {
    term: "Beta",
    body: "Sensitivity to the broad market. A beta above 1 usually means the stock amplifies index moves.",
  },
  {
    term: "Drawdown",
    body: "Peak-to-trough decline. It tells you how painful a strategy can feel, not just how profitable it looks on average.",
  },
  {
    term: "Realized Volatility",
    body: "Observed volatility from actual returns. When realized volatility expands, model confidence should usually fall.",
  },
  {
    term: "Mean Reversion",
    body: "The tendency for stretched prices to move back toward a rolling center. It matters most when positioning and volatility are crowded.",
  },
  {
    term: "Regime Shift",
    body: "A change in market behavior such as moving from growth optimism to inflation stress or risk-off liquidation.",
  },
];

const state = {
  watchlist: loadStoredWatchlist(),
  activeTicker: localStorage.getItem(STORAGE_KEYS.activeTicker) || "BHARTIARTL.NS",
  recentTickers: loadStoredRecentTickers(),
  chartRange: localStorage.getItem(STORAGE_KEYS.chartRange) || "1M",
  chartFeatures: loadStoredChartFeatures(),
  eventCategory: localStorage.getItem(STORAGE_KEYS.eventCategory) || "business",
  eventResult: null,
  dashboard: null,
  presets: [],
  savedWatchlists: [],
  config: null,
  labResult: null,
  statusTimer: null,
  researchResult: null,
  quoteStream: null,
  eventRequestId: 0,
  liveQuoteMemory: {},
  alerts: [],
  alertCooldowns: {},
  radarFloatOpenId: "",
};

if (state.watchlist.length === 0) {
  state.watchlist = ["BHARTIARTL.NS", "ICICIBANK.NS", "GLENMARK.NS"];
}

function loadStoredWatchlist() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.watchlist) || "[]");
  } catch {
    return [];
  }
}

function loadStoredRecentTickers() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.recentTickers) || "[]");
  } catch {
    return [];
  }
}

function loadStoredChartFeatures() {
  try {
    return {
      sma20: true,
      sma50: true,
      bands: false,
      ...(JSON.parse(localStorage.getItem(STORAGE_KEYS.chartFeatures) || "{}") || {}),
    };
  } catch {
    return { sma20: true, sma50: true, bands: false };
  }
}

function persistWatchlist() {
  localStorage.setItem(STORAGE_KEYS.watchlist, JSON.stringify(state.watchlist));
  localStorage.setItem(STORAGE_KEYS.activeTicker, state.activeTicker);
  localStorage.setItem(STORAGE_KEYS.recentTickers, JSON.stringify(state.recentTickers));
  localStorage.setItem(STORAGE_KEYS.chartRange, state.chartRange);
  localStorage.setItem(STORAGE_KEYS.chartFeatures, JSON.stringify(state.chartFeatures));
  localStorage.setItem(STORAGE_KEYS.eventCategory, state.eventCategory);
}

function pushRecentTicker(symbol, name = "") {
  if (!symbol) return;
  state.recentTickers = [{ symbol, name }]
    .concat(state.recentTickers.filter((item) => item.symbol !== symbol))
    .slice(0, 10);
  persistWatchlist();
}

function movingAverage(values, period) {
  return values.map((_, index) => {
    if (index + 1 < period) return null;
    const window = values.slice(index + 1 - period, index + 1);
    return window.reduce((sum, value) => sum + value, 0) / window.length;
  });
}

function rollingStd(values, period) {
  return values.map((_, index) => {
    if (index + 1 < period) return null;
    const window = values.slice(index + 1 - period, index + 1);
    const avg = window.reduce((sum, value) => sum + value, 0) / window.length;
    const variance = window.reduce((sum, value) => sum + (value - avg) ** 2, 0) / window.length;
    return Math.sqrt(variance);
  });
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

function formatPercent(value) {
  const numeric = Number(value || 0);
  return `${numeric >= 0 ? "+" : ""}${numeric.toFixed(2)}%`;
}

function formatCurrency(value, currency = "USD") {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  } catch {
    return `${Number(value).toFixed(2)} ${currency}`;
  }
}

function formatCompactNumber(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "n/a";
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: numeric >= 1000 ? 1 : 2,
  }).format(numeric);
}

function formatSignedCurrency(value, currency = "USD") {
  const numeric = Number(value || 0);
  return `${numeric >= 0 ? "+" : ""}${formatCurrency(numeric, currency)}`;
}

function formatSourceLabel(value) {
  if (!value) return "Unknown";
  return String(value)
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function extractDomainLabel(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

function formatRegionLabel(value) {
  return String(value || "World")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function shortenHeadline(text, words = 5) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  if (!clean) return "Live event";
  const parts = clean.split(" ");
  if (parts.length <= words) return clean;
  return `${parts.slice(0, words).join(" ")}...`;
}

function buildRadarFloatItems(radar = {}) {
  const items = radar.items || [];
  const hotspots = radar.hotspots || [];
  return items
    .slice(0, 3)
    .map((item, index) => ({
      id: item.url || `radar-float-${index}`,
      title: item.title || "Market event",
      url: item.url || "",
      source: extractDomainLabel(item.url) || "Live scan",
      region: formatRegionLabel(hotspots[index]?.region || "world"),
      bubble: shortenHeadline(item.title || "Market event", 4),
    }));
}

function setStatus(message) {
  const node = document.getElementById("status-updated");
  if (!node) return;
  node.textContent = message;
}

function flashStatus(message, timeout = 1600) {
  window.clearTimeout(state.statusTimer);
  setStatus(message);
  state.statusTimer = window.setTimeout(() => {
    if (state.dashboard?.updatedAt) {
      setStatus("Live now");
    }
  }, timeout);
}

function dismissAlert(id) {
  state.alerts = state.alerts.filter((item) => item.id !== id);
  renderAlerts();
}

function renderAlerts() {
  const node = document.getElementById("alert-stack");
  if (!node) return;
  node.innerHTML = state.alerts
    .map(
      (alert) => `
        <div class="alert-toast ${alert.direction}" data-alert-id="${alert.id}">
          <div class="alert-copy">
            <strong>${alert.symbol} ${alert.direction === "up" ? "surged" : "slipped"}</strong>
            <p>${alert.message}</p>
          </div>
          <button class="alert-close" type="button" data-alert-close="${alert.id}">Dismiss</button>
        </div>
      `,
    )
    .join("");
  node.querySelectorAll(".alert-close").forEach((button) => {
    button.addEventListener("click", () => dismissAlert(button.dataset.alertClose));
  });
}

function queueAlert(symbol, direction, message) {
  const id = `${symbol}-${direction}-${Date.now()}`;
  state.alerts = [{ id, symbol, direction, message }].concat(state.alerts).slice(0, 4);
  renderAlerts();
  window.setTimeout(() => dismissAlert(id), 9000);
}

function processRecentTickerAlerts(quotes = []) {
  const tracked = new Set((state.recentTickers || []).map((item) => item.symbol).slice(0, 10));
  const now = Date.now();
  quotes.forEach((item) => {
    if (!tracked.has(item.symbol) || !Number.isFinite(Number(item.price))) return;
    const price = Number(item.price);
    const previousSeen = Number(state.liveQuoteMemory[item.symbol]);
    state.liveQuoteMemory[item.symbol] = price;
    if (!Number.isFinite(previousSeen) || previousSeen <= 0) return;
    const movePercent = ((price - previousSeen) / previousSeen) * 100;
    if (Math.abs(movePercent) < 1) return;
    const direction = movePercent > 0 ? "up" : "down";
    const cooldownKey = `${item.symbol}:${direction}`;
    if ((state.alertCooldowns[cooldownKey] || 0) > now - 120000) return;
    state.alertCooldowns[cooldownKey] = now;
    const absoluteMove = price - previousSeen;
    queueAlert(
      item.symbol,
      direction,
      `${formatPercent(movePercent)} from ${formatCurrency(previousSeen, item.currency)} to ${formatCurrency(price, item.currency)} (${formatSignedCurrency(absoluteMove, item.currency)}).`,
    );
  });
}

function drawSparkline(svg, values, strokeA = "#54d2ff", strokeB = "#5af2c5") {
  if (!svg) return;
  if (!values?.length) {
    svg.innerHTML = `<text x="50%" y="52%" text-anchor="middle" fill="rgba(255,255,255,0.45)" font-size="12">No chart data</text>`;
    return;
  }
  const width = 320;
  const height = 100;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const points = values
    .map((value, index) => {
      const x = (index / (values.length - 1 || 1)) * width;
      const y = height - ((value - min) / range) * (height - 12) - 6;
      return `${x},${y}`;
    })
    .join(" ");

  svg.innerHTML = `
    <defs>
      <linearGradient id="spark-gradient" x1="0%" x2="100%" y1="0%" y2="0%">
        <stop offset="0%" stop-color="${strokeA}" />
        <stop offset="100%" stop-color="${strokeB}" />
      </linearGradient>
    </defs>
    <polyline fill="none" stroke="url(#spark-gradient)" stroke-width="4" points="${points}" stroke-linecap="round" stroke-linejoin="round"></polyline>
  `;
}

function drawProjection(svg, history, projected, features = {}) {
  if (!svg) return;
  if (!history?.length) {
    svg.innerHTML = `<text x="50%" y="52%" text-anchor="middle" fill="rgba(255,255,255,0.45)" font-size="14">No chart data</text>`;
    return;
  }
  if (!projected?.length) {
    projected = [history[history.length - 1]];
  }
  const width = 640;
  const height = 240;
  const values = [...history, ...projected];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const toPoint = (value, index, total) => {
    const x = (index / (total - 1 || 1)) * width;
    const y = height - ((value - min) / range) * (height - 24) - 12;
    return `${x},${y}`;
  };

  const historicalPoints = history.map((value, index) => toPoint(value, index, values.length)).join(" ");
  const projectedPoints = projected
    .map((value, index) => toPoint(value, history.length + index, values.length))
    .join(" ");

  const overlays = [];
  const drawSeries = (series, stroke, dash = "", width = 2, opacity = 0.8) => {
    const points = series
      .map((value, index) => (Number.isFinite(value) ? toPoint(value, index, values.length) : ""))
      .filter(Boolean)
      .join(" ");
    if (!points) return;
    overlays.push(
      `<polyline fill="none" stroke="${stroke}" stroke-width="${width}" ${dash ? `stroke-dasharray="${dash}"` : ""} opacity="${opacity}" points="${points}" stroke-linecap="round"></polyline>`,
    );
  };

  if (features.sma20) {
    drawSeries(movingAverage(history, 20), "rgba(93,214,255,0.8)", "6 5", 2);
  }
  if (features.sma50) {
    drawSeries(movingAverage(history, 50), "rgba(255,176,0,0.75)", "10 6", 2);
  }
  if (features.bands) {
    const avg = movingAverage(history, 20);
    const std = rollingStd(history, 20);
    drawSeries(avg.map((value, index) => (value !== null && std[index] !== null ? value + (std[index] * 2) : null)), "rgba(255,255,255,0.35)", "4 4", 1.5, 0.7);
    drawSeries(avg.map((value, index) => (value !== null && std[index] !== null ? value - (std[index] * 2) : null)), "rgba(255,255,255,0.35)", "4 4", 1.5, 0.7);
  }

  svg.innerHTML = `
    <line x1="0" y1="${height - 24}" x2="${width}" y2="${height - 24}" stroke="rgba(255,255,255,0.10)"></line>
    <polyline fill="none" stroke="#54d2ff" stroke-width="3.5" points="${historicalPoints}" stroke-linecap="round"></polyline>
    ${overlays.join("")}
    <polyline fill="none" stroke="#f3b85f" stroke-width="3.5" stroke-dasharray="8 8" points="${projectedPoints}" stroke-linecap="round"></polyline>
  `;
}

function drawTimeline(svg, history, projected, features = {}) {
  drawProjection(svg, history, projected, features);
}

function renderSearchResults(results = []) {
  const node = document.getElementById("search-results");
  if (!results.length) {
    node.innerHTML = "";
    return;
  }

  node.innerHTML = results
    .map(
      (item) => `
        <button class="search-result" type="button" data-symbol="${item.symbol}">
          <div>
            <strong>${item.symbol}</strong>
            <p>${item.name || item.exchange || "Market listing"}</p>
          </div>
          <span>${item.exchange || item.region || "Global"}</span>
        </button>
      `,
    )
    .join("");

  node.querySelectorAll(".search-result").forEach((button) => {
    button.addEventListener("click", () => addTicker(button.dataset.symbol));
  });
}

function renderPresets() {
  const node = document.getElementById("preset-grid");
  node.innerHTML = state.presets
    .map(
      (preset) => `
        <button class="preset-pill" type="button" data-preset="${preset.name}">
          <strong>${preset.label}</strong>
          <span>${preset.symbols.length} symbols</span>
          <em>${preset.symbols.slice(0, 3).join(" · ")}</em>
        </button>
      `,
    )
    .join("");

  node.querySelectorAll(".preset-pill").forEach((button) => {
    button.addEventListener("click", () => {
      const preset = state.presets.find((item) => item.name === button.dataset.preset);
      if (!preset) return;
      state.watchlist = [...preset.symbols];
      selectActiveTicker(preset.symbols[0]);
    });
  });
}

function reorderWatchlist(sourceSymbol, targetSymbol) {
  if (!sourceSymbol || !targetSymbol || sourceSymbol === targetSymbol) return;
  const sourceIndex = state.watchlist.indexOf(sourceSymbol);
  const targetIndex = state.watchlist.indexOf(targetSymbol);
  if (sourceIndex < 0 || targetIndex < 0) return;
  const next = [...state.watchlist];
  const [moved] = next.splice(sourceIndex, 1);
  next.splice(targetIndex, 0, moved);
  state.watchlist = next;
  if (state.dashboard?.watchlist) {
    const map = new Map(state.dashboard.watchlist.map((item) => [item.symbol, item]));
    state.dashboard.watchlist = state.watchlist.map((symbol) => map.get(symbol)).filter(Boolean);
  }
  persistWatchlist();
  renderWatchlist();
  renderBoard();
}

function renderSavedWatchlists() {
  const select = document.getElementById("saved-watchlists");
  const saved = state.savedWatchlists || [];
  select.innerHTML = ['<option value="">Load saved list</option>']
    .concat(saved.map((item) => `<option value="${item.name}">${item.name} (${item.count})</option>`))
    .join("");
}

function renderRecentTickers() {
  const node = document.getElementById("recent-tickers");
  if (!node) return;
  if (!state.recentTickers.length) {
    node.innerHTML = `<p class="muted">Recent names will appear here.</p>`;
    return;
  }
  node.innerHTML = state.recentTickers
    .map(
      (item) => `
        <button class="recent-pill ${item.symbol === state.activeTicker ? "active" : ""}" type="button" data-symbol="${item.symbol}" title="${item.name || item.symbol}">
          <strong>${item.symbol}</strong>
          <span>${item.name || "Recent ticker"}</span>
        </button>
      `,
    )
    .join("");

  node.querySelectorAll(".recent-pill").forEach((button) => {
    button.addEventListener("click", () => {
      selectActiveTicker(button.dataset.symbol);
    });
  });
}

function renderWatchlist() {
  const node = document.getElementById("watchlist");
  const count = document.getElementById("watchlist-count");
  const entries = state.dashboard?.watchlist || [];
  count.textContent = String(entries.length);

  node.innerHTML = entries
    .map(
      (item) => `
        <button class="watch-item ${item.symbol === state.activeTicker ? "active" : ""}" type="button" data-symbol="${item.symbol}" draggable="true">
          <div class="watch-row">
            <span class="watch-symbol">${item.symbol}</span>
            <div class="watch-actions">
              <span class="drag-handle" data-drag-handle="${item.symbol}">::</span>
              <span class="watch-change ${item.changePercent >= 0 ? "positive" : "negative"}">${formatPercent(item.changePercent)}</span>
              <span class="delete-chip" data-delete="${item.symbol}">Delete</span>
            </div>
          </div>
          <div class="watch-row">
            <span class="watch-name">${item.name}</span>
            <span class="watch-price">${formatCurrency(item.price, item.currency)}</span>
          </div>
          <div class="watch-row watch-meta-row">
            <span>${item.exchange} · ${item.currency}</span>
            <span>Vol ${formatCompactNumber(item.volume)}</span>
          </div>
        </button>
      `,
    )
    .join("");

  let draggedSymbol = "";
  node.querySelectorAll(".watch-item").forEach((button) => {
    button.addEventListener("click", () => {
      selectActiveTicker(button.dataset.symbol);
    });
    let startX = 0;
    button.addEventListener("pointerdown", (event) => {
      startX = event.clientX;
    });
    button.addEventListener("pointerup", (event) => {
      if (startX - event.clientX > 70) {
        removeTicker(button.dataset.symbol);
      }
    });
    button.addEventListener("wheel", (event) => {
      if (Math.abs(event.deltaX) > 30 && event.deltaX > 0) {
        removeTicker(button.dataset.symbol);
      }
    });
    button.addEventListener("dragstart", (event) => {
      draggedSymbol = button.dataset.symbol;
      button.classList.add("dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", draggedSymbol);
    });
    button.addEventListener("dragend", () => {
      button.classList.remove("dragging");
      draggedSymbol = "";
    });
    button.addEventListener("dragover", (event) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
    });
    button.addEventListener("drop", (event) => {
      event.preventDefault();
      const sourceSymbol = draggedSymbol || event.dataTransfer.getData("text/plain");
      const targetSymbol = button.dataset.symbol;
      reorderWatchlist(sourceSymbol, targetSymbol);
    });
  });
  node.querySelectorAll(".delete-chip").forEach((chip) => {
    chip.addEventListener("click", (event) => {
      event.stopPropagation();
      removeTicker(chip.dataset.delete);
    });
  });
}

function renderBanner() {
  const track = document.getElementById("headline-track");
  const summary = document.getElementById("radar-summary");
  const hotspotNode = document.getElementById("radar-hotspots");
  const sourceNote = document.getElementById("radar-source-note");
  const floatNode = document.getElementById("radar-floats");
  const floatDetailNode = document.getElementById("radar-float-detail");
  const radar = state.dashboard?.radar || {};
  const headlines = radar.headlines?.length
    ? radar.headlines
    : state.dashboard?.headlines?.length
      ? state.dashboard.headlines
      : ["Live radar updates are loading."];
  const repeated = [...headlines, ...headlines].map((headline) => `<span>${headline}</span>`).join("");
  track.innerHTML = repeated;
  summary.textContent = radar.summary || "Global event radar is loading.";

  const hotspots = radar.hotspots || [];
  const activeRegions = new Set(hotspots.map((item) => item.region));
  [
    "north_america",
    "south_america",
    "europe",
    "africa",
    "middle_east",
    "south_asia",
    "east_asia",
  ].forEach((region) => {
    const node = document.getElementById(`hotspot-${region}`);
    if (!node) return;
    node.classList.toggle("active", activeRegions.has(region));
  });
  hotspotNode.classList.toggle("is-fallback", hotspots.length === 0);

  hotspotNode.innerHTML = hotspots.length
    ? hotspots
        .map(
          (item) => `
            <div class="radar-hotspot-card">
              <strong>${item.region.replace("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase())}</strong>
              <p>${item.headline || "Market-sensitive developments detected."}</p>
            </div>
          `,
        )
        .join("")
    : `
      <div class="radar-hotspot-card">
        <strong>Global scan</strong>
        <p>${headlines[0] || "Latest cross-market developments are being gathered."}</p>
      </div>
      <div class="radar-hotspot-card">
        <strong>Watching</strong>
        <p>${headlines[1] || "Macro, geopolitical, and company-driven market impacts will appear here."}</p>
      </div>
    `;

  const radarSources = [...new Set((radar.items || []).map((item) => extractDomainLabel(item.url)).filter(Boolean))].slice(0, 4);
  sourceNote.textContent = radarSources.length
    ? `Radar sources: ${radarSources.join(" • ")}`
    : "Radar sources: live event scan";

  const floatPositions = [
    { x: "6%", y: "4px", delay: "0s" },
    { x: "40%", y: "14px", delay: "1.6s" },
    { x: "72%", y: "2px", delay: "3.1s" },
  ];
  const floatItems = buildRadarFloatItems(radar);
  if (floatNode) {
    floatNode.innerHTML = floatItems
      .map((item, index) => {
        const pos = floatPositions[index] || floatPositions[floatPositions.length - 1];
        return `
          <button
            class="radar-float-chip ${state.radarFloatOpenId === item.id ? "active" : ""}"
            type="button"
            data-radar-float="${item.id}"
            style="--float-x:${pos.x}; --float-y:${pos.y}; --float-delay:${pos.delay};"
            title="${item.title}"
          >
            <span>${item.region}</span>
            <strong>${item.bubble}</strong>
          </button>
        `;
      })
      .join("");
    floatNode.querySelectorAll("[data-radar-float]").forEach((button) => {
      button.addEventListener("click", () => {
        const id = button.dataset.radarFloat;
        state.radarFloatOpenId = state.radarFloatOpenId === id ? "" : id;
        renderBanner();
      });
    });
  }

  if (floatDetailNode) {
    const activeFloat = floatItems.find((item) => item.id === state.radarFloatOpenId);
    if (!activeFloat) {
      floatDetailNode.hidden = true;
      floatDetailNode.innerHTML = "";
    } else {
      floatDetailNode.hidden = false;
      floatDetailNode.innerHTML = `
        <div class="radar-float-pop">
          <button class="radar-float-close" type="button" data-radar-float-close="true">Close</button>
          <span>${activeFloat.region} • ${activeFloat.source}</span>
          <strong>${activeFloat.title}</strong>
          ${activeFloat.url ? `<a href="${activeFloat.url}" target="_blank" rel="noreferrer">Open coverage</a>` : ""}
        </div>
      `;
      const closeNode = floatDetailNode.querySelector("[data-radar-float-close]");
      if (closeNode) {
        closeNode.addEventListener("click", () => {
          state.radarFloatOpenId = "";
          renderBanner();
        });
      }
    }
  }
}

function renderEventFeed() {
  const brief = document.getElementById("event-brief");
  const list = document.getElementById("event-list");
  const label = document.getElementById("event-summary-label");
  label.textContent = state.eventCategory.charAt(0).toUpperCase() + state.eventCategory.slice(1);
  document.querySelectorAll(".event-chip").forEach((button) => {
    button.classList.toggle("active", button.dataset.category === state.eventCategory);
  });

  if (!state.eventResult) {
    brief.innerHTML = `<p class="muted">Event feed is loading.</p>`;
    list.innerHTML = `<div class="event-card"><strong>Waiting for updates</strong><p>Latest category events will appear here.</p></div>`;
    return;
  }

  brief.innerHTML = `<p>${state.eventResult.brief || "No major updates in this category."}</p>`;
  const items = state.eventResult.items || [];
  list.innerHTML = items.length
    ? items
        .map(
          (item) => `
            <article class="event-card">
              <a href="${item.url}" target="_blank" rel="noreferrer"><strong>${item.title || "Update"}</strong></a>
              <span>${state.eventResult.category.toUpperCase()}</span>
              <p><a href="${item.url}" target="_blank" rel="noreferrer">${item.url}</a></p>
            </article>
          `,
        )
        .join("")
    : `<div class="event-card"><strong>No live matches</strong><p>Try another category or search phrase.</p></div>`;
}

function renderPulse() {
  const grid = document.getElementById("pulse-grid");
  const items = state.dashboard?.macroPulse || [];
  grid.innerHTML = items
    .map(
      (item) => `
        <div class="pulse-card">
          <span>${item.label}</span>
          <strong>${item.value}</strong>
          <div class="metric-trend ${item.positive ? "positive" : "negative"}">${item.trend}</div>
        </div>
      `,
    )
    .join("");
}

function renderBoard() {
  const board = document.getElementById("overview-board");
  const entries = (state.dashboard?.watchlist || []).slice(0, 8);
  board.innerHTML = entries
    .map(
      (item) => `
        <button class="board-tile ${item.changePercent >= 0 ? "up" : "down"} ${item.symbol === state.activeTicker ? "active" : ""}" type="button" data-symbol="${item.symbol}">
          <span class="board-symbol">${item.symbol}</span>
          <strong class="board-price">${formatCurrency(item.price, item.currency)}</strong>
          <span class="board-change ${item.changePercent >= 0 ? "positive" : "negative"}">${formatPercent(item.changePercent)}</span>
        </button>
      `,
    )
    .join("");

  board.querySelectorAll(".board-tile").forEach((button) => {
    button.addEventListener("click", () => {
      selectActiveTicker(button.dataset.symbol);
    });
  });
}

function renderOverview() {
  const active = state.dashboard?.active;
  if (!active) return;

  document.getElementById("hero-ticker").textContent = `${active.symbol} · ${active.name}`;
  document.getElementById("hero-regime").textContent = active.regime;
  document.getElementById("hero-price").textContent = formatCurrency(active.price, active.currency);
  const changeNode = document.getElementById("hero-change");
  changeNode.textContent = formatPercent(active.changePercent);
  changeNode.className = `hero-change ${active.changePercent >= 0 ? "positive" : "negative"}`;
  document.getElementById("forecast-direction").textContent = active.forecast.direction;
  document.getElementById("forecast-confidence").textContent = `Confidence ${active.forecast.confidence.toFixed(0)}%`;
  document.getElementById("fair-value-gap").textContent = formatPercent(active.forecast.fairValueGap);
  document.getElementById("event-pressure").textContent = active.forecast.eventPressureLabel;
  document.getElementById("model-error").textContent = `${active.forecast.mae.toFixed(1)}%`;
  document.getElementById("forecast-range").textContent = `10D projection ${formatPercent(active.forecast.expectedReturn)}`;
  document.getElementById("buy-sell-signal").textContent = active.recommendation?.signal || "Balanced";
  document.getElementById("buy-sell-breakdown").textContent = `Buy ${active.recommendation?.buy ?? 0}% · Hold ${active.recommendation?.hold ?? 100}% · Sell ${active.recommendation?.sell ?? 0}%`;
  document.getElementById("overview-meta").innerHTML = `
    <span>${active.exchange || active.region || "Global"}</span>
    <span>${active.currency || "USD"} pricing</span>
    <span>${active.marketState || "Live"}</span>
    <span>Vol ${formatCompactNumber(active.volume)}</span>
    <span>${active.asOf ? new Date(active.asOf).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "Delayed"}</span>
  `;
  const quoteSource = document.getElementById("quote-source-note");
  const asOf = active.asOf ? new Date(active.asOf).toLocaleString() : "";
  quoteSource.textContent = asOf
    ? `Quote source: ${formatSourceLabel(active.dataSource)} • Updated ${asOf}`
    : `Quote source: ${formatSourceLabel(active.dataSource)}`;
  document.getElementById("hero-stats").innerHTML = (active.stats || [])
    .map(
      (stat) => `
        <div class="hero-stat-card">
          <span>${stat.label}</span>
          <strong>${stat.value}</strong>
        </div>
      `,
    )
    .join("");

  drawSparkline(document.getElementById("hero-sparkline"), (active.history || []).slice(-24));
  drawTimeline(document.getElementById("hero-projection-chart"), active.history || [], active.forecast.projected, state.chartFeatures);
  document.querySelectorAll(".range-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.range === state.chartRange);
  });
  document.getElementById("feature-sma20").checked = Boolean(state.chartFeatures.sma20);
  document.getElementById("feature-sma50").checked = Boolean(state.chartFeatures.sma50);
  document.getElementById("feature-bands").checked = Boolean(state.chartFeatures.bands);

  document.getElementById("factor-map").innerHTML = (active.relationshipCards || active.forecast.factors)
    .map(
      (factor) => `
        <div class="factor-card">
          <div class="factor-card-header">
            <strong>${factor.title}</strong>
            <span>${factor.score.toFixed(0)}</span>
          </div>
          <div class="impact-bar"><div class="impact-fill" style="width:${Math.abs(factor.score)}%"></div></div>
          <p>${factor.description}</p>
        </div>
      `,
    )
    .join("");

  document.getElementById("catalyst-list").innerHTML = (active.driverCards || active.forecast.triggers)
    .map(
      (item, index) => `
        <div class="catalyst-card">
          <div class="catalyst-header">
            <strong>${index + 1}. ${item.title}</strong>
            <span>${item.tag || (index === 0 ? "Primary" : "Active")}</span>
          </div>
          <p>${item.body || item.description}</p>
        </div>
      `,
    )
    .join("");
}

function renderLab() {
  const active = state.dashboard?.active;
  const result = state.labResult || active?.lab;
  const sourceNode = document.getElementById("lab-source-note");
  const tickerInput = document.getElementById("lab-ticker");
  if (tickerInput && document.activeElement !== tickerInput) {
    tickerInput.value = (result?.symbol || active?.symbol || state.activeTicker || "").toUpperCase();
  }
  if (!active || !result) {
    if (sourceNode) {
      sourceNode.textContent = "History source pending.";
    }
    document.getElementById("validation-metrics").innerHTML = `<div class="metric-card"><span>Model lab</span><strong>Waiting</strong></div>`;
    document.getElementById("trigger-reasons").innerHTML = `<div class="reason-card"><strong>Run a scenario</strong><p>Choose a ticker and horizon to inspect projected path, error rate, and trigger attribution.</p></div>`;
    return;
  }

  const cacheStamp = result.historyCachedAt ? new Date(result.historyCachedAt).toLocaleString() : "";
  if (sourceNode) {
    const sourceText = result.historySource || active.historySource || "Unavailable";
    const cacheState = result.historyCacheState === "stale" ? "stale cache" : result.historyCacheState === "fresh" ? "local cache" : "live fetch";
    sourceNode.textContent = cacheStamp
      ? `History: ${sourceText} • ${cacheState} • Cached ${cacheStamp}`
      : `History: ${sourceText}`;
  }

  drawProjection(document.getElementById("lab-chart"), result.history, result.projected, state.chartFeatures);
  document.getElementById("validation-metrics").innerHTML = `
    <div class="metric-card">
      <span>Direction</span>
      <strong>${result.direction || active.forecast.direction}</strong>
    </div>
    <div class="metric-card">
      <span>Expected return</span>
      <strong>${formatPercent(result.expectedReturn)}</strong>
    </div>
    <div class="metric-card">
      <span>Rolling MAE</span>
      <strong>${result.backtest.mae.toFixed(2)}%</strong>
    </div>
    <div class="metric-card">
      <span>Hit rate</span>
      <strong>${result.backtest.hitRate.toFixed(1)}%</strong>
    </div>
    <div class="metric-card">
      <span>Median error</span>
      <strong>${result.backtest.medianApe.toFixed(2)}%</strong>
    </div>
    <div class="metric-card">
      <span>Samples</span>
      <strong>${result.backtest.sampleCount || 0}</strong>
    </div>
  `;

  document.getElementById("trigger-reasons").innerHTML = result.triggers
    .map(
      (trigger) => `
        <div class="reason-card">
          <strong>${trigger.title}</strong>
          <p>${trigger.body}</p>
        </div>
      `,
    )
    .join("");
}

function renderAcademy() {
  const active = state.dashboard?.active;
  const tickerSpecific = active
    ? [
        {
          title: "Current stock read",
          body: `${active.name} is trading in ${active.currency} with ${active.forecast.direction.toLowerCase()} model bias and ${active.forecast.eventPressureLabel.toLowerCase()} event pressure.`,
        },
        {
          title: "Current macro linkage",
          body: `${active.exchange} exposure, ${active.sector || "sector"} context, and volume at ${formatCompactNumber(active.volume)} are part of the current relationship map.`,
        },
      ]
    : [];
  document.getElementById("academy-cards").innerHTML = ACADEMY_CONTENT
    .concat(tickerSpecific)
    .map(
      (item) => `
        <div class="academy-card">
          <strong>${item.title}</strong>
          <p>${item.body}</p>
        </div>
      `,
    )
    .join("");

  document.getElementById("glossary-list").innerHTML = GLOSSARY
    .map(
      (item) => `
        <div class="glossary-card">
          <strong>${item.term}</strong>
          <p>${item.body}</p>
        </div>
      `,
    )
    .join("");

  document.getElementById("research-list").innerHTML = RESEARCH_REFERENCES
    .map(
      (item) => `
        <a class="research-card" href="${item.url}" target="_blank" rel="noreferrer">
          <span>${item.year}</span>
          <strong>${item.title}</strong>
          <p>${item.why}</p>
        </a>
      `,
    )
    .join("");
}

function renderResearch() {
  const summary = document.getElementById("research-summary");
  const sources = document.getElementById("research-sources");
  if (!state.researchResult) {
    summary.innerHTML = `<p class="muted">Ask about the active ticker, dashboard signals, a macro event, or a company. The assistant can use your local LLM and optional web search.</p>`;
    sources.innerHTML = `<div class="source-card"><strong>Waiting for query</strong><p>Web grounding and dashboard context will appear here.</p></div>`;
    return;
  }

  const { answer, takeaways = [], context = {}, webResults = [] } = state.researchResult;
  summary.innerHTML = `
    <h4>${context.symbol ? `${context.symbol} Research Brief` : "Research Brief"}</h4>
    <p>${answer}</p>
    <ul>${takeaways.map((item) => `<li>${item}</li>`).join("")}</ul>
  `;

  if (!webResults.length) {
    sources.innerHTML = `<div class="source-card"><strong>No web results</strong><p>The response used dashboard context${state.researchResult.llmUsed ? " and your local LLM" : ""}.</p></div>`;
    return;
  }

  sources.innerHTML = webResults
    .map(
      (item) => `
        <div class="source-card">
          <strong>${item.title || "Result"}</strong>
          <p><a href="${item.url}" target="_blank" rel="noreferrer">${item.url}</a></p>
        </div>
      `,
    )
    .join("");
}

function renderTopbar() {
  document.getElementById("provider-badge").textContent = state.dashboard?.provider || state.config?.provider || "yahoo";
  document.getElementById("status-updated").textContent = state.dashboard?.updatedAt ? "Live now" : "Loading data";
}

function applyLiveQuoteUpdate(payload) {
  if (!state.dashboard || !payload) return;
  state.dashboard.updatedAt = payload.updatedAt;
  processRecentTickerAlerts(payload.watchlist || []);

  const quoteMap = new Map((payload.watchlist || []).map((item) => [item.symbol, item]));
  state.dashboard.watchlist = (state.dashboard.watchlist || []).map((item) => {
    const live = quoteMap.get(item.symbol);
    return live ? { ...item, ...live } : item;
  });

  if (payload.active && state.dashboard.active?.symbol === payload.active.symbol) {
    state.dashboard.active = {
      ...state.dashboard.active,
      ...payload.active,
    };
  } else if (payload.active) {
    const live = quoteMap.get(state.activeTicker);
    if (live && state.dashboard.active) {
      state.dashboard.active = { ...state.dashboard.active, ...live };
    }
  }

  renderWatchlist();
  renderOverview();
  renderTopbar();
  flashStatus("Live now", 900);
}

function startQuoteStream() {
  if (state.quoteStream) {
    state.quoteStream.close();
  }
  const symbols = encodeURIComponent(state.watchlist.join(","));
  const active = encodeURIComponent(state.activeTicker || "");
  const stream = new EventSource(`/api/stream?symbols=${symbols}&active=${active}`);
  state.quoteStream = stream;
  stream.addEventListener("quote", (event) => {
    try {
      const payload = JSON.parse(event.data);
      applyLiveQuoteUpdate(payload);
    } catch (error) {
      console.error(error);
    }
  });
  stream.onerror = () => {
    setStatus("Stream retry");
  };
}

function render() {
  renderAlerts();
  renderSearchResults();
  renderPresets();
  renderSavedWatchlists();
  renderRecentTickers();
  renderWatchlist();
  renderBanner();
  renderBoard();
  renderPulse();
  renderOverview();
  renderLab();
  renderAcademy();
  renderResearch();
  renderEventFeed();
  renderTopbar();
  document.getElementById("lab-ticker").value = state.activeTicker;
}

async function loadConfig() {
  setStatus("Loading config");
  state.config = await api("/api/config");
  document.getElementById("provider-select").value = state.config.provider || "yahoo";
  document.getElementById("alpha-key").value = state.config.alphaVantageApiKey || "";
  document.getElementById("llm-base-url").value = state.config.localLlmBaseUrl || "http://127.0.0.1:11434";
  document.getElementById("llm-model").value = state.config.localLlmModel || "Bonsai-8B-1bit";
}

async function loadPresets() {
  setStatus("Loading presets");
  const payload = await api("/api/presets");
  state.presets = payload.presets || [];
}

async function loadSavedWatchlists() {
  setStatus("Loading lists");
  const payload = await api("/api/watchlists");
  state.savedWatchlists = payload.watchlists || [];
}

async function loadEventFeed(keyword = "", { silent = false } = {}) {
  const requestId = ++state.eventRequestId;
  if (!silent) {
    setStatus("Loading feed");
  }
  const params = new URLSearchParams({
    category: state.eventCategory,
    symbol: state.activeTicker || "",
  });
  if (keyword.trim()) {
    params.set("q", keyword.trim());
  }
  const result = await api(`/api/events?${params.toString()}`);
  if (requestId !== state.eventRequestId) return;
  state.eventResult = result;
}

function selectActiveTicker(symbol, { refresh = true } = {}) {
  const cleaned = (symbol || "").trim().toUpperCase();
  if (!cleaned) return;
  const changed = state.activeTicker !== cleaned;
  state.activeTicker = cleaned;
  persistWatchlist();
  renderWatchlist();
  renderBoard();
  renderRecentTickers();
  if (!refresh) return;
  if (changed) {
    setStatus("Loading data");
  }
  refreshDashboard();
}

async function refreshDashboard() {
  setStatus("Refreshing");
  const payload = await api("/api/dashboard", {
    method: "POST",
    body: JSON.stringify({
      symbols: state.watchlist,
      active: state.activeTicker,
      chartRange: state.chartRange,
    }),
  });

  state.dashboard = payload;
  state.watchlist = payload.watchlist.map((item) => item.symbol);
  state.activeTicker = payload.active.symbol;
  if (!state.labResult || state.labResult.symbol !== state.activeTicker) {
    state.labResult = payload.active.lab;
  }
  pushRecentTicker(payload.active.symbol, payload.active.name);
  persistWatchlist();
  render();
  startQuoteStream();
  flashStatus("Live now");
  loadEventFeed("", { silent: true }).then(() => {
    renderEventFeed();
  }).catch((error) => {
    console.error(error);
  });
}

async function runSearch() {
  const input = document.getElementById("ticker-input");
  const query = input.value.trim();
  if (!query) {
    renderSearchResults();
    return;
  }

  setStatus("Searching");
  const payload = await api(`/api/search?q=${encodeURIComponent(query)}`);
  renderSearchResults(payload.results || []);
  flashStatus("Search ready", 1200);
}

function addTicker(symbol) {
  const cleaned = symbol.trim().toUpperCase();
  if (!cleaned) return;
  if (!state.watchlist.includes(cleaned)) {
    state.watchlist.unshift(cleaned);
  }
  state.activeTicker = cleaned;
  state.labResult = null;
  pushRecentTicker(cleaned);
  persistWatchlist();
  refreshDashboard();
}

function removeTicker(symbol) {
  if (state.watchlist.length <= 1) return;
  state.watchlist = state.watchlist.filter((item) => item !== symbol);
  if (state.activeTicker === symbol) {
    state.activeTicker = state.watchlist[0];
  }
  state.labResult = null;
  persistWatchlist();
  setStatus("Removing");
  refreshDashboard();
}

async function addTickerFromInput() {
  const input = document.getElementById("ticker-input");
  const query = input.value.trim();
  if (!query) return;
  setStatus("Resolving");
  const payload = await api(`/api/search?q=${encodeURIComponent(query)}`);
  const best = payload.results?.[0];
  addTicker(best?.symbol || query.toUpperCase());
  input.value = "";
  renderSearchResults(payload.results || []);
}

function bindEvents() {
  const labTickerInput = document.getElementById("lab-ticker");
  if (labTickerInput && !labTickerInput.value.trim()) {
    labTickerInput.value = state.activeTicker;
  }

  document.getElementById("ticker-form").addEventListener("submit", (event) => {
    event.preventDefault();
    addTickerFromInput();
  });

  document.getElementById("search-button").addEventListener("click", runSearch);
  document.getElementById("ticker-input").addEventListener("input", () => {
    window.clearTimeout(bindEvents.searchTimer);
    bindEvents.searchTimer = window.setTimeout(runSearch, 260);
  });

  document.querySelectorAll(".range-tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.chartRange = button.dataset.range;
      persistWatchlist();
      refreshDashboard();
    });
  });

  [
    ["feature-sma20", "sma20"],
    ["feature-sma50", "sma50"],
    ["feature-bands", "bands"],
  ].forEach(([id, key]) => {
    const node = document.getElementById(id);
    node.checked = Boolean(state.chartFeatures[key]);
    node.addEventListener("change", () => {
      state.chartFeatures[key] = node.checked;
      persistWatchlist();
      renderOverview();
    });
  });

  document.querySelectorAll(".event-chip").forEach((button) => {
    button.addEventListener("click", async () => {
      state.eventCategory = button.dataset.category;
      persistWatchlist();
      await loadEventFeed();
      renderEventFeed();
      flashStatus("Feed ready", 1000);
    });
  });

  document.getElementById("event-search-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const keyword = document.getElementById("event-search-input").value.trim();
    await loadEventFeed(keyword);
    renderEventFeed();
    flashStatus("Feed ready", 1000);
  });

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      document.querySelectorAll(".tab").forEach((node) => node.classList.toggle("active", node === tab));
      document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === target));
    });
  });

  const settingsDialog = document.getElementById("settings-dialog");
  document.getElementById("open-settings").addEventListener("click", () => settingsDialog.showModal());
  document.getElementById("save-settings").addEventListener("click", async (event) => {
    event.preventDefault();
    setStatus("Saving config");
    state.config = await api("/api/config", {
      method: "POST",
      body: JSON.stringify({
        provider: document.getElementById("provider-select").value,
        alphaVantageApiKey: document.getElementById("alpha-key").value.trim(),
        localLlmBaseUrl: document.getElementById("llm-base-url").value.trim(),
        localLlmModel: document.getElementById("llm-model").value.trim(),
      }),
    });
    settingsDialog.close();
    refreshDashboard();
  });

  document.getElementById("save-watchlist").addEventListener("click", async () => {
    const nameInput = document.getElementById("watchlist-name");
    const name = nameInput.value.trim();
    if (!name) return;
    setStatus("Saving list");
    await api("/api/watchlists", {
      method: "POST",
      body: JSON.stringify({ name, symbols: state.watchlist }),
    });
    nameInput.value = "";
    await loadSavedWatchlists();
    renderSavedWatchlists();
  });

  document.getElementById("load-watchlist").addEventListener("click", async () => {
    const name = document.getElementById("saved-watchlists").value;
    const saved = state.savedWatchlists.find((item) => item.name === name);
    if (!saved) return;
    setStatus("Loading list");
    state.watchlist = [...saved.symbols];
    state.activeTicker = saved.symbols[0];
    state.labResult = null;
    persistWatchlist();
    refreshDashboard();
  });

  document.getElementById("lab-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const symbolInput = document.getElementById("lab-ticker").value.trim().toUpperCase() || state.activeTicker;
    setStatus("Running lab");
    const payload = await api("/api/lab", {
      method: "POST",
      body: JSON.stringify({
        symbol: symbolInput,
        horizon: Number(document.getElementById("lab-horizon").value),
        stress: document.getElementById("lab-stress").value,
        chartRange: state.chartRange,
      }),
    });
    if (!state.watchlist.includes(payload.symbol)) {
      state.watchlist.unshift(payload.symbol);
    }
    state.activeTicker = payload.symbol;
    state.labResult = payload;
    pushRecentTicker(payload.symbol);
    persistWatchlist();
    document.querySelector('[data-tab="lab"]').click();
    renderLab();
    flashStatus("Lab ready", 1200);
  });

  document.getElementById("research-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = document.getElementById("research-query").value.trim();
    if (!query) return;
    setStatus("Thinking");
    const payload = await api("/api/research", {
      method: "POST",
      body: JSON.stringify({
        query,
        symbol: state.activeTicker,
        useWeb: document.getElementById("research-use-web").checked,
        useLlm: document.getElementById("research-use-llm").checked,
      }),
    });
    state.researchResult = payload;
    document.querySelector('[data-tab="research"]').click();
    renderResearch();
    flashStatus("Answer ready", 1600);
  });
}

async function init() {
  setStatus("Loading data");
  bindEvents();
  await Promise.all([loadConfig(), loadPresets(), loadSavedWatchlists()]);
  await refreshDashboard();
  window.setInterval(refreshDashboard, 180000);
}

init().catch((error) => {
  console.error(error);
  document.getElementById("headline-track").innerHTML = `<span>Backend unavailable. Start server.py to enable the full-stack dashboard.</span>`;
});
