---
type: "[[feature]]"
id: FEAT-0097
aliases: ["FEAT-0097"]
title: "A decision offers its options — the note declares them in a form the tool can read, the validator keeps them that way, and accepting records which one"
status: done
phase: "[[PHASE-032-The-Reasoning-Is-Recorded]]"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
source: ["Edwin 2026-08-12: 'why for ADR-0010 do I not have a way to select an option? (how can we make sure the LLM formats the document correctly for me to be able to make these decisions?)'"]
goal: "A decision note that offers options declares them parseably; the cockpit offers them as a choice; accepting records which was chosen; and the validator reports a section it cannot read."
requirements: []
tasks:
  - "[[TASK-0401-Options-Are-Parsed]]"
  - "[[TASK-0402-The-Choice-On-The-Row]]"
  - "[[TASK-0403-The-Validator-Keeps-The-Shape]]"
related: ["[[ADR-0010]]", "[[FEAT-0095]]", "[[ISS-0152]]"]
tests: []
---

# A decision offers its options

## Goal

[[ADR-0010]] lists three options and proposes the third. The cockpit offers `Accept` and `Supersede`, so the only recordable outcome is *accepted* — **which option was chosen is lost**, and choosing a different one is not expressible at all.

Edwin's second question is the load-bearing one: *"how can we make sure the LLM formats the document correctly for me to be able to make these decisions?"* A widget is not the answer on its own. **The document has to declare its options in a form the tool can read, and something has to keep it that way** — otherwise the shape drifts per author and the control silently stops appearing.

Measured 2026-08-12: three ADRs carry an `## Options` section and they use **two different forms** already — `1. **Label.** rationale` in two, `### 1. Label` in the third. Nothing has ever said which is right, so both are.

## Out of scope

- **Requiring options.** Most ADRs are a yes/no. The section is available, not mandatory — the same rule the Acceptance section got.
- **Forcing a choice to accept.** A decision may be accepted as proposed; the option is recorded when one is picked, not demanded.
- **Rewriting the corpus.** Both observed forms parse. A convention that invalidated existing notes would be a migration wearing a convention's clothes.

## Acceptance

- [x] Both observed forms parse into `{number, label, body}` — `N. **Label.**` and `### N. Label` — and a decision with no options section is unaffected.
- [x] `/api/notes/actions` carries the options for a decision that declares them, so the surface never parses markdown itself.
- [x] The actuator row offers them as a choice, defaulting to the one the note proposes when it names one.
- [x] Accepting with an option chosen records it **in the note**: named in the decision-record callout and in a `decided_option` field.
- [x] Accepting without choosing is still allowed and records nothing extra.
- [x] **The validator reports an `## Options` section it cannot read** — an error rather than a warning, because the convention is new and there is no debt to grandfather ([[ADR-0011]] upstream).
- [x] The reasoning field is large enough to write a sentence in without scrolling it.


## Evidence — 2026-08-12

All three decisions with options parse, both forms, with the proposed one read from the `## Decision` section rather than from the list — every option mentions itself by number, so scanning the whole note would return option 1 every time:

| note | form | options | proposed |
|---|---|---|---|
| [[ADR-0010]] | `N. **Label.**` | 3 | 3 |
| [[ADR-0021]] | `N. **Label.**` | 4 | 4 |
| [[ADR-0022]] | `### N. Label` | 3 | 1 |

Choosing option 3 on a clone wrote `decided_option: "3"` and `> [!note] Accept — option 3: Mode 1 is the reading surface — 2026-08-12 (user:edwin)`. Option `9` was refused, naming what the note actually offers.

**The check was proved by breaking a real note**: mangling two of ADR-0021's options made `DECISION-OPTIONS` report `numbers its options [3, 4]`, and restoring the file cleared it.

## Why the validator is the answer, not the widget

Edwin's question was *"how can we make sure the LLM formats the document correctly"*, and a control that silently disappears when the shape drifts is not an answer. The convention is in the template's `DECISIONS.md` and in the ADR template itself, so it is where an author starts; and `DECISION-OPTIONS` fires at pre-commit and in CI, so it is not a suggestion the next author does not read.
