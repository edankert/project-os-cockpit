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

[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] was `proposed` when this phase was written; **nothing was to migrate, scaffold or write a `CHK-*` until Edwin accepted it.** *(Accepted 2026-08-17 on his instruction to build. The gate held for exactly as long as it was meant to — the phase was documented in full while the ADR said `proposed`, and nothing migrated.)* After that, upstream lands first — the `check` type reaches `~/Dev/repos/project-os` and syncs down before any note exists, because nothing here carries permanent template divergence. Then: migrate this repo as pilot (34 rows), the generated view, the two-shape delta, the frontmatter verdict writes, the sweep, Mark released, and the fleet migration last — `your-trainer` (579 rows) only after the schema has survived a real sweep in the pilot. The per-item view comes after the sweep exists, because until then it has nothing honest to say about a feature with no checks. Measured price accepted up front: **~9.5 days**, against ~1 day for the projection alternative [[FEAT-0112-The-Acceptance-Suite-Gets-A-Machine-Readable-Projection]] recorded — the premium buys evidence attachments, index-resolvable coverage, burden tags, and the native shape.

## What this phase must not do

- **No per-check obligations, ever.** [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] named acceptance rows the most self-re-arming population in the corpus; granularity makes them addressable, not owed. The release gate stays one campaign row, and `your-trainer`'s badge total must not rise.
  - *Amended 2026-08-17, after building it: **the last clause was wrong and is retired.*** It was drafted as though [[TASK-0468-The-Considered-Obligation]] were free, and it is not — a feature in flight with no `acceptance_impact:` is asked one question, which is the obligation this phase exists to create. Measured: `your-trainer` 32 → 36, `your-sudoku` 7 → 12, this repo 29 → 31, **every added row a feature and none a check**. The rule that was actually at stake is the first sentence, and it holds exactly: 0 of 669 checks reach any badge. A must-not that forbids the phase's own deliverable is a drafting error, not a finding, and pretending it was met would have been the more expensive mistake.
- **No maintained mirror.** The old file is deleted at migration, never kept as a tombstone someone will edit; frozen per-release snapshot suites are never rewritten.
- **Nothing writes unasked and nothing pushes.** Every write stays loopback-guarded and human-initiated; Mark released prints the `git tag`/`git push` commands rather than running them.
- **No lost rows.** Migration asserts row-count and mark parity per repo (34 / 56 / 579) rather than assuming it — ISS-0175's lesson.

## Exit criteria

*Measured 2026-08-17 at the end of the build session. Three are met, three are partly met and say where they stop, and one is **not** met and is recorded as a contradiction inside this note rather than smoothed over.*

