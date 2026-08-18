---
type: "[[requirement]]"
id: REQ-0038
aliases: ["REQ-0038"]
title: "Nothing is lost in the merge — row count, mark and coverage parity asserted per repo before the old shape is deleted"
status: implemented
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: migration
implements: "[[FEAT-0119-The-Merge-Migration]]"
acceptance:
  - "[x] Note count identical per repo: 34 / 56 / 579."
  - "[x] `mark:` distribution identical per repo, not just the settled total."
  - "[x] `covers:` target set identical per repo."
  - "[x] Blocking count identical per repo: 0 / 56 / 60."
  - "[x] Asserted through the reader — `acceptance.load` — and the script exits non-zero rather than reporting a mismatch."
  - "[x] `your-trainer`'s twelve-tag delta is unchanged — the one property outside the per-repo fingerprint, and the one this migration could have broken silently."
covers: []
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
---

# Nothing is lost in the merge

The previous migration asserted parity per repo (34 / 56 / 579) rather than assuming it, and that discipline is why it is trusted. This is the same corpus moving a second time in two weeks; the bar does not drop because the move is smaller.

**Assert through the reader, not the files.** A file-count match proves the script wrote as many notes as it read. It does not prove the suite still loads, still tiers, still marks and still gates — which is what a reader depends on and what [[ISS-0175]] was filed about.

## Approved 2026-08-18

Approved on the pilot's evidence rather than ahead of it: 34 notes migrated with the fingerprint identical on all six original dimensions and bodies byte-identical. It stays `approved` rather than `implemented` because two of the three suites — `your-sudoku` (56) and `your-trainer` (579) — have not run the migration, and this requirement is a claim about all of them.

## Acceptance criteria

- [x] **Note count identical per repo** — `project-os-cockpit` 34, `your-sudoku` 56, `your-trainer` 579.
- [x] **`mark:` distribution identical per repo** — `{x: 33, /: 1}`, `{unwalked: 56}`, `{x: 513, unwalked: 66}`.
- [x] **`covers:` target set identical per repo**, and every target still resolves.
- [x] **Blocking count identical per repo** — 0 / 56 / 60.
- [x] **Asserted through the reader before any file was removed.** The fingerprint compares thirteen fields, not six — widened after review found it guarding the gate fields only — and the script refuses rather than reports.
- [x] **And the one thing outside the fingerprint**: `your-trainer`'s twelve-tag delta, unchanged at 84, 87, 87, 111, 212, 268, 361, 536, 560, 560, 560, 560.

## Advanced 2026-08-18

Satisfied across all three suites rather than on the pilot alone.
