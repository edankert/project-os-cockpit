---
type: "[[task]]"
id: TASK-0445
aliases: ["TASK-0445"]
title: "At ship the cockpit asks for the snapshot and writes what was verified — it does not write files unasked"
status: backlog
owner: user:edwin
created: 2026-08-16
updated: 2026-08-16
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0107]]", "Independent review of PHASE-034, 2026-08-16"]
parent: "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]"
effort: M
depends: []
blocks: []
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
tests: []
---

# At ship the cockpit asks for the snapshot and writes what was verified — it does not write files unasked

## Why

The practice exists — two snapshots, one `tests_verified` naming them — and it is entirely manual, so it happened for 2 of 12 releases. Prompting is the difference between a convention and a habit.

## Definition of done

- [ ] Shipping asks which suite snapshot this release verified
- [ ] `tests_verified:` is written from the answer, alongside any `TST-*` the release names
- [ ] **Nothing is written unasked** — no auto-snapshot, no auto-copy
- [ ] Declining leaves `tests_verified` empty and the page says *not recorded*, which is honest
- [ ] Loopback-only, enumerated by the existing guard
