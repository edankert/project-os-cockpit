---
type: "[[reference]]"
id: TESTING-MODEL
aliases: ["TESTING-MODEL"]
title: "The testing model — one type, a level scale, and who runs what"
status: active
owner: user:edwin
created: 2026-08-18
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: changes-requested
scope: tests
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]"]
---

# The testing model

> [!warning] Superseded in substance by [[PHASE-036-One-Human-Walk]], 2026-08-18.
> Everything below describes the model **before** ADR-0034 separated the three axes. It still documents the four-heuristic `_is_manual_test`, the two-predicate disagreement, the character marks and a group called `Needs a run` — none of which is current. It is kept because the *reasoning* is still the clearest account of why the merge happened, and because rewriting a reference note into pretending it always said the right thing is how a record stops being one.
>
> **What is current**: `level:` says what a test exercises, `command:` says who runs it and how it re-arms, `covers:` says what it gates. Marks are the seven words. The verb is *walk*. Read [[ADR-0034-Three-Axes-Not-One-Word]] and the phase note.

**Written down at Edwin's request, 2026-08-18, after PHASE-035 closed.** It describes what is *implemented*, not what was intended — where the two differ, the difference is named. The open questions this raised are [[ISS-0200-Marks-Versus-Statuses]] … [[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]].

## One type, one scale

There used to be two types. There is now one — `[[test]]` — and a scale, `level:`, running `unit → integration → system → e2e → acceptance`.

A note moves **along** that scale rather than **between** types, and that is the point: adding a `command:` is how a hand-walk becomes automated, without changing what the note is or breaking anything that points at it. Before [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]], a check could not be automated at all — the asymmetry that caused the merge.

## Who runs it: `command:` decides

`cockpit._is_manual_test` asks, in order:

1. **Does it declare a `command:`?** → the machine runs it. Full stop.
2. Otherwise, does `kind`/`automation`/`mode`/`method` say manual? → a person.
3. Otherwise, does the body have a Steps section? → a person.

The order matters and was a fix: a test with a pytest `command:` and a checklist-shaped body used to be offered a manual stepper and counted among the tests a scope asks a human to walk.

**But there are two rules, not one, and this note claimed otherwise.** `obligations._is_owed` decides the `Run` obligation — the thing that fills `Needs a run` and the badge — with its own predicate: *does `kind`/`level`/`runner` contain "manual"*, and it never reads `command:` at all. **8 of 788 fleet tests disagree between the two.** None involves a `command:`, so it is latent rather than live. [[REQ-0041-One-Answer-To-Who-Runs-This]] closes it.

## Two populations, one type

| | **automated test** (`command:`) | **manual test** | **acceptance test** (`level: acceptance`) |
|---|---|---|---|
| executed by | CI | a person | a person, in `~checks` |
| result in | **nowhere** — the note records no verdict ([[ADR-0038]]) | `status:` — `passing`/`failing`, author-written | `mark:` — `" " x / - ! ?`, with `verdict_date:` and `verdict_reason:` |
| rests at | `active` | `ready` (defined, never executed) | `active` |
| terminal | `retired` | `retired` | `retired` |
| goes stale by | **nothing** — CI is current by construction | **time** — `last_verified:` against a threshold | **change** — `invalidated_by:` against `verdict_date:` |
| gates | a task/issue/feature reaching terminal, discharged when its `command:` resolves | the same, discharged by `passing` and not stale | the release (any unsettled manual check ⇒ blocked) |
| appears in | `Automated tests`, or `Broken command` when its command stops resolving | `Needs you` when owed | `Feature tests` / `Regression tests`, and `~checks` |

