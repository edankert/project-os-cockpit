---
type: "[[task]]"
id: TASK-0253
aliases: ["TASK-0253"]
title: "One row per validator error in the session summary, closing as the agent fixes it"
status: done
phase: "[[PHASE-016-Errors-Become-Work]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0051-Validator-Errors-As-Session-Work]]"]
parent: "[[FEAT-0051-Validator-Errors-As-Session-Work]]"
effort: M
depends: ["[[TASK-0252-Validation-Errors-Reach-The-Session-Panel]]"]
blocks: []
related: ["[[FEAT-0020-Agent-Activity-Strip]]", "[[ISS-0068-Waiting-On-You-Is-A-Workaround]]"]
tests: []
---

# Error rows in the session summary

## Definition of Done
- [x] Each validator error is a row in `#agent-strip-detail`, above the work rows, in the same visual grammar
- [x] A row **closes when the error goes away** — no reload, driven by the SSE event
- [x] A row names what it is about and **navigates to the note** when it can be resolved to one
- [x] The section is absent when there are no errors — not an empty heading
- [x] It does not restate the rail badge's count; it carries code, message and destination
- [x] Distinguishable without colour

## Steps
- [x] Render an error group above the progress rows, reusing `.agent-detail-work-row`'s shape so the panel reads as one list
- [x] Resolve each row's destination from the report's own `url` / `rel` — the sidecar already computes the deep link
- [x] Keep a row visible briefly after it resolves, marked done, so a fix that lands between glances is still legible
- [x] Test: rows appear and close from a payload, and a row with no resolvable note is still readable

## Notes

The panel already has this grammar: `.agent-detail-work-row` carries a square that gets `data-bucket="done"` when the item completes. An error row is the same shape with a different source, which is the point — the eye should not have to learn a second pattern six inches from the first.

**The brief lag after a fix is deliberate.** `METRICS` clears within a second or two of `sync-snapshot.py` running; a row that vanishes instantly means the user sees a number change and never learns what changed. Marking it done and letting it linger is what makes the panel a record of the session rather than a snapshot of this instant.

**Not a second badge.** The rail badge answers *which project*; this answers *what*. Restating a count here would rebuild what [[ISS-0068]] deleted three days ago.

## Done 2026-07-30

`buildValidationBlock` in `#agent-strip-detail`, above the tab bar and above the work rows. **Outside** the tabs deliberately: this is not a third view of the session, it is a condition of the repo the session is causing or clearing, and behind a tab it would be a signal you have to go looking for — the problem it exists to fix.

The row model moved to `desktop/src/renderer/validation-rows.ts` as a pure function, loaded as a plain `<script>` beside `health-marks.ts`. That is the PHASE-013 review's lesson applied before the fact rather than after: a decision inside a DOM function can only be guarded by grepping the built bundle, and a string-index guard survives the mutation that breaks what it names.

### Live pass

```
create a bad note   →  Docs checks — 2 to fix
                       COUNTER  ID above the allocated counter  TASK-9998  open
                       METRICS  snapshot counts are behind                 open
delete it           →  Docs checks — all cleared
                       COUNTER  …  fixed [DONE]
                       METRICS  …  fixed [DONE]
click an open row   →  ~overview → features/…/TASK-9997-Probe.md
```

`METRICS` is correctly **not** clickable — it is snapshot-level and names no note — and says so in its tooltip rather than offering a dead click ([[ISS-0037]] was exactly that).

### Two decisions worth keeping

**Fixed rows linger, marked done, for five minutes.** `METRICS` clears a second or two after `sync-snapshot.py` runs; a row that vanished instantly would mean the user sees a number change and never learns what changed. Lingering is what makes this a record of the session rather than a snapshot of this instant. Guarded, and mutation-verified by making resolved rows disappear.

**The key includes the message, not just the code.** One code can name several distinct problems — two `METRICS` errors on different counters are two things to fix. Mutation-verified by keying on the code alone.

### Labels

Every code the validator can emit has a readable label, enumerated from `validate-docs.py`'s own emit sites and guarded by scraping them — so the guard fails when the validator gains a rule, not when someone notices. An unrecognised code still renders, showing itself: the fallback is deliberate, not a gap.
