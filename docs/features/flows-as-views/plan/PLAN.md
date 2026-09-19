---
type: "[[plan]]"
title: "Delivery plan — flows as views"
status: draft
owner: user:edwin
created: 2026-09-17
updated: 2026-09-17
source: ["[[FEAT-0153-Flows-As-Views]]"]
implements: ["[[FEAT-0153-Flows-As-Views]]"]
related: ["[[PHASE-045-The-Cockpit-In-Layers]]", "[[DES-0015-The-Cockpit-In-Layers]]", "[[FEAT-0152-Home-First]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:` — see docs/__templates__/plan.md. -->
# Delivery plan — flows as views

Written before acceptance. Tasks are minted only once [[DES-0015-The-Cockpit-In-Layers]] is accepted and D2 is decided in an ADR.

## Delivery sequence

0. **D2 first, as an ADR.** Where the publication ladder lives narrows [[ADR-0028-Work-Has-Three-Phases]]; nothing here is built until that is written and accepted.
1. **Folded groups in the navigator payload.** `nav_payload` sends a terminal group as a count with a key; a new route expands one group. No view changes yet; the renderer draws a folded group as today's `Quiet` fold. This alone removes most of the 297 KB.
2. **State-first ordering per view**, one view per task, in the order Issues, Build, Verify, Design, because Issues already gathers its triage queue and Build is where the phase containers cost the most.
3. **Text labels on the mode buttons** and the renaming of Intent to Design and Features to Build, with the stored preference migrated as the Tasks mode's was.
4. **Triage next**, once D4 is decided.
5. **The acceptance checks**: one per view, each stating that the first screen shows no finished work unless a fold is opened.

## Dependencies

- **Hard:** [[DES-0015-The-Cockpit-In-Layers]] accepted; D2 decided as an ADR; D4 decided before step 4.
- **Soft:** [[FEAT-0152-Home-First]] first, so the Home mode exists before the modes are renamed around it.

## Open questions

- Whether Publication stays a sixth mode (as [[ADR-0028-Work-Has-Three-Phases]] decided) or folds into Home and Verify (as the design recommends). This is D2.
- Whether the retired mode names keep answering on the server, as `tasks`, `active` and `recent` do today. They should; the register's rule keeps their keys.