*(Corrected 2026-08-19, [[ADR-0038]] and [[ADR-0039]]. The `result in` row used to read **"written by the runner from the exit code"** and the last row named `Tier 1/2/3`. Both are reversed: an automated test records no verdict, and there are no tiers — a check's section is derived from `covers:` and `command:`.)*

**Walking an acceptance test never touches `status:`.** That one rule carries the design.

## Why that rule is load-bearing

Three gates key on statuses an acceptance test does not hold, so all three stay off several hundred notes **by construction rather than by exemption**:

- the **independent-review gate** fires at `passing` — it rests at `active`;
- the **runner-only rule** governs `passing`/`failing` — its verdict is not a status;
- the **`Run` obligation** fires at `ready` — it rests at `active`.

The third is the dangerous one: it is what keeps a self-re-arming suite off a badge nobody could act on ([[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]). Because it is a construction and not a rule, one careless status write disarms it — so `ACCEPTANCE-STATUS` is a validator **error** if an acceptance test holds `ready`/`passing`/`failing`. `passing`/`failing` are excused **only** with a `command:`, since the runner then owns them. **`ready` is never excused**: that is the status the badge counts.

## The automation path

> ⛔ **SUPERSEDED 2026-08-21 by [[REQ-0057-Coverage-Is-Observed-From-A-Run]] / [[FEAT-0138-Coverage-Is-Observed-Not-Declared]].** Marked in this section's own first line, not only in the banner at the top: a heading is a landing target, and a reader arriving by link or scroll never sees a warning further up.
>
> **`covered_by:` and `automation:` are gone, and `note_writes.cover_check` is deleted.** A note no longer declares that a machine covers it. The **test** declares the check — `# Covers: TST-0016` in its own source — and a **run** emits a `method: automated` verdict into the ledger, so deleting the covering test stops the emission and the check reappears on the run list by itself.
>
> Everything below was true of the code and **had never once been true of the corpus**: the field held nothing on 671 of 671 checks fleet-wide ([[ISS-0198]]), and the write path that could have filled it was reachable from no front door ([[ISS-0249]]). The six refutations recorded further down are about a mechanism that never settled a single check in any repo.
>
> The direction it protected survives and is now structural rather than guarded: a machine's exit code can discharge a person's checkbox and never the reverse, because **only a run emits `method: automated`**.

```yaml
covered_by: ["[[TST-0016-Seat-Resolution]]"]
automation: full
```

`Item.settled` is: the mark is settled **or** every test in `covered_by:` is `passing`. So automating a check discharges it. Three properties, each corrected during review:

- **all covers must pass, not any** — one passing and one failing used to settle it;
- **only an executable test counts** — a manual `passing` would let one hand-walk launder itself into another's automation;
- **resolved at load, never stored** — which is why a *failing* cover un-settles the check, and why a `ready` cover settles nothing. *"Not failing"* is not coverage.

`note_writes.cover_check` writes the link behind **six** refusals — empty `covered_by`, an automation value outside `full`/`partial`, `partial` without a reason, an unresolvable id, a target that is not a test, and a target with no `command:`. The last is the load-bearing one.

## The verification link

[[ADR-0032-The-Verification-Link-Has-One-Direction]]: **one encoding, one direction — the test's `covers:`**. A feature does not list its tests; surfaces derive that from a reverse index. The previous arrangement had three encodings (the directory path, the test's `features:`, the feature's `tests:`) and 10 of 61 edges already disagreed.

## What the cockpit implements today

> ⛔ **PARTLY SUPERSEDED 2026-08-21 by [[REQ-0057]].** In this section's own first line, because *a heading is a landing target* — the banner on `## The automation path` above does not reach a reader who arrives here.
>
> Every mention below of **`covered_by:`**, of **`automation:`** as a coverage claim, of **`_resolve_coverage`**, and of *"Covered by"* as something the cockpit writes describes a mechanism that **no longer exists**. The three properties the Verified section says *"all hold"* held of code that is deleted. A test declares the check in its own source and a run emits the verdict into the ledger.
>
> The rest of the section — the six derived tests-view groups, `_is_manual_test`, the two-predicate disagreement, the staleness row and its corpus caveat — is unaffected, and is why this file is kept rather than rewritten.

**Tests view** — six sections, every one of them derived ([[ADR-0039]]):

- `Needs you` — what a person owes, gathered from the sections below.
- `Feature tests` — `covers:` names a `FEAT-*`. Re-checked when a change overlaps.
- `Regression tests` — `covers:` names an `ISS-*`. Completed once, never re-opened by a change.
- `Automated tests` — `command:` is non-empty. Executed by CI, no verdict, no checkbox.
- `Broken command` — an automated test whose `command:` no longer resolves. The one thing an automated test can owe a person.
- `Retired` — the subject is gone; kept as record.

**`~checks`** — section → area → rows, the six-mark dialog, and filters over mark, area, covers and automation.

**Writes** — mark, *Needs re-check* (clears the mark and names the invalidating change in one write), *Covered by* and retire. Each refuses rather than accept a claim nobody can check.

*(Corrected 2026-08-19. This list used to name `Needs a run`, four verdict-state groups and `Tier 1/2/3`. The verdict states went with [[ADR-0038]] — an automated test has no verdict, and 37 of this repo's 38 sat in one collapsed `Verified` group — and the tiers went with [[ADR-0039]].)*

**Reads** — `## Runs` parses back, so a partly-walked procedure can say which steps stand. *(This belongs to the executable/manual half, not the acceptance surface it is filed under here: 14 notes fleet-wide carry a `## Runs` section, all in this repo, none at `level: acceptance`.)* A step's state is: a step's state is its result in the most recent run that **mentions** it, so a partial walk does not un-prove what it never reached.

## What is not true yet

**Nothing in the fleet is discharged by automation.** `your-trainer` has 203 notes whose bodies name 54 JVM test classes. **Four do name a `TST-*` id** (`TST-0050`, `TST-0051`, `TST-0364`, `TST-0586`) — this note originally said none did — but 199 do not, so the gate has almost nothing to check. The mechanism is proven; the corpus has not been given data it can act on.

**Release membership does not exist for tests.** A check cannot be marked as belonging to a release, so `your-trainer`'s iOS-only checks sit in the same undifferentiated blocking set as everything else. See [[ISS-0202-Needs-A-Run-Versus-The-Tiers]].

## Independent review

**2026-08-18, `model:claude-opus-5`, fresh context — the notes, the diff of `2c79393`, the code and the live payloads on `:8765`/`:8766`. Verdict: `changes-requested`.** Not because the model is wrong — most of it verified exactly — but because five statements are refutable as written and three material facts are missing. Same model family as the author, different session, no access to the authoring reasoning (ADR-0013).

### Verified against the code, unchanged

> ⛔ **Partly superseded 2026-08-21 by [[REQ-0057]]**, in this heading's own first line. Anything below about `covered_by:`, `automation:` as a coverage claim, `_resolve_coverage` or `note_writes.cover_check` is written in the present tense about code that is **deleted**. *"All three hold"* held; it does not now.

- **`_is_manual_test` precedence** — `cockpit.py:2609`. `command:` first, then `automation`/`kind`/`mode`/`method`, then a Steps section. The order is as documented. (One thing the summary omits: an explicit `automated`/`auto`/`ci` on any of those four keys returns *machine* before the Steps fallback is reached.)
- **The three gates and `ACCEPTANCE-STATUS`** — `REVIEW_SETTLED_STATUSES = {"tests": ("passing",)}`, `TEST_RUNNER_STATUSES = ("passing","failing")`, `OBLIGATIONS["test"] = Obligation(("ready",), …, "Run")`. `ACCEPTANCE_FORBIDDEN_STATUSES = ("ready","passing","failing")`; with a `command:` the forbidden tuple drops the two runner statuses and keeps `ready`. It is `report.error` unless grandfathered. Exactly as written.
- **`Item.settled` / `_resolve_coverage`** — all-covers-must-pass (`bool(...) and all(...)`, empty tuple first), executable-only (a cover without `command:` resolves to the literal `not-executable`), resolved at load and never stored. All three hold.
- **The Tests view group list** — six buckets plus the tier groups, each absent when empty, acceptance excluded by `level`. Correct.
- **A step's state is its result in the most recent run that *mentions* it** — `manual_test_step_state` walks runs oldest-first and overwrites per step text. Correct.
- **Nothing in the fleet is discharged by automation** — 669 of 669 acceptance notes carry `covered_by: []` (34 + 56 + 579). Verified, and sharper than the note puts it: `cover_check` refuses any test without a `command:`, and **`your-trainer` has exactly 2 tests fleet-eligible to be named** (`LicenseSeatResolverTest`, `Migration34To35Test`). 50 tests carry a `command:` across all twelve repos, 38 of them in this one.

### Refuted

> ⛔ **Partly superseded 2026-08-21 by [[REQ-0057]]**, in this heading's own first line. Anything below about `covered_by:`, `automation:` as a coverage claim, `_resolve_coverage` or `note_writes.cover_check` is written in the present tense about code that is **deleted**. *"All three hold"* held; it does not now.

1. **"`note_writes.cover_check` writes the link behind four refusals."** It is **six** — empty `covered_by`, an automation value outside `full`/`partial`, `partial` without a reason, an id the index cannot resolve, a target that is not a test, and the `command:` one. (A seventh `raise` is an I/O error.)
2. **"not one names a `TST-*` id"** — four `your-trainer` acceptance bodies do: `TST-0050`, `TST-0051` (naming TST-0009), `TST-0364` (TST-0010), `TST-0586` (TST-0008). The *point* survives — all four name manual tests, none is a `covered_by:` link — but the sentence is false and this document says it describes what is implemented.
3. **"One rule for *who runs this*, not two."** There are two. `obligations._is_owed` decides whether a person owes a `Run` with its own predicate — `"manual" in (kind|level|runner)` — which never reads `command:`. It is that rule, not `_is_manual_test`, that fills `Needs a run` and the Tests badge. Measured: **8 of 788 fleet tests disagree between the two predicates** today, none of them involving a `command:`, so the divergence is latent rather than live — but a note with a `command:` and `kind: manual` at `ready` would be offered to a person by the badge while `_is_manual_test` calls it automated.
4. **"`Needs a run` — non-acceptance manual tests at `ready`."** Incomplete in the way that matters: the bucket is `_owed_flag(...).owed`, which also requires the subject to be in flight. That missing clause is the whole of [[ISS-0202-Needs-A-Run-Versus-The-Tiers]] — this repo's one row is there *because* two `draft` requirements outvote a `backlog` feature.
5. **"`## Runs` parses back"**, placed under the `~checks` heading, reads as a property of the acceptance surface. It is not: **14 notes in the fleet carry a `## Runs` section, all in this repo, none at `level: acceptance`.** The read-back is real and it belongs to the executable/manual population.

### The staleness row is true of the code and false of the corpus

`Item.stale` implements exactly what the table says. But **all 669 acceptance notes carry `invalidated_by: {}`** — the change-driven half has no data anywhere in the fleet, which is the same caveat this document makes for automation and does not make here.

Worse, the data existed. `your-trainer`'s 54 `RE-RUN` annotations were migrated into `invalidated_by:` by ADR-0030 and were **still populated at the merge commit `0535db82`**. They were cleared afterwards by an uncommitted bulk write — 54 files, all mtime `13:17:41` on 2026-08-18, each diff exactly `invalidated_by: {…} → {}` plus an `updated:` bump. Consequence, measured by parsing the pre-migration suite at `5976a658`: **53 stale Tier 1/2 rows then, 0 now.** The gate's honest figure was 60 blocking + 53 stale; the release page's `Stale evidence` group is now permanently empty. The merge script's own parity fingerprint *does* include `invalidated`, so the merge did not do it — and the pilot could never have caught it either way, because this repo's 34 and `your-sudoku`'s 56 had zero invalidations on both sides. It is recoverable: `git -C ../your-trainer checkout -- docs/tests/acceptance`.

### Materially true and omitted

- **The sweep still writes the retired type, and a migrated repo cannot see what it writes.** `sweep._write_new_check` authors `type: "[[check]]"` with a `CHK-####` id. `acceptance.load` reads `[tests at level: acceptance] or [notes_by_type("check")]` — so in any repo that has migrated, the `or` never evaluates and a swept check is invisible: absent from `~checks`, absent from the tiers, and not blocking. Proved on a two-note corpus (one `TST` at `level: acceptance`, one `CHK`): the reader returns one item. The obligation is live right now — 1 feature owes a Sweep here, 4 on `your-trainer` — and `tests/test_acceptance_sweep.py` cannot fail on it, because its entire fixture is `type: "[[check]]"` notes, which is the branch that no longer exists in the three migrated repos.
- **The release page still speaks the pre-migration address.** `buildGateSection` renders each blocking row by `item.number` (`1.4.20`) and navigates to `/docs/${gate.rel}#${item.anchor}`, where `gate.rel` is the *directory* `tests/acceptance` and the anchor is the old document's. Every row therefore lands on the suite README with a dead fragment, while `item.rel` — the check's own note — sits unused in the same payload. `_acceptance_tier_groups` compensates for the notes shape by sending `~checks`; this call site does not.
- **`suite_rel`'s docstring claims it returns "the generated view" for notes shape.** It returns `CHECKS_REL`, a directory. Only the tier-group caller adds the `~checks` substitution; every other consumer of `rel` inherits the directory.

## Overturned 2026-08-18 — the two populations are one

This note described `Needs a run` and the tiers as two things and offered a distinction: *a manual test verifies a change and retires; an acceptance test names standing behaviour and re-arms.*

Edwin: *"Why would these manual tests not be true in a year? If the feature changes, or code the feature depends upon changes, the test has to be re-run. I think a manual test is always an acceptance test."*

**The first half was fiction and the corpus says so.** `TST-0024` does not retire when FEAT-0099 ships — it re-arms the next time that code changes. `your-trainer`'s `TST-0018`, cited here as the example of a retirement path, says of the half that stays: *"which stays manual permanently."* Zero of 22 manual tests fleet-wide have ever been retired by automation.

And the one genuine verify-this-build-then-stop case — this repo's `TST-0026` and its measured *"64 to 31"* claim — is **a Tier 3 acceptance test**, which TESTING.md already defines as *"one-time checks for a specific build, promoted or removed after a verified release."* It was never a separate kind of note.

**And the reason was wrong too.** [[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]] argued from re-arming and then wrote *"manual tests gate a feature, acceptance tests gate the release"* as an accepted cost. Edwin: *"It doesn't matter … they should be able to gate at any granularity. I think we don't need necessarily acceptance tests any more in that case?"*

Two independent bodies of practice agree with him. **ISTQB** keeps test *level* and test *type* independent expressly to prevent gaps in a test concept, and holds manual-versus-automated out of both as an execution concern; acceptance is a level defined by *whose criteria are checked*, never by who performs it. **The Agile Testing Quadrants** (Marick; Crispin and Gregory) run business-facing/technology-facing against supporting/critiquing — and manual-versus-automated is **not an axis in either**: Q2 is the ATDD/BDD quadrant and is routinely automated.

So `level: acceptance` has been carrying three independent claims: *a person walks it*, *its verdict is `mark:`*, and *it gates the release*. None follows from the word.

[[ADR-0034-Three-Axes-Not-One-Word]] supersedes ADR-0033 and separates them — `level:` says what a test exercises, `command:` says who runs it and how it re-arms, `covers:` says what it gates, at any granularity. [[PHASE-036-One-Human-Walk]] carries the work, gated on a measured precondition: **83 of 669 acceptance tests carry an empty `covers:`** and would gate nothing under a derived rule.

**Read every table above as a description of what is implemented today, not as a design.**


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all four earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. **This supersedes the fourth pass's verdict on this note.**

**Verdict: changes-requested (low).** The fourth pass's finding is **partially** addressed. The new banner is genuinely in `## What the cockpit implements today`'s own first line and it names all four stranded things — `covered_by:`, `automation:` as a coverage claim, `_resolve_coverage`, and *Covered by* as a write the cockpit performs — so the `**Writes** — … *Covered by* and retire` line at 116 and the `automation` filter at 114 are now covered where a reader lands.

**What is still unbannered is the part that asserts the claims in the present tense, under headings of its own.** Line 136, under `### Verified against the code, unchanged`: *"**`Item.settled` / `_resolve_coverage`** — all-covers-must-pass …, executable-only …, resolved at load and never stored. **All three hold.**"* Line 143, under `### Refuted`: *"`note_writes.cover_check` writes the link behind four refusals." It is **six** …"* — present tense about a function that is deleted. The new banner reaches them by naming them, from two headings away; the banner's own argument is that *"a heading is a landing target, and a reader arriving by link or scroll never sees a warning further up"*, and `#verified-against-the-code-unchanged` is a landing target. This is a sentence-level fix on a reference file and it does not block anything.

**Suite, validator, CI step set — observed, not reported.** **2066 passed, 3 skipped** in 269s; `validate-docs: OK` (warnings only); `--as-committed` reports *"HEAD passes the full CI step set"*. Working tree clean at `991838e`.
