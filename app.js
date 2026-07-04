const STORAGE_KEYS = {
  watchlist: "financial-board-fullstack-watchlist",
  activeTicker: "financial-board-fullstack-active",
  recentTickers: "financial-board-recent-tickers",
  chartRange: "financial-board-chart-range",
  chartFeatures: "financial-board-chart-features",
  eventCategory: "financial-board-event-category",
  boardHidden: "financial-board-market-board-hidden",
  benchmarksCollapsed: "financial-board-benchmarks-collapsed",
  detailMode: "financial-board-detail-mode",
  region: "financial-board-region",
  dossierOrder: "financial-board-dossier-order",
  dataFlow: "financial-board-data-flow",
  sectorMatrix: "financial-board-sector-matrix",
  marketHeatMap: "financial-board-market-heat-map",
  dashboardCache: "financial-board-dashboard-cache-v2",
  brandIntroSeen: "financial-board-brand-intro-v2",
};

const REFRESH_INTERVALS = {
  quotes: 7_000,
  overview: 20_000,
  globalMarkets: 15_000,
  dashboard: 600_000,
  radar: 900_000,
  events: 1_800_000,
  sectorsLive: 20_000,
  historyActive: 3_500,
  historyIdle: 30_000,
  chartLive: 1_500,
};

const DASHBOARD_CACHE_MAX_AGE_MS = 10 * 60_000;

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

const CLASSIC_QUANT_REFERENCES = [
  {
    title: "Lo, Mamaysky, and Wang",
    year: 2000,
    why: "A classic bridge between chart structure and statistical testing, useful for thinking about trend and reversal without treating patterns as magic.",
    url: "https://doi.org/10.1111/0022-1082.00265",
    track: "Classic",
  },
  {
    title: "Piotroski F-Score",
    year: 2000,
    why: "A practical way to separate cheap-and-healthy from cheap-and-broken, which is why quality overlays matter in value signals.",
    url: "https://doi.org/10.1111/1475-679X.00009",
    track: "Classic",
  },
  {
    title: "Acharya and Pedersen Liquidity Risk",
    year: 2003,
    why: "Useful reminder that price alone is not enough; participation and liquidity conditions change expected return and risk.",
    url: "https://doi.org/10.1016/j.jfineco.2004.06.001",
    track: "Classic",
  },
  {
    title: "Gatev, Goetzmann, and Rouwenhorst",
    year: 2006,
    why: "A classic mean-reversion reference that helps explain why spread and reversion signals can work, and when they stop working.",
    url: "https://doi.org/10.1093/rfs/hhj020",
    track: "Classic",
  },
];

const ACADEMY_CONTENT = [
  {
    title: "Classic core first",
    body:
      "The engine starts from classic market signals such as momentum, mean reversion, volatility, valuation, beta, and participation before any modern overlay is considered.",
  },
  {
    title: "Radar layer",
    body:
      "The radar is the event override layer. Wars, policy shifts, deals, sanctions, and earnings shocks can matter more than a slow-moving factor model for short periods.",
  },
  {
    title: "Model lab",
    body:
      "The lab shows what the current methodology would have done on observed history, so forecast confidence is always paired with actual error and hit-rate evidence.",
  },
  {
    title: "Modern overlay",
    body:
      "Modern research is used as an overlay, not a replacement. If a newer method improves uncertainty, regime adaptation, or speed, it complements the classic stack instead of hiding it.",
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

const REGION_LABELS = {
  us: "United States",
  india: "India",
};

const API_BASE =
  window.location.protocol === "file:"
    ? "http://127.0.0.1:8000"
    : "";

const COMPACT_SECTIONS = [
  { id: "market-radar", label: "Radar" },
  { id: "market-board-panel", label: "Board" },
  { id: "overview", label: "Overview" },
  { id: "stock-dossier-panel", label: "Dossier" },
  { id: "bond-market", label: "Bonds" },
  { id: "events-calendar", label: "Events" },
  { id: "methodology", label: "Method" },
  { id: "comparison", label: "Compare" },
];

/*
 * Dossier layout — 12-column grid with three "shape" classes:
 *   narrow (span 3)  — vertical stat cards, 4 across a row
 *   wide   (span 6)  — horizontal tables, 2 across a row
 *   full   (span 12) — long strips on their own row (bar charts, graphs)
 *
 * Default order groups by shape so each row sums to 12 with no gaps:
 *   Row 1: day(3) + ma(3) + fundamentals(3) + activity(3) = 12   (4 verticals)
 *   Row 2: peers(6) + consensus(6)                        = 12   (2 mid-horizontals)
 *   Row 3: benchmarks(12)                                 = 12   (full strip — bar comparison)
 *   Row 4: links(12)                                      = 12   (full strip — influence graph)
 *   Row 5: metrics(12)                                    = 12   (full-width metric drawer)
 *
 * Users can drag cards into any order; spans are all divisors of 12 so any
 * stored permutation still tiles cleanly.
 */
const DEFAULT_DOSSIER_ORDER = [
  "day",
  "ma",
  "fundamentals",
  "activity",
  "peers",
  "consensus",
  "benchmarks",
  "links",
  "metrics",
];

const DOSSIER_CARD_META = {
  day: { title: "Day snapshot", span: 3, tier: "primary", value: "live" },
  ma: { title: "Trend stack", span: 3, tier: "primary", value: "predictive" },
  fundamentals: { title: "Fundamentals", span: 3, tier: "support", value: "supporting" },
  activity: { title: "Range watch", span: 3, tier: "support", value: "predictive" },
  peers: { title: "Peer comparison", span: 6, tier: "primary", value: "context" },
  consensus: { title: "Expert consensus", span: 6, tier: "support", value: "external" },
  benchmarks: { title: "Benchmark comparison", span: 12, tier: "primary", value: "context" },
  links: { title: "Influence graph", span: 12, tier: "support", value: "source" },
  metrics: { title: "Show all metrics", span: 12, tier: "metrics", value: "reference" },
};

function dossierCardClass(key, extra = "") {
  const meta = DOSSIER_CARD_META[key] || {};
  return [
    "dossier-card",
    `dossier-span-${meta.span || 3}`,
    `dossier-tier-${meta.tier || "support"}`,
    extra,
  ].filter(Boolean).join(" ");
}

function dossierCardBody(markup, extra = "") {
  const bodyClass = ["dossier-card-body", extra].filter(Boolean).join(" ");
  return `<div class="${bodyClass}">${markup}</div>`;
}

const state = {
  watchlist: loadStoredWatchlist(),
  activeTicker: localStorage.getItem(STORAGE_KEYS.activeTicker) || "BHARTIARTL.NS",
  selectedRegion: localStorage.getItem(STORAGE_KEYS.region) || "india",
  recentTickers: loadStoredRecentTickers(),
  chartRange: localStorage.getItem(STORAGE_KEYS.chartRange) || "1M",
  chartFeatures: loadStoredChartFeatures(),
  eventCategory: localStorage.getItem(STORAGE_KEYS.eventCategory) || "markets",
  eventResult: null,
  dashboard: null,
  presets: [],
  savedWatchlists: [],
  config: null,
  labResult: null,
  statusTimer: null,
  marketClockTimer: null,
  researchResult: null,
  researchLoading: false,
  researchError: "",
  quoteStream: null,
  eventRequestId: 0,
  eventTimer: null,
  overviewTimer: null,
  quotesTimer: null,
  quotesRequestId: 0,
  globalMarketTimer: null,
  sectorMatrixTimer: null,
  dashboardTimer: null,
  historyPollTimer: null,
  eventCache: {},
  eventLastQuery: "",
  liveQuoteMemory: {},
  alerts: [],
  alertCooldowns: {},
  radarHeadlineDetail: null,
  marketSessionTimer: null,
  dashboardRequestId: 0,
  overviewRequestId: 0,
  searchRequestId: 0,
  academyRequestId: 0,
  radarRequestId: 0,
  academyDetail: null,
  academyCache: {},
  bootReady: false,
  radarTimer: null,
  boardHidden: localStorage.getItem(STORAGE_KEYS.boardHidden) === "1",
  benchmarksCollapsed: localStorage.getItem(STORAGE_KEYS.benchmarksCollapsed) !== "0",
  detailMode: localStorage.getItem(STORAGE_KEYS.detailMode) === "1",
  eventCategoryPinned: false,
  recentLastAdded: "",
  recentAddTimer: null,
  visualValueMemory: {},
  impactGraphPositions: {},
  impactGraphCy: null,
  impactResizeTimer: null,
  pendingImpactGraph: null,
  revealObserver: null,
  dossierMasonryFrame: null,
  dossierResizeObserver: null,
  lastOverviewChartRefreshAt: 0,
  lastLiveChartRenderAt: 0,
  chartHoverFrame: null,
  chartHoverEvent: null,
  historyWarmupKeys: new Set(),
  dossierOrder: loadStoredDossierOrder(),
  dataFlow: loadStoredDataFlowState(),
  sectorStripSectors: [],
  marketHeatMap: null,
  marketHeatMapRequestId: 0,
  marketHeatMapObserver: null,
  pendingHeatMapWarmup: null,
  operations: null,
  operationsLoading: false,
  operationsPollTimer: null,
};

if (state.watchlist.length === 0) {
  state.watchlist = ["BHARTIARTL.NS", "ICICIBANK.NS", "GLENMARK.NS"];
}

const marketClockKeys = new WeakMap();

/* ── Skeleton Loading Helpers ──────────────────────────────────────────────── */
function showSkeleton(containerId, template) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.classList.add("section-reveal");
  el.innerHTML = template;
}
function revealSection(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.classList.add("revealed");
}
function initSkeletons() {
  showSkeleton("hero-stats", `<div class="skel skel-pill"></div><div class="skel skel-pill"></div><div class="skel skel-pill"></div>`);
  showSkeleton("prediction-panel", `<div class="skel-grid"><div class="skel skel-card"></div><div class="skel skel-card"></div><div class="skel skel-card"></div></div>`);
  const chartCard = document.querySelector(".hero-chart-card");
  if (chartCard && !chartCard.querySelector(".skel-chart")) {
    const placeholder = document.createElement("div");
    placeholder.className = "skel skel-chart skel-chart-placeholder";
    chartCard.appendChild(placeholder);
  }
  showSkeleton("stock-dossier", `<div class="skel skel-card"></div><div class="skel skel-card"></div>`);
}
function clearChartSkeleton() {
  document.querySelector(".skel-chart-placeholder")?.remove();
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
      chartType: "line",
      sma20: true,
      sma50: true,
      bands: false,
      ...(JSON.parse(localStorage.getItem(STORAGE_KEYS.chartFeatures) || "{}") || {}),
    };
  } catch {
    return { chartType: "line", sma20: true, sma50: true, bands: false };
  }
}

function loadStoredDossierOrder() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEYS.dossierOrder) || "[]");
    const oldDefaultOrders = [
      ["day", "ma", "peers", "benchmarks", "metrics", "activity", "fundamentals", "consensus", "links"],
      ["day", "ma", "peers", "benchmarks", "metrics", "fundamentals", "activity", "consensus", "links"],
    ];
    if (Array.isArray(stored) && oldDefaultOrders.some((order) => stored.join("|") === order.join("|"))) {
      return DEFAULT_DOSSIER_ORDER.slice();
    }
    return DEFAULT_DOSSIER_ORDER.filter((key) => stored.includes(key)).length
      ? DEFAULT_DOSSIER_ORDER.filter((key) => stored.includes(key)).sort((a, b) => stored.indexOf(a) - stored.indexOf(b))
      : DEFAULT_DOSSIER_ORDER.slice();
  } catch {
    return DEFAULT_DOSSIER_ORDER.slice();
  }
}

function persistDossierOrder() {
  localStorage.setItem(STORAGE_KEYS.dossierOrder, JSON.stringify(state.dossierOrder));
}

function loadStoredDataFlowState() {
  const fallback = {
    expanded: false,
    x: null,
    y: null,
    tasks: {},
    history: { jobs: [], active: [] },
    stream: "connecting",
    lastUpdated: "",
    polling: false,
    hidden: false,
    hideTimer: null,
    boot: { config: false, presets: false, watchlists: false },
    lastError: "",
  };
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEYS.dataFlow) || "{}") || {};
    return {
      ...fallback,
      ...stored,
      tasks: {},
      history: { jobs: [], active: [] },
      boot: { ...fallback.boot },
      polling: false,
      hidden: false,
      hideTimer: null,
      lastError: "",
    };
  } catch {
    return fallback;
  }
}

function persistDataFlowState() {
  const { expanded, x, y } = state.dataFlow || {};
  localStorage.setItem(STORAGE_KEYS.dataFlow, JSON.stringify({ expanded: Boolean(expanded), x, y }));
}

function dashboardCacheKey() {
  return JSON.stringify({
    active: state.activeTicker,
    watchlist: state.watchlist,
    chartRange: state.chartRange,
    region: state.selectedRegion,
  });
}

function saveDashboardCache(payload) {
  if (!payload?.active?.symbol || !payload?.watchlist?.length) return;
  try {
    localStorage.setItem(STORAGE_KEYS.dashboardCache, JSON.stringify({
      key: dashboardCacheKey(),
      ts: Date.now(),
      payload,
    }));
  } catch (_) { /* localStorage quota — cache is optional */ }
}

function loadDashboardCache() {
  try {
    const cached = JSON.parse(localStorage.getItem(STORAGE_KEYS.dashboardCache) || "null");
    if (!cached?.payload || cached.key !== dashboardCacheKey()) return null;
    if (Date.now() - Number(cached.ts || 0) > DASHBOARD_CACHE_MAX_AGE_MS) {
      localStorage.removeItem(STORAGE_KEYS.dashboardCache);
      return null;
    }
    return cached.payload;
  } catch {
    return null;
  }
}

function hydrateDashboardFromPayload(payload, { fromCache = false } = {}) {
  if (!payload?.active || !payload?.watchlist?.length) return false;
  state.dashboard = payload;
  state.selectedRegion = payload.selectedRegion || state.selectedRegion;
  state.watchlist = payload.watchlist.map((item) => item.symbol);
  state.activeTicker = payload.active.symbol;
  if (!state.eventCategoryPinned) {
    state.eventCategory = payload.active?.eventFocus?.category || state.eventCategory;
  }
  if (!state.labResult || state.labResult.symbol !== state.activeTicker) {
    state.labResult = payload.active.lab;
  }
  state.academyDetail = state.academyCache[state.activeTicker] || null;
  if (payload.active?.historySeries?.length) {
    saveChartCache(payload.active.symbol, state.chartRange, payload.active.historySeries);
  }
  if (!fromCache && payload.active?.name && payload.active?.price) {
    pushRecentTicker(payload.active.symbol, payload.active.name);
  }
  return true;
}

function persistWatchlist() {
  localStorage.setItem(STORAGE_KEYS.watchlist, JSON.stringify(state.watchlist));
  localStorage.setItem(STORAGE_KEYS.activeTicker, state.activeTicker);
  localStorage.setItem(STORAGE_KEYS.recentTickers, JSON.stringify(state.recentTickers));
  localStorage.setItem(STORAGE_KEYS.chartRange, state.chartRange);
  localStorage.setItem(STORAGE_KEYS.chartFeatures, JSON.stringify(state.chartFeatures));
  localStorage.setItem(STORAGE_KEYS.eventCategory, state.eventCategory);
  localStorage.setItem(STORAGE_KEYS.boardHidden, state.boardHidden ? "1" : "0");
  localStorage.setItem(STORAGE_KEYS.region, state.selectedRegion);
}

function pushRecentTicker(symbol, name = "") {
  if (!symbol) return;
  const isNewFront = state.recentTickers[0]?.symbol !== symbol;
  state.recentTickers = [{ symbol, name }]
    .concat(state.recentTickers.filter((item) => item.symbol !== symbol))
    .slice(0, 10);
  state.recentLastAdded = isNewFront ? symbol : "";
  persistWatchlist();
}

function movingAverage(values, period) {
  return values.map((_, index) => {
    if (index + 1 < period) return null;
    const window = values.slice(index + 1 - period, index + 1);
    return window.reduce((sum, value) => sum + value, 0) / window.length;
  });
}

function liveBadgeMarkup(label = "Live update") {
  return `<span class="live-badge-inline" aria-label="${label}" title="${label}"></span>`;
}

function setTextIfChanged(node, value) {
  if (!node) return;
  const text = String(value ?? "");
  if (node.childNodes.length === 1 && node.firstChild?.nodeType === Node.TEXT_NODE) {
    if (node.firstChild.nodeValue !== text) {
      node.firstChild.nodeValue = text;
    }
    return;
  }
  if (node.textContent !== text) {
    node.textContent = text;
  }
}

function setHTMLIfChanged(node, html) {
  if (!node) return false;
  const markup = String(html ?? "");
  if (node.innerHTML !== markup) {
    node.innerHTML = markup;
    return true;
  }
  return false;
}

function setAttributeIfChanged(node, name, value) {
  if (!node) return;
  const next = String(value ?? "");
  if (node.getAttribute(name) !== next) {
    node.setAttribute(name, next);
  }
}

function setClassIfChanged(node, className) {
  if (!node) return;
  const next = String(className ?? "");
  if (node.className !== next) {
    node.className = next;
  }
}

function setupScrollReveal() {
  if (!state.revealObserver) {
    state.revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            entry.target.classList.add("revealed");
          }
        });
      },
      { threshold: 0.08 },
    );
  }
  document.querySelectorAll(".glass-panel, .macro-panel, .hero-chart-card, .stock-dossier-panel").forEach((node) => {
    if (node.dataset.revealObserved === "1") return;
    node.dataset.revealObserved = "1";
    node.classList.add("scroll-reveal");
    const rect = node.getBoundingClientRect();
    if (rect.top < window.innerHeight && rect.bottom > 0) {
      node.classList.add("is-visible", "revealed");
    }
    state.revealObserver.observe(node);
  });
}

function applyRevealObserver() {
  if (!state.revealObserver) return;
  document.querySelectorAll("[data-reveal]:not(.reveal-on-scroll)").forEach((node) => {
    node.classList.add("reveal-on-scroll");
    state.revealObserver.observe(node);
  });
}

function isFreshUpdate(timestamp, minutes = 30) {
  if (!timestamp) return false;
  const parsed = new Date(timestamp);
  if (Number.isNaN(parsed.getTime())) return false;
  return Date.now() - parsed.getTime() <= minutes * 60 * 1000;
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
  const controller = new AbortController();
  const timeoutMs = options.timeoutMs || 15000;
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  let response;
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const taskId = startDataFlowTask(path);
  try {
    response = await fetch(url, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      signal: controller.signal,
      ...options,
    });
    finishDataFlowTask(taskId, response.ok ? "done" : "error");
  } catch (error) {
    finishDataFlowTask(taskId, "error");
    throw error;
  } finally {
    window.clearTimeout(timer);
  }

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

function isUnavailableSector(s = {}) {
  const source = String(s.source || "").toLowerCase();
  const price = Number(s.price);
  const pct = Number(s.changePct ?? s.changePercent ?? s.change);
  return source.includes("unavailable") && (!Number.isFinite(price) || price <= 0) && (!Number.isFinite(pct) || Math.abs(pct) < 0.0001);
}

