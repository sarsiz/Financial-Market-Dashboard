const STORAGE_KEYS = {
  watchlist: "financial-board-fullstack-watchlist",
  activeTicker: "financial-board-fullstack-active",
  recentTickers: "financial-board-recent-tickers",
  chartRange: "financial-board-chart-range",
  chartFeatures: "financial-board-chart-features",
  eventCategory: "financial-board-event-category",
  boardHidden: "financial-board-market-board-hidden",
  benchmarksCollapsed: "financial-board-benchmarks-collapsed",
  region: "financial-board-region",
  dossierOrder: "financial-board-dossier-order",
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

const DEFAULT_DOSSIER_ORDER = [
  "day",
  "fundamentals",
  "ma",
  "consensus",
  "activity",
  "peers",
  "benchmarks",
  "links",
  "metrics",
];

const state = {
  watchlist: loadStoredWatchlist(),
  activeTicker: localStorage.getItem(STORAGE_KEYS.activeTicker) || "BHARTIARTL.NS",
  selectedRegion: localStorage.getItem(STORAGE_KEYS.region) || "india",
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
  marketClockTimer: null,
  researchResult: null,
  researchLoading: false,
  researchError: "",
  quoteStream: null,
  eventRequestId: 0,
  eventTimer: null,
  eventCache: {},
  eventLastQuery: "",
  liveQuoteMemory: {},
  alerts: [],
  alertCooldowns: {},
  radarFloatOpenId: "",
  radarHeadlineDetail: null,
  radarFloatPositions: {},
  radarDismissedFloatIds: [],
  radarFloatDrag: null,
  marketSessionTimer: null,
  dashboardRequestId: 0,
  overviewRequestId: 0,
  academyRequestId: 0,
  radarRequestId: 0,
  academyDetail: null,
  academyCache: {},
  bootReady: false,
  radarTimer: null,
  radarGlobalPointerCleanupBound: false,
  boardHidden: localStorage.getItem(STORAGE_KEYS.boardHidden) === "1",
  benchmarksCollapsed: localStorage.getItem(STORAGE_KEYS.benchmarksCollapsed) === "1",
  radarFloatsCollapsed: false,
  eventCategoryPinned: false,
  recentLastAdded: "",
  recentAddTimer: null,
  radarFreshFloatIds: [],
  visualValueMemory: {},
  impactGraphPositions: {},
  impactGraphCy: null,
  impactResizeTimer: null,
  revealObserver: null,
  lastOverviewChartRefreshAt: 0,
  historyWarmupKeys: new Set(),
  dossierOrder: loadStoredDossierOrder(),
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

function loadStoredDossierOrder() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEYS.dossierOrder) || "[]");
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

