---
type: "[[task]]"
id: TASK-0309
aliases: ["TASK-0309"]
title: "design: on features, and the DESIGN-GATE warning"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0070-Design-Gating-And-Scaffolding]]"]
parent: "[[FEAT-0070-Design-Gating-And-Scaffolding]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# design: on features, and the DESIGN-GATE warning

## Definition of Done

- Optional `design:` frontmatter on features; local validator warning while the named design is unaccepted and the feature leaves the pending band.
- Warning first per ADR-0011's path; the escalation decision is deferred until lived with.

## Done — 2026-08-11

`design:` on the feature template and in `TAXONOMY.md`; `DESIGN-GATE` in the validator.

**A warning, per [[project-os-dev#ADR-0011]]'s path**, and for the same reason `ACCEPT-STALE` is: the judgment being gated — *is this design right?* — cannot be automated, and a blocking gate on it gets cleared to unblock the build rather than because somebody looked. Escalation is deferred until the convention has been lived with.

**It only applies past the pending band.** Naming a design you have not accepted yet is the normal state of planning; warning about it would fire on every feature the moment it was written.

**The satisfied set was narrowed after it fired five false positives immediately.** The first cut required `status == "accepted"` and warned on five real features whose designs were `implemented` — which is the status *after* accepted (`proposed → accepted → implemented`). `superseded` joins them: it means a later design replaced one that had been accepted. Zero warnings on this corpus now.

That mistake is worth the record rather than a quiet fix, because it is exactly the failure mode this warning is shaped to avoid: **a nag that fires wrongly teaches people to ignore it**, and I wrote that sentence about `ACCEPT-STALE` an hour before making the mistake here.

Proven three ways: fires on a `done` feature naming a `draft` design, silent when the same feature names an `accepted` one, and silent across the whole live corpus.
