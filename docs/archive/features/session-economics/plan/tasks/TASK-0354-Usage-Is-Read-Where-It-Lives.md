---
type: "[[task]]"
id: TASK-0354
aliases: ["TASK-0354"]
title: "A turn's usage is read where it actually lives, and one decision keeps one implementation"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: M
due: ""
depends: []
blocks: []
related: ["[[ISS-0114-The-Zero-Usage-Filter-Discards-Real-Turns]]", "[[ISS-0115-ISS-0110s-Repro-Still-Reproduces]]"]
tests: []
---

# Usage is read where it lives

Fixes [[ISS-0114-The-Zero-Usage-Filter-Discards-Real-Turns]] and the duplicated-decision half of [[ISS-0115-ISS-0110s-Repro-Still-Reproduces]].

## Definition of Done
- [x] When an entry's top-level `usage` totals are all zero but `usage.iterations[]` carries real accounting, the turn's figures are read from there — the entry is a real turn and it is neither dropped nor counted as zero.
- [x] The placeholder test becomes "no tokens **anywhere** in this entry", so it still rejects API-error entries while keeping turns whose totals merely live one level down.
- [x] The docstring's premise is corrected. It asserted that an entry consuming no tokens did no work; the corpus it was derived from contains five counter-examples, one of 1,000,255 tokens.
- [x] `tickTemperatures` uses `railKey` rather than restating its rule inline, so the cold decision has one implementation and it is the tested one.
- [x] Tests: an iterations-only entry is kept with its real figures and can be `prev`; an all-zero-everywhere entry is still rejected; a `<synthetic>` entry with iterations is still rejected. Each verified by mutation.

## Notes
The ISS-0106 fix widened the rejection to be robust against a future placeholder under another name, and caught real turns in the net. The signal it should have keyed on was never "zero tokens at the top level" but "zero tokens anywhere" — a distinction the corpus could have shown at the time and was not asked.
