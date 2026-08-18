---
type: "[[feature]]"
id: FEAT-0123
aliases: ["FEAT-0123"]
title: "The walk surfaces say one thing — one verb, a tier you can address, a page that leads with the checks, and a release that shows what is outstanding"
status: doing
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
goal: "Once there is one human-walked population, make every surface show it as one: a single verb across the registry and the headings, tiers that are addressable so selecting one changes the page, a filter bar that leads with the mark, and a release page that lists what is outstanding rather than re-rendering the suite."
requirements: ["[[REQ-0042-The-Suite-Is-Addressable]]"]
tasks: ["[[TASK-0495-One-Verb-For-One-Act]]", "[[TASK-0496-The-Tier-Is-In-The-Address]]", "[[TASK-0497-The-Page-Leads-With-The-Checks]]", "[[TASK-0498-The-Release-Page-Shows-What-Is-Outstanding]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ISS-0201-Walk-And-Run-Vocabulary]]", "[[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]]", "[[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]]", "[[FEAT-0114-The-Suite-Is-A-View]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-18
review_verdict: changes-requested
---

# The walk surfaces say one thing

Four defects Edwin found from use, and they share a cause: [[FEAT-0114-The-Suite-Is-A-View]] built a view of the whole suite, and every entry point was then pointed at it wholesale.

**Addressability is the common fix.** The tier heads share one url; the filters are click-only on all five axes; the release page re-renders rows rather than linking to them. All three are the same missing thing — a **filter that lives in the address** — and solving it once solves them together, with back/forward working as a consequence rather than as extra work.

**The filter bar is measured, not felt**: 164 chips above the first check on `your-trainer` (areas 76, covers 80), and 65 over 34 checks here — 1.9 per check, the worse ratio. Both axes scale with the corpus, so the surface degrades exactly as the suite becomes more useful. `area` earns its place at 7.6 checks per area (one sitting's work); `covers` has no such defence.

## Where this stands

**Three of four done.** The tier is in the address, the filter bar leads with the checks, and a release-page row opens its check rather than a dead fragment — and the three shared one cause, exactly as this note predicted: *a filtered view had no URL*.

**[[TASK-0495-One-Verb-For-One-Act]] is open**, deliberately last. It is the only piece with no measurement behind it — *walk* versus *run* is a naming judgement where the other three each had a number — and it is smaller than when it was written, because `Needs a run` is no longer a different kind of test but the same population filtered by execution.
