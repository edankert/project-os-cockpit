---
type: "[[issue]]"
id: ISS-0105
aliases: ["ISS-0105"]
title: "The rail pulses identically for a session waiting two minutes and one waiting two hundred hours, so the amber never means act now"
status: fixed
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
severity: medium
component: "renderer"
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[FEAT-0020-Agent-Activity-Surfaces]]", "[[ISS-0102-The-Attention-Pill-Borrowed-Another-Surfaces-Words]]"]
tests: []
---

# The rail pulses identically for a session waiting two minutes and one waiting two hundred hours

## Problem

`.ws-square.state-waiting .ws-dot` is amber on a 1.4s pulse and means "the agent finished its turn — review it". It carries no notion of age, so a turn that ended two minutes ago and one that ended 211 hours ago are the same pixels.

Two costs to that:

1. **The pulse stops meaning anything.** Measured on this machine 2026-08-06: five of ten workspaces were pulsing amber, at ages 1 min, 50h, 185h, 209h and 211h. A signal that is on for half the fleet permanently is decoration.
2. **It hides the fact that now matters.** After an hour the prompt cache behind that session has lapsed ([[FEAT-0081]]), so resuming it re-writes the whole prefix at the cache-write rate. The two-minute one is nearly free to pick up; the 211-hour one is not. The rail says they are identical, which is precisely backwards — it shouts loudest about the ones that cost most.

Edwin's framing, which is the fix: *cold sessions always show as grey*. Then amber-pulse means "waiting **and** cheap to resume right now", which is a claim worth making, and the existing vocabulary gains a distinction instead of a third meaning.

## Repro

1. Leave a workspace's agent in `waiting` for more than an hour.
2. Look at the rail: still amber, still pulsing, indistinguishable from a session that finished seconds ago.

## Expected

A session whose last turn is older than the cache TTL reads grey, like any other resting session. Amber-pulse is reserved for work that is both waiting and still warm.

**And the transition actually happens.** A dot that would only go grey when some event arrives is the same bug wearing a different colour: the whole point is that nothing is happening in that session.

## Actual

Amber forever. Nothing repaints the rail on a clock — `updateLiveDurations` ticks every 30s but only rewrites `[data-dur-start]` text; the rail squares are painted only when an agent-state event arrives over SSE.

## Evidence

- `desktop/src/renderer/renderer.css` — `.ws-square.state-waiting .ws-dot` sets `--severity-medium` + `ws-waiting-pulse 1.4s`; the neighbouring comment for `needs-input` says the two pulse speeds exist so "answer me now" reads differently from "done, review". Age is not a dimension either of them has.
- `renderer.ts` `applyAgentStateToSquare` — paints from `agentStates`, which is fed by SSE only.
- The precedent for the fix is in that same function: `const key = state.decayed_from ? 'idle' : state.state` already demotes a stale state to the grey dot. Cold is a second reason to take the same branch.

## Scope note

**A cold session leaves NEEDS YOU entirely** (Edwin, 2026-08-06). An earlier draft of this issue kept the entry and annotated it with the resume cost; that was the weaker answer. One rule applied to both surfaces — cold is grey on the rail, and absent from the list — is simpler than two, and it needs no cost figure on the row because the row is gone.

NEEDS YOU then means *blocked on you and still cheap to pick up*, which is a list worth reading. Measured 2026-08-06 it would have dropped from five entries to one: the 50h, 185h, 209h and 211h entries leave, the 1-minute one stays.

**The consequence, stated plainly:** a genuinely blocked session becomes invisible in the list an hour after it blocks. The rail's grey square is then the only place it appears. That is the intended trade — a list that keeps everything forever is the thing being fixed — but it is a real loss of a nag, not a free win. If work is ever dropped because of it, the fix is a separate surface for stale obligations, not putting them back here.

## Next Actions

- [x] Cold demotes to the grey dot, through the branch `decayed_from` already uses
- [x] A repaint tick, so the transition happens with nothing else going on
- [x] Cold entries leave the NEEDS YOU list
- [x] The tooltip says why the square went grey
