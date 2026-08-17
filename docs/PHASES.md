---
type: "[[reference]]"
id: PHASES
title: "Phase registry"
owner: user:edwin
created: 2026-05-07
updated: 2026-08-10
tags: [phases, registry]
---

# Phase Registry

This document is the **semantic source of truth** for development phases. It maps phase IDs to specific milestones, and is read by the cockpit's phase surfaces and by anyone orienting in the repo.

*(Corrected 2026-08-10, [[ISS-0125]]: this line used to say the registry was "consumed by Bases / dashboards". `DASHBOARD.md` was removed the same day — an Obsidian artifact whose six `.base` embeds pointed at files that no longer exist — and the cockpit reads the `PHASE-*` notes directly, never this document.)*

## How Phases Work

- **Property**: `phase` (string wikilink in frontmatter, e.g. `"[[PHASE-001-MVP]]"`)
- **Purpose**: Groups related work into delivery milestones.

## Phase Definitions

| Phase | Name | Description | Key Deliverables | Status |
|---|---|---|---|---|
| [PHASE-001](phases/PHASE-001-MVP.md) | MVP | Renderer + live reload — the smallest useful tool. | FEAT-0001, FEAT-0002 | done |
| [PHASE-002](phases/PHASE-002-Project-OS-Adapter.md) | Project-os adapter | ID resolution polish, auto-index pages, backlinks panel, bases-driven cockpit layout. | FEAT-0004, FEAT-0006 | active |
| [PHASE-003](phases/PHASE-003-Downstream-Pilot.md) | Downstream pilot | Would have proven cross-repo invocation with one shim. **Never built** — workspace discovery (PHASE-005) replaced the need, and the shell now serves all 12 fleet repos (ISS-0078). | FEAT-0005 | superseded → PHASE-005 |
| [PHASE-004](phases/PHASE-004-Embedded-Terminal.md) | Embedded terminal | Opt-in `ttyd`-iframe terminal panel, loopback-only. Pulled out of PHASE-001. | FEAT-0003 | planned |
| [PHASE-005](phases/PHASE-005-Desktop-Shell.md) | Desktop shell (Electron + Python sidecar) | System-wide Electron app that wraps the existing cockpit as a sidecar. Multi-project. Additive to modes 1 + 2. | FEAT-0007 | active |
| [PHASE-006](phases/PHASE-006-Native-Cockpit-UI.md) | Native cockpit UI (TypeScript rewrite) | Replace the iframe-mounted cockpit with native TypeScript panes. Python becomes a pure data + Markdown-render API. Mode 1 (browser) preserved. | FEAT-0008..FEAT-0013 | done |
| [PHASE-007](phases/PHASE-007-Agent-Instrumentation.md) | Agent instrumentation (hooks-aware terminal) | Auto-instrument Claude Code / Codex sessions in the embedded terminal via lifecycle hooks; activity strip, needs-input inbox, task dispatch, session insight. **Reopened and re-closed 2026-08-06** for session economics — what the context weighs and what the next turn costs. | FEAT-0019..FEAT-0022, FEAT-0081, ISS-0104..ISS-0119 | done |
| [PHASE-008](phases/PHASE-008-State-And-Review-Surfaces.md) | State & review surfaces | State-first overview rework (project + phase dashboards per the 2026-07-26 design dossier) and the ~review desk where agent proposals, questions, and manual test runs meet a human. | FEAT-0040, FEAT-0041 | done |
| [PHASE-009](phases/PHASE-009-Design-Surfaces.md) | Design surfaces | Design artifacts become project records: rendered live at the app's own viewport, versioned with per-revision reasoning, annotated and reviewed where the notes live. | FEAT-0042, FEAT-0043 | done |
| [PHASE-010](phases/PHASE-010-Surface-Ownership.md) | Surface ownership | Every note type gets one purpose surface; Library reduces to Pinned + the Docs tree. Plans nest under features, risks join Issues, changes join the overview, tests and reviewed items join the review desk. | FEAT-0046..FEAT-0050 | done |
| [PHASE-011](phases/PHASE-011-Unproven-Claims.md) | Unproven claims become visible | Where the system already knows a claim is unproven — a waiver, a stale manual verification, a drifted status guard, a hand-maintained coverage register — the surfaces must say so. | FEAT-0018 | done |
| [PHASE-012](phases/PHASE-012-Attention-In-The-Strip.md) | Attention in the strip | Give the phase squares the states they lack (DES-0004) so the Waiting-on-you list has no job, plus PHASE-010's reachability residue. Gated on DES-0004 having a verdict. | ISS-0067, ISS-0068 | done |
| [PHASE-013](phases/PHASE-013-Fleet-Surfaces.md) | Fleet surfaces | Finish the cross-repo work: roll the design-system convention across the fleet, and surface per-workspace validator health. | FEAT-0028, FEAT-0044 | planned |
| [PHASE-015](phases/PHASE-015-Phase-Hygiene.md) | Record hygiene | An item's phase becomes a record of what delivered it rather than a plan-time answer nobody revisits. Sixteen delivered notes re-homed out of the sentinel; the rule itself proposed upstream. | ISS-0074 | done |
| [PHASE-016](phases/PHASE-016-The-Overview-Answers-Questions.md) | The overview answers questions | Every number on the overview leads somewhere and everything on it says what it is: validator counts become session work, the history band becomes documents, that history becomes reachable, and the phase rows name themselves. **Absorbed PHASE-017/018/019** (ISS-0077). | FEAT-0051, FEAT-0052, FEAT-0053 | done |
| [PHASE-017](phases/PHASE-017-History-As-Document-Events.md) | History as document events | One History surface replacing Activity + Changes + Commits: rows are note status transitions, commits are dividers marking what is saved. | FEAT-0052 | superseded → PHASE-016 |
| [PHASE-018](phases/PHASE-018-History-You-Can-Reach-And-Traverse.md) | History you can reach and traverse | A contribution grid whose days are destinations, and a History button in the rail. GitHub's shape, with its constants replaced — relative intensity, absent-is-not-empty, no year controls without a second year. | FEAT-0053 | superseded → PHASE-016 |
| [PHASE-019](phases/PHASE-019-Overview-Legibility.md) | Overview legibility | Small "I can't tell what I'm looking at" fixes on the project overview. A standing home, so each one need not invent a phase. | ISS-0076 | superseded → PHASE-016 |
| [PHASE-020](phases/PHASE-020-Clipboard-That-Works.md) | A clipboard that works everywhere | One clipboard path through the main process, a right-click menu that acts on the link rather than the auto-selected word, and no copy that fails in silence. | FEAT-0054 | done |
| [PHASE-021](phases/PHASE-021-Git-Is-Not-The-Users-Job.md) | Git is not the user's job | Close-out commits its own work, scoped; being behind a remote is visible where repo health already is; pushing is deliberate and refuses deploy remotes. | FEAT-0055 | done |
| [PHASE-022](phases/PHASE-022-Completed-Work-Gets-Quieter.md) | Completed work gets quieter | Ordering over hiding, the record grammar in both panes, one shape per navigator, cards that look like cards. Twelve closings; the registry row was forgotten until PHASE-023's planning — which is itself a datum about manual registries. | FEAT-0056..FEAT-0058, ISS-0082..ISS-0093 | done |
| [PHASE-023](phases/PHASE-023-Levers-For-The-Human.md) | Levers for the human | The cockpit writes the record it renders: human-owned transitions as actions, live criteria ticks, quick capture into triage, the desk's flows closed. | FEAT-0059..FEAT-0062, DES-0005 | done |
| [PHASE-024](phases/PHASE-024-Acceptance-Witnessed.md) | Acceptance witnessed | The acceptance runner, the opt-in gate distinct from independent review, the debt surface, visual evidence. | FEAT-0063..FEAT-0066, DES-0006 | done |
| [PHASE-025](phases/PHASE-025-Design-Before-Code.md) | Design before code | Variants rendered and chosen, the measure view, annotate-to-request, the design gate with its upstream proposal. | FEAT-0067..FEAT-0070, DES-0007 | done |
| [PHASE-026](phases/PHASE-026-The-Returning-Human.md) | The returning human | The since-you-looked digest, the release surface, one voice across the panes, mode 1 decided by ADR. | FEAT-0071..FEAT-0073, DES-0008 | done |
| [PHASE-027](phases/PHASE-027-The-Standing-Worker.md) | The standing worker | ADR-0009 made operational: the driver with lease and stop conditions, the delegation policy the actuators consult, escalation defaults, the intent charter for delegated acceptance. Opt-in per repo by approved DELEGATION.md; default everywhere is no worker. | FEAT-0074..FEAT-0078, DES-0009 | done |
| [PHASE-028](phases/PHASE-028-Borrowed-Capability.md) | Borrowed capability | **Standing.** Adopt what adjacent agent harnesses have proven rather than inventing it, and keep looking. First round: t3.codes, 2026-08-05; Omnigent.ai queued 2026-08-11 ([[TASK-0386]]). Declines are recorded as carefully as adoptions. | FEAT-0079, FEAT-0080 | active |
| [PHASE-029](phases/PHASE-029-One-Tool-Two-Front-Doors.md) | One tool, two front doors | The browser cockpit and the desktop shell answer the same questions, and differ only where a difference was decided. Gated on [[ADR-0010]], still `proposed`. | FEAT-0083, FEAT-0084 | planned |
| [PHASE-030](phases/PHASE-030-Obligations-Go-Home.md) | Obligations go home | Every judgment the record owes surfaces where its subject lives, the count is always on screen, and Tests becomes a view. The desk retires. **Widened 2026-08-13 ([[ADR-0027]]): the registry counts what needs a *person*, not only what the record owes — publication is its first new subject.** | FEAT-0086..FEAT-0091, FEAT-0100 | done |
| [PHASE-031](phases/PHASE-031-The-Supervised-Week.md) | The supervised week | The standing worker runs under daily human supervision for a week, and [[RISK-0006]] closes on what the ledger shows rather than on confidence. Re-homed from PHASE-027, not descoped. | RISK-0006 | planned |
| [PHASE-032](phases/PHASE-032-The-Reasoning-Is-Recorded.md) | The reasoning is recorded | A judgment a person makes on the record carries the reasoning behind it, in the note where the decision lives, in a form both the cockpit and Obsidian render. Reopened and re-closed the same day for the option-selection half. *(Row added 2026-08-13 — the phase closed without one.)* | FEAT-0095..FEAT-0097, ISS-0152 | done |
| [PHASE-033](phases/PHASE-033-The-Workspace-Is-Not-Always-Local.md) | The workspace is not always local | A project-os repo on another machine is a workspace like any other — record, terminals and fleet surfaces — with the authorisation that made a local workspace safe rebuilt rather than assumed. Opens on a decision ([[ADR-0026]]), not on build work. | FEAT-0099, REQ-0035, REQ-0036, RISK-0007 | planned |
| [PHASE-034](phases/PHASE-034-Three-Phases-And-Publication-Is-The-Third.md) | Three phases, and publication is the third | Work has a design phase, an implementation phase and a publication phase, and the tool has only ever had two. Publication becomes a view over the whole ladder — commit, push, deploy, versioned release — and every obligation routes to the phase that owns its subject, asking only while that subject is in flight. Opens on a decision ([[ADR-0028]]), not on build work. | FEAT-0101, FEAT-0102, FEAT-0108, FEAT-0109, FEAT-0110, FEAT-0111, FEAT-0104, ISS-0172, ISS-0173, ISS-0177, ISS-0183, ISS-0184, ISS-0185 | done |
| [PHASE-999](phases/PHASE-999-Future.md) | Future / Unphased | Sentinel parking-lot for items without a concrete delivery phase yet. Re-phase out when planning crystallises. **Not a second sentinel:** `PHASE-999-Unscheduled` was a dangling link on 13 notes until 2026-07-30 and never existed. | FEAT-0029, TASK-0045, TASK-0065 | planned |