function hasUsableSectorData(sectors = []) {
  return Array.isArray(sectors) && sectors.some((sector) => !isUnavailableSector(sector));
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

function formatIndexLevel(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "n/a";
  const fractionDigits = Math.abs(numeric) >= 1000 ? 2 : 2;
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(numeric);
}

function formatSignedCurrency(value, currency = "USD") {
  const numeric = Number(value || 0);
  return `${numeric >= 0 ? "+" : ""}${formatCurrency(numeric, currency)}`;
}

function selectedRegionPayload() {
  return state.dashboard?.regions?.[state.selectedRegion] || null;
}

function selectedRegionMeta() {
  const payload = selectedRegionPayload();
  if (payload) return payload;
  const option = (state.dashboard?.regionOptions || []).find((item) => item.key === state.selectedRegion);
  if (option) return { key: option.key, label: option.label };
  return {
    key: state.selectedRegion,
    label: REGION_LABELS[state.selectedRegion] || formatRegionLabel(state.selectedRegion),
  };
}

function renderRegionPanels() {
  renderTopbar();
  renderOverview();
  renderBondMarket();
  renderInflationView();
  renderEquityContext();
  renderMacroEvents();
  renderWatchlistImplications();
  renderComparison();
  renderOperations();
}

function liveValueClass(key, value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "";
  const previous = Number(state.visualValueMemory[key]);
  state.visualValueMemory[key] = numeric;
  if (!Number.isFinite(previous) || previous === numeric) return "";
  return numeric > previous ? "flash-up" : "flash-down";
}

function setModelErrorNote(forecast) {
  const node = document.getElementById("model-error-note");
  if (!node || !forecast) return;
  const source = forecast.maeSource || "";
  const samples = Number(forecast.backtestSamples || 0);
  const hitRate = Number(forecast.backtestHitRate || 0);
  const learning = forecast.learning || {};
  const runs = Number(learning.trainingRuns || 0);
  const biasApplied = Number(learning.biasApplied || 0);
  if (source === "walk-forward" && samples > 0) {
    const parts = [`Walk-forward · ${samples} samples · ${hitRate.toFixed(0)}% hit`];
    if (runs > 0) parts.push(`retrained ${runs}×`);
    if (Math.abs(biasApplied) >= 0.05) parts.push(`bias ${biasApplied >= 0 ? "−" : "+"}${Math.abs(biasApplied).toFixed(2)}pp`);
    node.textContent = parts.join(" · ");
    node.title = "Empirical mean absolute % error from walk-forward backtest. Bias = mean signed return error subtracted from the forecast (EMA-blended across runs).";
  } else {
    node.textContent = "Vol-scaled heuristic · awaiting backtest";
    node.title = "Not enough history yet for a walk-forward backtest. Showing a volatility/beta-scaled estimate; the empirical MAE will replace this once ≥6 windows are available.";
  }
}

function buildPriceFlipMarkup(value, currency = "USD") {
  return formatCurrency(value, currency)
    .split("")
    .map((char) => {
      const cls = /\d/.test(char) ? "digit" : char === "." ? "sep decimal" : char.trim() ? "sep symbol" : "sep space";
      const safe = char === " " ? "&nbsp;" : char;
      return `<span class="price-flip ${cls}">${safe}</span>`;
    })
    .join("");
}

function animateSvgRefresh(svg, { force = false } = {}) {
  if (!svg?.animate) return;
  if (!force && svg.dataset.hasAnimated === "1") return;
  svg.dataset.hasAnimated = "1";
  svg.animate(
    [
      { opacity: 0.36, transform: "translateY(8px) scaleY(0.94)" },
      { opacity: 1, transform: "translateY(0) scaleY(1)" },
    ],
    {
      duration: 420,
      easing: "cubic-bezier(0.22, 1, 0.36, 1)",
      fill: "both",
    },
  );
}

function renderOverviewLowerPanels() {
  /* Factor map and catalyst list removed — prediction panel and dossier cover this data. */
}

function dossierMetric(value, kind = "plain", currency = "") {
  if (value === null || value === undefined || value === "" || value === "Unavailable") return "Unavailable";
  const number = Number(value);
  if (!Number.isFinite(number)) return String(value);
  if (kind === "currency") return formatCurrency(number, currency);
  if (kind === "large") return formatCompactNumber(number);
  if (kind === "percent") return formatPercent(number);
  if (kind === "ratio") return `${number.toFixed(2)}x`;
  return number.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function renderBenchmarkBars(items = []) {
  if (!items.length) return `<div class="dossier-empty">Benchmark history unavailable.</div>`;
  const usable = items.filter((item) => Array.isArray(item.series) && item.series.length && Number.isFinite(Number(item.returnPercent)));
  if (!usable.length) return `<div class="dossier-empty">Benchmark history is warming up from local cache and provider history.</div>`;
  const maxAbs = Math.max(4, ...usable.map((item) => Math.abs(Number(item.returnPercent || 0))));
  return `
    <div class="benchmark-bars">
      ${items.map((item) => {
        const available = Array.isArray(item.series) && item.series.length && Number.isFinite(Number(item.returnPercent));
        const value = available ? Number(item.returnPercent || 0) : 0;
        const width = Math.max(4, Math.abs(value) / maxAbs * 100);
        return `
          <div class="benchmark-row ${available ? "" : "is-pending"}">
            <span title="${item.symbol || item.label}">${item.label}</span>
            <div class="benchmark-bar-track" aria-label="${item.label} normalized return">
              <div class="benchmark-bar ${value >= 0 ? "positive" : "negative"}" style="width:${available ? width : 0}%"></div>
            </div>
            <strong class="${available ? (value >= 0 ? "positive" : "negative") : "pending"}">${available ? formatPercent(value) : "Pending"}</strong>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function dossierValueRecord(value, formatter, source = "Provider") {
  const unavailable = value === null || value === undefined || value === "" || value === "Unavailable" || (typeof value === "number" && !Number.isFinite(value));
  return {
    label: unavailable ? "Unavailable" : formatter(value),
    available: !unavailable,
    source,
  };
}

function activityMetricRecord(unusual = {}, key, fallbackValue, formatter, source = "Provider") {
  const metric = unusual.metrics?.[key];
  if (metric && typeof metric === "object") {
    return {
      label: metric.label || "Unavailable",
      available: metric.value !== null && metric.value !== undefined,
      source: metric.source || source,
      status: metric.status || "",
    };
  }
  return dossierValueRecord(fallbackValue, formatter, source);
}

function renderDossierCard(key, { kicker = "", title = "", subtitle = "", summary = "", body = "", extraClass = "" } = {}) {
  const meta = DOSSIER_CARD_META[key] || {};
  const panelId = `dossier-panel-${key}`;
  return `
    <section id="dossier-${key}" class="${dossierCardClass(key, extraClass)}" draggable="true" data-dossier-card="${key}" data-reveal>
      <button class="dossier-drag-handle" type="button" aria-label="Move ${meta.title || key}" title="Move card">
        <span aria-hidden="true"></span>
      </button>
      <div class="dossier-card-title" id="${panelId}-title">
        <span>${kicker || meta.value || "Dossier"}</span>
        <strong>${title || meta.title || key}</strong>
        <small>${subtitle || "Source noted"}</small>
      </div>
      ${summary ? `<div class="dossier-card-summary">${summary}</div>` : ""}
      <div id="${panelId}" class="dossier-card-body" aria-labelledby="${panelId}-title">
        ${body}
      </div>
    </section>
  `;
}

function buildMetricCommandGroups(active, dossier, day, fundamentals, unusual) {
  const currency = active.currency;
  const maItems = dossier.movingAverages || [];
  const provenance = dossier.sourceProvenance || [];
  const activity = unusual.metrics || {};
  return [
    {
      section: "Quote",
      source: day.source || active.dataSource || "Quote provider",
      metrics: [
        ["Price", active.price, (value) => formatCurrency(value, currency)],
        ["Open", day.open, (value) => dossierMetric(value, "currency", currency)],
        ["Previous close", day.previousClose, (value) => dossierMetric(value, "currency", currency)],
        ["Session", active.marketState || active.marketSession?.status, (value) => String(value)],
      ],
    },
    {
      section: "Range",
      source: day.source || "Quote provider",
      metrics: [
        ["Day low", day.dayLow, (value) => dossierMetric(value, "currency", currency)],
        ["Day high", day.dayHigh, (value) => dossierMetric(value, "currency", currency)],
        ["52W low", day.fiftyTwoWeekLow, (value) => dossierMetric(value, "currency", currency)],
        ["52W high", day.fiftyTwoWeekHigh, (value) => dossierMetric(value, "currency", currency)],
        ["Breakout", activity.breakout?.label || unusual.breakout, (value) => String(value)],
      ],
    },
    {
      section: "Volume",
      source: day.source || "Quote provider",
      metrics: [
        ["Volume", day.volume, (value) => dossierMetric(value, "large")],
        ["Avg volume", day.averageVolume, (value) => dossierMetric(value, "large")],
        ["Volume ratio", activity.volumeRatio?.label || unusual.volumeRatio, (value) => typeof value === "string" ? value : dossierMetric(value, "ratio")],
      ],
    },
    {
      section: "Fundamentals",
      source: fundamentals.source || "Quote summary",
      metrics: [
        ["EPS", fundamentals.eps, (value) => dossierMetric(value)],
        ["Revenue", fundamentals.revenue, (value) => dossierMetric(value, "large")],
        ["Net income", fundamentals.netIncome, (value) => dossierMetric(value, "large")],
        ["ROE", fundamentals.roe, (value) => dossierMetric(Number(value) * 100, "percent")],
        ["Sales growth", fundamentals.salesGrowth, (value) => dossierMetric(Number(value) * 100, "percent")],
        ["Debt/equity", fundamentals.debtToEquity, (value) => dossierMetric(value)],
      ],
    },
    {
      section: "Trend",
      source: "Local historical cache",
      metrics: maItems.map((item) => [item.label, item.value, (value) => `${dossierMetric(value, "currency", currency)} · ${item.state || "Unknown"}`]),
    },
    {
      section: "Benchmark",
      source: "Local historical cache",
      metrics: (dossier.benchmarkComparison || []).map((item) => [item.label, item.returnPercent, (value) => formatPercent(value)]),
    },
    {
      section: "Provenance",
      source: "Source labels",
      metrics: provenance.map((item) => [item.label, item.usedFor, (value) => String(value)]),
    },
  ];
}

function renderMetricCommandCard(groups) {
  const records = groups.flatMap((group) =>
    group.metrics.map(([label, value, formatter]) => {
      const record = dossierValueRecord(value, formatter, group.source);
      return { ...record, labelName: label, group: group.section };
    }),
  );
  const available = records.filter((item) => item.available).length;
  const missing = records.length - available;
  const top = records.filter((item) => item.available).slice(0, 3);
  return {
    summary: `
      <div class="metric-command-summary">
        <span>${available} available</span>
        <span>${missing} unavailable</span>
        ${top.map((item) => `<span>${item.labelName}: ${item.label}</span>`).join("")}
      </div>
    `,
    body: `
      <label class="metric-command-search">
        <span>Find metric</span>
        <input class="metric-filter-input" type="search" placeholder="Search ROE, SMA 50, volume…" data-metric-filter />
      </label>
      <div class="metric-command-grid">
        ${groups.map((group) => `
          <section class="metric-command-group" data-metric-group>
            <strong>${group.section}</strong>
            <small>${group.source}</small>
            <div>
              ${group.metrics.map(([label, value, formatter]) => {
                const record = dossierValueRecord(value, formatter, group.source);
                return `<span class="${record.available ? "" : "is-missing"}" data-metric-pill="${`${group.section} ${label} ${record.label}`.toLowerCase()}">${label}: ${record.label}<em>${record.source}</em></span>`;
              }).join("")}
            </div>
          </section>
        `).join("")}
      </div>
    `,
  };
}

function renderRangeWatchStrip(unusual) {
  const metrics = [
    ["2D move", activityMetricRecord(unusual, "twoDayMove", unusual.twoDayMove, formatPercent, "Local history")],
    ["Gap", activityMetricRecord(unusual, "gapPercent", unusual.gapPercent, formatPercent, "Quote provider")],
    ["Volume", activityMetricRecord(unusual, "volumeRatio", unusual.volumeRatio, (value) => `${Number(value).toFixed(2)}x`, "Quote provider")],
    ["Breakout", unusual.metrics?.breakout || { label: unusual.breakout || "Range watch", available: true, source: "Quote provider", status: "" }],
  ];
  return `
    <section id="dossier-activity" class="${dossierCardClass("activity", "range-watch-card")}" draggable="true" data-dossier-card="activity" data-reveal>
      <button class="dossier-drag-handle" type="button" aria-label="Move Range watch" title="Move card">
        <span aria-hidden="true"></span>
      </button>
      <div class="dossier-card-title">
        <span>Range watch</span>
        <strong>${unusual.breakout || unusual.metrics?.breakout?.label || "Range watch"}</strong>
        <small>Gap, 2D, volume</small>
      </div>
      <div class="range-watch-stack">
        ${metrics.map(([label, item]) => `
          <article class="${item.available === false ? "is-missing" : ""}">
            <span>${label}</span>
            <strong>${item.label || "Unavailable"}</strong>
            <small>${item.status || item.source || "Source noted"}</small>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderMarketDiscovery(discoveryItems, sourceLabel) {
  return `
    <div class="discovery-compact-head">
      <div><span>Market discovery</span><strong>Unusual movers</strong></div>
      <small>${sourceLabel || "Local scan"}</small>
    </div>
    <div class="discovery-chip-stack">
      ${discoveryItems.length ? discoveryItems.map((item) => `
        <button type="button" data-symbol="${item.symbol}">
          <strong>${String(item.symbol || "").replace(/\.(NS|BO)$/i, "")}</strong>
          <span>${formatPercent(item.latestMove)} latest</span>
          <span>${formatPercent(item.twoDayMove)} 2D</span>
          <em>${item.reason} · ${item.confidence}</em>
        </button>
      `).join("") : `<div class="dossier-empty">No unusual watchlist movers yet.</div>`}
    </div>
  `;
}

function dossierRailCell(label, value, { className = "", sub = "", liveKey = "" } = {}) {
  const numeric = Number(String(value).replace(/[^\d.+-]/g, ""));
  const liveClass = liveKey ? liveValueClass(liveKey, numeric) : "";
  const classes = ["v", "live-number", className, liveClass].filter(Boolean).join(" ");
  return `
    <div class="rail-cell">
      <div class="k">${escapeHtml(label)}</div>
      <div class="${classes}">${escapeHtml(value || "Unavailable")}</div>
      ${sub ? `<div class="vsub">${sub}</div>` : ""}
    </div>
  `;
}

function renderDossierRail(active = {}) {
  const node = document.getElementById("dossier-rail-summary");
  const status = document.getElementById("dossier-rail-status");
  if (!node) return;
  const dossier = active.stockDossier || {};
  const day = dossier.daySnapshot || {};
  const fundamentals = dossier.fundamentals || {};
  const consensus = dossier.expertConsensus || {};
  const freshness = quoteFreshnessForDisplay(active);
  const freshnessMarkup = freshnessBadgeMarkup(freshness);
  const sourceLabel = formatSourceLabel(day.source || active.dataSource || "Quote provider");
  const scores = fundamentals.scores || {};
  const roeLabel = fundamentals.roe === null || fundamentals.roe === undefined || fundamentals.roe === ""
    ? "Unavailable"
    : dossierMetric(Number(fundamentals.roe) * 100, "percent");
  const benchmarks = (dossier.benchmarkComparison || []).slice(0, 3);
  const peers = (dossier.peerComparison || []).slice(0, 3);
  const movingAverages = (dossier.movingAverages || []).filter((item) => item.value !== null && item.value !== undefined).slice(0, 2);
  const consensusLabel = consensus.rating || "External tone unavailable";
  const statusText = freshness.label || (freshness.isStale ? "Stale" : "Live");
  setHTMLIfChanged(status, `<span class="rail-live-dot ${freshness.isStale ? "is-stale" : ""}"></span>${escapeHtml(statusText)}`);

  setTextIfChanged(document.getElementById("rail-2d-move"), active.changePercent === null || active.changePercent === undefined ? "Live" : formatPercent(active.changePercent));
  setClassIfChanged(document.getElementById("rail-2d-move"), `v live-number ${Number(active.changePercent || 0) >= 0 ? "up positive" : "down negative"} ${liveValueClass(`rail:${active.symbol}:move`, active.changePercent)}`);
  const gap = Number(day.open) && Number(day.previousClose)
    ? ((Number(day.open) - Number(day.previousClose)) / Number(day.previousClose)) * 100
    : null;
  setTextIfChanged(document.getElementById("rail-gap"), Number.isFinite(gap) ? formatPercent(gap) : "Unavailable");
  setClassIfChanged(document.getElementById("rail-gap"), `v live-number ${Number(gap || 0) >= 0 ? "up positive" : "down negative"} ${liveValueClass(`rail:${active.symbol}:gap`, gap)}`);
  setTextIfChanged(document.getElementById("rail-volume"), dossierMetric(day.volume, "large"));
  setClassIfChanged(document.getElementById("rail-volume"), `v live-number ${liveValueClass(`rail:${active.symbol}:volume`, day.volume)}`);
  setTextIfChanged(document.getElementById("rail-breakout"), dossier.unusualActivity?.breakout || dossier.unusualActivity?.metrics?.breakout?.label || "Range watch");

  setHTMLIfChanged(node, `
    <div class="rail-source-row">
      <span>${freshnessMarkup}</span>
      <span>${escapeHtml(sourceLabel)}</span>
    </div>
    <div class="rail-grid">
      ${dossierRailCell("Valuation", dossierMetric(scores.valuation), { liveKey: `rail:${active.symbol}:valuation` })}
      ${dossierRailCell("Risk", dossierMetric(scores.risk), { className: "warn", liveKey: `rail:${active.symbol}:risk` })}
      ${dossierRailCell("ROE", roeLabel)}
      ${dossierRailCell("EPS", dossierMetric(fundamentals.eps), { liveKey: `rail:${active.symbol}:eps` })}
    </div>
    <div class="rail-list">
      <div class="rail-list-head"><span>Benchmarks</span><em>Moved from dossier</em></div>
      ${benchmarks.length ? benchmarks.map((item) => `
        <div class="rail-row">
          <strong>${escapeHtml(item.label || "Benchmark")}</strong>
          <span class="live-number ${Number(item.returnPercent || 0) >= 0 ? "up positive" : "down negative"} ${liveValueClass(`rail:${active.symbol}:bench:${item.label}`, item.returnPercent)}">${formatPercent(item.returnPercent || 0)}</span>
        </div>
      `).join("") : `<div class="rail-empty">Benchmark history warming from local cache.</div>`}
    </div>
    <div class="rail-list">
      <div class="rail-list-head"><span>Peers</span><em>Compact</em></div>
      ${peers.length ? peers.map((peer) => `
        <div class="rail-row">
          <strong>${escapeHtml(peer.symbol || "Peer")}</strong>
          <span>${escapeHtml(peer.oneYearReturn || peer.pe || "Unavailable")}</span>
        </div>
      `).join("") : `<div class="rail-empty">Peer comparison unavailable.</div>`}
    </div>
    <div class="rail-list">
      <div class="rail-list-head"><span>Trend</span><em>${escapeHtml(consensusLabel)}</em></div>
      ${movingAverages.length ? movingAverages.map((item) => `
        <div class="rail-row">
          <strong>${escapeHtml(item.label || "SMA")}</strong>
          <span>${escapeHtml(item.state || "Unavailable")}${item.distancePercent !== null && item.distancePercent !== undefined ? ` · ${formatPercent(item.distancePercent)}` : ""}</span>
        </div>
      `).join("") : `<div class="rail-empty">Moving averages unavailable.</div>`}
    </div>
  `);
}

function setupDossierControls(container) {
  container.querySelectorAll("[data-metric-filter]").forEach((input) => {
    input.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      container.querySelectorAll("[data-metric-pill]").forEach((pill) => {
        pill.hidden = Boolean(query) && !pill.dataset.metricPill.includes(query);
      });
      scheduleDossierMasonry(container);
    });
  });
}

function relayoutDossierMasonry(container = document.getElementById("stock-dossier")) {
  /*
   * The dossier uses a plain row-based 12-col grid where each row equalises to
   * its tallest card (`grid-auto-rows: minmax(178px, auto)`). The old masonry
   * pass computed per-card row-spans against a fine 8px row track + dense
   * packing, which let the browser reorder cards to fill gaps — that's what
   * made the layout look scrambled. We keep the function for compatibility
   * with existing call sites (drag reorder, ResizeObserver) but it now just
   * strips any inline grid-row state from previous runs.
   */
  if (!container) return;
  const cards = Array.from(container.querySelectorAll("[data-dossier-card]"));
  if (!cards.length) return;
  cards.forEach((card) => {
    card.style.gridRowEnd = "";
    card.style.removeProperty("--dossier-row-span");
  });
}

function scheduleDossierMasonry(container = document.getElementById("stock-dossier")) {
  if (!container) return;
  window.cancelAnimationFrame(state.dossierMasonryFrame);
  state.dossierMasonryFrame = window.requestAnimationFrame(() => {
    relayoutDossierMasonry(container);
  });
}

function observeDossierMasonry(container) {
  if (!container || !("ResizeObserver" in window)) {
    scheduleDossierMasonry(container);
    return;
  }
  state.dossierResizeObserver?.disconnect();
  state.dossierResizeObserver = new ResizeObserver(() => scheduleDossierMasonry(container));
  state.dossierResizeObserver.observe(container);
  scheduleDossierMasonry(container);
}

function setupDossierDrag(container) {
  const cards = Array.from(container.querySelectorAll("[data-dossier-card]"));
  if (!cards.length) return;

  const syncOrder = () => {
    state.dossierOrder = Array.from(container.querySelectorAll("[data-dossier-card]"))
      .map((card) => card.dataset.dossierCard)
      .filter(Boolean);
    persistDossierOrder();
  };

  cards.forEach((card) => {
    card.addEventListener("dragstart", (event) => {
      card.classList.add("dragging");
      container.classList.add("is-dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", card.dataset.dossierCard || "");
    });

    card.addEventListener("dragend", () => {
      card.classList.remove("dragging");
      container.classList.remove("is-dragging");
      syncOrder();
      scheduleDossierMasonry(container);
    });
  });

  container.ondragover = (event) => {
    event.preventDefault();
    const dragging = container.querySelector(".dossier-card.dragging");
    if (!dragging || !(event.target instanceof Element)) return;

    // Find all non-dragging cards; pick closest by center distance
    const siblings = Array.from(container.querySelectorAll("[data-dossier-card]:not(.dragging)"));
    if (!siblings.length) return;

    let closest = null;
    let closestDist = Infinity;
    for (const sibling of siblings) {
      const rect = sibling.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const dist = Math.hypot(event.clientX - centerX, event.clientY - centerY);
      if (dist < closestDist) { closestDist = dist; closest = sibling; }
    }
    if (!closest) return;

    const rect = closest.getBoundingClientRect();
    // Use Y position primarily; for same-row cards use X
    const midY = rect.top + rect.height / 2;
    const midX = rect.left + rect.width / 2;
    const insertBefore = event.clientY < midY || (Math.abs(event.clientY - midY) < 24 && event.clientX < midX);
    container.insertBefore(dragging, insertBefore ? closest : closest.nextSibling);
  };

  container.ondrop = (event) => {
    event.preventDefault();
    syncOrder();
    scheduleDossierMasonry(container);
  };
}

function renderStockDossier(active) {
  const dossier = active.stockDossier || {};
  const panel = document.getElementById("stock-dossier-panel");
  const nav = document.getElementById("stock-dossier-nav");
  const node = document.getElementById("stock-dossier");
  const discoveryNode = document.getElementById("market-discovery");
  if (!panel || !nav || !node || !discoveryNode) return;
  if (!dossier.daySnapshot) {
    setHTMLIfChanged(node, `<div class="dossier-empty">Stock dossier is loading.</div>`);
    setHTMLIfChanged(discoveryNode, "");
    renderDossierRail(active);
    return;
  }
  const day = dossier.daySnapshot || {};
  const fundamentals = dossier.fundamentals || {};
  const consensus = dossier.expertConsensus || {};
  const expertOutlook = active.expertOutlook || {};
  const unusual = dossier.unusualActivity || {};
  const influence = dossier.influenceGraph || {};
  const discoveryItems = state.dashboard?.discovery?.items || [];
  const movingAverages = dossier.movingAverages || [];
  const visibleMovingAverages = state.detailMode
    ? movingAverages
    : movingAverages.filter((item) => item.value !== null && item.value !== undefined).slice(0, 4);
  const simpleDossierKeys = ["day", "ma", "fundamentals", "activity", "benchmarks"];
  const compactDossierKeys = ["day", "ma", "activity"];
  const visibleDossierKeys = state.detailMode ? DEFAULT_DOSSIER_ORDER : compactDossierKeys;
  setTextIfChanged(
    panel.querySelector(".section-heading span"),
    state.detailMode ? "Peers, fundamentals, benchmarks, consensus, and sourced links" : "Essentials only: quote, trend, and range; quality and benchmarks sit in the right rail",
  );
  const roeLabel = fundamentals.roe === null || fundamentals.roe === undefined || fundamentals.roe === ""
    ? "Unavailable"
    : dossierMetric(Number(fundamentals.roe) * 100, "percent");
  const navChanged = setHTMLIfChanged(nav, `
    <div class="dossier-nav-scroll">
      ${(state.detailMode ? [
        ["Snapshot", "dossier-day"],
        ["Averages", "dossier-ma"],
        ["Quality", "dossier-fundamentals"],
        ["Range", "dossier-activity"],
        ["Benchmarks", "dossier-benchmarks"],
        ["Peers", "dossier-peers"],
        ["Metrics", "dossier-metrics"],
        ["Sources", "dossier-links"],
      ] : [
        ["Snapshot", "dossier-day"],
        ["Averages", "dossier-ma"],
        ["Range", "dossier-activity"],
      ]).map(([label, target]) => `<button type="button" data-scroll-target="${target}">${label}</button>`).join("")}
      <button type="button" data-detail-toggle>${state.detailMode ? "Simple dossier" : "Full dossier"}</button>
      <button type="button" data-dossier-reset title="Reset card order to default">Reset layout</button>
    </div>
  `);
  if (navChanged) {
    nav.querySelectorAll("button").forEach((button) => {
      if (button.dataset.detailToggle !== undefined) {
        button.addEventListener("click", () => setDetailMode(!state.detailMode));
        return;
      }
      if (button.dataset.dossierReset !== undefined) {
        button.addEventListener("click", () => {
          state.dossierOrder = [...DEFAULT_DOSSIER_ORDER];
          try { localStorage.removeItem(STORAGE_KEYS.dossierOrder); } catch {}
          renderStockDossier(state.dashboard?.active || active);
        });
        return;
      }
      if (!button.dataset.scrollTarget) return;
      button.addEventListener("click", () => document.getElementById(button.dataset.scrollTarget)?.scrollIntoView({ behavior: "smooth", block: "nearest" }));
    });
  }
  const metricCard = renderMetricCommandCard(buildMetricCommandGroups(active, dossier, day, fundamentals, unusual));
  const benchmarkSummary = (dossier.benchmarkComparison || [])
    .slice(0, 3)
    .map((item) => `<span>${item.label}: ${formatPercent(item.returnPercent || 0)}</span>`)
    .join("");
  const cards = {
    day: renderDossierCard("day", {
      kicker: "Live quote",
      title: active.symbol,
      subtitle: day.source || "Quote provider",
      summary: `<div class="dossier-context-line"><span>${formatCurrency(active.price, active.currency)}</span><span>${formatPercent(active.changePercent || 0)}</span><span>${active.marketState || "Session pending"}</span></div>`,
      body: `<div class="dossier-metric-grid">
        <div><span>Open</span><strong>${dossierMetric(day.open, "currency", active.currency)}</strong></div>
        <div><span>Previous</span><strong>${dossierMetric(day.previousClose, "currency", active.currency)}</strong></div>
        <div><span>Day range</span><strong>${dossierMetric(day.dayLow, "currency", active.currency)} - ${dossierMetric(day.dayHigh, "currency", active.currency)}</strong></div>
        <div><span>52W range</span><strong>${dossierMetric(day.fiftyTwoWeekLow, "currency", active.currency)} - ${dossierMetric(day.fiftyTwoWeekHigh, "currency", active.currency)}</strong></div>
        <div><span>Volume</span><strong>${dossierMetric(day.volume, "large")}</strong></div>
        <div><span>Avg volume</span><strong>${dossierMetric(day.averageVolume, "large")}</strong></div>
      </div>`,
    }),
    ma: renderDossierCard("ma", {
      kicker: "Trend stack",
      title: "Moving averages",
      subtitle: "SMA 5-200",
      summary: `<div class="dossier-context-line">${visibleMovingAverages.slice(0, 2).map((item) => `<span>${item.label}: ${item.state || "Unavailable"}</span>`).join("") || "<span>Moving averages unavailable</span>"}</div>`,
      body: `<div class="ma-dossier-list">
        ${visibleMovingAverages.map((item) => {
          const stateLabel = item.state || "Unavailable";
          const distance = item.distancePercent !== null && item.distancePercent !== undefined ? formatPercent(item.distancePercent) : "";
          const stateClass = item.state === "Above" ? "positive" : item.state === "Below" ? "negative" : "";
          return `
            <div>
              <span>${item.label}</span>
              <strong>${dossierMetric(item.value, "currency", active.currency)}</strong>
              <em class="${stateClass}"><span>${stateLabel}</span>${distance ? `<small>${distance}</small>` : ""}</em>
            </div>
          `;
        }).join("") || `<div><span>SMA</span><strong>Unavailable</strong><em><span>No cached trend</span></em></div>`}
      </div>`,
    }),
    peers: renderDossierCard("peers", {
      kicker: "Context",
      title: "Peer comparison",
      subtitle: "Market cap, P/E, return, growth, ROE",
      summary: `<div class="dossier-context-line">${(dossier.peerComparison || []).slice(0, 3).map((peer) => `<span>${peer.symbol} · ${peer.oneYearReturn}</span>`).join("")}</div>`,
      body: `<div class="peer-table">
        <div class="peer-row peer-head"><span>Peer</span><span>MCap</span><span>P/E</span><span>1Y</span><span>Sales</span><span>ROE</span></div>
        ${(dossier.peerComparison || []).map((peer) => `
          <div class="peer-row"><strong>${peer.symbol}</strong><span>${peer.marketCap}</span><span>${peer.pe}</span><span>${peer.oneYearReturn}</span><span>${peer.salesGrowth}</span><span>${peer.roe}</span></div>
        `).join("")}
      </div>`,
    }),
    benchmarks: renderDossierCard("benchmarks", {
      kicker: "Relative path",
      title: "Benchmark comparison",
      subtitle: "Normalized 1Y",
      summary: `<div class="dossier-context-line">${benchmarkSummary || "<span>Benchmark history unavailable</span>"}</div>`,
      body: renderBenchmarkBars(dossier.benchmarkComparison || []),
    }),
    metrics: renderDossierCard("metrics", {
      kicker: "Command drawer",
      title: "Show all metrics",
      subtitle: "Searchable source-backed facts",
      summary: metricCard.summary,
      body: metricCard.body,
      extraClass: "metric-command-card",
    }),
    activity: renderRangeWatchStrip(unusual),
    fundamentals: renderDossierCard("fundamentals", {
      kicker: "Supporting",
      title: `Quality ${dossierMetric(fundamentals.scores?.quality)}`,
      subtitle: fundamentals.source || "Provider summary",
      summary: `<div class="dossier-context-line"><span>Valuation ${dossierMetric(fundamentals.scores?.valuation)}</span><span>Risk ${dossierMetric(fundamentals.scores?.risk)}</span><span>ROE ${roeLabel}</span></div>`,
      body: `<div class="dossier-score-row">
        <span>Valuation ${dossierMetric(fundamentals.scores?.valuation)}</span>
        <span>Risk ${dossierMetric(fundamentals.scores?.risk)}</span>
      </div>
      <div class="dossier-mini-grid">
        <div><span>EPS</span><strong>${dossierMetric(fundamentals.eps)}</strong></div>
        <div><span>Revenue</span><strong>${dossierMetric(fundamentals.revenue, "large")}</strong></div>
        <div><span>Net income</span><strong>${dossierMetric(fundamentals.netIncome, "large")}</strong></div>
        <div><span>ROE</span><strong>${roeLabel}</strong></div>
      </div>`,
    }),
    consensus: renderDossierCard("consensus", {
      kicker: "External",
      title: consensus.rating || "Unavailable",
      subtitle: consensus.sourceLabel || "External source",
      summary: `<div class="dossier-context-line"><span>Buy ${consensus.buy || 0}%</span><span>Hold ${consensus.hold || 0}%</span><span>Sell ${consensus.sell || 0}%</span></div>`,
      body: `<div class="consensus-stack">
        <span style="--w:${consensus.buy || 0}" class="positive">Buy ${consensus.buy || 0}%</span>
        <span style="--w:${consensus.hold || 0}" class="neutral">Hold ${consensus.hold || 0}%</span>
        <span style="--w:${consensus.sell || 0}" class="negative">Sell ${consensus.sell || 0}%</span>
      </div>
      <p class="dossier-note">${consensus.note || "External consensus only; not dashboard advice."}</p>
      ${expertOutlook ? `
        <div class="expert-outlook-list">
          <div class="expert-outlook-head">
            <span>${escapeHtml(expertOutlook.sourceLabel || "Web outlook")}</span>
            <strong>${escapeHtml(expertOutlook.label || "External tone")}</strong>
          </div>
          ${(expertOutlook.items || []).slice(0, 4).map((item) => {
            const url = safeExternalUrl(item.url);
            if (!url) return "";
            return `
              <a href="${escapeHtml(url)}" target="_blank" rel="noreferrer noopener">
                <span>${escapeHtml(item.view)}${item.target ? ` · ${escapeHtml(item.target)}` : ""}</span>
                <strong>${escapeHtml(item.title)}</strong>
                <em>${escapeHtml(item.source)}</em>
              </a>
            `;
          }).join("") || `<p class="expert-outlook-empty">Expert outlook links are unavailable right now; the dashboard keeps the prediction context visible and labels this source gap.</p>`}
          <small>${escapeHtml(expertOutlook.note || "External sources require verification.")}</small>
        </div>
      ` : ""}
      `,
    }),
    links: renderDossierCard("links", {
      kicker: "Sources",
      title: `${(influence.nodes || []).length} influence nodes`,
      subtitle: "Public cited only",
      summary: `<div class="dossier-context-line"><span>${(influence.ledger || []).length || 1} sourced notes</span><span>${influence.policy || "Public cited relationships only"}</span></div>`,
      body: `<div class="influence-ledger">
        ${(influence.ledger || []).length ? (influence.ledger || []).map((item) => `
          <div><strong>${item.claim}</strong><span>${item.confidence} · ${item.sourceLabel || "Source noted"}</span><p>${item.status}</p></div>
        `).join("") : `<div><strong>No sourced sensitive links yet</strong><span>${influence.policy || "Public cited only"}</span><p>Unsourced political or shell-company claims are intentionally hidden.</p></div>`}
      </div>
      <div class="source-provenance">${(dossier.sourceProvenance || []).map((item) => `<span>${item.label}: ${item.usedFor}</span>`).join("")}</div>`,
    }),
  };
  const orderedKeys = (state.detailMode
    ? visibleDossierKeys
        .filter((key) => state.dossierOrder.includes(key))
        .sort((a, b) => state.dossierOrder.indexOf(a) - state.dossierOrder.indexOf(b))
        .concat(visibleDossierKeys.filter((key) => !state.dossierOrder.includes(key)))
    : visibleDossierKeys
  ).filter((key) => cards[key]);
  const dossierChanged = setHTMLIfChanged(node, orderedKeys.map((key) => cards[key]).join(""));
  if (dossierChanged) {
    setupDossierControls(node);
    setupDossierDrag(node);
    observeDossierMasonry(node);
  } else {
    scheduleDossierMasonry(node);
  }
  const discoveryChanged = setHTMLIfChanged(discoveryNode, renderMarketDiscovery(discoveryItems, state.dashboard?.discovery?.source || "Local scan"));
  if (discoveryChanged) {
    discoveryNode.querySelectorAll("button[data-symbol]").forEach((button) => {
      button.addEventListener("click", () => selectActiveTicker(button.dataset.symbol));
    });
  }
  renderDossierRail(active);
  revealSection("stock-dossier");
  applyRevealObserver();
  renderDataFlowBar();
}

function buildProbabilityFan(forecast, active) {
  // Based on: Chronos (2024) quantile forecasting + realized vol scaling
  // Shows 50%, 80%, 95% confidence intervals as a fan chart
  const price = Number(active.price || 0);
  const vol = Number(forecast.realizedVol || 0.02);
  const mae = Number(forecast.mae || 3) / 100;
  const horizon = 10;
  const expectedReturn = Number(forecast.expectedReturn || 0) / 100;
  const intervals = [
    { label: "95%", z: 1.96, opacity: 0.12 },
    { label: "80%", z: 1.28, opacity: 0.22 },
    { label: "50%", z: 0.67, opacity: 0.38 },
  ];
  return intervals.map((band) => {
    const spread = vol * Math.sqrt(horizon) * band.z;
    const upper = price * (1 + expectedReturn + spread);
    const lower = price * (1 + expectedReturn - spread);
    return { ...band, upper, lower, spread: spread * 100 };
  });
}

function percentile(values, ratio) {
  const sorted = (values || []).map(Number).filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) return null;
  const index = clamp(Math.round((sorted.length - 1) * ratio), 0, sorted.length - 1);
  return sorted[index];
}

function buildShortTermSetup(active = {}, forecast = {}) {
  const price = Number(active.price || 0);
  const currency = active.currency || "USD";
  const historySeries = normalizeHistorySeries(active.historySeries?.length ? active.historySeries : (active.history || []), state.chartRange);
  const closes = historySeries.map((item) => Number(item.value)).filter(Number.isFinite);
  const recent = closes.slice(-Math.min(40, closes.length));
  const projected = (forecast.projected || []).map(Number).filter(Number.isFinite);
  const factors = forecast.factorsRaw || {};
  const lastProjected = projected.length ? projected[projected.length - 1] : price;
  const expectedReturn = Number(forecast.expectedReturn || 0);
  const maePct = Math.max(Number(forecast.mae || 0), 1.2);
  const realizedVolPct = Math.max(Number(factors.realizedVol || forecast.realizedVol || 0) * 100, 0.8);
  const bufferPct = clamp(Math.max(maePct * 0.45, realizedVolPct * 0.65), 0.8, 6.5);
  const support = Math.min(
    percentile(recent, 0.18) ?? price * (1 - bufferPct / 100),
    price * (1 - Math.min(bufferPct, 5.5) / 100),
  );
  const resistance = Math.max(
    percentile(recent, 0.82) ?? price * (1 + bufferPct / 100),
    lastProjected || price,
    price * (1 + Math.min(bufferPct, 6.5) / 100),
  );
  const entryLow = Math.min(price, support * 1.002);
  const entryHigh = Math.max(entryLow, Math.min(price * 0.995, support * 1.018));
  const invalidation = support * (1 - Math.min(bufferPct * 0.55, 3.2) / 100);
  const upsidePct = price ? ((resistance - price) / price) * 100 : 0;
  const downsidePct = price ? ((price - invalidation) / price) * 100 : 0;
  const riskReward = downsidePct > 0 ? Math.max(0, upsidePct / downsidePct) : 0;
  const trendScore = Number(factors.fastMomentum || 0) * 100 + Number(factors.macdSignal || 0) * 75 + Number(factors.meanReversion || 0) * 30;
  const trend = trendScore > 0.35 ? "Uptrend bias" : trendScore < -0.35 ? "Downtrend risk" : "Range-bound";
  const eventPressure = forecast.eventPressureLabel || "Pending";
  const agreement = forecast.models?.agreement || {};
  const confidence = Number(forecast.confidence || 0);
  const direction = String(forecast.direction || "").toLowerCase();
  const bearishSetup = expectedReturn < -1 || direction === "bearish";
  const bullishSetup = expectedReturn > 1 || direction === "bullish";
  const quality = bearishSetup
    ? (confidence >= 60 ? "Defensive" : "Fragile")
    : bullishSetup && confidence >= 68 && riskReward >= 1.15
      ? "Constructive"
      : confidence < 45 || riskReward < 0.7
        ? "Fragile"
        : "Balanced";
  const entryLabel = bearishSetup ? "Recovery confirmation" : "Support confirmation";
  const entryNote = bearishSetup ? "Scenario improves after a reclaim or calmer pullback." : "Observed support zone for scenario monitoring.";
  const upsideNote = bearishSetup ? "Recovery ceiling to watch before trend improves." : `${formatPercent(upsidePct)} to resistance/projection.`;
  const riskLabel = bearishSetup ? "Breakdown threshold" : "Risk threshold";
  const riskNote = bearishSetup ? `${formatPercent(-downsidePct)} to the lower risk line.` : `${formatPercent(-downsidePct)} scenario buffer.`;
  return {
    currency,
    price,
    entryLow,
    entryHigh,
    resistance,
    invalidation,
    upsidePct,
    downsidePct,
    riskReward,
    trend,
    eventPressure,
    expectedReturn,
    confidence,
    quality,
    agreementLabel: agreement.label || "Pending",
    agreementScore: Number(agreement.score || 0),
    volatility: realizedVolPct,
    modelError: maePct,
    entryLabel,
    entryNote,
    upsideNote,
    riskLabel,
    riskNote,
  };
}

function renderTradePlanPanel(active, forecast) {
  const node = document.getElementById("trade-plan-panel");
  if (!node || !active?.price) return;
  const setup = buildShortTermSetup(active, forecast);
  const entryText = setup.entryLow >= setup.entryHigh
    ? formatCurrency(setup.entryLow, setup.currency)
    : `${formatCurrency(setup.entryLow, setup.currency)}-${formatCurrency(setup.entryHigh, setup.currency)}`;
  const html = `
    <div class="trade-plan-head">
      <div>
        <span>Short-term setup</span>
        <strong>${setup.quality} scenario</strong>
      </div>
      <em>${setup.trend} · ${formatPercent(setup.expectedReturn)} 10D</em>
    </div>
    <div class="trade-plan-grid">
      <div class="trade-plan-tile watch">
        <span>${setup.entryLabel}</span>
        <strong>${entryText}</strong>
        <small>${setup.entryNote}</small>
      </div>
      <div class="trade-plan-tile upside">
        <span>Upside watch</span>
        <strong>${formatCurrency(setup.resistance, setup.currency)}</strong>
        <small>${setup.upsideNote}</small>
      </div>
      <div class="trade-plan-tile risk">
        <span>${setup.riskLabel}</span>
        <strong>${formatCurrency(setup.invalidation, setup.currency)}</strong>
        <small>${setup.riskNote}</small>
      </div>
      <div class="trade-plan-tile params">
        <span>Forecast params</span>
        <strong>${setup.agreementLabel} ${setup.agreementScore.toFixed(0)}/100</strong>
        <small>Conf ${setup.confidence.toFixed(0)}% · MAE ${setup.modelError.toFixed(1)}% · Vol ${setup.volatility.toFixed(1)}% · Event ${setup.eventPressure}</small>
      </div>
    </div>
    <div class="trade-plan-foot">
      <span>Upside/downside ratio ${setup.riskReward.toFixed(2)}x</span>
      <span>Scenario context only; not a trading instruction.</span>
    </div>
  `;
  setHTMLIfChanged(node, html);
}

function renderPredictionPanel(active, forecast) {
  const node = document.getElementById("prediction-panel");
  if (!node) return;
  if (!active?.price || !forecast?.direction || forecast.direction === "Refreshing") {
    setHTMLIfChanged(node, `<div class="prediction-loading">Prediction model loading…</div>`);
    return;
  }

  const factors = forecast.factorsRaw || {};
  const confidence = Number(forecast.confidence || 0);
  const direction = forecast.direction || "Neutral";
  const expectedReturn = Number(forecast.expectedReturn || 0);
  const fan = buildProbabilityFan(forecast, active);
  const agreement = forecast.models?.agreement || {};
  const classic = forecast.models?.classic || {};
  const modern = forecast.models?.modern || {};

  // Key factor contributions for display
  const factorItems = [
    { label: "Momentum (5D)", value: Number(factors.fastMomentum || 0) * 100, method: "Lo, Mamaysky & Wang (2000)" },
    { label: "RSI (14)", value: Number(factors.rsi || 50), unit: "", raw: factors.rsiSignal, method: "Wilder (1978)" },
    { label: "MACD Signal", value: Number(factors.macdSignal || 0) * 100, method: "Appel (1979)" },
    { label: "Bollinger %B", value: Number(factors.bollPosition || 0.5) * 100, unit: "%", method: "Bollinger (1983)" },
    { label: "Mean Reversion", value: Number(factors.meanReversion || 0) * 100, method: "Gatev et al. (2006)" },
    { label: "Realized Vol", value: Number(factors.realizedVol || 0) * 100, method: "Acharya & Pedersen (2003)" },
    { label: "Macro Score", value: Number(factors.macroScore || 0) * 100, method: "Multi-factor model" },
    { label: "Volume Trend", value: Number(factors.volumeTrend || 1), unit: "x", method: "Participation analysis" },
  ];

  const dirClass = direction.toLowerCase() === "bullish" ? "pred-bullish" : direction.toLowerCase() === "bearish" ? "pred-bearish" : "pred-neutral";
  const gaugeAngle = clamp((confidence / 100) * 180 - 90, -90, 90);

  const html = `
    <div class="prediction-grid ${dirClass}">
      <div class="pred-direction-card">
        <div class="pred-gauge">
          <svg viewBox="0 0 120 70" class="pred-gauge-svg">
            <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8" stroke-linecap="round"/>
            <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke="url(#gauge-gradient)" stroke-width="8" stroke-linecap="round" stroke-dasharray="${(confidence / 100) * 157} 157"/>
            <line x1="60" y1="65" x2="${60 + 38 * Math.cos((gaugeAngle - 90) * Math.PI / 180)}" y2="${65 + 38 * Math.sin((gaugeAngle - 90) * Math.PI / 180)}" stroke="var(--pred-accent)" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="60" cy="65" r="4" fill="var(--pred-accent)"/>
            <defs><linearGradient id="gauge-gradient" x1="0%" x2="100%"><stop offset="0%" stop-color="#ef4444"/><stop offset="50%" stop-color="#f3b85f"/><stop offset="100%" stop-color="#22c55e"/></linearGradient></defs>
          </svg>
          <div class="pred-gauge-label">
            <strong>${confidence.toFixed(0)}%</strong>
            <span>confidence</span>
          </div>
        </div>
        <div class="pred-direction-label">
          <span class="pred-dir-text">${direction}</span>
          <span class="pred-return">${formatPercent(expectedReturn)} 10D</span>
        </div>
        <div class="pred-models-row">
          <span title="Classic: momentum, mean-reversion, macro, quality">Classic ${classic.direction || "—"}</span>
          <span title="Modern: regime, breakout, trend-patch">Modern ${modern.direction || "—"}</span>
          <span title="Model agreement score">${agreement.label || "Pending"} ${Number(agreement.score || 0).toFixed(0)}/100</span>
        </div>
      </div>
      <div class="pred-range-card">
        <div class="pred-range-head">
          <span>10-Day Price Range</span>
          <small>Quantile fan · Chronos/Moirai methodology</small>
        </div>
        <div class="pred-fan-chart">
          ${fan.map((band) => `
            <div class="pred-fan-band" style="--opacity:${band.opacity}">
              <span class="pred-fan-label">${band.label}</span>
              <div class="pred-fan-bar">
                <div class="pred-fan-fill" style="--left:${clamp(50 - band.spread * 2, 5, 48)}%; --right:${clamp(50 + band.spread * 2, 52, 95)}%"></div>
              </div>
              <span class="pred-fan-lo">${formatCurrency(band.lower, active.currency)}</span>
              <span class="pred-fan-hi">${formatCurrency(band.upper, active.currency)}</span>
            </div>
          `).join("")}
        </div>
        <div class="pred-range-footer">
          <span>Fair value ${formatCurrency(forecast.fairValue || active.price, active.currency)}</span>
          <span>MAE ${Number(forecast.mae || 0).toFixed(1)}%</span>
          <span>Vol ${(Number(factors.realizedVol || 0) * 100).toFixed(1)}%</span>
        </div>
      </div>
      <div class="pred-factors-card">
        <div class="pred-factors-head">
          <span>Key Factor Contributions</span>
          <small>Signal strength relative to neutral</small>
        </div>
        <div class="pred-factor-bars">
          ${factorItems.map((item) => {
            const barValue = item.label === "RSI (14)" ? (item.value - 50) : (item.label === "Volume Trend" ? (item.value - 1) * 50 : item.value);
            const capped = clamp(barValue, -5, 5);
            const barPct = Math.abs(capped) / 5 * 50;
            const isPositive = capped >= 0;
            return `
              <div class="pred-factor-row" title="${item.method}">
                <span class="pred-factor-name">${item.label}</span>
                <div class="pred-factor-track">
                  <div class="pred-factor-center"></div>
                  <div class="pred-factor-fill ${isPositive ? "positive" : "negative"}" style="--w:${barPct}%; --dir:${isPositive ? "right" : "left"}"></div>
                </div>
                <span class="pred-factor-val ${isPositive ? "positive" : "negative"}">${item.label === "RSI (14)" ? item.value.toFixed(0) : (item.label === "Volume Trend" ? item.value.toFixed(2) + "x" : (capped >= 0 ? "+" : "") + capped.toFixed(2) + "%")}</span>
                <span class="pred-factor-method">${item.method}</span>
              </div>
            `;
          }).join("")}
        </div>
      </div>
    </div>
  `;
  setHTMLIfChanged(node, html);
  revealSection("prediction-panel");
}

function renderShortHorizonCard(active, forecast) {
  // Hand-crafted short-horizon directional model (see scripts/short_horizon_model.py).
  // Renders side-by-side with the existing prediction panel so the user can compare
  // the calibrated short-horizon call against the longer-horizon classic/modern blend.
  const node = document.getElementById("short-horizon-card");
  if (!node) return;
  const sh = forecast?.shortHorizon;
  if (!sh || !sh.available) {
    setHTMLIfChanged(node, `<div class="sh-empty">Short-horizon model: ${sh?.reason || "warming up."}</div>`);
    return;
  }
  const dir = sh.direction || "Neutral";
  const dirClass = dir === "Bullish" ? "sh-bullish" : dir === "Bearish" ? "sh-bearish" : "sh-neutral";
  const expected = Number(sh.expectedReturnPct || 0);
  const coneLow = Number(sh.coneLowPct || 0);
  const coneHigh = Number(sh.coneHighPct || 0);
  const conf = Number(sh.confidence || 0);
  const skill = sh.skill || {};
  const hit = Number(skill.hit_rate_pct || 0);
  const skillSamples = Number(skill.samples || 0);
  const skillIc = Number(skill.ic || 0);
  const horizon = sh.horizon || 5;
  const notes = Array.isArray(sh.notes) ? sh.notes.slice(0, 2) : [];
  const skillBadge = skillSamples >= 20
    ? `${hit.toFixed(0)}% hit · IC ${skillIc.toFixed(2)} · n=${skillSamples}`
    : "Skill: warming up";

  const html = `
    <div class="sh-card ${dirClass}">
      <div class="sh-head">
        <span class="sh-title">Short-Horizon Forecast</span>
        <span class="sh-horizon">${horizon}-bar · calibrated</span>
      </div>
      <div class="sh-body">
        <div class="sh-call">
          <span class="sh-direction">${dir}</span>
          <strong class="sh-expected">${expected >= 0 ? "+" : ""}${expected.toFixed(2)}%</strong>
          <span class="sh-cone">cone ${coneLow >= 0 ? "+" : ""}${coneLow.toFixed(2)}% … ${coneHigh >= 0 ? "+" : ""}${coneHigh.toFixed(2)}%</span>
        </div>
        <div class="sh-meta">
          <span class="sh-conf">${conf.toFixed(0)}% conf</span>
          <span class="sh-skill" title="Walk-forward hit rate / information coefficient / sample size">${skillBadge}</span>
        </div>
      </div>
      ${notes.length ? `<div class="sh-notes">${notes.map((n) => `<span>${n}</span>`).join("")}</div>` : ""}
    </div>
  `;
  setHTMLIfChanged(node, html);
}

function patchHeroSurface(active, forecast, { renderPrediction = true, renderStats = true, renderSparkline = true } = {}) {
  const agreement = forecast.models?.agreement || { label: "Pending", score: 0, summary: "Agreement refreshing." };
  const recommendation = active.recommendation || { upside: 0, base: 100, downside: 0, scenarioSignal: "Refreshing" };
  const displayFreshness = quoteFreshnessForDisplay(active);
  setTextIfChanged(document.getElementById("hero-ticker"), `${active.symbol} · ${active.name}`);
  setTextIfChanged(document.getElementById("hero-regime"), active.regime);
  const heroPriceNode = document.getElementById("hero-price");
  const heroPriceText = formatCurrency(active.price, active.currency);
  const priceSizeClass = heroPriceText.length >= 14 ? "is-compact" : heroPriceText.length >= 11 ? "is-tight" : "";
  setClassIfChanged(heroPriceNode, `hero-price ${priceSizeClass} ${liveValueClass(`hero:${active.symbol}:price`, active.price)}`.trim());
  setHTMLIfChanged(heroPriceNode, buildPriceFlipMarkup(active.price, active.currency));
  setTextIfChanged(document.getElementById("metric-live-price"), heroPriceText);
  const changeNode = document.getElementById("hero-change");
  const changeText = formatPercent(active.changePercent);
  setTextIfChanged(changeNode, changeText);
  setTextIfChanged(document.getElementById("metric-live-move"), changeText);
  setClassIfChanged(changeNode, `hero-change live-number ${active.changePercent >= 0 ? "positive" : "negative"} ${liveValueClass(`hero:${active.symbol}:change`, active.changePercent)}`);
  const forecastRangeNode = document.getElementById("forecast-range");
  const forecastReturnText = formatPercent(forecast.expectedReturn);
  setTextIfChanged(forecastRangeNode, `10D projection ${forecastReturnText}`);
  setTextIfChanged(document.getElementById("forecast-rail-return"), forecastReturnText);
  setClassIfChanged(forecastRangeNode, `forecast-range live-number ${liveValueClass(`hero:${active.symbol}:projection`, forecast.expectedReturn)}`);
  const bsEl = document.getElementById("buy-sell-signal");
  const bsText = recommendation.scenarioSignal || recommendation.signal || "Base-led";
  setTextIfChanged(bsEl, bsText);
  const bsDir = forecast.direction?.toLowerCase() || "";
  setClassIfChanged(bsEl, bsDir === "bullish" ? "bullish" : bsDir === "bearish" ? "bearish" : "neutral");
  const upside = recommendation.upside ?? recommendation.buy ?? 0;
  const base = recommendation.base ?? recommendation.hold ?? 100;
  const downside = recommendation.downside ?? recommendation.sell ?? 0;
  setHTMLIfChanged(document.getElementById("buy-sell-breakdown"), `<span class="bsb-buy">Upside ${upside}%</span><span class="bsb-hold">Base ${base}%</span><span class="bsb-sell">Downside ${downside}%</span>`);
  setTextIfChanged(document.getElementById("model-agreement-note"), `${agreement.summary} Score ${Number(agreement.score || 0).toFixed(0)}/100.`);
  setTextIfChanged(document.getElementById("quote-source-note"), quoteSourceDisplayText(active, displayFreshness));
  const overviewMetaItems = [
    { label: active.exchange || active.region || "Global", help: "Where the stock trades." },
    { label: `${active.currency || "USD"} pricing`, help: "Home-market trading currency." },
    { label: `${active.marketState || "Live"} ${liveBadgeMarkup()}`, help: "Current session state." },
    { label: `Vol ${formatCompactNumber(active.volume)} ${liveBadgeMarkup()}`, help: "Current traded volume." },
    { label: `${quoteDisplayTime(active)} ${freshnessBadgeMarkup(displayFreshness)}`, help: "Last provider quote print and dashboard stream status." },
  ];
  setHTMLIfChanged(document.getElementById("overview-meta"), overviewMetaItems
    .map((item) => `<span class="overview-meta-pill" data-help="${item.help.replace(/"/g, "&quot;")}" tabindex="0">${item.label}</span>`)
    .join(""));
  if (renderStats) {
    setHTMLIfChanged(document.getElementById("hero-stats"), (active.stats || [])
      .map(
        (stat, index) => `
          <div class="hero-stat-card">
            <span>${stat.label}</span>
            <strong class="live-number ${liveValueClass(`hero:${active.symbol}:stat:${index}`, parseFloat(String(stat.value).replace(/[^\d.+-]/g, "")))}">${stat.value}</strong>
          </div>
        `,
      )
      .join(""));
    revealSection("hero-stats");
  }
  if (renderSparkline) {
    drawSparkline(document.getElementById("hero-sparkline"), (active.history || []).slice(-24));
  }
  clearChartSkeleton();
  if (renderPrediction) {
    renderPredictionPanel(active, forecast);
    renderShortHorizonCard(active, forecast);
  }
  renderTradePlanPanel(active, forecast);
}

function patchOverviewLiveSurface(active, forecast, { redrawChart = false } = {}) {
  patchHeroSurface(active, forecast, { renderPrediction: false, renderStats: false, renderSparkline: redrawChart });
  const sessionNode = document.getElementById("market-session-strip");
  if (sessionNode) {
    const session = active.marketSession?.nextTransitionAt
      ? active.marketSession
      : buildClientMarketSession(active.exchange || active.region, active.marketState, active.region);
    patchMarketSessionStrip(sessionNode, session);
  }
  if (redrawChart) {
    drawTimeline(
      document.getElementById("hero-projection-chart"),
      active.historySeries?.length ? active.historySeries : (active.history || []),
      forecast.projected || [],
      state.chartFeatures,
      { currency: active.currency, range: state.chartRange, overlayId: "hero-chart-hover", item: active },
    );
  }
}

function renderHeroChartOnly(active = state.dashboard?.active) {
  if (!active) return;
  const forecast = active.forecast || emptyForecastPayload();
  drawTimeline(
    document.getElementById("hero-projection-chart"),
    active.historySeries?.length ? active.historySeries : (active.history || []),
    forecast.projected || [],
    state.chartFeatures,
    { currency: active.currency, range: state.chartRange, overlayId: "hero-chart-hover", item: active },
  );
  document.querySelectorAll(".range-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.range === state.chartRange);
  });
  document.querySelectorAll(".chart-mode-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.chartType === (state.chartFeatures.chartType || "line"));
  });
  const sma20 = document.getElementById("feature-sma20");
  const sma50 = document.getElementById("feature-sma50");
  const bands = document.getElementById("feature-bands");
  if (sma20) sma20.checked = Boolean(state.chartFeatures.sma20);
  if (sma50) sma50.checked = Boolean(state.chartFeatures.sma50);
  if (bands) bands.checked = Boolean(state.chartFeatures.bands);
  renderDataFlowBar();
}

