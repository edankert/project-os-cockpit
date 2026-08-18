---
type: "[[test]]"
id: TST-0057
aliases: ["TST-0057", "CHK-0014"]
title: "A design renders its artifact"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Design and the constraints view"
section: "1.6"
ordinal: 20
mark: done
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0042]]", "[[FEAT-0043]]", "[[FEAT-0044]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.6.2 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0014 @ 4c02731"
---

# A design renders its artifact

open a `DES-*` with a committed artifact. Expect: it renders in the frame, in this project's own tokens, in both light and dark. — 2026-08-11, **rendered**, [[DES-0010]]: the artifact renders in the frame with its Revisions rail (`Working copy · current`, `2026-08-09 · 5ed3a68`) and `Annotate selection` beside it, and its own light/dark control round-trips both ways. **Finding, filed as [[ISS-0136]]:** five of the nine committed artifacts hard-code a dark palette and stay dark under a light app — DES-0009 among them. Ticked on DES-0010 rather than waived, because the check says *a* design and one demonstrably satisfies it; the other five are a defect in the artifacts, not in the frame. **DES-0009's is deliberately not being fixed** — its `design_revision: 31eac79` is what Edwin's acceptance is pinned to, and editing the artifact would move the sha out from under the verdict. (user:edwin, 2026-08-11)