## Active phase

None — **[[PHASE-034]]** closed 2026-08-16 on its fourth close, after building the functionality review's four features (FEAT-0108..0111). It had opened and closed the same day after three closes and an independent review that returned `changes-requested` on the phase and five of six features; those verdicts stand.

*(This section read "None" all through PHASE-030's life and reopen, because `sync-snapshot.py` propagates status to `SNAPSHOT.yaml` and not to this hand-maintained registry. Kept current by hand until something reads it.)*

Historic — PHASE-011 through PHASE-016 all closed on 2026-07-30, and PHASE-017/018/019 were merged into PHASE-016 the same day ([[ISS-0077]]: nine phases opened in one day against nine in the preceding twelve weeks). PHASE-013 (fleet surfaces) was independently reviewed and returned `changes-requested`; all nine findings were addressed before close-out. PHASE-014 and PHASE-015 came out of Edwin's question about delivered-but-unplanned work: 014 is a **retrospective** record of the project inbox, and 015 is the correction that required writing it. See `SNAPSHOT.yaml` `focus`.

**Phase numbers are allocation order, not chronology.** PHASE-014 documents work that shipped between PHASE-009 and PHASE-010; its note says so rather than leaving the reader to infer it from the number.

## Operational rules for LLMs

1. **Verify phase alignment**: check `phase` in task/feature frontmatter before starting work.
2. **Consult this registry**: understand the boundaries of the current phase.
3. **Prevent phase bleeding**: don't introduce implementations from future phases prematurely.
4. **Flag scope concerns**: if a task requires future-phase dependencies, document it and discuss before proceeding.
