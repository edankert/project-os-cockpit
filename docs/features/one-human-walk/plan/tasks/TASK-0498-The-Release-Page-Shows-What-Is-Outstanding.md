---
type: "[[task]]"
id: TASK-0498
aliases: ["TASK-0498"]
title: "The release page shows what is outstanding, and its rows address the check"
status: backlog
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"]
parent: "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
effort: M
depends: ["[[TASK-0496-The-Tier-Is-In-The-Address]]"]
blocks: []
related: []
tests: []
---

# The release page shows what is outstanding

Edwin: *"it should probably now just show a list of unchecked/open acceptance tests and link to this."*

**Half of that is already built and the note should say so**: the page renders 13 new + 27 chronic + 0 regressed, collapses 20 quiet, and caps each group at 40 — it does not re-render 579 rows. What is wrong is narrower and worse.

**The rows do not address the check.** They show `item.number` (`1.4.20`) and link to `/docs/tests/acceptance#16-monetization-licensing` — the suite README with a dead fragment — while `item.rel`, the check's own path, sits unused in the same payload. That is [[ISS-0142]]'s defect with a new subject: an id nothing routes to.

**And this reverses part of [[ISS-0190]]**, which put the acceptance section first *and* rendered its rows, on Edwin's own instruction the day before. Say so in the note rather than letting the next reader find two decisions pointing opposite ways.

Done when: a row opens its check, the outstanding set is what the page leads with, and the link carries the filter ([[TASK-0496-The-Tier-Is-In-The-Address]]).
