---
type: "[[test]]"
id: TST-0073
aliases: ["TST-0073"]
title: "`implemented` reads as done everywhere"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "One status vocabulary"
covers: ["[[ISS-0023]]", "[[ISS-0024]]"]
related: []
level: acceptance
---

# `implemented` reads as done everywhere

expect an `implemented` requirement to render in the done band, rank as completed in the fold, and count as done in the progress boxes — on both front doors. — 2026-08-11, **rendered on both**. *Blocked earlier the same day and unblocked by fixing what blocked it ([[ISS-0138]]).* **Mode 3:** REQ-0001/0002/0003/0006/0007/0012 render with `implemented` chips under FEAT-0001 inside PHASE-001's completed band, the phase counted `✓ 2`, REQS tile `32 /33`. **Mode 1**, the same six on the same note: nested under `FEAT-0001` inside `PHASE-001 MVP · 2 · done`, itself inside `COMPLETED · 23 · 86 FEATURES` — done band, ranked completed, counted done. Both doors agree, which is what the check is for. (user:edwin, 2026-08-11)
