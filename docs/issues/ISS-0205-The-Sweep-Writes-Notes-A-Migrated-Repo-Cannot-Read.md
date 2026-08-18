---
type: "[[issue]]"
id: ISS-0205
aliases: ["ISS-0205"]
title: "The close-out sweep writes `type: [[check]]` notes with `CHK-*` ids, which a migrated repo's reader cannot see — the sweep is silently writing invisible checks right now"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: high
component: cockpit-server
phase: "[[PHASE-036-One-Human-Walk]]"
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[FEAT-0115-The-Sweep-Is-Continuous]]", "[[TESTING-MODEL]]"]
---

# The sweep writes notes nothing can read

Found by independent review, 2026-08-18, and it is live.

`sweep._write_new_check` still authors the retired shape — `type: "[[check]]"` with a `CHK-####` id. `acceptance.load` reads:

```python
records = [tests at level: acceptance] or list(index.notes_by_type("check"))
```

**In a migrated repo the `or` never evaluates.** The left side is non-empty (34 here, 56 in `your-sudoku`, 579 in `your-trainer`), so a freshly swept `CHK-*` note is written to disk, counted by nothing, rendered by nothing and gated by nothing.

Reproduced on a two-note corpus — one `TST` at `level: acceptance` plus one `CHK` — the reader returns **one** item and reports **0 blocking**.

## Why no test catches it

`tests/test_acceptance_sweep.py` builds its whole fixture from `type: "[[check]]"` notes, so the reader's left branch is empty there and the `or` falls through to exactly the shape the sweep writes. **The guard and the defect share an assumption**, which is the same failure that let `_require_check` refuse the entire corpus after the merge: guards die with their fixtures.

## Why it matters now rather than later

The acceptance-sweep obligation is **live**: 1 feature in this repo and 4 in `your-trainer` are being asked to sweep. The first person to answer that ask writes checks that vanish — and the sweep's whole purpose is that invalidation happens where work lands.

## Done when

- [ ] `_write_new_check` writes a `[[test]]` at `level: acceptance` with a `TST-*` id, and `_TIER_LABELS`-consistent fields.
- [ ] The sweep's tests run against a **migrated** corpus. The existing fixture must move, not be supplemented — leaving it in place preserves the branch that hid this.
- [ ] A guard that a swept check is readable by the repo it was written into, asserted through `acceptance.load`.
## Fixed 2026-08-18

`_write_new_check` writes `[[test]]` at `level: acceptance` with a `TST-*` id allocated from **both** populations, since they share the space.

**The third done-when was the one that mattered and was initially unmet.** Moving the fixture to the merged type was not enough: reverting the writer to `type: "[[check]]"` left all 22 sweep tests green, because they assert the note's fields rather than whether the suite can load it. `test_the_sweep_writes_a_note_the_reader_can_see` reads the sweep's own output back through `acceptance.load` on a migrated corpus, and is the only thing that fails on that mutation. Found by independent review.
