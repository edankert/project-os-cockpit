---
type: instruction
id: INSTR-TESTING
status: active
owner: group:maintainers
created: 2026-03-16
updated: 2026-07-17
tags: [instructions, testing]
---

# Acceptance test rules

This document defines the acceptance test tier system, lifecycle rules, and release gating requirements.

## Acceptance test tiers

### Tier 1 — Feature Tests (permanent)
- Verify core user-facing capabilities.
- One or more tests per feature (linked via `FEAT-*` in section headers).
- Always relevant. Never removed.
- Created when a feature is first implemented.

### Tier 2 — Regression Tests (permanent)
- Guard against previously-broken behavior.
- Each references the `ISS-*` that created it.
- Kept permanently — these test edge cases that feature tests don't cover.
- Created when a bug fix is implemented.

### Tier 3 — Verification Tests (temporary)
- One-time checks for a specific build or fix.
- After a verified release, each is either:
  - **Promoted** to Tier 2 if the scenario could regress
  - **Removed** if covered by unit tests or the fix is stable (one-liner, config change)
- Include a note explaining why they're temporary and what unit tests cover them.

## Lifecycle rules

### When to create
1. **New feature implemented** → create Tier 1 test(s) covering the user-visible behavior.
2. **Bug fixed** → create a Tier 2 test that reproduces the original bug and verifies the fix.
3. **One-time verification needed** → create a Tier 3 test with a note about removal criteria.

### When to uncheck (mark for re-run)
- Any code change must uncheck all Tier 1 and Tier 2 tests whose scope overlaps with the changed code.
- Use judgment: a change to `WorkoutViewModel` unchecks workout tests, not Bluetooth tests.
- **Say which change did it, in the same action.** This half of the rule is the one that does not get done: measured across the fleet, 54 rows carried a hand-written `RE-RUN (…)` annotation and **all 54 were still ticked**, because unticking destroyed the only record that the check had ever passed and there was nowhere to say why. In note form that record is `invalidated_by:` — the change id, the reason and the date — written in the same act that clears the mark, and refused without a change id. In document form it stays a `RE-RUN (TASK-####: reason)` annotation on the line.
- Best done **at the close-out of the work that caused it**, not saved up for release time: a sweep over the areas a feature touched, adding the checks it needs and invalidating the ones it overtook, in one commit.

### When to remove
- **Tier 3 tests** are removed after a verified release if:
  - They are covered by passing unit tests, OR
  - The fix is a stable one-liner unlikely to regress, OR
  - The scenario was a one-time data/config fix
- **Tier 1 and Tier 2 tests** are never removed (only deprecated if the feature is retired).

### Unit test replacement
- When unit tests are written that cover the same logic as an acceptance test, the acceptance test can be moved from Tier 2 to Tier 3.
- Add a note to the Tier 3 section: "Covered by `<TestClassName>` (<N> tests). Remove after next release."
- After the next verified release, remove the Tier 3 test.

## Where the acceptance suite lives

**Two shapes, split by time.** A repo stores its acceptance suite one way or the other, never both.

**Notes (current).** One check per note, `type: [[check]]`, id `CHK-*`, at `docs/tests/acceptance/CHK-####-Slug.md`, scaffolded from `../../docs/__templates__/check.md`. `status:` is the lifecycle (`draft`/`active`/`retired`) and **`mark:` is the verdict** — ticking never touches status, which is what keeps a check outside the runner-only rule and the independent-review gate. Tier, area and ordinal are fields; the suite is read as a generated list rather than as a document. See `SCHEMAS.md` `check.md` and `STATUSES.md` `[[check]]`.

**One document (older).** `docs/tests/ACCEPTANCE_TESTS.md`, scaffolded from `../../docs/__templates__/acceptance-tests.md`, with the structure below. A repo that has not migrated keeps using it and everything in this file still applies; a repo that migrates **deletes** it in the migration commit rather than keeping a copy, because two records of one thing is a source of drift and git holds the file at every earlier ref.

The document form:

```markdown
# Acceptance Test Suite: <Project> v<version>

## Test Tiers
<!-- Tier definitions and rules summary -->

## Rules
<!-- Numbered rules for create/uncheck/remove/gate -->

---

# Tier 1 — Feature Tests

## 1.1 <Area> (<FEAT-IDs>)
- [x] **Test Name:** Test procedure and expected result.

---

# Tier 2 — Regression Tests

## 2.1 <Bug Area> (<ISS-ID>)
- [x] **Test Name:** Test procedure and expected result.

---

# Tier 3 — Verification Tests (current build)
<!-- Temporary tests. Remove after verified release. -->

---

# Test Execution Notes
<!-- Prerequisites, environment setup -->

# Release History
<!-- Build notes per version -->
```

## Test adequacy (who verifies the tests?)

A guarding test that cannot fail does not guard: LLM-authored test suites cluster their blind spots in the same places the LLM-authored fix does. Every Tier 2 regression test (and any `TST-*` gating a terminal status) should carry adequacy evidence in its note:

- **Minimum bar (cheap, always possible):** demonstrate the test fails when the fix is reverted or deliberately broken, and record that in the `TST-*` note's Adequacy section (or `adequacy` frontmatter field).
- **Stronger bar (when tooling exists):** run mutation testing over the code the test guards and record the score in `mutation_score`. A surviving mutant in the guarded code means the test does not actually guard it. Per-stack tools: `mutmut` (Python), Stryker (`stryker-js`/`stryker-net` for JS/TS/C#), `cargo-mutants` (Rust), PIT/`pitest` (JVM/Kotlin/Android), `muter` (Swift/iOS); record the tool and command in the test note's evidence so runs are reproducible.
- **Independence:** tests created alongside the fix they guard should get an independent review pass (`../skills/independent-review/SKILL.md`) — the author of a fix must not be the sole judge of its guarding test.
- **Cadence threshold:** if mutation scores on guarding tests are consistently above ~80%, reduce the adequacy-check cadence; below that, keep checking every guarded fix.

## Release gating

- A release is **blocked** if any Tier 1 or Tier 2 test is unchecked (not passing).
- Tier 3 tests do not gate releases (they are verification aids, not requirements).
- A test may be marked as a **release exception** if it cannot be completed (e.g., third-party API key unavailable). Exceptions must be documented in the release note with justification.

## Relationship to TST-* notes

- `TST-*` notes in `docs/tests/` or `docs/features/<slug>/plan/tests/` are individual test specifications with frontmatter, preconditions, procedures, and evidence.
- An acceptance check is a **`[[check]]` note (`CHK-*`)**, or — in a repo that has not migrated — a line in `ACCEPTANCE_TESTS.md`. Either way it is a manual acceptance check: it references features and issues and is **not** a `TST-*` note.
- Both systems coexist: `TST-*` notes for formal test tracking, checks for the release checklist. `level: acceptance` on a `TST-*` is a third, different thing — an automated test at acceptance level — and is not a check.
- The type boundary is load-bearing, not tidiness. A check never reaches `passing`, so the runner-only rule (`STATUSES.md` `[[test]]`) and the independent-review gate (`QUALITY.md`) — both keyed on that status — never apply to one. **The review of a check is the walk.** Checks are also declared owed-nothing in the obligation registry: a suite is hundreds of rows that re-arm on every overlapping change, and counting them individually is a badge that never empties.
