# Financial Board

Full-stack dark financial dashboard with:

- functional Python backend and browser frontend
- support for US symbols plus exchange-suffixed markets like NSE (`.NS`), BSE (`.BO`), ASX (`.AX`), JPX (`.T`), and more
- live quote, history, market-pulse, and headline fetching with offline fallback
- multi-region macro + markets framing with US and India as the first supported regions
- bond-market-first regional analysis covering yields, inflation, policy, events, equity context, and watchlist implications
- explainable multi-factor forecasting and walk-forward validation
- a methodology tab that maps quant concepts, live inputs, cadence, and factor flow
- saved watchlists persisted in SQLite
- a learning tab that explains what the signals mean

## Stack

- `server.py`: threaded Python HTTP server, JSON API, SQLite watchlist storage, market data adapters, forecast engine
- `index.html`, `styles.css`, `app.js`: dashboard client
- `financial_board.db`: created automatically on first run, now stores saved watchlists and local historical-price cache entries
- `data/universes/`: synced index and exchange membership files
- `data/relations/`: precomputed stock relation graphs built from cached history
- `data/company_networks.json`: local company/entity relationship hints for deeper market maps
- `data/factors/`: factor cadence and update-significance datasets
- `data/papers/`: local paper registry for research-backed factor and graph design
- `vendor/cytoscape.min.js`: local graph engine for the dependency workspace
- `data/macro/`: local macro factor store and sync manifest
- `vault/market-map/`: local markdown notes generated from universes, relation graphs, papers, and playbooks
- `config.json`: created automatically when you save provider settings
- local LLM features are pinned to `Bonsai-8B-1bit` through the Ollama-compatible endpoint
- `kb/`: durable local knowledge base for macro, region, sector, company, and playbook notes
- `scripts/sync_macro_factor_store.py`: local macro-factor downloader / manifest builder
- `scripts/build_research_protocol_vault.py`: research note generator
- `scripts/build_agent_memory_vault.py`: builds manifest, templates, and working-note folders
- `scripts/update_knowledge_base.py`: refreshes generated markdown and checks docs for stale wording
- `vault/market-map/concepts/`: quant concept notes
- `vault/market-map/workflows/`: methodology flow notes
- `vault/market-map/_meta/`: vault manifest and memory protocol
- `vault/market-map/inbox/`, `sessions/`, `sources/`, `templates/`: working-memory and note-promotion structure

## Technical Summary

This platform is built as a lightweight full-stack app with a browser client and a Python server:

- the frontend is a static single-page dashboard built with plain `HTML`, `CSS`, and modular `JavaScript`
- the backend is a threaded Python HTTP server that serves the UI, normalizes ticker symbols, fetches market/news data, computes forecasts, and exposes JSON APIs
- market data is pulled server-side from layered providers, then normalized into one response shape for the UI
- multi-region payloads are built from region configs and adapter-style helper functions so new regions can be added without rewriting the dashboard
- historical price series are cached locally in SQLite so previously viewed symbols load faster on later visits
- normalized historical records are also stored locally in SQLite so old data can be reused by charts, macro analysis, and relation graphs without repeated refetches
- regional bond, inflation, events, and calendar payloads are also cached locally with TTLs and stale-safe fallback so older context is reused instead of being refetched on every dashboard load
- derived insights such as the 5D/25D moving-average signal are persisted locally so repeated dashboard refreshes reuse computed stock context
- a local macro factor store can be materialized under `data/macro/` so slower-moving official series become reusable local context instead of repeated fetches
- the overview includes a decision cockpit that combines live quote movement, local history, 5D/25D trend, radar sentiment, event risk, bonds, inflation, policy, confidence, and model error into facts, scenarios, unknowns, and monitor-next items
- the overview includes a stock dossier with day snapshot, fundamentals, moving averages, peer comparison, benchmark comparison, external consensus, unusual activity, source provenance, and public-cited influence/ownership context
- live quote updates are pushed to the UI through server-sent events
- forecasting and model-lab outputs are computed on the backend so the browser stays fast and thin
- the client now renders in stages, so the active quote and overview paint first while slower Academy and event explainers fill in afterward
- first load is optimized so the dashboard request starts immediately, while presets, settings, saved lists, and deeper explainers stream in after the first useful paint
- the browser now hits a lightweight overview endpoint first, so watchlist quotes and the active overview can paint before the heavier full dashboard finishes
- Academy and Research now degrade gracefully: they show market-structure-first content immediately, use shorter local-LLM time budgets, and fall back to web-grounded or rules-based answers when the LLM is slow
- event flow is now timestamp-aware and significance-ranked, so important recent and prior events remain visible with source and publish time
- market radar has its own refresh path and now auto-refreshes every 15 minutes without waiting for the full dashboard refresh
- market radar surfaces a compact news ticker, sentiment box, and event hotspots from live news items without the older floating cloud layer
- market radar now blends live event headlines with macro pulse and active-ticker micro context, so the section reflects both top-down and stock-specific pressure
- the overview now includes a dense market heat map, using local universe manifests, live quotes where available, and documented sector/watchlist fallbacks when a provider is missing
- every dashboard load now starts a bounded backend maintenance check, refreshes stale macro/universe scripts in the background, and exposes script status in the dashboard data-flow bar
- the stock dossier uses an auto-masonry card layout so peer comparison and other cards repack tightly across viewport sizes
- the sector matrix renders benchmark-relative performance by market, benchmark, and period with a local-cache-first path
- the dashboard now keeps a region-selected macro layer for bonds, inflation, policy, events, equity context, watchlist implications, and US-vs-India comparison
- the main overview now carries a research methodology layer showing live formulas, cadence, and factor transmission for the active ticker
- the dashboard now includes a dedicated methodology tab showing popular quant concepts, live inputs, cadence, and an animated factor flow
- watchlist implications now use a dedicated graph workspace with pan/zoom and details instead of a cramped inline SVG
- universe sync, historical backfill, and relation-graph generation are now explicit scripts so large-market datasets can be refreshed deterministically
- the top watch overview can be compacted away with a user toggle, and the radar panel stays dense by using ticker/hotspot surfaces instead of floating cards
- news retrieval now blends Google News RSS with popular publisher RSS feeds like BBC and NPR, then dedupes and ranks them server-side
- large charts now carry timestamp-aware history series, axis labels, and hover inspection instead of only raw close arrays
- local-LLM features are pinned to `Bonsai-8B-1bit`, even if another model name is saved in config, to keep inference lighter and more predictable
- factor governance and paper-backed protocol are now local datasets, so cadence, significance, provenance, and methodology are explicit rather than hidden in code

