---
type: "[[task]]"
id: TASK-0348
aliases: ["TASK-0348"]
title: "An API-error placeholder is not a turn, and a turn with no timestamp yields no badge"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: M
due: ""
depends: []
blocks: []
related: ["[[ISS-0106-Synthetic-API-Error-Entries-Are-Counted-As-Turns-And-Reported-As-Model-Switches]]", "[[ISS-0108-A-Transcript-Entry-With-No-Timestamp-Reads-As-Confidently-Cold]]"]
tests: []
---

# An API-error placeholder is not a turn

Fixes [[ISS-0106-Synthetic-API-Error-Entries-Are-Counted-As-Turns-And-Reported-As-Model-Switches]] (high) and [[ISS-0108-A-Transcript-Entry-With-No-Timestamp-Reads-As-Confidently-Cold]].

## Definition of Done
- [x] `_turn_from_entry` rejects any assistant entry whose `message.model` is `<synthetic>`, and any whose usage is entirely zero — before dedupe, so it can neither be counted nor become `prev`.
- [x] Rejection is on the **shape of the data** (all-zero usage), not only the sentinel string: a future placeholder under a different name must not reintroduce the defect.
- [x] `live_state` returns `None` when the last real turn carries no usable timestamp, matching the module's stated contract that every failure is an absent badge rather than a confident one.
- [x] Tests: a `<synthetic>` entry between two real turns does not become `prev`, is not counted in `turns`, and does not produce a `model-switch`; a zero-usage entry under any model name is likewise skipped; a timestampless last turn yields `None`.
- [x] The fleet re-scan is re-run and the corrected counts recorded in [[TASK-0352-The-Scan-Committed-And-The-Figures-Corrected]].

## Notes
The harm is not the count. It is that the placeholder becomes the *previous* turn, so a retry seconds after a connection reset makes a 151-hour idle gap read as 52 seconds and lands the event in `model-switch` with `prev_model: "<synthetic>"` — corrupting the exact statistic the feature was argued from.
