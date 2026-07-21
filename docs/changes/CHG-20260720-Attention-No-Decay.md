---
type: "[[change]]"
id: CHG-20260720-Attention-No-Decay
aliases: ["CHG-20260720-Attention-No-Decay"]
title: "Attention states no longer decay — needs-input/waiting persist until acted or dismissed (REQ-0018)"
status: merged
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
impacts: ["agent-state decay window (server + poller)", "agent inbox / rail-dot persistence"]
issues: []
features: ["[[FEAT-0030-Agent-Inbox]]"]
related: ["[[TASK-0175]]", "[[REQ-0018]]"]
---

# Attention states no longer decay (REQ-0018)

## Summary

`needs-input` and `waiting` were in the agent-state decay set, so after the 600s window they flipped to `idle` and disappeared from the inbox, rail dot, and tally. A genuinely-blocked agent sends no further events while waiting on a permission prompt, so it decayed identically to a dead process — you could step away for >10 min and return to an empty inbox while an agent was still blocked. That defeated the exact "what needs me while I was away?" guarantee REQ-0018 was written to provide.

Fix: `_AGENT_DECAYABLE_STATES` (server) and `DECAYABLE` (poller) are now `{busy}` only. A working agent that goes silent still idles its rail dot (a dead worker), but attention states persist until a later hook event supersedes them (you acted → busy/next turn), `SessionEnd` clears them, or you dismiss the row via the existing ✕ control. The ack/read-state (pulse when unseen → static once seen) keeps a stale row from crying wolf without dropping it.

## Verification

New test `test_lazy_decay_does_not_touch_attention_states` (parametrized needs-input + waiting) — passes with the fix, fails without (adequacy checked). Full suite 220 passed; tsc clean. Independent review (opus) re-verified all three decay layers and downstream persistence, and confirmed REQ-0018 is now satisfied (advanced to verified).

Files: `src/project_os_cockpit/server.py`, `desktop/src/ipc/agent-state-poller.ts`, `tests/test_cockpit_state.py`.
