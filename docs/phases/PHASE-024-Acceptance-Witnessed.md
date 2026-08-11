---
type: "[[phase]]"
id: PHASE-024
aliases: ["PHASE-024"]
title: "Acceptance witnessed — the human accepts work through the cockpit, and the record shows who accepted what, with what evidence"
status: done
order: 24
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
goal: "Make human acceptance a first-class, recorded act: a guided runner over acceptance criteria, an explicit acceptance gate distinct from independent review, a surface for acceptance debt, and visual evidence a non-code reader can trust."
features:
  - "[[FEAT-0063-The-Acceptance-Runner]]"
  - "[[FEAT-0064-The-Acceptance-Gate]]"
  - "[[FEAT-0065-Acceptance-Debt-Surface]]"
  - "[[FEAT-0066-Visual-Evidence]]"
requirements:
  - "[[REQ-0028-Evidence-Names-Its-Witness]]"
issues: []
depends: ["[[PHASE-023-Levers-For-The-Human]]"]
related: ["[[DES-0006-The-Acceptance-Desk]]"]
tags: [acceptance, testing, review]
---

# Acceptance witnessed

## Where this came from

The 2026-08-03 review's sharpest finding: **the acceptance contract already exists on paper and has no surface.** `docs/__templates__/acceptance-tests.md` defines a three-tier suite, re-run marking, and a release gate — rendered as just another note. Meanwhile independent review (ADR-0013) is satisfiable by an agent with clean context, and every terminal status in STATUSES.md is agent-stamped: **nothing anywhere requires the human to have accepted the experience.**

PHASE-022 measured the cost: agent review passed twice while Edwin found five further rounds of problems by using the app. His acceptance testing happened — twelve times — with no record beyond chat.

## The distinction this phase encodes

Independent review answers *"is the work sound?"* — clean context, adversarial, satisfiable by an agent. Acceptance answers *"is this what I asked for?"* — and only the asker can say. Two gates, not one relabelled; the second is optional per feature, because most features do not need it and a mandatory gate would become a rubber stamp within a week.

## Scope

[[FEAT-0063]] — the runner: criteria walked one at a time, pass ticks with the human as evidence, fail files a pre-linked issue (via PHASE-023's capture machinery — the dependency is real). [[FEAT-0064]] — the gate and its desk queue. [[FEAT-0065]] — what has no test, what is unticked, what was ticked without evidence. [[FEAT-0066]] — screenshots as evidence, captured by the shell, stored in the record.

Design: [[DES-0006]] — the acceptance desk.

## Out of Scope

- **Replacing independent review.** ADR-0013 stands untouched; this adds the second question, not a substitute for the first.
- **Mandatory acceptance.** Opt-in per feature. The gate that is always required is the gate nobody performs honestly.
- **Automated UI testing.** The runner structures *human* judgment; it does not simulate it.

## Exit Criteria

- [x] A feature can be accepted end-to-end in the cockpit and its criteria show who accepted them, when — evidence: walked against a copy of this corpus — four criteria on [[REQ-0028]], three passed and one reconciled, each stamped `(user:edwin, 2026-08-11)` by [[TASK-0288]]'s runner, and the validator reports 0 REQ-BOXES errors for that requirement afterwards (user:edwin, 2026-08-11)
- [x] A failed criterion becomes a linked issue in one step — evidence: `Fail…` posts to `/api/notes/create` with the criterion as the title and `related: [[FEAT-…]], [[REQ-…]]`, and **the run continues** — a fail is a datum, not an abort ([[TASK-0288]]) (user:edwin, 2026-08-11)
- [x] The overview answers "what awaits my acceptance" and "what has no verification at all" — evidence: the first re-homed to the feature's own row per [[ADR-0020]] (marked owed by the registry, `▶ Accept…` opens the run — [[TASK-0292]]); the second is `Acceptance debt · 28` on the record column, **24 unverified · 4 unresolved · 0 evidence-free** ([[TASK-0295]]) (user:edwin, 2026-08-11)
- [x] Evidence can be a picture, stored in the repo, rendered in the note — evidence: `POST /api/notes/attach` files a PNG at `docs/attachments/<NOTE-ID>/<date>-<n>.png` and returns the Markdown that cites it; `/docs/<path>` and `ImageSourceTreeprocessor` already render it, so no new read path was needed ([[TASK-0297]]) (user:edwin, 2026-08-11)
- [x] An acceptance run leaves a log in the feature note in the same grammar test runs use — evidence: `### 2026-08-11 — user:edwin — 3 passed · 0 failed · 1 skipped` under `## Acceptance runs`, written through `_append_run_log`'s own shape ([[TASK-0289]]) (user:edwin, 2026-08-11)