function setupScrollReveal() {
  if (state.revealObserver) {
    state.revealObserver.disconnect();
  }
  state.revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("revealed");
        }
      });
    },
    { threshold: 0.12 },
  );
  document.querySelectorAll(".glass-panel, .macro-panel, .event-card, .factor-card, .catalyst-card, .pulse-card").forEach((node) => {
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
  try {
    response = await fetch(url, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      signal: controller.signal,
      ...options,
    });
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
}

function liveValueClass(key, value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "";
  const previous = Number(state.visualValueMemory[key]);
  state.visualValueMemory[key] = numeric;
  if (!Number.isFinite(previous) || previous === numeric) return "";
  return numeric > previous ? "flash-up" : "flash-down";
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

function renderOverviewLowerPanels(active, forecast) {
  const seenContextLabels = new Set();
  const macroMicroContext = []
    .concat(state.dashboard?.radar?.macroFactors || [])
    .concat(state.dashboard?.radar?.microFactors || [])
    .filter((item) => {
      const label = String(item?.label || "").trim();
      if (!label) return false;
      if (/(^|\b)(s&p|nasdaq|dow|nifty|sensex)(\b|$)/i.test(label)) return false;
      const key = label.toLowerCase();
      if (seenContextLabels.has(key)) return false;
      seenContextLabels.add(key);
      return true;
    })
    .slice(0, 4);
  const relationshipCards = active.relationshipCards || forecast.factors || [];
  const factorSchedule = selectedRegionPayload()?.researchProtocol?.factors?.length
    ? (selectedRegionPayload()?.researchProtocol?.factors || []).slice(0, 3)
    : state.dashboard?.selectedRegion
      ? (selectedRegionPayload()?.watchlistImplications?.graph?.factorSchedule || []).slice(0, 3)
      : [];
  const researchOverview = active.researchOverview || {};
  const decisionInputs = active.decisionInputs || {};
  const decisionCockpit = active.decisionCockpit || {};
  const featureCards = active.featureCards || [];
  const movingAverage = forecast.movingAverageSignal || {};
  const ma5Label = Number.isFinite(Number(movingAverage.sma5))
    ? formatCurrency(movingAverage.sma5, active.currency)
    : "n/a";
  const ma25Label = Number.isFinite(Number(movingAverage.sma25))
    ? formatCurrency(movingAverage.sma25, active.currency)
    : "n/a";
  document.getElementById("factor-map").innerHTML = `
    ${decisionCockpit.stance ? `
      <div class="decision-cockpit-card">
        <div class="decision-cockpit-head">
          <div>
            <span>Decision cockpit</span>
            <strong>${decisionCockpit.stance}</strong>
          </div>
          <div class="decision-score-ring" style="--score:${Number(decisionCockpit.edgeScore || 0).toFixed(0)}">
            <b>${Number(decisionCockpit.edgeScore || 0).toFixed(0)}</b>
            <small>edge</small>
          </div>
        </div>
        <div class="decision-cockpit-grid">
          ${(decisionCockpit.facts || []).slice(0, 4).map((item) => `
            <div class="decision-fact">
              <span>${item.label}</span>
              <strong>${item.value}</strong>
              <p>${item.why}</p>
            </div>
          `).join("")}
        </div>
        <div class="decision-brief-lines">
          ${(decisionCockpit.interpretation || []).slice(0, 2).map((item) => `<p>${item}</p>`).join("")}
        </div>
        <div class="decision-monitor-row">
          ${(decisionCockpit.monitor || []).slice(0, 3).map((item) => `<span>${item}</span>`).join("")}
        </div>
        <small class="decision-source-note">${decisionCockpit.sourceNote || "Scenario support only, not direct investment advice."}</small>
      </div>
    ` : ""}
    ${featureCards.length ? `
      <div class="operator-check-grid">
        ${featureCards.slice(0, 10).map((item) => `
          <div class="operator-check-card">
            <span>${item.label}</span>
            <strong>${item.value}</strong>
            <p>${item.note}</p>
          </div>
        `).join("")}
      </div>
    ` : ""}
    ${movingAverage.state ? `
      <div class="research-overview-hero ma-signal-hero">
        <div class="research-overview-copy">
          <span>5D / 25D trend</span>
          <strong>${movingAverage.state} · ${movingAverage.nextRunBias || "Mixed"}</strong>
        </div>
        <div class="research-overview-monitor">
          <p>5D ${ma5Label} · 25D ${ma25Label}</p>
          <p>Spread ${formatPercent(movingAverage.spreadPercent || 0)} · Confidence ${Number(movingAverage.confidence || 0).toFixed(0)}%</p>
        </div>
      </div>
    ` : ""}
    ${decisionInputs.inputs?.length ? `
      <div class="research-overview-hero">
        <div class="research-overview-copy">
          <span>${decisionInputs.mode || "Decision inputs"}</span>
          <strong>Live calculation inputs for the active market regime.</strong>
        </div>
        <div class="research-overview-monitor">
          ${decisionInputs.inputs.slice(0, 2).map((item) => `<p>${item.label}: ${item.note || item.why}</p>`).join("")}
        </div>
      </div>
      <div class="research-formula-grid decision-input-grid">
        ${decisionInputs.inputs.slice(0, 4).map((item) => `
          <div class="formula-card decision-card">
            <div class="formula-card-head">
              <span>${item.label}</span>
              <strong>${item.value}</strong>
            </div>
            <code>${item.formula}</code>
            <p>${item.why}</p>
            <small>${item.cadence}${item.significance ? ` • ${item.significance}` : ""}${item.sourceLabel ? ` • ${item.sourceLabel}` : ""}</small>
          </div>
        `).join("")}
      </div>
    ` : ""}
    ${researchOverview.headline ? `
      <div class="research-overview-hero">
        <div class="research-overview-copy">
          <span>Research stack</span>
          <strong>${researchOverview.headline}</strong>
        </div>
        <div class="research-overview-monitor">
          ${(researchOverview.nextWatch || []).slice(0, 2).map((item) => `<p>${item}</p>`).join("")}
        </div>
      </div>
    ` : ""}
    ${(researchOverview.cards || []).length ? `
      <div class="research-formula-grid">
        ${(researchOverview.cards || [])
          .slice(0, 4)
          .map(
            (item) => `
              <div class="formula-card">
                <div class="formula-card-head">
                  <span>${item.label}</span>
                  <strong>${item.value}</strong>
                </div>
                <code>${item.formula}</code>
                <p>${item.why}</p>
                <small>${item.note}${item.cadence ? ` • ${item.cadence}` : ""}</small>
              </div>
            `,
          )
          .join("")}
      </div>
    ` : ""}
    ${macroMicroContext.length ? `
      <div class="analysis-context-grid">
        ${macroMicroContext
          .map(
            (item) => `
              <div class="factor-context-card">
                <span>${item.label}</span>
                <strong>${item.value || "Live"}</strong>
                <p>${item.trend || "Current live context."}</p>
              </div>
            `,
          )
          .join("")}
      </div>
    ` : ""}
    ${factorSchedule.length ? `
      <div class="analysis-context-grid factor-cadence-grid">
        ${factorSchedule
          .map(
            (item) => `
              <div class="factor-context-card cadence-card">
                <span>${item.label}</span>
                <strong>${item.cadence}</strong>
                <p>${item.significance} significance • ${item.use || item.why || item.factsFirst}</p>
              </div>
            `,
          )
          .join("")}
      </div>
    ` : ""}
    <div class="analysis-flow-grid">
      ${relationshipCards
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
        .join("")}
    </div>
  `;

  const latestDriverEvents = [...(state.eventResult?.items || state.dashboard?.radar?.items || [])]
    .slice(0, 2)
    .map((item) => ({
      title: item.title || "Live catalyst",
      tag: item.category || "Live",
      meta: `${formatEventDateTime(item.publishedAt)}${item.source ? ` • ${item.source}` : ""}`,
      body: item.description || item.summary || item.title || "Latest event context is being refreshed.",
    }));
  const signalDrivers = (active.driverCards || forecast.triggers || []).slice(0, 5);
  const paperNotes = (selectedRegionPayload()?.researchProtocol?.practices || selectedRegionPayload()?.watchlistImplications?.graph?.papers || []).slice(0, 2);
  document.getElementById("catalyst-list").innerHTML = `
    ${latestDriverEvents.length ? `
      <div class="driver-event-strip">
        ${latestDriverEvents
          .map(
            (item) => `
              <div class="catalyst-card event-led">
                <div class="catalyst-header">
                  <strong>${item.title}</strong>
                  <span>${String(item.tag).toUpperCase()}</span>
                </div>
                <small>${item.meta}</small>
                <p>${item.body}</p>
              </div>
            `,
          )
          .join("")}
      </div>
    ` : ""}
    ${paperNotes.length ? `
      <div class="driver-event-strip paper-strip">
        ${paperNotes
          .map(
            (item) => `
              <div class="catalyst-card paper-led">
                <div class="catalyst-header">
                  <strong>${item.title}</strong>
                  <span>PAPER</span>
                </div>
                <small>${item.year || ""} • ${item.type || "research"}</small>
                <p>${item.practice || item.whyItMatters}</p>
              </div>
            `,
          )
          .join("")}
      </div>
    ` : ""}
    ${(researchOverview.papers || []).length ? `
      <div class="driver-event-strip paper-strip methodology-strip">
        ${(researchOverview.papers || [])
          .slice(0, 2)
          .map(
            (item) => `
              <div class="catalyst-card paper-led">
                <div class="catalyst-header">
                  <strong>${item.title}</strong>
                  <span>METHOD</span>
                </div>
                <small>${item.year || ""} • ${item.type || "research"}</small>
                <p>${item.dashboardUse || item.practice}</p>
              </div>
            `,
          )
          .join("")}
      </div>
    ` : ""}
    <div class="driver-card-stack">
      ${signalDrivers
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
        .join("")}
    </div>
  `;
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
  const maxAbs = Math.max(4, ...items.map((item) => Math.abs(Number(item.returnPercent || 0))));
  return `
    <div class="benchmark-bars">
      ${items.map((item) => {
        const value = Number(item.returnPercent || 0);
        const width = Math.max(4, Math.abs(value) / maxAbs * 100);
        return `
          <div class="benchmark-row">
            <span>${item.label}</span>
            <div class="benchmark-bar-track">
              <div class="benchmark-bar ${value >= 0 ? "positive" : "negative"}" style="width:${width}%"></div>
            </div>
            <strong class="${value >= 0 ? "positive" : "negative"}">${formatPercent(value)}</strong>
          </div>
        `;
      }).join("")}
    </div>
  `;
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
    });
  });

  container.ondragover = (event) => {
    event.preventDefault();
    const dragging = container.querySelector(".dossier-card.dragging");
    if (!dragging || !(event.target instanceof Element)) return;
    const target = event.target.closest("[data-dossier-card]");
    if (!target || target === dragging || !container.contains(target)) return;

    const rect = target.getBoundingClientRect();
    const shouldInsertBefore = event.clientY < rect.top + rect.height / 2;
    container.insertBefore(dragging, shouldInsertBefore ? target : target.nextSibling);
  };

  container.ondrop = (event) => {
    event.preventDefault();
    syncOrder();
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
    node.innerHTML = `<div class="dossier-empty">Stock dossier is loading.</div>`;
    discoveryNode.innerHTML = "";
    return;
  }
  const day = dossier.daySnapshot || {};
  const fundamentals = dossier.fundamentals || {};
  const consensus = dossier.expertConsensus || {};
  const expertOutlook = active.expertOutlook || {};
  const unusual = dossier.unusualActivity || {};
  const influence = dossier.influenceGraph || {};
  const discoveryItems = state.dashboard?.discovery?.items || [];
  const roeLabel = fundamentals.roe === null || fundamentals.roe === undefined || fundamentals.roe === ""
    ? "Unavailable"
    : dossierMetric(Number(fundamentals.roe) * 100, "percent");
  nav.innerHTML = [
    ["Snapshot", "dossier-day"],
    ["Averages", "dossier-ma"],
    ["Fundamentals", "dossier-fundamentals"],
    ["Peers", "dossier-peers"],
    ["Benchmarks", "dossier-benchmarks"],
    ["Links", "dossier-links"],
  ].map(([label, target]) => `<button type="button" data-scroll-target="${target}">${label}</button>`).join("");
  nav.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => document.getElementById(button.dataset.scrollTarget)?.scrollIntoView({ behavior: "smooth", block: "nearest" }));
  });
  const cards = {
    day: `
    <section id="dossier-day" class="dossier-card dossier-card-focus" draggable="true" data-dossier-card="day">
      <button class="dossier-drag-handle" type="button" aria-label="Drag Day snapshot">⠿</button>
      <div class="dossier-card-head"><span>Day snapshot</span><strong>${active.symbol}</strong><small>${day.source || "Quote provider"}</small></div>
      <div class="dossier-metric-grid">
        <div><span>Open</span><strong>${dossierMetric(day.open, "currency", active.currency)}</strong></div>
        <div><span>Previous</span><strong>${dossierMetric(day.previousClose, "currency", active.currency)}</strong></div>
        <div><span>Day range</span><strong>${dossierMetric(day.dayLow, "currency", active.currency)} - ${dossierMetric(day.dayHigh, "currency", active.currency)}</strong></div>
        <div><span>52W range</span><strong>${dossierMetric(day.fiftyTwoWeekLow, "currency", active.currency)} - ${dossierMetric(day.fiftyTwoWeekHigh, "currency", active.currency)}</strong></div>
        <div><span>Volume</span><strong>${dossierMetric(day.volume, "large")}</strong></div>
        <div><span>Avg volume</span><strong>${dossierMetric(day.averageVolume, "large")}</strong></div>
      </div>
    </section>`,
    ma: `
    <section id="dossier-ma" class="dossier-card dossier-card-compact" draggable="true" data-dossier-card="ma">
      <button class="dossier-drag-handle" type="button" aria-label="Drag Moving averages">⠿</button>
      <div class="dossier-card-head"><span>Moving averages</span><strong>Trend stack</strong><small>5 / 20 / 25 / 50 / 200</small></div>
      <div class="ma-dossier-list">
        ${(dossier.movingAverages || []).map((item) => `
          <div>
            <span>${item.label}</span>
            <strong>${dossierMetric(item.value, "currency", active.currency)}</strong>
            <em class="${item.state === "Above" ? "positive" : item.state === "Below" ? "negative" : ""}">${item.state}${item.distancePercent !== null && item.distancePercent !== undefined ? ` · ${formatPercent(item.distancePercent)}` : ""}</em>
          </div>
        `).join("")}
      </div>
    </section>`,
    fundamentals: `
    <section id="dossier-fundamentals" class="dossier-card dossier-card-focus" draggable="true" data-dossier-card="fundamentals">
      <button class="dossier-drag-handle" type="button" aria-label="Drag Fundamentals">⠿</button>
      <div class="dossier-card-head"><span>Fundamentals</span><strong>Quality ${dossierMetric(fundamentals.scores?.quality)}</strong><small>${fundamentals.source || "Provider summary"}</small></div>
      <div class="dossier-score-row">
        <span>Valuation ${dossierMetric(fundamentals.scores?.valuation)}</span>
        <span>Risk ${dossierMetric(fundamentals.scores?.risk)}</span>
      </div>
      <div class="dossier-mini-grid">
        <div><span>EPS</span><strong>${dossierMetric(fundamentals.eps)}</strong></div>
        <div><span>Revenue</span><strong>${dossierMetric(fundamentals.revenue, "large")}</strong></div>
        <div><span>Net income</span><strong>${dossierMetric(fundamentals.netIncome, "large")}</strong></div>
        <div><span>ROE</span><strong>${roeLabel}</strong></div>
      </div>
    </section>`,
    consensus: `
    <section class="dossier-card dossier-card-compact" draggable="true" data-dossier-card="consensus">
      <button class="dossier-drag-handle" type="button" aria-label="Drag Expert consensus">⠿</button>
      <div class="dossier-card-head"><span>Expert consensus</span><strong>${consensus.rating || "Unavailable"}</strong><small>${consensus.sourceLabel || "External source"}</small></div>
      <div class="consensus-stack">
        <span style="--w:${consensus.buy || 0}" class="positive">Buy ${consensus.buy || 0}%</span>
        <span style="--w:${consensus.hold || 0}" class="neutral">Hold ${consensus.hold || 0}%</span>
        <span style="--w:${consensus.sell || 0}" class="negative">Sell ${consensus.sell || 0}%</span>
      </div>
      <p class="dossier-note">${consensus.note || "External consensus only; not dashboard advice."}</p>
      ${expertOutlook ? `
        <div class="expert-outlook-list">
          <div class="expert-outlook-head">
            <span>${expertOutlook.sourceLabel || "Web outlook"}</span>
            <strong>${expertOutlook.label || "External tone"}</strong>
          </div>
          ${(expertOutlook.items || []).slice(0, 4).map((item) => `
            <a href="${item.url}" target="_blank" rel="noreferrer">
              <span>${item.view}${item.target ? ` · ${item.target}` : ""}</span>
              <strong>${item.title}</strong>
              <em>${item.source}</em>
            </a>
          `).join("") || `<p class="expert-outlook-empty">Expert outlook links are unavailable right now; the dashboard keeps the prediction context visible and labels this source gap.</p>`}
          <small>${expertOutlook.note || "External sources require verification."}</small>
        </div>
      ` : ""}
    </section>`,
    peers: `
    <section id="dossier-peers" class="dossier-card dossier-card-table" draggable="true" data-dossier-card="peers">
      <button class="dossier-drag-handle" type="button" aria-label="Drag Peer comparison">⠿</button>
      <div class="dossier-card-head"><span>Peer comparison</span><strong>5 closest peers</strong><small>Market cap, P/E, return, growth, ROE</small></div>
      <div class="peer-table">
        <div class="peer-row peer-head"><span>Peer</span><span>MCap</span><span>P/E</span><span>1Y</span><span>Sales</span><span>ROE</span></div>
        ${(dossier.peerComparison || []).map((peer) => `
          <div class="peer-row"><strong>${peer.symbol}</strong><span>${peer.marketCap}</span><span>${peer.pe}</span><span>${peer.oneYearReturn}</span><span>${peer.salesGrowth}</span><span>${peer.roe}</span></div>
        `).join("")}
      </div>
    </section>`,
    benchmarks: `
    <section id="dossier-benchmarks" class="dossier-card dossier-card-compact" draggable="true" data-dossier-card="benchmarks">
      <button class="dossier-drag-handle" type="button" aria-label="Drag Benchmark comparison">⠿</button>
      <div class="dossier-card-head"><span>Benchmark comparison</span><strong>Normalized 1Y</strong><small>Selected vs region indices</small></div>
      ${renderBenchmarkBars(dossier.benchmarkComparison || [])}
    </section>`,
    activity: `
    <section id="dossier-activity" class="dossier-card dossier-card-band" draggable="true" data-dossier-card="activity">
      <button class="dossier-drag-handle" type="button" aria-label="Drag Range watch">⠿</button>
      <div class="dossier-card-head"><span>Range watch</span><strong>${unusual.breakout || "Range watch"}</strong><small>Gap, breakout, volume, two-day move</small></div>
      <div class="activity-band-grid">
        <div><span>2D move</span><strong>${formatPercent(unusual.twoDayMove || 0)}</strong></div>
        <div><span>Gap</span><strong>${formatPercent(unusual.gapPercent || 0)}</strong></div>
        <div><span>Volume</span><strong>${Number(unusual.volumeRatio || 0).toFixed(2)}x</strong></div>
        <div><span>Breakout</span><strong>${unusual.breakout || "Range watch"}</strong></div>
      </div>
    </section>`,
    links: `
    <section id="dossier-links" class="dossier-card dossier-card-table" draggable="true" data-dossier-card="links">
      <button class="dossier-drag-handle" type="button" aria-label="Drag Influence graph">⠿</button>
      <div class="dossier-card-head"><span>Influence / ownership graph</span><strong>${(influence.nodes || []).length} nodes</strong><small>Public cited only</small></div>
      <div class="influence-ledger">
        ${(influence.ledger || []).length ? (influence.ledger || []).map((item) => `
          <div><strong>${item.claim}</strong><span>${item.confidence} · ${item.sourceLabel || "Source noted"}</span><p>${item.status}</p></div>
        `).join("") : `<div><strong>No sourced sensitive links yet</strong><span>${influence.policy || "Public cited only"}</span><p>Unsourced political or shell-company claims are intentionally hidden.</p></div>`}
      </div>
    </section>`,
    metrics: `
    <section class="dossier-card dossier-card-table" draggable="true" data-dossier-card="metrics">
      <button class="dossier-drag-handle" type="button" aria-label="Drag Show all metrics">⠿</button>
      <div class="dossier-card-head"><span>Show all metrics</span><strong>Drawer preview</strong><small>Grouped source-backed values</small></div>
      <div class="metric-drawer-preview">
        ${(dossier.metricDrawer || []).map((section) => `<div><strong>${section.section}</strong><span>${(section.metrics || []).join(" · ")}</span></div>`).join("")}
      </div>
      <div class="source-provenance">${(dossier.sourceProvenance || []).map((item) => `<span>${item.label}: ${item.usedFor}</span>`).join("")}</div>
    </section>`,
  };
  const orderedKeys = state.dossierOrder.filter((key) => cards[key]).concat(DEFAULT_DOSSIER_ORDER.filter((key) => !state.dossierOrder.includes(key)));
  node.innerHTML = orderedKeys.map((key) => cards[key]).join("");
  setupDossierDrag(node);
  discoveryNode.innerHTML = `
    <div class="dossier-card-head"><span>Market discovery</span><strong>Unusual movers</strong><small>${state.dashboard?.discovery?.source || "Local scan"}</small></div>
    <div class="discovery-strip">
      ${discoveryItems.length ? discoveryItems.map((item) => `
        <button type="button" data-symbol="${item.symbol}">
          <strong>${item.symbol}</strong>
          <span>${formatPercent(item.twoDayMove)} 2D · ${formatPercent(item.latestMove)} latest</span>
          <em>${item.reason} · ${item.confidence}</em>
        </button>
      `).join("") : `<div class="dossier-empty">No unusual watchlist movers yet.</div>`}
    </div>
  `;
  discoveryNode.querySelectorAll("button[data-symbol]").forEach((button) => {
    button.addEventListener("click", () => selectActiveTicker(button.dataset.symbol));
  });
}

