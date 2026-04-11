# Market Graph Architecture

Keep this simple in a Karpathy-style way:

1. sync plain-text universes
2. backfill historical series once
3. cache older data locally
4. build relation graphs from durable files
5. let the UI read precomputed structure instead of recomputing everything on every load

## Core files

- `data/universes/*.json`: index membership and company metadata
- `financial_board.db`: cached historical series and macro payloads
- `data/relations/*.json`: relation graph ready for UI/analysis
- `scripts/sync_universes.py`: refresh index membership
- `scripts/backfill_history.py`: seed or extend local historical cache
- `scripts/build_relations.py`: derive graph edges from cached history
- `scripts/prepare_market_graph.py`: one-command orchestration

## Graph design

Use three edge families:

- structural edges: same sector / same index bucket
- market edges: rolling return correlation from cached history
- macro edges: rates / inflation / policy transmission already modeled in the dashboard

This keeps the graph explainable:

- structural says who should move together
- market says who has moved together
- macro says why the move may matter now

## Papers informing this structure

- Temporal Relational Ranking for Stock Prediction
  - https://arxiv.org/abs/1809.09441
  - Takeaway: relations between stocks help ranking/prediction more than isolated per-stock modeling.

- HIST: A Graph-based Framework for Stock Trend Forecasting via Mining Concept-Oriented Shared Information
  - https://arxiv.org/abs/2110.13716
  - Takeaway: concept and shared-information graphs matter, not just raw pairwise correlation.

- Chronos: Learning the Language of Time Series
  - https://arxiv.org/abs/2403.07815
  - Takeaway: modern forecasting layers can sit on top of a simpler durable data pipeline.

- TimesFM
  - https://arxiv.org/abs/2310.10688
  - Takeaway: large time-series models are useful overlays, but the stored time-series substrate should remain simple and reusable.

## Rules for extending

- Never make the UI depend on a one-off scraping path for old data.
- Persist older histories locally and update incrementally.
- Prefer additive metadata over changing response shapes destructively.
- Separate facts from interpretation: cached series are facts, relation labels are interpretation.
