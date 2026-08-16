---
type: "[[task]]"
id: TASK-0443
aliases: ["TASK-0443"]
title: "The navigator lists releases and the mode opens a page — the two things every other view already does"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0107]]", "Independent review of PHASE-034, 2026-08-16"]
parent: "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]"
effort: M
depends: []
blocks: []
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
tests: []
---

# The navigator lists releases and the mode opens a page — the two things every other view already does

## Why

Publication is the only badge-bearing view with no landing: absent from `VIEW_LANDING_RELS` and `MODES_WITH_VIRTUAL_LANDING`, so selecting it leaves the centre pane on whatever you were reading and opening a workspace in it lands on README.md. The ninth mode was added after FEAT-0092 fixed exactly this and did not join the fix.

## Definition of done

- [x] The navigator lists releases, newest first, each with its content nested
- [x] Selecting Publication opens `~release/next`
- [x] A release row opens `~release/<id>`, which today is reachable only by typing
- [x] The next release shows its accumulated contents and the LIVING suite's outstanding count
- [x] Opening the suite from the page lands in `ACCEPTANCE_TESTS.md`, where ticking already works
- [x] Commit/push/deploy are not groups here
