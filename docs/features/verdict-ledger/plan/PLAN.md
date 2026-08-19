# Plan — a verdict is an event

[[PHASE-038-A-Verdict-Is-An-Event]]. Six features, twenty tasks, three issues, one decision ([[ADR-0037-A-Verdict-Is-An-Event]]).

**Nothing here starts until [[ADR-0037]] is accepted.** It reads `proposed`, which is the gate [[ADR-0030]], [[ADR-0031]] and [[ADR-0034]] all used: the phase is documented in full, and no note migrates.

## Order, and why

**0. [[TASK-0532]] — the splitter — is first and is not negotiable.** [[ISS-0216]]: the row parser drops every physical line after the first in a hard-wrapped bullet, silently. Six notes in `your-trainer` are already truncated by it and one body is the word `From`. Running another migration through a parser that loses input is how the same damage gets multiplied.

**1. [[FEAT-0133]] — the ledger file.** JSON, at `docs/releases/ledgers/`. Everything else reads or writes it. The backfill ([[TASK-0529]]) is inside this feature rather than after it, because a format with no data in it is a format nobody has tested. **Sealing is not bookkeeping** — it assigns events to a release *and* expires that release's `excused` entries ([[ADR-0037]] decision 7), which is the one behaviour of the seal that changes what the gate says next cycle.

**2. [[FEAT-0134]] — the note sheds the verdict.** Upstream first ([[TASK-0530]]), then the migration ([[TASK-0531]]). One commit strips and emits, so no state exists where both hold a verdict.

**3. [[FEAT-0135]] — the queries.** The gate must keep answering throughout, so this is Stage 1 and not a follow-on. [[TASK-0534]] carries the phase's only real risk: the per-repo gate delta.

**4. [[FEAT-0136]] — the cockpit.** Read path, write path, 87 TypeScript sites, five endpoints. Largest single body of work and pointless before the format and the queries are settled.

**5. [[FEAT-0137]] — the vocabulary.** Independent of the others and could go first; placed here because [[ISS-0218]] is a live defect the ledger does not cause and does not need. If [[ADR-0037]] is declined, **this feature survives on its own** — the same test [[ISS-0198]] applied to itself.

**6. [[FEAT-0138]] — observed coverage.** Stage 2. [[TASK-0541]] (seed the mapping) must land before [[TASK-0530]] removes `automation:`, which is the one cross-stage ordering constraint in the plan.

## Two amendments to [[ADR-0037]], made before acceptance

Both are Edwin's, 2026-08-19, and both are recorded in the ADR's decision record rather than folded in silently.

**"Not run" is three answers, not one.** Asked how to record *unable to test (with reason)* and *not tested (with reason)*, and whether either should gate. Measured: today `excused` → `mark: canceled` is the only non-gating route, and *"not tested, and here is why"* is structurally impossible — `_mark_check_note` blanks `verdict_reason` when a mark is cleared. Decision 6 now splits it into `na` (cannot apply here — clears, persists), `excused` (not done this cycle, by decision — clears, **expires at the seal**) and `blocked` (could not run it right now — **gates**). Decision 7 is new and carries the expiry rule.

That surfaced a live defect: `Item.excepted` is scoped to nothing, so **an exception never expires**, while the comment above it still describes the per-release property [[ADR-0029]] removed when the mark moved from `[!]` to `[-]`. Latent — `mark: canceled` is written 0 times in all three repos — and unfiled as an issue; if the ADR is declined it should be.

**JSON, not YAML.** Decision 9. The measurement is better than the first draft's hand-editability argument: `yaml.dump`/`yaml.safe_dump` occur **zero times** in `src/` and `tools/scripts/`, so YAML would mean this project's first hand-rolled YAML writer on the file CI appends to most often.

## Progress — 2026-08-19

Stage 1, against Edwin's goal *"implement, test and independently review the full PHASE-038 functionality, Stage 1 only."*

