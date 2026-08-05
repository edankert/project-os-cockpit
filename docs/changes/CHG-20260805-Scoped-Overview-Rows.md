---
type: "[[change]]"
id: CHG-20260805-Scoped-Overview-Rows
title: "The phase-scoped overview's rows become rows: fields in columns, one height, and ids that fit"
status: merged
reviewed_by: model:claude-opus-5
review_date: 2026-08-05
review_verdict: approved
date: 2026-08-05
owner: user:edwin
component: [desktop-renderer]
related: ["[[PHASE-016-The-Overview-Answers-Questions]]", "[[ISS-0097-Scoped-List-Rows-Have-No-Layout]]", "[[ISS-0098-The-Squares-Strip-Collapses-To-A-Column]]", "[[ISS-0099-Change-Ids-Unshortened-In-The-Activity-Feed]]"]
---

# The scoped overview's rows

## What changed

**Verification and Remaining rows have a layout.** They had none — not one CSS rule in either stylesheet — so `TST-0005GET /api/render — … guardauto · ran 2026-05-25` was four fields rendered as one string. Now flex, gapped, with a fixed id column and an ellipsising title.

**Feature rows are all one height.** They ran 32…116px on your-health PHASE-0010; now 32…33px across twelve rows. The task squares no longer wrap into a vertical column, cap at twelve with a `+N`, and the annotation trail shows one item — failing, then doing, then triage, then next — with the rest in a `+N` tooltip.

**Activity ids fit.** A `CHG-` slug wrapped to four lines beside neighbours showing `TASK-0174`; the feed now shortens like every other surface.

## The rule behind all three

**A row whose height depends on its contents is not a row.** Whichever child is most compressible absorbs every shortfall — and a 3px square is the most compressible thing on a feature row.

## And a guard worth keeping

ISS-0099's fix asked for a guard that *enumerates* id-rendering sites rather than naming the known ones. Written that way it immediately failed on two surfaces nobody had reported — the Now board's cards and the agent detail's work rows, the fifth and sixth places this shortening has had to reach.

Mutation then found the guard's own hole: its `title="…"` exemption applied per line rather than per occurrence, so one legitimate full-value tooltip exempted the visible id beside it.

## Restart required

Mode 3 is a built bundle. The change is live after the desktop app restarts.
