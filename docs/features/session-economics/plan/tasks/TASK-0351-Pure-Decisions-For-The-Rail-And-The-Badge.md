---
type: "[[task]]"
id: TASK-0351
aliases: ["TASK-0351"]
title: "The rail key, the panel's id list and the badge's label become pure functions, so the behaviour is guarded and not just the decision behind it"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: M
due: ""
depends: ["[[TASK-0349-The-Switch-Announcement-Expires]]"]
blocks: []
related: ["[[ISS-0110-The-Whole-Cold-Reads-Grey-Behaviour-Can-Be-Reverted-With-A-Green-Suite]]"]
tests: []
---

# Pure decisions for the rail and the badge

Fixes [[ISS-0110-The-Whole-Cold-Reads-Grey-Behaviour-Can-Be-Reverted-With-A-Green-Suite]].

## Definition of Done
- [x] `railKey(state, now)` returns the state class the square should carry; `attentionIds(states, now)` returns the ids the panel should show; `cacheBadge(cache)` returns the label, tooltip and tone the strip should render. All pure, all in the plain-script module the node suite can evaluate.
- [x] The three call sites become one-line adapters, so reverting the behaviour means deleting a tested function rather than an untested branch.
- [x] Node-suite cases cover each, including the boundary crossing for `railKey` and `attentionIds`, and every branch of `cacheBadge`.
- [x] Verified by mutation: removing the cold demotion, removing the panel filter, or neutering the badge's cold branch each turns the suite red. Recorded in the task.
- [x] The standing decision against a JS test framework is **not** overturned — no jsdom, no new dependency.

## Notes
`cacheTemperature` guarded the decision; the fix was three call sites and a renderer, and all four could be deleted with a green suite. Pushing the decision out of the DOM is the route this repo already used for `healthMarks`, and it is why that guard survived a review that specifically went looking.
