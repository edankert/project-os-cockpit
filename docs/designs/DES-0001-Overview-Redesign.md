---
type: "[[design]]"
id: DES-0001
aliases: ["DES-0001"]
title: "Overview redesign — the design PHASE-008 was built from"
status: implemented
owner: user:edwin
created: 2026-07-26
updated: 2026-07-27
implements: ["[[FEAT-0040-Overview-Rework]]", "[[FEAT-0041-Review-Desk]]", "[[PHASE-008-State-And-Review-Surfaces]]"]
supersedes: ""
superseded_by: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
related: ["[[FEAT-0040-Overview-Rework]]", "[[FEAT-0041-Review-Desk]]", "[[PHASE-008-State-And-Review-Surfaces]]", "[[ADR-0006-Retire-Delivered-Band]]"]
asset: "overview-redesign-dossier.html"
---

# Overview redesign dossier

## Purpose

The design input that produced PHASE-008. It is committed here rather than left in a chat transcript or a hosted artifact because the reasoning behind a surface outlives the conversation that produced it — and because a link to somebody's chat history is not a project record. This is the reference half of the queue-vs-record split that shapes FEAT-0041: the review queue empties, the record grows.

Open `overview-redesign-dossier.html` beside this note for the rendered version (five annotated plates, both themes, a states audit, and a data-source map).

## Contents

Five plates, each a full three-pane mockup built from the app's own design tokens:

- **A / B — the current screens as built**, with numbered critique pins: the hero spending ~170 px on six numbers while `hero.requirements` went computed-but-unrendered; five finished phases shouting as loudly as the live one; donuts restating the hero without labels; the feed below the fold; a right pane with no job.
- **C — the proposed project overview**: quiet-first focus band, mix-bar stat tiles, phase accordion with a Completed band, Waiting-on-you, full-width activity and commits, record column.
- **D — the proposed phase detail**: header fraction + gates chip, health band, feature rows that name the next action, exit criteria with evidence chips, a Remaining list.
- **E — the review desk (`~review`)**: proposal-set review, questions, and the manual test runner, with the durable homes (verification panel, design references) exhibited separately.

Two findings did most of the work and are worth re-reading before changing these surfaces:

- **The states audit.** Every status the design leans on was checked against the corpus. Work here is *bursty* — `doing` and `triage` clear within a session — so the overview is mostly viewed quiet, and the durable states are the human-shaped ones (open issues, review stalls, never-executed tests, parked work, open risks, phases finished but not closed). The screens are designed quiet-first for that reason.
- **The Delivered lesson.** An earlier revision of this dossier proposed adopting the `delivered` status band; [[ADR-0006-Retire-Delivered-Band]] retired that band the next day, having measured zero writes of its members fleet-wide. The "Completed" grouping that shipped is a *view* over done phases, never a status. Surfaces must follow what the corpus writes, not what a design wishes it wrote.

## Maintenance

Update the HTML in place when the surfaces change materially, and keep the plate numbering stable so the annotations in [[FEAT-0040-Overview-Rework]] and [[FEAT-0041-Review-Desk]] keep resolving. The `design:` frontmatter field on those notes is what puts this dossier in their attachment strip and in the record column's Library card; adding the same field to a new feature is all it takes to surface its own input.

## Migration note (2026-07-27)

Filed as `REF-0001` under `docs/references/design/` because no design note type existed. It does now (project-os-dev FEAT-0019), so this became `DES-0001` under `docs/designs/`.

Status is **`implemented`**, not `accepted`. PHASE-008 shipped from this dossier — FEAT-0040 and FEAT-0041 are both `done` — so recording it as merely accepted would understate what happened, and `superseded` would be wrong because nothing has replaced it. `implemented` is terminal-but-alive on purpose: the design still describes the built surface, which is what makes design/implementation parity checkable at all (project-os-cockpit TASK-0219).

What this note still does not carry, and [[FEAT-0042]] exists to fix: the artifact went through six revisions in one session and only the sixth survives. The five earlier ones and the reasoning between them are in a chat transcript. Future revisions are commits against the asset, with the reason in the commit message.
