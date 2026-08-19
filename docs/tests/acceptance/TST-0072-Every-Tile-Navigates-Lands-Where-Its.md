---
type: "[[test]]"
id: TST-0072
aliases: ["TST-0072", "CHK-0029"]
title: "Every tile navigates, and lands where its type lives"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "Stat tiles are not dead ends"
covers: ["[[ISS-0063]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#2.2.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0029 @ 4c02731"
---

# Every tile navigates, and lands where its type lives

click all five live tiles. Expect: no tile that looks clickable and does nothing, and no tile that opens a pane its type has left. (Risks pointed at Issues for a commit after risks moved to the constraints view.) — 2026-08-10, **rendered**: five buttons, one inert div, and the constraints view showing `Risks · 6 · open` where the tile now points.
