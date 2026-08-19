---
type: "[[test]]"
id: TST-0052
aliases: ["TST-0052", "CHK-0009"]
title: "Actuators"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "The note page"
section: "1.4"
ordinal: 10
covers: ["[[FEAT-0011]]", "[[FEAT-0060]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.4.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0009 @ 4c02731"
---

# Actuators

open a note whose status is a human-owned intake state (a `draft` requirement, a `proposed` ADR). Expect: an `Owed` row of buttons naming that type's own vocabulary; a note with nothing owed shows no row at all. — 2026-08-11, **rendered**: [[ADR-0022]] at `proposed` shows `OWED  [Accept] [Supersede]` beneath the frontmatter strip — the `decision` vocabulary, not a generic pair. [[DES-0009]], now `accepted`, shows **no row**, and `GET /api/notes/actions?id=DES-0009` answers `"actions": []` — the surface and the server agree that nothing is owed. (user:edwin, 2026-08-11)