function shouldRedrawLiveChart() {
  const svg = document.getElementById("hero-projection-chart");
  const now = Date.now();
  if (svg?.dataset.chartReady !== "1" || now - state.lastLiveChartRenderAt >= REFRESH_INTERVALS.chartLive) {
    state.lastLiveChartRenderAt = now;
    return true;
  }
  return false;
}

function formatDuration(seconds) {
  const total = Math.max(0, Math.floor(Number(seconds) || 0));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const remainingSeconds = total % 60;
  return [hours, minutes, remainingSeconds].map((value) => String(value).padStart(2, "0")).join(":");
}

function formatSourceLabel(value) {
  if (!value) return "Unknown";
  return String(value)
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function quoteSourceLooksHistorical(source = "") {
  return /history|historical|cache|derived/i.test(String(source || ""));
}

function quoteFreshnessForDisplay(active = {}) {
  const freshness = { ...(active.quoteFreshness || {}) };
  if (!quoteSourceLooksHistorical(active.dataSource)) return freshness;
  const sessionOpen = Boolean(active.marketSession?.isOpen) || String(active.marketState || "").toUpperCase() === "REGULAR";
  const parsed = active.asOf ? new Date(active.asOf) : null;
  const ageMinutes = parsed && !Number.isNaN(parsed.getTime())
    ? Math.max(0, (Date.now() - parsed.getTime()) / 60000)
    : null;
  if (sessionOpen) {
    return {
      ...freshness,
      label: "Historical fallback",
      state: "stale",
      isStale: true,
      ageMinutes: ageMinutes === null ? freshness.ageMinutes : Math.round(ageMinutes * 10) / 10,
      note: `${formatSourceLabel(active.dataSource)} is not a confirmed live quote while the market is open.`,
    };
  }
  return {
    ...freshness,
    label: freshness.label && freshness.label !== "Live edge" ? freshness.label : "Last history close",
    state: freshness.state === "stale" ? "stale" : "reference",
    isStale: Boolean(freshness.isStale),
    ageMinutes: ageMinutes === null ? freshness.ageMinutes : Math.round(ageMinutes * 10) / 10,
    note: `${formatSourceLabel(active.dataSource)} is a historical/cache-derived level.`,
  };
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

function formatEventDateTime(value) {
  if (!value) return "Time unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Time unavailable";
  return date.toLocaleString([], {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatEventTime(value) {
  return formatEventDateTime(value);
}

function formatZonedTime(timeZone) {
  try {
    return new Intl.DateTimeFormat("en-US", {
      timeZone,
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    }).format(new Date());
  } catch {
    return "--:--";
  }
}

function formatZonedDate(timeZone) {
  try {
    return new Intl.DateTimeFormat("en-US", {
      timeZone,
      weekday: "short",
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(new Date());
  } catch {
    return "Date unavailable";
  }
}

function exchangeTimeZoneForItem(item = {}) {
  if (item.marketSession?.timezone) return item.marketSession.timezone;
  const exchange = `${item.exchange || ""} ${item.region || ""} ${item.symbol || ""}`.toUpperCase();
  if (exchange.includes("NSE") || exchange.includes("BSE") || exchange.includes(".NS") || exchange.includes(".BO")) return "Asia/Kolkata";
  if (exchange.includes("NASDAQ") || exchange.includes("NYSE") || exchange.includes("US")) return "America/New_York";
  if (exchange.includes("LSE") || exchange.includes("LONDON")) return "Europe/London";
  if (exchange.includes("ASX") || exchange.includes(".AX")) return "Australia/Sydney";
  if (exchange.includes("HKEX") || exchange.includes("HONG")) return "Asia/Hong_Kong";
  if (exchange.includes("JPX") || exchange.includes("TOKYO") || exchange.includes(".T")) return "Asia/Tokyo";
  return "UTC";
}

function formatQuotePrintTime(value, item = {}) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const timeZone = exchangeTimeZoneForItem(item);
  try {
    const time = new Intl.DateTimeFormat("en-US", {
      timeZone,
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    }).format(date);
    const zoneLabel = item.marketSession?.hoursLabel?.split(" ").pop() || timeZone.replace(/^[^/]+\//, "").replace(/_/g, " ");
    return `${time} ${zoneLabel}`;
  } catch {
    return date.toISOString().slice(11, 16);
  }
}

function freshnessBadgeMarkup(freshness = {}) {
  const stateLabel = freshness.state || (freshness.isStale ? "stale" : "fresh");
  const label = freshness.label || (freshness.isStale ? "Stale quote" : "Fresh quote");
  return `<span class="freshness-badge ${stateLabel}" title="${freshness.note || ""}">${label}</span>`;
}

function streamFreshnessText(active = {}) {
  const receivedAt = active.receivedAt || state.dashboard?.updatedAt || "";
  if (!receivedAt) return "Stream pending";
  const parsed = new Date(receivedAt);
  if (Number.isNaN(parsed.getTime())) return "Stream active";
  const ageSeconds = Math.max(0, Math.round((Date.now() - parsed.getTime()) / 1000));
  if (ageSeconds < 15) return "Stream live now";
  if (ageSeconds < 90) return "Stream live <1m ago";
  return `Stream live ${Math.round(ageSeconds / 60)}m ago`;
}

function providerPrintText(active = {}, freshness = null) {
  const displayFreshness = freshness || quoteFreshnessForDisplay(active);
  const label = displayFreshness.label || quoteFreshnessText(active, displayFreshness);
  return label === "Live edge" ? "provider print live" : `provider print ${String(label).toLowerCase()}`;
}

function quoteDisplayTime(active = {}) {
  if (!active.asOf) return streamFreshnessText(active);
  const printTime = formatQuotePrintTime(active.asOf, active);
  return `${streamFreshnessText(active)} · exchange print ${printTime}`;
}

function quoteSourceDisplayText(active = {}, freshness = null) {
  const displayFreshness = freshness || quoteFreshnessForDisplay(active);
  const parts = [
    `Quote source: ${formatSourceLabel(active.dataSource)}`,
    streamFreshnessText(active),
    providerPrintText(active, displayFreshness),
  ];
  if (active.asOf) {
    parts.push(`exchange print ${formatQuotePrintTime(active.asOf, active)}`);
  }
  return parts.join(" • ");
}

function quoteFreshnessText(active = {}, displayFreshness = null) {
  const freshness = displayFreshness || quoteFreshnessForDisplay(active);
  if (freshness.label) return freshness.label;
  if (active.asOf) return `Updated ${new Date(active.asOf).toLocaleString()}`;
  return "No live timestamp";
}

function shortenHeadline(text, words = 5) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  if (!clean) return "Live event";
  const parts = clean.split(" ");
  if (parts.length <= words) return clean;
  return `${parts.slice(0, words).join(" ")}...`;
}

const CLIENT_MARKET_SESSION_RULES = [
  { matches: ["NSE", "BSE", "INDIA"], timeZone: "Asia/Kolkata", open: [9, 15], close: [15, 30], hoursLabel: "09:15-15:30 IST" },
  { matches: ["NASDAQ", "NYSE", "US"], timeZone: "America/New_York", open: [9, 30], close: [16, 0], hoursLabel: "09:30-16:00 ET" },
  { matches: ["LSE", "LONDON"], timeZone: "Europe/London", open: [8, 0], close: [16, 30], hoursLabel: "08:00-16:30 UK" },
  { matches: ["HKEX", "HONG KONG", "HONGKONG"], timeZone: "Asia/Hong_Kong", open: [9, 30], close: [16, 0], hoursLabel: "09:30-16:00 HKT" },
  { matches: ["ASX", "AUSTRALIA"], timeZone: "Australia/Sydney", open: [10, 0], close: [16, 0], hoursLabel: "10:00-16:00 AEST/AEDT" },
  { matches: ["JPX", "TSE", "TOKYO"], timeZone: "Asia/Tokyo", open: [9, 0], close: [15, 0], hoursLabel: "09:00-15:00 JST" },
];

function sessionHaystackTokens(...values) {
  return values
    .filter(Boolean)
    .flatMap((value) => String(value).toUpperCase().split(/[^A-Z0-9]+/))
    .filter(Boolean);
}

function clientSessionRuleMatches(rule, exchange = "", region = "") {
  const exchangeUpper = String(exchange || "").toUpperCase();
  const regionUpper = String(region || "").toUpperCase();
  const tokens = sessionHaystackTokens(exchangeUpper, regionUpper);
  return rule.matches.some((label) => {
    const candidate = String(label || "").toUpperCase();
    if (candidate.length <= 3) {
      return tokens.includes(candidate);
    }
    return exchangeUpper.includes(candidate) || regionUpper.includes(candidate) || tokens.includes(candidate);
  });
}

function getZonedDateParts(timeZone) {
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    weekday: "short",
    hour12: false,
  });
  return formatter.formatToParts(new Date()).reduce((acc, part) => {
    if (part.type !== "literal") acc[part.type] = part.value;
    return acc;
  }, {});
}

function buildClientMarketSession(exchange, marketState = "", region = "") {
  const rule = CLIENT_MARKET_SESSION_RULES.find((item) => clientSessionRuleMatches(item, exchange, region));
  if (!rule) {
    return {
      status: marketState === "REGULAR" ? "Open" : "Closed",
      isOpen: marketState === "REGULAR",
      transitionLabel: marketState === "REGULAR" ? "close" : "open",
      nextTransitionAt: null,
      hoursLabel: "Hours unavailable",
      timezone: "UTC",
    };
  }

  const parts = getZonedDateParts(rule.timeZone);
  const zonedNow = new Date(`${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}:${parts.second}`);
  const weekday = parts.weekday || "Mon";
  const openTime = new Date(zonedNow);
  openTime.setHours(rule.open[0], rule.open[1], 0, 0);
  const closeTime = new Date(zonedNow);
  closeTime.setHours(rule.close[0], rule.close[1], 0, 0);
  const isWeekend = weekday === "Sat" || weekday === "Sun";

  let isOpen = !isWeekend && zonedNow >= openTime && zonedNow < closeTime;
  let transitionLabel = isOpen ? "close" : "open";
  let nextTransitionLocal = new Date(zonedNow);

  if (isWeekend) {
    const daysToMonday = weekday === "Sat" ? 2 : 1;
    nextTransitionLocal.setDate(nextTransitionLocal.getDate() + daysToMonday);
    nextTransitionLocal.setHours(rule.open[0], rule.open[1], 0, 0);
    isOpen = false;
  } else if (isOpen) {
    nextTransitionLocal = closeTime;
  } else if (zonedNow < openTime) {
    nextTransitionLocal = openTime;
  } else {
    nextTransitionLocal.setDate(nextTransitionLocal.getDate() + 1);
    nextTransitionLocal.setHours(rule.open[0], rule.open[1], 0, 0);
    const nextDay = nextTransitionLocal.getDay();
    if (nextDay === 6) nextTransitionLocal.setDate(nextTransitionLocal.getDate() + 2);
    if (nextDay === 0) nextTransitionLocal.setDate(nextTransitionLocal.getDate() + 1);
  }

  return {
    status: isOpen ? "Open" : "Closed",
    isOpen,
    transitionLabel,
    nextTransitionAt: new Date(Date.now() + (nextTransitionLocal.getTime() - zonedNow.getTime())).toISOString(),
    hoursLabel: rule.hoursLabel,
    timezone: rule.timeZone,
  };
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function safeExternalUrl(value) {
  if (!value) return "";
  try {
    const url = new URL(String(value), window.location.href);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
}

async function loadRadar({ silent = false } = {}) {
  const requestId = ++state.radarRequestId;
  if (!silent) {
    setStatus("Loading radar");
  }
  const result = await api(`/api/radar?symbol=${encodeURIComponent(state.activeTicker || "")}`);
  if (requestId !== state.radarRequestId) return;
  if (!state.dashboard) {
    state.dashboard = {};
  }
  state.dashboard.radar = result.radar || {};
  state.dashboard.radarUpdatedAt = result.updatedAt || "";
  state.dashboard.headlines = result.headlines || state.dashboard.headlines || [];
  renderBanner();
}

async function loadOverviewFast({ silent = false } = {}) {
  const requestId = ++state.overviewRequestId;
  if (!silent) {
    setStatus("Loading quote");
  }
  const params = new URLSearchParams({
    symbols: state.watchlist.join(","),
    active: state.activeTicker || "",
    region: state.selectedRegion || "",
  });
  const result = await api(`/api/overview?${params.toString()}`);
  if (requestId !== state.overviewRequestId) return;
  if (!state.dashboard) {
    state.dashboard = {};
  }

  state.dashboard.updatedAt = result.updatedAt || state.dashboard.updatedAt;
  state.dashboard.watchlist = result.watchlist || state.dashboard.watchlist || [];
  if (result.active) {
    const previousActive = state.dashboard.active || {};
    const mergedActive = {
      ...buildPendingActive(result.active.symbol),
      ...previousActive,
      ...result.active,
      marketSession:
        result.active.marketSession ||
        buildClientMarketSession(result.active.exchange || result.active.region, result.active.marketState, result.active.region),
    };
    state.dashboard.active = mergeQuoteIntoActiveHistory(mergedActive, previousActive, result.updatedAt);
  }
  if (result.active?.price || (result.watchlist || []).length) {
    setStatus("Live quote loaded");
    markDashboardInteractive("Live quote loaded");
    renderDataFlowBar();
    if (!state.quoteStream) {
      startQuoteStream();
    }
  }

  nextFrame(() => {
    renderWatchlist();
    renderBoard();
    renderPulse();
    if (state.dashboard?.active) {
      patchOverviewLiveSurface(
        state.dashboard.active,
        state.dashboard.active.forecast || emptyForecastPayload(),
        { redrawChart: true },
      );
    }
    renderTopbar();
  });
}

function emptyForecastPayload() {
  return {
    direction: "Refreshing",
    confidence: 0,
    fairValueGap: 0,
    eventPressureLabel: "Pending",
    mae: 0,
    expectedReturn: 0,
    projected: [],
    factors: [],
    triggers: [],
    models: {
      classic: { direction: "Pending", expectedReturn: 0, confidence: 0, summary: "Classic stack refreshing." },
      modern: { direction: "Pending", expectedReturn: 0, confidence: 0, summary: "Modern overlay refreshing." },
      agreement: { label: "Pending", score: 0, summary: "Agreement refreshing." },
    },
  };
}

function buildPendingActive(symbol) {
  const watchItem = (state.dashboard?.watchlist || []).find((item) => item.symbol === symbol);
  const previous = state.dashboard?.active || {};
  if (!watchItem && previous.symbol === symbol) {
    return previous;
  }
  const nextName = watchItem?.name || previous.name || symbol;
  return {
    ...previous,
    ...watchItem,
    symbol,
    name: nextName,
    regime: "Refreshing",
    history: watchItem?.symbol === previous.symbol ? previous.history || [] : [],
    historySeries: watchItem?.symbol === previous.symbol
      ? previous.historySeries || []
      : (loadChartCache(symbol, state.chartRange) || []),
    relationshipCards: [],
    driverCards: [],
    stats: watchItem?.symbol === previous.symbol ? previous.stats || [] : [],
    headlines: watchItem?.symbol === previous.symbol ? previous.headlines || [] : [],
    marketSession: buildClientMarketSession(
      watchItem?.exchange || previous.exchange || previous.region,
      watchItem?.marketState || previous.marketState,
      watchItem?.region || previous.region,
    ),
    forecast: {
      ...emptyForecastPayload(),
      ...(watchItem?.price !== undefined ? { expectedReturn: 0 } : {}),
    },
    recommendation: { upside: 0, base: 100, downside: 0, scenarioSignal: "Refreshing" },
    classicQuant: {
      summary: "Classic quant readings are refreshing for the new active ticker.",
      cards: [],
    },
  };
}

function primeActiveTickerSelection(symbol) {
  if (!state.dashboard) return;
  state.dashboard.active = buildPendingActive(symbol);
  state.labResult = null;
  state.academyDetail = state.academyCache[symbol] || null;
  state.eventResult = null;
}

function setStatus(message) {
  // Update all live indicators in the page
  document.body.classList.toggle("status-updated", Boolean(message));
  const indicators = document.querySelectorAll(".live-indicator-label");
  const loadingWords = ["Loading", "Refreshing", "Searching", "Resolving", "Saving", "Running", "Thinking", "Syncing"];
  const isLoading = loadingWords.some((word) => String(message).startsWith(word));
  indicators.forEach((el) => {
    setTextIfChanged(el, isLoading ? "Updating" : "Live");
  });
  const dots = document.querySelectorAll(".live-indicator-dot");
  const background = isLoading ? "rgba(255, 176, 0, 0.9)" : "rgba(90, 242, 197, 0.9)";
  const boxShadow = isLoading ? "0 0 4px rgba(255, 176, 0, 0.6)" : "0 0 4px rgba(90, 242, 197, 0.6)";
  dots.forEach((el) => {
    if (el.style.background !== background) el.style.background = background;
    if (el.style.boxShadow !== boxShadow) el.style.boxShadow = boxShadow;
  });
}

function markDashboardInteractive(message = "Live quote loaded") {
  if (state.bootReady) return;
  state.bootReady = true;
  document.body.classList.add("app-ready");
  document.body.classList.remove("app-booting");
  setStatus(message);
}

function nextFrame(callback) {
  window.requestAnimationFrame(() => window.requestAnimationFrame(callback));
}

function deferWork(callback, timeout = 120) {
  if ("requestIdleCallback" in window) {
    window.requestIdleCallback(callback, { timeout });
    return;
  }
  window.setTimeout(callback, 0);
}

function logNonAbort(error) {
  if (error?.name === "AbortError") return;
  if (String(error?.message || error).includes("signal is aborted")) return;
  console.error(error);
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

function initStarfieldParallax() {
  const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
  const finePointer = window.matchMedia?.("(pointer: fine)")?.matches;
  if (reduceMotion || !finePointer || window.innerWidth < 1100 || !document.body.classList.contains("enable-ambient-motion")) return;
  let raf = 0;
  let lastPaint = 0;
  const update = (event) => {
    if (event.target instanceof Element && event.target.closest(".hero-chart-card, #overview")) {
      return;
    }
    const now = performance.now();
    if (now - lastPaint < 160) return;
    lastPaint = now;
    window.cancelAnimationFrame(raf);
    raf = window.requestAnimationFrame(() => {
      const x = (event.clientX / window.innerWidth - 0.5) * 28;
      const y = (event.clientY / window.innerHeight - 0.5) * 22;
      document.body.style.setProperty("--star-x", `${x.toFixed(2)}px`);
      document.body.style.setProperty("--star-y", `${y.toFixed(2)}px`);
      document.body.style.setProperty("--star-glow-x", `${(event.clientX / window.innerWidth * 100).toFixed(2)}%`);
      document.body.style.setProperty("--star-glow-y", `${(event.clientY / window.innerHeight * 100).toFixed(2)}%`);
    });
  };
  window.addEventListener("pointermove", update, { passive: true });
  window.addEventListener("pointerleave", () => {
    document.body.style.setProperty("--star-x", "0px");
    document.body.style.setProperty("--star-y", "0px");
    document.body.style.setProperty("--star-glow-x", "50%");
    document.body.style.setProperty("--star-glow-y", "18%");
  }, { passive: true });
}

function dataFlowLabel(path = "") {
  if (path.includes("/api/dashboard")) return "Dashboard refresh";
  if (path.includes("/api/overview")) return "Quote overview";
  if (path.includes("/api/sectors")) return "Sector matrix";
  if (path.includes("/api/market-map")) return "Market heat map";
  if (path.includes("/api/data-sources")) return "Source registry";
  if (path.includes("/api/academy")) return "Learning context";
  if (path.includes("/api/research")) return "Research workspace";
  if (path.includes("/api/history/warm")) return "History warmup";
  if (path.includes("/api/events")) return "Event flow";
  if (path.includes("/api/radar")) return "Market radar";
  if (path.includes("/api/search")) return "Symbol search";
  return "";
}

function startDataFlowTask(path) {
  if (String(path).includes("/api/history/status")) return "";
  const label = dataFlowLabel(String(path));
  if (!label) return "";
  const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  state.dataFlow.tasks[id] = { id, label, status: "running", startedAt: Date.now(), progress: 18 };
  renderDataFlowBar();
  return id;
}

function finishDataFlowTask(id, status = "done") {
  if (!id || !state.dataFlow?.tasks?.[id]) return;
  state.dataFlow.tasks[id] = {
    ...state.dataFlow.tasks[id],
    status,
    progress: status === "done" ? 100 : 0,
    finishedAt: Date.now(),
  };
  if (status !== "done") {
    state.dataFlow.lastError = `${state.dataFlow.tasks[id].label} failed`;
  }
  window.setTimeout(() => {
    if (state.dataFlow?.tasks?.[id]?.finishedAt && Date.now() - state.dataFlow.tasks[id].finishedAt >= 2200) {
      delete state.dataFlow.tasks[id];
      renderDataFlowBar();
    }
  }, 2400);
  renderDataFlowBar();
}

function hasActiveDataFlowWork() {
  const taskActive = Object.values(state.dataFlow?.tasks || {}).some((task) => ["queued", "running", "connecting", "retry"].includes(String(task.status).toLowerCase()));
  const jobActive = (state.dataFlow?.history?.active || []).length > 0 || (state.dataFlow?.history?.scriptActive || []).length > 0;
  const readinessActive = readinessJobs().some((job) => !["done", "ready"].includes(String(job.status).toLowerCase()));
  return readinessActive || taskActive || jobActive || state.dataFlow?.stream === "connecting" || state.dataFlow?.stream === "retry";
}

function scheduleDataFlowAutoHide(delay = 4200) {
  if (!state.dataFlow) return;
  window.clearTimeout(state.dataFlow.hideTimer);
  if (state.dataFlow.expanded || hasActiveDataFlowWork()) {
    state.dataFlow.hidden = false;
    return;
  }
  state.dataFlow.hideTimer = window.setTimeout(() => {
    if (!state.dataFlow.expanded && !hasActiveDataFlowWork()) {
      const node = document.getElementById("data-flow-bar");
      if (node) {
        const rect = node.getBoundingClientRect();
        state.dataFlow.x = window.innerWidth - 46;
        state.dataFlow.y = Math.max(12, Math.min(window.innerHeight - Math.max(72, rect.height) - 12, rect.top));
      }
      state.dataFlow.hidden = true;
      renderDataFlowBar({ skipAutoHide: true });
    }
  }, delay);
}

function revealDataFlow({ expand = false } = {}) {
  if (!state.dataFlow) return;
  const node = document.getElementById("data-flow-bar");
  if (node && Number(state.dataFlow.x) > window.innerWidth - 90) {
    const width = Math.min(node.offsetWidth || 420, window.innerWidth - 24);
    state.dataFlow.x = Math.max(12, window.innerWidth - width - 18);
  }
  state.dataFlow.hidden = false;
  if (expand) state.dataFlow.expanded = true;
  persistDataFlowState();
  renderDataFlowBar();
}

function dataFlowJobs() {
  const requestTasks = Object.values(state.dataFlow?.tasks || {});
  const historyJobs = (state.dataFlow?.history?.jobs || []).slice(-5).map((job) => {
    const total = Number(job.total || 0);
    const completed = Number(job.completed || 0);
    const progress = total ? Math.round((completed / total) * 100) : job.status === "done" ? 100 : 0;
    return {
      id: job.jobKey || `history-${job.queuedAt || ""}`,
      label: `History ${job.reason || "warmup"}`,
      status: job.status || "queued",
      progress,
      detail: `${completed}/${total || "?"} ranges`,
      errors: job.errors || [],
    };
  });
  const scriptJobs = (state.dataFlow?.history?.scripts || []).slice(-5).map((job) => {
    const steps = job.steps || [];
    const total = Number(job.total || steps.length || 0);
    const completed = Number(job.completed || steps.filter((step) => ["done", "skipped"].includes(String(step.status).toLowerCase())).length);
    const activeStep = steps.find((step) => ["queued", "running"].includes(String(step.status).toLowerCase())) || steps.find((step) => String(step.status).toLowerCase() === "error") || steps[0];
    const progress = total ? Math.round((completed / total) * 100) : job.status === "done" ? 100 : 0;
    return {
      id: job.jobKey || `script-${job.queuedAt || ""}`,
      label: "Backend scripts",
      status: job.status || "queued",
      progress,
      detail: activeStep ? `${activeStep.label || activeStep.script}: ${activeStep.status}` : `${completed}/${total || "?"} scripts`,
      errors: job.errors || [],
      background: true,
    };
  });
  const quoteProviders = state.dataFlow?.history?.quoteProviders || [];
  const quoteProviderJob = {
    id: "quote-source-chain",
    label: "Quote source chain",
    status: quoteProviders.some((provider) => provider.status === "available") ? "ready" : "retry",
    progress: quoteProviders.length ? Math.round((quoteProviders.filter((provider) => provider.status === "available").length / quoteProviders.length) * 100) : 0,
    detail: quoteProviders.length ? `${quoteProviders.filter((provider) => provider.status === "available").length}/${quoteProviders.length} sources available` : "waiting for provider registry",
    errors: quoteProviders.filter((provider) => provider.status === "cooldown").slice(0, 2).map((provider) => `${provider.label} cooling down`),
    background: true,
  };
  const streamJob = {
    id: "quote-stream",
    label: "Quote stream",
    status: state.dataFlow.stream || "connecting",
    progress: state.dataFlow.stream === "live" ? 100 : 40,
    detail: state.activeTicker || "watchlist",
    background: true,
  };
  return [...readinessJobs(), streamJob, quoteProviderJob, ...requestTasks, ...scriptJobs, ...historyJobs];
}

function readinessJobs() {
  const active = state.dashboard?.active;
  const hasQuote = Boolean(active?.symbol && Number.isFinite(Number(active.price)));
  const hasDashboardPayload = Boolean(active?.forecast && active?.stockDossier?.daySnapshot);
  const hasChart = document.getElementById("hero-projection-chart")?.dataset.chartReady === "1";
  const hasVisibleDossier = document.querySelectorAll("#stock-dossier .dossier-card").length > 0;
  const hasVisiblePrediction = Boolean(document.querySelector("#prediction-panel .prediction-grid"));
  const boot = state.dataFlow?.boot || {};
  const workspaceReady = Boolean(boot.config && boot.presets && boot.watchlists);
  const hasSectorContext = (state.sectorStripSectors || []).length > 0 || Boolean(document.querySelector("#sector-overview-strip")?.children.length);
  const hasMarketHeatMap = (state.marketHeatMap?.tiles || []).length > 0 || document.querySelectorAll("#market-heat-map-grid .market-heat-tile").length > 0;
  const dashboardFailed = Boolean(state.dataFlow?.lastError && !hasDashboardPayload);
  return [
    {
      id: "ready-quote",
      label: "Quote overview",
      status: hasQuote ? "done" : "running",
      progress: hasQuote ? 100 : 35,
      detail: hasQuote ? active.symbol : "loading active quote",
      readiness: true,
    },
    {
      id: "ready-dashboard",
      label: "Dashboard payload",
      status: hasDashboardPayload ? "done" : dashboardFailed ? "error" : "running",
      progress: hasDashboardPayload ? 100 : dashboardFailed ? 0 : 45,
      detail: hasDashboardPayload ? "forecast + dossier data" : (state.dataFlow?.lastError || "loading full API payload"),
      readiness: true,
    },
    {
      id: "ready-chart",
      label: "Price chart",
      status: hasChart ? "done" : hasDashboardPayload ? "running" : "queued",
      progress: hasChart ? 100 : hasDashboardPayload ? 65 : 0,
      detail: hasChart ? "rendered" : "waiting for history",
      readiness: true,
    },
    {
      id: "ready-panels",
      label: "Visible panels",
      status: hasVisibleDossier && hasVisiblePrediction ? "done" : hasDashboardPayload ? "running" : "queued",
      progress: hasVisibleDossier && hasVisiblePrediction ? 100 : hasDashboardPayload ? 70 : 0,
      detail: hasVisibleDossier ? "dossier/prediction painting" : "waiting for full dashboard",
      readiness: true,
    },
    {
      id: "ready-workspace",
      label: "Workspace setup",
      status: workspaceReady ? "done" : "running",
      progress: workspaceReady ? 100 : 50,
      detail: `config ${boot.config ? "ok" : "..."}, presets ${boot.presets ? "ok" : "..."}, lists ${boot.watchlists ? "ok" : "..."}`,
      readiness: true,
    },
    {
      id: "ready-sectors",
      label: "Sector context",
      status: hasSectorContext ? "done" : "running",
      progress: hasSectorContext ? 100 : 40,
      detail: hasSectorContext ? "sector strip ready" : "loading market context",
      readiness: true,
    },
    {
      id: "ready-market-map",
      label: "Market heat map",
      status: hasMarketHeatMap ? "done" : hasSectorContext ? "running" : "queued",
      progress: hasMarketHeatMap ? 100 : hasSectorContext ? 60 : 0,
      detail: hasMarketHeatMap ? "tiles painted" : "waiting for quote/proxy tiles",
      readiness: true,
    },
  ];
}

function ensureDataFlowShell(node) {
  if (!node || node.querySelector(".data-flow-shell")) return;
  node.innerHTML = `
    <div class="data-flow-shell">
      <button class="data-flow-grip" type="button" aria-label="Move data flow bar" title="Move data flow" data-data-flow-drag>
        <span aria-hidden="true"></span>
      </button>
      <button class="data-flow-main" type="button" aria-expanded="false" data-data-flow-toggle>
        <span data-flow-label></span>
        <strong data-flow-status></strong>
        <em data-flow-progress></em>
      </button>
      <div class="data-flow-meter"><span data-flow-meter></span></div>
      <div class="data-flow-detail" data-flow-detail></div>
    </div>
  `;
}

function renderDataFlowBar({ skipAutoHide = false } = {}) {
  // Mirror updates into the new notification bell + panel. The bell is the
  // visible surface now; the floating bar is hidden via CSS but its render
  // function still runs cheaply so its sub-components (auto-hide timer,
  // history-progress polls) keep working.
  renderNotificationCenter();
  const node = document.getElementById("data-flow-bar");
  if (!node || !state.dataFlow) return;
  if (state.dataFlow.x !== null && state.dataFlow.y !== null) {
    node.style.left = `${state.dataFlow.x}px`;
    node.style.top = `${state.dataFlow.y}px`;
    node.style.right = "auto";
    node.style.bottom = "auto";
  }
  const jobs = dataFlowJobs();
  const activeJobs = jobs.filter((job) => ["queued", "running", "connecting", "retry"].includes(String(job.status).toLowerCase()));
  const errorJobs = jobs.filter((job) => String(job.status).toLowerCase() === "error");
  const readiness = jobs.filter((job) => job.readiness);
  const backgroundJobs = jobs.filter((job) => job.background);
  const readinessProgress = readiness.length
    ? Math.round(readiness.reduce((sum, job) => sum + Number(job.progress || 0), 0) / readiness.length)
    : 100;
  const readinessDone = readiness.length > 0 && readiness.every((job) => ["done", "ready"].includes(String(job.status).toLowerCase()));
  const blockingErrors = errorJobs.filter((job) => job.readiness);
  const progress = readinessDone ? 100 : Math.min(readinessProgress, 99);
  const primary =
    blockingErrors[0]
    || readiness.find((job) => !["done", "ready"].includes(String(job.status).toLowerCase()))
    || activeJobs.find((job) => !job.background)
    || backgroundJobs[0]
    || jobs[0]
    || { label: "Data flow", status: "ready", progress: 100 };
  node.classList.toggle("is-expanded", Boolean(state.dataFlow.expanded));
  node.classList.toggle("is-peek", Boolean(state.dataFlow.hidden && !state.dataFlow.expanded));
  ensureDataFlowShell(node);
  const toggle = node.querySelector("[data-data-flow-toggle]");
  if (toggle) toggle.setAttribute("aria-expanded", state.dataFlow.expanded ? "true" : "false");
  setTextIfChanged(node.querySelector("[data-flow-label]"), primary.label);
  setTextIfChanged(node.querySelector("[data-flow-status]"), blockingErrors.length ? "Needs attention" : readinessDone && !activeJobs.length ? "Ready" : primary.status);
  setTextIfChanged(node.querySelector("[data-flow-progress]"), `${progress}%`);
  const meter = node.querySelector("[data-flow-meter]");
  if (meter) meter.style.width = `${Math.max(4, progress)}%`;
  const detail = node.querySelector("[data-flow-detail]");
  if (detail && state.dataFlow.expanded) {
    setHTMLIfChanged(detail, `
      ${jobs.map((job) => {
        const isDone = ["done", "ready", "live"].includes(String(job.status).toLowerCase());
        return `
        <article class="data-flow-job ${String(job.status).toLowerCase()}">
          <span>${isDone ? "✓ " : ""}${job.label}</span>
          <strong>${isDone ? "done" : job.status}</strong>
          <em>${job.detail || `${job.progress || 0}%`}</em>
          ${(job.errors || []).slice(0, 1).map((error) => `<small>${error}</small>`).join("")}
        </article>`;
      }).join("")}
      <small>${readiness.filter((job) => ["done", "ready"].includes(String(job.status).toLowerCase())).length}/${readiness.length || 1} visible stages complete · ${backgroundJobs.map((job) => `${job.label}: ${job.status}`).join(" · ") || "background idle"} · Updated ${state.dataFlow.lastUpdated ? new Date(state.dataFlow.lastUpdated).toLocaleTimeString() : "just now"}</small>
    `);
  }
  bindDataFlowBar();
  if (!skipAutoHide) scheduleDataFlowAutoHide(activeJobs.length || !readinessDone ? 7200 : 4200);
}

function bindDataFlowBar() {
  const node = document.getElementById("data-flow-bar");
  if (!node || node.dataset.bound === "1") return;
  node.dataset.bound = "1";
  node.addEventListener("click", (event) => {
    const target = event.target;
    if (state.dataFlow.hidden) {
      revealDataFlow({ expand: true });
      return;
    }
    if (!(target instanceof Element) || !target.closest("[data-data-flow-toggle]")) return;
    state.dataFlow.expanded = !state.dataFlow.expanded;
    state.dataFlow.hidden = false;
    persistDataFlowState();
    renderDataFlowBar();
  });
  node.addEventListener("mouseenter", () => {
    if (state.dataFlow.hidden) revealDataFlow();
  });
  let dragOffset = null;
  node.addEventListener("pointerdown", (event) => {
    const target = event.target;
    if (!(target instanceof Element) || !target.closest("[data-data-flow-drag]")) return;
    event.preventDefault();
    state.dataFlow.hidden = false;
    node.classList.remove("is-peek");
    const rect = node.getBoundingClientRect();
    dragOffset = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    node.classList.add("is-dragging");
    node.setPointerCapture(event.pointerId);
  });
  node.addEventListener("pointermove", (event) => {
    if (!dragOffset) return;
    const width = node.offsetWidth || 280;
    const height = node.offsetHeight || 80;
    state.dataFlow.x = Math.max(12, Math.min(window.innerWidth - width - 12, event.clientX - dragOffset.x));
    state.dataFlow.y = Math.max(12, Math.min(window.innerHeight - height - 12, event.clientY - dragOffset.y));
    node.style.left = `${state.dataFlow.x}px`;
    node.style.top = `${state.dataFlow.y}px`;
    node.style.right = "auto";
    node.style.bottom = "auto";
  });
  node.addEventListener("pointerup", () => {
    if (!dragOffset) return;
    dragOffset = null;
    node.classList.remove("is-dragging");
    persistDataFlowState();
  });
  node.addEventListener("pointercancel", () => {
    dragOffset = null;
    node.classList.remove("is-dragging");
  });
  node.addEventListener("lostpointercapture", () => {
    dragOffset = null;
    node.classList.remove("is-dragging");
  });
}

async function pollHistoryProgress() {
  if (state.dataFlow.polling) return;
  state.dataFlow.polling = true;
  try {
    const payload = await api("/api/history/status", { timeoutMs: 5000 });
    state.dataFlow.history = payload || { jobs: [], active: [] };
    state.dataFlow.lastUpdated = new Date().toISOString();
    renderDataFlowBar();
  } catch (error) {
    state.dataFlow.stream = state.dataFlow.stream || "retry";
    logNonAbort(error);
  } finally {
    state.dataFlow.polling = false;
    scheduleHistoryProgressPoll();
  }
}

function hasActiveHistoryJobs() {
  const history = state.dataFlow?.history || {};
  const jobs = [...(history.active || []), ...(history.jobs || []), ...(history.scriptActive || []), ...(history.scripts || [])];
  return jobs.some((job) => ["queued", "running"].includes(String(job.status || "").toLowerCase()));
}

function scheduleHistoryProgressPoll(delayMs = null) {
  window.clearTimeout(state.historyPollTimer);
  const delay = delayMs ?? (hasActiveHistoryJobs() ? REFRESH_INTERVALS.historyActive : REFRESH_INTERVALS.historyIdle);
  state.historyPollTimer = window.setTimeout(() => {
    pollHistoryProgress();
  }, delay);
}

function setBootMessage(message, detail = "") {
  const track = document.getElementById("headline-track");
  if (!track) return;
  track.innerHTML = `<span>${message}${detail ? ` ${detail}` : ""}</span>`;
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
  state.alerts = [{ id, symbol, direction, message, createdAt: Date.now() }].concat(state.alerts).slice(0, 8);
  renderAlerts();
  renderNotificationCenter();
  window.setTimeout(() => dismissAlert(id), 9000);
}

/* ── Notification bell + panel ──────────────────────────────────────────────
 * Consolidates the old `.alert-stack` toasts and the floating `.data-flow-bar`
 * into a single top-right surface:
 *   - Bell icon shows an amber count badge for live alerts.
 *   - Thin ring around the bell shows backend job progress (0–100%).
 *   - Click opens a dropdown with alerts (top) + flow rows (bottom).
 * A separate `showStatusBanner(text, kind)` renders the transient horizontal
 * banner under the topbar for blocked-source notices that auto-dismiss.
 */
function renderNotificationCenter() {
  renderNotificationBell();
  if (!document.getElementById("notification-panel")?.hidden) {
    renderNotificationPanel();
  }
  detectBlockedProviders();
}

function renderNotificationBell() {
  const bell = document.getElementById("notification-bell");
  if (!bell) return;
  const jobs = (typeof dataFlowJobs === "function" ? dataFlowJobs() : []) || [];
  const activeJobs = jobs.filter((job) => ["queued", "running", "connecting", "retry"].includes(String(job.status).toLowerCase()));
  const errorJobs = jobs.filter((job) => String(job.status).toLowerCase() === "error");
  const readiness = jobs.filter((job) => job.readiness);
  const readinessProgress = readiness.length
    ? Math.round(readiness.reduce((sum, job) => sum + Number(job.progress || 0), 0) / readiness.length)
    : 100;
  const readinessDone = readiness.length > 0 && readiness.every((job) => ["done", "ready"].includes(String(job.status).toLowerCase()));
  const progress = readinessDone ? 100 : Math.min(readinessProgress, 99);
  const busy = activeJobs.length > 0 || (!readinessDone && readiness.length > 0);
  const alertCount = (state.alerts || []).length;
  const badgeCount = alertCount + errorJobs.length;
  bell.classList.toggle("is-busy", busy);
  bell.classList.toggle("is-warn", errorJobs.length > 0 && errorJobs.length < jobs.length / 2);
  bell.classList.toggle("is-error", errorJobs.length > 0 && errorJobs.length >= Math.max(1, jobs.length / 2));
  const fill = bell.querySelector(".bell-progress-fill");
  if (fill) fill.style.strokeDashoffset = String(100 - progress);
  const countNode = document.getElementById("notification-count");
  if (countNode) {
    if (badgeCount > 0) {
      setTextIfChanged(countNode, String(Math.min(badgeCount, 99)));
      countNode.hidden = false;
    } else {
      countNode.hidden = true;
    }
  }
  bell.title = busy
    ? `Backend ${progress}% · ${activeJobs.length} active`
    : alertCount
      ? `${alertCount} alert${alertCount > 1 ? "s" : ""}`
      : "Notifications";
}

function renderNotificationPanel() {
  const panel = document.getElementById("notification-panel");
  if (!panel) return;
  const alertsHost = document.getElementById("notification-panel-alerts");
  const flowHost = document.getElementById("notification-panel-flow");
  const summary = document.getElementById("notification-panel-summary");
  const jobs = (typeof dataFlowJobs === "function" ? dataFlowJobs() : []) || [];
  const readiness = jobs.filter((job) => job.readiness);
  const readinessProgress = readiness.length
    ? Math.round(readiness.reduce((sum, job) => sum + Number(job.progress || 0), 0) / readiness.length)
    : 100;
  if (summary) {
    const errorJobs = jobs.filter((job) => String(job.status).toLowerCase() === "error");
    setTextIfChanged(
      summary,
      errorJobs.length
        ? `${errorJobs.length} source${errorJobs.length > 1 ? "s" : ""} blocked · backend ${readinessProgress}%`
        : `Backend ${readinessProgress}% · ${jobs.length} stage${jobs.length === 1 ? "" : "s"}`
    );
  }
  if (alertsHost) {
    const alerts = state.alerts || [];
    if (!alerts.length) {
      setHTMLIfChanged(alertsHost, "");
    } else {
      setHTMLIfChanged(
        alertsHost,
        alerts.map((alert) => {
          const dirClass = alert.direction === "up" ? "is-up" : alert.direction === "down" ? "is-down" : "is-warn";
          const action = alert.direction === "up" ? "surged" : alert.direction === "down" ? "slipped" : "update";
          const when = alert.createdAt ? new Date(alert.createdAt).toLocaleTimeString() : "";
          return `
            <div class="npa-item ${dirClass}" data-alert-id="${escapeHtml(alert.id)}">
              <div class="npa-dot" aria-hidden="true"></div>
              <div class="npa-body">
                <strong>${escapeHtml(alert.symbol)} ${action}</strong>
                <span>${escapeHtml(alert.message)}</span>
                ${when ? `<time>${escapeHtml(when)}</time>` : ""}
              </div>
            </div>
          `;
        }).join("")
      );
    }
  }
  if (flowHost) {
    if (!jobs.length) {
      setHTMLIfChanged(flowHost, `<div class="npf-row"><span class="npf-label">No active jobs</span><span class="npf-state is-ok">idle</span></div>`);
    } else {
      setHTMLIfChanged(
        flowHost,
        jobs.slice(0, 8).map((job) => {
          const status = String(job.status || "").toLowerCase();
          const stateClass = status === "error" ? "is-error"
            : status === "done" || status === "ready" || status === "live" ? "is-ok"
            : status === "retry" || status === "queued" || status === "connecting" || status === "running" ? "is-busy"
            : "is-warn";
          const stateLabel = status || (job.progress != null ? `${job.progress}%` : "idle");
          return `<div class="npf-row"><span class="npf-label">${escapeHtml(job.label || "Job")}</span><span class="npf-state ${stateClass}">${escapeHtml(stateLabel)}</span></div>`;
        }).join("")
      );
    }
  }
}

function bindNotificationBell() {
  const bell = document.getElementById("notification-bell");
  const panel = document.getElementById("notification-panel");
  if (!bell || !panel || bell.dataset.bound === "1") return;
  bell.dataset.bound = "1";
  const closePanel = () => {
    panel.hidden = true;
    bell.setAttribute("aria-expanded", "false");
  };
  const openPanel = () => {
    renderNotificationPanel();
    panel.hidden = false;
    bell.setAttribute("aria-expanded", "true");
  };
  bell.addEventListener("click", (event) => {
    event.stopPropagation();
    if (panel.hidden) openPanel(); else closePanel();
  });
  document.addEventListener("click", (event) => {
    if (panel.hidden) return;
    if (!(event.target instanceof Node)) return;
    if (panel.contains(event.target) || bell.contains(event.target)) return;
    closePanel();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) closePanel();
  });
  const clearBtn = panel.querySelector(".notification-clear");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      state.alerts = [];
      renderAlerts();
      renderNotificationCenter();
    });
  }
}

const STATUS_BANNER_TIMERS = new Map();
function showStatusBanner(message, { kind = "warn", duration = 4500, key = "" } = {}) {
  const banner = document.getElementById("status-banner");
  if (!banner || !message) return;
  const bannerKey = key || message;
  // Dedupe: same message within 8s gets ignored to avoid spam.
  const existingTimer = STATUS_BANNER_TIMERS.get(bannerKey);
  if (existingTimer) window.clearTimeout(existingTimer);
  banner.classList.remove("is-error", "is-warn", "is-info");
  banner.classList.add(`is-${kind}`);
  banner.innerHTML = `<span class="sb-dot" aria-hidden="true"></span><strong>${escapeHtml(message)}</strong>`;
  banner.hidden = false;
  // Force reflow so the transform animates from off-screen
  void banner.offsetHeight;
  banner.classList.add("is-visible");
  const timer = window.setTimeout(() => {
    banner.classList.remove("is-visible");
    window.setTimeout(() => {
      // Only hide if no later banner replaced it
      if (!banner.classList.contains("is-visible")) banner.hidden = true;
    }, 260);
    STATUS_BANNER_TIMERS.delete(bannerKey);
  }, duration);
  STATUS_BANNER_TIMERS.set(bannerKey, timer);
}

let lastBlockedProviderSnapshot = new Set();
function detectBlockedProviders() {
  // Watch state.dataFlow.history.quoteProviders for newly-failed entries and
  // surface them via the status banner. Each provider only triggers once
  // until it recovers (so we don't re-banner on every poll while still down).
  const providers = state.dataFlow?.history?.quoteProviders || [];
  const blockedNow = new Set();
  providers.forEach((entry) => {
    if (!entry || !entry.id) return;
    const status = String(entry.status || "").toLowerCase();
    if (status === "error" || status === "blocked") {
      blockedNow.add(entry.id);
      if (!lastBlockedProviderSnapshot.has(entry.id)) {
        const label = entry.label || entry.id;
        const next = entry.fallback || "switching to alternate source";
        showStatusBanner(`${label} unreachable — ${next}`, { kind: "warn", key: `block:${entry.id}` });
      }
    }
  });
  lastBlockedProviderSnapshot = blockedNow;
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
  animateSvgRefresh(svg);
}

// ── Client-side chart history cache (localStorage) ───────────────────────────
const CHART_CACHE_KEY_PREFIX = "fb-chart-v1:";
const CHART_CACHE_MAX_AGE_MS = {
  "1D": 90_000, "3D": 300_000, "5D": 600_000,
  "1M": 3_600_000, "1Y": 21_600_000,
  "2Y": 43_200_000, "3Y": 86_400_000, "5Y": 86_400_000, "MAX": 86_400_000,
};

function saveChartCache(symbol, range, historySeries) {
  if (!symbol || !range || !Array.isArray(historySeries) || !historySeries.length) return;
  try {
    const key = `${CHART_CACHE_KEY_PREFIX}${symbol}:${range}`;
    localStorage.setItem(key, JSON.stringify({ ts: Date.now(), series: historySeries }));
  } catch (_) { /* quota exceeded — silent */ }
}

function loadChartCache(symbol, range) {
  if (!symbol || !range) return null;
  try {
    const key = `${CHART_CACHE_KEY_PREFIX}${symbol}:${range}`;
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const { ts, series } = JSON.parse(raw);
    const maxAge = CHART_CACHE_MAX_AGE_MS[range.toUpperCase()] || 3_600_000;
    if (Date.now() - ts > maxAge) { localStorage.removeItem(key); return null; }
    return Array.isArray(series) && series.length ? series : null;
  } catch (_) { return null; }
}
// ─────────────────────────────────────────────────────────────────────────────

function normalizeChartRange(range = "1M") {
  return String(range || "1M").toUpperCase();
}

function buildFallbackHistorySeries(history, range = "1M") {
  const values = (history || []).map((value) => Number(value)).filter((value) => Number.isFinite(value));
  if (!values.length) return [];
  const now = new Date();
  const stepMap = {
    "1D": 5 * 60 * 1000,
    "3D": 24 * 60 * 60 * 1000,
    "5D": 24 * 60 * 60 * 1000,
    "1M": 24 * 60 * 60 * 1000,
    "1Y": 7 * 24 * 60 * 60 * 1000,
    "2Y": 14 * 24 * 60 * 60 * 1000,
    "3Y": 30 * 24 * 60 * 60 * 1000,
    "5Y": 30 * 24 * 60 * 60 * 1000,
    "MAX": 30 * 24 * 60 * 60 * 1000,
  };
  const step = stepMap[range] || stepMap["1M"];
  const start = now.getTime() - ((values.length - 1) * step);
  return values.map((value, index) => ({
    value,
    timestamp: new Date(start + (index * step)).toISOString(),
  }));
}

function normalizeHistorySeries(history, range = "1M") {
  if (!Array.isArray(history) || !history.length) return [];
  if (typeof history[0] === "object" && history[0] !== null) {
    return history
      .map((item) => ({
        value: Number(item.value),
        timestamp: item.timestamp || null,
        providerTimestamp: item.providerTimestamp || null,
        observedTimestamp: item.observedTimestamp || null,
      }))
      .filter((item) => Number.isFinite(item.value));
  }
  return buildFallbackHistorySeries(history, range);
}

function mergeQuoteIntoActiveHistory(active = {}, previousActive = {}, updatedAt = "", range = state.chartRange) {
  const price = Number(active.price);
  if (!Number.isFinite(price)) return active;
  const providerTimestamp = active.asOf || "";
  const observedTimestamp = active.receivedAt || updatedAt || new Date().toISOString();
  const timestamp = providerTimestamp || observedTimestamp;
  const normalizedRange = normalizeChartRange(range);
  const nextActive = { ...active };
  const previousSeries = Array.isArray(previousActive.historySeries) ? previousActive.historySeries : [];
  if (previousSeries.length) {
    const nextSeries = [...previousSeries];
    const lastPoint = nextSeries[nextSeries.length - 1] || {};
    const lastTime = lastPoint.timestamp ? new Date(lastPoint.timestamp).getTime() : 0;
    const nextTime = timestamp ? new Date(timestamp).getTime() : 0;
    const observedTime = observedTimestamp ? new Date(observedTimestamp).getTime() : 0;
    const priceChanged = Math.abs(Number(lastPoint.value) - price) > Math.max(Math.abs(price) * 0.00001, 0.0001);
    const providerAdvanced = Boolean(nextTime && lastTime && nextTime > lastTime);
    const liveTimestamp = providerAdvanced ? nextTime : observedTime;
    const livePoint = {
      value: price,
      timestamp: liveTimestamp ? new Date(liveTimestamp).toISOString() : timestamp,
      providerTimestamp,
      observedTimestamp,
    };
    const appendGap = normalizedRange === "1D" ? 5_000 : 15_000;
    const canAppend = ["1D", "3D", "5D"].includes(normalizedRange)
      && priceChanged
      && liveTimestamp
      && lastTime
      && liveTimestamp > lastTime + appendGap;
    if (canAppend) {
      nextSeries.push(livePoint);
      nextActive.historySeries = nextSeries.slice(-320);
    } else if (priceChanged || providerAdvanced) {
      nextSeries[nextSeries.length - 1] = { ...lastPoint, ...livePoint };
      nextActive.historySeries = nextSeries;
    } else {
      nextActive.historySeries = nextSeries;
    }
  }
  const previousHistory = Array.isArray(previousActive.history) ? previousActive.history : [];
  if (previousHistory.length) {
    const nextHistory = [...previousHistory];
    nextHistory[nextHistory.length - 1] = price;
    nextActive.history = nextHistory;
  }
  return nextActive;
}

function buildProjectedSeries(historySeries, projected, range = "1M") {
  const values = (projected || []).map((value) => Number(value)).filter((value) => Number.isFinite(value));
  if (!values.length) return [];
  const lastTimestamp = historySeries[historySeries.length - 1]?.timestamp ? new Date(historySeries[historySeries.length - 1].timestamp) : new Date();
  const stepMap = {
    "1D": 5 * 60 * 1000,
    "3D": 24 * 60 * 60 * 1000,
    "5D": 24 * 60 * 60 * 1000,
    "1M": 24 * 60 * 60 * 1000,
    "1Y": 7 * 24 * 60 * 60 * 1000,
    "2Y": 14 * 24 * 60 * 60 * 1000,
    "3Y": 30 * 24 * 60 * 60 * 1000,
    "5Y": 30 * 24 * 60 * 60 * 1000,
    "MAX": 30 * 24 * 60 * 60 * 1000,
  };
  const step = stepMap[range] || stepMap["1M"];
  return values.map((value, index) => ({
    value,
    timestamp: new Date(lastTimestamp.getTime() + ((index + 1) * step)).toISOString(),
  }));
}

function chartTimeZone(options = {}) {
  return options.timeZone || exchangeTimeZoneForItem(options.item || state.dashboard?.active || {});
}

function chartZoneLabel(options = {}) {
  const item = options.item || state.dashboard?.active || {};
  return item.marketSession?.hoursLabel?.split(" ").pop() || chartTimeZone(options).replace(/^[^/]+\//, "").replace(/_/g, " ");
}

function formatAxisDate(timestamp, range = "1M", options = {}) {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "";
  const normalizedRange = normalizeChartRange(range);
  const longRanges = new Set(["2Y", "3Y", "5Y", "MAX"]);
  const timeZone = chartTimeZone(options);
  const formatterOptions = normalizedRange === "1D"
    ? { timeZone, hour: "2-digit", minute: "2-digit" }
    : (normalizedRange === "3D" || normalizedRange === "5D")
      ? { timeZone, day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }
      : (normalizedRange === "1Y" || longRanges.has(normalizedRange))
      ? { timeZone, month: "short", year: "2-digit" }
      : { timeZone, day: "2-digit", month: "short" };
  return date.toLocaleString([], formatterOptions);
}

function formatTooltipDate(timestamp, range = "1M", options = {}) {
  if (!timestamp) return "Time unavailable";
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "Time unavailable";
  const normalizedRange = normalizeChartRange(range);
  const timeZone = chartTimeZone(options);
  const formatterOptions = ["1D", "3D", "5D"].includes(normalizedRange)
    ? { timeZone, day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }
    : { timeZone, day: "2-digit", month: "short", year: "numeric" };
  return `${date.toLocaleString([], formatterOptions)} ${chartZoneLabel(options)}`;
}

function stdDev(values) {
  const clean = (values || []).map(Number).filter(Number.isFinite);
  if (clean.length < 2) return 0;
  const avg = clean.reduce((sum, value) => sum + value, 0) / clean.length;
  const variance = clean.reduce((sum, value) => sum + ((value - avg) ** 2), 0) / clean.length;
  return Math.sqrt(variance);
}

function buildSyntheticCandles(historySeries) {
  if (!Array.isArray(historySeries) || !historySeries.length) return [];
  const closes = historySeries.map((item) => Number(item.value)).filter(Number.isFinite);
  const typicalMove = Math.max(stdDev(closes.slice(-20)) || 0, Math.abs(closes[closes.length - 1] || 0) * 0.002);
  return historySeries.map((item, index) => {
    const close = Number(item.value);
    const open = index > 0 ? Number(historySeries[index - 1].value) : close;
    const prior = index > 1 ? Number(historySeries[index - 2].value) : open;
    const next = index < historySeries.length - 1 ? Number(historySeries[index + 1].value) : close;
    const wick = Math.max(Math.abs(close - open) * 0.32, typicalMove * 0.2, Math.abs(next - prior) * 0.08);
    return {
      open,
      close,
      high: Math.max(open, close) + wick,
      low: Math.min(open, close) - wick,
      timestamp: item.timestamp,
      synthetic: true,
    };
  });
}

function drawProjection(svg, historyInput, projectedInput, features = {}, options = {}) {
  if (!svg) return;
  const historySeries = normalizeHistorySeries(historyInput, options.range || "1M");
  if (!historySeries?.length) {
    svg.innerHTML = `<text x="50%" y="52%" text-anchor="middle" fill="rgba(255,255,255,0.45)" font-size="14">No chart data</text>`;
    return;
  }
  let projectedSeries = buildProjectedSeries(historySeries, projectedInput, options.range || "1M");
  if (!projectedSeries?.length) {
    projectedSeries = [{ value: historySeries[historySeries.length - 1].value, timestamp: historySeries[historySeries.length - 1].timestamp }];
  }
  const chartSignature = JSON.stringify({
    range: options.range || "1M",
    currency: options.currency || "USD",
    features,
    historyLength: historySeries.length,
    first: historySeries[0],
    last: historySeries[historySeries.length - 1],
    projected: projectedSeries,
  });
  if (svg.dataset.chartSignature === chartSignature) return;
  const shouldAnimate = options.animate !== false && svg.dataset.chartReady !== "1";
  svg.dataset.chartSignature = chartSignature;
  const width = 640;
  const height = 240;
  const margin = { top: 12, right: 12, bottom: 34, left: 56 };
  const chartType = features.chartType || "line";
  const candles = chartType === "candles" ? buildSyntheticCandles(historySeries) : [];
  const candleScaleValues = candles.flatMap((candle) => [candle.high, candle.low]);
  const values = [...historySeries.map((item) => item.value), ...projectedSeries.map((item) => item.value), ...candleScaleValues];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const toPoint = (value, index, total) => {
    const x = margin.left + ((index / (total - 1 || 1)) * (width - margin.left - margin.right));
    const y = height - margin.bottom - (((value - min) / range) * (height - margin.top - margin.bottom));
    return `${x},${y}`;
  };

  const historyValues = historySeries.map((item) => item.value);
  const projectedValues = projectedSeries.map((item) => item.value);
  const pointTotal = historyValues.length + projectedValues.length;
  const historicalPoints = historyValues.map((value, index) => toPoint(value, index, pointTotal)).join(" ");
  const projectedPoints = projectedValues
    .map((value, index) => toPoint(value, historyValues.length + index, pointTotal))
    .join(" ");
  const candleWidth = clamp((width - margin.left - margin.right) / Math.max(historySeries.length, 1) * 0.58, 3, 15);

  const overlays = [];
  const drawSeries = (series, stroke, dash = "", width = 2, opacity = 0.8) => {
    const points = series
      .map((value, index) => (Number.isFinite(value) ? toPoint(value, index, pointTotal) : ""))
      .filter(Boolean)
      .join(" ");
    if (!points) return;
    overlays.push(
      `<polyline fill="none" stroke="${stroke}" stroke-width="${width}" ${dash ? `stroke-dasharray="${dash}"` : ""} opacity="${opacity}" points="${points}" stroke-linecap="round"></polyline>`,
    );
  };

  if (features.sma20) {
    drawSeries(movingAverage(historyValues, 20), "rgba(93,214,255,0.8)", "6 5", 2);
  }
  if (features.sma50) {
    drawSeries(movingAverage(historyValues, 50), "rgba(255,176,0,0.75)", "10 6", 2);
  }
  if (features.bands) {
    const avg = movingAverage(historyValues, 20);
    const std = rollingStd(historyValues, 20);
    drawSeries(avg.map((value, index) => (value !== null && std[index] !== null ? value + (std[index] * 2) : null)), "rgba(255,255,255,0.35)", "4 4", 1.5, 0.7);
    drawSeries(avg.map((value, index) => (value !== null && std[index] !== null ? value - (std[index] * 2) : null)), "rgba(255,255,255,0.35)", "4 4", 1.5, 0.7);
  }

  const yTicks = Array.from({ length: 4 }, (_, index) => {
    const ratio = index / 3;
    const value = max - (range * ratio);
    const y = margin.top + ((height - margin.top - margin.bottom) * ratio);
    return { y, value };
  });
  const xTickCount = Math.min(5, historySeries.length);
  const xTickIndices = Array.from(new Set(
    Array.from({ length: xTickCount }, (_, i) => Math.round(i * (historySeries.length - 1) / Math.max(xTickCount - 1, 1)))
  )).filter((index) => index >= 0 && index < historySeries.length);
  const xTicks = xTickIndices.map((index) => ({
    x: margin.left + ((index / (pointTotal - 1 || 1)) * (width - margin.left - margin.right)),
    label: formatAxisDate(historySeries[index]?.timestamp, options.range || "1M", options),
  }));

  const hoverPoints = historySeries.map((item, index) => {
    const [x, y] = toPoint(item.value, index, pointTotal).split(",");
    return {
      x: Number(x),
      y: Number(y),
      value: item.value,
      timestamp: item.timestamp,
    };
  });
  const hoverOverlayId = options.overlayId || "";
  const candleLayer = candles.map((candle, index) => {
    const x = margin.left + ((index / (pointTotal - 1 || 1)) * (width - margin.left - margin.right));
    const [openY, closeY, highY, lowY] = [candle.open, candle.close, candle.high, candle.low].map((value) => {
      const [, y] = toPoint(value, index, pointTotal).split(",");
      return Number(y);
    });
    const up = candle.close >= candle.open;
    const bodyY = Math.min(openY, closeY);
    const bodyHeight = Math.max(2, Math.abs(closeY - openY));
    const color = up ? "rgba(63,224,142,0.88)" : "rgba(255,107,107,0.88)";
    return `
      <line x1="${x}" y1="${highY}" x2="${x}" y2="${lowY}" stroke="${color}" stroke-width="1.4" opacity="0.82"></line>
      <rect x="${x - candleWidth / 2}" y="${bodyY}" width="${candleWidth}" height="${bodyHeight}" rx="2" fill="${color}" opacity="0.72"></rect>
    `;
  }).join("");
  const barLayer = chartType === "bars" ? historyValues.map((value, index) => {
    const [x, y] = toPoint(value, index, pointTotal).split(",").map(Number);
    return `<line x1="${x}" y1="${height - margin.bottom}" x2="${x}" y2="${y}" stroke="rgba(84,210,255,0.58)" stroke-width="${Math.max(2, candleWidth * 0.72)}" stroke-linecap="round"></line>`;
  }).join("") : "";
  const areaLayer = chartType === "area"
    ? `<polygon points="${margin.left},${height - margin.bottom} ${historicalPoints} ${margin.left + (((historyValues.length - 1) / (pointTotal - 1 || 1)) * (width - margin.left - margin.right))},${height - margin.bottom}" fill="url(#chart-area-fill)" opacity="0.8"></polygon>`
    : "";
  const lineLayer = chartType === "candles" || chartType === "bars"
    ? `<polyline fill="none" stroke="rgba(84,210,255,0.34)" stroke-width="2" points="${historicalPoints}" stroke-linecap="round"></polyline>`
    : `<polyline fill="none" stroke="#54d2ff" stroke-width="3.5" points="${historicalPoints}" stroke-linecap="round"></polyline>`;

  svg.innerHTML = `
    <defs>
      <linearGradient id="chart-area-fill" x1="0%" x2="0%" y1="0%" y2="100%">
        <stop offset="0%" stop-color="rgba(84,210,255,0.28)" />
        <stop offset="100%" stop-color="rgba(84,210,255,0.02)" />
      </linearGradient>
    </defs>
    ${yTicks.map((tick) => `<line x1="${margin.left}" y1="${tick.y}" x2="${width - margin.right}" y2="${tick.y}" stroke="rgba(255,255,255,0.08)"></line>`).join("")}
    ${yTicks.map((tick) => `<text x="${margin.left - 8}" y="${tick.y + 4}" text-anchor="end" fill="rgba(255,255,255,0.55)" font-size="11">${formatCurrency(tick.value, options.currency || "USD")}</text>`).join("")}
    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(255,255,255,0.12)"></line>
    <line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(255,255,255,0.12)"></line>
    ${xTicks.map((tick) => `<text x="${tick.x}" y="${height - 10}" text-anchor="middle" fill="rgba(255,255,255,0.55)" font-size="11">${tick.label}</text>`).join("")}
    ${areaLayer}
    ${barLayer}
    ${candleLayer}
    ${lineLayer}
    ${overlays.join("")}
    <polyline fill="none" stroke="#f3b85f" stroke-width="3.5" stroke-dasharray="8 8" points="${projectedPoints}" stroke-linecap="round"></polyline>
    <g id="chart-hover-layer">
      <line id="chart-hover-line" x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(243,184,95,0.7)" stroke-width="1.5" stroke-dasharray="5 5" opacity="0"></line>
      <circle id="chart-hover-point" cx="${margin.left}" cy="${margin.top}" r="4.5" fill="#f3b85f" stroke="#131313" stroke-width="2" opacity="0"></circle>
    </g>
  `;
  if (shouldAnimate) {
    animateSvgRefresh(svg, { force: true });
  }
  svg.dataset.chartReady = "1";

  const hoverLine = svg.querySelector("#chart-hover-line");
  const hoverPoint = svg.querySelector("#chart-hover-point");
  const hoverCard = hoverOverlayId ? document.getElementById(hoverOverlayId) : null;
  if (hoverCard && !hoverCard.querySelector("[data-hover-price]")) {
    hoverCard.innerHTML = `<strong data-hover-price></strong><span data-hover-date></span>`;
  }
  const updateHover = (event) => {
    if (!hoverPoints.length || !hoverLine || !hoverPoint || !hoverCard) return;
    const rect = svg.getBoundingClientRect();
    const relativeX = ((event.clientX - rect.left) / rect.width) * width;
    let nearestIndex = 0;
    for (let index = 1; index < hoverPoints.length; index += 1) {
      if (Math.abs(hoverPoints[index].x - relativeX) < Math.abs(hoverPoints[nearestIndex].x - relativeX)) {
        nearestIndex = index;
      }
    }
    const nearest = hoverPoints[nearestIndex];
    setAttributeIfChanged(hoverLine, "x1", nearest.x);
    setAttributeIfChanged(hoverLine, "x2", nearest.x);
    setAttributeIfChanged(hoverLine, "opacity", "1");
    setAttributeIfChanged(hoverPoint, "cx", nearest.x);
    setAttributeIfChanged(hoverPoint, "cy", nearest.y);
    setAttributeIfChanged(hoverPoint, "opacity", "1");
    hoverCard.hidden = false;
    if (hoverCard.dataset.hoverIndex !== String(nearestIndex)) {
      hoverCard.dataset.hoverIndex = String(nearestIndex);
      setTextIfChanged(hoverCard.querySelector("[data-hover-price]"), formatCurrency(nearest.value, options.currency || "USD"));
      setTextIfChanged(hoverCard.querySelector("[data-hover-date]"), formatTooltipDate(nearest.timestamp, options.range || "1M", options));
    }
    const leftPercent = Math.max(8, Math.min(78, (nearest.x / width) * 100));
    hoverCard.style.left = `${leftPercent}%`;
    hoverCard.style.top = `${Math.max(10, ((nearest.y / height) * 100) - 12)}%`;
  };
  svg.onmousemove = (event) => {
    state.chartHoverEvent = event;
    if (state.chartHoverFrame) return;
    state.chartHoverFrame = window.requestAnimationFrame(() => {
      state.chartHoverFrame = null;
      updateHover(state.chartHoverEvent);
    });
  };
  svg.onmouseleave = () => {
    if (state.chartHoverFrame) {
      window.cancelAnimationFrame(state.chartHoverFrame);
      state.chartHoverFrame = null;
    }
    state.chartHoverEvent = null;
    if (hoverLine) setAttributeIfChanged(hoverLine, "opacity", "0");
    if (hoverPoint) setAttributeIfChanged(hoverPoint, "opacity", "0");
    if (hoverCard) {
      hoverCard.hidden = true;
      delete hoverCard.dataset.hoverIndex;
    }
  };
}

function drawTimeline(svg, history, projected, features = {}, options = {}) {
  drawProjection(svg, history, projected, features, options);
}

function drawMethodologyFlow(svg, flow = {}) {
  if (!svg) return;
  const nodes = flow.nodes || [];
  const edges = flow.edges || [];
  if (!nodes.length) {
    svg.innerHTML = "";
    return;
  }
  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  svg.innerHTML = `
    <defs>
      <linearGradient id="method-flow-line" x1="0%" x2="100%" y1="0%" y2="0%">
        <stop offset="0%" stop-color="rgba(84,210,255,0.48)" />
        <stop offset="100%" stop-color="rgba(255,176,0,0.64)" />
      </linearGradient>
      <filter id="method-flow-glow"><feGaussianBlur stdDeviation="2.4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
    ${edges
      .map((edge, index) => {
        const source = nodeMap.get(edge.source);
        const target = nodeMap.get(edge.target);
        if (!source || !target) return "";
        const d = `M ${source.x + 88} ${source.y + 34} C ${source.x + 146} ${source.y + 34}, ${target.x - 38} ${target.y + 34}, ${target.x} ${target.y + 34}`;
        return `
          <path d="${d}" fill="none" stroke="url(#method-flow-line)" stroke-width="3.2" stroke-linecap="round" opacity="0.68" />
          <path d="${d}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8" stroke-linecap="round" />
          <circle r="4.2" fill="#f3b85f" filter="url(#method-flow-glow)">
            <animateMotion dur="${4.8 + (index * 0.8)}s" repeatCount="indefinite" path="${d}" />
          </circle>
          <text x="${(source.x + target.x) / 2}" y="${Math.min(source.y, target.y) + 18}" text-anchor="middle" fill="rgba(223,214,194,0.62)" font-size="10" font-family="Azeret Mono, monospace">${edge.label || ""}</text>
        `;
      })
      .join("")}
    ${nodes
      .map(
        (node) => `
          <g transform="translate(${node.x}, ${node.y})">
            <rect width="176" height="68" rx="20" fill="rgba(12,12,12,0.86)" stroke="rgba(255,176,0,0.14)" />
            <text x="18" y="24" fill="rgba(255,176,0,0.78)" font-size="10" font-family="Azeret Mono, monospace">FLOW</text>
            <text x="18" y="42" fill="#fff1cc" font-size="14" font-family="Sora, sans-serif">${node.label}</text>
            <text x="18" y="58" fill="rgba(224,214,193,0.7)" font-size="10.5" font-family="Manrope, sans-serif">${splitImpactLabel(node.summary || "", 30, 1)[0]}</text>
          </g>
        `,
      )
      .join("")}
  `;
  animateSvgRefresh(svg);
}

function renderMethodology() {
  const methodology = state.dashboard?.methodology;
  const headlineNode = document.getElementById("methodology-headline");
  const cockpitNode = document.getElementById("methodology-cockpit");
  const principlesNode = document.getElementById("methodology-principles");
  const inputsNode = document.getElementById("methodology-live-inputs");
  const conceptsNode = document.getElementById("methodology-concepts");
  const signalMapNode = document.getElementById("methodology-signal-map");
  const formulasNode = document.getElementById("methodology-formulas");
  const flowNode = document.getElementById("methodology-flowchart");
  if (!headlineNode || !cockpitNode || !principlesNode || !inputsNode || !conceptsNode || !signalMapNode || !formulasNode || !flowNode) return;
  if (!methodology) {
    headlineNode.textContent = "Methodology is loading.";
    cockpitNode.innerHTML = "";
    principlesNode.innerHTML = "";
    inputsNode.innerHTML = "";
    conceptsNode.innerHTML = "";
    signalMapNode.innerHTML = "";
    formulasNode.innerHTML = "";
    drawMethodologyFlow(flowNode, { nodes: [], edges: [] });
    return;
  }
  const cockpit = methodology.cockpit || {};
  headlineNode.textContent = methodology.headline || "Methodology is ready.";
  cockpitNode.innerHTML = cockpit.stance ? `
    <div class="methodology-cockpit-hero">
      <div>
        <span>Current operating model</span>
        <strong>${cockpit.stance}</strong>
        <p>${cockpit.summary || "Inputs are transformed into scenario support with risks and unknowns kept visible."}</p>
      </div>
      <div class="methodology-cockpit-score">
        <b>${Number(cockpit.edgeScore || 0).toFixed(0)}</b>
        <small>edge score</small>
        <em>${cockpit.riskLevel || "Monitoring"} risk</em>
      </div>
    </div>
    <div class="methodology-rule-grid">
      ${(cockpit.rules || []).map((item) => `
        <div class="methodology-rule-card decision-cockpit-card">
          <span>${item.label}</span>
          <strong>${item.value}</strong>
          <p>${item.note}</p>
        </div>
      `).join("")}
    </div>
  ` : "";
  principlesNode.innerHTML = (methodology.principles || [])
    .map(
      (item) => `
        <div class="methodology-principle-pill">${item}</div>
      `,
    )
    .join("");
  inputsNode.innerHTML = (methodology.liveInputs || [])
    .map(
      (item) => `
        <div class="metric-card methodology-input-card">
          <span>${item.label}</span>
          <strong>${item.value || "Monitoring"}</strong>
          <p>${item.impactPath || item.useWhere || "Feeds the scenario engine."}</p>
          <small>${item.cadence}${item.significance ? ` • ${item.significance}` : ""}</small>
        </div>
      `,
    )
    .join("");
  conceptsNode.innerHTML = (methodology.concepts || [])
    .map(
      (item) => `
        <div class="research-card methodology-card">
          <div class="methodology-card-header">
            <div>
              <span class="methodology-card-family">${item.family}</span>
              <strong>${item.label}</strong>
            </div>
            ${item.liveValue ? `<span class="methodology-card-live">${item.liveValue}</span>` : ""}
          </div>
          <code>${item.formula}</code>
          <p>${item.whyItMatters || item.impactPath}</p>
          <div class="methodology-card-meta">
            ${item.useWhere ? `<span>${item.useWhere}</span>` : ""}
            ${item.cadence ? `<span>${item.cadence}</span>` : ""}
            ${item.phase ? `<span>${item.phase}</span>` : ""}
          </div>
          ${item.url ? `<a class="methodology-card-source" href="${item.url}" target="_blank" rel="noreferrer noopener">↗ ${item.sourceTitle || "Source"}</a>` : (item.sourceTitle ? `<small class="methodology-card-source-text">${item.sourceTitle}</small>` : "")}
        </div>
      `,
    )
    .join("");
  signalMapNode.innerHTML = `
    <div class="methodology-signal-grid">
      ${(methodology.signalLayers || []).map((item) => `
        <article>
          <span>${item.layer}</span>
          <strong>${item.signal}</strong>
          <p>${item.explanation}</p>
          <small>${item.guardrail}</small>
        </article>
      `).join("")}
    </div>
  `;
  formulasNode.innerHTML = `
    ${(methodology.explainers || []).map((item) => `
      <article class="methodology-formula-card">
        <div>
          <span>${item.label}</span>
          <strong>${item.title}</strong>
        </div>
        <code>${item.formula}</code>
        <p>${item.interpretation}</p>
      </article>
    `).join("")}
  `;
  drawMethodologyFlow(flowNode, methodology.flow || {});
  renderMethodologySignalCharts();
  renderMethodologyPapers(methodology.tradingPapers || []);
}

// ── Signal Pattern Library ─────────────────────────────────────────────────
// Purely educational SVG illustrations. Actual thresholds stay in gitignored
// data/factors/prediction_formulas.json and vault/.
const SIGNAL_PATTERNS = [
  {
    id: "rsi",
    family: "Momentum",
    badge: "badge-momentum",
    kicker: "Oscillator · Overbought / Oversold",
    title: "Relative Strength Index (RSI)",
    formula: "RSI = 100 − 100 / (1 + RS)\nRS = Avg Gain₁₄ / Avg Loss₁₄",
    description: "Measures the speed and magnitude of recent price changes on a 0–100 scale. Readings above the upper zone signal exhausted buying; readings below the lower zone signal exhausted selling. Divergences from price are often more predictive than the level itself.",
    cadence: "Intraday / Daily",
    phase: "Trend confirmation",
    paper: "Wilder, 1978",
    drawChart(w, h) {
      // Price line (top half) + RSI indicator (bottom half)
      const pts = [18,14,22,20,28,18,35,24,44,30,56,38,62,42,70,48,78,52,84,55,90,51,96,46,102,40,108,34,114,28,118,22,122,18,126,16,130,18,136,22,142,28,148,34,154,40,160,46,166,52,172,56,176,58];
      const priceH = h * 0.42;
      const rsiH = h * 0.42;
      const rsiY = h * 0.56;
      const px = (i) => (i / 176) * w;
      const py = (v) => priceH - (v / 60) * priceH + 4;
      const rsiVals = [42,46,52,55,60,66,71,76,80,82,79,74,68,62,55,48,40,34,28,25,28,33,40,46,52];
      const rx = (i) => (i / (rsiVals.length - 1)) * w;
      const ry = (v) => rsiY + rsiH - ((v / 100) * rsiH);
      const priceD = pts.reduce((acc, v, i) => i % 2 === 0 ? acc + (acc ? " L" : "M") + px(v) : acc + "," + py(v), "");
      const rsiD = rsiVals.map((v, i) => (i === 0 ? "M" : "L") + rx(i) + "," + ry(v)).join(" ");
      const ob = ry(70); const os = ry(30);
      return `
        <rect width="${w}" height="${h}" rx="8" fill="rgba(0,0,0,0.18)"/>
        <!-- OB zone -->
        <rect x="0" y="${rsiY}" width="${w}" height="${ob - rsiY}" fill="rgba(255,107,107,0.07)"/>
        <!-- OS zone -->
        <rect x="0" y="${os}" width="${w}" height="${rsiY + rsiH - os}" fill="rgba(63,224,142,0.07)"/>
        <!-- Price area -->
        <path d="${priceD}" fill="none" stroke="rgba(255,176,0,0.55)" stroke-width="1.6"/>
        <!-- Divider -->
        <line x1="0" y1="${h*0.52}" x2="${w}" y2="${h*0.52}" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
        <!-- RSI line -->
        <path d="${rsiD}" fill="none" stroke="#7dd6ff" stroke-width="1.8"/>
        <!-- OB/OS labels -->
        <text x="${w-28}" y="${ob - 3}" fill="rgba(255,107,107,0.72)" font-size="8" font-family="Azeret Mono,monospace">OB</text>
        <text x="${w-28}" y="${os + 10}" fill="rgba(63,224,142,0.72)" font-size="8" font-family="Azeret Mono,monospace">OS</text>
        <!-- OB/OS lines -->
        <line x1="0" y1="${ob}" x2="${w}" y2="${ob}" stroke="rgba(255,107,107,0.22)" stroke-width="1" stroke-dasharray="4,3"/>
        <line x1="0" y1="${os}" x2="${w}" y2="${os}" stroke="rgba(63,224,142,0.22)" stroke-width="1" stroke-dasharray="4,3"/>
        <text x="6" y="14" fill="rgba(255,176,0,0.55)" font-size="8" font-family="Azeret Mono,monospace">PRICE</text>
        <text x="6" y="${rsiY + 12}" fill="rgba(125,214,255,0.6)" font-size="8" font-family="Azeret Mono,monospace">RSI</text>
      `;
    },
  },
  {
    id: "macd",
    family: "Momentum",
    badge: "badge-momentum",
    kicker: "Trend · Signal Line Crossover",
    title: "MACD — Moving Avg Convergence/Divergence",
    formula: "MACD = EMA₁₂ − EMA₂₆\nSignal = EMA₉(MACD)  |  Histogram = MACD − Signal",
    description: "Tracks the gap between two exponential moving averages. When the MACD line crosses above the signal line, trend momentum is shifting up — the histogram turns positive. Histogram shrinkage before the cross often gives early warning.",
    cadence: "Daily / Intraday",
    phase: "Trend + momentum",
    paper: "Appel, 1979",
    drawChart(w, h) {
      const macdVals = [-6,-5,-3,-1,0,2,4,5,6,5,4,2,0,-1,-3,-5,-4,-2,0,2,4,6,7,6,4];
      const sigVals  = [-5,-5,-4,-3,-2,-1,1,2,4,5,4,3,2,1,-1,-2,-3,-2,0,1,3,4,6,6,5];
      const n = macdVals.length;
      const cx = (i) => (i / (n-1)) * w;
      const cy = (v) => h/2 - (v / 8) * (h * 0.38);
      const macdD = macdVals.map((v,i) => (i===0?"M":"L") + cx(i)+","+cy(v)).join(" ");
      const sigD  = sigVals.map((v,i) => (i===0?"M":"L") + cx(i)+","+cy(v)).join(" ");
      const bars = macdVals.map((v,i) => {
        const diff = v - sigVals[i];
        const barH = Math.abs(diff / 8) * (h * 0.36);
        const col = diff >= 0 ? "rgba(63,224,142,0.5)" : "rgba(255,107,107,0.5)";
        const barW = Math.max(4, w/n - 3);
        return `<rect x="${cx(i) - barW/2}" y="${diff>=0 ? h/2-barH : h/2}" width="${barW}" height="${barH}" fill="${col}" rx="2"/>`;
      }).join("");
      return `
        <rect width="${w}" height="${h}" rx="8" fill="rgba(0,0,0,0.18)"/>
        <line x1="0" y1="${h/2}" x2="${w}" y2="${h/2}" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
        ${bars}
        <path d="${macdD}" fill="none" stroke="rgba(255,176,0,0.8)" stroke-width="1.8"/>
        <path d="${sigD}"  fill="none" stroke="#ff8fa3" stroke-width="1.4" stroke-dasharray="5,3"/>
        <text x="6" y="13" fill="rgba(255,176,0,0.6)" font-size="8" font-family="Azeret Mono,monospace">MACD</text>
        <text x="${w*0.42}" y="13" fill="rgba(255,143,163,0.6)" font-size="8" font-family="Azeret Mono,monospace">SIGNAL</text>
        <text x="${w*0.72}" y="13" fill="rgba(63,224,142,0.6)" font-size="8" font-family="Azeret Mono,monospace">HIST</text>
      `;
    },
  },
  {
    id: "bollinger",
    family: "Volatility",
    badge: "badge-volatility",
    kicker: "Volatility · Band Squeeze / Expansion",
    title: "Bollinger Bands",
    formula: "Upper = SMA₂₀ + 2σ\nLower = SMA₂₀ − 2σ\nBandwidth = (Upper − Lower) / SMA",
    description: "Envelopes price at a standard deviation distance from a moving average. A squeeze (bands converging) signals compressed volatility before a potential breakout. Price tagging the upper band is not a sell signal — it means strong trend, not exhaustion.",
    cadence: "Intraday / Daily",
    phase: "Volatility state",
    paper: "Bollinger, 1983",
    drawChart(w, h) {
      const mid = [30,32,33,34,35,36,37,38,38,39,40,41,42,44,46,47,48,49,50,51,52,54,56,58,60];
      const n = mid.length;
      const bw = (i) => i < 10 ? 12 - i*0.8 : i < 14 ? 4 + (i-10)*0.5 : 6 + (i-14)*2;
      const scale = (v) => h - (v / 75) * h * 0.88 + h * 0.06;
      const cx = (i) => (i / (n-1)) * w;
      const upperD = mid.map((v,i) => (i===0?"M":"L") + cx(i)+","+scale(v+bw(i))).join(" ");
      const lowerD = mid.map((v,i) => (i===0?"M":"L") + cx(i)+","+scale(v-bw(i))).join(" ");
      const midD   = mid.map((v,i) => (i===0?"M":"L") + cx(i)+","+scale(v)).join(" ");
      // band fill
      const bandFill = upperD + " " + mid.map((v,i) => (i===0?"L":"L") + cx(n-1-i)+","+scale(mid[n-1-i]-bw(n-1-i))).join(" ") + " Z";
      // price (hugs upper then crosses lower)
      const price = [31,33,34,36,38,40,43,46,50,53,54,52,50,47,44,42,40,39,38,38,40,44,52,60,66];
      const priceD = price.map((v,i) => (i===0?"M":"L") + cx(i)+","+scale(v)).join(" ");
      return `
        <rect width="${w}" height="${h}" rx="8" fill="rgba(0,0,0,0.18)"/>
        <path d="${bandFill}" fill="rgba(88,214,255,0.05)"/>
        <path d="${upperD}" fill="none" stroke="rgba(88,214,255,0.4)" stroke-width="1.2" stroke-dasharray="4,3"/>
        <path d="${lowerD}" fill="none" stroke="rgba(88,214,255,0.4)" stroke-width="1.2" stroke-dasharray="4,3"/>
        <path d="${midD}"   fill="none" stroke="rgba(88,214,255,0.2)" stroke-width="1"/>
        <path d="${priceD}" fill="none" stroke="rgba(255,220,130,0.85)" stroke-width="1.8"/>
        <text x="6" y="13" fill="rgba(88,214,255,0.6)" font-size="8" font-family="Azeret Mono,monospace">BB ±2σ</text>
        <text x="${w*0.55}" y="13" fill="rgba(255,220,130,0.6)" font-size="8" font-family="Azeret Mono,monospace">PRICE</text>
        <!-- squeeze annotation -->
        <rect x="${w*0.3}" y="${h*0.04}" width="${w*0.18}" height="${h*0.92}" fill="rgba(200,180,255,0.04)" rx="4"/>
        <text x="${w*0.31}" y="${h-5}" fill="rgba(200,180,255,0.55)" font-size="7.5" font-family="Azeret Mono,monospace">SQUEEZE</text>
      `;
    },
  },
  {
    id: "zscore",
    family: "Mean Reversion",
    badge: "badge-reversion",
    kicker: "Statistical · Deviation from Mean",
    title: "Z-Score Mean Reversion",
    formula: "Z = (Pₜ − MA₂₀) / σ₂₀\nReversion signal when |Z| > threshold",
    description: "Measures how far current price sits from its rolling mean in standard deviation units. High positive Z = stretched above mean, likely to revert. Pairs with a trend filter — reversion trades against trend carry higher failure rate in strong momentum regimes.",
    cadence: "Intraday / Daily",
    phase: "Entry timing",
    paper: "Lo & MacKinlay, 1988",
    drawChart(w, h) {
      const zVals = [0.2,0.5,0.9,1.4,1.9,2.2,1.8,1.2,0.6,0.1,-0.3,-0.7,-1.1,-1.8,-2.1,-1.6,-1.0,-0.4,0.2,0.7,1.1,1.5,1.2,0.7,0.2];
      const n = zVals.length;
      const cx = (i) => (i / (n-1)) * w;
      const cy = (v) => h/2 - (v/2.5) * (h*0.4);
      const zD = zVals.map((v,i) => (i===0?"M":"L") + cx(i)+","+cy(v)).join(" ");
      const ob = cy(1.8); const os = cy(-1.8);
      return `
        <rect width="${w}" height="${h}" rx="8" fill="rgba(0,0,0,0.18)"/>
        <rect x="0" y="${h*0.06}" width="${w}" height="${ob - h*0.06}" fill="rgba(255,107,107,0.06)"/>
        <rect x="0" y="${os}" width="${w}" height="${h*0.94 - os}" fill="rgba(63,224,142,0.06)"/>
        <line x1="0" y1="${h/2}" x2="${w}" y2="${h/2}" stroke="rgba(255,255,255,0.09)" stroke-width="1"/>
        <line x1="0" y1="${ob}"  x2="${w}" y2="${ob}"  stroke="rgba(255,107,107,0.22)" stroke-dasharray="4,3" stroke-width="1"/>
        <line x1="0" y1="${os}"  x2="${w}" y2="${os}"  stroke="rgba(63,224,142,0.22)"  stroke-dasharray="4,3" stroke-width="1"/>
        <path d="${zD}" fill="none" stroke="#ff8fa3" stroke-width="1.8"/>
        <text x="6" y="13" fill="rgba(255,143,163,0.6)" font-size="8" font-family="Azeret Mono,monospace">Z-SCORE</text>
        <text x="${w-42}" y="${ob-3}" fill="rgba(255,107,107,0.65)" font-size="7.5" font-family="Azeret Mono,monospace">+1.8σ</text>
        <text x="${w-42}" y="${os+10}" fill="rgba(63,224,142,0.65)" font-size="7.5" font-family="Azeret Mono,monospace">−1.8σ</text>
        <text x="6" y="${h/2+10}" fill="rgba(255,255,255,0.2)" font-size="7.5" font-family="Azeret Mono,monospace">0</text>
      `;
    },
  },
  {
    id: "yieldcurve",
    family: "Macro",
    badge: "badge-macro",
    kicker: "Rates · Curve Shape Signal",
    title: "Yield Curve 2s10s Spread",
    formula: "Spread = Y₁₀ − Y₂\nInversion: Spread < 0\nSteepening: ΔSpread > 0",
    description: "The gap between 10-year and 2-year treasury yields is the most-watched leading indicator for credit conditions and recession probability. Inversion (negative spread) has preceded every US recession since 1955. Steepening after inversion is often the confirmation phase.",
    cadence: "Daily / Intraday",
    phase: "Macro regime",
    paper: "Estrella & Mishkin, 1996",
    drawChart(w, h) {
      const spread = [1.6,1.4,1.1,0.8,0.5,0.2,-0.1,-0.3,-0.5,-0.6,-0.4,-0.2,0.1,0.3,0.6,0.9,1.1,1.3,1.2,1.0,0.8,0.7,0.6,0.5,0.7];
      const n = spread.length;
      const cx = (i) => (i/(n-1))*w;
      const cy = (v) => h*0.45 - (v/1.8)*(h*0.38);
      const zero = cy(0);
      const spreadD = spread.map((v,i) => (i===0?"M":"L")+cx(i)+","+cy(v)).join(" ");
      const areaAbove = spread.map((v,i) => (i===0?"M":"L")+cx(i)+","+cy(Math.max(0,v))).join(" ")
        + ` L${w},${zero} L0,${zero} Z`;
      const areaBelow = spread.map((v,i) => (i===0?"M":"L")+cx(i)+","+cy(Math.min(0,v))).join(" ")
        + ` L${w},${zero} L0,${zero} Z`;
      return `
        <rect width="${w}" height="${h}" rx="8" fill="rgba(0,0,0,0.18)"/>
        <path d="${areaAbove}" fill="rgba(63,224,142,0.08)"/>
        <path d="${areaBelow}" fill="rgba(255,107,107,0.1)"/>
        <line x1="0" y1="${zero}" x2="${w}" y2="${zero}" stroke="rgba(255,255,255,0.14)" stroke-width="1"/>
        <path d="${spreadD}" fill="none" stroke="rgba(200,180,255,0.9)" stroke-width="2"/>
        <text x="6" y="13" fill="rgba(200,180,255,0.6)" font-size="8" font-family="Azeret Mono,monospace">2s10s SPREAD</text>
        <text x="${w*0.28}" y="${h-6}" fill="rgba(255,107,107,0.6)" font-size="7.5" font-family="Azeret Mono,monospace">INVERTED</text>
        <text x="${w*0.62}" y="13" fill="rgba(63,224,142,0.6)" font-size="7.5" font-family="Azeret Mono,monospace">NORMAL</text>
      `;
    },
  },
  {
    id: "momentum",
    family: "Momentum",
    badge: "badge-momentum",
    kicker: "Price · Rate of Change + Participation",
    title: "Trend + Volume Participation",
    formula: "Score = 0.45·MOM₅ + 0.35·MOM₂₀ + 0.20·log(VR)\nVR = Volume / Avg Volume₂₀",
    description: "Combines short- and medium-term momentum with volume participation. A large price move on thin volume is down-weighted — markets are more likely to sustain a move when breadth and participation confirm it. The log transform keeps the volume term from dominating.",
    cadence: "Intraday",
    phase: "Trend confirmation",
    paper: "Jegadeesh & Titman, 1993",
    drawChart(w, h) {
      const price = [38,39,40,39,40,42,44,46,48,50,51,52,51,50,49,51,54,57,61,65,68,70,72,73,74];
      const vols  = [20,22,18,25,30,35,28,40,45,50,30,25,22,28,20,35,55,65,70,80,60,50,42,35,30];
      const n = price.length;
      const cx = (i) => (i/(n-1))*w;
      const py = (v) => h*0.56 - ((v-36)/42)*(h*0.5);
      const vy = (v) => h - (v/90)*(h*0.34);
      const priceD = price.map((v,i)=>(i===0?"M":"L")+cx(i)+","+py(v)).join(" ");
      const bars = vols.map((v,i) => {
        const strong = v > 45;
        return `<rect x="${cx(i)-w/n/2+1}" y="${vy(v)}" width="${w/n-2}" height="${h-vy(v)}" fill="${strong?"rgba(255,176,0,0.45)":"rgba(255,176,0,0.18)"}" rx="2"/>`;
      }).join("");
      return `
        <rect width="${w}" height="${h}" rx="8" fill="rgba(0,0,0,0.18)"/>
        ${bars}
        <line x1="0" y1="${h*0.6}" x2="${w}" y2="${h*0.6}" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
        <path d="${priceD}" fill="none" stroke="rgba(255,220,100,0.9)" stroke-width="2"/>
        <text x="6" y="13" fill="rgba(255,220,100,0.6)" font-size="8" font-family="Azeret Mono,monospace">PRICE + TREND</text>
        <text x="${w*0.55}" y="13" fill="rgba(255,176,0,0.55)" font-size="8" font-family="Azeret Mono,monospace">VOLUME</text>
      `;
    },
  },
];

function renderMethodologySignalCharts() {
  const node = document.getElementById("methodology-signal-charts");
  if (!node) return;
  node.innerHTML = `
    <div class="signal-private-note">
      <span class="signal-private-note-icon">🔒</span>
      <div>
        <strong>Educational patterns only</strong>
        <p>These diagrams show how each pattern family works conceptually. Actual detection thresholds, weights, and signal triggers for this dashboard are stored in gitignored local files and never uploaded.</p>
      </div>
    </div>
    <div class="methodology-signal-chart-grid">
      ${SIGNAL_PATTERNS.map((pat) => {
        const W = 360; const H = 120;
        return `
          <div class="signal-chart-card ${pat.id === "yieldcurve" ? "signal-neutral" : pat.id === "zscore" ? "signal-negative" : "signal-positive"}">
            <div class="signal-chart-head">
              <div class="signal-chart-head-text">
                <span class="signal-chart-kicker">${pat.kicker}</span>
                <span class="signal-chart-title">${pat.title}</span>
              </div>
              <span class="signal-chart-badge ${pat.badge}">${pat.family}</span>
            </div>
            <div class="signal-chart-canvas">
              <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
                ${pat.drawChart(W, H)}
              </svg>
            </div>
            <p class="signal-chart-desc">${pat.description}</p>
            <code class="signal-chart-formula">${pat.formula}</code>
            <div class="signal-chart-meta">
              <span>${pat.cadence}</span>
              <span>${pat.phase}</span>
              <span>Basis: ${pat.paper}</span>
            </div>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

// ── Academic Research Papers ───────────────────────────────────────────────
function renderMethodologyPapers(papers) {
  const node = document.getElementById("methodology-papers");
  if (!node) return;
  const list = papers.length ? papers : [];
  if (!list.length) {
    node.innerHTML = `<p class="micro-note">Research index loading.</p>`;
    return;
  }
  node.innerHTML = list.map((p) => `
    <div class="methodology-paper-card">
      <div class="methodology-paper-meta">
        <span class="methodology-paper-year">${p.year}</span>
        <span class="methodology-paper-type">${p.type}</span>
        <span class="methodology-paper-cadence">${p.updateCadence}</span>
      </div>
      <div class="methodology-paper-title">${p.title}</div>
      <p class="methodology-paper-why">${p.whyItMatters}</p>
      <div class="methodology-paper-factors">
        ${(p.factors || []).map((f) => `<span>${f}</span>`).join("")}
      </div>
      ${p.url ? `<a class="methodology-paper-link" href="${p.url}" target="_blank" rel="noreferrer noopener">↗ arxiv / doi</a>` : ""}
    </div>
  `).join("");
}

function buildImpactGraphElements(graph = {}) {
  const nodes = (graph.nodes || []).map((node) => ({
    data: {
      id: node.id,
      label: node.label,
      group: node.group || "entity",
      subtitle: node.subtitle || "",
      summary: node.summary || "",
      detail: node.detail || "",
      impact: node.impact || "",
      worthLabel: node.worthLabel || "",
      status: node.status || "",
      sourceUrl: node.sourceUrl || "",
      sourceLabel: node.sourceLabel || "",
      confidence: node.confidence || "",
      entityType: node.entityType || "",
      asOf: node.asOf || "",
    },
  }));
  const nodeIds = new Set(nodes.map((node) => node.data.id));
  const links = (graph.links || [])
    .filter((link) => nodeIds.has(link.source) && nodeIds.has(link.target))
    .map((link, index) => ({
    data: {
      id: `${link.source}->${link.target}->${index}`,
      source: link.source,
      target: link.target,
      relation: link.relation || "",
      direction: link.direction || "neutral",
      strength: Number(link.value || 1),
      worthLabel: link.worthLabel || "",
    },
  }));
  return nodes.concat(links);
}

function renderImpactGraphDetail(nodeData = null) {
  const detailNode = document.getElementById("impact-graph-detail");
  const legendNode = document.getElementById("impact-graph-legend");
  if (!detailNode || !legendNode) return;
  legendNode.innerHTML = `
    <span class="legend-pill macro">Macro</span>
    <span class="legend-pill market">Market</span>
    <span class="legend-pill stock">Stock</span>
    <span class="legend-pill project">Project</span>
    <span class="legend-pill entity">Entity</span>
  `;
  if (!nodeData) {
    detailNode.innerHTML = `<p>Pick a node to inspect its role, dependency path, and source context.</p>`;
    return;
  }
  detailNode.innerHTML = `
    <div class="impact-detail-card">
      <span>${String(nodeData.group || "entity").toUpperCase()}</span>
      <strong>${nodeData.label || "Node"}</strong>
      ${nodeData.subtitle ? `<small>${nodeData.subtitle}</small>` : ""}
      ${nodeData.summary ? `<p>${nodeData.summary}</p>` : ""}
      ${nodeData.detail ? `<p>${nodeData.detail}</p>` : ""}
      <div class="impact-detail-meta">
        ${nodeData.confidence ? `<span>${nodeData.confidence}</span>` : ""}
        ${nodeData.impact ? `<span>${nodeData.impact}</span>` : ""}
        ${nodeData.worthLabel ? `<span>${nodeData.worthLabel}</span>` : ""}
        ${nodeData.status ? `<span>${nodeData.status}</span>` : ""}
        ${nodeData.asOf ? `<span>${formatEventDateTime(nodeData.asOf)}</span>` : ""}
      </div>
      ${nodeData.sourceUrl ? `<a class="project-source-link" href="${nodeData.sourceUrl}" target="_blank" rel="noreferrer noopener">${nodeData.sourceLabel || "Source"}</a>` : ""}
    </div>
  `;
}

function renderImpactGraphWorkspace(graph = {}) {
  const container = document.getElementById("impact-graph");
  if (!container) return;
  const noteNode = document.getElementById("impact-graph-note");
  const panel = document.getElementById("watchlist-implications");
  const isVisible = panel?.classList.contains("active");
  if (!isVisible) {
    state.pendingImpactGraph = graph;
    return;
  }
  state.pendingImpactGraph = null;
  if (!window.cytoscape) {
    container.innerHTML = `<div class="impact-graph-fallback">Graph engine unavailable.</div>`;
    if (noteNode) noteNode.textContent = "Graph engine unavailable.";
    return;
  }
  const elements = buildImpactGraphElements(graph);
  if (!elements.length) {
    if (state.impactGraphCy) {
      state.impactGraphCy.destroy();
      state.impactGraphCy = null;
    }
    container.innerHTML = `<div class="impact-graph-fallback">No graph data for the current region.</div>`;
    renderImpactGraphDetail(null);
    if (noteNode) noteNode.textContent = "Graph source pending.";
    return;
  }
  container.querySelectorAll(".impact-graph-fallback").forEach((node) => node.remove());
  if (!state.impactGraphCy) container.innerHTML = "";
  if (!state.impactGraphCy) {
    state.impactGraphCy = window.cytoscape({
      container,
      elements,
      minZoom: 0.25,
      maxZoom: 3,
      boxSelectionEnabled: false,
      autoungrabify: false,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#101010",
            "border-width": 1.2,
            "border-color": "rgba(255,176,0,0.2)",
            label: "data(label)",
            color: "#fff1cf",
            "font-family": "Manrope",
            "font-size": 9.5,
            "text-wrap": "wrap",
            "text-max-width": 106,
            "text-valign": "center",
            "text-halign": "center",
            width: (ele) => (ele.data("group") === "project" ? 152 : ele.data("group") === "stock" ? 126 : 108),
            height: (ele) => (ele.data("group") === "project" ? 64 : ele.data("group") === "stock" ? 54 : 48),
            shape: (ele) => (ele.data("group") === "entity" ? "round-rectangle" : "round-hexagon"),
            "overlay-opacity": 0,
          },
        },
        { selector: 'node[group = "macro"]', style: { "background-color": "#2d2000", "border-color": "#f3b85f" } },
        { selector: 'node[group = "market"]', style: { "background-color": "#102437", "border-color": "#73d2ff" } },
        { selector: 'node[group = "stock"]', style: { "background-color": "#10271f", "border-color": "#7dffc4" } },
        { selector: 'node[group = "project"]', style: { "background-color": "#2b170d", "border-color": "#ff9c6a" } },
        { selector: 'node[group = "entity"]', style: { "background-color": "#1a1a1a", "border-color": "#bcb7a5" } },
        {
          selector: "edge",
          style: {
            width: (ele) => Math.max(1.8, Math.min(7, Number(ele.data("strength") || 1) * 1.5)),
            "line-color": (ele) => (ele.data("direction") === "positive" ? "#4dd889" : ele.data("direction") === "negative" ? "#ff6d6d" : "#f2c572"),
            "target-arrow-color": (ele) => (ele.data("direction") === "positive" ? "#4dd889" : ele.data("direction") === "negative" ? "#ff6d6d" : "#f2c572"),
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            opacity: 0.72,
            label: "data(relation)",
            color: "rgba(224,214,193,0.52)",
            "font-size": 7,
            "text-background-color": "#15120d",
            "text-background-opacity": 0.72,
            "text-background-padding": 2,
            "text-rotation": "autorotate",
          },
        },
        {
          selector: ":selected",
          style: {
            "border-width": 2.2,
            "border-color": "#fff0c8",
            "line-color": "#fff0c8",
            "target-arrow-color": "#fff0c8",
          },
        },
      ],
    });
    state.impactGraphCy.on("tap", "node", (event) => {
      renderImpactGraphDetail(event.target.data());
    });
  } else {
    state.impactGraphCy.elements().remove();
    state.impactGraphCy.add(elements);
  }
  relayoutImpactGraph();
  const firstNode = state.impactGraphCy.nodes()[0];
  renderImpactGraphDetail(firstNode ? firstNode.data() : null);
  if (noteNode) {
    const relationMeta = graph.relationMeta || {};
    const projectMeta = graph.projectMeta || {};
    const graphMeta = graph.graphMeta || {};
    const generatedAt = relationMeta.generatedAt ? new Date(relationMeta.generatedAt).toLocaleString() : "";
    const noteBits = [
      relationMeta.source || graphMeta.layout || "Dependency workspace",
      generatedAt,
      projectMeta.coverage ? `${projectMeta.coverage} project maps` : "",
      `${state.impactGraphCy.nodes().length} nodes`,
      `${state.impactGraphCy.edges().length} links`,
      "fit-all view, zoom for detail",
    ].filter(Boolean);
    noteNode.textContent = noteBits.join(" • ");
  }
}

function getImpactGraphGroupOrder(group) {
  const groupOrder = { macro: 0, market: 1, stock: 2, project: 3, entity: 4 };
  return groupOrder[group] ?? groupOrder.entity;
}

function buildImpactGraphPresetPositions(cy) {
  if (!cy) return {};
  const nodes = cy.nodes().toArray();
  const width = Math.max(cy.width() || 760, 760);
  const height = Math.max(cy.height() || 540, 540);
  const groups = ["macro", "market", "stock", "project", "entity"];
  const buckets = groups.reduce((acc, group) => ({ ...acc, [group]: [] }), {});
  nodes.forEach((node) => {
    const group = node.data("group") || "entity";
    (buckets[group] || buckets.entity).push(node);
  });

  const activeGroups = groups.filter((group) => buckets[group].length);
  const horizontalPad = activeGroups.length > 3 ? 96 : 132;
  const verticalPad = 78;
  const usableWidth = Math.max(width - horizontalPad * 2, 260);
  const columnGap = activeGroups.length > 1 ? usableWidth / (activeGroups.length - 1) : 0;
  const positions = {};

  activeGroups.forEach((group, groupIndex) => {
    const items = buckets[group].sort((a, b) => {
      const groupDelta = getImpactGraphGroupOrder(a.data("group")) - getImpactGraphGroupOrder(b.data("group"));
      if (groupDelta) return groupDelta;
      return String(a.data("label") || a.id()).localeCompare(String(b.data("label") || b.id()));
    });
    const laneCount = items.length > 7 ? 2 : 1;
    const rowCount = Math.ceil(items.length / laneCount);
    const usableHeight = Math.max(height - verticalPad * 2, 240);
    const rowGap = rowCount > 1 ? Math.min(94, usableHeight / (rowCount - 1)) : 0;
    const groupHeight = rowGap * Math.max(rowCount - 1, 0);
    const startY = height / 2 - groupHeight / 2;
    const baseX = activeGroups.length > 1 ? horizontalPad + columnGap * groupIndex : width / 2;
    const laneGap = Math.min(58, Math.max(38, usableWidth / Math.max(activeGroups.length, 1) * 0.16));

    items.forEach((node, index) => {
      const lane = laneCount === 2 ? index % 2 : 0;
      const row = laneCount === 2 ? Math.floor(index / 2) : index;
      const laneOffset = laneCount === 2 ? (lane === 0 ? -laneGap / 2 : laneGap / 2) : 0;
      positions[node.id()] = {
        x: baseX + laneOffset,
        y: startY + rowGap * row,
      };
    });
  });

  return positions;
}

function relayoutImpactGraph() {
  if (!state.impactGraphCy) return;
  state.impactGraphCy.resize();
  const positions = buildImpactGraphPresetPositions(state.impactGraphCy);
  state.impactGraphCy.layout({
    name: "preset",
    positions: (node) => positions[node.id()] || { x: 0, y: 0 },
    fit: true,
    padding: 28,
    animate: true,
    animationDuration: 360,
    animationEasing: "ease-out-cubic",
  }).run();
  window.setTimeout(() => {
    state.impactGraphCy?.fit(state.impactGraphCy.elements(), 28);
    state.impactGraphCy?.center(state.impactGraphCy.elements());
  }, 180);
}

function renderSearchResults(results = []) {
  const node = document.getElementById("search-results");
  if (!results.length) {
    setHTMLIfChanged(node, "");
    return;
  }

  const changed = setHTMLIfChanged(node, results
    .map(
      (item) => {
        const sectorLabel = item.sector ? `<em class="search-result-sector">${escapeHtml(item.sector)}</em>` : "";
        return `
        <button class="search-result" type="button" data-symbol="${escapeHtml(item.symbol)}" title="${escapeHtml(item.name || item.symbol)}">
          <div>
            <strong>${escapeHtml(item.symbol)}</strong>
            <p>${escapeHtml(item.name || item.exchange || "Market listing")}</p>
          </div>
          <div class="search-result-right">
            <span>${escapeHtml(item.matchType || "Match")}</span>
            ${sectorLabel}
            <em>${escapeHtml(item.matchReason || item.exchange || item.region || "Global")}</em>
          </div>
        </button>
      `;
      },
    )
    .join(""));
  if (!changed) return;

  node.querySelectorAll(".search-result").forEach((button) => {
    button.addEventListener("click", () => addTicker(button.dataset.symbol));
  });
}

function setSearchBusy(isBusy) {
  const form = document.getElementById("ticker-form");
  const button = document.getElementById("ticker-search-button");
  form?.classList.toggle("is-searching", Boolean(isBusy));
  if (button) {
    button.disabled = Boolean(isBusy);
    setTextIfChanged(button, isBusy ? "..." : "Search");
  }
}

function renderPresets() {
  const node = document.getElementById("preset-grid");
  node.innerHTML = state.presets
    .map(
      (preset) => `
        <button class="preset preset-pill" type="button" data-preset="${preset.name}">
          <span class="pn">${preset.label}</span>
          <span class="pc">${preset.symbols.length} sym</span>
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
  const quoteMap = new Map((state.dashboard?.watchlist || []).map((item) => [item.symbol, item]));
  node.innerHTML = state.recentTickers
    .map(
      (item) => {
        const quote = quoteMap.get(item.symbol);
        const priceLabel = quote ? formatCurrency(quote.price, quote.currency) : "Price pending";
        const moveClass = quote ? (Number(quote.changePercent || 0) >= 0 ? "up" : "down") : "";
        const liveClass = quote ? liveValueClass(`recent:${item.symbol}:price`, quote.price) : "";
        const freshClass = item.symbol === state.recentLastAdded ? "is-new" : "";
        return `
        <button class="recent-pill ${moveClass} ${freshClass} ${liveClass} ${item.symbol === state.activeTicker ? "active" : ""}" type="button" data-symbol="${item.symbol}" title="${item.name || item.symbol}">
          <strong>${item.symbol}${quote ? liveBadgeMarkup() : ""}</strong>
          <span>${item.name || "Recent ticker"}</span>
          <em class="live-number">${priceLabel}</em>
        </button>
      `;
      },
    )
    .join("");

  node.querySelectorAll(".recent-pill").forEach((button) => {
    button.addEventListener("click", () => {
      selectActiveTicker(button.dataset.symbol);
    });
  });
  if (state.recentLastAdded) {
    window.clearTimeout(state.recentAddTimer);
    state.recentAddTimer = window.setTimeout(() => {
      state.recentLastAdded = "";
      renderRecentTickers();
    }, 900);
  }
}

function renderWatchlist() {
  const node = document.getElementById("watchlist");
  const count = document.getElementById("watchlist-count");
  const entries = state.dashboard?.watchlist || [];
  const sidebar = node?.closest(".sidebar");
  const sidebarScrollTop = sidebar?.scrollTop || 0;
  const focusedSymbol = document.activeElement?.closest?.(".watch-item")?.dataset?.symbol || "";
  setTextIfChanged(count, String(entries.length));

  const markup = entries
    .map(
      (item) => {
        const priceClass = liveValueClass(`watch:${item.symbol}:price`, item.price);
        const changeClass = liveValueClass(`watch:${item.symbol}:change`, item.changePercent);
        return `
        <button class="watch-row watch-item ${priceClass} ${item.symbol === state.activeTicker ? "active" : ""}" type="button" data-symbol="${escapeHtml(item.symbol)}" draggable="true">
          <div>
            <div class="sym watch-symbol" title="${escapeHtml(item.symbol)}">${escapeHtml(item.symbol)}</div>
            <div class="name watch-name" title="${escapeHtml(item.name || item.symbol)}">${escapeHtml(item.name || item.symbol)}</div>
          </div>
          <div>
            <div class="px watch-price live-number ${priceClass}">${formatCurrency(item.price, item.currency)}</div>
            <div class="chg watch-change live-number ${item.changePercent >= 0 ? "up positive" : "down negative"} ${changeClass}">${formatPercent(item.changePercent)}</div>
          </div>
          <div class="watch-meta-row">
            <span>${escapeHtml(item.exchange)} · ${escapeHtml(item.currency)} · Vol ${formatCompactNumber(item.volume)}</span>
            <span class="drag-handle" data-drag-handle="${escapeHtml(item.symbol)}">::</span>
            <span class="delete-chip" data-delete="${escapeHtml(item.symbol)}">Delete</span>
          </div>
        </button>
      `;
      },
    )
    .join("");
  const changed = setHTMLIfChanged(node, markup);
  if (!changed) return;
  if (sidebar) sidebar.scrollTop = sidebarScrollTop;
  if (focusedSymbol) {
    node.querySelector(`.watch-item[data-symbol="${CSS.escape(focusedSymbol)}"]`)?.focus({ preventScroll: true });
  }

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
  const sourceNote = document.getElementById("radar-source-note");
  if (!track) return;
  const radar = state.dashboard?.radar || {};
  const headlineItems = radar.items?.length
    ? radar.items
        .filter((item) => item?.title)
        .slice(0, 6)
        .map((item) => ({
          title: item.title,
          url: safeExternalUrl(item.url || item.link),
          source: item.source || "",
        }))
    : (radar.headlines?.length ? radar.headlines : state.dashboard?.headlines?.length ? state.dashboard.headlines : ["Live radar updates are loading."])
        .slice(0, 6)
        .map((headline) => (typeof headline === "string"
          ? { title: headline, url: "", source: "" }
          : { title: headline?.title || "Market update", url: safeExternalUrl(headline?.url || headline?.link), source: headline?.source || "" }));
  const signature = headlineItems.map((item) => `${item.title}|${item.url}`).join(" | ");
  const useStaticLoadingHeadline = headlineItems.length === 1 && headlineItems[0].title === "Live radar updates are loading.";
  if (track.dataset.signature !== signature || !track.children.length) {
    const laneMarkup = (isDuplicate = false) => headlineItems
      .map((item) => {
        const title = escapeHtml(item.title);
        const source = item.source ? ` · ${escapeHtml(item.source)}` : "";
        return item.url
          ? `<a class="ticker-headline" href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer noopener" title="${title}${source}"${isDuplicate ? ' tabindex="-1"' : ""}>${title}</a>`
          : `<span class="ticker-headline" title="${title}${source}">${title}</span>`;
      })
      .join("");
    const duration = Math.max(22, Math.round(signature.length / 8));
    track.dataset.signature = signature;
    track.style.setProperty("--ticker-duration", `${duration}s`);
    track.innerHTML = useStaticLoadingHeadline
      ? `<div class="ticker-status">${escapeHtml(headlineItems[0].title)}</div>`
      : `
        <div class="ticker-lane ticker-lane-a">${laneMarkup(false)}</div>
        <div class="ticker-lane ticker-lane-b" aria-hidden="true">${laneMarkup(true)}</div>
      `;
  }
  if (sourceNote) {
    const sentiment = radar.sentiment || {};
    const label = sentiment.label || "Balanced";
    setTextIfChanged(sourceNote, label);
    const toneClass = sentiment.tone || (Number(sentiment.score || 0) > 0.2 ? "positive" : Number(sentiment.score || 0) < -0.2 ? "negative" : "");
    setClassIfChanged(sourceNote, toneClass);
  }

  // Populate the static breaking-news ribbon (template `.news-ribbon`).
  // Same source as the ticker tape, but rendered as a static flex row of
  // `<span class="item"><b>{source}</b> {title}</span>` so it matches the
  // design template (no marquee — the tape already handles scrolling).
  const ribbonList = document.querySelector(".news-ribbon .news-list");
  if (ribbonList) {
    const ribbonItems = useStaticLoadingHeadline
      ? [
          { source: "Radar", title: "Live headlines loading from source-labeled feeds" },
          { source: "Macro", title: "Bonds and inflation context stays visible while feeds refresh" },
          { source: "Cache", title: "Local history remains available for older series" },
          { source: "Risk", title: "Sentiment tone will update when radar data arrives" },
        ]
      : headlineItems.slice(0, 4);
    const ribbonSignature = ribbonItems.map((item) => `${item.source}|${item.title}`).join(" | ");
    if (ribbonList.dataset.signature !== ribbonSignature) {
      ribbonList.dataset.signature = ribbonSignature;
      setHTMLIfChanged(
        ribbonList,
        ribbonItems
          .map((item) => {
            const title = escapeHtml(item.title);
            const source = item.source ? `<b>${escapeHtml(item.source)}</b> ` : "";
            return `<span class="item">${source}${title}</span>`;
          })
          .join("")
      );
    }
  }
  const ribbonRisk = document.getElementById("news-ribbon-risk");
  if (ribbonRisk) {
    const sentiment = radar.sentiment || {};
    const score = Number(sentiment.score || 0);
    const riskLabel = sentiment.risk
      || (score < -0.2 ? "Risk-off" : score > 0.2 ? "Risk-on" : "Balanced");
    setTextIfChanged(ribbonRisk, riskLabel);
  }
}