| task | state | |
| --- | --- | --- |
| [[TASK-0532]] splitter | **done** | ran first; six truncated notes in `your-trainer` repaired |
| [[TASK-0527]] ledger schema | **done** | `ledger.py`, JSON, `entries` + `evidence` |
| [[TASK-0528]] validator | **done** | six `LEDGER-*` codes |
| [[TASK-0529]] backfill | **done** | delta **0** in all three repos; cockpit applied |
| [[TASK-0533]] run list | **done** | `ledger.owed` — not wired to the badge |
| [[TASK-0534]] gate | **done** | reads the shipping platform's ledger |
| [[TASK-0535]] burndown | **done** | no rendered view |
| [[TASK-0536]] read path | **done** | `apply_ledger`; the frontmatter-read guard is owed |
| [[TASK-0537]] write path | **done** | `record_verdict`; concurrency not addressed |
| [[TASK-0539]] vocabulary | **done here, not upstream** | |
| [[TASK-0540]] drift check | **done** | mutation-proven both ways |
| [[TASK-0544]] evidence | **decided, part-built** | schema done; `Item.evidence` waits on [[TASK-0530]] |
| [[TASK-0530]] remove the fields | **not started** | upstream-first, and the fleet repos are a generation behind |
| [[TASK-0531]] migration script | **not started** | |
| [[TASK-0538]] renderer | **not started** | 87 sites |
| [[TASK-0545]] `suite_at` | **not started** | |
| [[TASK-0546]] `tests_verified` | **not started** | |

**[[FEAT-0133]] and [[FEAT-0137]] are `doing`, not `done`, and the validator is why.** Both were set to `done` and `FEATURE-REQ`/`VERIFY` refused it, correctly: [[TASK-0544]] still owes `Item.evidence` reading the ledger and [[TASK-0539]] still owes the upstream copy. A feature whose task has an open item is not finished, and the gate said so before anybody had to notice.

**The read path and the write path both exist and neither is the only path yet.** That is the honest state of a migration whose second half ([[TASK-0530]], removing the seven fields) has not run: `mark_check` still writes notes for the nine fleet repos with no ledger, and `apply_ledger` is an overlay rather than a replacement. Nothing is dual-written — a repo has a ledger or it does not — but the frontmatter-read guard [[REQ-0055]] asks for cannot be written until the field is gone.

## Independent review, 2026-08-19 — `changes-requested`, ten findings, all addressed

The verdict was right and the findings were real. Two could have destroyed data and one was a false claim in this very file.

| # | finding | fix |
| --- | --- | --- |
| 1 | **The migration measured a smaller corpus than the gate it protects.** `backfill-ledger.py` called `acceptance.load(docs)` with no index; every production gate passes one, and the indexed branch finds acceptance tests anywhere under `docs/`. 581/62 in `your-trainer`, not 579/60 | builds an index; delta re-measured and still 0 everywhere |
| 2 | **An expiring mark destroyed the verdict underneath it.** `pass` in REL-0001 + `excused` in REL-0002 resolved to *nothing* after the seal — contradicting decision 7 in as many words. Benign for the gate, **not** for the burndown, which selects A-`pass` rows | `resolve` keeps a standing and a transient layer |
| 3 | Three of four `close_row()` sites were unguarded — two tests passed with the thing they name deleted | three distinguishing tests; all four sites mutation-proven |
| 4 | The continuation rule folded ordered lists, tables, headings and quotes — the docstring's own argument, ignored | exclusion widened to five shapes, four parametrised guards |
| 5 | A ledger whose filename misses the naming rule still vanished from its own platform | reader refuses; `LEDGER-NAME` in the validator |
| 6 | **`validate_ledgers` had no test at all** — 142 lines, six codes, `grep LEDGER- tests/` empty | 18 tests, one per defect |
| 7 | The drift check left the persistence column free — flipping `na` to *expires* stayed green | reads both behaviour columns |
| 8 | "Has a ledger" meant *the directory exists*, which `write()` creates first | `has_ledger()` looks for a file |
| 9 | **`mark_check` could still write a scalar in a repo with a ledger**, and `walkOneCheck` sends no platform | refused with a 409 |
| 10 | dates were shape-checked (`2026-13-45` passed); resolution was file order; `by` defaulted to a hardcoded name; `release` unguarded in a filename; seven `done` tasks had every DoD box unticked | each fixed |

**Three corrections to claims in this record**, because a wrong number is a finding too: `your-trainer` is **581 checks / 62 blocking / 507 owed on iOS** (not 579/60/505); `automation:` is non-empty on **669** of 671, and 203 is the count that is not `manual`; and **this file's "nothing is dual-written" was false of this repo** — it held a ledger *and* 34 notes carrying `mark:`. Finding 9 is now what makes it true.