- [x] [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] is `accepted` before any migration lands, and the `check` type lands upstream and syncs down before any `CHK-*` note exists in any repo. — Accepted 2026-08-17 on Edwin's instruction to build; the five template-owned surfaces changed in `~/Dev/repos/project-os` and, byte-identically, downstream, **before** the first `CHK-*` was written. Measured: four of the five (TAXONOMY, QUALITY, SCHEMAS, validate-docs.py) were **already diverged from upstream at HEAD before this phase**, so "zero divergence afterwards" was never reachable; what is true is that this phase created **no new** divergence — the check-type spans are identical in both copies, and `STATUSES.md`, the one file that was in sync, still is.
- [/] All three suites migrate with row-count and mark parity asserted per repo (34, 56, 579) and zero verdict changes. — **Two of three.** This repo: 34 rows, 34 settled, 0 blocking, marks `x` 33 / `/` 1, parity green. `your-sudoku`: 56 rows, 0 settled, 56 blocking, parity green, committed there as `87a1ff7`. **`your-trainer` is not migrated**, and the reason is not the schema: its working tree carries **102 uncommitted files** of parallel work, and writing 579 notes into it — with a pre-commit hook that re-stages `SNAPSHOT.yaml` — would put somebody else's afternoon in this commit, which is the measured failure `close-out-commit.sh` exists to prevent. Its dry run is green (579 rows, 513 settled, 60 blocking, parity asserted), so the leg is *ready* rather than *unknown*. See [[TASK-0463-The-Fleet-Migrates-Trainer-Last]].
- [/] The release-gate delta still computes at every real `your-trainer` tag after the cut, and matches the file-shape numbers at the boundary. — The two-shape read is built and asserted end to end on a purpose-built repo: a tag before the cut yields file shape, one after yields note shape, both with the same item and blocking counts, and the delta between them is empty. **The claim about `your-trainer`'s twelve real tags is untested**, because that repo has not migrated — there are no note-shape tags in it to read. The cost claim is asserted structurally (three subprocesses per ref regardless of suite size) rather than timed, which is the honest form while the 579-row corpus is still file-shaped.
- [x] TESTING.md rule 3 is one action: invalidate-with-named-change writes note + reason in one commit, and a feature close-out sweep reproduces `a4577c01`'s shape — N additions and M invalidations, one Save, one commit. — Built and driven. **Needs re-run** is the seventh action on the mark dialog, refused without a change id and refused when the id resolves to nothing. The sweep was run against a throwaway clone of this repo's own corpus: two checks authored, one invalidated, one commit touching exactly four files — the feature, the invalidated check and the two new ones.
- [x] A release travels from *Name the version* to `released` entirely in the cockpit, and Mark released refuses while any frozen feature lacks `acceptance_impact` — naming which. — Driven end to end on a clone: `Name the version` scaffolds from `docs/__templates__/release.md` (Known-issues and Post-Release-Actions sections present, filename `REL-####-v<version>.md`), the refusal fires naming `FEAT-0113`, and after the field is authored the note carries `status: released`, `date:`, `tag: v1.1.0` and a frozen `features:`. It prints the `git tag`/`git push` commands and runs neither.
- [ ] **`your-trainer`'s obligation badge total does not increase at any point in this phase.** — **Not met, and the phase note contradicts itself here.** Measured: `your-trainer` 32 → 36, `your-sudoku` 7 → 12, this repo 29 → 31. **Every one of those rows is a FEATURE, and zero are checks.** The rise is [[TASK-0468-The-Considered-Obligation]] working exactly as this phase designed it — a feature in flight with no `acceptance_impact:` is asked whether its acceptance impact was considered, which is the obligation [[FEAT-0115-The-Sweep-Is-Continuous]] exists to create and which Edwin asked for in as many words. The guarantee that was actually at risk holds exactly: **0 of 669 checks reach any badge, any Needs-you group or any digest**, asserted on a corpus where every check is unwalked. The clause as written was about per-check flooding and was drafted as though the sweep obligation were free; it is not, and four features being asked one question is the price of the rule Edwin asked for.
- [/] Every feature in this phase links `TST-*` coverage before reaching `done`. — Five test notes exist ([[TST-0039]]..[[TST-0043]]) and every feature links at least one. **No feature reached `done`**: FEAT-0113 and FEAT-0114 are `doing` (both wait on `your-trainer`), and FEAT-0115/0116/0117 are at `review` rather than `done` because QUALITY.md's independent-review gate is unpaid and the author must not be the sole judge of his own work. That debt now stands at seven closes.

## What is left, precisely

1. **`your-trainer`'s migration** — ready, dry-run green, waiting on a clean working tree in that repo.
2. **`mountAcceptanceMarks` and the `li[data-check]` plumbing** — [[FEAT-0114-The-Suite-Is-A-View]] asks for them deleted, and they cannot be until the last file-shaped suite migrates: `your-trainer` still stores its suite as a document, and deleting the document's mark control would strand it. Retire them in the same commit as leg 1.
3. **The independent review** — owed on five `TST-*` notes and one `CHG-*`, and on any feature moving from `review` to `done`.
