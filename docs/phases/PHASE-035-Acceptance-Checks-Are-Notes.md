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
- [x] All three suites migrate with row-count and mark parity asserted per repo (34, 56, 579) and zero verdict changes. — **All three, 2026-08-17.** This repo 34 rows (34 settled, 0 blocking); `your-sudoku` 56 (0 settled, 56 blocking), committed there as `87a1ff7`; `your-trainer` 579 (513 settled, 60 blocking, 53 stale), committed there as `1acc3850`. Every number identical across every cut, parity asserted through the reader after the write and before the source was deleted. **669 rows, three suites, zero lost.** `your-trainer` was held back a day for a dirty working tree and then migrated on Edwin's instruction — which produced the better artefact: the script now detects rows absent from `HEAD` and stamps them `(uncommitted at migration)` rather than pointing `migrated_from:` at a sha that does not contain them. Nineteen rows there needed it.
- [x] The release-gate delta still computes at every real `your-trainer` tag after the cut, and matches the file-shape numbers at the boundary. — **Measured 2026-08-17, after `your-trainer` migrated, and it found a defect.** All twelve tags read file-shape and give the recorded series (1, 10, 10, 15, 26, 85, 130, 22, 47, 47, 47, 47); `HEAD` reads note-shape and gives **579 items / 60 blocking, identical to the working tree**; and the delta across the boundary — `v2.1.6` (file, 560) → `HEAD` (notes, 579) — is **13 new / 47 chronic / 0 regressed**, the exact split the original review measured on the file shape before any of this existed. Cost: **0.13s cold for all twelve tags, ~0ms warm**; a note-shape ref is three subprocesses whatever the suite's size. *The defect this criterion caught is in the review section below; the first reading of `HEAD` returned 314 of 579.*
- [x] TESTING.md rule 3 is one action: invalidate-with-named-change writes note + reason in one commit, and a feature close-out sweep reproduces `a4577c01`'s shape — N additions and M invalidations, one Save, one commit. — Built and driven. **Needs re-run** is the seventh action on the mark dialog, refused without a change id and refused when the id resolves to nothing. The sweep was run against a throwaway clone of this repo's own corpus: two checks authored, one invalidated, one commit touching exactly four files — the feature, the invalidated check and the two new ones.
- [x] A release travels from *Name the version* to `released` entirely in the cockpit, and Mark released refuses while any frozen feature lacks `acceptance_impact` — naming which. — Driven end to end on a clone: `Name the version` scaffolds from `docs/__templates__/release.md` (Known-issues and Post-Release-Actions sections present, filename `REL-####-v<version>.md`), the refusal fires naming `FEAT-0113`, and after the field is authored the note carries `status: released`, `date:`, `tag: v1.1.0` and a frozen `features:`. It prints the `git tag`/`git push` commands and runs neither.
- [ ] **`your-trainer`'s obligation badge total does not increase at any point in this phase.** — **Not met, and the phase note contradicts itself here.** Measured: `your-trainer` 32 → 36, `your-sudoku` 7 → 12, this repo 29 → 31. **Every one of those rows is a FEATURE, and zero are checks.** The rise is [[TASK-0468-The-Considered-Obligation]] working exactly as this phase designed it — a feature in flight with no `acceptance_impact:` is asked whether its acceptance impact was considered, which is the obligation [[FEAT-0115-The-Sweep-Is-Continuous]] exists to create and which Edwin asked for in as many words. The guarantee that was actually at risk holds exactly: **0 of 669 checks reach any badge, any Needs-you group or any digest**, asserted on a corpus where every check is unwalked. The clause as written was about per-check flooding and was drafted as though the sweep obligation were free; it is not, and four features being asked one question is the price of the rule Edwin asked for.
- [/] Every feature in this phase links `TST-*` coverage before reaching `done`. — Five test notes exist ([[TST-0039]]..[[TST-0043]]) and every feature links at least one. **No feature reached `done`**: FEAT-0113 and FEAT-0114 are `doing` (both wait on `your-trainer`), and FEAT-0115/0116/0117 are at `review` rather than `done` because QUALITY.md's independent-review gate is unpaid and the author must not be the sole judge of his own work. That debt now stands at seven closes.

## What was witnessed on screen, and what was not

The built bundle was run against a **real sidecar on this repo's own corpus**, one origin through a local proxy — the venue [[REL-0001]]'s walk established, chosen because it is a current renderer against a current sidecar without restarting anybody's window.

**Seen:** the cockpit rendering the migrated corpus; PHASE-035 reading `active · 12/19 · 63% · 7 in flight · 4 attention`; and — the one that matters for [[TASK-0468-The-Considered-Obligation]] — the Features badge tooltip reading **"6 features to sweep, 2 requirements to approve"**, the new obligation with the noun and verb coming from the registry rather than from a string in the renderer. The `/api/cockpit/acceptance` payload served `shape: notes`, 34 checks, Tier 1 26/27 across 14 areas and Tier 2 7/7 across 7.

