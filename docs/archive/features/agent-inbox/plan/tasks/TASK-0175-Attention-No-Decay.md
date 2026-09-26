---
type: "[[task]]"
id: TASK-0175
aliases: ["TASK-0175"]
title: "Attention states must not decay — needs-input/waiting persist until acted or dismissed (REQ-0018)"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: ["[[REQ-0018]]"]
parent: "FEAT-0030"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[REQ-0018]]", "[[FEAT-0020-Agent-Activity-Surfaces]]"]
tests: ["[[TST-0009]]"]
---

# TASK-0175 — attention states must not decay

Independent review of REQ-0018 (2026-07-20) found the completeness claim unmet: `needs-input` and `waiting` were in the decayable set (`server.py` `_AGENT_DECAYABLE_STATES`, `agent-state-poller.ts` `DECAYABLE`), so a genuinely-blocked agent — which by definition sends no further events while blocked on a permission prompt — decayed to `idle` after the 600s window and vanished from the inbox, rail dot, and tally. The exact "what needs me while I was away?" failure REQ-0018 was written to prevent.

REQ-0018 is explicit: `needs-input` (act now) and `waiting` (turn finished, review) "must persist until the user acts or dismisses — not evaporate on state decay," with the read-state mechanism (pulse when unseen → static when seen, no data change) handling staleness *without* dropping the row.

Fix: remove `needs-input` and `waiting` from both decay clocks; only `busy` (working, does not need the user) still decays to idle when its process goes silent. Attention states now persist until a later hook event supersedes them (the user acted — busy/idle/next turn) or `SessionEnd` clears them. The already-shipped ack/read-state (static-once-seen) covers staleness visually.

Verification: unit test that a stale `needs-input` (older than the decay window) is NOT decayed to idle on the read path, while a stale `busy` still is. Then re-run the REQ-0018 independent review.

## Verification

`_AGENT_DECAYABLE_STATES` (server) and `DECAYABLE` (poller) are now `{busy}` only. Test `test_lazy_decay_does_not_touch_attention_states` (parametrized needs-input + waiting) asserts the read path keeps the state and `decay_tick` stays silent — passes with the fix, fails without it (adequacy checked by reverting). Full suite 220 passed, tsc clean. Independent review re-verified all three decay layers plus downstream inbox/rail persistence, and confirmed the ✕ dismiss control (`dismissAlert`) satisfies the "or dismisses" clause.
