---
type: "[[change]]"
id: CHG-20260817-Acceptance-Checks-Are-Notes
aliases: ["CHG-20260817-Acceptance-Checks-Are-Notes"]
title: "Acceptance checks became notes, the sweep became an action, and a release can be finished"
status: merged
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[FEAT-0113-The-Check-Type-And-The-Migration]]", "[[FEAT-0114-The-Suite-Is-A-View]]", "[[FEAT-0115-The-Sweep-Is-Continuous]]", "[[FEAT-0116-A-Release-Can-Be-Finished]]", "[[FEAT-0117-One-View-Per-Item]]"]
tags: [acceptance, schema, release]
---

# Acceptance checks became notes

## What changed for a person

**The acceptance suite is a list you walk, not a document you read.** `~checks` renders every check from its own note — tier, then area, then rows in order, with the same six-mark dialog. Filters over mark, tier, area, covering feature and automation, every one derived from a field. `docs/tests/ACCEPTANCE_TESTS.md` is **deleted** in this repo and in `your-sudoku`; `docs/tests/acceptance/README.md` keeps the document's own prose and says how to read history from before the cut.

**Needs re-run is a seventh action on the mark dialog.** It clears the mark *and* records which change invalidated the check, in one write, and is refused without a change id that resolves. That is the half of `TESTING.md` rule 3 the corpus annotates and does not perform — 54 rows across the fleet carry a hand-written `RE-RUN (…)` and all 54 are still ticked.

**A feature's close-out has a sweep.** `~sweep/<FEAT-ID>` shows the checks it originated, the checks in its areas, and the ones an earlier sweep already invalidated; you tick what the work overtook, type any new checks as repeating rows, and **one Save writes them all, writes `acceptance_impact:` on the feature, and makes one commit**. The benchmark is the corpus's own hand commit `a4577c01` — six added, three invalidated, one commit.

**A feature in flight that has not said whether its acceptance impact was considered is now asked.** One row on the features view, discharged permanently by either a date or `none — <reason>`.

**A release can be finished.** `Mark released` writes `status`, `date`, `tag` and **freezes the derived feature list**, behind two refusals that name their subjects: a blocked gate with no documented exceptions, and any feature being frozen with no `acceptance_impact:`. It prints `git tag` and `git push` and runs neither. `Start ▸` is now `Name the version` and scaffolds from `docs/__templates__/release.md`, so the note it writes finally has the Known-issues and Post-Release-Actions sections `FEAT-0110` has been reading for.

**Selecting a feature inside a release opens `~release/<id>/<ITEM-ID>`** — what this item is *in this release* — instead of the bare note.

## Paths and contracts

- **New:** `docs/tests/acceptance/CHK-####-*.md` (34 here, 56 in `your-sudoku`), `docs/tests/acceptance/README.md`, `docs/__templates__/check.md`, `tools/scripts/migrate-acceptance-checks.py`, `src/project_os_cockpit/sweep.py`.
- **Deleted:** `docs/tests/ACCEPTANCE_TESTS.md`. Git holds it at every ref before the migration commit; each note carries `migrated_from:` with its old `#section.ordinal` address and the pre-migration sha, because blame does not cross the cut.
- **New endpoints:** `GET /api/cockpit/sweep`, `GET /api/cockpit/release-item`, `POST /api/notes/acceptance-sweep`, `POST /api/notes/release-mark-released`. `POST /api/notes/mark-check` gained `id` (a `CHK-*`) and `verdict: "needs-re-run"`. All loopback-only, as every write path here already was.
- **New routes:** `~checks`, `~sweep/<FEAT-ID>`, `~release/<id>/<ITEM-ID>`.
- **Template-owned, upstream first:** `TAXONOMY.md` (the `mark`/`automation`/`burden` vocabularies), `STATUSES.md` (`[[check]]`), `QUALITY.md` (a check does not owe a review), `SCHEMAS.md` (`check.md`), and `validate-docs.py` (`ID_PREFIXES`, `ALLOWED_STATUS`, `COLLECTION_TYPE`, `METRIC_PREFIX_TYPE`, `TERMINAL`). Landed in `~/Dev/repos/project-os` and byte-identically downstream before any `CHK-*` existed.
- **New frontmatter:** `acceptance_impact:` on a feature — a date, `none — <reason>`, or absent.

## What this deliberately does not do

**No check is ever owed.** `check` is declared owed-nothing in the obligation registry, forced by the completeness test, and a guard walks a corpus of unwalked checks asserting that none reaches any badge, group or digest. `ADR-0027` called acceptance rows the most self-re-arming population in the corpus; granularity gave that population 669 addresses and must not give it 669 obligations.

**Nothing is pushed.** `Mark released` prints the tag commands. The sweep commits, with named paths and **never `--no-verify`** — the pre-commit hook is what raises `counters.CHK` for the checks the sweep just wrote.

## Two things that are not finished, and why

**`your-trainer` has not migrated.** Its dry run is green — 579 rows, 513 settled, 60 blocking, parity asserted — but its working tree carries 102 uncommitted files, and writing 579 notes into it would put somebody else's work in this commit.

**`mountAcceptanceMarks` and the `li[data-check]` plumbing are still here.** They cannot be deleted until the last file-shaped suite migrates, because `your-trainer` still stores its suite as a document and deleting the document's mark control would strand it.

## Verification

1,634 tests pass, 2 skipped; validator green in this repo and in `your-sudoku`. Fourteen mutations were run against the new guards; **four survived and all four were addressed** — an unclassifiable check silently becoming Tier 3 (a real defect, fixed: it now blocks), a pass that did not discharge the invalidation it answered, staleness that ignored a later pass, and a frozen feature list that was never exercised in its empty-list case, which is the exact state `your-trainer`'s REL-0013 is in.

**The independent review is unpaid** and is now owed on five `TST-*` notes and this change note. That debt stands at seven closes.
