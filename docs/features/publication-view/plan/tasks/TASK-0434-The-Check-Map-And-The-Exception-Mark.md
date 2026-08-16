---
type: "[[task]]"
id: TASK-0434
aliases: ["TASK-0434"]
title: "The check map and the exception mark — the render payload says which suite check each checkbox is, and `[!]` joins the vocabulary"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0104]] — the client must address a check without owning a rule about the suite's shape"]
parent: "[[FEAT-0104-The-Suite-Is-The-Surface]]"
effort: M
depends: []
blocks: ["[[TASK-0435-The-Cycling-Mark-And-Its-Paired-Write]]"]
related: ["[[ISS-0141]]", "[[TASK-0430-The-Suite-Is-Addressable]]"]
tests: ["[[TST-0031-The-Exception-Mark-And-Its-Justification]]"]
---

# The check map and the exception mark

## What

Two things the rest of [[FEAT-0104]] stands on.

**The map.** The rendered document addresses a checkbox by DOM position; the suite addresses a check by section-and-ordinal ([[TASK-0430]]). The render payload gains the mapping between them, computed by `acceptance.parse` when the path is the suite. The client owns no rule about the suite's shape — [[TASK-0357]]'s rule, and the reason the obligation vocabulary ships from the server.

**The mark.** `[!]` joins `[ ]`, `[x]` and `[~]`. It is **not blocking** — like `[~]` it is counted and named — but it is reported **separately**, because the two mean different things and conflating them loses the difference [[ISS-0141]] exists to protect.

## Definition of done

- [ ] `acceptance` classifies `[!]` as `excepted`: not settled-by-walking, not reconciled, and not blocking
- [ ] `Item` exposes it, and the tier counts report `excepted` beside `checked` and `reconciled` — never folded into either
- [ ] `gate_payload` reports exceptions and does not count them as blocking
- [ ] The render payload for the suite carries `checks: [{index, number, name, mark}]`, in DOM order
- [ ] The map is **absent** for any other document — this is not a general markdown feature
- [ ] An index the map does not cover is addressable by nothing rather than by a guess
- [ ] `[!]` is refused by `walk_check`'s pass/fail path — an exception is a different act with a different record
