---
type: "[[requirement]]"
id: REQ-0038
aliases: ["REQ-0038"]
title: "Nothing is lost in the merge — row count, mark and coverage parity asserted per repo before the old shape is deleted"
status: approved
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: migration
implements: "[[FEAT-0119-The-Merge-Migration]]"
acceptance:
  - "[ ] Per repo, note count before equals note count after: project-os-cockpit 34, your-sudoku 56, your-trainer 579."
  - "[ ] Per repo, the distribution of `mark:` values is identical before and after — not just the settled total."
  - "[ ] Per repo, the set of `covers:` targets is identical before and after, and every target still resolves."
  - "[ ] The release gate reports the same blocking count before and after in every repo. Baseline: your-trainer 60, your-sudoku 56, project-os-cockpit 0."
  - "[ ] Parity is asserted **through the reader** — the loaded suite payload — before any `CHK-*` file is removed, which is the shape TASK-0461 used and ISS-0175 is the reason for."
covers: []
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
---

# Nothing is lost in the merge

The previous migration asserted parity per repo (34 / 56 / 579) rather than assuming it, and that discipline is why it is trusted. This is the same corpus moving a second time in two weeks; the bar does not drop because the move is smaller.

**Assert through the reader, not the files.** A file-count match proves the script wrote as many notes as it read. It does not prove the suite still loads, still tiers, still marks and still gates — which is what a reader depends on and what [[ISS-0175]] was filed about.

## Approved 2026-08-18

Approved on the pilot's evidence rather than ahead of it: 34 notes migrated with the fingerprint identical on all six original dimensions and bodies byte-identical. It stays `approved` rather than `implemented` because two of the three suites — `your-sudoku` (56) and `your-trainer` (579) — have not run the migration, and this requirement is a claim about all of them.
