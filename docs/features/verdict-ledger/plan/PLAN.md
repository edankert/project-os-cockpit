# Plan — a verdict is an event

[[PHASE-038-A-Verdict-Is-An-Event]]. Six features, seventeen tasks, three issues, one decision ([[ADR-0037-A-Verdict-Is-An-Event]]).

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

## The through-line

**Every deformation this phase fixes has the same cause: a scalar holding a fact with three dimensions.** The platform silence, `invalidated_by:` reconstructing history from one field, `automation:` as a claim that rots, `todo` as a value meaning "no data" — each is what a one-slot container does to a three-slot fact.

And every task has the same obligation as [[PHASE-037]]'s, in a different register: **measure the movement before making it.** [[TASK-0529]] and [[TASK-0534]] both refuse to run until a number is written down, because this phase moves a release gate and the last three schema changes to this corpus did not.

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
