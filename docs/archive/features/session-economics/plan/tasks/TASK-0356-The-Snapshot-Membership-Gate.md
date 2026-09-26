---
type: "[[task]]"
id: TASK-0356
aliases: ["TASK-0356"]
title: "The snapshot's copy of a feature's task list is checked against the note's"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: S
due: ""
depends: ["[[TASK-0353-The-Feature-Note-Catches-Up-And-Links-Are-Checked-Both-Ways]]"]
blocks: []
related: ["[[ISS-0117-The-Snapshot-Task-List-Was-Still-Not-Extended]]"]
tests: []
---

# The snapshot-membership gate

**Written after the code, which is the defect it documents.** `SNAPSHOT-MEMBERSHIP` is a blocking pre-commit gate affecting every feature in the repo and it landed with no task — while its sibling `PARENT-BACKLINK` got [[TASK-0353-The-Feature-Note-Catches-Up-And-Links-Are-Checked-Both-Ways]] one commit earlier. LIFECYCLE's "No Orphaned Code" rule applies to both. Round 4 of the independent review caught it; this note is the correction, and it is dated honestly rather than back-dated.

## Definition of Done
- [x] `items.features.*.tasks` must agree with the feature note's `tasks:`; the note wins, because ADR-0009 makes it the authored source of state.
- [x] Only `TASK-` ids are compared — a `tasks:` list mentioning another id type is a different defect and not this gate's business.
- [x] Drift in **either** direction errors: a task missing from the snapshot, and a task present there but not in the note.
- [x] Tests in `tests/test_parent_backlink.py` cover both directions plus the clean case, and assert this repo stays clean.
- [x] The three features found drifting are corrected against their notes rather than by whichever edit silences the gate fastest. FEAT-0005 and FEAT-0042 gained the tasks their notes already listed; FEAT-0023 gained [[TASK-0173]] in its note — its snapshot entry was briefly "fixed" by deletion instead, which removed a real relationship, and that was reversed.
- [x] Retiring [[TASK-0173]]'s line from `tools/GRANDFATHERED.yaml`, since the ledger only shrinks.

## Notes
The gate exists because being careful failed four times. `PARENT-BACKLINK` walks note frontmatter and is structurally blind to the snapshot's own copy of the list, which is where FEAT-0081 carried five tasks against thirteen through three review rounds — twice recorded as repaired without being repaired.

**Known gap, shared with `PARENT-BACKLINK`:** the gate's *severity* is untested. Demoting `emit_for(...)` to `report.warn` leaves every test green. That is a repo-wide pattern across these gates rather than something this task introduced, and it is filed rather than fixed here.
