---
type: "[[task]]"
id: TASK-0437
aliases: ["TASK-0437"]
title: "The suite band, and the stepper retires — the acceptance document says which release it gates and how many checks are outstanding, and `~walk` is removed"
status: backlog
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'show the acceptance tests document and maybe a counter on how many checks are outstanding … and at the top allows to select whether it is completed or not and a comment'"]
parent: "[[FEAT-0104-The-Suite-Is-The-Surface]]"
effort: M
depends: ["[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]", "[[TASK-0434-The-Check-Map-And-The-Exception-Mark]]"]
blocks: []
related: ["[[ISS-0139]]", "[[FEAT-0103-The-Gate-Is-Walkable]]"]
tests: ["[[TST-0031-The-Exception-Mark-And-Its-Justification]]"]
---

# The suite band, and the stepper retires

## What

A band at the top of the rendered `ACCEPTANCE_TESTS.md`: which release these checks gate, how many are outstanding, how many are excepted, and the gate's own rule in the contract's words. The same shape as the release-gate band that already mounts on a release note, pointed at the document where the work is actually done.

And **`~walk` is removed**. It works, it is tested, and it is the wrong answer to the question — Edwin: *"why do we need the walk button there."* Keeping it beside the document would be two ways in, which is [[ISS-0139]]: `fillChanges` and `/api/cockpit/changes` surviving with no caller.

## Definition of done

- [ ] The band mounts on the acceptance suite and on no other document
- [ ] It names the release in preparation, or says none is
- [ ] It states outstanding and excepted counts, from the same computation the gate uses
- [ ] The gate row in Publication opens the document — the counter is the row's subtitle
- [ ] `~walk`, `renderAcceptanceWalkPage`, `buildAcceptanceWalker` and `POST /api/notes/walk-check`'s pass/fail path are removed together with their tests, not left unreferenced
- [ ] `TST-0029`/`TST-0030` are superseded rather than deleted — they recorded a real walk, and the record of what the stepper proved stays
- [ ] Nothing else regresses: full suite green


## Blocked 2026-08-16

Waiting on [[ISS-0175]]. The interaction is keyed on which rendered checkbox is which check, and that correspondence does not hold: `your-trainer` parses 579 checks and renders 542 inputs. A control wired to DOM position would write to the wrong check, which is worse than no control.
