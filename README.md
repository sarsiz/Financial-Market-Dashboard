# Financial Board

Full-stack dark financial dashboard with:

- functional Python backend and browser frontend
- support for US symbols plus exchange-suffixed markets like NSE (`.NS`), BSE (`.BO`), ASX (`.AX`), JPX (`.T`), and more
- live quote, history, market-pulse, and headline fetching with offline fallback
- explainable multi-factor forecasting and walk-forward validation
- saved watchlists persisted in SQLite
- a learning tab that explains what the signals mean

## Stack

- `server.py`: threaded Python HTTP server, JSON API, SQLite watchlist storage, market data adapters, forecast engine
- `index.html`, `styles.css`, `app.js`: dashboard client
- `financial_board.db`: created automatically on first run, now stores saved watchlists and local historical-price cache entries
- `config.json`: created automatically when you save provider settings
- local LLM features are pinned to `Bonsai-8B-1bit` through the Ollama-compatible endpoint

## Technical Summary

This platform is built as a lightweight full-stack app with a browser client and a Python server:

- the frontend is a static single-page dashboard built with plain `HTML`, `CSS`, and modular `JavaScript`
- the backend is a threaded Python HTTP server that serves the UI, normalizes ticker symbols, fetches market/news data, computes forecasts, and exposes JSON APIs
- market data is pulled server-side from layered providers, then normalized into one response shape for the UI
- historical price series are cached locally in SQLite so previously viewed symbols load faster on later visits
- live quote updates are pushed to the UI through server-sent events
- forecasting and model-lab outputs are computed on the backend so the browser stays fast and thin
- the client now renders in stages, so the active quote and overview paint first while slower Academy and event explainers fill in afterward
- first load is optimized so the dashboard request starts immediately, while presets, settings, saved lists, and deeper explainers stream in after the first useful paint
- event flow is now timestamp-aware and significance-ranked, so important recent and prior events remain visible with source and publish time
- large charts now carry timestamp-aware history series, axis labels, and hover inspection instead of only raw close arrays
- local-LLM features are pinned to `Bonsai-8B-1bit`, even if another model name is saved in config, to keep inference lighter and more predictable

## Architecture

```mermaid
flowchart LR
  A["Browser UI<br/>index.html / styles.css / app.js"] --> A1["Progressive Boot<br/>core quote first, deferred academy/events"]
  A1 --> B["Python App Server<br/>server.py"]
  B --> C["Quote + History Adapters<br/>Yahoo / Google Finance fallback / Alpha Vantage"]
  B --> D["News + Event Retrieval<br/>Google News RSS / RSS / search / ranking"]
  B --> E["Forecast + Backtest Engine<br/>classic factors / modern overlay / validation"]
  B --> F["Local Storage Layer<br/>SQLite watchlists + history cache"]
  B --> G["Local LLM Integration<br/>Bonsai-8B-1bit via Ollama-compatible endpoint"]
  B --> H["SSE Quote Stream<br/>sub-second live updates"]
  C --> C1["Timestamped History Series<br/>chart labels / hover inspection"]
  D --> D1["Event Significance Layer<br/>recency + catalyst scoring + source notes"]
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

The current suite covers:

- backend history caching and fallback behavior
- dashboard assembly and model-lab payload shape
- timestamped and significance-ranked event feed responses
- local LLM config pinning to `Bonsai-8B-1bit`
- recommendation and backtest regression checks
- frontend HTML and JavaScript contract checks for the main dashboard panels and tabs

## What is functional now

- add/search tickers globally from the UI
- quick-load presets for NASDAQ, S&P 500 leaders, NSE leaders, and macro baskets
- fetch quotes and historical charts from backend market adapters
- cache previously fetched historical series locally so already-viewed tickers load faster on later visits
- show urgent market banner headlines on the main screen
- render timestamp-aware charts with X/Y axes and hoverable value/date inspection
- compute explainable forecast direction, confidence, fair-value gap, and factor attribution
- compare classic quant signals with a modern overlay and surface whether both agree or diverge
- run scenario tests with walk-forward validation, hit-rate, and error metrics
- teach the active ticker through classic quant formulas such as momentum, z-score, volatility, volume ratio, beta, valuation, and drawdown inside Academy
- enrich Academy with ticker-specific explainers grounded on live market state plus web search results and optional local-LLM summarization
- rank and timestamp event flow items so major catalysts remain visible with source, publish time, and impact score
- save and reload watchlists through SQLite

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
- local SQLite history cache for already-tracked symbols

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
- `GET /api/presets`
- `GET /api/search?q=AAPL`
- `GET /api/watchlists`
- `POST /api/watchlists`
- `POST /api/dashboard`
- `POST /api/lab`

## Validation and limitation

This is a decision-support dashboard, not personalized investment advice.
The forecasting logic is research-inspired and explainable, but it is still heuristic and should be treated as an analytical aid rather than an execution model.
