---
type: "[[phase]]"
id: PHASE-038
aliases: ["PHASE-038"]
title: "A verdict is an event — the ledger holds what was actually verified, on which platform, for which release"
status: active
order: 38
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
goal: "An acceptance verdict stops being a scalar field on a check note and becomes a dated, attributed, single-platform event in a per-release ledger — so a repo can say what was verified, by what method, on which platform, for which release, and every downstream question becomes a query instead of a maintained document."
features:
  - "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
  - "[[FEAT-0134-The-Note-Sheds-The-Verdict]]"
  - "[[FEAT-0135-Everything-Downstream-Is-A-Query]]"
  - "[[FEAT-0136-The-Cockpit-Reads-And-Writes-The-Ledger]]"
  - "[[FEAT-0137-One-Outcome-Vocabulary-Written-Down-Once]]"
  - "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
requirements:
  - "[[REQ-0052-A-Verdict-Names-Its-Platform-Method-Author-And-Date]]"
  - "[[REQ-0053-The-Note-Holds-Nothing-Verdict-Shaped]]"
  - "[[REQ-0054-Absence-Is-The-Initial-State]]"
  - "[[REQ-0055-No-Surface-Writes-A-Verdict-Onto-A-Note]]"
  - "[[REQ-0056-One-Outcome-Vocabulary-And-The-Document-Matches-The-Data]]"
  - "[[REQ-0057-Coverage-Is-Observed-From-A-Run]]"
