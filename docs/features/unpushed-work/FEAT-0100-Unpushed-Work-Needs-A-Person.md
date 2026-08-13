---
type: "[[feature]]"
id: FEAT-0100
aliases: ["FEAT-0100"]
title: "Unpushed work needs a person — publication joins the obligation registry, and the push moves next to the commits it publishes"
status: doing
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["Edwin 2026-08-13: 'let's add the git status to the needs you section instead and have the actual push solution in the overview history. Can we then have an indication of having to push using a number on the overview icon?'", "Edwin 2026-08-13: 'widen the registry's definition'"]
goal: "A person learns that work is unpublished the same way they learn everything else that needs them — a number on the view button, a row in Needs you — and publishes it from the surface that already draws the commits."
requirements: []
tasks: ["[[TASK-0415-Git-State-For-Every-Workspace]]", "[[TASK-0416-Generalise-The-Note-Less-Obligation]]", "[[TASK-0417-Publication-Enters-The-Registry]]", "[[TASK-0418-The-Push-Lives-With-The-Commits]]", "[[TASK-0419-Every-Card-Is-A-Full-Card]]", "[[TASK-0420-A-Dismissal-Means-Until-Something-Changes]]"]
design: "[[DES-0011-Publication-Is-An-Obligation]]"
release: ""
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ADR-0025]]", "[[ADR-0022]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0098]]", "[[FEAT-0055]]", "[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]"]
tests: []
---

# Unpushed work needs a person

## Goal

**A person learns that work is unpublished the same way they learn everything else that needs them.** A number on the Overview button, a row in `Needs you`, and the push where the commits already are.

## Why this is a feature and not a fix

[[ISS-0156]] is the fix: the count is missing for the workspace you have open. Restoring it would repair three surfaces that were already the wrong shape — a band that exists only on the overview, a group you have to navigate to, and a tooltip line. None of them is where a person looks to find out what needs them.

The tool already answers that question, continuously, through the registry and its badges. Publication was outside it only because the registry counted judgments about the record. [[ADR-0027]] widened that on 2026-08-13; this is the widening's first subject, and the one that motivated it.

## Scope

- **The data, for every workspace, always** ([[TASK-0415]]) — closing [[ISS-0156]]. Nothing else here is truthful until this lands, because absent-at-zero makes an unknown count invisible.
- **The note-less obligation path, generalised** ([[TASK-0416]]) — standing documents and unpushed work through one walk that yields a count and its rows together, replacing two bolt-on special cases whose seam has already produced a badge that disagreed with its own group.
- **Publication registered as an obligation** ([[TASK-0417]]) — owned by the overview, with a noun and a verb, so the badge, the `Needs you` group and the landing page all read from one place.
- **The push, with the commits** ([[TASK-0418]]) — the overview history tile and `~history` mark which commits are unpublished and carry the action, plus the design artifact [[DES-0011]] needs before it can leave draft.

## Out of scope

- **A push control on the rail square** — [[DES-0004]]'s channel budget, and a publishing action on a 44px target.
- **A push button beside the project name** — considered and dropped on 2026-08-13; recorded in [[DES-0011]] because it is the obvious idea and will be re-proposed.
- **Retiring the Agents-screen group** — it answers *which of my twelve repos*, which no per-project surface can.
- **Pushing anything automatically.** Unchanged and not negotiable here: [[FEAT-0055]]'s rule is that a person clicks it, and the deploy-remote refusal keeps its single home.

## Acceptance

- With unpushed commits on a backup remote, the Overview button carries the count, hovering names it (`3 · commits to push`, not "items"), the overview's `Needs you` group lists it, and history offers the push beside the commits it would publish.
- The same three surfaces agree **by construction**, reading one walk — asserted, not observed.
- With no remote at all, the surfaces say *nothing here is backed up* rather than reporting a count of zero.
- With a deploy remote, the state is visible and the push is refused as a decision, not as a broken control.
- With nothing to publish, **every one of these surfaces is silent** — no zero badge, no empty group.
- The count is correct for a workspace with a live sidecar, which is the case that is wrong today.

## Links

- Decision: [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]
- Design: [[DES-0011-Publication-Is-An-Obligation]]
- The defect that motivated it: [[ISS-0156]]
- Phase: [[PHASE-030-Obligations-Go-Home]]
