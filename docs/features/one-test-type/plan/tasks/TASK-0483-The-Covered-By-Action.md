---
type: "[[task]]"
id: TASK-0483
aliases: ["TASK-0483"]
title: "The *Covered by* action — one write, refused unless the id resolves to a runnable test"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0120-The-Automation-Path]]"]
parent: "[[FEAT-0120-The-Automation-Path]]"
effort: M
depends: ["[[TASK-0482-Covered-By-Reaches-The-Gate]]"]
blocks: []
related: []
tests: []
---

# The *Covered by* action

An action on the acceptance page that sets `automation:` and `covered_by:` in one write, alongside the six marks and *Needs re-run*. **Refused unless the id resolves to a test carrying a `command:`** — the same refusal shape *Needs re-run* already uses for a change id that does not resolve, and for the same reason: a link to something unrunnable records a claim nobody can check.

`automation:` follows from the shape of the claim rather than being asked for separately: naming one covering test that fully covers it is `full`; naming one that covers part is `partial` and requires the reason field, exactly as a `/` mark does.

Done when: the link is writable from the surface, unresolvable and non-runnable ids are refused with the replacement named, and the `automation` filter on `~checks` has more than one value for the first time.
