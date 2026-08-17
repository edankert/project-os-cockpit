---
type: "[[phase]]"
id: PHASE-035
aliases: ["PHASE-035"]
title: "Acceptance checks are notes — the record gets granular, the sweep gets a surface, and a release can be finished"
status: active
order: 35
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
goal: "Move the acceptance record from one grammar-bearing document to first-class notes, and make the release process run on them end to end: invalidation happens where work lands, walking happens on a generated view with the same marks, and a release can be taken from naming its version to released inside the cockpit — with the sweep-was-considered question enforced at the one moment it is cheap and final."
features:
  - "[[FEAT-0113-The-Check-Type-And-The-Migration]]"
  - "[[FEAT-0114-The-Suite-Is-A-View]]"
  - "[[FEAT-0115-The-Sweep-Is-Continuous]]"
  - "[[FEAT-0116-A-Release-Can-Be-Finished]]"
  - "[[FEAT-0117-One-View-Per-Item]]"
issues: []
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[FEAT-0112-The-Acceptance-Suite-Gets-A-Machine-Readable-Projection]]", "[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
---

# Acceptance checks are notes

## Where this phase came from

A three-round independent functionality review of the releases surface (2026-08-17, clean context, every number measured against the live fleet), steered by Edwin at each turn. The decisions that shaped it, in his words:

1. *"not all features might need acceptance tests and the current set of features have caused existing acceptance-tests to become un-checked"* — the feature↔check coupling runs through **invalidation** of existing checks, not naming of new ones. Measured: the suite is organised by product area; 27 features are named by section headings covering 403 of 579 rows, and the 57 hand-written `RE-RUN (…)` annotations name the invalidating change (39 TASK, 17 ISS, 8 FEAT ids).
2. *"the acceptance tests should constantly be kept up to date and the human should be able to tick them off as features appear/change"* — the sweep belongs at **feature close-out**, not at release time. This is already TESTING.md's rule 3; the corpus shows it done by hand (`a4577c01`: six checks added + three unchecked, one commit) and shows how it fails without tooling — **54 of the 57 RE-RUN-annotated rows are still ticked**, because unchecking destroys the record and there is nowhere to say why.
3. *"having this granularity should allow us to build a lot more functionality around these TST notes"* — one note per check, [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]. Type `check`, id `CHK-*`, `status:` for lifecycle and `mark:` for verdict, deliberately outside the test gates.
4. *"Document this as a new phase with its own features/tasks etc."* — this note.

## Why this passes the phase test

The goal is stateable without listing its parts — *the acceptance record becomes notes and the release process runs on them* — and the exit criteria below are measurements, not a restatement of the task list.

## Order, and the two hard gates

[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] is `proposed`; **nothing migrates, scaffolds or writes a `CHK-*` until Edwin accepts it.** After that, upstream lands first — the `check` type reaches `~/Dev/repos/project-os` and syncs down before any note exists, because nothing here carries permanent template divergence. Then: migrate this repo as pilot (34 rows), the generated view, the two-shape delta, the frontmatter verdict writes, the sweep, Mark released, and the fleet migration last — `your-trainer` (579 rows) only after the schema has survived a real sweep in the pilot. The per-item view comes after the sweep exists, because until then it has nothing honest to say about a feature with no checks. Measured price accepted up front: **~9.5 days**, against ~1 day for the projection alternative [[FEAT-0112-The-Acceptance-Suite-Gets-A-Machine-Readable-Projection]] recorded — the premium buys evidence attachments, index-resolvable coverage, burden tags, and the native shape.

## What this phase must not do

- **No per-check obligations, ever.** [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] named acceptance rows the most self-re-arming population in the corpus; granularity makes them addressable, not owed. The release gate stays one campaign row, and `your-trainer`'s badge total must not rise.
- **No maintained mirror.** The old file is deleted at migration, never kept as a tombstone someone will edit; frozen per-release snapshot suites are never rewritten.
- **Nothing writes unasked and nothing pushes.** Every write stays loopback-guarded and human-initiated; Mark released prints the `git tag`/`git push` commands rather than running them.
- **No lost rows.** Migration asserts row-count and mark parity per repo (34 / 56 / 579) rather than assuming it — ISS-0175's lesson.

## Exit criteria

- [ ] [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] is `accepted` before any migration lands, and the `check` type lands upstream and syncs down before any `CHK-*` note exists in any repo.
- [ ] All three suites migrate with row-count and mark parity asserted per repo (34, 56, 579) and zero verdict changes.
- [ ] The release-gate delta still computes at every real `your-trainer` tag after the cut, and matches the file-shape numbers at the boundary.
- [ ] TESTING.md rule 3 is one action: invalidate-with-named-change writes note + reason in one commit, and a feature close-out sweep reproduces `a4577c01`'s shape — N additions and M invalidations, one Save, one commit.
- [ ] A release travels from *Name the version* to `released` entirely in the cockpit, and Mark released refuses while any frozen feature lacks `acceptance_impact` — naming which.
- [ ] `your-trainer`'s obligation badge total does not increase at any point in this phase (measured before and after each leg — the ADR-0027 guarantee).
- [ ] Every feature in this phase links `TST-*` coverage before reaching `done` — the [[PHASE-034-Three-Phases-And-Publication-Is-The-Third]] lesson, applied in advance rather than found by review.