function renderEventFeed() {
  const list = document.getElementById("event-list");
  document.querySelectorAll(".event-chip").forEach((button) => {
    button.classList.toggle("active", button.dataset.category === state.eventCategory);
  });
  if (!list) return;
  const items = state.eventResult?.items?.length
    ? [...state.eventResult.items].sort((a, b) => String(b.publishedAt || "").localeCompare(String(a.publishedAt || ""))).slice(0, 3)
    : [...(state.dashboard?.radar?.items || [])].slice(0, 3);
  setHTMLIfChanged(list, items.length
    ? items.map((item) => {
        const url = safeExternalUrl(item.url);
        const title = escapeHtml(item.title || "Update");
        return url
          ? `<a class="event-chip-link" href="${escapeHtml(url)}" target="_blank" rel="noreferrer noopener">${title}</a>`
          : `<span class="event-chip-link">${title}</span>`;
      }).join("")
    : "");
}

function renderPulse() {
  const grid = document.getElementById("pulse-grid");
  if (!grid) return;
  const items = state.dashboard?.macroPulse?.length
    ? state.dashboard.macroPulse
    : state.dashboard?.active
      ? [
          { label: "Risk tone", value: state.dashboard.active.regime || "–", positive: true },
          { label: "Move", value: formatPercent(state.dashboard.active.changePercent || 0), positive: Number(state.dashboard.active.changePercent || 0) >= 0 },
        ]
      : [];
  if (!items.length) { setHTMLIfChanged(grid, ""); return; }
  setHTMLIfChanged(grid, items
    .map((item) => `<span class="pulse-chip ${typeof item.positive === "boolean" ? (item.positive ? "positive" : "negative") : ""}">${escapeHtml(item.label)}: <strong>${escapeHtml(item.value)}</strong></span>`)
    .join(""));
}

