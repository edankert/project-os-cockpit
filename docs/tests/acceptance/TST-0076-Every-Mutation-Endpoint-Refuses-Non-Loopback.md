---
type: "[[test]]"
id: TST-0076
aliases: ["TST-0076", "CHK-0033"]
title: "Every mutation endpoint refuses a non-loopback caller"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 2
area: "Writes are loopback-only"
section: "2.6"
ordinal: 10
covers: ["[[ISS-0129]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#2.6.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0033 @ 4c02731"
---

# Every mutation endpoint refuses a non-loopback caller

enumerate the POST dispatch table and confirm each handler consults the guard — including `/api/notes/check-toggle`, which wrote note body text for any peer that could reach the `0.0.0.0` render port. — 2026-08-10: driven over the LAN interface, **10 of 10 returned 403**, `check-toggle` among them. See §1.1 for the run.
