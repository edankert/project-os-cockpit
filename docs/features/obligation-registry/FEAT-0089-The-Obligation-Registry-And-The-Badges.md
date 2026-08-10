---
type: "[[feature]]"
id: FEAT-0089
aliases: ["FEAT-0089"]
title: "The obligation registry and the badges — one source for what is owed, of what kind, and which view owns it; a count on every view button that together covers all of them"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
goal: "Enumerate every owed human judgment in one module — kind, subject, owning view — and render each view's share as a badge on its button, so 'what needs me' is answered continuously and no kind can exist without a home."
requirements: []
tasks:
  - "[[TASK-0369-The-Obligation-Registry]]"
  - "[[TASK-0370-Badges-On-The-View-Buttons]]"
release: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[TASK-0357-Obligation-Groups-And-Verbs-In-The-Payload]]", "[[ISS-0023-Status-Vocabulary-Drift]]", "[[DES-0008-The-Returning-Human]]"]
tests: []
---

# The obligation registry and the badges

## Goal

[[ADR-0020]] decision 3: *the count lives on the view button, and the badges must cover every obligation kind.* That is only enforceable if the kinds exist as data. This feature is that data, plus its first consumer.

The registry answers three things per kind: **what state makes something owed** (`requirement @ draft`, `issue @ triage`, `test @ ready` and manual, `design @ proposed` or offered, `adr @ proposed`, `review_verdict: changes-requested` on a live subject), **which view owns it**, and **what verb discharges it** (approve · accept · decide · triage · run · re-review).

## Why this is first, and why it is one module

Every other feature in [[PHASE-030]] reads it. Building the views first would put the vocabulary in four renderers — which is [[ISS-0023]] with a different noun, and that cost weeks the last time.

It also carries forward the one idea worth keeping from the superseded desk board: [[TASK-0357]] specified *"the verb ships in the payload beside the group; no obligation vocabulary in TypeScript."* Same rule, wider scope.

## Scope

**In:**

- One module enumerating obligation kinds with their predicate, owning view and verb
- `issue: triage` as a first-class kind — the largest pool in the fleet and the one the old queue omitted
- A payload the renderers consume for counts and for each view's own list
- Badges on the view buttons in the shell
- A test that fails when a kind exists with no owning view, or a view claims a kind the registry does not have

**Out:**

- Rendering any view's obligation section — each view's own feature does that
- Any write path. The registry says what is owed; [[DES-0005]]'s actuators discharge it, unchanged
- Questions. [[ADR-0020]] decision 6 drops them deliberately; the registry has no kind for them, and that absence is the decision, not an omission

## Acceptance

- [x] Every obligation kind is declared once, with predicate, owning view and verb; `review_queue_payload`'s intake states are replaced by it rather than duplicated
- [x] `issue: triage` is among them
- [x] The badges together equal the registry's total — asserted, so a kind cannot be added without appearing somewhere
- [x] A kind with no owning view fails a test
- [x] Removing a kind removes its badge with no renderer change
- [x] A settled subject is never counted as owed ([[ISS-0121]]'s predicate belongs here, not in a register)

## Links

- Decision: [[ADR-0020-Obligations-Live-With-Their-Subject]]
- Precedent: `src/project_os_cockpit/statuses.py` + `tests/test_status_vocabulary.py` — the same shape of fix, for statuses
- Paths: `src/project_os_cockpit/cockpit.py` (`QUEUE_INTAKE_STATES`, `review_queue_payload`), `desktop/src/renderer/renderer.ts`

## Closed 2026-08-10

The registry exists and the badges read it: **18 types declared, 8 owed, 10 explicit `none`**, and `overview 81 · issues 7 · features 5 · intent 1 · tests 0`.

Two properties are what make it worth having, and both are asserted rather than intended:

- **The corpus supplies the checklist.** A type in the notes with no declaration fails a test. The list this replaced was wrong three times in one day — `change`, `release`, then `risk`/`workflow`/`phase` — each found by Edwin asking rather than by anything failing.
- **`none` carries its reason.** The test caught two of my own entries saying only *"a standing document; see `reference`"*. `task` and `plan` owe nothing correctly, and an unexplained absence is indistinguishable from a forgotten one.
