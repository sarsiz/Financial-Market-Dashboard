# Financial Board Improvement Plan

This plan keeps the existing architecture: `server.py` owns APIs and computation,
`app.js` owns client state and rendering, and `index.html`/`styles.css` own the UI
shell. Work should continue through shared region adapters and bond-led market
context rather than one-off country or stock rules.

## Product principles

- Lead with the smallest useful market view; reveal depth on demand.
- Treat bonds as the macro anchor for inflation, policy, events, equities, and
  watchlist implications.
- Separate observed facts, interpretation, scenarios, risks, confidence,
  unknowns, timestamps, and source labels.
- Never describe fallback or cached data as live.
- Keep response-shape changes additive so panels can render progressively.
- Automate routine deterministic maintenance; keep development and evaluation
  utilities on the command line.

## Phase 1: Safety, correctness, and a simpler shell

Status: implemented.

- Redact stored API secrets from browser responses and preserve omitted secrets
  during settings updates.
- Restrict local-model requests to loopback addresses, block redirects, and
  bound response sizes.
- Validate request origins, content types, payload sizes, symbols, and operator
  job identifiers.
- Replace wildcard CORS with local-origin protections and add browser security
  headers.
- Remove present-day context from historical backtests and avoid retraining an
  unchanged residual model.
- Rename prescriptive buy/hold/sell presentation to upside/base/downside
  scenarios while keeping deprecated aliases for API compatibility.
- Consolidate navigation into one accessible tab system.
- Add a single-column mobile layout and collapsible watchlist.
- Defer the large NSE heat-map request and history warm-up until the panel is
  near the viewport.
- Add an Operations tab for fixed, allowlisted maintenance workflows.

Acceptance checks:

- Automated server, route, and UI-contract tests pass.
- No raw credentials or local data paths appear in the diff.
- Desktop and mobile views have no horizontal overflow.
- Only one tab panel is active at a time and keyboard navigation works.
- An idle Overview load does not start the heat-map history warm-up.

## Phase 2: Faster data delivery

Priority: high.

1. Split `/api/dashboard` into stable, independently cached modules for macro,
   ticker dossier, events, relations, and methodology.
2. Add `ETag`/`If-None-Match` support for stable JSON and static assets.
3. Use one live-update coordinator: server-sent events while healthy, bounded
   polling only as fallback.
4. Cancel or supersede stale symbol, region, and range requests on the client.
5. Persist provider health and latency so the quote chain starts with the best
   recently healthy source.
6. Add per-endpoint timing and cache-hit metrics without recording watchlists or
   secrets.
7. Move expensive deterministic calculations to bounded background jobs and
   return last-known-good labelled results while they refresh.

Targets:

- First useful cached render under 500 ms on a typical local machine.
- Overview API p95 under 300 ms from cache.
- No duplicate live quote request for the same symbol window.
- No unbounded worker, queue, or response growth.

## Phase 3: Decision-quality and data integrity

Priority: high.

1. Introduce a shared evidence envelope with `value`, `asOf`, `source`,
   `sourceType`, `isFallback`, `confidence`, and `unknowns`.
2. Add point-in-time fixtures for backtests so revisions and future information
   cannot leak into historical samples.
3. Version model features, training inputs, and validation windows.
4. Add region adapters for calendars, currencies, policy rates, yield curves,
   benchmarks, and inflation releases.
5. Make contradictions explicit when providers disagree; do not silently blend
   values.
6. Add freshness policies by market session and data type.
7. Record deterministic lineage from bond facts to macro interpretation,
   equity context, and watchlist implications.

Targets:

- Every decision-support panel exposes timestamp and source state.
- Backtests are reproducible from local cached inputs.
- Region additions require config and adapters, not duplicated route logic.

## Phase 4: Professional UI and accessibility

Priority: medium.

1. Add a compact design-token layer for spacing, typography, color, elevation,
   and state.
2. Standardize loading, empty, fallback, stale, partial, and error states.
3. Reduce card density by making the Overview an executive summary and moving
   diagnostics into contextual drawers.
4. Provide saved views for macro, equity, event, and watchlist workflows.
5. Add accessible chart summaries, visible focus, reduced-motion support, and
   contrast checks.
6. Preserve user context across region and ticker changes without retaining
   private data outside local storage.

Targets:

- WCAG 2.2 AA keyboard and contrast checks on primary flows.
- No layout shift when live values replace skeletons.
- Common tasks are reachable in two interactions or fewer.

## Phase 5: Operations and resilience

Priority: medium.

Dashboard buttons should remain limited to safe, routine workflows:

- Refresh macro foundations and universe manifests.
- Refresh the timestamped market-event cache.
- Prepare the deterministic market relations graph.
- Rebuild local knowledge indexes.

Keep migrations, destructive cleanup, development smoke tests, evaluations, and
ad-hoc backfills as explicit command-line operations.

Next improvements:

1. Persist resumable job state with bounded logs and cancellation.
2. Show input scope, last success, data changed, duration, and failure reason.
3. Add single-flight locks and resource limits per workflow.
4. Add backup/restore validation for local cache schemas.
5. Add a read-only diagnostics bundle that excludes secrets and local user data.

## Delivery discipline

For every phase:

1. Define the user-facing behavior and failure state first.
2. Inspect existing callers and response shapes.
3. Make additive, deterministic changes.
4. Add tests for intent, fallback labels, and stale-data behavior.
5. Verify the real browser at desktop and mobile sizes.
6. Report anything skipped, mocked, stale, or unverified.
