---
type: "[[task]]"
id: TASK-0440
aliases: ["TASK-0440"]
title: "The release payload — what is in a release, and what stands between it and shipping, in one answer"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0106]]"]
parent: "[[FEAT-0106-The-Release-Page]]"
effort: M
depends: []
blocks: ["[[TASK-0441-The-Release-Page-And-An-Input-That-Works]]"]
related: ["[[FEAT-0072]]"]
tests: ["[[TST-0033-The-Release-Page]]"]
---

# The release payload

## Definition of done

- [ ] `GET /api/cockpit/release?id=next|REL-####` answers with the release's state, its contents and its gate
- [ ] Contents come from `unreleased_payload` for `next`, and from `features:` for a named one — the derived set for what has not shipped, the frozen set for what has
- [ ] The gate section is `acceptance.gate_payload`, not a second read
- [ ] `next` answers even when no release note exists — that is the ordinary case
- [ ] A repo with no suite says so rather than reporting nothing blocking
