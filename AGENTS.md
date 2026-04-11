# Repo Guidance

- Keep the current stack: `server.py` is the backend API/computation layer, `app.js` is the client state/render layer, and `index.html`/`styles.css` define the UI shell.
- Prefer extending region-aware interfaces instead of adding new one-off country logic. Add new regions through shared config and adapter functions first.
- Treat bonds as the macro anchor. Inflation, policy, events, equity context, and watchlist implications should derive from that layer rather than from standalone stock heuristics.
- Keep decision support factual and scenario-based. Show facts, interpretation, risks, confidence, unknowns, timestamps, and source labels. Avoid direct buy/sell advice.
- Reuse existing response shapes where possible, and expand them with additive keys so the frontend can stage-render without breaking older panels.
- When live data is missing, return documented fallback/mock data with source notes instead of blank panels or invented “live” claims.
- Use the local historical cache as the source of truth for older data. Fetch the live edge, then persist the older series and reuse it rather than scraping the same back history repeatedly.
- Keep universe/history/relations pipelines scriptable and deterministic. Prefer plain JSON manifests plus resumable backfill jobs over hidden one-off logic.