function renderBoard() {
  /* Market board removed — watchlist sidebar is the single source */
}

function patchMarketSessionStrip(node, session) {
  if (!node || !session) return;
  if (!node.querySelector("[data-session-status]")) {
    node.innerHTML = `
      <span class="market-session-pill" data-session-status></span>
      <strong data-session-countdown></strong>
      <small data-session-hours></small>
    `;
  }
  const nextTransitionAt = session.nextTransitionAt ? new Date(session.nextTransitionAt) : null;
  const remainingSeconds = nextTransitionAt ? Math.max(0, Math.floor((nextTransitionAt.getTime() - Date.now()) / 1000)) : 0;
  const minuteRoundedSeconds = Math.ceil(remainingSeconds / 60) * 60;
  const countdown = nextTransitionAt ? formatDuration(minuteRoundedSeconds).replace(/:00$/, "") : "--:--";
  const nextLabel = session.transitionLabel === "close" ? "Closes in" : "Opens in";
  const statusNode = node.querySelector("[data-session-status]");
  const countdownNode = node.querySelector("[data-session-countdown]");
  const hoursNode = node.querySelector("[data-session-hours]");
  const statusClass = `market-session-pill ${session.isOpen ? "open" : "closed"}`;
  if (statusNode.className !== statusClass) {
    statusNode.className = statusClass;
  }
  setTextIfChanged(statusNode, session.status || "Closed");
  setTextIfChanged(countdownNode, `${nextLabel} ${countdown}`);
  setTextIfChanged(hoursNode, `${session.hoursLabel || "Hours unavailable"} · ${session.timezone || "UTC"}`);
}

