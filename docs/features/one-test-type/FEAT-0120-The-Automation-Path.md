---
type: "[[feature]]"
id: FEAT-0120
aliases: ["FEAT-0120"]
title: "The automation path — a passing covering test settles the check, `covered_by:` becomes writable, and `retired` becomes reachable"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
goal: "Make automating an acceptance check pay: a check whose `covered_by:` names a passing test is settled without a human mark, the link is writable from the surface and refused unless it resolves to a runnable test, `status: retired` finally has a writer, and the 203 checks that already name their covering test in prose have it moved into the field."
requirements: ["[[REQ-0039-A-Covering-Test-Settles-The-Check]]"]
tasks: ["[[TASK-0482-Covered-By-Reaches-The-Gate]]", "[[TASK-0483-The-Covered-By-Action]]", "[[TASK-0484-A-Writer-For-Retired]]", "[[TASK-0485-Backfill-Automation-From-The-Prose]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]", "[[REQ-0039-A-Covering-Test-Settles-The-Check]]"]
---

# The automation path

**This is why the merge is happening.** [[FEAT-0118-The-Test-Type-Absorbs-The-Check]] and [[FEAT-0119-The-Merge-Migration]] are cost; this is the return. If the phase ships without this feature it will have moved 669 notes and changed nothing a person experiences.

Three mechanisms, each small:

1. **`Item.settled` reads coverage** — settled if the mark is settled *or* the `covered_by:` test is `passing`. One clause.
2. **The link is writable and refused when meaningless** — *Covered by `<TST>`* on the acceptance page, rejected unless the id resolves to a test carrying a `command:`. `Needs re-run` already has this exact shape: refused without a change id that resolves.
3. **`retired` gets a writer**, which makes TESTING.md's Tier 2 → Tier 3 → remove path performable instead of described.

**And the backfill is where it becomes visible.** 203 of `your-trainer`'s bodies already name their covering test in prose — *"(partially automated: `LicensingManagerTest` covers PRO tier resolution…)"*. The data is in the corpus and in the wrong place. Moving it is a script, and afterwards the automation filter has more than one value for the first time.
