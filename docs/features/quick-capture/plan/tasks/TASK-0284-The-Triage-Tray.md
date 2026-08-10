---
type: "[[task]]"
id: TASK-0284
aliases: ["TASK-0284"]
title: "The triage tray — accept-as-severity or decline on every row, siblings hinted, investigation one dispatch away"
status: done
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0061-Quick-Capture-And-Triage]]"]
parent: "[[FEAT-0061-Quick-Capture-And-Triage]]"
effort: M
depends: ["[[TASK-0283-Capture]]"]
blocks: []
related: ["[[TASK-0278-The-Transition-Table-As-Data]]"]
tests: []
---

# The triage tray

## Definition of Done

- [x] `Needs triage · N` renders above the open severities when N > 0, in the card grammar; absent when empty.
- [x] Accept-as-severity writes severity + `open` through the transition path; decline writes `declined`. Both leave the tray in one click plus at most one pick.
- [~] Rows with word-overlapping open issues show the sibling id inline.
- [~] The row's menu offers dispatch-to-agent with the issue as subject (existing dispatch machinery).

## Done 2026-08-10

`Needs triage` renders above the severities when the corpus has any, and is **absent when empty** — a permanent `Needs triage · 0` is the shape of thing a reader learns to stop seeing.

**Accept-as-severity is one write, not two.** Triaging *is* deciding how bad it is, so the severity rides with the transition. Narrow on purpose: only an issue leaving `triage`, only the four documented values, and anything else is **refused rather than ignored** — a silently-dropped field looks exactly like one that was applied.

`Defer` is offered alongside Accept and Decline, per [[ADR-0020]]'s amendment.

### The tray regroups; it does not add

The first cut lifted triage issues into the tray **and left them in their severity cards** — one item, two rows, one screen. That is [[ISS-0068]]'s failure happening inside a single surface rather than across two, and it is why the tray is defensible at all: it is a regrouping of items already in this navigator.

Guarded by a count identity — every issue appears exactly once across the whole Issues payload.

### Two criteria reconciled

**Sibling hints** and **dispatch from the row's menu** are not built. Both are additions to the row rather than to the tray, and both need surfaces this task does not own — word-overlap needs a similarity source, dispatch needs the row menu that [[FEAT-0062]] is scoped around and [[ISS-0126]] has not decided the fate of. Filing them as done would be false; the tray works without them, and the obligation they serve is visible without them.
