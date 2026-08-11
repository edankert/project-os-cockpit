---
type: "[[feature]]"
id: FEAT-0087
aliases: ["FEAT-0087"]
title: "Design widens into the project's constraints — decisions, risks, references and the brief join the designs"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "Edwin 2026-08-10: 'these documents are further input/constraints on the project, tool, to me these should include a project description and ADRs and possibly others'"]
goal: "Make one view for what bounds the project rather than what is built in it — designs, ADRs, risks, references, workflows, the glossary and the brief — and give the judgments those documents ask for (accept a design, decide an ADR) a home on it."
requirements: []
tasks:
  - "[[TASK-0374-Constraints-Membership]]"
  - "[[TASK-0375-Decide-And-Accept-On-The-Constraints-View]]"
  - "[[TASK-0379-Architecture-Becomes-A-Design]]"
  - "[[TASK-0385-The-View-Is-Called-Intent]]"
release: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[FEAT-0042-Design-Bench]]", "[[FEAT-0050-Library-Reduction]]", "[[FEAT-0077-The-Intent-Charter]]", "[[DES-0003-Intent-Page-And-Claims-Board]]"]
tests: []
---

# Design widens into the project's constraints

## Goal

The Design view holds 10 design notes. Beside it, the Library holds 17 rows — `reference/`, `references/`, `workflows/` — and the ADRs, risks and glossary have no view at all, reachable only through the overview's record column or a by-type group.

These are one kind of thing: **documents that bound what gets built**, as opposed to the work itself (Features), what went wrong (Issues), or what verifies it (Tests).

## The line, and the 32 notes that turn on it

**Project-level constraints belong here; feature-level specifications stay with their feature.**

An ADR, a risk, a design or the glossary constrains the whole project. A **requirement constrains one feature**, is already nested under the feature it specifies (with an `Unattached requirements` group for the rest), and "what must this feature do" belongs beside the feature. So the 32 requirements **stay in Features**, and requirement approval surfaces there ([[FEAT-0088]]).

This is recorded because it is the assumption most likely to be revisited, and it is one line away from moving 32 notes.

## Library stays, and the split is by question

Edwin's call, 2026-08-10. The two views answer different questions and the overlap is accepted knowingly:

- **Library is a file browser** — the docs tree and project-root files. *"Where is that file?"* It shows paths, including files that are not lifecycle notes at all.
- **This view is typed notes** — *"What constrains this project?"* It shows an ADR as a decision, not as a path.

So a `reference/` note appears in both, as a file there and as a constraint here. That is one item with two *addresses*, not two lists of obligations — the distinction [[ISS-0068]] turns on, and it stays acceptable only while Library remains a browser. If it ever grows typed groups of these notes, the overlap becomes duplication and this decision should be revisited.

## Scope

**In:** design (10) · adr/decision (10) · risk (6) · reference (18) · workflow (3) · architecture, glossary, dashboard (3) · the project brief and README. Both obligations the view owns — design `proposed`/offered → **accept**, adr `proposed` → **decide** — from [[FEAT-0089]]'s registry, with the badge.

**Out:**

- Requirements, per the line above.
- Change notes — [[ADR-0020]]'s amendment gives those to the Overview.
- The design bench's verdict machinery ([[FEAT-0042]]), which already exists and is reused, not rebuilt.
- **Retiring the Library** (Edwin, 2026-08-10: *"I do want to keep the library view for now"*). See the split below.
- **The view's name.** It stops being "Design" once it holds ADRs and risks, and [[ADR-0020]] leaves the name open. Naming it is part of the task, not assumed here — note that mode 1 already uses "Project" for `library`, so that word is taken.

## Acceptance

- [x] One view lists designs, decisions, risks, references, workflows, the glossary and the brief, grouped so each kind is findable — `Designs 10 · Decisions 11 · Risks 6 · Workflows 3 · Reference 11` ([[TASK-0374]])
- [x] The Library view still works, unchanged, and the overlap below is deliberate rather than drift — Edwin's call: *"I do want to keep the library view for now"*
- [x] A `proposed` design and a `proposed` ADR appear as this view's obligations and are counted in its badge — marked on the row, from the registry, asserted to be the same predicate as the badge ([[TASK-0375]])
- [x] Accepting a design still stamps `design_revision` through the existing guarded path — an approval given to one revision cannot launder another — **and the generic transition path, which had quietly become a second way in, now refuses designs with a 403**
- [x] Requirements do **not** appear here; they remain nested under their features — 32 of them, deliberately unmoved
- [x] The view has a name that covers its contents, agreed rather than inherited — **Intent**, done in [[TASK-0385]] on 2026-08-11: the button, the mode id, the server's mode and the stored preference. This criterion was reconciled rather than ticked on the reasoning quoted below, and **both halves of that reasoning were wrong** — it is one front door, not two (mode 1 has never exposed this view), and the migration is existing machinery (`RETIRED_NAV_MODES`, four entries already). Edwin re-read [[FEAT-0084]] and found it declines naming decisions by its own scope, so the park had no owner

## Links

- Decision: [[ADR-0020-Obligations-Live-With-Their-Subject]]
- Paths: `src/project_os_cockpit/cockpit.py` (`_design_groups`, `_library_groups`, `decisions_payload`), `desktop/src/renderer/renderer.ts`

## Closed 2026-08-10

The membership landed in [[TASK-0374]]; the obligations in [[TASK-0375]], which found the interesting thing.

**[[ISS-0056]] had been quietly re-opened.** [[FEAT-0059]]'s generic human-transition table included `design: proposed → accepted`, so a design's actuator row offered an Accept that would have written `status: accepted` with no `design_revision` — an approval given to revision 3 covering revision 6, the failure `/api/design/verdict` was built to prevent. Unreachable in this corpus, because no design has ever been `proposed`; reachable by the first design anyone offers for review. The writer refuses it now, and the button carries the route that has to serve it.

**The name was the one loose end, and it is closed** — [[TASK-0385]], 2026-08-11. What follows is the reasoning that deferred it, kept because the deferral was reasonable and still wrong.

> *(superseded 2026-08-11)* **The name is the one loose end**, and it is deliberate. Edwin agreed **Intent**; the registry's view is `intent` and the badge maps it; the mode id and the button label are still `design`, because renaming a mode means migrating a stored preference in two front doors, which is [[FEAT-0084]]'s subject and [[PHASE-029]]'s gate. The criterion is reconciled rather than ticked, so the gap is a decision with an owner instead of a claim.

**Measured when it was finally done:** *"two front doors"* was one — the browser cockpit's `NAV_MODES` is `library / features / issues / recent` and has never carried this view. *"a stored-preference migration"* was `RETIRED_NAV_MODES`, which already had four entries and took a fifth. The deferral was written while the surface was being built and never re-checked, which is the failure mode worth naming: **a reconciled criterion is a closed decision, and this one closed on a cost nobody measured.**