**Not seen:** the `~checks` page itself. The harness's navigator would not switch nav mode, so the route could not be reached from it, and chasing that further was the wrong use of the session. The page's structure is asserted against the renderer source by [[TST-0041]] and its payload end to end here, which is real coverage and is **not** the same as having looked at it. **A visual walk of `~checks`, `~sweep/<FEAT>` and `~release/<id>/<ITEM-ID>` is owed** — and it is exactly what the migrated suite is for.

## The review, 2026-08-17 — three defects, one of them mine and severe

Run after the fleet migrated, against real corpora rather than fixtures. Every number below is measured.

**1. `suite_at` read 314 of 579 checks at a ref, silently.** `git cat-file --batch` reports each object's `size` in **bytes**; the walk sliced a *decoded string* by characters. `../your-trainer`'s notes are 503,860 bytes decoding to 501,153 characters, so the walk drifted one position per non-ASCII byte — em-dashes, `✅`, arrows — reached a header it could not parse, and stopped. **The gate at every post-migration ref would have read 20 blocking where the truth is 60**: the direction that lets a release through. The docstring already said *"the size is authoritative — counted, not guessed"*; the code counted the wrong unit. Fixed, and guarded by a fixture whose multi-byte characters sit in the **first** note — drift only affects what follows, so a corpus with its non-ASCII last round-trips perfectly and proves nothing. The guard fails against the shipped code and **the other sixteen tests in that module do not**, which is the honest measure of what the suite was blind to.

**2. `[[ACCEPTANCE-TESTS]]` resolved to a template, in every repo, for as long as both existed.** `docs/__templates__/acceptance-tests.md` is the **only** type template carrying a real id instead of a placeholder — `adr.md` has `ADR-0000`, `test.md` has `TST-0000`, and this one had `ACCEPTANCE-TESTS`, the same id the record uses. Three notes here link it and landed on a placeholder. Pre-existing (both files carried the id at `7de1a86`, before this phase) and fixed upstream and in all three migrated repos: the template is `ACCEPTANCE-TESTS-TEMPLATE` and the link now resolves to `tests/acceptance/README.md`.

**3. A memo keyed on `id(index)`.** `note_less_row_for` cached the note-less owed rows under `(id(index), generation)`. CPython reuses an address once the object at it is collected, and a freshly built index is always at generation 0 — so a freed index and a new one in its place would share a key, and one corpus would be served another's owed rows. Mine, introduced with the sweep obligation. The memo now hangs off the index object, so it cannot outlive what it describes and identity reuse is unrepresentable rather than unlikely.

**What the review did not find.** Corpus integrity is clean across all 669 checks in three repos: no duplicate ids, no duplicate filenames, no note whose `tier:` needed the fail-safe, and **no `covers:` reference that does not resolve** — which is [[ISS-0173]] genuinely closed rather than moved. At scale on 579 checks: `view_payload` 10ms, `gate_payload` 8ms, `candidates` 5ms, and a real verdict write round-trips. Twelve of twelve fleet repos validate green.

**Downstream, stated precisely.** Four of twelve repos carry the `check` type — `project-os` and the three that have suites. The other eight are full project-os installs sitting **13–18 upstream commits behind, and they were behind before this phase**: their sync baselines are July, and upstream had 15 template-owned commits pending before either of mine. So the type's absence there is the standing sync debt, not a regression, and it is inert — those repos hold no checks and all eight validate green. They pick it up whenever somebody syncs them, which is a separate decision about a month of upstream change.

## What is left, precisely

*Both build legs are closed. What remains is a judgement, not a task.*

1. ~~**`your-trainer`'s migration**~~ — **done 2026-08-17** (`1acc3850`): 579 rows, badges 37 → 37, zero checks owed.
2. ~~**`mountAcceptanceMarks` and the `li[data-check]` plumbing**~~ — **deleted 2026-08-17.** 258 lines of source across five files, 22 guards whose subject went with them, three new ones in their place. `ACCEPTANCE_TESTS_v2.1.0.md` parses as 300 checks and renders **0 addresses, 0 marks** — the frozen record is inert. The delta at all twelve historical `your-trainer` tags is unchanged, which is the one thing the cull could have broken. The unreachable-function guard caught `suppressNextSoftReload` on the first run afterwards. [[ISS-0192-A-Frozen-Release-Suite-Still-Offers-Live-Marks]] is `fixed`.
3. **The independent review** — owed on five `TST-*` notes and one `CHG-*`, and on any feature moving from `review` to `done`.
