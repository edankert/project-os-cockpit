---
type: "[[issue]]"
id: ISS-0192
aliases: ["ISS-0192"]
title: "A frozen per-release suite still renders 300 live mark controls, and they write to a file that no longer exists"
status: triage
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
severity: medium
component: ui
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[FEAT-0114-The-Suite-Is-A-View]]", "[[TASK-0464-The-Generated-List-View]]", "[[ISS-0184-Clicking-A-Checkbox-In-The-Acceptance-Suite-Writes-To-A-Different-Row]]"]
---

# A frozen release suite still offers live marks

## What happens

`../your-trainer/docs/tests/ACCEPTANCE_TESTS_v2.1.0.md` is a **frozen record of what v2.1.0 was measured against**. [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] decision 5 says these never migrate, because rewriting them would falsify history.

It still parses as **300 addressable checks**, so `renderer.AcceptanceMarkTreeprocessor` stamps every one of its list items with `data-check` and the client mounts a live mark control on each. Clicking one posts to `/api/notes/mark-check`, which writes to `docs/tests/ACCEPTANCE_TESTS.md`.

That file **no longer exists** in any repo.

## The part that is worse than the symptom

Today the click fails. **Before the migration it succeeded, against the wrong document** — a mark clicked on the frozen v2.1.0 record was written into the living suite, silently, matched by section-and-ordinal in a file that shares none of its 300 check titles with the one being edited. That is [[ISS-0184]]'s defect one level up: not *a different row*, **a different document**.

So the migration did not create this. It converted a silent corruption into a loud failure, which is the better of the two and is still not right: a frozen historical record must not wear a control at all.

## Why it was not fixed with the rest of the phase

The fix is the deletion [[FEAT-0114-The-Suite-Is-A-View]] already asks for — `mountAcceptanceMarks`, the `li[data-check]` path, the treeprocessor that stamps it, and the row-grammar write path (`rewrite_check`, `locate`, `verdict_note`, `strip_verdict`, `check_map`). With the last file-shaped suite migrated, all of it has lost its subject, and removing it fixes this **by construction** rather than by adding a rule about which documents may be clicked.

That is ~5 source files and ~80 tests across four modules — including the guards four rounds of work built ([[ISS-0185]]..[[ISS-0189]]). Deleting those wants a deliberate pass, not the tail end of a migration.

**`acceptance.parse` must survive the cull.** `suite_at` reads file shape at every pre-migration ref, which is all twelve of `../your-trainer`'s tags; the delta depends on it and always will.

## Done when

- [ ] No rendered Markdown document anywhere carries a `data-check` attribute or a mark control.
- [ ] The row-grammar write path is gone; `mark_check` addresses a `CHK-*` and nothing else.
- [ ] `acceptance.parse` still reads the file shape, and the gate delta still computes at every historical `your-trainer` tag.
- [ ] The unreachable-function guard is green — nothing left reading as coverage for a mechanism that no longer exists.
