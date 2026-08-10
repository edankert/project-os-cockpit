---
type: "[[feature]]"
id: FEAT-0087
aliases: ["FEAT-0087"]
title: "Design widens into the project's constraints — decisions, risks, references and the brief join the designs"
status: planned
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

- [ ] One view lists designs, decisions, risks, references, workflows, the glossary and the brief, grouped so each kind is findable
- [ ] The Library view still works, unchanged, and the overlap below is deliberate rather than drift
- [ ] A `proposed` design and a `proposed` ADR appear as this view's obligations and are counted in its badge
- [ ] Accepting a design still stamps `design_revision` through the existing guarded path — an approval given to one revision cannot launder another
- [ ] Requirements do **not** appear here; they remain nested under their features
- [ ] The view has a name that covers its contents, agreed rather than inherited

## Links

- Decision: [[ADR-0020-Obligations-Live-With-Their-Subject]]
- Paths: `src/project_os_cockpit/cockpit.py` (`_design_groups`, `_library_groups`, `decisions_payload`), `desktop/src/renderer/renderer.ts`
