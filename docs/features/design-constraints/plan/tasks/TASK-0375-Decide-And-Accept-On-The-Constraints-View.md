---
type: "[[task]]"
id: TASK-0375
aliases: ["TASK-0375"]
title: "A proposed ADR and a proposed design surface as this view's obligations"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"]
parent: "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"
effort: S
due: ""
depends: ["[[TASK-0374-Constraints-Membership]]", "[[TASK-0369-The-Obligation-Registry]]"]
blocks: []
related: ["[[FEAT-0042-Design-Bench]]"]
tests: []
---

# Decide and accept on the constraints view

## Definition of Done
- [x] `adr @ proposed` → **decide** and `design @ proposed`/offered → **accept** appear as this view's obligations, from the registry — `_owed_flag` on every row of the Decisions, Risks, Workflows, Reference and Designs groups
- [x] Both counted in the view's badge — asserted to be the *same predicate*, not the same number by coincidence (`test_a_proposed_adr_is_this_views_obligation`)
- [x] Accepting a design still stamps `design_revision` through `/api/design/verdict` — never through the generic proposal path — and the generic path now **refuses** designs outright, 403 (`test_a_design_verdict_cannot_go_through_the_transition_path`)
- [x] Rejecting still writes the design's own guarded transition — `Decline` posts the same endpoint with `accept: false`, semantics sent by the server (`test_the_buttons_still_appear_and_carry_their_endpoint`)
- [x] The actuators are on the note, not in the panes — the row marks what is owed; the buttons are where they have been since [[DES-0005]]

## Steps
- [x] Mark obligated rows in the view; group them if the count warrants, without creating a second list — it does not warrant one, see below
- [x] Route to the existing design-verdict machinery ([[FEAT-0042]]), which is not rebuilt
- [x] Assert the design path is used for designs — a design going through the proposal path is [[ISS-0056]]

## Notes
[[ISS-0056]] is the specific hazard: a design sent through the generic proposal path stamps `plan-accepted` with no revision, and rejection writes `cancelled` onto a design that may be `implemented`. An approval given to revision 3 must never launder revision 6, and the only thing preventing that is using the right endpoint.

## Done 2026-08-10

### The hazard was live, and the generic table had re-opened it

[[ISS-0056]] was fixed in July by building `/api/design/verdict`, which requires the verdict to name the revision it judged and validates that revision against real git history. [[FEAT-0059]] then added a **generic** human-transition table, and put `design: proposed → accepted | cancelled` in it.

Nothing refused it. A `proposed` design's actuator row offered **Accept**, and pressing it would have posted `/api/notes/transition` and written `status: accepted` with **no `design_revision`** — an approval given to revision 3 silently covering revision 6, which is the exact failure ISS-0056 exists to prevent. `Decline` was worse: `cancelled` onto a design that may already be `implemented`.

Never triggered, because no design in this corpus has ever been `proposed` (measured: DES-0001/0002 `implemented`, DES-0003/0009 `draft`, four `accepted`, one `superseded`). **A hazard nobody could reach is still a hazard**, and the first design ever offered for review would have reached it.

Closed in two places, deliberately:

1. **The writer refuses.** `stamp_transition` raises 403 for any type in `VERDICT_ENDPOINTS`, naming the route that should have been used. A design arriving there at all means something routed around the endpoint, and the UI is not the guard.
2. **The action carries its route.** `legal_actions` ships `endpoint` (the URL itself, so the renderer posts to what it is sent) plus `verdict` and `accept` from `VERDICT_SEMANTICS`. The buttons still appear, from the same table, in the same place — only the destination changed.

The first cut of (2) used a nickname, `"design-verdict"`, which the refusal message then rendered as `/api/design-verdict` — a URL that does not exist, in the one sentence a person reads when they are already blocked. The map holds the route now.

**And `accept` was very nearly inferred in the renderer** — from `!action.confirm`, the tone field — which is the status vocabulary leaking into TypeScript one field at a time, ISS-0023 in a new costume, and something this session already fixed once for the button's styling. The server says what the button means.

### The count is one, and it is ADR-0010

The step allowed grouping obligated rows "if the count warrants". Measured: **the constraints view owes exactly one thing** — `ADR-0010`, still `proposed`. Zero proposed designs, zero other proposed ADRs.

One row does not warrant a group, and a group would be the second list [[ISS-0068]] forbids. So the obligation is a **mark on the row where the note already lives**, which is what ADR-0020 decided and what the badge counts.

Worth noting where it points: the view's single obligation is one of the four decisions [[REL-0001]] tells this session to raise and stop on. The surface and the release note agree without either being written from the other.

### Verification

`915 passed, 2 skipped`; `validate-docs: OK`; `tsc --noEmit` clean; `dist/` rebuilt. Four new assertions, adequacy by mutation:

| mutation | killed by |
|---|---|
| drop the design refusal in `stamp_transition` | `test_a_design_verdict_cannot_go_through_the_transition_path` |
| stop shipping `endpoint` on actions | `test_the_buttons_still_appear_and_carry_their_endpoint` |
| drop `_owed_flag` from the constraints rows | `test_a_proposed_adr_is_this_views_obligation` |

The refusal test also asserts the note is **unchanged** after the 403 — a guard that half-wrote before refusing would be worse than the bug it replaced.