## Local Data Privacy

The public repository should contain source code, scripts, tests, and empty folder placeholders only. Local financial data is private by default:

- `data/`, `kb/`, and `vault/market-map/` are ignored except for `.gitkeep` placeholders.
- Do not commit watchlists, quote/history caches, generated universes, relation graphs, job manifests, SQLite databases, provider captures, local notes, or research vault content.
- Recreate or refresh local data with scripts at runtime instead of storing it in Git.

## Data Sources

The dashboard keeps provider usage factual and labelled. Current and candidate sources are:

- SEC EDGAR APIs: US filings and XBRL company facts.
- FRED API: US rates, inflation, policy, labor, and macro series.
- Alpha Vantage: quotes, adjusted history, market status, earnings calendar, and estimates where API keys permit.
- Google Finance: live quote edge fallback, especially for exchange-suffixed regional symbols.
- Yahoo Finance: quote summary, chart live edge, fundamentals, and public consensus fields.
- Stooq: daily CSV history fallback when live quote providers are unavailable.
- Finnhub: candidate source for analyst price targets, recommendation trends, estimates, ownership, and company profiles.
- Financial Modeling Prep: candidate source for analyst revenue/EPS estimates.
- Nasdaq Trader Symbol Directory: current-day US symbol metadata for universe sync.
- Reserve Bank of India: India policy, rates, circulars, and official macro context.
- Federal Reserve: US policy statements, rate decisions, speeches, and calendars.
- NSE India data products: official reference for India EOD/historical market data provenance.

Consensus and analyst data should be shown as public context with source, timestamp, confidence, and limitations. It should not be converted into direct buy/sell advice.

## Architecture

```mermaid
flowchart LR
  A["Browser UI<br/>index.html / styles.css / app.js"] --> A1["Progressive Boot<br/>core quote first, deferred academy/events"]
  A1 --> B["Python App Server<br/>server.py"]
  B --> C["Quote + History Adapters<br/>Yahoo / Google Finance fallback / Alpha Vantage"]
  B --> D["News + Event Retrieval<br/>Google News RSS / BBC + NPR RSS / search / ranking"]
  B --> E["Forecast + Backtest Engine<br/>classic factors / modern overlay / validation"]
  B --> F["Local Storage Layer<br/>SQLite watchlists + history cache"]
  F --> F1["Historical Records + Payload Cache<br/>old data reused locally"]
  B --> G["Local LLM Integration<br/>Bonsai-8B-1bit via Ollama-compatible endpoint"]
  B --> H["SSE Quote Stream<br/>sub-second live updates"]
  C --> C1["Timestamped History Series<br/>chart labels / hover inspection"]
  D --> D1["Event Significance Layer<br/>recency + catalyst scoring + source notes"]
  D1 --> D2["Radar Ticker + Hotspots<br/>compact news strip / sentiment / 15 min refresh"]
  F --> F2["Sector Matrix Cache<br/>benchmark-relative local snapshots"]
```