function renderOverview() {
  const active = state.dashboard?.active;
  if (!active) return;
  const forecast = active.forecast || emptyForecastPayload();

  setTextIfChanged(document.getElementById("hero-ticker"), `${active.symbol} · ${active.name}`);
  patchHeroSurface(active, forecast);

  const majorEvent = Boolean(
    (active.eventFocus?.category && ["war", "deals", "partnerships", "layoffs"].includes(active.eventFocus.category))
      || String(forecast.eventPressureLabel || "").toLowerCase() === "high"
  );
  document.getElementById("overview-spotlight")?.classList.toggle("major-event", majorEvent);
  document.querySelector(".event-panel")?.classList.toggle("major-event", majorEvent);

  window.clearInterval(state.marketSessionTimer);
  const marketSessionNode = document.getElementById("market-session-strip");
  const renderSession = () => {
    const session = active.marketSession?.nextTransitionAt
      ? active.marketSession
      : buildClientMarketSession(active.exchange || active.region, active.marketState);
    patchMarketSessionStrip(marketSessionNode, session);
  };
  renderSession();
  if (active.marketSession?.nextTransitionAt) {
    state.marketSessionTimer = window.setInterval(renderSession, 1000);
  }

  // Defer the heavy SVG chart render so hero text & stats paint first.
  nextFrame(() => renderHeroChartOnly(active));
  renderStockDossier(active);
  renderOverviewLowerPanels(active, forecast);
}

function renderBondMarket() {
  const region = selectedRegionPayload();
  const summaryNode = document.getElementById("bond-summary");
  const curveNode = document.getElementById("bond-curve");
  const analysisNode = document.getElementById("bond-analysis");
  if (!summaryNode || !curveNode || !analysisNode) return;
  if (!region?.bonds) {
    summaryNode.innerHTML = `<div class="metric-card"><span>Bond market</span><strong>Loading</strong></div>`;
    curveNode.innerHTML = "";
    analysisNode.innerHTML = "";
    return;
  }
  const bonds = region.bonds;
  const research = region.researchProtocol || {};
  summaryNode.innerHTML = `
    <div class="metric-card"><span>10Y</span><strong>${bonds.tenors[2].yield.toFixed(2)}%</strong><small>${bonds.tenors[2].change1D >= 0 ? "+" : ""}${bonds.tenors[2].change1D.toFixed(1)} bp today</small></div>
    <div class="metric-card"><span>2s10s</span><strong>${bonds.curve.slope2s10s.toFixed(2)}%</strong><small>${bonds.curve.shape}</small></div>
    <div class="metric-card"><span>Real yield</span><strong>${Number(bonds.realYield || 0).toFixed(2)}%</strong><small>Rates anchor</small></div>
    <div class="metric-card"><span>Source</span><strong>${bonds.source}</strong><small>${formatEventDateTime(bonds.asOf)}</small></div>
  `;
  curveNode.innerHTML = bonds.tenors
    .map(
      (item) => `
        <div class="curve-point-card">
          <span>${item.tenor}</span>
          <strong>${item.yield.toFixed(2)}%</strong>
          <small>${item.change1D >= 0 ? "+" : ""}${item.change1D.toFixed(1)} bp</small>
        </div>
      `,
    )
    .join("");
  const analysis = region.analysis || {};
  analysisNode.innerHTML = `
    <div class="reason-card"><span class="analysis-tag fact">Fact</span><strong>What changed?</strong><p>${analysis.whatChanged || bonds.narrative}</p></div>
    <div class="reason-card"><span class="analysis-tag interpretation">Interpretation</span><strong>Why it changed</strong><p>${analysis.whyChanged || bonds.narrative}</p></div>
    <div class="reason-card"><span class="analysis-tag implication">Implication</span><strong>What it implies</strong><p>${analysis.marketImplication || "Rates are shaping cross-asset leadership."}</p></div>
    ${research.summary ? `<div class="reason-card"><span class="analysis-tag note">Protocol</span><strong>Research protocol</strong><p>${research.summary}</p></div>` : ""}
    ${(research.factors || [])
      .slice(0, 3)
      .map(
        (item) => `
          <div class="reason-card">
            <span class="analysis-tag fact">${item.significance || "High"}</span>
            <strong>${item.label}</strong>
            <p>${item.factsFirst}</p>
            <small>${item.cadence}${item.sourceLabel ? ` • ${item.sourceLabel}` : ""}</small>
          </div>
        `,
      )
      .join("")}
    ${(analysis.kbNotes || [])
      .map((note) => `<div class="reason-card"><span class="analysis-tag note">Note</span><strong>Regime note</strong><p>${note}</p></div>`)
      .join("")}
  `;
}

function renderInflationView() {
  const region = selectedRegionPayload();
  const inflationNode = document.getElementById("inflation-cards");
  const policyNode = document.getElementById("policy-cards");
  if (!inflationNode || !policyNode) return;
  if (!region?.inflation || !region?.policy) {
    inflationNode.innerHTML = "";
    policyNode.innerHTML = "";
    return;
  }
  const inflation = region.inflation;
  const policy = region.policy;
  inflationNode.innerHTML = `
    <div class="metric-card"><span>Headline CPI</span><strong>${Number(inflation.headline).toFixed(2)}%</strong><small>${inflation.source}</small></div>
    <div class="metric-card"><span>Core CPI</span><strong>${Number(inflation.core).toFixed(2)}%</strong><small>${inflation.impulse}</small></div>
    <div class="metric-card"><span>Breakeven</span><strong>${Number(inflation.breakeven || 0).toFixed(2)}%</strong><small>Inflation expectations</small></div>
    <div class="metric-card"><span>Real policy gap</span><strong>${Number(inflation.realPolicyGap || 0).toFixed(2)}%</strong><small>Policy minus headline CPI</small></div>
  `;
  policyNode.innerHTML = `
    <div class="reason-card"><span class="analysis-tag fact">Fact</span><strong>${policy.centralBank}</strong><p>${policy.policyRateLabel}: ${Number(policy.policyRate || 0).toFixed(2)}% • ${policy.stance}. ${policy.bias}.</p></div>
    <div class="reason-card"><span class="analysis-tag interpretation">Interpretation</span><strong>Inflation narrative</strong><p>${inflation.narrative}${inflation.officialLabel ? ` (${inflation.officialLabel})` : ""}</p></div>
  `;
}

function renderEquityContext() {
  const region = selectedRegionPayload();
  const summaryNode = document.getElementById("equity-summary");
  const sectorNode = document.getElementById("sector-grid");
  if (!summaryNode || !sectorNode) return;
  if (!region?.equity) {
    summaryNode.innerHTML = "";
    sectorNode.innerHTML = "";
    return;
  }
  const equity = region.equity;
  summaryNode.innerHTML = `
    <div class="reason-card"><span class="analysis-tag interpretation">Interpretation</span><strong>Rates to equities</strong><p>${equity.summary}</p></div>
    <div class="reason-card"><span class="analysis-tag implication">Implication</span><strong>Likely leadership</strong><p>${equity.styleBias}</p></div>
    ${equity.breadth ? `<div class="reason-card"><span class="analysis-tag fact">Breadth</span><strong>${equity.breadth.label}</strong><p>${equity.breadth.detail}</p></div>` : ""}
    ${equity.kbNote ? `<div class="reason-card"><span class="analysis-tag note">Note</span><strong>Sensitivity note</strong><p>${equity.kbNote}</p></div>` : ""}
  `;
  sectorNode.innerHTML = (equity.sectors || [])
    .map(
      (item) => {
        const effectCls = item.effect === "Positive" ? "positive" : item.effect === "Negative" ? "negative" : "neutral";
        const barW = item.effect === "Positive" ? 80 : item.effect === "Negative" ? 80 : 45;
        return `
        <div class="factor-card ${effectCls}">
          <div class="factor-card-header">
            <strong>${item.sector}</strong>
            <span>${item.effect}</span>
          </div>
          <div class="factor-score-bar"><div class="factor-score-fill ${effectCls}" style="width:${barW}%"></div></div>
          <p>${item.why}</p>
        </div>
      `;
      },
    )
    .join("");
}

function renderMacroEvents() {
  const region = selectedRegionPayload();
  const eventsNode = document.getElementById("macro-events-list");
  const watchNode = document.getElementById("macro-watch-next");
  if (!eventsNode || !watchNode) return;
  const eventPayload = state.eventResult?.items?.length ? state.eventResult : region?.events;
  if (!eventPayload) {
    eventsNode.innerHTML = "";
    watchNode.innerHTML = "";
    return;
  }
  document.querySelectorAll(".event-chip").forEach((button) => {
    button.classList.toggle("active", button.dataset.category === state.eventCategory);
  });
  eventsNode.innerHTML = (eventPayload.items || [])
    .slice(0, 6)
    .map(
      (item) => `
        <div class="event-card">
          <div class="event-card-header">
            <strong>${escapeHtml(item.title)}</strong>
            <span class="event-tag">${escapeHtml(String(item.category || "event").toUpperCase())}</span>
          </div>
          <p>${item.source ? `Source: ${escapeHtml(item.source)} • ` : ""}${escapeHtml(formatEventDateTime(item.publishedAt))}${item.sourceType ? ` • ${escapeHtml(item.sourceType.replace(/_/g, " "))}` : ""}${isFreshUpdate(item.publishedAt) ? ` • ${liveBadgeMarkup()}` : ""}</p>
        </div>
      `,
    )
    .join("");
  const monitorCards = (region.analysis?.monitorNext || [])
    .map((item) => `<div class="reason-card"><span class="analysis-tag monitor">Monitor</span><strong>Monitor</strong><p>${escapeHtml(item)}</p></div>`);
  const calendarCards = (region.calendar?.items || [])
    .slice(0, 4)
    .map(
      (item) => `
        <div class="reason-card">
          <span class="analysis-tag fact">Fact</span>
          <strong>Calendar</strong>
          <p>${escapeHtml(item.title)}${item.date ? ` • ${escapeHtml(item.date)}` : ""}${item.source ? ` • ${escapeHtml(item.source)}` : ""}</p>
        </div>
      `,
    );
  watchNode.innerHTML = monitorCards
    .concat(calendarCards)
    .join("");
}

function splitImpactLabel(text, limit = 18, maxLines = 2) {
  const words = String(text || "").trim().split(/\s+/).filter(Boolean);
  if (!words.length) return [""];
  const lines = [];
  let current = "";
  words.forEach((word) => {
    const next = current ? `${current} ${word}` : word;
    if (next.length <= limit || !current) {
      current = next;
      return;
    }
    lines.push(current);
    current = word;
  });
  if (current) lines.push(current);
  if (lines.length <= maxLines) return lines;
  const trimmed = lines.slice(0, maxLines);
  trimmed[maxLines - 1] = `${trimmed[maxLines - 1].replace(/\.\.\.$/, "").slice(0, Math.max(0, limit - 3)).trim()}...`;
  return trimmed;
}

function impactNodeDimensions(node = {}) {
  if (node.group === "project") return { width: 184, height: 60, radius: 20 };
  if (node.group === "entity") return { width: 156, height: 46, radius: 16 };
  if (node.group === "stock") return { width: 150, height: 50, radius: 18 };
  return { width: 134, height: 46, radius: 18 };
}