function patchOverviewLiveSurface(active, forecast, { redrawChart = false } = {}) {
  const agreement = forecast.models?.agreement || { label: "Pending", score: 0, summary: "Agreement refreshing." };
  const recommendation = active.recommendation || { buy: 0, hold: 100, sell: 0, signal: "Refreshing" };
  document.getElementById("hero-regime").textContent = active.regime;
  const heroPriceNode = document.getElementById("hero-price");
  const heroPriceText = formatCurrency(active.price, active.currency);
  const priceSizeClass = heroPriceText.length >= 14 ? "is-compact" : heroPriceText.length >= 11 ? "is-tight" : "";
  heroPriceNode.className = `hero-price ${priceSizeClass} ${liveValueClass(`hero:${active.symbol}:price`, active.price)}`.trim();
  heroPriceNode.innerHTML = buildPriceFlipMarkup(active.price, active.currency);
  const changeNode = document.getElementById("hero-change");
  changeNode.textContent = formatPercent(active.changePercent);
  changeNode.className = `hero-change live-number ${active.changePercent >= 0 ? "positive" : "negative"} ${liveValueClass(`hero:${active.symbol}:change`, active.changePercent)}`;
  document.getElementById("forecast-direction").textContent = forecast.direction;
  document.getElementById("forecast-confidence").textContent = `Confidence ${Number(forecast.confidence || 0).toFixed(0)}% · ${agreement.label}`;
  const fairValueNode = document.getElementById("fair-value-gap");
  fairValueNode.textContent = formatPercent(forecast.fairValueGap);
  fairValueNode.className = liveValueClass(`hero:${active.symbol}:fair`, forecast.fairValueGap);
  document.getElementById("event-pressure").textContent = forecast.eventPressureLabel;
  const modelErrorNode = document.getElementById("model-error");
  modelErrorNode.textContent = `${Number(forecast.mae || 0).toFixed(1)}%`;
  modelErrorNode.className = liveValueClass(`hero:${active.symbol}:mae`, forecast.mae);
  const forecastRangeNode = document.getElementById("forecast-range");
  forecastRangeNode.textContent = `10D projection ${formatPercent(forecast.expectedReturn)}`;
  forecastRangeNode.className = `forecast-range live-number ${liveValueClass(`hero:${active.symbol}:projection`, forecast.expectedReturn)}`;
  document.getElementById("buy-sell-signal").textContent = recommendation.signal ? recommendation.signal.replace("bias", "scenario") : "Balanced scenario";
  document.getElementById("buy-sell-breakdown").textContent = `Upside ${recommendation.buy ?? 0}% · Base ${recommendation.hold ?? 100}% · Downside ${recommendation.sell ?? 0}%`;
  document.getElementById("model-agreement-note").textContent = `${agreement.summary} Score ${Number(agreement.score || 0).toFixed(0)}/100.`;
  document.getElementById("quote-source-note").textContent = active.asOf
    ? `Quote source: ${formatSourceLabel(active.dataSource)} • ${quoteFreshnessText(active)} • ${new Date(active.asOf).toLocaleString()}`
    : `Quote source: ${formatSourceLabel(active.dataSource)} • ${quoteFreshnessText(active)}`;
  const overviewMetaItems = [
    {
      label: active.exchange || active.region || "Global",
      help: "Where the stock trades.",
    },
    {
      label: `${active.currency || "USD"} pricing`,
      help: "Home-market trading currency.",
    },
    {
      label: `${active.marketState || "Live"} ${liveBadgeMarkup()}`,
      help: "Current session state.",
    },
    {
      label: `Vol ${formatCompactNumber(active.volume)} ${liveBadgeMarkup()}`,
      help: "Current traded volume.",
    },
    {
      label: `${active.asOf ? new Date(active.asOf).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "Delayed"} ${freshnessBadgeMarkup(active.quoteFreshness || {})}`,
      help: "Last quote update time.",
    },
  ];
  document.getElementById("overview-meta").innerHTML = `
    ${overviewMetaItems
      .map(
        (item) => `<span class="overview-meta-pill" data-help="${item.help.replace(/"/g, "&quot;")}" tabindex="0">${item.label}</span>`,
      )
      .join("")}
  `;
  const sessionNode = document.getElementById("market-session-strip");
  if (sessionNode) {
    const session = active.marketSession?.nextTransitionAt
      ? active.marketSession
      : buildClientMarketSession(active.exchange || active.region, active.marketState, active.region);
    const nextTransitionAt = session.nextTransitionAt ? new Date(session.nextTransitionAt) : null;
    const remainingSeconds = nextTransitionAt ? Math.max(0, Math.floor((nextTransitionAt.getTime() - Date.now()) / 1000)) : 0;
    const countdown = nextTransitionAt ? formatDuration(remainingSeconds) : "--:--:--";
    const nextLabel = session.transitionLabel === "close" ? "Closes in" : "Opens in";
    sessionNode.innerHTML = `
      <span class="market-session-pill ${session.isOpen ? "open" : "closed"}">${session.status || "Closed"}</span>
      <strong>${nextLabel} ${countdown}</strong>
      <small>${session.hoursLabel || "Hours unavailable"} · ${session.timezone || "UTC"}</small>
    `;
  }
  document.getElementById("hero-stats").innerHTML = (active.stats || [])
    .map(
      (stat, index) => `
        <div class="hero-stat-card">
          <span>${stat.label}</span>
          <strong class="live-number ${liveValueClass(`hero:${active.symbol}:stat:${index}`, parseFloat(String(stat.value).replace(/[^\d.+-]/g, "")))}">${stat.value}</strong>
        </div>
      `,
    )
    .join("");
  drawSparkline(document.getElementById("hero-sparkline"), (active.history || []).slice(-24));
  if (redrawChart) {
    drawTimeline(
      document.getElementById("hero-projection-chart"),
      active.historySeries?.length ? active.historySeries : (active.history || []),
      forecast.projected || [],
      state.chartFeatures,
      { currency: active.currency, range: state.chartRange, overlayId: "hero-chart-hover" },
    );
  }
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
      second: "2-digit",
      hour12: true,
    }).format(new Date());
  } catch {
    return "--:--:--";
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

function freshnessBadgeMarkup(freshness = {}) {
  const stateLabel = freshness.state || (freshness.isStale ? "stale" : "fresh");
  const label = freshness.label || (freshness.isStale ? "Stale quote" : "Fresh quote");
  return `<span class="freshness-badge ${stateLabel}" title="${freshness.note || ""}">${label}</span>`;
}

function quoteFreshnessText(active = {}) {
  const freshness = active.quoteFreshness || {};
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

function buildRadarFloatItems(radar = {}) {
  const items = radar.items || [];
  const hotspots = radar.hotspots || [];
  const fromItems = items
    .map((item, index) => ({
      id: item.url || `radar-float-item-${index}`,
      title: item.title || "Market event",
      url: item.url || "",
      source: extractDomainLabel(item.url) || "Live scan",
      region: formatRegionLabel(hotspots[index]?.region || "world"),
      when: formatEventDateTime(item.publishedAt),
      bubble: item.title || "Market event",
      summary: item.source || extractDomainLabel(item.url) || "",
      cta: item.url ? "View full" : "View detail",
    }));
  if (fromItems.length) {
    return fromItems;
  }

  const fallbackHeadlines = (radar.headlines || [])
    .filter(Boolean)
    .map((headline, index) => ({
      id: `radar-float-headline-${index}`,
      title: headline,
      url: "",
      source: "Radar brief",
      region: formatRegionLabel(hotspots[index]?.region || "world"),
      when: "Latest",
      bubble: headline,
      summary: "",
      cta: "View detail",
    }));
  if (fallbackHeadlines.length) {
    return fallbackHeadlines;
  }

  const hotspotItems = hotspots.map((item, index) => ({
    id: `radar-float-hotspot-${index}`,
    title: item.headline || `${formatRegionLabel(item.region)} market signal`,
    url: "",
    source: "Radar zone",
    region: formatRegionLabel(item.region || "world"),
    when: "Live",
    bubble: item.headline || `${formatRegionLabel(item.region)} signal`,
    summary: "",
    cta: "View detail",
  }));
  if (hotspotItems.length) return hotspotItems;
  return [];
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function getDefaultRadarFloatSlots() {
  return [{ x: 12, y: 14 }];
}

function buildRadarFloatSlots(floatNode, count) {
  if (!floatNode || count <= 0) return [];
  const width = Math.max(260, floatNode.clientWidth || 0);
  const height = Math.max(92, floatNode.clientHeight || 0);
  const leftPad = 18;
  const rightPad = 20;
  const topPad = 14;
  const bottomPad = 10;
  const rows = count <= 3 ? 1 : 2;
  const usableWidth = Math.max(188, width - leftPad - rightPad);
  const usableHeight = Math.max(52, height - topPad - bottomPad);
  const cols = Math.max(1, Math.ceil(count / rows));
  const approxChipWidth = 196;
  const capacity = Math.max(1, rows * cols);
  const slots = [];
  for (let index = 0; index < Math.min(count, capacity); index += 1) {
    const row = Math.floor(index / cols);
    const col = index % cols;
    const itemsInRow = row === rows - 1 ? Math.max(1, count - (row * cols)) : Math.min(cols, count);
    const rowSpan = Math.max(approxChipWidth, usableWidth);
    const availableLeft = Math.max(0, rowSpan - approxChipWidth);
    const xStep = itemsInRow > 1 ? availableLeft / (itemsInRow - 1) : 0;
    const yStep = rows > 1 ? usableHeight / (rows - 1) : 0;
    slots.push({
      x: leftPad + (itemsInRow > 1 ? col * xStep : availableLeft / 2),
      y: topPad + (rows > 1 ? row * yStep : 10),
    });
  }
  return slots;
}

function hydrateRadarFloatPositions(floatItems) {
  const floatNode = document.getElementById("radar-floats");
  const slots = buildRadarFloatSlots(floatNode, floatItems.length);
  const next = {};
  floatItems.forEach((item, index) => {
    const saved = state.radarFloatPositions[item.id];
    next[item.id] = saved || slots[index] || slots[slots.length - 1];
  });
  state.radarFloatPositions = next;
}

function syncRadarFloatExpansion(floatNode) {
  if (!floatNode) return;
  floatNode.querySelectorAll("[data-radar-float]").forEach((card) => {
    const isActive = card.dataset.radarFloat === state.radarFloatOpenId;
    card.classList.toggle("active", isActive);
    card.setAttribute("aria-expanded", isActive ? "true" : "false");
  });
}

function bindRadarFloatInteractions(floatNode, floatItems) {
  if (!floatNode) return;
  const clearDrag = (pointerId = null) => {
    const drag = state.radarFloatDrag;
    if (!drag) return;
    if (pointerId !== null && drag.pointerId !== pointerId) return;
    if (drag.holdTimer) {
      window.clearTimeout(drag.holdTimer);
    }
    const activeCard = document.querySelector(`[data-radar-float="${drag.id}"]`);
    if (activeCard) {
      activeCard.classList.remove("dragging");
      activeCard.style.removeProperty("--drag-rotate");
      activeCard.style.removeProperty("--drag-skew");
      activeCard.style.removeProperty("--drag-scale-x");
      activeCard.style.removeProperty("--drag-scale-y");
      if (activeCard.hasPointerCapture?.(drag.pointerId)) {
        activeCard.releasePointerCapture(drag.pointerId);
      }
    }
    state.radarFloatDrag = null;
  };
  const bounds = () => ({
    width: floatNode.clientWidth || 340,
    height: floatNode.clientHeight || 188,
  });

  floatNode.querySelectorAll("[data-radar-float]").forEach((card) => {
    const id = card.dataset.radarFloat;
    card.addEventListener("pointerdown", (event) => {
      if (!event.isPrimary || event.button !== 0) return;
      if (event.target.closest("[data-radar-detail]")) return;
      clearDrag();
      const rect = card.getBoundingClientRect();
      const holdTimer = window.setTimeout(() => {
        const drag = state.radarFloatDrag;
        if (!drag || drag.id !== id || drag.pointerId !== event.pointerId) return;
        drag.dragReady = true;
      }, 180);
      state.radarFloatDrag = {
        id,
        pointerId: event.pointerId,
        startX: event.clientX,
        startY: event.clientY,
        originX: state.radarFloatPositions[id]?.x ?? rect.left,
        originY: state.radarFloatPositions[id]?.y ?? rect.top,
        moved: false,
        dragging: false,
        startedAt: performance.now(),
        lastX: event.clientX,
        lastY: event.clientY,
        lastAt: performance.now(),
        velocityX: 0,
        velocityY: 0,
        dragReady: false,
        holdTimer,
      };
    });

    card.addEventListener("pointermove", (event) => {
      const drag = state.radarFloatDrag;
      if (!drag || drag.id !== id || drag.pointerId !== event.pointerId) return;
      if (event.buttons !== 1) {
        clearDrag(event.pointerId);
        return;
      }
      const area = bounds();
      const dx = event.clientX - drag.startX;
      const dy = event.clientY - drag.startY;
      if (!drag.dragReady && Math.abs(dx) < 14 && Math.abs(dy) < 14) {
        return;
      }
      drag.dragReady = true;
      if (!drag.dragging) {
        drag.dragging = true;
        if (drag.holdTimer) {
          window.clearTimeout(drag.holdTimer);
          drag.holdTimer = null;
        }
        card.setPointerCapture(event.pointerId);
        card.classList.add("dragging");
      }
      const nextX = clamp(drag.originX + dx, 0, area.width - card.offsetWidth);
      const nextY = clamp(drag.originY + dy, 0, area.height - card.offsetHeight);
      drag.moved = drag.moved || Math.abs(dx) > 5 || Math.abs(dy) > 5;
      drag.velocityX = event.clientX - drag.lastX;
      drag.velocityY = event.clientY - drag.lastY;
      drag.lastX = event.clientX;
      drag.lastY = event.clientY;
      drag.lastAt = performance.now();
      state.radarFloatPositions[id] = { x: nextX, y: nextY };
      card.style.left = `${nextX}px`;
      card.style.top = `${nextY}px`;
      card.style.setProperty("--drag-rotate", `${clamp(drag.velocityX * 0.8, -16, 16)}deg`);
      card.style.setProperty("--drag-skew", `${clamp(drag.velocityX * 0.12, -8, 8)}deg`);
      card.style.setProperty("--drag-scale-x", `${1 + clamp(Math.abs(drag.velocityX) / 80, 0, 0.14)}`);
      card.style.setProperty("--drag-scale-y", `${1 - clamp(Math.abs(drag.velocityX) / 180, 0, 0.08)}`);
    });

    const finishDrag = (event) => {
      const drag = state.radarFloatDrag;
      if (!drag || drag.id !== id || (event && drag.pointerId !== event.pointerId)) return;
      if (drag.holdTimer) {
        window.clearTimeout(drag.holdTimer);
        drag.holdTimer = null;
      }
      if (drag.dragging) {
        card.classList.remove("dragging");
        if (card.hasPointerCapture?.(drag.pointerId)) {
          card.releasePointerCapture(drag.pointerId);
        }
      }
      const speed = Math.hypot(drag.velocityX, drag.velocityY);
      const shouldDismiss = drag.dragging && drag.moved && speed > 20;
      if (shouldDismiss) {
        card.classList.add("popping");
        card.style.setProperty("--pop-x", `${drag.velocityX * 2.4}px`);
        card.style.setProperty("--pop-y", `${drag.velocityY * 2.4}px`);
        window.setTimeout(() => {
          state.radarDismissedFloatIds = [...new Set(state.radarDismissedFloatIds.concat(id))];
          if (state.radarFloatOpenId === id) {
            state.radarFloatOpenId = "";
          }
          renderBanner();
        }, 260);
      } else if (drag.dragging) {
        card.style.removeProperty("--drag-rotate");
        card.style.removeProperty("--drag-skew");
        card.style.removeProperty("--drag-scale-x");
        card.style.removeProperty("--drag-scale-y");
      }

      if (!drag.moved && !shouldDismiss) {
        state.radarFloatOpenId = state.radarFloatOpenId === id ? "" : id;
        syncRadarFloatExpansion(floatNode);
      }
      state.radarFloatDrag = null;
    };

    card.addEventListener("pointerup", finishDrag);
    card.addEventListener("pointercancel", finishDrag);
    card.addEventListener("lostpointercapture", () => {
      clearDrag();
    });
    card.addEventListener("pointerleave", (event) => {
      if (event.buttons !== 1) {
        clearDrag();
      }
    });
  });

  if (!state.radarGlobalPointerCleanupBound) {
    window.addEventListener(
      "pointerup",
      (event) => {
        clearDrag(event.pointerId);
      },
      { passive: true },
    );
    state.radarGlobalPointerCleanupBound = true;
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
    state.dashboard.active = {
      ...buildPendingActive(result.active.symbol),
      ...previousActive,
      ...result.active,
      marketSession:
        result.active.marketSession ||
        buildClientMarketSession(result.active.exchange || result.active.region, result.active.marketState, result.active.region),
    };
  }

  nextFrame(() => {
    renderWatchlist();
    renderBoard();
    renderOverview();
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
    regime: "Refreshing active view",
    history: watchItem?.symbol === previous.symbol ? previous.history || [] : [],
    historySeries: watchItem?.symbol === previous.symbol ? previous.historySeries || [] : [],
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
    recommendation: { buy: 0, hold: 100, sell: 0, signal: "Refreshing" },
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
  const node = document.getElementById("status-updated");
  if (!node) return;
  const activeCurrency =
    state.dashboard?.active?.currency ||
    (state.dashboard?.watchlist || []).find((item) => item.symbol === state.activeTicker)?.currency ||
    "USD";
  const label = node.querySelector(".status-label");
  const token = node.querySelector(".status-token-code");
  if (label) {
    label.textContent = message;
  } else {
    node.textContent = message;
  }
  if (token) {
    token.textContent = String(activeCurrency).slice(0, 4).toUpperCase();
  }
  const loadingWords = ["Loading", "Refreshing", "Searching", "Resolving", "Saving", "Running", "Thinking", "Syncing"];
  const isLoading = loadingWords.some((word) => String(message).startsWith(word));
  node.classList.toggle("loading", isLoading);
  node.classList.toggle("ready", !isLoading);
  node.dataset.currency = String(activeCurrency).slice(0, 4).toUpperCase();
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
  animateSvgRefresh(svg);
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
      }))
      .filter((item) => Number.isFinite(item.value));
  }
  return buildFallbackHistorySeries(history, range);
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
  };
  const step = stepMap[range] || stepMap["1M"];
  return values.map((value, index) => ({
    value,
    timestamp: new Date(lastTimestamp.getTime() + ((index + 1) * step)).toISOString(),
  }));
}

function formatAxisDate(timestamp, range = "1M") {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  const options = range === "1D"
    ? { hour: "2-digit", minute: "2-digit" }
    : range === "1Y"
      ? { month: "short", year: "2-digit" }
      : { day: "2-digit", month: "short" };
  return date.toLocaleString([], options);
}

function formatTooltipDate(timestamp, range = "1M") {
  if (!timestamp) return "Time unavailable";
  const date = new Date(timestamp);
  const options = range === "1D"
    ? { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }
    : { day: "2-digit", month: "short", year: "numeric" };
  return date.toLocaleString([], options);
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
  const values = [...historySeries.map((item) => item.value), ...projectedSeries.map((item) => item.value)];
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
  const historicalPoints = historyValues.map((value, index) => toPoint(value, index, values.length)).join(" ");
  const projectedPoints = projectedValues
    .map((value, index) => toPoint(value, historyValues.length + index, values.length))
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
    x: margin.left + ((index / (values.length - 1 || 1)) * (width - margin.left - margin.right)),
    label: formatAxisDate(historySeries[index]?.timestamp, options.range || "1M"),
  }));

  const hoverPoints = historySeries.map((item, index) => {
    const [x, y] = toPoint(item.value, index, values.length).split(",");
    return {
      x: Number(x),
      y: Number(y),
      value: item.value,
      timestamp: item.timestamp,
    };
  });
  const hoverOverlayId = options.overlayId || "";

  svg.innerHTML = `
    ${yTicks.map((tick) => `<line x1="${margin.left}" y1="${tick.y}" x2="${width - margin.right}" y2="${tick.y}" stroke="rgba(255,255,255,0.08)"></line>`).join("")}
    ${yTicks.map((tick) => `<text x="${margin.left - 8}" y="${tick.y + 4}" text-anchor="end" fill="rgba(255,255,255,0.55)" font-size="11">${formatCurrency(tick.value, options.currency || "USD")}</text>`).join("")}
    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(255,255,255,0.12)"></line>
    <line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(255,255,255,0.12)"></line>
    ${xTicks.map((tick) => `<text x="${tick.x}" y="${height - 10}" text-anchor="middle" fill="rgba(255,255,255,0.55)" font-size="11">${tick.label}</text>`).join("")}
    <polyline fill="none" stroke="#54d2ff" stroke-width="3.5" points="${historicalPoints}" stroke-linecap="round"></polyline>
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
  svg.onmousemove = (event) => {
    if (!hoverPoints.length || !hoverLine || !hoverPoint || !hoverCard) return;
    const rect = svg.getBoundingClientRect();
    const relativeX = ((event.clientX - rect.left) / rect.width) * width;
    const nearest = hoverPoints.reduce((best, point) => (
      Math.abs(point.x - relativeX) < Math.abs(best.x - relativeX) ? point : best
    ));
    hoverLine.setAttribute("x1", String(nearest.x));
    hoverLine.setAttribute("x2", String(nearest.x));
    hoverLine.setAttribute("opacity", "1");
    hoverPoint.setAttribute("cx", String(nearest.x));
    hoverPoint.setAttribute("cy", String(nearest.y));
    hoverPoint.setAttribute("opacity", "1");
    hoverCard.hidden = false;
    hoverCard.innerHTML = `
      <strong>${formatCurrency(nearest.value, options.currency || "USD")}</strong>
      <span>${formatTooltipDate(nearest.timestamp, options.range || "1M")}</span>
    `;
    const leftPercent = Math.max(8, Math.min(78, (nearest.x / width) * 100));
    hoverCard.style.left = `${leftPercent}%`;
    hoverCard.style.top = `${Math.max(10, ((nearest.y / height) * 100) - 12)}%`;
  };
  svg.onmouseleave = () => {
    if (hoverLine) hoverLine.setAttribute("opacity", "0");
    if (hoverPoint) hoverPoint.setAttribute("opacity", "0");
    if (hoverCard) {
      hoverCard.hidden = true;
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
        <div class="methodology-rule-card">
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
          ${item.url ? `<a class="methodology-card-source" href="${item.url}" target="_blank" rel="noreferrer">↗ ${item.sourceTitle || "Source"}</a>` : (item.sourceTitle ? `<small class="methodology-card-source-text">${item.sourceTitle}</small>` : "")}
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
    formula: "Score = 0.45·MOM₅ + 0.35·MOM₂₀ + 0.20·log(1+VR)\nVR = Volume / Avg Volume₂₀",
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
      ${p.url ? `<a class="methodology-paper-link" href="${p.url}" target="_blank" rel="noreferrer">↗ arxiv / doi</a>` : ""}
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
  const links = (graph.links || []).map((link, index) => ({
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
      ${nodeData.sourceUrl ? `<a class="project-source-link" href="${nodeData.sourceUrl}" target="_blank" rel="noreferrer">${nodeData.sourceLabel || "Source"}</a>` : ""}
    </div>
  `;
}

function renderImpactGraphWorkspace(graph = {}) {
  const container = document.getElementById("impact-graph");
  if (!container) return;
  const noteNode = document.getElementById("impact-graph-note");
  if (!window.cytoscape) {
    container.innerHTML = `<div class="impact-graph-fallback">Graph engine unavailable.</div>`;
    if (noteNode) noteNode.textContent = "Graph engine unavailable.";
    return;
  }
  const elements = buildImpactGraphElements(graph);
  if (!elements.length) {
    container.innerHTML = `<div class="impact-graph-fallback">No graph data for the current region.</div>`;
    renderImpactGraphDetail(null);
    if (noteNode) noteNode.textContent = "Graph source pending.";
    return;
  }
  if (!state.impactGraphCy) {
    state.impactGraphCy = window.cytoscape({
      container,
      elements,
      wheelSensitivity: 0.18,
      minZoom: 0.45,
      maxZoom: 1.8,
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
            "font-size": 10,
            "text-wrap": "wrap",
            "text-max-width": 120,
            "text-valign": "center",
            "text-halign": "center",
            width: (ele) => (ele.data("group") === "project" ? 168 : ele.data("group") === "stock" ? 136 : 116),
            height: (ele) => (ele.data("group") === "project" ? 70 : ele.data("group") === "stock" ? 58 : 50),
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
            "font-size": 8,
            "text-background-opacity": 0,
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
  state.impactGraphCy.layout({
    name: "breadthfirst",
    directed: true,
    padding: 34,
    spacingFactor: 1.1,
    animate: true,
    roots: ["#bonds", "#inflation", "#policy"],
  }).run();
  state.impactGraphCy.fit(undefined, 34);
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
      graphMeta.maxNodes ? `${graphMeta.maxNodes} nodes` : "",
    ].filter(Boolean);
    noteNode.textContent = noteBits.join(" • ");
  }
}

function renderSearchResults(results = []) {
  const node = document.getElementById("search-results");
  if (!results.length) {
    node.innerHTML = "";
    return;
  }

  node.innerHTML = results
    .map(
      (item) => {
        const sectorLabel = item.sector ? `<em class="search-result-sector">${item.sector}</em>` : "";
        return `
        <button class="search-result" type="button" data-symbol="${item.symbol}">
          <div>
            <strong>${item.symbol}</strong>
            <p>${item.name || item.exchange || "Market listing"}</p>
          </div>
          <div class="search-result-right">
            ${sectorLabel}
            <span>${item.exchange || item.region || "Global"}</span>
          </div>
        </button>
      `;
      },
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
  count.textContent = String(entries.length);

  node.innerHTML = entries
    .map(
      (item) => {
        const priceClass = liveValueClass(`watch:${item.symbol}:price`, item.price);
        const changeClass = liveValueClass(`watch:${item.symbol}:change`, item.changePercent);
        return `
        <button class="watch-item ${priceClass} ${item.symbol === state.activeTicker ? "active" : ""}" type="button" data-symbol="${item.symbol}" draggable="true">
          <div class="watch-row">
            <span class="watch-symbol">${item.symbol}</span>
            <div class="watch-actions">
              <span class="drag-handle" data-drag-handle="${item.symbol}">::</span>
              <span class="watch-change live-number ${item.changePercent >= 0 ? "positive" : "negative"} ${changeClass}">${formatPercent(item.changePercent)}</span>
              <span class="delete-chip" data-delete="${item.symbol}">Delete</span>
            </div>
          </div>
          <div class="watch-row">
            <span class="watch-name">${item.name}</span>
            <span class="watch-price live-number ${priceClass}">${formatCurrency(item.price, item.currency)}</span>
          </div>
          <div class="watch-row watch-meta-row">
            <span>${item.exchange} · ${item.currency}</span>
            <span>Vol ${formatCompactNumber(item.volume)}</span>
          </div>
        </button>
      `;
      },
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
  const hotspotNode = document.getElementById("radar-hotspots");
  const sourceNote = document.getElementById("radar-source-note");
  const sentimentBox = document.getElementById("radar-sentiment-box");
  const floatNode = document.getElementById("radar-floats");
  const floatDetailNode = document.getElementById("radar-float-detail");
  const radarPanel = document.getElementById("market-radar");
  const popButton = document.getElementById("pop-radar-clouds");
  const popLabel = document.getElementById("radar-cloud-toggle-label");
  const footerNode = document.querySelector(".radar-footer");
  const radar = state.dashboard?.radar || {};
  const allLiveFloatItems = buildRadarFloatItems(radar);
  const headlines = radar.headlines?.length
    ? radar.headlines
    : radar.items?.length
      ? radar.items.map((item) => item.title).filter(Boolean).slice(0, 6)
    : state.dashboard?.headlines?.length
      ? state.dashboard.headlines
      : ["Live radar updates are loading."];
  const signature = headlines.join(" | ");
  const useStaticLoadingHeadline = headlines.length === 1 && headlines[0] === "Live radar updates are loading.";
  const radarSignature = `${signature}::${state.dashboard?.radarUpdatedAt || ""}::${allLiveFloatItems.map((item) => item.id).join("|")}`;
  if (floatNode && floatNode.dataset.radarSignature !== radarSignature) {
    const previousIds = (floatNode.dataset.radarIds || "").split("|").filter(Boolean);
    const nextIds = allLiveFloatItems.map((item) => item.id);
    state.radarFreshFloatIds = nextIds.filter((id) => !previousIds.includes(id));
    state.radarDismissedFloatIds = state.radarDismissedFloatIds.filter((id) => nextIds.includes(id) && !state.radarFreshFloatIds.includes(id));
    state.radarFloatPositions = Object.fromEntries(
      Object.entries(state.radarFloatPositions).filter(([id]) => nextIds.includes(id)),
    );
    if (state.radarFloatOpenId && !nextIds.includes(state.radarFloatOpenId)) {
      state.radarFloatOpenId = "";
    }
    if (state.radarFreshFloatIds.length) {
      state.radarDismissedFloatIds = state.radarDismissedFloatIds.filter((id) => !state.radarFreshFloatIds.includes(id));
      state.radarFloatsCollapsed = false;
    }
    floatNode.dataset.radarSignature = radarSignature;
    floatNode.dataset.radarIds = nextIds.join("|");
  }
  const floatItemsAll = allLiveFloatItems.filter((item) => !state.radarDismissedFloatIds.includes(item.id));
  if (radarPanel) {
    radarPanel.classList.toggle("floats-collapsed", state.radarFloatsCollapsed || floatItemsAll.length === 0);
  }
  const floatSlots = floatNode ? buildRadarFloatSlots(floatNode, floatItemsAll.length) : [];
  const floatItems = state.radarFloatsCollapsed ? [] : floatItemsAll.slice(0, floatSlots.length);
  if (radarPanel) {
    radarPanel.classList.toggle("floats-collapsed", state.radarFloatsCollapsed || floatItems.length === 0);
  }
  if (popButton) {
    const hasClouds = floatItemsAll.length > 0;
    popButton.disabled = !hasClouds;
    popButton.classList.toggle("is-idle", !hasClouds);
    popButton.setAttribute("aria-label", state.radarFloatsCollapsed ? "Bring back clouds" : "Hide clouds");
  }
  if (popLabel) {
    popLabel.textContent = state.radarFloatsCollapsed ? "Bring clouds" : "Hide clouds";
  }
  if (track.dataset.signature !== signature || !track.children.length) {
    const lane = headlines
      .map(
        (headline) => `<span class="ticker-headline" title="${headline}">${headline}</span>`,
      )
      .join("");
    const duration = Math.max(22, Math.round(signature.length / 8));
    track.dataset.signature = signature;
    track.style.setProperty("--ticker-duration", `${duration}s`);
    track.innerHTML = useStaticLoadingHeadline
      ? `<div class="ticker-status">${headlines[0]}</div>`
      : `
        <div class="ticker-lane ticker-lane-a">${lane}</div>
        <div class="ticker-lane ticker-lane-b" aria-hidden="true">${lane}</div>
      `;
  }
  const hotspots = radar.hotspots || [];
  if (hotspotNode) {
    hotspotNode.innerHTML = "";
    hotspotNode.hidden = true;
  }

  const radarSources = [...new Set((radar.items || []).map((item) => extractDomainLabel(item.url)).filter(Boolean))].slice(0, 4);
  sourceNote.textContent = radarSources.length
    ? `Radar sources: ${radarSources.join(" • ")}`
    : "Radar sources: live event scan";
  if (radarPanel && footerNode) {
    const footerHeight = Math.ceil(footerNode.getBoundingClientRect().height || 36);
    radarPanel.style.setProperty("--radar-footer-height", `${footerHeight}px`);
  }
  if (sentimentBox) {
    const sentiment = radar.sentiment || { label: "Balanced", score: 0 };
    const score = Number(sentiment.score || 0);
    const scoreText = score > 0 ? `+${(score * 100).toFixed(0)}` : `${(score * 100).toFixed(0)}`;
    const toneClass = sentiment.tone || (score > 0.2 ? "positive" : score < -0.2 ? "negative" : "neutral");
    sentimentBox.className = `radar-sentiment-box ${toneClass}`;
    sentimentBox.innerHTML = `
      <span>Radar sentiment</span>
      <strong>${sentiment.label || "Balanced"}</strong>
      <small>${scoreText} • ${sentiment.driver || "headline balance"}</small>
    `;
  }

  hydrateRadarFloatPositions(floatItems);
  if (floatNode) {
    floatNode.innerHTML = floatItems
      .map((item, index) => {
        const pos = state.radarFloatPositions[item.id] || floatSlots[index] || getDefaultRadarFloatSlots()[0];
        const size = item.title.length > 120 ? "large" : item.title.length > 72 ? "medium" : "small";
        const active = state.radarFloatOpenId === item.id;
        return `
          <div
            class="radar-float-chip radar-float-chip-${size} radar-float-shape-${index % 6} ${active ? "active" : ""} ${state.radarFreshFloatIds.includes(item.id) ? "forming" : ""}"
            data-radar-float="${item.id}"
            style="left:${pos.x}px; top:${pos.y}px; --float-delay:${index * 1.15}s;"
            title="${item.title}"
            role="button"
            tabindex="0"
            aria-expanded="${active ? "true" : "false"}"
          >
            <i class="cloud-puff cloud-puff-a" aria-hidden="true"></i>
            <i class="cloud-puff cloud-puff-b" aria-hidden="true"></i>
            <i class="cloud-puff cloud-puff-c" aria-hidden="true"></i>
            <span><label>${item.region}</label><b>${item.when || "Live"}</b></span>
            <strong>${item.bubble}</strong>
            ${item.summary ? `<p>${item.summary}</p>` : ""}
            ${
              item.url
                ? `<a class="radar-float-link" data-radar-detail="true" href="${item.url}" target="_blank" rel="noreferrer">${item.cta || "View detail"}</a>`
                : ""
            }
          </div>
        `;
      })
      .join("");
    floatNode.querySelectorAll("[data-radar-detail]").forEach((link) => {
      link.addEventListener("pointerdown", (event) => {
        event.stopPropagation();
      });
      link.addEventListener("pointerup", (event) => {
        event.stopPropagation();
      });
      link.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        window.open(link.href, "_blank", "noopener,noreferrer");
      });
    });
    syncRadarFloatExpansion(floatNode);
    bindRadarFloatInteractions(floatNode, floatItems);
  }

  if (floatDetailNode) {
    floatDetailNode.hidden = true;
    floatDetailNode.innerHTML = "";
  }
}

function renderEventFeed() {
  const list = document.getElementById("event-list");
  const label = document.getElementById("event-summary-label");
  label.textContent = state.eventCategory === "all" ? "All" : state.eventCategory.charAt(0).toUpperCase() + state.eventCategory.slice(1);
  document.querySelectorAll(".event-chip").forEach((button) => {
    button.classList.toggle("active", button.dataset.category === state.eventCategory);
  });

  if (!state.eventResult) {
    const fallbackItems = [...(state.dashboard?.radar?.items || [])]
      .slice(0, 4)
      .map((item) => ({
        title: item.title || "Radar update",
        url: item.url || "",
        source: item.source || extractDomainLabel(item.url) || "Live source",
        category: "radar",
        publishedAt: item.publishedAt,
        significance: 0,
      }));
    list.innerHTML = fallbackItems.length
      ? fallbackItems
          .map(
            (item) => `
              <article class="event-card">
                <div class="event-card-header">
                  <span class="event-tag">${String(item.category).toUpperCase()}</span>
                  <span class="event-source">${item.source}</span>
                </div>
                <a class="event-title" href="${item.url}" target="_blank" rel="noreferrer"><strong>${item.title}</strong></a>
                <div class="event-card-meta">
                  <span>${formatEventDateTime(item.publishedAt)}</span>
                  <span>Refreshing</span>
                </div>
                <p>Full category event flow is being updated.</p>
              </article>
            `,
          )
          .join("")
      : `<div class="event-card"><div class="event-card-header"><strong>Waiting for updates</strong><span class="event-tag">Loading</span></div><p>Latest category events will appear here.</p></div>`;
    return;
  }
  const items = [...(state.eventResult.items || [])]
    .sort((a, b) => String(b.publishedAt || "").localeCompare(String(a.publishedAt || "")))
    .slice(0, 5);
  list.innerHTML = items.length
    ? items
        .map(
          (item) => `
            <article class="event-card">
              <div class="event-card-header">
                <span class="event-tag">${String(item.category || state.eventResult.category || "event").toUpperCase()}</span>
                <span class="event-source">${item.source || extractDomainLabel(item.url) || "Live source"}</span>
              </div>
              <a class="event-title" href="${item.url}" target="_blank" rel="noreferrer"><strong>${item.title || "Update"}</strong></a>
              <div class="event-card-meta">
                <span>${formatEventDateTime(item.publishedAt)}</span>
                <span>Impact ${Number(item.significance || 0)}</span>
              </div>
              <p>${item.source ? `Source: ${item.source}` : "Source note unavailable."}</p>
            </article>
          `,
        )
        .join("")
    : `<div class="event-card"><div class="event-card-header"><strong>No live matches</strong><span class="event-tag">Empty</span></div><p>Try another category or search phrase.</p></div>`;
}

function renderPulse() {
  const grid = document.getElementById("pulse-grid");
  const items = state.dashboard?.macroPulse?.length
    ? state.dashboard.macroPulse
    : state.dashboard?.active
      ? [
          {
            label: "Risk tone",
            value: state.dashboard.active.regime || "Refreshing",
            trend: state.dashboard.active.marketState || "Live",
            positive: true,
          },
          {
            label: "Active move",
            value: formatPercent(state.dashboard.active.changePercent || 0),
            trend: `${state.dashboard.active.exchange || state.dashboard.active.region || "Market"} pulse`,
            positive: Number(state.dashboard.active.changePercent || 0) >= 0,
          },
        ]
      : [];
  if (!items.length) {
    grid.innerHTML = `
      <div class="pulse-card">
        <span>Market pulse</span>
        <strong>Loading</strong>
        <div class="metric-trend neutral">Cross-asset read is refreshing</div>
      </div>
    `;
    return;
  }
  grid.innerHTML = items
    .map(
      (item, index) => {
        const pulseClass = liveValueClass(`pulse:${item.label || index}`, parseFloat(String(item.value).replace(/[^\d.+-]/g, "")));
        return `
        <div class="pulse-card ${pulseClass}">
          <span>${item.label}${liveBadgeMarkup()}</span>
          <strong class="live-number">${item.value}</strong>
          <div class="metric-trend ${typeof item.positive === "boolean" ? (item.positive ? "positive" : "negative") : "neutral"}">${item.trend}</div>
        </div>
      `;
      },
    )
    .join("");
}

function renderBoard() {
  const board = document.getElementById("overview-board");
  const panel = document.getElementById("market-board-panel");
  const utilityGrid = document.querySelector(".utility-grid");
  const toggle = document.getElementById("toggle-market-board");
  const entries = (state.dashboard?.watchlist || []).slice(0, 8);
  if (panel) {
    panel.classList.toggle("collapsed", state.boardHidden);
  }
  if (utilityGrid) {
    utilityGrid.classList.toggle("board-hidden", state.boardHidden);
  }
  if (toggle) {
    toggle.textContent = state.boardHidden ? "Show" : "Hide";
    toggle.setAttribute("aria-pressed", state.boardHidden ? "true" : "false");
  }
  if (state.boardHidden) {
    board.innerHTML = "";
    return;
  }
  board.innerHTML = entries
    .map(
      (item) => {
        const priceClass = liveValueClass(`board:${item.symbol}:price`, item.price);
        const changeClass = liveValueClass(`board:${item.symbol}:change`, item.changePercent);
        return `
        <button class="board-tile ${item.changePercent >= 0 ? "up" : "down"} ${priceClass} ${item.symbol === state.activeTicker ? "active" : ""}" type="button" data-symbol="${item.symbol}">
          <span class="board-symbol">${item.symbol}</span>
          <strong class="board-price live-number ${priceClass}">${formatCurrency(item.price, item.currency)}</strong>
          <span class="board-change live-number ${item.changePercent >= 0 ? "positive" : "negative"} ${changeClass}">${formatPercent(item.changePercent)}</span>
        </button>
      `;
      },
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
  const forecast = active.forecast || emptyForecastPayload();
  const agreement = forecast.models?.agreement || { label: "Pending", score: 0, summary: "Agreement refreshing." };
  const recommendation = active.recommendation || { buy: 0, hold: 100, sell: 0, signal: "Refreshing" };

  document.getElementById("hero-ticker").textContent = `${active.symbol} · ${active.name}`;
  document.getElementById("hero-regime").textContent = active.regime;
  const heroPriceNode = document.getElementById("hero-price");
  const heroPriceText = formatCurrency(active.price, active.currency);
  const priceSizeClass = heroPriceText.length >= 14 ? "is-compact" : heroPriceText.length >= 11 ? "is-tight" : "";
  heroPriceNode.className = `hero-price ${priceSizeClass} ${liveValueClass(`hero:${active.symbol}:price`, active.price)}`.trim();
  heroPriceNode.innerHTML = buildPriceFlipMarkup(active.price, active.currency);
  const changeNode = document.getElementById("hero-change");
  changeNode.textContent = formatPercent(active.changePercent);
  changeNode.className = `hero-change live-number ${active.changePercent >= 0 ? "positive" : "negative"} ${liveValueClass(`hero:${active.symbol}:change`, active.changePercent)}`;
  document.getElementById("forecast-direction").textContent = forecast.direction;
  document.getElementById("forecast-confidence").textContent = `Confidence ${Number(forecast.confidence || 0).toFixed(0)}% · ${agreement.label}`;
  document.getElementById("fair-value-gap").textContent = formatPercent(forecast.fairValueGap);
  document.getElementById("fair-value-gap").className = liveValueClass(`hero:${active.symbol}:fair`, forecast.fairValueGap);
  document.getElementById("event-pressure").textContent = forecast.eventPressureLabel;
  document.getElementById("model-error").textContent = `${Number(forecast.mae || 0).toFixed(1)}%`;
  document.getElementById("model-error").className = liveValueClass(`hero:${active.symbol}:mae`, forecast.mae);
  document.getElementById("forecast-range").textContent = `10D projection ${formatPercent(forecast.expectedReturn)}`;
  document.getElementById("forecast-range").className = `forecast-range live-number ${liveValueClass(`hero:${active.symbol}:projection`, forecast.expectedReturn)}`;
  document.getElementById("buy-sell-signal").textContent = recommendation.signal ? recommendation.signal.replace("bias", "scenario") : "Balanced scenario";
  document.getElementById("buy-sell-breakdown").textContent = `Upside ${recommendation.buy ?? 0}% · Base ${recommendation.hold ?? 100}% · Downside ${recommendation.sell ?? 0}%`;
  document.getElementById("model-agreement-note").textContent = `${agreement.summary} Score ${Number(agreement.score || 0).toFixed(0)}/100.`;
  const overviewMetaItems = [
    {
      label: active.exchange || active.region || "Global",
      help: "Where the stock trades.",
    },
    {
      label: `${active.currency || "USD"} pricing`,
      help: "Home-market trading currency.",
    },
    {
      label: `${active.marketState || "Live"} ${liveBadgeMarkup()}`,
      help: "Current session state.",
    },
    {
      label: `Vol ${formatCompactNumber(active.volume)} ${liveBadgeMarkup()}`,
      help: "Current traded volume.",
    },
    {
      label: `${active.asOf ? new Date(active.asOf).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "Delayed"} ${freshnessBadgeMarkup(active.quoteFreshness || {})}`,
      help: "Last quote update time.",
    },
  ];
  document.getElementById("overview-meta").innerHTML = `
    ${overviewMetaItems
      .map(
        (item) => `<span class="overview-meta-pill" data-help="${item.help.replace(/"/g, "&quot;")}" tabindex="0">${item.label}</span>`,
      )
      .join("")}
  `;
  const quoteSource = document.getElementById("quote-source-note");
  const asOf = active.asOf ? new Date(active.asOf).toLocaleString() : "";
  quoteSource.textContent = asOf
    ? `Quote source: ${formatSourceLabel(active.dataSource)} • ${quoteFreshnessText(active)} • ${asOf}`
    : `Quote source: ${formatSourceLabel(active.dataSource)} • ${quoteFreshnessText(active)}`;
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
    const nextTransitionAt = session.nextTransitionAt ? new Date(session.nextTransitionAt) : null;
    const remainingSeconds = nextTransitionAt ? Math.max(0, Math.floor((nextTransitionAt.getTime() - Date.now()) / 1000)) : 0;
    const countdown = nextTransitionAt ? formatDuration(remainingSeconds) : "--:--:--";
    const nextLabel = session.transitionLabel === "close" ? "Closes in" : "Opens in";
    marketSessionNode.innerHTML = `
      <span class="market-session-pill ${session.isOpen ? "open" : "closed"}">${session.status || "Closed"}</span>
      <strong>${nextLabel} ${countdown}</strong>
      <small>${session.hoursLabel || "Hours unavailable"} · ${session.timezone || "UTC"}</small>
    `;
  };
  renderSession();
  if (active.marketSession?.nextTransitionAt) {
    state.marketSessionTimer = window.setInterval(renderSession, 1000);
  }

  document.getElementById("hero-stats").innerHTML = (active.stats || [])
    .map(
      (stat, index) => `
        <div class="hero-stat-card">
          <span>${stat.label}</span>
          <strong class="live-number ${liveValueClass(`hero:${active.symbol}:stat:${index}`, parseFloat(String(stat.value).replace(/[^\d.+-]/g, "")))}">${stat.value}</strong>
        </div>
      `,
    )
    .join("");

  drawSparkline(document.getElementById("hero-sparkline"), (active.history || []).slice(-24));
  drawTimeline(
    document.getElementById("hero-projection-chart"),
    active.historySeries?.length ? active.historySeries : (active.history || []),
    forecast.projected || [],
    state.chartFeatures,
    { currency: active.currency, range: state.chartRange, overlayId: "hero-chart-hover" },
  );
  document.querySelectorAll(".range-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.range === state.chartRange);
  });
  document.getElementById("feature-sma20").checked = Boolean(state.chartFeatures.sma20);
  document.getElementById("feature-sma50").checked = Boolean(state.chartFeatures.sma50);
  document.getElementById("feature-bands").checked = Boolean(state.chartFeatures.bands);
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
      (item) => `
        <div class="factor-card">
          <div class="factor-card-header">
            <strong>${item.sector}</strong>
            <span>${item.effect}</span>
          </div>
          <p>${item.why}</p>
        </div>
      `,
    )
    .join("");
}

function renderMacroEvents() {
  const region = selectedRegionPayload();
  const eventsNode = document.getElementById("macro-events-list");
  const watchNode = document.getElementById("macro-watch-next");
  if (!eventsNode || !watchNode) return;
  if (!region?.events) {
    eventsNode.innerHTML = "";
    watchNode.innerHTML = "";
    return;
  }
  eventsNode.innerHTML = (region.events.items || [])
    .slice(0, 6)
    .map(
      (item) => `
        <div class="event-card">
          <div class="event-card-header">
            <strong>${item.title}</strong>
            <span class="event-tag">${String(item.category || "event").toUpperCase()}</span>
          </div>
          <p>${item.source ? `Source: ${item.source} • ` : ""}${formatEventDateTime(item.publishedAt)}${isFreshUpdate(item.publishedAt) ? ` • ${liveBadgeMarkup()}` : ""}</p>
        </div>
      `,
    )
    .join("");
  const monitorCards = (region.analysis?.monitorNext || [])
    .map((item) => `<div class="reason-card"><span class="analysis-tag monitor">Monitor</span><strong>Monitor</strong><p>${item}</p></div>`);
  const calendarCards = (region.calendar?.items || [])
    .slice(0, 4)
    .map(
      (item) => `
        <div class="reason-card">
          <span class="analysis-tag fact">Fact</span>
          <strong>Calendar</strong>
          <p>${item.title}${item.date ? ` • ${item.date}` : ""}${item.source ? ` • ${item.source}` : ""}</p>
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
                              ? `<a class="project-source-link" href="${project.sourceUrl}" target="_blank" rel="noreferrer">${project.sourceLabel || "Source"}</a>`
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
        <a class="research-card" href="${item.url}" target="_blank" rel="noreferrer">
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
      <strong>${academyDetail.symbol} Explainer</strong>
      <p>${academyDetail.summary}</p>
    </div>
    ${(academyDetail.cards || [])
      .map(
        (item) => `
          <div class="academy-brief-card">
            <strong>${item.title}</strong>
            <p>${item.body}</p>
          </div>
        `,
      )
      .join("")}
  `;

  academySources.innerHTML = (academyDetail.sources || []).length
    ? (academyDetail.sources || [])
        .map(
          (item) => `
            <a class="academy-source-pill" href="${item.url}" target="_blank" rel="noreferrer">${item.title || extractDomainLabel(item.url) || "Source"}</a>
          `,
        )
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
    summary.innerHTML = `<div class="research-state-card"><strong>Research unavailable</strong><p>${state.researchError}</p></div>`;
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
      <h4>${context.symbol ? `${context.symbol} Research Brief` : "Research Brief"}</h4>
      <div class="research-context-pills">
        ${context.symbol ? `<span>${context.symbol}</span>` : ""}
        ${context.regime ? `<span>${context.regime}</span>` : ""}
        <span>${state.researchResult.llmUsed ? "Bonsai assisted" : "Rules + context"}</span>
      </div>
    </div>
    <p>${answer}</p>
    ${takeaways.length ? `<ul>${takeaways.map((item) => `<li>${item}</li>`).join("")}</ul>` : ""}
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
          <p><a href="${item.url}" target="_blank" rel="noreferrer">${extractDomainLabel(item.url) || item.url}</a></p>
        </div>
      `,
    )
    .join("");
}

function renderTopbar() {
  document.getElementById("provider-badge").textContent = state.dashboard?.provider || state.config?.provider || "yahoo";
  setStatus(state.dashboard?.updatedAt ? "Live now" : "Loading data");
  document.body.classList.toggle("app-ready", state.bootReady);
  document.body.classList.toggle("app-booting", !state.bootReady);
  const heading = document.querySelector(".topbar-copy h2");
  if (heading) {
    const region = selectedRegionMeta();
    heading.textContent = region
      ? `${region.label} macro, bonds, inflation, equities, and watchlist context`
      : "US and India macro, bond, inflation, and market context";
  }
  renderGlobalMarketOverview();
}

function renderGlobalMarketOverview() {
  const node = document.getElementById("global-market-overview");
  if (!node) return;
  const markets = state.dashboard?.globalMarkets || [];
  if (!markets.length) {
    node.classList.remove("collapsed");
    node.innerHTML = `
      <button class="global-market-overview-head" type="button" disabled>
        <div>
          <span class="overview-panel-kicker">Global clocks</span>
          <strong>Loading market benchmarks</strong>
        </div>
      </button>
    `;
    return;
  }
  node.classList.toggle("collapsed", state.benchmarksCollapsed);
  node.innerHTML = `
    <button class="global-market-overview-head" type="button" aria-expanded="${state.benchmarksCollapsed ? "false" : "true"}" aria-controls="global-market-benchmark-grid">
      <div>
        <span class="overview-panel-kicker">Global clocks</span>
        <strong>Major benchmarks</strong>
      </div>
      <span class="overview-panel-note">
        Local time, session, latest quote age
        <i class="benchmark-chevron" aria-hidden="true"></i>
      </span>
    </button>
    <div class="global-market-collapse" id="global-market-benchmark-grid">
      <div class="global-market-grid">
        ${markets.map((market) => `
          <article class="market-clock-card">
            <div class="market-clock-top">
              <div>
                <strong>${market.label}</strong>
                <span>${formatZonedDate(market.timezone)}</span>
              </div>
              <div class="market-clock-status ${market.session?.isOpen ? "open" : "closed"}">
                ${market.session?.isOpen ? "Open" : "Closed"}
              </div>
            </div>
            <div class="market-clock-meta">
              <strong>${formatZonedTime(market.timezone)}</strong>
              <span>${market.session?.hoursLabel || market.timezone}</span>
            </div>
            <div class="market-clock-indices">
              ${(market.indices || []).map((item) => `
                <div class="market-index-row ${item.quoteFreshness?.isStale ? "is-stale" : ""}">
                  <span>${item.label}</span>
                  <strong>${formatIndexLevel(item.price)}</strong>
                  <em class="${Number(item.changePercent || 0) >= 0 ? "positive" : "negative"}">${formatPercent(item.changePercent || 0)}</em>
                  ${freshnessBadgeMarkup(item.quoteFreshness || {})}
                </div>
              `).join("")}
            </div>
          </article>
        `).join("")}
      </div>
    </div>
  `;
  const toggle = node.querySelector(".global-market-overview-head");
  toggle?.addEventListener("click", () => {
    state.benchmarksCollapsed = !state.benchmarksCollapsed;
    localStorage.setItem(STORAGE_KEYS.benchmarksCollapsed, state.benchmarksCollapsed ? "1" : "0");
    node.classList.toggle("collapsed", state.benchmarksCollapsed);
    toggle.setAttribute("aria-expanded", state.benchmarksCollapsed ? "false" : "true");
  });
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
  const run = () => {
    document.querySelectorAll(".tab").forEach((node) => node.classList.toggle("active", node.dataset.tab === target));
    document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === target));
    if (target === "watchlist-implications" && state.impactGraphCy) {
      window.setTimeout(() => {
        state.impactGraphCy.resize();
        state.impactGraphCy.fit(undefined, 34);
      }, 80);
    }
  };
  if (document.startViewTransition) {
    document.startViewTransition(run);
  } else {
    run();
  }
}

function startMarketClockTimer() {
  window.clearInterval(state.marketClockTimer);
  state.marketClockTimer = window.setInterval(() => {
    renderGlobalMarketOverview();
  }, 1000);
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
  renderOverview();
  renderBondMarket();
  renderInflationView();
  renderEquityContext();
  renderMacroEvents();
  renderMethodology();
  renderWatchlistImplications();
  renderComparison();
  renderTopbar();
  renderCompactMenu();
  setupScrollReveal();
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
      marketSession:
        payload.active.marketSession ||
        buildClientMarketSession(payload.active.exchange || payload.active.region, payload.active.marketState, payload.active.region),
    };
  } else if (payload.active) {
    const live = quoteMap.get(state.activeTicker);
    if (live && state.dashboard.active) {
      state.dashboard.active = {
        ...state.dashboard.active,
        ...live,
        marketSession: buildClientMarketSession(live.exchange || live.region, live.marketState, live.region),
      };
    }
  }

  if (state.dashboard.active?.price && Array.isArray(state.dashboard.active.historySeries) && state.dashboard.active.historySeries.length) {
    const nextSeries = [...state.dashboard.active.historySeries];
    nextSeries[nextSeries.length - 1] = {
      ...nextSeries[nextSeries.length - 1],
      value: Number(state.dashboard.active.price),
      timestamp: payload.updatedAt || nextSeries[nextSeries.length - 1].timestamp,
    };
    state.dashboard.active.historySeries = nextSeries;
  }
  if (state.dashboard.active?.price && Array.isArray(state.dashboard.active.history) && state.dashboard.active.history.length) {
    const nextHistory = [...state.dashboard.active.history];
    nextHistory[nextHistory.length - 1] = Number(state.dashboard.active.price);
    state.dashboard.active.history = nextHistory;
  }

  renderWatchlist();
  renderBoard();
  if (state.dashboard.active) {
    patchOverviewLiveSurface(
      state.dashboard.active,
      state.dashboard.active.forecast || emptyForecastPayload(),
      { redrawChart: false },
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
  const stream = new EventSource(`/api/stream?symbols=${symbols}&active=${active}`);
  state.quoteStream = stream;
  stream.addEventListener("quote", (event) => {
    try {
      const payload = JSON.parse(event.data);
      applyLiveQuoteUpdate(payload);
    } catch (error) {
      logNonAbort(error);
    }
  });
  stream.onerror = () => {
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

function popAllRadarClouds() {
  const floatNode = document.getElementById("radar-floats");
  const liveItems = buildRadarFloatItems(state.dashboard?.radar || {}).filter((item) => !state.radarDismissedFloatIds.includes(item.id));
  if (!floatNode || !liveItems.length) return;
  floatNode.querySelectorAll("[data-radar-float]").forEach((card, index) => {
    card.classList.add("popping");
    card.style.setProperty("--pop-x", `${(index % 2 === 0 ? -1 : 1) * (34 + index * 7)}px`);
    card.style.setProperty("--pop-y", `${-38 - index * 9}px`);
  });
  window.setTimeout(() => {
    state.radarDismissedFloatIds = [...new Set(state.radarDismissedFloatIds.concat(liveItems.map((item) => item.id)))];
    state.radarFloatOpenId = "";
    state.radarFloatsCollapsed = true;
    renderBanner();
  }, 260);
}

function toggleRadarClouds() {
  const liveIds = buildRadarFloatItems(state.dashboard?.radar || {}).map((item) => item.id);
  if (!liveIds.length) return;
  if (state.radarFloatsCollapsed) {
    state.radarDismissedFloatIds = state.radarDismissedFloatIds.filter((id) => !liveIds.includes(id));
    state.radarFloatsCollapsed = false;
    const radarPanel = document.getElementById("market-radar");
    if (radarPanel) {
      radarPanel.classList.remove("floats-collapsed");
    }
    renderBanner();
    return;
  }
  popAllRadarClouds();
}

function startRadarRefresh() {
  window.clearInterval(state.radarTimer);
  state.radarTimer = window.setInterval(() => {
    loadRadar({ silent: true }).catch((error) => {
      logNonAbort(error);
    });
  }, 900000);
}

async function loadConfig() {
  setStatus("Loading config");
  state.config = await api("/api/config");
  document.getElementById("provider-select").value = state.config.provider || "yahoo";
  document.getElementById("alpha-key").value = state.config.alphaVantageApiKey || "";
  document.getElementById("llm-base-url").value = state.config.localLlmBaseUrl || "http://127.0.0.1:11434";
  document.getElementById("llm-model").value = state.config.localLlmModel || "Bonsai-8B-1bit";
  renderTopbar();
}

async function loadPresets() {
  const payload = await api("/api/presets");
  state.presets = payload.presets || [];
  renderPresets();
}

async function loadSavedWatchlists() {
  const payload = await api("/api/watchlists");
  state.savedWatchlists = payload.watchlists || [];
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
  }, 1800000);
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
    primeActiveTickerSelection(cleaned);
    const knownName =
      state.dashboard?.watchlist?.find((item) => item.symbol === cleaned)?.name
      || state.recentTickers.find((item) => item.symbol === cleaned)?.name
      || "";
    pushRecentTicker(cleaned, knownName);
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
  const ranges = ["1D", "3D", "5D", "1M", "1Y"];
  const key = `${symbols.join(",")}::${ranges.join(",")}`;
  if (state.historyWarmupKeys.has(key)) return;
  state.historyWarmupKeys.add(key);
  const run = () => {
    api("/api/history/warm", {
      method: "POST",
      timeoutMs: 6000,
      body: JSON.stringify({ symbols, ranges }),
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

async function refreshDashboard() {
  const requestId = ++state.dashboardRequestId;
  setStatus("Refreshing");
  loadOverviewFast({ silent: true }).catch((error) => {
    logNonAbort(error);
  });
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
  pushRecentTicker(payload.active.symbol, payload.active.name);
  persistWatchlist();
  nextFrame(() => {
    renderCorePanels();
  });
  deferWork(() => {
    if (requestId !== state.dashboardRequestId) return;
    renderLab();
    renderAcademy();
    renderResearch();
  });
  startQuoteStream();
  state.bootReady = true;
  document.body.classList.add("app-ready");
  document.body.classList.remove("app-booting");
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

function loadSectorHistory() {
  try { return JSON.parse(localStorage.getItem(SECTOR_MATRIX_STORAGE_KEY) || "{}"); }
  catch { return {}; }
}

function saveSectorHistory(market, period, sectors) {
  try {
    const history = loadSectorHistory();
    if (!history[market]) history[market] = {};
    if (!history[market][period]) history[market][period] = [];
    const snap = { ts: Date.now(), sectors };
    history[market][period].unshift(snap);
    // Keep last 90 snapshots per market+period
    history[market][period] = history[market][period].slice(0, 90);
    localStorage.setItem(SECTOR_MATRIX_STORAGE_KEY, JSON.stringify(history));
  } catch { /* quota */ }
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

function renderSectorMatrix(sectors, updatedAt) {
  const grid = document.getElementById("sector-matrix-grid");
  const footer = document.getElementById("sector-matrix-updated");
  if (!grid) return;
  if (!sectors?.length) {
    grid.innerHTML = `<div class="sector-matrix-empty">Loading sector data…</div>`;
    return;
  }
  const sorted = [...sectors].sort((a, b) => b.changePct - a.changePct);
  grid.innerHTML = sorted.map((s) => {
    const pct = Number(s.changePct || 0);
    const color = sectorHeatColor(pct);
    const sign = pct >= 0 ? "+" : "";
    const intensity = Math.min(Math.abs(pct) / 3, 1);
    return `
      <div class="sector-tile" style="--heat:${color}; --intensity:${intensity.toFixed(2)}">
        <span class="sector-tile-label">${s.label}</span>
        <strong class="sector-tile-pct ${pct >= 0 ? "positive" : "negative"}">${sign}${pct.toFixed(2)}%</strong>
        ${s.price ? `<em class="sector-tile-price">${s.price.toLocaleString()}</em>` : ""}
      </div>
    `;
  }).join("");
  if (footer && updatedAt) {
    const age = Math.round((Date.now() - new Date(updatedAt).getTime()) / 60000);
    footer.textContent = `Updated ${age < 1 ? "just now" : `${age}m ago`} · cached 15 min · history saved locally`;
  }
}

async function fetchSectorMatrix(market, period) {
  const grid = document.getElementById("sector-matrix-grid");
  if (grid) grid.innerHTML = `<div class="sector-matrix-empty">Fetching ${market} sectors…</div>`;
  try {
    const data = await api(`/api/sectors?market=${encodeURIComponent(market)}&period=${encodeURIComponent(period)}`);
    if (data?.sectors?.length) {
      saveSectorHistory(market, period, data.sectors);
      renderSectorMatrix(data.sectors, data.updatedAt);
    }
  } catch {
    // Fall back to last cached local history snapshot
    const history = loadSectorHistory();
    const snap = history?.[market]?.[period]?.[0];
    if (snap?.sectors) {
      renderSectorMatrix(snap.sectors, new Date(snap.ts).toISOString());
    } else if (grid) {
      grid.innerHTML = `<div class="sector-matrix-empty">Sector data unavailable. Server may still be starting.</div>`;
    }
  }
}

function initSectorMatrix() {
  const marketSelect = document.getElementById("sector-matrix-market");
  const periodTabs = document.querySelectorAll(".sector-period-tab");
  if (!marketSelect) return;

  let currentMarket = marketSelect.value;
  let currentPeriod = "1D";

  // Show last local snapshot immediately while fetching
  const cachedSnap = loadSectorHistory()?.[currentMarket]?.[currentPeriod]?.[0];
  if (cachedSnap?.sectors) renderSectorMatrix(cachedSnap.sectors, new Date(cachedSnap.ts).toISOString());

  fetchSectorMatrix(currentMarket, currentPeriod);

  marketSelect.addEventListener("change", () => {
    currentMarket = marketSelect.value;
    const snap = loadSectorHistory()?.[currentMarket]?.[currentPeriod]?.[0];
    if (snap?.sectors) renderSectorMatrix(snap.sectors, new Date(snap.ts).toISOString());
    fetchSectorMatrix(currentMarket, currentPeriod);
  });

  periodTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      periodTabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      currentPeriod = tab.dataset.period;
      const snap = loadSectorHistory()?.[currentMarket]?.[currentPeriod]?.[0];
      if (snap?.sectors) renderSectorMatrix(snap.sectors, new Date(snap.ts).toISOString());
      fetchSectorMatrix(currentMarket, currentPeriod);
    });
  });
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
      state.eventCategoryPinned = true;
      state.eventCategory = button.dataset.category;
      state.eventLastQuery = "";
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
      activateTab(tab.dataset.tab);
    });
  });
  document.getElementById("compact-menu-toggle")?.addEventListener("click", () => {
    const menu = document.getElementById("compact-section-menu");
    const isOpen = !menu?.classList.contains("open");
    menu?.classList.toggle("open", isOpen);
    document.getElementById("compact-menu-toggle")?.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });
  window.addEventListener("resize", () => {
    if (!state.impactGraphCy) return;
    window.clearTimeout(state.impactResizeTimer);
    state.impactResizeTimer = window.setTimeout(() => {
      state.impactGraphCy?.resize();
      state.impactGraphCy?.fit(undefined, 34);
    }, 120);
  });

  const settingsDialog = document.getElementById("settings-dialog");
  document.getElementById("open-settings").addEventListener("click", () => settingsDialog.showModal());
  document.getElementById("toggle-market-board").addEventListener("click", () => {
    state.boardHidden = !state.boardHidden;
    persistWatchlist();
    renderBoard();
  });
  document.getElementById("pop-radar-clouds").addEventListener("click", () => {
    toggleRadarClouds();
  });
  document.getElementById("impact-fit")?.addEventListener("click", () => state.impactGraphCy?.fit(undefined, 34));
  document.getElementById("impact-reset")?.addEventListener("click", () => {
    if (!state.impactGraphCy) return;
    state.impactGraphCy.layout({
      name: "breadthfirst",
      directed: true,
      padding: 34,
      spacingFactor: 1.1,
      animate: true,
      roots: ["#bonds", "#inflation", "#policy"],
    }).run();
    window.setTimeout(() => state.impactGraphCy?.fit(undefined, 34), 320);
  });
  document.getElementById("impact-zoom-in")?.addEventListener("click", () => {
    if (!state.impactGraphCy) return;
    state.impactGraphCy.zoom({
      level: Math.min(1.8, state.impactGraphCy.zoom() * 1.16),
      renderedPosition: { x: state.impactGraphCy.width() / 2, y: state.impactGraphCy.height() / 2 },
    });
  });
  document.getElementById("impact-zoom-out")?.addEventListener("click", () => {
    if (!state.impactGraphCy) return;
    state.impactGraphCy.zoom({
      level: Math.max(0.45, state.impactGraphCy.zoom() / 1.16),
      renderedPosition: { x: state.impactGraphCy.width() / 2, y: state.impactGraphCy.height() / 2 },
    });
  });
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
      pushRecentTicker(payload.symbol);
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
  document.body.classList.add("app-booting");
  setStatus("Loading data");
  bindEvents();
  initSectorMatrix();
  render();
  startMarketClockTimer();
  loadOverviewFast({ silent: true }).catch((error) => {
    logNonAbort(error);
  });
  const dashboardPromise = refreshDashboard();
  const backgroundLoads = Promise.allSettled([loadConfig(), loadPresets(), loadSavedWatchlists()]);
  try {
    await dashboardPromise;
  } catch (error) {
    logNonAbort(error);
    setStatus("Backend slow");
    setBootMessage("Dashboard API is reachable, but the first full refresh is taking longer than usual.");
  }
  startRadarRefresh();
  backgroundLoads.then(() => {
    flashStatus("Workspace ready", 1200);
  });
  window.setInterval(refreshDashboard, 180000);
  startEventRefresh();
}

init().catch((error) => {
  logNonAbort(error);
  setStatus("Backend check failed");
  setBootMessage("Backend check failed.", `Open ${API_BASE || window.location.origin || "http://127.0.0.1:8000"} and refresh once the server is running.`);
});