## Run

```bash
python3 server.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Research Protocol

The dashboard now keeps a local research-backed operating model:

- `data/factors/factor_registry.json`: factor significance, cadence, fact-first reading, and provenance
- `data/factors/prediction_formulas.json`: live formula lenses used in the main overview
- `data/papers/dashboard_practices.json`: paper and classic-quant practices mapped into concrete dashboard behavior
- `data/papers/quant_concepts.json`: popular quant and trading concepts used by the methodology tab
- `data/factors/methodology_flow.json`: local definition of how inputs become factors, regimes, and decision support
- `data/macro/manifest.json`: local macro-store coverage by region
- `kb/playbooks/research-backed-dashboard-protocol.md`: the repo-level methodology rulebook
- `kb/playbooks/quant-concepts-dashboard-map.md`: concise map from concepts to dashboard surfaces
- `vault/market-map/research/`: factor notes generated from the registry
- `vault/market-map/concepts/`: concept notes
- `vault/market-map/workflows/`: flow notes
- `vault/market-map/_meta/Agent Memory Protocol.md`: how agents should use durable vs working memory
- `vault/market-map/_meta/Vault Manifest.md`: coverage snapshot for the current local memory system

This lets the UI show:

- what is fact
- what is interpretation
- what cadence a factor should refresh at
- what datasets are local, partial, fallback-backed, or still missing

## Rich Market Workflow Plan

The dashboard is moving toward the useful parts of Mint, Moneycontrol, Groww, and similar market tools while keeping the current local-first architecture:

- `Market snapshot`: price, change, volume, session status, breadth, radar sentiment, and watchlist movement.
- `Sector matrix`: benchmark-relative sector performance by market, benchmark, and period with local-cache-first rendering.
- `Technical context`: 5D/25D moving-average spread, slope, trend confirmation, volatility, breakout pressure, and reversion stretch.
- `Fundamental context`: valuation, quality, project exposure, supplier risk, and sector sensitivity where local data exists.
- `Events`: market-relevant RSS/news, category filters, impact score, source timestamps, and major event overrides.
- `Decision support`: scenarios, confidence, unknowns, and monitor-next signals, not direct buy/sell instructions.
- `Local database`: historical records, cached payloads, derived insights, relation graphs, and local markdown notes.

## Local Knowledge Base

The repo keeps durable market context as plain markdown, generated where possible:

- durable memory:
  - `companies/`
  - `concepts/`
  - `papers/`
  - `playbooks/`
  - `research/`
  - `sectors/`
  - `workflows/`
- working memory:
  - `inbox/`
  - `sessions/`
  - `sources/`
  - `templates/`
  - `_meta/`

Generate or refresh it with:

```bash
python3 scripts/build_market_map_vault.py
python3 scripts/build_research_protocol_vault.py
python3 scripts/build_agent_memory_vault.py
```

Or refresh the generated notes and wording checks together:

```bash
python3 scripts/update_knowledge_base.py
```

The current suite covers:

- backend history caching and fallback behavior
- dashboard assembly and model-lab payload shape
- timestamped and significance-ranked event feed responses
- multi-source RSS aggregation for event and radar feeds
- local LLM config pinning to `Bonsai-8B-1bit`
- historical-record persistence and relation-graph wiring
- recommendation and backtest regression checks
- Wilder RSI, aligned MACD, benchmark sector matrix, and search-ranking regression checks
- frontend HTML and JavaScript contract checks for the main dashboard panels and tabs

## What is functional now

- add/search tickers globally from the UI
- quick-load presets for NASDAQ, S&P 500 leaders, NSE leaders, and macro baskets
- fetch quotes and historical charts from backend market adapters
- cache previously fetched historical series locally so already-viewed tickers load faster on later visits
- show urgent market banner headlines on the main screen
- render timestamp-aware charts with X/Y axes and hoverable value/date inspection
- switch sector matrix benchmark and period while reusing local snapshots before fetching the live edge
- compute explainable forecast direction, confidence, fair-value gap, and factor attribution
- compare classic quant signals with a modern overlay and surface whether both agree or diverge
- run scenario tests with walk-forward validation, hit-rate, and error metrics
- teach the active ticker through classic quant formulas such as momentum, z-score, volatility, volume ratio, beta, valuation, and drawdown inside Academy
- enrich Academy with ticker-specific explainers grounded on live market state plus web search results and optional local-LLM summarization
- rank and timestamp event flow items so major catalysts remain visible with source, publish time, and impact score
- highlight major active-ticker catalyst regimes visually when event pressure is elevated
- blend popular RSS feeds into radar and event flow so the news layer updates with broader publisher coverage
- save and reload watchlists through SQLite
- compare US and India using bond-first macro tabs, calendars, and watchlist implication flows
- label fact vs interpretation in the macro workflow so decision support stays transparent

## Coverage notes

- US tickers work directly, for example `AAPL`, `MSFT`, `NVDA`
- NSE tickers can be entered as `RELIANCE` with market set to `NSE`, or directly as `RELIANCE.NS`
- The same suffix pattern works for several other exchanges through the market selector

## Provider model

Default mode is a Yahoo-style no-key fallback for broad symbol coverage.
You can optionally save an Alpha Vantage API key in the settings dialog and switch the backend to `alpha_vantage` for additional enrichment where available.

Historical-price loading now uses a layered path:

- Yahoo chart API when available
- Google Finance page timeline extraction as fallback
- Alpha Vantage daily history when an API key is configured
- Stooq daily CSV as a low-request fallback for supported US symbols
- local SQLite history cache for already-tracked symbols
- local SQLite historical-record storage for durable series reuse
- SQLite payload cache for regional macro/event/calendar context with TTL-based refresh

## Outbound data and request safety

The backend now uses a guarded outbound request layer:

- HTTPS-only allowlisted hosts
- small per-host minimum intervals to avoid bombarding providers
- short response caching for repeated URLs
- TTL-based payload caches for slower macro/event/calendar paths
- local history reuse before external back-history fetches
- security headers on dashboard responses

Alternative sources currently wired:

- Yahoo Finance
- Google Finance page extraction
- Alpha Vantage, when a key is configured
- FRED / BLS / Fed / RBI for macro context
- Stooq daily CSV for supported US history fallback

## Market graph pipeline

The repo now supports a simple durable pipeline for large stock universes:

```bash
python3 scripts/sync_universes.py
python3 scripts/backfill_history.py --universe sensex30 --range 1Y
python3 scripts/backfill_history.py --universe sp500 --range 1Y
python3 scripts/backfill_history.py --universe nasdaq_listed --range 1Y --limit 250
python3 scripts/build_relations.py --universe sensex30
python3 scripts/build_relations.py --universe sp500
python3 scripts/build_relations.py --universe nasdaq_listed --limit 250
```

Or run the orchestrator:

```bash
python3 scripts/prepare_market_graph.py --nasdaq-limit 250
```

Why this shape:

- universes are stored as plain JSON manifests
- historical records are cached once and reused
- relation graphs are generated from cached history plus sector structure
- company/entity relationship nodes can be layered on top of stock graphs for deeper context
- the dashboard can consume those precomputed relations without refetching the past

The relation layer is inspired by:

- [Temporal Relational Ranking for Stock Prediction](https://arxiv.org/abs/1809.09441)
- [HIST: A Graph-based Framework for Stock Trend Forecasting via Mining Concept-Oriented Shared Information](https://arxiv.org/abs/2110.13716)
- [Chronos](https://arxiv.org/abs/2403.07815)
- [TimesFM](https://arxiv.org/abs/2310.10688)

## Market Map Notes

The repo now supports a local markdown vault in:

- `vault/market-map/Market Graph Index.md`
- `vault/market-map/companies/`
- `vault/market-map/sectors/`
- `vault/market-map/papers/`
- `vault/market-map/playbooks/`

Build it with:

```bash
python3 scripts/build_market_map_vault.py
python3 scripts/build_research_protocol_vault.py
python3 scripts/sync_macro_factor_store.py
```

To refresh the generated markdown and validate wording:

```bash
python3 scripts/update_knowledge_base.py
```

This follows the same simple pattern:

- store facts as local files
- keep derived structure explicit
- use markdown + links for durable memory
- let the dashboard read local notes instead of hiding context in runtime code

This project keeps provider calls on the server side so:

- secrets are not exposed in frontend code
- cross-origin limitations stay off the client
- provider-specific normalization is centralized

## API endpoints

- `GET /api/health`
- `GET /api/config`
- `POST /api/config`
- `GET /api/academy?symbol=ICICIBANK.NS`
- `GET /api/events?category=world&symbol=ICICIBANK.NS`
- `GET /api/overview?symbols=ICICIBANK.NS,AAPL&active=AAPL`
- `GET /api/presets`
- regional macro, inflation, policy, calendar, and comparison payloads are returned inside `POST /api/dashboard`
- `GET /api/search?q=AAPL`
- `GET /api/watchlists`
- `POST /api/watchlists`
- `POST /api/dashboard`
- `POST /api/lab`

## Validation and limitation

This is a decision-support dashboard, not personalized investment advice.
The forecasting logic is research-inspired and explainable, but it is still heuristic and should be treated as an analytical aid rather than an execution model.