**Two things the review left standing that are worth naming.** `LEDGER-SEALED` compares the working tree to `HEAD`, so editing a sealed ledger **and committing it** passes forever — filed as [[ISS-0220]], with the gap asserted by a test so it cannot quietly stop being true. And [[TASK-0534]], [[TASK-0536]] and [[TASK-0539]] went back to `doing`: each has one genuinely open DoD item, and a task with an open box is not done — the same rule the validator taught about [[FEAT-0133]] an hour earlier, one level down.

## The through-line

**Every deformation this phase fixes has the same cause: a scalar holding a fact with three dimensions.** The platform silence, `invalidated_by:` reconstructing history from one field, `automation:` as a claim that rots, `todo` as a value meaning "no data" — each is what a one-slot container does to a three-slot fact.

And every task has the same obligation as [[PHASE-037]]'s, in a different register: **measure the movement before making it.** [[TASK-0529]] and [[TASK-0534]] both refuse to run until a number is written down, because this phase moves a release gate and the last three schema changes to this corpus did not.

## Three gaps the audit found, 2026-08-19

Each of [[ADR-0037]]'s ten decisions was checked against a task after the two amendments landed. Three had none, and all three are the same shape: **a surface that reads the verdict from the note and was not on anybody's list.**

- **[[TASK-0545]] — `suite_at` gets a third shape.** It already carries two, split by time. A ref after this migration holds notes with no verdict in them. **This is the only one that produces a wrong answer rather than an error**: every historical tag would report zero walked, and the chronic-rows surface would call every row chronic.
- **[[TASK-0544]] — `evidence:` has no destination.** [[REQ-0053]] removes seven fields; six have a home or a stated reason to go. [[ADR-0030]] led its list of what granularity *genuinely unlocked* with per-check evidence attachments, so deleting the field silently gives that back.
- **[[TASK-0546]] — `tests_verified:` on a release** answers the same question a sealed ledger answers, by hand. Two encodings of one fact is what [[ADR-0032]] spent a decision removing.

[[TASK-0529]] also gained the `canceled` migration rule, which decision 6 created by giving one old value two successors — a backfill that guessed would make a permanent exception expire, or a per-release one permanent.

## What is deliberately not here

- **[[ISS-0208]]** (the tier rule) — orthogonal. Where a verdict is stored says nothing about which checks gate, and the six unwalked Tier 3 checks still need Edwin's reading.
- **[[ISS-0209]]** (the fleet validators) — a migration per repo, and the reason nothing this phase builds is enforced where the checks live. Stated as a limit in [[REQ-0057]] and [[TASK-0543]] rather than absorbed.
- **[[ISS-0215]]** (156 stranded checklist rows in four notes) — not in the suite, so this migration does not reach them. They need a surface and a `covers:` per row first.
- **Retiring `PARITY_MATRIX`** — the ledger subsumes its verdict columns and its back-port table, not its coverage-gap question. That is [[FEAT-0130]]'s `SUR-*` work and `your-trainer`'s decision.
- **[[FEAT-0130]] and [[FEAT-0132]]** — the ledger makes coverage legible, not complete. A behaviour with no check stays invisible to all of this.

## The four measurements this plan rests on

Taken 2026-08-19 across `project-os-cockpit`, `your-trainer` and `your-sudoku`, and each one corrected the source proposal:

1. **671 acceptance notes; `verdict_date`, `verdict_reason`, `invalidated_by` and `covered_by` are empty on all 671.** Four of the seven removed fields cost nothing to remove.
2. **The live mark vocabulary is three values** — `done` 546, `todo` 124, `incomplete` 1. `canceled`, `important`, `question` and `rerun` are written zero times, so the vocabulary can be settled on the argument rather than on the migration cost.
3. **579 of `your-trainer`'s 581 acceptance notes carry no `platform:`** — and the two that do are the notes [[TASK-0507]] relevelled from ordinary tests the day before. The absence is a migration artefact, not a position.
4. **`renderer.ts` carries 87 `mark` sites**, more than any Python module. The proposal's "~9 cockpit modules" understates the cost.
