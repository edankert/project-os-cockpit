---
type: "[[adr]]"
id: ADR-0037
aliases: ["ADR-0037"]
title: "A verdict is an event in a per-release, single-platform ledger — the note holds intent, the ledger holds reality, and platform stops being a note field"
status: proposed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
decision_date: ""
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
source: ["Edwin 2026-08-19, via a working session in ~/Dev/repos/your-trainer: 'Acceptance verification becomes a per-release ledger, and platform stops being a note field'"]
supersedes: ""
superseded: ""
related: ["[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0036-The-Sweep-Is-Withdrawn]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[ISS-0215-One-Hundred-And-Forty-Rows-Outside-The-Suite]]", "[[ISS-0216-The-Suite-Parser-Splits-On-Physical-Lines]]", "[[ISS-0217-The-Two-Repos-Holding-Every-Check-Describe-A-Retired-Type]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [acceptance, conventions, schema, testing]
---

# A verdict is an event

## Status

**Proposed 2026-08-19.** Nothing migrates while this reads `proposed` — the same gate [[ADR-0030]], [[ADR-0031]], [[ADR-0033]] and [[ADR-0034]] all used, and the same reason: an acceptance should be about something concrete and fully costed.

**Read this sentence before the rest. This is the fourth schema change to the same corpus in four weeks** — [[ADR-0030]] (~9.5 days), [[ADR-0031]] (6–8 days), [[ADR-0034]], and now this. Nobody should accept it without that on the record. What is different this time, and it is the whole argument for going again, is stated under *Why a fourth time* below: the previous three all moved the same scalar between shapes. This one is the first to notice that the scalar cannot hold the fact.

## Context

The design arrived as a written proposal from a working session in `~/Dev/repos/your-trainer`, the repo with the real data. Everything below was **re-measured in this repo on 2026-08-19** before being written down; where the measurement corrected the proposal, the correction is stated rather than quietly applied.

### The problem, in one line

**An acceptance verdict is a fact about (check × platform × release).** It is stored as a scalar `mark:` in the check note's frontmatter. A scalar cannot hold a three-tuple, and everything downstream is deformed by that.

### What is measured, fleet-wide, 2026-08-19

**671 acceptance notes** carry a `mark:` — `your-trainer` 581, `your-sudoku` 56, this repo 34.

| field | non-empty | of |
| --- | --- | --- |
| `mark:` | 671 — `done` 546, `todo` 124, `incomplete` 1 | 671 |
| `platform:` | **2** | 671 |
| `verdict_date:` | **0** | 671 |
| `verdict_reason:` | **0** | 671 |
| `invalidated_by:` | **0** | 671 |
| `covered_by:` | **0** | 671 |
| `automation:` | 203 (`your-trainer` only: 22 `full`, 181 `partial`) | 671 |

Four of the six fields this decision removes are empty in **100%** of the corpus. That is not an argument that they are harmless — it is the measurement that makes the removal nearly free, and it is also the strongest available evidence that a per-note verdict record does not get kept. `verdict_reason:` is empty on all 671 while [[ADR-0029]] made it *required* for four of six marks; the requirement holds only because nobody has ever written one of those four marks.

**546 `done` verdicts carry no date.** They cannot say when they were earned, and — the point of this decision — they cannot say **on what**. `your-trainer`'s suite was migrated verbatim from an Android `ACCEPTANCE_TESTS.md`; all 513 of its `done` verdicts were earned on Android, on a repo that ships two platforms with independent tag namespaces (`v2.1.6` against `ios/v0.1.0`, its ADR-0004). **579 notes are quietly claiming more than they know**, and the schema has no way for them to say otherwise.

**The two exceptions prove it is an artefact.** Exactly two acceptance notes carry a `platform:` — `TST-0015` (`cross`) and `TST-0018` (`android`) — and both are the notes [[TASK-0507]] relevelled *yesterday* from ordinary tests. They kept a field they already had. Nothing in the migration ever considered platform; the absence is not a position anybody took.

### The same shape fails one level up

`your-trainer/docs/features/ios-parity/PARITY_MATRIX.md` (57 KB, hand-maintained) is a per-behaviour × per-platform matrix for surfaces. It documents three of its own failure modes in its own prose, and a single device session produced eight rider-visible bugs (`ISS-0359`..`ISS-0366`) on rows it called DONE:

1. **A surface with no row cannot be MISSING** — coverage gaps are structurally invisible.
2. **Presence-only verdicts** — *"a view exists"* accepted as *"the behaviour holds"*.
3. **Back-ports** — a fix to an already-DONE surface never crossing was invisible, and was patched with *another* hand-maintained table inside the matrix.

**A maintained matrix rots; a computed query cannot.** That is the sentence driving this decision, and failure mode 1 is the one it does **not** fix — see *The limit* below.

### Why a fourth time

[[ADR-0030]] made a check a note. [[ADR-0031]] merged it into `[[test]]`. [[ADR-0034]] separated level from execution from gating, and rewrote the mark values as words. **All three moved the same scalar between shapes.** None asked whether a scalar was the right container, because none of them had a second platform in frame. [[ISS-0206]] is where that question first surfaced, filed and left open on 2026-08-18 with a done-when that reads *"`platform:` is either part of that answer or explicitly ruled out"*. This is that answer.

## Options

1. **Leave it.** A scalar `mark:`, plus `invalidated_by:` reconstructing history from one field, plus a `platform:` on the note if the two-platform case ever bites. Cheapest, and it is the option that produced 579 notes claiming an Android result as a platform-free fact.
2. **Add `platform:` to the check note, and a per-platform mark map.** A per-note × per-platform `applies:`/`marks:` field. This is `PARITY_MATRIX` hiding in frontmatter — hand-maintained, per-note, and rotting by the same mechanism.
3. **A per-release, single-platform ledger of dated events; the note keeps only intent.** The proposal. Most expensive, and the only one where the stored fact has the same arity as the real fact.

## Decision

**Option 3.**

### 1. The note is intent

The check note holds what the behaviour is, how it is grouped and how it gates. Nothing else.

```yaml
tier: 1
area: "Hardware Connectivity"
covers: ["[[FEAT-####-Slug]]"]
level: acceptance
```

**Removed:** `mark`, `verdict_date`, `verdict_reason`, `invalidated_by`, `automation`, `covered_by`, `evidence`. **The note holds nothing platform-shaped and nothing verdict-shaped at all.**

`covers:` stays — it is the gating axis [[ADR-0034]] decision 1 established and [[ADR-0032]] built, and it is a statement of intent, not of outcome.

### 2. The ledger is reality

Append-only, **one per release per platform**. Because releases are per-platform in any repo shipping independent cadences, **each ledger is single-platform by construction** — there is no cross-platform release object to hang a shared ledger on. The cross-platform view is a query across ledgers, not a document.

```json
{
  "release": "REL-0012",
  "version": "v2.1.6",
  "platform": "android",
  "sealed": "2026-08-20",
  "entries": [
    {"check": "TST-0028", "mark": "pass", "date": "2026-08-14",
     "method": "automated", "by": "ScannerModalTest"},
    {"check": "TST-0034", "mark": "pass", "date": "2026-08-15",
     "method": "manual", "by": "user:edwin"},
    {"check": "TST-0141", "mark": "na", "date": "2026-08-19",
     "method": "manual", "by": "user:edwin",
     "reason": "No OS-level auto-backup surface on iOS."},
    {"check": "TST-0402", "mark": "excused", "date": "2026-08-19",
     "method": "manual", "by": "user:edwin",
     "reason": "Route-map redraw is not in v2.1.6; owed again at the next seal."},
    {"check": "TST-0028", "invalidated_by": "TASK-0776", "date": "2026-08-16"}
  ]
}
```

`sealed` is absent while this is the working ledger. One entry per line, so a diff reads as *what was added*, which is what an append-only file is for.

### 3. Automation is an event, not a standing claim

A standing `automation: full, covered_by: [X]` rots **silently**: rename, delete or `@Ignore` the covering test and the note keeps asserting coverage while the check drops out of the walk list permanently, with no signal. That is worse than a stale verdict, because a stale verdict at least still asks.

Automation is not a property of the check. It is a claim about the codebase at a point in time, carrying the same three dimensions as a verdict. A CI-green run and a human walk are two answers to one question, so they unify into one event with a `method:` field.

**This repo already measured the failure.** [[ISS-0198]] found `covered_by: []` on 669 of 669 checks and closed with the field still empty *on purpose*: the 203 annotated bodies name **54 JVM test classes and not one `TST-*` id**, and `cover_check` correctly refuses a link to something no runner can execute. The standing-claim field could not be filled without inventing 54 unrunnable notes. Under an observed-coverage model that population is exactly the one that works — see decision 8.

### 4. Platform applicability is an event, not a note field

**A check with no entry for a platform is owed on that platform.** Add a new platform and every check is immediately owed there — no schema change, no key to add, no mass backfill. The absence *is* the initial state, and it is the honest one.

The escape hatch is a `mark: na` event carrying date, author and a **required** reason, invalidatable by a later event through the same machinery that re-arms a stale pass.

This is the explicit ruling-out [[ISS-0206]] asked for: **platform is not a field on a check.** A platform is also not a release — the ledger keys on both, separately, which is what stops *"the iOS ones"* from being a release question.

### 5. "Not yet walked" ceases to exist as a value

You do not record that you did not do something. `todo` — **124 of the 671 notes** — becomes *no entry*. This eliminates a mark value rather than adding one.

`rerun` goes the same way, and its going is the most awkward consequence here: [[ADR-0034]] minted it three weeks ago and called it *"the addition that earns the migration on its own"*. It earned that on the argument that `mark: " "` plus an `invalidated_by:` block recorded *"nobody has walked it"* against a check somebody had walked — two states indistinguishable in the one field every surface reads. **The ledger makes the argument moot rather than wrong**: an invalidation is an event with a date, sitting after the pass it invalidates, so the two states are distinguishable by construction and neither needs a value. Measured: `mark: rerun` is written **0 times in every repo**, so nothing is lost in the corpus — only in the record, which this paragraph is.

### 6. One outcome vocabulary, and "not run" is three answers, not one

Edwin, 2026-08-19: *"How do I mark a TST as unable to test (with reason) and not tested (with reason) — maybe these are the same, but these should then not gate a release?"*

**They are not the same, and the current schema cannot tell them apart.** Measured against the live code: `excused` → `mark: canceled` is the *only* non-gating route for a check nobody ran, and *"not tested, and here is why"* is structurally impossible — `_mark_check_note` blanks `verdict_date` and `verdict_reason` when a mark is cleared, on the stated rule that *"a row cannot claim both that nobody walked it and that somebody decided why"*. So there is one value where there are three questions.

| ADR-0034 word | ledger mark | gate | persists past the seal | means |
| --- | --- | --- | --- | --- |
| `done` | **`pass`** | clears | yes, until invalidated | walked, it held |
| `incomplete` | **`partial`** | clears | yes, until invalidated | some clauses hold; the reason says which |
| `canceled` | **`na`** | clears | **yes, until invalidated** | **cannot apply here** — no OS surface on this platform, the surface was retired |
| — | **`excused`** | clears | **no — expires with its release** | **not done this cycle, by decision** — out of scope, low risk, no time |
| — | **`blocked`** | **blocks** | no | **could not be run right now** — rig down, device unavailable, dependency broken |
| `important` | **`fail`** | blocks | no | walked, it failed |
| `question` | **`question`** | blocks | no | walked, and the *check* is not understood |
| `todo` | *(no entry)* | blocks | — | decision 5 |
| `rerun` | *(an invalidation event)* | — | — | decision 5 |

**Why `blocked` blocks and the other two clear.** `na` and `excused` are *decisions*: somebody weighed the check against this release and said it does not hold shipping. `blocked` is an *accident* — the evidence is missing for a reason that will be gone next week, and nobody decided the release is safe without it. A gate that clears on "the device was unplugged" is a gate that clears on whatever happens to be broken on the day.

**Why `na` and `excused` are two values and not one.** They differ in exactly one property and it is the one that matters: **whether the exception comes back.** `na` is a statement about the check and the platform — re-asking it every release is the maintained-matrix failure this whole decision exists to avoid, so it persists until something invalidates it. `excused` is a statement about the check, the platform **and this release** — and if it persists, a check excused once is excused forever.

**That is not hypothetical; it is what the code does today.** `Item.excepted` is `mark in {canceled, -}` read from frontmatter, and **nothing anywhere scopes it to a release** — not `acceptance.py`, not `cockpit.py`, not `note_writes.py`. Meanwhile the comment sitting directly above that set still describes the property the mark is supposed to have: *"`~` is permanent and says the check no longer applies; `!` is **per-release** and says the check still applies and was not done… conflating them would make an exception look settled forever when it expires with its release."* [[ADR-0029]] moved the release exception from `[!]` to `[-]`, and **the per-release half did not move with it.** The comment has described a design the code stopped implementing ever since, and nothing reported it because `mark: canceled` is written **0 times in all three repos** — latent, not live, and verified before deciding rather than after.

So this decision **amends [[ADR-0029]] decision 2**, which moved the release exception onto `[-]` and lost its expiry. The concept is restored as `excused`, and it expires by construction rather than by anybody remembering — see decision 7.

**`question` is kept, and it is one of two places this decision widens the proposal it came from.** The source proposal lists five values and drops `question` by omission rather than by argument. [[ADR-0029]] made the distinction deliberately — *"nobody looked, somebody looked and it broke, somebody looked and could not tell"* — three things, all blocking. Decision 5 retires the first. The remaining two are still two: `fail` says the behaviour is wrong, `question` says **the check is wrong**, and they route to different work. Collapsing them into `blocked` would lose the only signal the corpus has that a check needs rewriting.

**The cost of getting any of this wrong is zero, and that is why it is decided on the argument.** Measured 2026-08-19: `canceled`, `important`, `question` and `rerun` are each written **0 times in all three repos**. The live vocabulary is three values — `done` 546, `todo` 124, `incomplete` 1. This is the same standing [[ADR-0029]] had when it reversed the meaning of `[!]`.

`fail`, `partial`, `blocked`, `question`, `na` and `excused` are **refused without a reason**. `pass` is not. That is [[ADR-0029]]'s rule unchanged, moved onto the event where it can finally be enforced against something that exists — measured, `verdict_reason:` is non-empty on 0 of 671 notes, so on the note it never was.

### 7. An entry either persists past the seal or expires with it, and the entry says which

Sealing a ledger does not only assign events to a release (decision 9) — **it is also when exceptions expire.**

- **`pass`, `partial` and `na` persist** into the next cycle's view until an invalidation event supersedes them. That is the existing re-arming model and it is unchanged.
- **`excused` does not.** It was true of one release. When that ledger seals, the check is owed again on the next one, with no action by anybody.
- `fail`, `blocked` and `question` block, so persistence is moot for the gate; they persist as history.

**This is the property the note form cannot have at any price**, and it is worth stating as the sharpest single argument in this ADR. A field on a note has one value and no release attached; "expires with its release" is not expressible in it, which is precisely why [[ADR-0029]]'s per-release exception quietly became permanent the moment its mark moved. An event in a per-release ledger gets the property **by construction** — the ledger it is in *is* the release it applies to.

*Inserting this shifted the last three decisions by one — coverage is now 8, the ledger's location 9, and the ADR-0030 carry-forward 10. Renumbered rather than appended because the persistence rule belongs beside the vocabulary that needs it, and the ADR was `proposed` with no external citation of the old numbers.*

### 8. Coverage is observed, not declared

**The test declares the check** — `@Covers("TST-0028")`, or a comment-and-grep convention for v1 — and the CI run emits `method: automated` entries into the working ledger. `covered_by:` is deleted from the note.

A deleted test simply stops emitting, and the check **reappears in the walk list on its own**. That is the structural fix for the silent-rot failure in decision 3, and it is only available because automation moved into the ledger.

This is Stage 2. Before `covered_by:` is deleted, whatever it holds is seeded into the mapping — measured, that is nothing, so the real seed is `your-trainer`'s 203 prose annotations naming 54 classes.

### 9. Where the ledger lives, and it is JSON

`docs/releases/ledgers/REL-####-<platform>.json`, with the open one at `docs/releases/ledgers/WORKING-<platform>.json`.

- **JSON, not a note.** *Edwin's call, 2026-08-19.* An earlier draft of this decision said plain YAML on a hand-editability argument; the measurement below is better than that argument was.
- **With its subject.** [[ADR-0020]]: obligations live with their subject, and a ledger's subject is a release.
- **One open ledger per platform, always.** Every event lands in the working ledger for its platform; **sealing is what assigns it to a release** ([[ISS-0206]]'s "somewhere else" answered). At release cut the working ledger gains `release`, `version` and `sealed`, is renamed, and a fresh working ledger starts.
- **A sealed ledger is never edited.** The validator enforces it. *Was release R walked?* is answered by reading its ledger, and the answer does not change afterwards.

**Why JSON, measured rather than preferred: this project has never written YAML.** `yaml.dump` and `yaml.safe_dump` occur **zero times** in `src/` and `tools/scripts/`. PyYAML is a read-only dependency — every YAML file in the corpus is authored by a person or edited line-by-line (`note_writes._set_field`, `_set_block`), and `note_writes._yaml_safe` exists precisely because hand-rolling YAML quoting is fiddly enough to need a helper. Twelve modules already import `json`.

So a YAML ledger would introduce this project's **first YAML writer**, hand-rolled, on the one file a CI runner appends to on every green build. `json.dumps` is stdlib and total. The failure mode being avoided is not theoretical: YAML's implicit typing reads `no` as `False` and bare dates as `date` objects, and a ledger is a file of ids, dates and short words.

**What is given up, stated:** comments, and a shape a person edits comfortably by hand. Neither is load-bearing. Comments have nowhere to go that `reason` does not already cover, and the ledger is written by a walk, a runner or a migration — **the notes are what stay hand-editable**, and that is what [[project-os-dev#ADR-0009]] actually protects.

**Why this is not the JSON that [[ADR-0030]] rejected — and the reason has nothing to do with the format.** [[FEAT-0112]]'s JSON was a *projection*: a second copy of state the notes already held, which is what made the tool mandatory to edit a check and what inverted the notes-are-the-source rule. The ledger holds state that exists **nowhere else**. It is authored, not derived. The distinction [[ADR-0009]] draws is *derived versus authored*, not *JSON versus frontmatter* — which is why the format is free to be chosen on the merits above, and why the earlier draft's YAML-versus-JSON framing was answering a question nobody had asked.

### 10. [[ADR-0030]] decisions 4, 5 and 6 carry forward unchanged

The suite is a generated view, not a document. The frozen per-release suites never migrate. **Template-owned surfaces land upstream in `~/Dev/repos/project-os` and sync down before any note changes downstream** — which for this decision covers `SCHEMAS.md`, `TAXONOMY.md`, `TESTING.md`, `STATUSES.md`, the test template, and `validate-docs.py`.

## Everything downstream becomes a query

| question | query |
| --- | --- |
| Is this automated on platform P? | `method` of its latest entry for P. Cannot rot — it describes a run, not a claim |
| What must a person run for release R? | No terminal entry since the last invalidation, and not covered by this cycle's CI |
| Where does platform B stand against A? | A-`pass` with no terminal B entry. `na` drops out by construction; `excused` does not, because it expires |
| Release gate | Every check the release gates on has a clearing entry for the shipping platform — `pass`, `partial`, `na`, or an `excused` belonging to **this** release. No entry, `fail`, `blocked` or `question` blocks |
| What did we ship without verifying? | The `excused` entries in that release's ledger, each with its reason. A question nothing can answer today |
| Was release R walked? | Read its ledger. Immutable once sealed |

## Consequences

**The gate moves, and the delta is measured per repo before it lands.** Under decision 5, 124 `todo` notes become *no entry* — which is the same blocking state, not a quieter one. But 546 `pass` entries land in a **single-platform** ledger, so on `your-trainer` every one of the 513 Android passes stops counting toward an iOS release. That is the honesty gain and it is also a large, deliberate tightening of one repo's gate. *"Quieter is the one direction a gate must never move without somebody deciding it"* ([[ISS-0208]]) cuts both ways, and this moves it the other way, hard. **No repo migrates before its delta is stated.**

**An exception now expires, and today it does not.** `Item.excepted` is `mark in {canceled, -}` read from frontmatter, scoped to nothing — so a check excused once is excused on every release afterwards, while the comment above that set still describes the per-release property [[ADR-0029]] removed when it moved the exception from `[!]` to `[-]`. Latent rather than live: `mark: canceled` is written **0 times in all three repos**. If this ADR is declined the defect stays and should be filed; if it is accepted, decision 7 removes it by construction rather than by a fix.

**The backfilled dates are honest and imprecise, because there is nothing better.** All 546 `pass` verdicts have no `verdict_date:`. The backfill writes the migration date with `by: migration` and a `note:` recording that the verdict predates the ledger and naming the pre-migration address from `migrated_from:`. Recovering true dates from `git log -L` over the pre-migration document is possible and is **not** proposed: it is expensive, partial, and the resulting precision would be indistinguishable from precision anybody could trust.

**The real cost is the read path, the write path and a new file format moving together.** Measured 2026-08-19, and larger than the source proposal's "~9 cockpit modules":

| surface | `mark` sites |
| --- | --- |
| `acceptance.py` | 65 |
| `desktop/src/renderer/renderer.ts` | **87** |
| `note_writes.py` | 17 |
| `validate_docs_bundled.py` | 15 |
| `cockpit.py` | 9 |
| `server.py` | 6 (five acceptance endpoints, incl. `POST /api/notes/mark-check`) |
| `renderer.py`, `templates.py`, `obligations.py`, `standing.py`, `fleet_validate.py` | 8 combined |

The TypeScript renderer alone carries more mark references than any Python module, and the source proposal does not mention it.

**[[ADR-0027]] is untouched and gets no easier.** Per-check obligations stay forbidden. A ledger with 671 entries must not become 671 badges; the release gate stays one aggregated row.

**[[ADR-0035]] is reinforced.** A release page reports and does not record — and under this decision the thing it would have recorded into does not exist on the page at all. The ledger is written by a walk, a runner or a migration, never by a report.

**Two live issues are answered rather than closed by this decision.** [[ISS-0206]] gets its explicit ruling (platform is not a note field; a release's checks are the ones its ledger carries). [[ISS-0208]] does not: `tier:` and the fail-closed clause are orthogonal to where the verdict is stored, and the six unwalked Tier 3 checks still need Edwin's reading.

## The limit, stated plainly

**None of this sees a behaviour that has no check.** The ledger makes coverage *legible*, not complete. `your-trainer` has zero acceptance checks for intervals.icu, MCP, the live route map, or the History dashboard's 28-day chart — all shipped — and after this migration there still will be none. They will be **visibly absent instead of invisibly absent**, which is worth something and is not the same thing.

That gap closes through [[FEAT-0132]] (a feature is scaffolded with its check, and close-out gates on it) and [[FEAT-0130]] (a surface exists whether or not a check names it) — not through the ledger. **This is also why the ledger does not yet subsume `PARITY_MATRIX`**: the matrix's failure mode 1 is precisely the surface-with-no-row case, which is [[FEAT-0130]]'s work. What the ledger *does* subsume is the matrix's per-behaviour verdict columns and its in-matrix back-port table — because under per-behaviour checks an Android fix invalidates **the check**, re-arming both platforms at once, which is the structural fix for the `ISS-0365`/`ISS-0366` class. Retiring the matrix is a decision for `your-trainer` after [[FEAT-0130]], and this ADR does not make it.

## Alternatives

- **Option 1, leave it.** Rejected on the 579 notes claiming a platform-free result they do not have, and on `invalidated_by:` existing only to reconstruct from one scalar what a log carries natively.
- **Option 2, `platform:` on the note.** Rejected as `PARITY_MATRIX` in frontmatter: per-note, hand-maintained, and rotting by the mechanism the matrix already demonstrated eight times in one device session.
- **One ledger with a `platform:` per entry.** Simpler file layout, and it makes "was release R walked" answerable only by filtering. Rejected because releases genuinely are per-platform where this bites, so the file boundary and the fact boundary coincide — and because a single file is a single append point for two independent cadences.
- **One exception value, as today.** Keep `na`/`canceled` alone and let it carry both *cannot apply here* and *not done this cycle*. Cheapest, and it is what the code does now — which is exactly why it is rejected: the two differ in whether the exception comes back, and one value cannot answer that. [[ADR-0029]] already tried to hold the distinction across two marks and lost it in a move nobody noticed for three weeks.
- **Make `blocked` clear the gate**, on the reading that *"unable to test"* should never hold a release. Rejected: `na` and `excused` are decisions somebody made about this release, and `blocked` is an accident that will be gone next week. A gate that clears because the rig was down clears on whatever happens to be broken that day — and the person who would have made that call was never asked.
- **YAML for the ledger**, as this ADR's first draft proposed on hand-editability. Rejected on measurement: the project has never written YAML — `yaml.dump`/`yaml.safe_dump` occur zero times in `src/` and `tools/scripts/` — so it would mean a first, hand-rolled YAML writer on the file CI appends to most often. *Edwin, 2026-08-19: "use json instead of yaml."*
- **Keep `automation:` as a note field alongside the ledger.** Rejected: [[DES-0012]] D2 already ruled that `command:` is the single answer to *who runs this*, and `automation:` disagreeing with itself (66 Tier 3 checks in an area named *"Fully Automated"* carrying `automation: manual`) is the evidence that a standing claim rots.

## Decision record

> [!note] Proposed — 2026-08-19
> Awaiting Edwin. What acceptance would cover: the fourth schema change to this corpus in four weeks; a gate that tightens sharply on `your-trainer` because 513 Android passes stop counting for iOS; `rerun` retired three weeks after being minted; and a read/write path spanning 87 TypeScript sites and six Python modules.
>
> **Amended 2026-08-19, twice, before acceptance.** Decision 6 was rewritten and decision 7 added after Edwin asked how to record *unable to test* and *not tested* separately — the answer being that the schema cannot, and that the per-release exception [[ADR-0029]] designed stopped expiring when its mark moved. Decision 9 moved the ledger from YAML to JSON on his instruction, and the measurement behind it is better than the argument the first draft gave.