function drawImpactGraph(svg, graph) {
  if (!svg) return;
  const nodes = graph?.nodes || [];
  const links = graph?.links || [];
  if (!nodes.length) {
    svg.innerHTML = "";
    return;
  }
  const positions = {};
  const columns = {
    macro: { x: 118, yStart: 84, gap: 108 },
    market: { x: 324, yStart: 144, gap: 108 },
    stock: { x: 530, yStart: 78, gap: 88 },
    project: { x: 746, yStart: 70, gap: 84 },
    entity: { x: 962, yStart: 60, gap: 70 },
  };
  const counts = { macro: 0, market: 0, stock: 0, project: 0, entity: 0 };
  nodes.forEach((node) => {
    const cached = state.impactGraphPositions[node.id];
    if (cached) {
      positions[node.id] = cached;
      return;
    }
    const column = columns[node.group] || columns.stock;
    const idx = counts[node.group] || 0;
    positions[node.id] = { x: column.x, y: column.yStart + idx * column.gap };
    counts[node.group] = idx + 1;
  });
  const graphHeight = Math.max(
    440,
    ...Object.entries(columns).map(([group, config]) => config.yStart + ((counts[group] || 0) * config.gap) + 64),
  );
  svg.setAttribute("viewBox", `0 0 1088 ${graphHeight}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  const paletteByGroup = {
    macro: "rgba(255,176,0,0.18)",
    market: "rgba(115,210,255,0.18)",
    stock: "rgba(125,255,196,0.18)",
    project: "rgba(255,156,106,0.24)",
    entity: "rgba(255,255,255,0.12)",
  };
  svg.innerHTML = `
    <defs>
      <filter id="impact-glow"><feGaussianBlur stdDeviation="2.6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
    <g data-impact-links>
    ${links
      .map((link, index) => {
        const source = positions[link.source];
        const target = positions[link.target];
        if (!source || !target) return "";
        const color = link.direction === "positive" ? "#4dd889" : link.direction === "negative" ? "#ff6d6d" : "#f2c572";
        const width = Math.max(2.2, Number(link.value || 1) * 1.9);
        const sourceNode = nodes.find((node) => node.id === link.source) || {};
        const targetNode = nodes.find((node) => node.id === link.target) || {};
        const sourceBox = impactNodeDimensions(sourceNode);
        const targetBox = impactNodeDimensions(targetNode);
        const d = `M ${source.x + (sourceBox.width / 2) - 8} ${source.y} C ${source.x + 124} ${source.y}, ${target.x - 124} ${target.y}, ${target.x - (targetBox.width / 2) + 8} ${target.y}`;
        return `
          <path data-impact-link="${index}" d="${d}" fill="none" stroke="${color}" stroke-width="${width + 3}" opacity="0.18" filter="url(#impact-glow)" />
          <path data-impact-link-core="${index}" d="${d}" fill="none" stroke="${color}" stroke-width="${width}" opacity="0.82" stroke-linecap="round" />
          <circle r="${Math.max(2, width - 1)}" fill="${color}" opacity="0.72">
            <animateMotion dur="${4 + index}s" repeatCount="indefinite" path="${d}" />
          </circle>
        `;
      })
      .join("")}
    </g>
    <g data-impact-nodes>
    ${nodes
      .map((node) => {
        const pos = positions[node.id];
        const groupTone = paletteByGroup[node.group] || paletteByGroup.entity;
        const { width, height, radius } = impactNodeDimensions(node);
        const labelLines = splitImpactLabel(node.label, node.group === "project" ? 22 : node.group === "entity" ? 18 : 16, node.group === "project" ? 2 : 1);
        const subtitle = String(node.subtitle || "").trim();
        const kicker = String(node.impact || node.status || node.entityType || node.group || "").trim().toUpperCase();
        return `
          <g class="impact-node-group" data-node-id="${node.id}" data-node-group="${node.group}" transform="translate(${pos.x}, ${pos.y})">
            <rect class="impact-node-plate" x="-${width / 2}" y="-${height / 2}" width="${width}" height="${height}" rx="${radius}" fill="rgba(10,10,10,0.88)" stroke="${groupTone}" />
            <text x="0" y="${labelLines.length > 1 ? "-11" : "-5"}" text-anchor="middle" fill="#f7f0dd" font-size="${node.group === "project" ? 11 : node.group === "entity" ? 10.5 : 11.5}" font-family="Manrope, sans-serif">
              ${labelLines.map((line, index) => `<tspan x="0" dy="${index === 0 ? 0 : 12}">${line}</tspan>`).join("")}
            </text>
            ${subtitle ? `<text x="0" y="${node.group === "project" ? "18" : "12"}" text-anchor="middle" fill="rgba(255,228,187,0.82)" font-size="${node.group === "project" ? 9.5 : 8.6}" font-family="Azeret Mono, monospace">${subtitle}</text>` : ""}
            <text x="0" y="${node.group === "project" ? "30" : subtitle ? "22" : "15"}" text-anchor="middle" fill="rgba(220,210,188,0.66)" font-size="8.4" font-family="Azeret Mono, monospace">${kicker}</text>
          </g>
        `;
      })
      .join("")}
    </g>
  `;
  bindImpactGraphInteractions(svg, graph, positions);
}

function bindImpactGraphInteractions(svg, graph, positions) {
  const nodeElements = [...svg.querySelectorAll("[data-node-id]")];
  if (!nodeElements.length) return;
  const updateLinkPaths = () => {
    [...svg.querySelectorAll("[data-impact-link]")].forEach((glowPath, index) => {
      const link = (graph?.links || [])[index];
      if (!link) return;
      const source = positions[link.source];
      const target = positions[link.target];
      if (!source || !target) return;
      const sourceNode = (graph?.nodes || []).find((node) => node.id === link.source) || {};
      const targetNode = (graph?.nodes || []).find((node) => node.id === link.target) || {};
      const sourceBox = impactNodeDimensions(sourceNode);
      const targetBox = impactNodeDimensions(targetNode);
      const d = `M ${source.x + (sourceBox.width / 2) - 8} ${source.y} C ${source.x + 124} ${source.y}, ${target.x - 124} ${target.y}, ${target.x - (targetBox.width / 2) + 8} ${target.y}`;
      glowPath.setAttribute("d", d);
      const core = svg.querySelector(`[data-impact-link-core="${index}"]`);
      if (core) core.setAttribute("d", d);
    });
  };
  nodeElements.forEach((element) => {
    element.addEventListener("pointerdown", (event) => {
      if (event.button !== 0) return;
      event.preventDefault();
      const nodeId = element.dataset.nodeId;
      const start = positions[nodeId];
      if (!start) return;
      const startX = event.clientX;
      const startY = event.clientY;
      const handleMove = (moveEvent) => {
        const limitY = Number(svg.getAttribute("viewBox")?.split(" ")[3] || 440) - 44;
        const next = {
          x: Math.max(70, Math.min(1018, start.x + (moveEvent.clientX - startX))),
          y: Math.max(42, Math.min(limitY, start.y + (moveEvent.clientY - startY))),
        };
        positions[nodeId] = next;
        state.impactGraphPositions[nodeId] = next;
        element.setAttribute("transform", `translate(${next.x}, ${next.y})`);
        updateLinkPaths();
      };
      const cleanup = () => {
        window.removeEventListener("pointermove", handleMove);
        window.removeEventListener("pointerup", cleanup);
      };
      window.addEventListener("pointermove", handleMove);
      window.addEventListener("pointerup", cleanup);
    });
  });
}

function renderWatchlistImplications() {
  const region = selectedRegionPayload();
  const cardsNode = document.getElementById("watchlist-implication-cards");
  if (!cardsNode) return;
  if (!region?.watchlistImplications) {
    cardsNode.innerHTML = "";
    renderImpactGraphWorkspace({});
    return;
  }
  cardsNode.innerHTML = (region.watchlistImplications.cards || [])
    .map(
      (item) => `
        <div class="factor-card">
          <div class="factor-card-header">
            <strong>${item.symbol}</strong>
            <span>${item.confidence}</span>
          </div>
          <div class="factor-score-bar"><div class="factor-score-fill ${item.confidence === "High" ? "positive" : item.confidence === "Low" ? "negative" : "neutral"}" style="width:${item.confidence === "High" ? 85 : item.confidence === "Low" ? 30 : 55}%"></div></div>
          <p><strong>Scenario:</strong> ${item.scenario}</p>
          <p><strong>Impact:</strong> ${item.impact}</p>
          <p><strong>Why:</strong> ${item.why}</p>
          ${
            item.projects?.length
              ? `
                <div class="project-implication-list">
                  ${item.projects
                    .map(
                      (project) => `
                        <article class="project-implication-card">
                          <div class="project-implication-head">
                            <strong>${project.title}</strong>
                            <span>${project.worthLabel || "Undisclosed"}</span>
                          </div>
                          <p>${project.summary}</p>
                          <div class="project-implication-meta">
                            ${project.theme ? `<span>${project.theme}</span>` : ""}
                            ${project.status ? `<span>${project.status}</span>` : ""}
                            ${project.asOf ? `<span>${formatEventDateTime(project.asOf)}</span>` : ""}
                          </div>
                          ${
                            project.suppliers?.length
                              ? `<div class="project-supplier-list">${project.suppliers.map((supplier) => `<span>${supplier.label}${supplier.role ? ` • ${supplier.role}` : ""}</span>`).join("")}</div>`
                              : ""
                          }
                          ${
                            project.sourceUrl
                              ? `<a class="project-source-link" href="${project.sourceUrl}" target="_blank" rel="noreferrer noopener">${project.sourceLabel || "Source"}</a>`
                              : ""
                          }
                        </article>
                      `,
                    )
                    .join("")}
                </div>
              `
              : ""
          }
          ${item.marketMapNote?.summary ? `<p><strong>Map:</strong> ${item.marketMapNote.summary}</p>` : ""}
        </div>
      `,
    )
    .join("");
  renderImpactGraphWorkspace(region.watchlistImplications.graph || {});
}

function renderComparison() {
  const comparison = state.dashboard?.comparison;
  const summaryNode = document.getElementById("comparison-summary");
  const tableNode = document.getElementById("comparison-table");
  if (!summaryNode || !tableNode) return;
  if (!comparison) {
    summaryNode.textContent = "Comparison is loading.";
    tableNode.innerHTML = "";
    return;
  }
  summaryNode.textContent = comparison.summary;
  tableNode.innerHTML = `
    <div class="comparison-header">
      <span>Metric</span>
      <span>US</span>
      <span>India</span>
    </div>
    ${(comparison.rows || [])
      .map(
        (row) => `
          <div class="comparison-row">
            <strong>${row.metric}</strong>
            <span>${row.us}</span>
            <span>${row.india}</span>
          </div>
        `,
      )
      .join("")}
  `;
}


function renderOperations() {
  const summary = document.getElementById("operations-summary");
  const jobsNode = document.getElementById("operations-jobs");
  const runsNode = document.getElementById("operations-runs");
  if (!summary || !jobsNode || !runsNode) return;
  const payload = state.operations;
  if (!payload) {
    setTextIfChanged(summary, state.operationsLoading ? "Loading maintenance status…" : "Maintenance status is not loaded.");
    setHTMLIfChanged(jobsNode, "");
    setHTMLIfChanged(runsNode, "");
    return;
  }
  const activeRuns = payload.active || [];
  setTextIfChanged(
    summary,
    activeRuns.length
      ? `${activeRuns.length} maintenance workflow running. Only one bounded job runs at a time.`
      : "No maintenance workflow is running. Automatic macro and universe refreshes remain enabled."
  );
  setHTMLIfChanged(
    jobsNode,
    (payload.jobs || []).map((job) => `
      <article class="operation-card">
        <div>
          <strong>${escapeHtml(job.label)}</strong>
          <p>${escapeHtml(job.description)}</p>
        </div>
        <button type="button" data-operation-job="${escapeHtml(job.id)}" ${activeRuns.length ? "disabled" : ""}>Run now</button>
      </article>
    `).join("")
  );
  const runs = [...(payload.runs || [])].reverse().slice(0, 8);
  setHTMLIfChanged(
    runsNode,
    runs.length
      ? runs.map((run) => {
          const total = Math.max(1, Number(run.total || 0));
          const completed = Math.min(total, Number(run.completed || 0));
          const percent = Math.round((completed / total) * 100);
          const errors = (run.errors || []).slice(0, 2);
          return `
            <article class="operation-run is-${escapeHtml(run.status || "idle")}">
              <div class="operation-run-head">
                <strong>${escapeHtml(run.label || run.jobId || run.reason || "Maintenance")}</strong>
                <span>${escapeHtml(run.status || "idle")} · ${percent}%</span>
              </div>
              <div class="operation-progress"><span style="width:${percent}%"></span></div>
              ${(run.steps || []).map((step) => `<small>${escapeHtml(step.label || step.id || "Step")} · ${escapeHtml(step.status || "queued")}</small>`).join("")}
              ${errors.map((error) => `<p>${escapeHtml(error)}</p>`).join("")}
            </article>
          `;
        }).join("")
      : `<p class="micro-note">No maintenance runs in this server session.</p>`
  );
  jobsNode.querySelectorAll("[data-operation-job]").forEach((button) => {
    if (button.dataset.bound === "1") return;
    button.dataset.bound = "1";
    button.addEventListener("click", () => runOperation(button.dataset.operationJob));
  });
}


async function loadOperations({ silent = true } = {}) {
  if (!silent) setStatus("Loading operations");
  state.operationsLoading = true;
  renderOperations();
  try {
    state.operations = await api("/api/operations", { timeoutMs: 8000 });
  } finally {
    state.operationsLoading = false;
    renderOperations();
  }
  window.clearTimeout(state.operationsPollTimer);
  if ((state.operations?.active || []).length) {
    state.operationsPollTimer = window.setTimeout(() => {
      loadOperations({ silent: true }).catch(logNonAbort);
    }, 1800);
  }
}


async function runOperation(jobId) {
  if (!jobId || state.operationsLoading) return;
  setStatus("Starting maintenance");
  await api("/api/operations/run", {
    method: "POST",
    timeoutMs: 10000,
    body: JSON.stringify({ jobId }),
  });
  await loadOperations({ silent: true });
  flashStatus("Maintenance queued", 1400);
}


function renderLab() {
  if (!document.getElementById("lab-chart")) return;
  const active = state.dashboard?.active;
  const result = state.labResult?.symbol === active?.symbol ? state.labResult : active?.lab;
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

  drawProjection(document.getElementById("lab-chart"), result.historySeries?.length ? result.historySeries : result.history, result.projected, state.chartFeatures, { currency: active.currency, range: state.chartRange });
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
  if (!document.getElementById("academy-cards")) return;
  const active = state.dashboard?.active;
  const academyDetail = state.academyDetail;
  const agreement = active?.forecast?.models?.agreement || { label: "Pending", summary: "Agreement refreshing.", score: 0 };
  const tickerSpecific = active
    ? [
        {
          title: "Current ticker read",
          body: `${active.name} is trading in ${active.currency} with ${active.forecast.direction.toLowerCase()} bias, ${active.forecast.eventPressureLabel.toLowerCase()} event pressure, and ${active.regime.toLowerCase()}.`,
        },
        {
          title: "Current model mix",
          body: `${active.classicQuant?.summary || `${active.exchange} exposure, ${active.sector || "sector"} context, and volume at ${formatCompactNumber(active.volume)} are part of the current relationship map.`} ${agreement.summary}`,
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

  const classicCards = active?.classicQuant?.cards?.length
    ? active.classicQuant.cards
    : GLOSSARY.map((item) => ({
        title: item.term,
        formula: "Concept guide",
        value: "n/a",
        interpretation: item.body,
        failureMode: "Use with context rather than as a standalone signal.",
        tag: "Glossary",
      }));

  document.getElementById("glossary-list").innerHTML = classicCards
    .map(
      (item) => `
        <div class="glossary-card">
          <span>${item.tag || "Classic"}</span>
          <strong>${item.title}</strong>
          <code>${item.formula || "Formula unavailable"}</code>
          <p><strong>Live reading:</strong> ${item.value || "n/a"}.</p>
          <p>${item.interpretation}</p>
          <p><strong>Failure mode:</strong> ${item.failureMode}</p>
        </div>
      `,
    )
    .join("");

  document.getElementById("research-list").innerHTML = CLASSIC_QUANT_REFERENCES
    .concat(
      RESEARCH_REFERENCES.map((item) => ({
        ...item,
        track: "Modern",
      })),
    )
    .map(
      (item) => `
        <a class="research-card" href="${item.url}" target="_blank" rel="noreferrer noopener">
          <span>${item.track} · ${item.year}</span>
          <strong>${item.title}</strong>
          <p>${item.why}</p>
        </a>
      `,
    )
    .join("");

  const academyBrief = document.getElementById("academy-ticker-brief");
  const academySources = document.getElementById("academy-source-list");
  if (!academyDetail) {
    academyBrief.innerHTML = `
      <div class="academy-brief-card academy-loading-card">
        <strong>${active?.symbol || "Ticker"} explainer</strong>
        <p>Using live market structure while deeper company context loads.</p>
      </div>
    `;
    academySources.innerHTML = `<div class="academy-source-note">Web grounding will appear here when ready.</div>`;
    return;
  }

  academyBrief.innerHTML = `
    <div class="academy-brief-card">
      <strong>${escapeHtml(academyDetail.symbol)} Explainer</strong>
      <p>${escapeHtml(academyDetail.summary)}</p>
    </div>
    ${(academyDetail.cards || [])
      .map(
        (item) => `
          <div class="academy-brief-card">
            <strong>${escapeHtml(item.title)}</strong>
            <p>${escapeHtml(item.body)}</p>
          </div>
        `,
      )
      .join("")}
  `;

  academySources.innerHTML = (academyDetail.sources || []).length
    ? (academyDetail.sources || [])
        .map((item) => {
          const url = safeExternalUrl(item.url);
          if (!url) return "";
          return `<a class="academy-source-pill" href="${escapeHtml(url)}" target="_blank" rel="noreferrer noopener">${escapeHtml(item.title || extractDomainLabel(url) || "Source")}</a>`;
        })
        .join("")
    : `<div class="academy-source-note">No live web sources were returned for this ticker.</div>`;
}

function renderResearch() {
  if (!document.getElementById("research-summary")) return;
  const summary = document.getElementById("research-summary");
  const sources = document.getElementById("research-sources");
  if (state.researchLoading) {
    summary.innerHTML = `
      <div class="research-state-card">
        <strong>Building answer</strong>
        <p>Pulling dashboard context${document.getElementById("research-use-web")?.checked ? ", web grounding," : ""} and ${document.getElementById("research-use-llm")?.checked ? "Bonsai-8B-1bit" : "rule-based synthesis"}.</p>
      </div>
    `;
    sources.innerHTML = `<div class="source-card"><strong>Collecting sources</strong><p>Relevant links will appear here as soon as they are ready.</p></div>`;
    return;
  }

  if (state.researchError) {
    summary.innerHTML = `<div class="research-state-card"><strong>Research unavailable</strong><p>${escapeHtml(state.researchError)}</p></div>`;
    sources.innerHTML = `<div class="source-card"><strong>Retry ready</strong><p>Adjust the query or rerun with web search enabled.</p></div>`;
    return;
  }

  if (!state.researchResult) {
    summary.innerHTML = `<p class="muted">Ask about the active ticker, dashboard signals, a macro event, or a company. The assistant can use your local LLM and optional web search.</p>`;
    sources.innerHTML = `<div class="source-card"><strong>Waiting for query</strong><p>Web grounding and dashboard context will appear here.</p></div>`;
    return;
  }

  const { answer, takeaways = [], context = {}, webResults = [] } = state.researchResult;
  summary.innerHTML = `
    <div class="research-summary-head">
      <h4>${context.symbol ? `${escapeHtml(context.symbol)} Research Brief` : "Research Brief"}</h4>
      <div class="research-context-pills">
        ${context.symbol ? `<span>${escapeHtml(context.symbol)}</span>` : ""}
        ${context.regime ? `<span>${escapeHtml(context.regime)}</span>` : ""}
        <span>${state.researchResult.llmUsed ? "Bonsai assisted" : "Rules + context"}</span>
      </div>
    </div>
    <p>${escapeHtml(answer)}</p>
    ${takeaways.length ? `<ul>${takeaways.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
  `;

  if (!webResults.length) {
    sources.innerHTML = `<div class="source-card"><strong>No web results</strong><p>The response used dashboard context${state.researchResult.llmUsed ? " and your local LLM" : ""}.</p></div>`;
    return;
  }

  sources.innerHTML = webResults
    .map((item) => {
      const url = safeExternalUrl(item.url);
      if (!url) return "";
      return `
        <div class="source-card">
          <strong>${escapeHtml(item.title || "Result")}</strong>
          <p><a href="${escapeHtml(url)}" target="_blank" rel="noreferrer noopener">${escapeHtml(extractDomainLabel(url) || url)}</a></p>
        </div>
      `;
    })
    .join("");
}

function renderTopbar() {
  setTextIfChanged(document.getElementById("provider-badge"), state.dashboard?.provider || state.config?.provider || "yahoo");
  renderGlobalMarketOverview();
  setStatus(state.dashboard?.updatedAt ? "Live now" : "Loading data");
  document.body.classList.toggle("app-ready", state.bootReady);
  document.body.classList.toggle("app-booting", !state.bootReady);
  applyDetailMode();
}

function detailOnlyTabIds() {
  return new Set(["methodology", "watchlist-implications", "comparison"]);
}

function applyDetailMode() {
  document.body.classList.toggle("detail-mode", state.detailMode);
  const toggle = document.getElementById("toggle-detail-mode");
  if (toggle) {
    toggle.setAttribute("aria-pressed", state.detailMode ? "true" : "false");
    setTextIfChanged(toggle, state.detailMode ? "Simple" : "Detailed");
    toggle.title = state.detailMode ? "Return to essentials view" : "Show advanced tools";
  }
}

function setDetailMode(enabled) {
  state.detailMode = Boolean(enabled);
  localStorage.setItem(STORAGE_KEYS.detailMode, state.detailMode ? "1" : "0");
  applyDetailMode();
  const activeTab = document.querySelector(".topnav-link.active")?.dataset?.target
    || document.querySelector(".tab.active")?.dataset?.tab;
  if (!state.detailMode && detailOnlyTabIds().has(activeTab)) {
    activateTab("overview");
  }
  if (state.dashboard?.active) {
    renderStockDossier(state.dashboard.active);
  }
}

function liveStatusClusterMarkup() {
  return `
    <span class="live-indicator" aria-label="Dashboard live status">
      <span class="live-indicator-dot"></span>
      <span class="live-indicator-label">Live</span>
    </span>
  `;
}

function sectorStripMarkup(sectors = state.sectorStripSectors) {
  if (!Array.isArray(sectors) || !sectors.length) {
    return `<span class="sector-strip-label">Sectors loading</span>`;
  }
  return sectors.map((s) => {
    const unavailable = isUnavailableSector(s);
    const pct = Number(s.changePct ?? s.changePercent ?? s.change ?? 0);
    const dir = pct > 0.05 ? "up" : pct < -0.05 ? "down" : "flat";
    const sign = pct > 0 ? "+" : "";
    const label = s.name || s.label || s.symbol || "Sector";
    const displayLabel = label.replace(/\s*\(US\)\s*/i, "").replace("Financial Svcs", "Financial Services");
    const pctLabel = unavailable ? "Data pending" : `${sign}${pct.toFixed(2)}%`;
    return `<div class="sector-strip-chip ${unavailable ? "is-pending" : ""}" title="${label} ${pctLabel}">
      <span class="sector-strip-chip-name">${displayLabel}</span>
      <span class="sector-strip-chip-pct ${unavailable ? "pending" : dir}">${pctLabel}</span>
    </div>`;
  }).join("");
}

function renderGlobalMarketOverview() {
  const node = document.getElementById("global-market-overview");
  if (!node) return;
  const markets = state.dashboard?.globalMarkets || [];
  if (!markets.length) {
    node.classList.remove("collapsed");
    const emptySignature = `empty:${sectorStripMarkup()}`;
    const emptyMarkup = `
      <div class="bench-cell">
        <div class="b-head">
          <span class="b-country">Global Benchmarks</span>
          <span class="b-status closed">LOAD</span>
        </div>
        <div class="b-time">Markets loading</div>
        <div id="sector-overview-strip" class="sector-overview-strip" aria-label="Sector performance" hidden></div>
        <span class="global-market-head-actions" hidden>${liveStatusClusterMarkup()}</span>
      </div>
    `;
    if (node.dataset.benchmarkSignature !== emptySignature) {
      node.innerHTML = emptyMarkup;
      node.dataset.benchmarkSignature = emptySignature;
    }
    setHTMLIfChanged(node.querySelector("#sector-overview-strip"), sectorStripMarkup());
    return;
  }
  node.classList.remove("collapsed");
  const sectorMarkup = sectorStripMarkup();
  const signature = JSON.stringify({
    detailMode: state.detailMode,
    sectors: sectorMarkup,
    markets: markets.map((market) => ({
      label: market.label,
      timezone: market.timezone,
      isOpen: Boolean(market.session?.isOpen),
      hoursLabel: market.session?.hoursLabel || "",
      indices: (market.indices || []).map((item) => ({
        label: item.label,
        price: item.price,
        changePercent: item.changePercent,
        freshness: item.quoteFreshness?.label || item.quoteFreshness?.state || "",
      })),
    })),
  });
  const markup = markets.map((market, index) => `
    <article class="bench-cell market-clock-card" data-market-timezone="${market.timezone || "UTC"}">
      <div class="b-head market-clock-top">
        <span class="b-flag flag-${String(market.key || market.label || "").toLowerCase().includes("india") ? "in" : String(market.key || market.label || "").toLowerCase().includes("japan") ? "jp" : String(market.key || market.label || "").toLowerCase().includes("australia") ? "au" : String(market.key || market.label || "").toLowerCase().includes("hong") ? "hk" : String(market.key || market.label || "").toLowerCase().includes("london") || String(market.key || market.label || "").toLowerCase().includes("uk") ? "uk" : "us"}"></span>
        <span class="b-country">${market.label}</span>
        <span class="b-status ${market.session?.isOpen ? "open" : "closed"}">${market.session?.isOpen ? "OPEN" : "CLSD"}</span>
      </div>
      <div class="b-time"><span data-market-time></span> · <span data-market-date></span> · ${market.session?.hoursLabel || market.timezone || ""}</div>
      <div class="b-indices">
        ${(market.indices || []).slice(0, 2).map((item) => `
          <div class="b-idx market-index-row ${item.quoteFreshness?.isStale ? "is-stale" : ""}">
            <span class="idx-name">${item.label}</span>
            <span class="idx-val">${formatIndexLevel(item.price)}</span>
            <span class="idx-chg ${Number(item.changePercent || 0) >= 0 ? "up positive" : "down negative"}">${formatPercent(item.changePercent || 0)}</span>
          </div>
        `).join("")}
      </div>
      ${index === 0 ? `<div id="sector-overview-strip" class="sector-overview-strip" aria-label="Sector performance" hidden>${sectorMarkup}</div><span class="global-market-head-actions" hidden>${liveStatusClusterMarkup()}</span>` : ""}
    </article>
  `).join("");
  if (node.dataset.benchmarkSignature !== signature) {
    node.innerHTML = markup;
    node.dataset.benchmarkSignature = signature;
  }
  updateGlobalMarketClocks();
}

function updateGlobalMarketClocks() {
  document.querySelectorAll(".market-clock-card[data-market-timezone]").forEach((card) => {
    const timezone = card.dataset.marketTimezone || "UTC";
    const dateLabel = formatZonedDate(timezone);
    const timeLabel = formatZonedTime(timezone);
    const clockKey = `${dateLabel}|${timeLabel}`;
    if (marketClockKeys.get(card) === clockKey) return;
    marketClockKeys.set(card, clockKey);
    setTextIfChanged(card.querySelector("[data-market-date]"), dateLabel);
    setTextIfChanged(card.querySelector("[data-market-time]"), timeLabel);
  });
}

function toggleBenchmarksCollapsed() {
  const node = document.getElementById("global-market-overview");
  const toggle = node?.querySelector(".global-market-overview-head");
  if (!node || !toggle) return;
  if (!state.detailMode) {
    state.benchmarksCollapsed = false;
    localStorage.setItem(STORAGE_KEYS.benchmarksCollapsed, "0");
    setDetailMode(true);
    renderGlobalMarketOverview();
    return;
  }
  state.benchmarksCollapsed = !state.benchmarksCollapsed;
  localStorage.setItem(STORAGE_KEYS.benchmarksCollapsed, state.benchmarksCollapsed ? "1" : "0");
  node.classList.toggle("collapsed", state.benchmarksCollapsed);
  toggle.setAttribute("aria-expanded", state.benchmarksCollapsed ? "false" : "true");
}

function renderCompactMenu() {
  const list = document.getElementById("compact-menu-list");
  if (!list) return;
  list.innerHTML = COMPACT_SECTIONS
    .map((item) => {
      const target = document.getElementById(item.id);
      if (!target) return "";
      return `<button type="button" data-compact-target="${item.id}">${item.label}</button>`;
    })
    .join("");
  list.querySelectorAll("[data-compact-target]").forEach((button) => {
    button.addEventListener("click", () => {
      const targetId = button.dataset.compactTarget;
      const panel = document.getElementById(targetId);
      if (!panel) return;
      if (panel.classList.contains("tab-panel") && !panel.classList.contains("active")) {
        activateTab(targetId);
      }
      document.getElementById("compact-section-menu")?.classList.remove("open");
      document.getElementById("compact-menu-toggle")?.setAttribute("aria-expanded", "false");
      panel.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

function activateTab(target) {
  document.querySelectorAll(".tab").forEach((node) => {
    const active = node.dataset.tab === target;
    node.classList.toggle("active", active);
    node.setAttribute("aria-selected", active ? "true" : "false");
    node.tabIndex = active ? 0 : -1;
  });
  document.querySelectorAll(".topnav-link").forEach((node) => {
    const active = node.dataset.target === target;
    node.classList.toggle("active", active);
    node.setAttribute("aria-selected", active ? "true" : "false");
    node.tabIndex = active ? 0 : -1;
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    const active = panel.id === target;
    panel.classList.toggle("active", active);
    panel.hidden = !active;
  });
  if (target === "watchlist-implications") {
    renderWatchlistImplications();
    window.setTimeout(() => {
      if (state.pendingImpactGraph) {
        const pending = state.pendingImpactGraph;
        state.pendingImpactGraph = null;
        renderImpactGraphWorkspace(pending);
      } else {
        relayoutImpactGraph();
      }
    }, 120);
  }
  if (target === "operations") {
    loadOperations({ silent: true }).catch(logNonAbort);
  }
}

function startMarketClockTimer() {
  window.clearInterval(state.marketClockTimer);
  state.marketClockTimer = window.setInterval(() => {
    updateGlobalMarketClocks();
  }, 15_000);
}

function renderCorePanels() {
  renderAlerts();
  renderSearchResults();
  renderPresets();
  renderSavedWatchlists();
  renderRecentTickers();
  renderWatchlist();
  renderBanner();
  renderBoard();
  renderPulse();
  renderOverview();     // critical — renders synchronously so hero paints first
  renderMarketHeatMap();
  renderTopbar();
  renderCompactMenu();
  // Defer hidden-tab renders to idle time so Overview paints before them
  deferWork(() => {
    renderBondMarket();
    renderInflationView();
    renderEquityContext();
    renderMacroEvents();
    renderMethodology();
    renderWatchlistImplications();
    renderComparison();
    renderOperations();
    setupScrollReveal();
  }, 200);
}

function renderDeferredPanels() {
  renderLab();
  renderAcademy();
  renderResearch();
  renderEventFeed();
  setupScrollReveal();
}

function applyLiveQuoteUpdate(payload) {
  if (!state.dashboard || !payload) return;
  state.dashboard.updatedAt = payload.updatedAt;
  const usableQuotes = (payload.watchlist || []).filter((item) => Number.isFinite(Number(item.price)));
  const payloadActiveUsable = payload.active && Number.isFinite(Number(payload.active.price));
  if (!usableQuotes.length && !payloadActiveUsable) return;
  processRecentTickerAlerts(usableQuotes);

  const quoteMap = new Map(usableQuotes.map((item) => [item.symbol, item]));
  state.dashboard.watchlist = (state.dashboard.watchlist || []).map((item) => {
    const live = quoteMap.get(item.symbol);
    return live ? { ...item, ...live } : item;
  });

  if (payloadActiveUsable && state.dashboard.active?.symbol === payload.active.symbol) {
    const previousActive = state.dashboard.active;
    state.dashboard.active = {
      ...state.dashboard.active,
      ...payload.active,
      receivedAt: payload.active.receivedAt || payload.updatedAt,
      marketSession:
        payload.active.marketSession ||
        buildClientMarketSession(payload.active.exchange || payload.active.region, payload.active.marketState, payload.active.region),
    };
    state.dashboard.active = mergeQuoteIntoActiveHistory(state.dashboard.active, previousActive, payload.updatedAt);
  } else if (payload.active) {
    const live = quoteMap.get(state.activeTicker);
    if (live && state.dashboard.active) {
      const previousActive = state.dashboard.active;
      state.dashboard.active = {
        ...state.dashboard.active,
        ...live,
        receivedAt: live.receivedAt || payload.updatedAt,
        marketSession: buildClientMarketSession(live.exchange || live.region, live.marketState, live.region),
      };
      state.dashboard.active = mergeQuoteIntoActiveHistory(state.dashboard.active, previousActive, payload.updatedAt);
    }
  }

  renderWatchlist();
  renderBoard();
  if (state.dashboard.active) {
    patchOverviewLiveSurface(
      state.dashboard.active,
      state.dashboard.active.forecast || emptyForecastPayload(),
      { redrawChart: shouldRedrawLiveChart() },
    );
  }
  renderTopbar();
  flashStatus("Live now", 900);
}

function startQuoteStream() {
  if (state.quoteStream) {
    state.quoteStream.close();
  }
  const symbols = encodeURIComponent(state.watchlist.join(","));
  const active = encodeURIComponent(state.activeTicker || "");
  const streamPath = `/api/stream?symbols=${symbols}&active=${active}`;
  const stream = new EventSource(`${API_BASE}${streamPath}`);
  state.quoteStream = stream;
  state.dataFlow.stream = "connecting";
  renderDataFlowBar();
  stream.addEventListener("open", () => {
    state.dataFlow.stream = "live";
    state.dataFlow.lastUpdated = new Date().toISOString();
    renderDataFlowBar();
  });
  stream.addEventListener("quote", (event) => {
    try {
      const payload = JSON.parse(event.data);
      state.dataFlow.stream = "live";
      state.dataFlow.lastUpdated = new Date().toISOString();
      applyLiveQuoteUpdate(payload);
      renderDataFlowBar();
    } catch (error) {
      logNonAbort(error);
    }
  });
  stream.onerror = () => {
    state.dataFlow.stream = "retry";
    renderDataFlowBar();
    setStatus("Stream retry");
  };
}

function render() {
  renderCorePanels();
  renderDeferredPanels();
  const labTicker = document.getElementById("lab-ticker");
  if (labTicker) {
    labTicker.value = state.activeTicker;
  }
}

function startRadarRefresh() {
  window.clearInterval(state.radarTimer);
  state.radarTimer = window.setInterval(() => {
    loadRadar({ silent: true }).catch((error) => {
      logNonAbort(error);
    });
  }, REFRESH_INTERVALS.radar);
}

function startOverviewRefresh() {
  window.clearInterval(state.overviewTimer);
  state.overviewTimer = window.setInterval(() => {
    if (document.hidden) return;
    loadOverviewFast({ silent: true }).catch((error) => {
      logNonAbort(error);
      setStatus("Quote refresh delayed");
    });
  }, REFRESH_INTERVALS.overview);
}

// Fast price-only poll. Reuses applyLiveQuoteUpdate, which is the same path
// the SSE stream uses, so DOM patching/event listeners stay intact.
async function loadQuotesFast() {
  if (!state.dashboard) return;
  if (!Array.isArray(state.watchlist) || !state.watchlist.length) return;
  const requestId = ++state.quotesRequestId;
  const params = new URLSearchParams({
    symbols: state.watchlist.join(","),
    active: state.activeTicker || "",
  });
  const payload = await api(`/api/quotes?${params.toString()}`, { timeoutMs: 6000 });
  if (requestId !== state.quotesRequestId) return;
  applyLiveQuoteUpdate(payload);
}

function startQuotesRefresh() {
  window.clearInterval(state.quotesTimer);
  state.quotesTimer = window.setInterval(() => {
    if (document.hidden) return;
    loadQuotesFast().catch((error) => {
      logNonAbort(error);
    });
  }, REFRESH_INTERVALS.quotes);
}

async function loadGlobalMarkets({ silent = true } = {}) {
  if (!state.dashboard) return;
  if (!silent) setStatus("Refreshing global markets");
  const payload = await api("/api/global-markets", { timeoutMs: 10000 });
  if (!Array.isArray(payload?.markets)) return;
  state.dashboard.globalMarkets = payload.markets;
  state.dashboard.updatedAt = payload.updatedAt || state.dashboard.updatedAt;
  renderTopbar();
}

function startGlobalMarketsRefresh() {
  window.clearInterval(state.globalMarketTimer);
  state.globalMarketTimer = window.setInterval(() => {
    if (document.hidden) return;
    loadGlobalMarkets({ silent: true }).catch((error) => {
      logNonAbort(error);
    });
  }, REFRESH_INTERVALS.globalMarkets);
}

function startDashboardRefresh() {
  window.clearInterval(state.dashboardTimer);
  state.dashboardTimer = window.setInterval(() => {
    refreshDashboard().catch((error) => {
      logNonAbort(error);
      setStatus("Refresh delayed");
    });
  }, REFRESH_INTERVALS.dashboard);
}

function captureDashboardViewport() {
  const main = document.querySelector(".main");
  if (!main) return null;
  const mainTop = main.getBoundingClientRect().top;
  const candidates = [
    document.getElementById("global-market-overview"),
    document.querySelector(".news-ribbon"),
    document.getElementById("overview-spotlight"),
    document.querySelector(".hero-chart-card"),
    document.getElementById("prediction-panel"),
    document.getElementById("stock-dossier-panel"),
  ].filter(Boolean);
  const visible = candidates
    .map((node) => ({ node, rect: node.getBoundingClientRect() }))
    .filter((item) => item.rect.bottom > mainTop + 1)
    .sort((a, b) => Math.abs(a.rect.top - mainTop) - Math.abs(b.rect.top - mainTop))[0];
  return {
    main,
    scrollTop: main.scrollTop,
    anchor: visible?.node || null,
    anchorTop: visible?.rect?.top ?? mainTop,
  };
}

function restoreDashboardViewport(snapshot) {
  if (!snapshot?.main?.isConnected) return;
  nextFrame(() => {
    if (!snapshot.main.isConnected) return;
    if (!snapshot.anchor?.isConnected) {
      snapshot.main.scrollTop = snapshot.scrollTop;
      return;
    }
    const delta = snapshot.anchor.getBoundingClientRect().top - snapshot.anchorTop;
    snapshot.main.scrollTop = snapshot.scrollTop + delta;
  });
}

async function loadConfig() {
  setStatus("Loading config");
  state.config = await api("/api/config");
  document.getElementById("provider-select").value = state.config.provider || "yahoo";
  const alphaKey = document.getElementById("alpha-key");
  const fredKey = document.getElementById("fred-key");
  alphaKey.value = "";
  alphaKey.placeholder = state.config.alphaVantageConfigured ? "Configured — enter to replace" : "Optional";
  fredKey.value = "";
  fredKey.placeholder = state.config.fredConfigured ? "Configured — enter to replace" : "Optional";
  document.getElementById("llm-base-url").value = state.config.localLlmBaseUrl || "http://127.0.0.1:11434";
  document.getElementById("llm-model").value = state.config.localLlmModel || "Bonsai-8B-1bit";
  state.dataFlow.boot.config = true;
  renderDataFlowBar();
  renderTopbar();
}

async function loadPresets() {
  const payload = await api("/api/presets");
  state.presets = payload.presets || [];
  state.dataFlow.boot.presets = true;
  renderDataFlowBar();
  renderPresets();
}

async function loadSavedWatchlists() {
  const payload = await api("/api/watchlists");
  state.savedWatchlists = payload.watchlists || [];
  state.dataFlow.boot.watchlists = true;
  renderDataFlowBar();
  renderSavedWatchlists();
}

function getEventCacheKey(keyword = "") {
  return [state.eventCategory || "business", state.activeTicker || "", keyword.trim().toLowerCase()].join("::");
}

function startEventRefresh() {
  window.clearInterval(state.eventTimer);
  state.eventTimer = window.setInterval(() => {
    loadEventFeed(state.eventLastQuery || "", { silent: true, force: true }).catch((error) => {
      logNonAbort(error);
    });
  }, REFRESH_INTERVALS.events);
}

async function loadEventFeed(keyword = "", { silent = false, force = false } = {}) {
  const requestId = ++state.eventRequestId;
  const normalizedKeyword = keyword.trim();
  const cacheKey = getEventCacheKey(normalizedKeyword);
  const cached = state.eventCache[cacheKey];
  state.eventLastQuery = normalizedKeyword;
  if (!force && cached && Date.now() - cached.cachedAt < 1800000) {
    state.eventResult = cached.payload;
    return cached.payload;
  }
  if (!silent) {
    setStatus("Loading feed");
  }
  const params = new URLSearchParams({
    category: state.eventCategory,
    symbol: state.activeTicker || "",
  });
  if (normalizedKeyword) {
    params.set("q", normalizedKeyword);
  }
  const result = await api(`/api/events?${params.toString()}`);
  if (requestId !== state.eventRequestId) return;
  state.eventResult = result;
  state.eventCache[cacheKey] = { payload: result, cachedAt: Date.now() };
  return result;
}

async function loadAcademyDetail(symbol = state.activeTicker, { silent = false } = {}) {
  const requestId = ++state.academyRequestId;
  if (!silent) {
    setStatus("Loading learn");
  }
  try {
    const result = await api(`/api/academy?symbol=${encodeURIComponent(symbol)}&web=1&llm=1`, { timeoutMs: 10000 });
    if (requestId !== state.academyRequestId) return;
    state.academyDetail = result;
    state.academyCache[symbol] = result;
  } catch (error) {
    const fallback = await api(`/api/academy?symbol=${encodeURIComponent(symbol)}&web=1&llm=0`, { timeoutMs: 8000 }).catch(() => null);
    if (requestId !== state.academyRequestId || !fallback) return;
    state.academyDetail = fallback;
    state.academyCache[symbol] = fallback;
  }
}

function selectActiveTicker(symbol, { refresh = true } = {}) {
  const cleaned = (symbol || "").trim().toUpperCase();
  if (!cleaned) return;
  const changed = state.activeTicker !== cleaned;
  state.activeTicker = cleaned;
  if (changed) {
    state.dataFlow.highWater = 0;
    primeActiveTickerSelection(cleaned);
    // Only pre-add to recent if we already know the name (resolved previously).
    // New unresolved tickers are added only after refreshDashboard confirms price+name.
    const knownName =
      state.dashboard?.watchlist?.find((item) => item.symbol === cleaned)?.name
      || state.recentTickers.find((item) => item.symbol === cleaned)?.name
      || "";
    if (knownName) pushRecentTicker(cleaned, knownName);
  }
  persistWatchlist();
  renderWatchlist();
  renderBoard();
  renderRecentTickers();
  renderOverview();
  renderLab();
  renderAcademy();
  if (!refresh) return;
  if (changed) {
    setStatus("Loading quote");
    loadOverviewFast({ silent: true }).catch((error) => {
      logNonAbort(error);
    });
  }
  refreshDashboard();
}

function scheduleHistoryWarmup({ immediate = false } = {}) {
  const symbols = Array.from(new Set([...(state.watchlist || []), state.activeTicker].filter(Boolean).map((item) => item.toUpperCase())));
  if (!symbols.length) return;
  const ranges = ["1D", "3D", "5D", "1M", "1Y", "2Y", "5Y"];
  const key = `${symbols.join(",")}::${ranges.join(",")}`;
  if (state.historyWarmupKeys.has(key)) return;
  state.historyWarmupKeys.add(key);
  const run = () => {
    api("/api/history/warm", {
      method: "POST",
      timeoutMs: 6000,
      body: JSON.stringify({ symbols, ranges }),
    }).then(() => {
      scheduleHistoryProgressPoll(750);
      pollHistoryProgress();
    }).catch((error) => {
      state.historyWarmupKeys.delete(key);
      logNonAbort(error);
    });
  };
  if (immediate) {
    run();
    return;
  }
  if ("requestIdleCallback" in window) {
    window.requestIdleCallback(run, { timeout: 3000 });
  } else {
    window.setTimeout(run, 900);
  }
}

async function refreshDashboard({ primeFast = true, primeRadar = true } = {}) {
  const requestId = ++state.dashboardRequestId;
  setStatus("Refreshing");
  if (primeFast) {
    loadOverviewFast({ silent: true }).catch((error) => {
      logNonAbort(error);
    });
  }
  if (primeRadar) {
    loadRadar({ silent: true }).catch((error) => {
      logNonAbort(error);
    });
  }
  const payload = await api("/api/dashboard", {
    method: "POST",
    timeoutMs: 45000,
    body: JSON.stringify({
      symbols: state.watchlist,
      active: state.activeTicker,
      chartRange: state.chartRange,
      region: state.selectedRegion,
    }),
  });
  if (requestId !== state.dashboardRequestId) return;

  if (!hydrateDashboardFromPayload(payload)) {
    state.dataFlow.lastError = "Dashboard payload was incomplete";
    renderDataFlowBar();
    throw new Error("Dashboard payload was incomplete");
  }
  state.dataFlow.lastError = "";
  saveDashboardCache(payload);
  persistWatchlist();
  const viewportSnapshot = captureDashboardViewport();
  nextFrame(() => {
    renderCorePanels();
    restoreDashboardViewport(viewportSnapshot);
    markDashboardInteractive("Live now");
    renderDataFlowBar();
  });
  deferWork(() => {
    if (requestId !== state.dashboardRequestId) return;
    renderLab();
    renderAcademy();
    renderResearch();
  });
  startQuoteStream();
  flashStatus("Live now");
  loadEventFeed("", { silent: true })
    .then(() => {
      deferWork(() => {
        if (requestId !== state.dashboardRequestId) return;
        renderEventFeed();
      });
    })
    .catch((error) => {
      logNonAbort(error);
    });
  if (document.getElementById("academy-cards")) {
    loadAcademyDetail(state.activeTicker, { silent: true })
      .then(() => {
        deferWork(() => {
          if (requestId !== state.dashboardRequestId) return;
          renderAcademy();
        });
      })
      .catch((error) => {
        logNonAbort(error);
      });
  }
  loadRadar({ silent: true }).catch((error) => {
    logNonAbort(error);
  });
  scheduleHistoryWarmup();
}

function initBrandIntro() {
  const intro = document.getElementById("brand-intro");
  if (!intro) return;
  const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
  const seen = localStorage.getItem(STORAGE_KEYS.brandIntroSeen) === "1";
  if (seen || reduceMotion) {
    intro.remove();
    return;
  }

  localStorage.setItem(STORAGE_KEYS.brandIntroSeen, "1");
  intro.hidden = false;
  requestAnimationFrame(() => intro.classList.add("is-visible"));
  let dismissed = false;
  const dismiss = () => {
    if (dismissed) return;
    dismissed = true;
    intro.classList.add("is-leaving");
    window.setTimeout(() => intro.remove(), 420);
  };
  intro.addEventListener("click", dismiss, { once: true });
  window.setTimeout(dismiss, 1450);
}

async function runSearch() {
  const input = document.getElementById("ticker-input");
  const query = input.value.trim();
  if (!query) {
    renderSearchResults();
    return;
  }

  const requestId = ++state.searchRequestId;
  setStatus("Searching");
  setSearchBusy(true);
  try {
    const payload = await api(`/api/search?q=${encodeURIComponent(query)}`, { timeoutMs: 9000 });
    if (requestId !== state.searchRequestId) return;
    renderSearchResults(payload.results || []);
    flashStatus("Search ready", 1200);
  } catch (error) {
    if (requestId !== state.searchRequestId) return;
    logNonAbort(error);
    renderSearchResults();
    setStatus("Search delayed");
  } finally {
    if (requestId === state.searchRequestId) setSearchBusy(false);
  }
}

function addTicker(symbol) {
  const cleaned = symbol.trim().toUpperCase();
  if (!cleaned) return;
  if (!state.watchlist.includes(cleaned)) {
    state.watchlist.unshift(cleaned);
  }
  state.activeTicker = cleaned;
  state.labResult = null;
  // Recent ticker added after refreshDashboard confirms resolution (price + name)
  persistWatchlist();
  refreshDashboard();
}

function removeTicker(symbol) {
  if (state.watchlist.length <= 1) return;
  const wasActive = state.activeTicker === symbol;
  state.watchlist = state.watchlist.filter((item) => item !== symbol);
  // Remove from dashboard watchlist cache so it vanishes immediately
  if (state.dashboard?.watchlist) {
    state.dashboard.watchlist = state.dashboard.watchlist.filter((item) => item.symbol !== symbol);
  }
  persistWatchlist();
  if (wasActive) {
    state.activeTicker = state.watchlist[0];
    state.labResult = null;
    renderWatchlist();
    renderRecentTickers();
    refreshDashboard();
  } else {
    // Non-active delete: just re-render the watchlist instantly, no API call
    renderWatchlist();
    renderRecentTickers();
  }
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

// ── Sector Performance Matrix ─────────────────────────────────────────────────

const SECTOR_MATRIX_STORAGE_KEY = "financial-board-sector-history";
const SECTOR_BENCHMARK_OPTIONS = {
  india: [
    ["^NSEI", "NIFTY 50"],
    ["^BSESN", "SENSEX"],
    ["^NSEBANK", "NIFTY Bank"],
  ],
  us: [
    ["^GSPC", "S&P 500"],
    ["^NDX", "NASDAQ 100"],
    ["^DJI", "Dow Jones"],
  ],
  global: [
    ["^NSEI", "NIFTY 50"],
    ["^GSPC", "S&P 500"],
    ["^N225", "Nikkei 225"],
  ],
};

function loadSectorMatrixPrefs() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.sectorMatrix) || "{}");
  } catch {
    return {};
  }
}

function saveSectorMatrixPrefs(prefs) {
  localStorage.setItem(STORAGE_KEYS.sectorMatrix, JSON.stringify(prefs));
}

function loadSectorHistory() {
  try { return JSON.parse(localStorage.getItem(SECTOR_MATRIX_STORAGE_KEY) || "{}"); }
  catch { return {}; }
}

function saveSectorHistory(market, period, benchmark, sectors, meta = {}) {
  try {
    const history = loadSectorHistory();
    if (!history[market]) history[market] = {};
    const key = `${period}:${benchmark || "default"}`;
    if (!history[market][key]) history[market][key] = [];
    const snap = { ts: Date.now(), sectors, meta };
    history[market][key].unshift(snap);
    // Keep last 90 snapshots per market+period
    history[market][key] = history[market][key].slice(0, 90);
    localStorage.setItem(SECTOR_MATRIX_STORAGE_KEY, JSON.stringify(history));
  } catch { /* quota */ }
}

function loadSectorSnapshot(market, period, benchmark) {
  return loadSectorHistory()?.[market]?.[`${period}:${benchmark || "default"}`]?.[0];
}

function loadMarketHeatMapPrefs() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.marketHeatMap) || "{}") || {};
  } catch {
    return {};
  }
}

function saveMarketHeatMapPrefs(prefs) {
  localStorage.setItem(STORAGE_KEYS.marketHeatMap, JSON.stringify(prefs));
}

