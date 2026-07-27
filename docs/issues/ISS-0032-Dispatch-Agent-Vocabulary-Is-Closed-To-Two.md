---
type: "[[issue]]"
id: ISS-0032
aliases: ["ISS-0032"]
title: "The dispatch agent vocabulary is a closed two-value union restated in four places, and its ternaries silently coerce any third agent to 'claude'"
status: triage
severity: medium
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
component: desktop
source: ["session:2026-07-27 external-review design"]
phase: "[[PHASE-999]]"
related: [ISS-0023, FEAT-0024, FEAT-0025]
tests: []
---

# Adding a third agent silently degrades to Claude

## Problem

The set of agents the cockpit can dispatch to is `claude | codex`, and it is written down in at least four places that do not agree on being a set:

| Where | Shape |
|---|---|
| `desktop/src/renderer/renderer.ts:7255` | `type DispatchAgent = 'claude' \| 'codex'` |
| `src/project_os_cockpit/cli.py:382` | `--agent` with `choices=["claude", "codex"]` |
| `renderer.ts:7308` (`loadDispatchAgent`) | `if (v === 'codex') return 'codex'; return 'claude'` |
| `renderer.ts:5983`, `5989`, `7467` | `x === 'codex' ? 'codex' : 'claude'` |

The last row is the defect. Those are not narrowing checks over a known set — they are **binary coercions**. Any value that is not the literal `'codex'` becomes `'claude'`, so a third agent does not fail, does not warn, and does not appear anywhere: it is silently relabelled as Claude in the session record, the rail dot, and the dispatch ledger.

This is [[ISS-0023]]'s shape exactly — one vocabulary restated across surfaces until they disagree — with an extra hazard the status vocabulary did not have. A status value that drifts renders in the wrong colour and gets reported. An agent value that drifts is *attributed to a different agent*, so the record says Claude did work that Claude did not do.

## Inconsistent already

`cli.py:367` documents the `signal` path's agent argument as **"Agent name (e.g. claude, codex, aider). Freeform."** So the ingestion side is already open-ended while the dispatch side is closed to two, and nothing reconciles them. A signal from `aider` is accepted and stored; a dispatch to `aider` is impossible, and a *record* of one would read as `claude`.

## How this surfaced

Designing the external-review runner (project-os-dev FEAT-0018), which needs a non-Claude model to satisfy `QUALITY.md`'s different-family gate. Kimi Code CLI turns out to fit the cockpit unusually well — its hook events (`PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, `UserPromptSubmit`) carry the same names Claude Code uses and pass JSON on stdin, so FEAT-0019's ingestion is close to drop-in. But adding it as a dispatch target lands on the coercion above on day one.

## Expected

One declaration of the agent set, consumed by every surface, with an unknown value handled explicitly — rejected, or preserved and rendered as unknown — never coerced to a sibling.

## Actual

Four declarations, three of them coercions, no test that a third value survives a round trip.

## Repro

```
grep -n "=== 'codex' ?" desktop/src/renderer/renderer.ts
```

Three coercions. Feeding `agent: 'kimi'` through the session-event path at `renderer.ts:5989` yields `'claude'`.

## Next Actions

- [ ] Decide where the agent set is declared once (the sidecar, alongside the verb registry that is already data-driven via `/api/cockpit/actions`, is the obvious candidate — it would make agents configurable the way verbs already are)
- [ ] Replace the three coercions with explicit handling of an unrecognised agent
- [ ] Reconcile the `signal` path's freeform agent with the dispatch path's closed set, in whichever direction is chosen
- [ ] Add a parity test in the shape of TST-0019: one vocabulary, asserted across every surface that restates it
- [ ] Only then add a third agent

## Notes

Filed before adding Kimi rather than after, because the whole point of [[ISS-0023]] was that this class of drift is cheap to prevent and expensive to find. Adding the third value first would have made the coercion a live misattribution bug instead of a latent one.
