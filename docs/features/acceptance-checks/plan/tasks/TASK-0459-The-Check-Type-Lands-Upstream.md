---
type: "[[task]]"
id: TASK-0459
aliases: ["TASK-0459"]
title: "The check type lands upstream — five template-owned surfaces change in ~/Dev/repos/project-os and sync down before any CHK-* note exists"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
parent: "[[FEAT-0113-The-Check-Type-And-The-Migration]]"
effort: M
depends: []
blocks: []
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
tests: []
---

# The check type lands upstream

Gated on [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] being `accepted` — this task is the first thing that happens afterwards and everything else in the phase queues behind it, because nothing here carries permanent template divergence.

## The edits, all in `~/Dev/repos/project-os`

- **TAXONOMY.md** — the `check` type; the six-value `mark:` vocabulary; `automation:` values (`full`/`partial`/`manual`); optional `burden:`. Note explicitly that `level: acceptance` on a TST stays and means something different.
- **STATUSES.md** — a `[[check]]` section: allowed `draft`/`active`/`retired`, terminal `retired`, and the load-bearing sentence: **the verdict is `mark:`, not status** — so the runner-only rule and the review gate, both keyed on status, never engage.
- **QUALITY.md** — one sentence: a `CHK-*` is not a `TST-*` and does not trigger the independent-review gate; the review of a check is the walk.
- **SCHEMAS.md** — the check's field list as [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] fixes it.
- **`tools/scripts/validate-docs.py`** — `ALLOWED_STATUS`, `COLLECTION_TYPE`, `METRIC_PREFIX_TYPE`, `TERMINAL` gain `check`.

Then `sync-project-os.sh` down, and the local `obligations.py` declares `"check"` as owed-nothing — **forced**, because the completeness test asserts every type is declared; the machinery makes the exemption a statement rather than an omission.

## Done when

- [ ] A `CHK-*` note with a verdict and no status change validates in a synced repo, and fires no REVIEW warning, no runner-status complaint, no obligation row.
- [ ] The sync reports zero divergence on the five files afterwards.