issues:
  - "[[ISS-0216-The-Suite-Parser-Splits-On-Physical-Lines]]"
  - "[[ISS-0217-The-Two-Repos-Holding-Every-Check-Describe-A-Retired-Type]]"
  - "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]"
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]", "[[PHASE-036-One-Human-Walk]]", "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]", "[[DES-0012-Tests-In-Two-Flows]]", "[[ISS-0215-One-Hundred-And-Forty-Rows-Outside-The-Suite]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
tags: [phase]
---

# A verdict is an event

## Goal

**An acceptance verdict is a fact about (check × platform × release).** It is stored as a scalar. This phase moves it into a per-release, single-platform ledger of dated events, leaves the note holding only intent, and turns the walk list, the release gate and the cross-platform burndown into queries over ledgers.

[[ADR-0037-A-Verdict-Is-An-Event]] carries the decision and the measurements. **Accepted 2026-08-19 by Edwin** — the gate [[ADR-0030]], [[ADR-0031]] and [[ADR-0034]] all used held for its day, and the phase was documented in full, amended twice and audited once while it read `proposed`. Two questions left open in the ADR were answered in the same instruction: `evidence` moves to the ledger as a sibling collection ([[TASK-0544]]), and `tests_verified:` becomes derived ([[TASK-0546]]). **This phase is now clear to start.**

## Why this is a phase

[[CLAUDE]]'s rule: a goal statable without listing its parts, and exit criteria that are not *"the tasks are done"*. Both hold. The goal is one sentence about where a verdict lives; the exit criteria are about what a query returns and what a gate reports, neither of which is a task list.

**And it is not a small request.** Six features, a new file format, a migration of 671 notes across three repos, and a read/write path spanning 87 TypeScript sites and six Python modules. This is the shape a phase exists for.

## Scope

- The ledger file: JSON schema, the working ledger, sealing at release cut, and immutability afterwards.
- The check note sheds `mark`, `verdict_date`, `verdict_reason`, `invalidated_by`, `automation`, `covered_by`, `evidence`.
- The four queries — walk list, release gate, cross-platform burndown, *was release R walked*.
- The cockpit's read path, write path and API surface.
- One outcome vocabulary, defined in one document that matches the data.
- The migration script for repos carrying scalar marks, and the splitter fix ([[ISS-0216]]) **before** any repo migrates again.
- Stage 2: the `@Covers` inversion and the CI emitter.

## Out of scope

- **Retiring `PARITY_MATRIX`.** [[ADR-0037]]'s limit section: the matrix's first failure mode is a surface with no row, which is [[FEAT-0130]]'s `SUR-*` work, not the ledger's. The retirement is `your-trainer`'s decision after [[FEAT-0130]] lands.
- **The tier rule.** [[ISS-0208]] owns it and is orthogonal — where a verdict is stored says nothing about which checks gate. The six unwalked Tier 3 checks still need Edwin's reading.
- **Getting the gate into the fleet repos.** [[ISS-0209]] is a validator migration per repo and is a precondition for the *benefit* landing anywhere but here — stated in *Sequencing* below rather than absorbed.
- **Migrating the 156 stranded checklist rows.** [[ISS-0215]]. They need a surface and a `covers:` per row first.
- **Behaviours with no check at all.** [[FEAT-0130]] and [[FEAT-0132]]. The ledger makes coverage legible, not complete.

## Exit criteria

- [ ] **A verdict cannot be written without a platform, a method, an author and a date.** Enforced by the validator, not by convention.
- [ ] **No acceptance note in any migrated repo carries `mark:`, `verdict_date:`, `verdict_reason:`, `invalidated_by:`, `automation:` or `covered_by:`** — and no cockpit surface reads or writes one.
- [ ] **The release gate is a query over ledgers**, and its delta against today's gate is measured and stated **per repo before that repo migrates**. A repo whose delta has not been stated does not migrate.
- [ ] **A check with no entry for a platform reports as owed on that platform**, with no field anywhere declaring applicability.
- [ ] **A sealed ledger cannot be modified**, proved by a test that tries — `entries` and `evidence` both.
- [ ] **A release's verified list is computed, not typed.** `tests_verified:` is gone from the schema and the page reads the sealed ledger, naming the platform it read.
- [ ] **A check can be excused from one release without being excused from the next.** *Unable to test*, *not tested this cycle* and *could not run it right now* are three recordable answers with three different effects on the gate, and the middle one **expires when its ledger seals** — the property [[ADR-0029]] designed and lost.
- [ ] **One outcome vocabulary exists in one document, and it is the vocabulary the data uses** — verified by a check that reads both, so `TAXONOMY.md` cannot drift from the corpus again ([[ISS-0218]] is what that drift looks like today).
- [ ] **The splitter is fixed and proved on a hard-wrapped bullet** before any repo runs a migration.

## Sequencing

Three stages, from [[ADR-0037]]. Each is independently useful.

**Stage 1 — the honesty gain.** [[FEAT-0133]], [[FEAT-0134]], [[FEAT-0135]], [[FEAT-0136]], [[FEAT-0137]]. Ledger format, one release backfilled, manual entries only; the notes shed the fields; the read and write paths move. This is where the *(check × platform × release)* fact starts being stored at its own arity.

**Stage 2 — observed coverage.** [[FEAT-0138]]. The `@Covers` inversion and the CI emitter. Seed the mapping from `covered_by:` **before** deleting the field — measured, it holds nothing, so the real seed is `your-trainer`'s 203 prose annotations naming 54 JVM classes.

**Stage 3 — rendered views replace hand-maintained tables.** Not scoped here; conditional on [[FEAT-0130]] and belonging to `your-trainer`.

**One ordering constraint that is not a stage.** [[ADR-0030]] decision 6 holds: `SCHEMAS.md`, `TAXONOMY.md`, `TESTING.md`, `STATUSES.md`, the test template and `validate-docs.py` land in `~/Dev/repos/project-os` and sync down **before** any note changes downstream. And [[ISS-0209]] means the gate currently runs in no repo that holds a check — so until it is resolved, everything this phase builds is enforced here and nowhere the data lives. That is not a reason to wait; it is a reason not to claim the fleet is gated when it is not.

## Notes

- **This is the fourth schema change to the same corpus in four weeks.** [[ADR-0037]] says so in its own status section and so does this. The argument for going again is that the previous three all moved the same scalar between shapes without asking whether a scalar could hold the fact.
- **The measurements are fresh**, taken 2026-08-19 against all three repos, and they corrected the source proposal in four places: the stranded-row count (156 across four notes, not ~156 across four — the fourth is `TST-0014`, and [[ISS-0215]] undercounts at 140/three), the doc-drift location ([[ISS-0217]] — the drift is in the fleet repos, not here), the vocabulary count (four live vocabularies, not three), and the cost (87 TypeScript sites the proposal does not mention).
