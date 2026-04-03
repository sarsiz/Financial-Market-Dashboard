const STORAGE_KEYS = {
  watchlist: "financial-board-fullstack-watchlist",
  activeTicker: "financial-board-fullstack-active",
  recentTickers: "financial-board-recent-tickers",
  chartRange: "financial-board-chart-range",
  chartFeatures: "financial-board-chart-features",
  eventCategory: "financial-board-event-category",
  boardHidden: "financial-board-market-board-hidden",
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
  radarFloatsCollapsed: false,
  eventCategoryPinned: false,
  recentLastAdded: "",
  recentAddTimer: null,
  radarFreshFloatIds: [],
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
  localStorage.setItem(STORAGE_KEYS.boardHidden, state.boardHidden ? "1" : "0");
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
  { matches: ["ASX", "AUSTRALIA"], timeZone: "Australia/Sydney", open: [10, 0], close: [16, 0], hoursLabel: "10:00-16:00 AEST/AEDT" },
  { matches: ["JPX", "TSE", "TOKYO"], timeZone: "Asia/Tokyo", open: [9, 0], close: [15, 0], hoursLabel: "09:00-15:00 JST" },
];

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

function buildClientMarketSession(exchange, marketState = "") {
  const exchangeLabel = String(exchange || "").toUpperCase();
  const rule = CLIENT_MARKET_SESSION_RULES.find((item) => item.matches.some((label) => exchangeLabel.includes(label)));
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
      bubble: shortenHeadline(item.title || "Market event", 4),
      summary: item.publishedAt || item.source || item.url
        ? `${formatEventTime(item.publishedAt)}${item.source || extractDomainLabel(item.url) ? ` • ${item.source || extractDomainLabel(item.url)}` : ""}`.trim()
        : "",
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
      bubble: shortenHeadline(headline, 4),
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
    bubble: shortenHeadline(item.headline || `${formatRegionLabel(item.region)} signal`, 4),
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
  const leftPad = 10;
  const rightPad = 14;
  const topPad = 14;
  const bottomPad = 8;
  const rowHeight = 52;
  const rows = Math.max(1, Math.floor((height - topPad - bottomPad) / rowHeight));
  const usableWidth = Math.max(148, width - leftPad - rightPad);
  const colStep = 142;
  const cols = Math.max(1, Math.floor(usableWidth / colStep));
  const capacity = Math.max(1, rows * cols);
  const slots = [];
  for (let index = 0; index < Math.min(count, capacity); index += 1) {
    const row = index % rows;
    const col = Math.floor(index / rows);
    slots.push({
      x: leftPad + Math.min(col, cols - 1) * Math.max(128, usableWidth / cols),
      y: topPad + row * rowHeight + (col % 2 ? 4 : 0),
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
        buildClientMarketSession(result.active.exchange || result.active.region, result.active.marketState),
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
    marketSession: buildClientMarketSession(watchItem?.exchange || previous.exchange || previous.region, watchItem?.marketState || previous.marketState),
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
  const xTickIndices = Array.from(new Set([0, Math.floor((historySeries.length - 1) / 2), historySeries.length - 1])).filter((index) => index >= 0);
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
  const quoteMap = new Map((state.dashboard?.watchlist || []).map((item) => [item.symbol, item]));
  node.innerHTML = state.recentTickers
    .map(
      (item) => {
        const quote = quoteMap.get(item.symbol);
        const priceLabel = quote ? formatCurrency(quote.price, quote.currency) : "Price pending";
        const moveClass = quote ? (Number(quote.changePercent || 0) >= 0 ? "up" : "down") : "";
        const freshClass = item.symbol === state.recentLastAdded ? "is-new" : "";
        return `
        <button class="recent-pill ${moveClass} ${freshClass} ${item.symbol === state.activeTicker ? "active" : ""}" type="button" data-symbol="${item.symbol}" title="${item.name || item.symbol}">
          <strong>${item.symbol}</strong>
          <span>${item.name || "Recent ticker"}</span>
          <em>${priceLabel}</em>
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
    const sentiment = radar.sentiment || { label: "Mixed", score: 0 };
    const score = Number(sentiment.score || 0);
    const scoreText = score > 0 ? `+${(score * 100).toFixed(0)}` : `${(score * 100).toFixed(0)}`;
    const toneClass = score > 0.2 ? "positive" : score < -0.2 ? "negative" : "neutral";
    sentimentBox.className = `radar-sentiment-box ${toneClass}`;
    sentimentBox.innerHTML = `
      <span>Radar sentiment</span>
      <strong>${sentiment.label || "Mixed"}</strong>
      <small>${scoreText} headline balance</small>
    `;
  }

  hydrateRadarFloatPositions(floatItems);
  if (floatNode) {
    floatNode.innerHTML = floatItems
      .map((item, index) => {
        const pos = state.radarFloatPositions[item.id] || floatSlots[index] || getDefaultRadarFloatSlots()[0];
        const size = item.title.length > 82 ? "large" : item.title.length > 58 ? "medium" : "small";
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
  const brief = document.getElementById("event-brief");
  const list = document.getElementById("event-list");
  const label = document.getElementById("event-summary-label");
  const active = state.dashboard?.active;
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
    brief.innerHTML = `<p class="muted">${fallbackItems.length ? "Showing the latest radar-linked headlines while the full event feed refreshes." : "Event feed is loading."}</p>`;
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

  const focusReason = state.eventCategory !== "all" && active?.eventFocus?.category === state.eventCategory
    ? `<div class="event-brief-note"><span class="event-brief-tag">Focus</span><strong>${active.eventFocus.label}</strong><p>${active.eventFocus.reason}</p></div>`
    : "";
  brief.innerHTML = `
    <p>${state.eventResult.brief || "No major updates in this category."}</p>
    <div class="event-brief-meta">Updated ${formatEventDateTime(state.eventResult.asOf)}</div>
    ${focusReason}
  `;
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
      (item) => `
        <div class="pulse-card">
          <span>${item.label}</span>
          <strong>${item.value}</strong>
          <div class="metric-trend ${typeof item.positive === "boolean" ? (item.positive ? "positive" : "negative") : "neutral"}">${item.trend}</div>
        </div>
      `,
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
  const forecast = active.forecast || emptyForecastPayload();
  const agreement = forecast.models?.agreement || { label: "Pending", score: 0, summary: "Agreement refreshing." };
  const recommendation = active.recommendation || { buy: 0, hold: 100, sell: 0, signal: "Refreshing" };

  document.getElementById("hero-ticker").textContent = `${active.symbol} · ${active.name}`;
  document.getElementById("hero-regime").textContent = active.regime;
  document.getElementById("hero-price").innerHTML = formatCurrency(active.price, active.currency)
    .split("")
    .map((char) => {
      const cls = /\d/.test(char) ? "digit" : char === "." ? "sep decimal" : char.trim() ? "sep symbol" : "sep space";
      const safe = char === " " ? "&nbsp;" : char;
      return `<span class="price-flip ${cls}">${safe}</span>`;
    })
    .join("");
  const changeNode = document.getElementById("hero-change");
  changeNode.textContent = formatPercent(active.changePercent);
  changeNode.className = `hero-change ${active.changePercent >= 0 ? "positive" : "negative"}`;
  document.getElementById("forecast-direction").textContent = forecast.direction;
  document.getElementById("forecast-confidence").textContent = `Confidence ${Number(forecast.confidence || 0).toFixed(0)}% · ${agreement.label}`;
  document.getElementById("fair-value-gap").textContent = formatPercent(forecast.fairValueGap);
  document.getElementById("event-pressure").textContent = forecast.eventPressureLabel;
  document.getElementById("model-error").textContent = `${Number(forecast.mae || 0).toFixed(1)}%`;
  document.getElementById("forecast-range").textContent = `10D projection ${formatPercent(forecast.expectedReturn)}`;
  document.getElementById("buy-sell-signal").textContent = recommendation.signal || "Balanced";
  document.getElementById("buy-sell-breakdown").textContent = `Buy ${recommendation.buy ?? 0}% · Hold ${recommendation.hold ?? 100}% · Sell ${recommendation.sell ?? 0}%`;
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
      label: active.marketState || "Live",
      help: "Current session state.",
    },
    {
      label: `Vol ${formatCompactNumber(active.volume)}`,
      help: "Current traded volume.",
    },
    {
      label: active.asOf ? new Date(active.asOf).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "Delayed",
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
    ? `Quote source: ${formatSourceLabel(active.dataSource)} • Updated ${asOf}`
    : `Quote source: ${formatSourceLabel(active.dataSource)}`;
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
      (stat) => `
        <div class="hero-stat-card">
          <span>${stat.label}</span>
          <strong>${stat.value}</strong>
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

  document.getElementById("factor-map").innerHTML = (active.relationshipCards || forecast.factors || [])
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

  document.getElementById("catalyst-list").innerHTML = (active.driverCards || forecast.triggers || [])
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
    academyBrief.innerHTML = `<div class="academy-brief-card"><strong>Loading active explainer</strong><p>The ticker-specific academy brief is being grounded on the active company and live web context.</p></div>`;
    academySources.innerHTML = `<div class="academy-source-note">Source notes will appear here.</div>`;
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
  setStatus(state.dashboard?.updatedAt ? "Live now" : "Loading data");
  document.body.classList.toggle("app-ready", state.bootReady);
  document.body.classList.toggle("app-booting", !state.bootReady);
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
  renderTopbar();
}

function renderDeferredPanels() {
  renderLab();
  renderAcademy();
  renderResearch();
  renderEventFeed();
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
        buildClientMarketSession(payload.active.exchange || payload.active.region, payload.active.marketState),
    };
  } else if (payload.active) {
    const live = quoteMap.get(state.activeTicker);
    if (live && state.dashboard.active) {
      state.dashboard.active = {
        ...state.dashboard.active,
        ...live,
        marketSession: buildClientMarketSession(live.exchange || live.region, live.marketState),
      };
    }
  }

  renderWatchlist();
  renderBoard();
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
  renderCorePanels();
  renderDeferredPanels();
  document.getElementById("lab-ticker").value = state.activeTicker;
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
    renderBanner();
    return;
  }
  popAllRadarClouds();
}

function startRadarRefresh() {
  window.clearInterval(state.radarTimer);
  state.radarTimer = window.setInterval(() => {
    loadRadar({ silent: true }).catch((error) => {
      console.error(error);
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

async function loadAcademyDetail(symbol = state.activeTicker, { silent = false } = {}) {
  const requestId = ++state.academyRequestId;
  if (!silent) {
    setStatus("Loading learn");
  }
  const result = await api(`/api/academy?symbol=${encodeURIComponent(symbol)}&web=1&llm=1`);
  if (requestId !== state.academyRequestId) return;
  state.academyDetail = result;
  state.academyCache[symbol] = result;
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
      console.error(error);
    });
  }
  refreshDashboard();
}

async function refreshDashboard() {
  const requestId = ++state.dashboardRequestId;
  setStatus("Refreshing");
  loadOverviewFast({ silent: true }).catch((error) => {
    console.error(error);
  });
  const payload = await api("/api/dashboard", {
    method: "POST",
    body: JSON.stringify({
      symbols: state.watchlist,
      active: state.activeTicker,
      chartRange: state.chartRange,
    }),
  });
  if (requestId !== state.dashboardRequestId) return;

  state.dashboard = payload;
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
      console.error(error);
    });
  loadAcademyDetail(state.activeTicker, { silent: true })
    .then(() => {
      deferWork(() => {
        if (requestId !== state.dashboardRequestId) return;
        renderAcademy();
      });
    })
    .catch((error) => {
      console.error(error);
    });
  loadRadar({ silent: true }).catch((error) => {
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
      state.eventCategoryPinned = true;
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
  document.getElementById("toggle-market-board").addEventListener("click", () => {
    state.boardHidden = !state.boardHidden;
    persistWatchlist();
    renderBoard();
  });
  document.getElementById("pop-radar-clouds").addEventListener("click", () => {
    toggleRadarClouds();
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
    primeActiveTickerSelection(payload.symbol);
    renderOverview();
    refreshDashboard().catch((error) => {
      console.error(error);
    });
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
  document.body.classList.add("app-booting");
  setStatus("Loading data");
  bindEvents();
  render();
  loadOverviewFast({ silent: true }).catch((error) => {
    console.error(error);
  });
  const dashboardPromise = refreshDashboard();
  const backgroundLoads = Promise.allSettled([loadConfig(), loadPresets(), loadSavedWatchlists()]);
  await dashboardPromise;
  startRadarRefresh();
  backgroundLoads.then(() => {
    flashStatus("Workspace ready", 1200);
  });
  window.setInterval(refreshDashboard, 180000);
}

init().catch((error) => {
  console.error(error);
  document.getElementById("headline-track").innerHTML = `<span>Backend unavailable. Start server.py to enable the full-stack dashboard.</span>`;
});
