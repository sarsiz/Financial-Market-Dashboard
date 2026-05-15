# Repo Guidance

- Keep the current stack: `server.py` is the backend API/computation layer, `app.js` is the client state/render layer, and `index.html`/`styles.css` define the UI shell.
- Prefer extending region-aware interfaces instead of adding new one-off country logic. Add new regions through shared config and adapter functions first.
- Treat bonds as the macro anchor. Inflation, policy, events, equity context, and watchlist implications should derive from that layer rather than from standalone stock heuristics.
- Keep decision support factual and scenario-based. Show facts, interpretation, risks, confidence, unknowns, timestamps, and source labels. Avoid direct buy/sell advice.
- Reuse existing response shapes where possible, and expand them with additive keys so the frontend can stage-render without breaking older panels.
- When live data is missing, return documented fallback/mock data with source notes instead of blank panels or invented “live” claims.
- Use the local historical cache as the source of truth for older data. Fetch the live edge, then persist the older series and reuse it rather than scraping the same back history repeatedly.
- For NSE breadth views, maintain the `nse_all` local universe manifest and queue bounded daily/history warmups for visible heatmap slices automatically; do not require manual reminders for routine daily-value storage.
- Keep universe/history/relations pipelines scriptable and deterministic. Prefer plain JSON manifests plus resumable backfill jobs over hidden one-off logic.
- Treat `vault/market-map/` as the local agent memory system. Durable notes go in stable folders like `companies/`, `concepts/`, `papers/`, `playbooks/`, `research/`, and `workflows/`; temporary captures should stay in `inbox/` or `sessions/` until promoted.
- Do not commit local data. `data/` and `kb/` may keep only folder placeholders such as `.gitkeep`; `vault/market-map/` must not be tracked at all. Never upload watchlists, caches, generated market maps, provider payloads, databases, job manifests, local notes, or research captures.
- Keep local memory simple: plain markdown, frontmatter where helpful, wiki-linkable notes, and generated indexes/manifests from scripts rather than hand-maintained sprawl.
- Read before writing: inspect callers, exports, shared helpers, response shapes, and local conventions before adding new code.
- Keep changes surgical and deterministic. Use scripts/code for refreshes, routing, retries, status, and transforms; reserve model judgment for interpretation and tradeoffs.
- Surface conflicts instead of blending contradictory patterns or sources. Keep source labels, fallback labels, timestamps, confidence, and unknowns visible.
- Treat time, token, and network budgets as real constraints. Checkpoint after meaningful steps and state anything skipped or unverified.
- Tests should verify the user-facing intent. Never claim tests pass, data is live, or a component works unless it was actually verified.