function sectorHeatColor(pct) {
  if (pct > 2) return "var(--positive, #22c55e)";
  if (pct > 0.5) return "rgba(34,197,94,0.7)";
  if (pct > 0) return "rgba(34,197,94,0.38)";
  if (pct < -2) return "var(--negative, #ef4444)";
  if (pct < -0.5) return "rgba(239,68,68,0.7)";
  if (pct < 0) return "rgba(239,68,68,0.38)";
  return "rgba(255,255,255,0.1)";
}

function marketHeatMapColor(pct) {
  if (pct > 3) return "rgba(24, 190, 104, 0.9)";
  if (pct > 1) return "rgba(39, 166, 97, 0.78)";
  if (pct > 0.15) return "rgba(60, 142, 87, 0.56)";
  if (pct < -3) return "rgba(235, 62, 72, 0.92)";
  if (pct < -1) return "rgba(200, 48, 58, 0.78)";
  if (pct < -0.15) return "rgba(150, 48, 56, 0.58)";
  return "rgba(116, 116, 126, 0.34)";
}

function marketHeatMapBucket(pct) {
  const value = Number(pct || 0);
  if (value >= 2.5) return "hp-3";
  if (value >= 1.25) return "hp-2";
  if (value >= 0.25) return "hp-1";
  if (value > 0.05) return "hp-0";
  if (value <= -2.5) return "hn-3";
  if (value <= -1.25) return "hn-2";
  if (value <= -0.25) return "hn-1";
  if (value < -0.05) return "hn-0";
  return "hz";
}

function marketHeatMapInitials(name = "", symbol = "") {
  const words = String(name || symbol).replace(/[^a-z0-9\s]/gi, " ").trim().split(/\s+/).filter(Boolean);
  const initials = words.slice(0, 2).map((word) => word[0]).join("");
  return (initials || String(symbol).slice(0, 2) || "?").toUpperCase();
}

function canonicalSectorKey(value = "") {
  return String(value || "other").toLowerCase().replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "other";
}

function fallbackMarketHeatMapPayload(market = "india", period = "1D") {
  const watchlistTiles = (state.dashboard?.watchlist || []).slice(0, 18).map((item, index) => ({
    symbol: item.symbol,
    name: item.name || item.symbol,
    sector: item.exchange || market,
    sectorKey: canonicalSectorKey(item.exchange || market),
    sizeBucket: index < 6 ? "mega" : "large",
    changePct: Number(item.changePercent || 0),
    span: index < 3 ? 2 : 1,
    quality: item.dataSourceType === "live" || /live|google|yahoo/i.test(item.dataSource || "") ? "live" : "proxy",
    source: item.dataSource || "Dashboard watchlist fallback",
    rank: index + 1,
  }));
  const sectorTiles = (state.sectorStripSectors || []).slice(0, 16).map((item) => ({
    symbol: item.symbol || item.label || item.name || "SECTOR",
    name: item.name || item.label || item.symbol || "Sector",
    sector: item.sector || item.label || market,
    sectorKey: canonicalSectorKey(item.sector || item.label || market),
    sizeBucket: "mega",
    changePct: Number(item.changePct ?? item.changePercent ?? item.change ?? 0),
    span: 2,
    quality: "proxy",
    source: item.source || "Sector strip fallback",
    rank: 999,
  }));
  const tiles = [...watchlistTiles, ...sectorTiles].filter((tile) => tile.symbol);
  if (!tiles.length) return null;
  return {
    market,
    period,
    periodLabel: period === "1D" ? "1 day" : period,
    updatedAt: new Date().toISOString(),
    tiles,
    liveCount: tiles.filter((tile) => tile.quality === "live").length,
    proxyCount: tiles.filter((tile) => tile.quality !== "live").length,
    sectorGroups: buildClientMarketHeatMapSectorGroups(tiles),
    sourceNote: "Frontend fallback from loaded watchlist and sector strip while the market-map endpoint recovers.",
  };
}

function marketHeatMapSizeLabel(size = "") {
  return ({
    mega: "Top 100",
    large: "101-250",
    mid: "251-750",
    small: "751+",
  })[String(size || "").toLowerCase()] || "Unranked";
}

function marketHeatMapScopeLabel(scope = "") {
  return ({
    top100: "Top 100",
    top250: "Top 250",
    top750: "Top 750",
    all: "All listed",
  })[String(scope || "").toLowerCase()] || "Top 250";
}

function marketHeatMapGroupLabel(key, groupBy) {
  if (groupBy === "size") return marketHeatMapSizeLabel(key);
  return String(key || "Other").replace(/-/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function groupMarketHeatMapTiles(tiles, groupBy) {
  if (groupBy === "flat") return [{ key: "all", label: "All listed", tiles }];
  const groups = new Map();
  tiles.forEach((tile) => {
    const key = groupBy === "size" ? (tile.sizeBucket || "other") : (tile.sectorKey || tile.sector || "other");
    if (!groups.has(key)) {
      groups.set(key, { key, label: marketHeatMapGroupLabel(key, groupBy), tiles: [] });
    }
    groups.get(key).tiles.push(tile);
  });
  return Array.from(groups.values()).sort((a, b) => b.tiles.length - a.tiles.length || a.label.localeCompare(b.label));
}

function buildClientMarketHeatMapSectorGroups(tiles = []) {
  const groups = new Map();
  tiles.forEach((tile) => {
    const key = tile.sectorKey || canonicalSectorKey(tile.sector || "Other");
    if (!groups.has(key)) {
      groups.set(key, {
        key,
        label: marketHeatMapGroupLabel(key, "sector"),
        count: 0,
        liveCount: 0,
        proxyCount: 0,
        avgChangePct: 0,
        companies: [],
      });
    }
    const group = groups.get(key);
    group.count += 1;
    if (tile.quality === "live") group.liveCount += 1;
    else group.proxyCount += 1;
    group.companies.push(tile);
  });
  return Array.from(groups.values()).map((group) => {
    const changes = group.companies.map((item) => Number(item.changePct || 0)).filter(Number.isFinite);
    return {
      ...group,
      avgChangePct: changes.length ? changes.reduce((sum, value) => sum + value, 0) / changes.length : 0,
      companies: [...group.companies].sort((a, b) => Number(a.rank || 999999) - Number(b.rank || 999999)),
    };
  });
}

function marketHeatMapSectorDetail(group, payload = state.marketHeatMap) {
  const companies = (payload?.sectorGroups || buildClientMarketHeatMapSectorGroups(payload?.tiles || []))
    .find((item) => item.key === group.key)?.companies || group.tiles || [];
  if (!companies.length) return "";
  const rows = companies.slice(0, 180).map((company) => {
    const pct = Number(company.changePct || 0);
    const direction = pct > 0.15 ? "up" : pct < -0.15 ? "down" : "flat";
    const sourceLabel = company.quality === "live" ? "Live" : "Proxy";
    return `
      <tr data-symbol="${escapeHtml(company.symbol || "")}">
        <td><b>${escapeHtml(String(company.symbol || "").replace(/\.(NS|BO)$/i, ""))}</b><span>${escapeHtml(company.name || company.symbol || "")}</span></td>
        <td>${escapeHtml(marketHeatMapSizeLabel(company.sizeBucket))}</td>
        <td>${company.price == null ? "n/a" : formatCurrency(company.price, payload?.market === "india" ? "INR" : "USD")}</td>
        <td class="${direction}">${formatPercent(pct)}</td>
        <td>${sourceLabel}</td>
      </tr>
    `;
  }).join("");
  const omitted = companies.length > 180 ? `<p>${companies.length - 180} more rows are kept in the local heatmap payload for this view.</p>` : "";
  return `
    <div class="market-heat-sector-detail">
      <div class="market-heat-sector-summary">
        <span>${escapeHtml(marketHeatMapScopeLabel(payload?.filters?.scope))}</span>
        <strong>${escapeHtml(group.label)} · ${companies.length} companies</strong>
        <em>${formatPercent(group.avgChangePct || 0)} avg · ${group.liveCount || 0} live / ${group.proxyCount || 0} proxy</em>
      </div>
      <div class="market-heat-table-wrap">
        <table class="market-heat-company-table">
          <thead><tr><th>Company</th><th>Scope</th><th>Price</th><th>Move</th><th>Source</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      ${omitted}
    </div>
  `;
}

function syncMarketHeatMapSectorOptions(payload) {
  const select = document.getElementById("market-heat-map-sector");
  if (!select || !Array.isArray(payload?.sectors)) return;
  const current = select.value || "all";
  const options = [
    `<option value="all">All sectors</option>`,
    ...payload.sectors.map((item) => `<option value="${escapeHtml(item.key)}">${escapeHtml(item.label)} (${item.count})</option>`),
  ].join("");
  if (setHTMLIfChanged(select, options)) {
    select.value = payload.sectors.some((item) => item.key === current) ? current : "all";
  }
}

function scheduleHeatMapHistoryWarmup(payload) {
  const panel = document.getElementById("market-heat-map-panel");
  const rect = panel?.getBoundingClientRect();
  const nearViewport = Boolean(rect && rect.top <= window.innerHeight + 320 && rect.bottom >= -320);
  if (!nearViewport) {
    state.pendingHeatMapWarmup = payload;
    return;
  }
  state.pendingHeatMapWarmup = null;
  const symbols = (payload?.warmupSymbols || payload?.tiles?.map((tile) => tile.symbol) || [])
    .filter(Boolean)
    .slice(0, 160);
  if (!symbols.length) return;
  const ranges = ["1D", "5D", "1M"];
  const key = `heat-map:${symbols.join(",")}::${ranges.join(",")}`;
  if (state.historyWarmupKeys.has(key)) return;
  state.historyWarmupKeys.add(key);
  const run = () => {
    api("/api/history/warm", {
      method: "POST",
      timeoutMs: 6000,
      body: JSON.stringify({ symbols, ranges }),
    }).then(() => {
      scheduleHistoryProgressPoll(750);
      pollHistoryProgress();
    }).catch((error) => {
      state.historyWarmupKeys.delete(key);
      logNonAbort(error);
    });
  };
  if ("requestIdleCallback" in window) {
    window.requestIdleCallback(run, { timeout: 4000 });
  } else {
    window.setTimeout(run, 1200);
  }
}

function renderMarketHeatMap(payload = state.marketHeatMap) {
  // Legacy grouped heatmap hooks remain available for contracts:
  // market-heat-group / data-heat-open-group / marketHeatMapSectorDetail.
  const grid = document.getElementById("market-heat-map-grid");
  const footer = document.getElementById("market-heat-map-footer");
  if (!grid) return;
  syncMarketHeatMapSectorOptions(payload);
  const tiles = payload?.tiles || [];
  if (!tiles.length) {
    setHTMLIfChanged(grid, `<div class="market-heat-map-empty">Fetching market map…</div>`);
    if (footer) footer.textContent = "Using local universe manifests and live edge quotes where available.";
    return;
  }
  const visibleTiles = tiles.slice(0, 40);
  const markup = `
    <div class="heatmap">
      ${visibleTiles.map((tile) => {
        const pct = Number(tile.changePct || 0);
        const title = `${tile.symbol} · ${tile.name} · ${formatPercent(pct)} · ${tile.source || (tile.quality === "live" ? "Live" : "Proxy")}`;
        const symbolLabel = escapeHtml(String(tile.symbol || "").replace(/\.(NS|BO)$/i, ""));
        return `
          <button class="heat market-heat-tile ${marketHeatMapBucket(pct)} ${tile.quality === "live" ? "is-live" : "is-proxy"}"
            type="button"
            data-symbol="${escapeHtml(tile.symbol || "")}"
            title="${escapeHtml(title)}">
            <div class="hs">${symbolLabel}</div>
            <div class="hc">${formatPercent(pct)}</div>
          </button>
        `;
      }).join("")}
    </div>
  `;
  setHTMLIfChanged(grid, markup);
  if (footer) {
    const age = payload.updatedAt ? Math.max(0, Math.round((Date.now() - new Date(payload.updatedAt).getTime()) / 60000)) : 0;
    const scopeLabel = marketHeatMapScopeLabel(payload.filters?.scope);
    const coverage = payload.universeCount ? `${payload.returnedCount || tiles.length}/${payload.filteredCount || payload.scopeCount || payload.universeCount} shown from ${scopeLabel.toLowerCase()} (${payload.universeCount} listed)` : `${tiles.length} tiles`;
    footer.textContent = `${payload.periodLabel || payload.period || "Selected period"} · ${coverage} · ${payload.liveCount || 0} live quote tiles · ${payload.proxyCount || 0} proxy tiles · local snapshot ${payload.cacheState || "fresh"} · ${payload.sourceNote || "Tile size is a display proxy."} · updated ${age < 1 ? "just now" : `${age}m ago`}`;
  }
}

async function fetchMarketHeatMap(market, period, options = {}) {
  const requestId = ++state.marketHeatMapRequestId;
  renderMarketHeatMap();
  try {
    const params = new URLSearchParams({
      market,
      period,
      limit: options.limit || (market === "us" ? "240" : "240"),
      sector: options.sector || "all",
      size: options.size || "all",
      sort: options.group === "sector" ? "sector" : "rank",
      scope: options.scope || "top250",
    });
    const payload = await api(`/api/market-map?${params.toString()}`, { timeoutMs: 30000 });
    if (requestId !== state.marketHeatMapRequestId) return;
    state.marketHeatMap = payload;
    renderMarketHeatMap(payload);
    scheduleHeatMapHistoryWarmup(payload);
  } catch (error) {
    logNonAbort(error);
    const fallback = fallbackMarketHeatMapPayload(market, period);
    if (fallback) {
      state.marketHeatMap = fallback;
      renderMarketHeatMap(fallback);
      return;
    }
    const grid = document.getElementById("market-heat-map-grid");
    const footer = document.getElementById("market-heat-map-footer");
    if (grid) setHTMLIfChanged(grid, `<div class="market-heat-map-empty">Market heat map unavailable. Existing dashboard panels are still active.</div>`);
    if (footer) footer.textContent = "Heat map uses an additive endpoint, so failures do not block the rest of the dashboard.";
  }
}

function initMarketHeatMap() {
  const panel = document.getElementById("market-heat-map-panel");
  const regionSelect = document.getElementById("market-heat-map-region");
  const groupSelect = document.getElementById("market-heat-map-group");
  const sectorSelect = document.getElementById("market-heat-map-sector");
  const scopeSelect = document.getElementById("market-heat-map-scope");
  const sizeSelect = document.getElementById("market-heat-map-size");
  const limitSelect = document.getElementById("market-heat-map-limit");
  const expandButton = document.getElementById("market-heat-map-expand");
  const grid = document.getElementById("market-heat-map-grid");
  const periodTabs = document.querySelectorAll(".market-heat-map-tab[data-period]");
  if (!panel || !regionSelect) return;
  const prefs = loadMarketHeatMapPrefs();
  let market = prefs.market || state.selectedRegion || "india";
  if (!["india", "us"].includes(market)) market = "india";
  let period = prefs.period || "1D";
  let group = prefs.group || "sector";
  let sector = prefs.sector || "all";
  let scope = prefs.scope || "top250";
  let size = prefs.size || "all";
  let limit = prefs.limit || "240";
  let expanded = Boolean(prefs.expanded);
  regionSelect.value = market;
  if (groupSelect) groupSelect.value = group;
  if (sectorSelect) sectorSelect.value = sector;
  if (scopeSelect) scopeSelect.value = scope;
  if (sizeSelect) sizeSelect.value = size;
  if (limitSelect) limitSelect.value = limit;
  panel.classList.toggle("is-expanded", expanded);
  expandButton?.setAttribute("aria-pressed", expanded ? "true" : "false");
  if (expandButton) setTextIfChanged(expandButton, expanded ? "Collapse" : "Expand");
  periodTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.period === period));
  const persistAndFetch = () => {
    const openGroup = loadMarketHeatMapPrefs().openGroup || "";
    saveMarketHeatMapPrefs({ market, period, group, sector, scope, size, limit, expanded, openGroup });
    fetchMarketHeatMap(market, period, { group, sector, scope, size, limit });
  };
  regionSelect.addEventListener("change", () => {
    market = regionSelect.value;
    sector = "all";
    if (sectorSelect) sectorSelect.value = "all";
    scope = market === "india" ? "top250" : "top250";
    if (scopeSelect) scopeSelect.value = scope;
    limit = market === "india" ? "240" : "240";
    persistAndFetch();
  });
  groupSelect?.addEventListener("change", () => {
    group = groupSelect.value || "sector";
    saveMarketHeatMapPrefs({ ...loadMarketHeatMapPrefs(), market, period, group, sector, scope, size, limit, expanded });
    renderMarketHeatMap();
    fetchMarketHeatMap(market, period, { group, sector, scope, size, limit });
  });
  sectorSelect?.addEventListener("change", () => {
    sector = sectorSelect.value || "all";
    saveMarketHeatMapPrefs({ ...loadMarketHeatMapPrefs(), openGroup: sector === "all" ? "" : sector });
    persistAndFetch();
  });
  scopeSelect?.addEventListener("change", () => {
    scope = scopeSelect.value || "top250";
    persistAndFetch();
  });
  sizeSelect?.addEventListener("change", () => {
    size = sizeSelect.value || "all";
    persistAndFetch();
  });
  limitSelect?.addEventListener("change", () => {
    limit = limitSelect.value || "240";
    persistAndFetch();
  });
  expandButton?.addEventListener("click", () => {
    expanded = !expanded;
    panel.classList.toggle("is-expanded", expanded);
    expandButton.setAttribute("aria-pressed", expanded ? "true" : "false");
    setTextIfChanged(expandButton, expanded ? "Collapse" : "Expand");
    saveMarketHeatMapPrefs({ ...loadMarketHeatMapPrefs(), market, period, group, sector, scope, size, limit, expanded });
  });
  grid?.addEventListener("click", (event) => {
    const tile = event.target instanceof Element ? event.target.closest("[data-symbol]") : null;
    if (tile?.dataset?.symbol) {
      selectActiveTicker(tile.dataset.symbol);
      return;
    }
    const button = event.target instanceof Element ? event.target.closest("[data-heat-open-group]") : null;
    if (!button) return;
    const openGroup = button.getAttribute("data-heat-open-group") || "";
    const prefsNow = loadMarketHeatMapPrefs();
    const nextOpenGroup = prefsNow.openGroup === openGroup ? "" : openGroup;
    saveMarketHeatMapPrefs({ ...prefsNow, market, period, group, sector, scope, size, limit, expanded, openGroup: nextOpenGroup });
    renderMarketHeatMap();
  });
  periodTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      periodTabs.forEach((item) => item.classList.remove("active"));
      tab.classList.add("active");
      period = tab.dataset.period || "1D";
      persistAndFetch();
    });
  });
  const loadVisibleHeatMap = () => {
    if (panel.dataset.marketMapLoaded === "1") {
      if (state.pendingHeatMapWarmup) scheduleHeatMapHistoryWarmup(state.pendingHeatMapWarmup);
      return;
    }
    panel.dataset.marketMapLoaded = "1";
    persistAndFetch();
  };
  if ("IntersectionObserver" in window) {
    state.marketHeatMapObserver?.disconnect();
    state.marketHeatMapObserver = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      loadVisibleHeatMap();
      state.marketHeatMapObserver?.disconnect();
      state.marketHeatMapObserver = null;
    }, { rootMargin: "320px 0px" });
    state.marketHeatMapObserver.observe(panel);
  } else {
    loadVisibleHeatMap();
  }
}

function renderSectorMatrix(sectors, updatedAt, meta = {}) {
  const grid = document.getElementById("sector-matrix-grid");
  const footer = document.getElementById("sector-matrix-updated");
  if (!grid) return;
  if (!sectors?.length) {
    grid.innerHTML = `<div class="sector-matrix-empty">Loading sector data…</div>`;
    return;
  }
  const sorted = [...sectors].sort((a, b) => {
    const aUnavailable = isUnavailableSector(a);
    const bUnavailable = isUnavailableSector(b);
    if (aUnavailable !== bUnavailable) return aUnavailable ? 1 : -1;
    return Number(b.changePct || 0) - Number(a.changePct || 0);
  });
  setHTMLIfChanged(grid, sorted.map((s) => {
    const unavailable = isUnavailableSector(s);
    const pct = Number(s.changePct || 0);
    const relativePct = Number(s.relativePct || 0);
    const color = unavailable ? "rgba(255,255,255,0.08)" : sectorHeatColor(pct);
    const sign = pct >= 0 ? "+" : "";
    const relativeSign = relativePct >= 0 ? "+" : "";
    const pctLabel = unavailable ? "Data pending" : `${sign}${pct.toFixed(2)}%`;
    const relativeLabel = unavailable ? "Awaiting live print" : `${relativeSign}${relativePct.toFixed(2)}%`;
    const intensity = unavailable ? 0.18 : Math.min(Math.abs(pct) / 3, 1);
    return `
      <article class="sector-tile ${unavailable ? "is-pending" : ""}" style="--heat:${color}; --intensity:${intensity.toFixed(2)}" title="${s.label}: ${pctLabel}">
        <div class="sector-tile-top">
          <span class="sector-tile-label">${s.label}</span>
          <strong class="sector-tile-pct ${unavailable ? "pending" : pct >= 0 ? "positive" : "negative"}">${pctLabel}</strong>
        </div>
        <div class="sector-tile-relative">
          <span>vs ${meta.benchmark?.label || "benchmark"}</span>
          <strong class="${unavailable ? "pending" : relativePct >= 0 ? "positive" : "negative"}">${relativeLabel}</strong>
        </div>
        <div class="sector-tile-meta">
          <span>${s.source || meta.source || "market data"}</span>
          ${!unavailable && s.price ? `<em class="sector-tile-price">${s.price.toLocaleString()}</em>` : ""}
        </div>
      </article>
    `;
  }).join(""));
  if (footer && updatedAt) {
    const age = Math.round((Date.now() - new Date(updatedAt).getTime()) / 60000);
    const benchmark = meta.benchmark ? `${meta.benchmark.label} ${formatPercent(meta.benchmark.changePct || 0)}` : "selected benchmark";
    const mode = meta.liveMode ? "live refresh" : (meta.cacheState || "cache");
    footer.textContent = `${meta.periodLabel || "Selected period"} · ${benchmark} · ${mode} · updated ${age < 1 ? "just now" : `${age}m ago`}`;
  }
}

async function fetchSectorMatrix(market, period, benchmark, { showLoading = true } = {}) {
  const grid = document.getElementById("sector-matrix-grid");
  const hasExistingTiles = Boolean(grid?.querySelector(".sector-tile"));
  if (grid && showLoading && !hasExistingTiles) {
    setHTMLIfChanged(grid, `<div class="sector-matrix-empty">Fetching ${market} sectors...</div>`);
  }
  try {
    const params = new URLSearchParams({ market, period, benchmark });
    const data = await api(`/api/sectors?${params.toString()}`, { timeoutMs: 12000 });
    if (data?.sectors?.length) {
      if (hasUsableSectorData(data.sectors)) {
        saveSectorHistory(market, period, benchmark, data.sectors, data);
      }
      renderSectorMatrix(data.sectors, data.updatedAt, data);
      if (market === "india" && period === "1D") renderSectorStrip(data.sectors);
    }
  } catch {
    // Fall back to last cached local history snapshot
    const snap = loadSectorSnapshot(market, period, benchmark);
    if (snap?.sectors && hasUsableSectorData(snap.sectors)) {
      renderSectorMatrix(snap.sectors, new Date(snap.ts).toISOString(), { ...(snap.meta || {}), cacheState: "local fallback" });
    } else if (grid) {
      grid.innerHTML = `<div class="sector-matrix-empty">Sector data unavailable. Server may still be starting.</div>`;
    }
  }
}

function initSectorMatrix() {
  const marketSelect = document.getElementById("sector-matrix-market");
  const benchmarkSelect = document.getElementById("sector-matrix-benchmark");
  const periodTabs = document.querySelectorAll(".sector-period-tab");
  if (!marketSelect) return;

  const prefs = loadSectorMatrixPrefs();
  let currentMarket = prefs.market || marketSelect.value || "india";
  let currentPeriod = prefs.period || "1D";
  let currentBenchmark = prefs.benchmark || SECTOR_BENCHMARK_OPTIONS[currentMarket]?.[0]?.[0] || "^NSEI";
  const syncBenchmarkOptions = () => {
    if (!benchmarkSelect) return;
    const options = SECTOR_BENCHMARK_OPTIONS[currentMarket] || SECTOR_BENCHMARK_OPTIONS.india;
    benchmarkSelect.innerHTML = options.map(([value, label]) => `<option value="${value}">${label}</option>`).join("");
    if (!options.some(([value]) => value === currentBenchmark)) {
      currentBenchmark = options[0][0];
    }
    benchmarkSelect.value = currentBenchmark;
  };
  const persist = () => saveSectorMatrixPrefs({ market: currentMarket, period: currentPeriod, benchmark: currentBenchmark });
  const refreshCurrent = (options = {}) => fetchSectorMatrix(currentMarket, currentPeriod, currentBenchmark, options);
  marketSelect.value = currentMarket;
  syncBenchmarkOptions();
  periodTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.period === currentPeriod));

  // Show last local snapshot immediately while fetching
  const cachedSnap = loadSectorSnapshot(currentMarket, currentPeriod, currentBenchmark);
  if (cachedSnap?.sectors && hasUsableSectorData(cachedSnap.sectors)) renderSectorMatrix(cachedSnap.sectors, new Date(cachedSnap.ts).toISOString(), cachedSnap.meta || {});

  refreshCurrent();

  window.clearInterval(state.sectorMatrixTimer);
  state.sectorMatrixTimer = window.setInterval(() => {
    if (currentPeriod !== "1D" || document.hidden) return;
    refreshCurrent({ showLoading: false }).catch((error) => {
      logNonAbort(error);
    });
  }, REFRESH_INTERVALS.sectorsLive);

  marketSelect.addEventListener("change", () => {
    currentMarket = marketSelect.value;
    syncBenchmarkOptions();
    persist();
    const snap = loadSectorSnapshot(currentMarket, currentPeriod, currentBenchmark);
    if (snap?.sectors && hasUsableSectorData(snap.sectors)) renderSectorMatrix(snap.sectors, new Date(snap.ts).toISOString(), snap.meta || {});
    refreshCurrent();
  });
  benchmarkSelect?.addEventListener("change", () => {
    currentBenchmark = benchmarkSelect.value;
    persist();
    const snap = loadSectorSnapshot(currentMarket, currentPeriod, currentBenchmark);
    if (snap?.sectors && hasUsableSectorData(snap.sectors)) renderSectorMatrix(snap.sectors, new Date(snap.ts).toISOString(), snap.meta || {});
    refreshCurrent();
  });

  periodTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      periodTabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      currentPeriod = tab.dataset.period;
      persist();
      const snap = loadSectorSnapshot(currentMarket, currentPeriod, currentBenchmark);
      if (snap?.sectors && hasUsableSectorData(snap.sectors)) renderSectorMatrix(snap.sectors, new Date(snap.ts).toISOString(), snap.meta || {});
      refreshCurrent();
    });
  });
}

// ── Sector Overview Strip — compact always-visible row above tabbar ──────────
function renderSectorStrip(sectors) {
  const strip = document.getElementById("sector-overview-strip");
  if (!Array.isArray(sectors) || !sectors.length) return;
  state.sectorStripSectors = sectors;
  if (strip) setHTMLIfChanged(strip, sectorStripMarkup(sectors));
}

function initSectorStrip() {
  // Show cached immediately
  const cached = loadSectorSnapshot("india", "1D", "^NSEI");
  if (cached?.sectors && hasUsableSectorData(cached.sectors)) renderSectorStrip(cached.sectors);

  // Fetch fresh — reuse the same endpoint as the matrix
  api("/api/sectors?market=india&period=1D").then((data) => {
    if (data?.sectors) renderSectorStrip(data.sectors);
  }).catch(() => {});

  // Refresh every 5 min
  window.setInterval(() => {
    api("/api/sectors?market=india&period=1D").then((data) => {
      if (data?.sectors) renderSectorStrip(data.sectors);
    }).catch(() => {});
  }, 5 * 60 * 1000);
}
// ─────────────────────────────────────────────────────────────────────────────

function bindEvents() {
  const labTickerInput = document.getElementById("lab-ticker");
  if (labTickerInput && !labTickerInput.value.trim()) {
    labTickerInput.value = state.activeTicker;
  }

  document.getElementById("ticker-form").addEventListener("submit", (event) => {
    event.preventDefault();
    addTickerFromInput();
  });

  document.getElementById("ticker-input").addEventListener("input", () => {
    window.clearTimeout(bindEvents.searchTimer);
    bindEvents.searchTimer = window.setTimeout(runSearch, 260);
  });

  document.querySelectorAll(".range-tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.chartRange = button.dataset.range;
      persistWatchlist();
      scheduleHistoryWarmup({ immediate: true });
      refreshDashboard();
    });
  });

  document.querySelectorAll(".chart-mode-tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.chartFeatures.chartType = button.dataset.chartType || "line";
      persistWatchlist();
      renderHeroChartOnly();
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
      renderHeroChartOnly();
    });
  });

  document.querySelectorAll(".event-chip").forEach((button) => {
    button.addEventListener("click", async () => {
      state.eventCategoryPinned = true;
      state.eventCategory = button.dataset.category;
      state.eventLastQuery = "";
      persistWatchlist();
      await loadEventFeed();
      renderEventFeed();
      renderMacroEvents();
      flashStatus("Feed ready", 1000);
    });
  });

  document.getElementById("event-search-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const keyword = document.getElementById("event-search-input")?.value.trim();
    if (keyword) { await loadEventFeed(keyword); renderEventFeed(); renderMacroEvents(); flashStatus("Feed ready", 1000); }
  });

  document.querySelectorAll(".tab").forEach((tab) => {
    if (!tab.dataset.tab) return;
    tab.addEventListener("click", () => {
      activateTab(tab.dataset.tab);
    });
  });
  document.querySelectorAll(".topnav-link").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      activateTab(button.dataset.target);
    });
    button.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const tabs = Array.from(document.querySelectorAll(".topnav-link"));
      const currentIndex = tabs.indexOf(button);
      const nextIndex = event.key === "Home"
        ? 0
        : event.key === "End"
          ? tabs.length - 1
          : (currentIndex + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
      const next = tabs[nextIndex];
      activateTab(next.dataset.target);
      next.focus();
    });
  });
  document.getElementById("mobile-sidebar-toggle")?.addEventListener("click", () => {
    const sidebar = document.querySelector(".sidebar");
    const toggle = document.getElementById("mobile-sidebar-toggle");
    const open = !sidebar?.classList.contains("mobile-open");
    sidebar?.classList.toggle("mobile-open", open);
    toggle?.setAttribute("aria-expanded", open ? "true" : "false");
    setTextIfChanged(toggle, open ? "Close watchlist" : "Watchlist");
  });
  document.getElementById("top-ticker-form")?.addEventListener("submit", (event) => {
    event.preventDefault();
    const topInput = document.getElementById("top-ticker-input");
    const sidebarInput = document.getElementById("ticker-input");
    if (topInput && sidebarInput) {
      sidebarInput.value = topInput.value;
    }
    addTickerFromInput();
  });
  document.getElementById("toggle-detail-mode")?.addEventListener("click", () => {
    setDetailMode(!state.detailMode);
  });
  document.getElementById("compact-menu-toggle")?.addEventListener("click", () => {
    const menu = document.getElementById("compact-section-menu");
    const isOpen = !menu?.classList.contains("open");
    menu?.classList.toggle("open", isOpen);
    document.getElementById("compact-menu-toggle")?.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });
  window.addEventListener("resize", () => {
    scheduleDossierMasonry();
    if (!state.impactGraphCy) return;
    window.clearTimeout(state.impactResizeTimer);
    state.impactResizeTimer = window.setTimeout(() => {
      relayoutImpactGraph();
    }, 120);
  }, { passive: true });

  const settingsDialog = document.getElementById("settings-dialog");
  document.querySelectorAll("#open-settings, .open-settings-trigger").forEach((button) => {
    button.addEventListener("click", () => settingsDialog.showModal());
  });
  document.getElementById("toggle-market-board")?.addEventListener("click", () => {
    state.boardHidden = !state.boardHidden;
    persistWatchlist();
    renderBoard();
  });
  document.getElementById("impact-fit")?.addEventListener("click", () => state.impactGraphCy?.fit(state.impactGraphCy.elements(), 28));
  document.getElementById("impact-reset")?.addEventListener("click", () => {
    relayoutImpactGraph();
  });
  document.getElementById("impact-zoom-in")?.addEventListener("click", () => {
    if (!state.impactGraphCy) return;
    state.impactGraphCy.zoom({
      level: Math.min(3, state.impactGraphCy.zoom() * 1.18),
      renderedPosition: { x: state.impactGraphCy.width() / 2, y: state.impactGraphCy.height() / 2 },
    });
  });
  document.getElementById("impact-zoom-out")?.addEventListener("click", () => {
    if (!state.impactGraphCy) return;
    state.impactGraphCy.zoom({
      level: Math.max(0.25, state.impactGraphCy.zoom() / 1.18),
      renderedPosition: { x: state.impactGraphCy.width() / 2, y: state.impactGraphCy.height() / 2 },
    });
  });
  document.getElementById("save-settings").addEventListener("click", async (event) => {
    event.preventDefault();
    setStatus("Saving config");
    const alphaVantageApiKey = document.getElementById("alpha-key").value.trim();
    const fredApiKey = document.getElementById("fred-key").value.trim();
    const payload = {
      provider: document.getElementById("provider-select").value,
      localLlmBaseUrl: document.getElementById("llm-base-url").value.trim(),
      localLlmModel: document.getElementById("llm-model").value.trim(),
    };
    if (alphaVantageApiKey) payload.alphaVantageApiKey = alphaVantageApiKey;
    if (fredApiKey) payload.fredApiKey = fredApiKey;
    state.config = await api("/api/config", {
      method: "POST",
      body: JSON.stringify(payload),
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

  const labForm = document.getElementById("lab-form");
  if (labForm) {
    labForm.addEventListener("submit", async (event) => {
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
      // Added to recent after dashboard confirms resolution
      persistWatchlist();
      document.querySelector('[data-tab="lab"]')?.click();
      renderLab();
      primeActiveTickerSelection(payload.symbol);
      renderOverview();
      refreshDashboard().catch((error) => {
        logNonAbort(error);
      });
      flashStatus("Lab ready", 1200);
    });
  }

  const researchForm = document.getElementById("research-form");
  if (researchForm) {
    researchForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const query = document.getElementById("research-query").value.trim();
      if (!query) return;
      setStatus("Thinking");
      state.researchLoading = true;
      state.researchError = "";
      document.querySelector('[data-tab="research"]')?.click();
      renderResearch();
      try {
        const payload = await api("/api/research", {
          method: "POST",
          timeoutMs: 12000,
          body: JSON.stringify({
            query,
            symbol: state.activeTicker,
            useWeb: document.getElementById("research-use-web").checked,
            useLlm: document.getElementById("research-use-llm").checked,
          }),
        });
        state.researchResult = payload;
        flashStatus("Answer ready", 1600);
      } catch (error) {
        state.researchError = "The research workspace took too long. Try again, or disable local LLM for a faster web-grounded answer.";
      } finally {
        state.researchLoading = false;
        renderResearch();
      }
    });
  }
}

async function init() {
  initBrandIntro();
  document.body.classList.add("app-booting");
  initSkeletons();
  setStatus("Loading data");
  bindNotificationBell();
  renderDataFlowBar();
  pollHistoryProgress();
  initStarfieldParallax();
  bindEvents();
  initSectorMatrix();
  initSectorStrip();
  initMarketHeatMap();
  const cachedDashboard = loadDashboardCache();
  if (cachedDashboard && hydrateDashboardFromPayload(cachedDashboard, { fromCache: true })) {
    markDashboardInteractive("Cached dashboard");
  }
  render();
  startMarketClockTimer();
  startOverviewRefresh();
  startQuotesRefresh();
  startGlobalMarketsRefresh();
  loadGlobalMarkets({ silent: true }).catch((error) => {
    logNonAbort(error);
  });
  loadOverviewFast({ silent: true }).catch((error) => {
    logNonAbort(error);
  });
  loadRadar({ silent: true }).catch((error) => {
    logNonAbort(error);
  });
  const dashboardPromise = refreshDashboard({ primeFast: false, primeRadar: false });
  const backgroundLoads = Promise.allSettled([loadConfig(), loadPresets(), loadSavedWatchlists()]);
  dashboardPromise.catch((error) => {
    logNonAbort(error);
    state.dataFlow.lastError = state.dataFlow.lastError || "Dashboard refresh failed";
    renderDataFlowBar();
    setStatus("Backend slow");
    if (!state.bootReady) {
      setBootMessage("Dashboard API is reachable, but the first full refresh is taking longer than usual.");
    }
  });
  startRadarRefresh();
  backgroundLoads.then(() => {
    flashStatus("Workspace ready", 1200);
  });
  startDashboardRefresh();
  startEventRefresh();
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) return;
    loadQuotesFast().catch(logNonAbort);
    loadOverviewFast({ silent: true }).catch(logNonAbort);
    loadGlobalMarkets({ silent: true }).catch(logNonAbort);
  });
}

init().catch((error) => {
  logNonAbort(error);
  setStatus("Backend check failed");
  setBootMessage("Backend check failed.", `Open ${API_BASE || window.location.origin || "http://127.0.0.1:8000"} and refresh once the server is running.`);
});
