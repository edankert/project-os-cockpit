---
type: "[[feature]]"
id: FEAT-0118
aliases: ["FEAT-0118"]
title: "The test type absorbs the check — one schema, `level: acceptance` as the discriminator, and `retired` at last"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
goal: "Make `[[test]]` the single type for anything that verifies behaviour, with `level: acceptance` carrying the distinction the `check` type used to carry, so that a check and a test differ by a field rather than by a schema — and so that adding `command:` is all it takes to automate one."
requirements: ["[[REQ-0037-The-Badge-Never-Admits-Acceptance-Tests]]"]
tasks: ["[[TASK-0473-Test-Statuses-Gain-Active-And-Retired]]", "[[TASK-0474-The-Test-Schema-Absorbs-The-Check-Fields]]", "[[TASK-0475-Level-Acceptance-Becomes-The-Discriminator]]", "[[TASK-0476-The-Validator-Learns-The-Merged-Type]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[ISS-0178-A-Test-Cannot-Be-Retired]]", "[[ISS-0195-Two-Types-Carry-One-Act]]"]
---

# The test type absorbs the check

**Upstream first, entirely.** Every file this feature touches is template-owned — `STATUSES.md`, `TAXONOMY.md`, `QUALITY.md`, `TESTING.md`, `SCHEMAS.md`, `test.md`, `check.md`, `validate-docs.py` — so all of it lands in `~/Dev/repos/project-os` and syncs down before a single note changes type in any repo. That is [[ADR-0030]] decision 6, carried forward unchanged and for the same reason: nothing here carries permanent template divergence.

**The status vocabulary is the load-bearing change.** Tests go from three values to five. `active` is what makes the merge safe — an acceptance test that rests at `active` reaches neither the review gate nor the Run obligation, by the same construction the `check` type used. `retired` is what makes it worth doing twice: [[ISS-0178-A-Test-Cannot-Be-Retired]] has been `deferred` because the vocabulary had no terminal value, and this repo's TST-0029 is the live instance — subject deleted, retired in prose because there was no word for it.

**`check.md` is deleted, not tombstoned.** The template directory is a scaffolding source; a template for a type that no longer exists scaffolds notes the validator will reject.
