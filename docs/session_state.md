# Session State Compatibility Entry - 2026-05-09

The active cross-assistant baton has moved to `.ai-context/`.

Read these first:

1. `.ai-context/05-current-state.md`
2. The top entry of `.ai-context/06-session-log.md`

This file remains only as a compatibility pointer for older instructions that
still say to read `docs/session_state.md` first. Do not maintain a separate
dynamic state here; update `.ai-context/05-current-state.md` and prepend to
`.ai-context/06-session-log.md` instead.

Latest migrated source:

- Previous baton: `docs/session_state.md` from 2026-05-08
- Latest audit record: `docs/paper/EXPERIMENT_ENVIRONMENT_AND_SYNC_STATUS_20260508.md`
- Current goal at migration: manuscript drafting under evidence-boundary guardrails
- Next safe step at migration: decide whether to archive the 27 server Stage 5A
  `best_model.pt` files locally, using a separate archive/package path and
  hash checks; do not overwrite local `results/` or Stage 5A/5B roots by default.
