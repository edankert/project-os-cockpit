---
type: "[[requirement]]"
id: REQ-0060
aliases: ["REQ-0060"]
title: "A check that is not a standing behaviour claim names the issue it verifies"
status: draft
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
source: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
priority: medium
scope: "Acceptance checks authored after the promotion date; 68 pre-existing instances grandfathered by ID."
acceptance: ["A new check with no `covers:` is refused", "The 68 are listed by ID with a promotion date"]
implements: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
verifies: []
related: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[project-os-dev#ADR-0011]]"]
tests: []
---

# A one-time check names its issue

## Statement

An acceptance check that is not a standing claim about behaviour **must** name the `ISS-*` it verifies in `covers:`. Without it the check cannot be distinguished from a behaviour claim, and is treated as one.

## Acceptance Criteria

- [ ] The check warns before the promotion date and errors after
- [ ] The 68 known instances are grandfathered **by ID**, never by a blanket exemption
- [ ] Debt cannot grow: a newly authored check violating this is refused from day one

## Notes

Measured 2026-08-19: 68 of `your-trainer`'s 164 Tier 2 checks name no `ISS-*` anywhere in the note — not in `covers:`, not in the body. Five more name one outside `covers:` and are a scripted repair. Deriving without this rule would silently classify all 68 as behaviour claims and put them back on the list at every overlapping change, which is the behaviour [[ADR-0039]] exists to remove.
