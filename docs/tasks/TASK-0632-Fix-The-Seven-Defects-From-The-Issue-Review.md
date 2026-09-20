---
type: "[[task]]"
id: TASK-0632
aliases: ["TASK-0632"]
title: "Fix the seven small defects the 2026-09-19 issue review left in the cockpit"
status: doing
phase: ""
owner: user:edwin
created: 2026-09-20
updated: 2026-09-20
source: ["[[ISS-0313-Seven-Small-Defects-From-The-Issue-Review-Are-Still-In-The-Cockpit]]", "project-os-dev PHASE-0007 step 3"]
parent: "ISS-0313"
effort: "M"
due: ""
depends: []
blocks: []
related: ["[[ISS-0184-Clicking-A-Checkbox-In-The-Acceptance-Suite-Writes-To-A-Different-Row]]", "[[ISS-0266-Five-Mutants-Survive-The-Guards-Written-For-Them]]", "[[ISS-0271-Five-Tasks-Joined-A-Feature-That-Was-Done-And-Reviewed]]", "[[ISS-0278-The-Recorded-Stale-Verdict-Count-Is-Out-Of-Date]]", "[[ISS-0279-A-List-Valued-Type-Field-Loses-Its-Type]]", "[[ISS-0292-The-Status-Vocabulary-Is-Not-Served-So-Every-Client-Keeps-A-Copy]]", "[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]"]
tests: []
---

# Fix the seven defects ISS-0313 lists

[[ISS-0313-Seven-Small-Defects-From-The-Issue-Review-Are-Still-In-The-Cockpit]] is the work order and holds the list. This task is the place the code changes hang off, because `tools/instructions/LIFECYCLE.md` wants a task behind every functional change and the seven issues share no feature.

**Where this note lives.** Every other task in this repo sits under `docs/features/<slug>/plan/tasks/`, because every other task belongs to a feature. These seven issues belong to none, and minting a feature to hold them would be the container-for-its-own-sake that `CLAUDE.md` warns about for phases. So it sits in `docs/tasks/`, which is where the sibling repo `your-trainer` keeps the same shape of work (its TASK-0936 against ISS-0484).

## Definition of Done
- [ ] Each of the seven issues is either `fixed` with a test that fails when the fix is reverted, or left `open` with the reason written in it.
- [ ] Both results — test passing with the fix, test failing without it — are recorded in each issue note.
- [ ] `ISS-0313`'s seven boxes are ticked or answered.
- [ ] The Python suite and `bash tools/scripts/validate-docs.sh` are green.
- [ ] A `CHG-*` note records the behaviour changes, and `docs/reference/cockpit-capability-register.md` carries a row for any new capability.

## Steps
- [ ] ISS-0279 — `_normalise_type` accepts a list.
- [ ] ISS-0184 — a checkbox toggle whose text does not match the line it would change is refused.
- [ ] ISS-0292 — one read route serves the status, severity and callout vocabularies.
- [ ] ISS-0266 — three guards get assertions that kill mutants B1, B2 and C2.
- [ ] ISS-0301 — a write body whose `Content-Type` is not `application/json` is refused. Left `open` for Edwin to see.
- [ ] ISS-0271 — docs only: the change note for the five page fixes, and a narrowed `acceptance_exception`.
- [ ] ISS-0278 — docs only: the stale-verdict figures in `CLAUDE.md`.

## Notes
ISS-0301 is a security change and stays `open` after the fix lands, by ISS-0313's instruction, until Edwin has looked at it.
