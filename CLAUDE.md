# CLAUDE.md — Financial Board

Coding guidelines for this project.

---

## Project Stack

- `server.py` — backend API, data fetching, computation
- `app.js` — client state and render layer
- `index.html` + `styles.css` — UI shell
- `data/` — JSON configs and factor definitions
- `vault/market-map/` — local markdown notes and generated market context

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Every changed line should trace directly to the request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add a chart" → "Chart renders correct data, no console errors, matches design"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

## 5. Execution Guardrails

**Make deterministic work deterministic. Make uncertainty visible.**

- Use code for routing, retries, transforms, status tracking, and refresh jobs; use model judgment only for interpretation and tradeoffs.
- Treat token, time, and network budgets as hard constraints. Checkpoint or summarize before context gets noisy.
- Surface contradictory project patterns or source claims instead of averaging them into a vague compromise.
- Read exports, callers, shared helpers, and existing response shapes before writing new code.
- Tests should prove intent, not just that a line executed. Name unverified gaps plainly.
- Checkpoint after meaningful steps: what changed, what is verified, what remains risky.
- Match local conventions even when another style is personally preferable.
- Fail loud: never claim code works, data is live, or tests pass unless it was actually verified.

## 6. Project-Specific Rules

- **Local data stays local.** Do not commit files under `data/`, `kb/`, or `vault/market-map/` except `.gitkeep` placeholders. These folders may contain watchlists, caches, generated notes, databases, provider payloads, job manifests, and private research.
- **Bonds first.** Inflation, policy, equity context, and implications derive from bonds — not from standalone stock heuristics.
- **Factual decision support only.** Show facts, interpretation, risks, confidence, unknowns, timestamps, source labels. No direct buy/sell advice.
- **Fallbacks over blanks.** Return documented mock data with source notes rather than empty panels or invented "live" claims.
- **Additive API shapes.** Expand response objects with new keys — never rename or remove existing keys.
- **Historical cache is truth.** Fetch the live edge, persist the older series, reuse rather than re-scrape.
- **Vault is private memory.** Never commit generated vault content; keep only `.gitkeep` placeholders in `vault/market-map/`. See `.gitignore`.
- **Methodology tab = educational only.** Signal pattern families and formulas are public domain. Proprietary triggers, weights, and thresholds belong in `data/factors/` (gitignored) and `vault/`.
- **Region-aware first.** Extend shared region adapters — never add one-off country logic.
