---
type: "[[phase]]"
id: PHASE-026
aliases: ["PHASE-026"]
title: "The returning human — the cockpit addresses the person who was away: what happened, what needs you, what shipped, in one voice"
status: done
order: 26
owner: user:edwin
created: 2026-08-03
updated: 2026-08-14
goal: "Give the docs-first human a daily entry point: a since-you-looked digest with a watermark, a release surface that distinguishes done from shipped, and one voice across the panes' remaining inconsistencies."
features:
  - "[[FEAT-0071-Since-You-Looked]]"
  - "[[FEAT-0072-The-Release-Surface]]"
  - "[[FEAT-0073-One-Voice]]"
requirements: []
issues:
  - "[[ISS-0142-The-Release-Note-Cannot-Be-Found-By-Name]]"
  - "[[ISS-0164-Phases-Are-The-Second-Type-The-Palette-Cannot-Find]]"
depends: []
related: ["[[DES-0008-The-Returning-Human]]"]
tags: [continuity, overview, release]
---

# The returning human

## Where this came from

The 2026-08-03 review, third cluster. The cockpit renders current state well and history on request — but nothing is addressed to *the person who was away while agents worked*. The landing page's NEEDS-YOU cards know only about waiting terminals; History knows every transition but not which ones you have seen; and "done" is the only fact the tool knows, though `docs/__templates__/acceptance-tests.md` already defines a release gate with nowhere to bite ("a release is blocked while any Tier 1/2 test is unchecked").

## Scope

[[FEAT-0071]] — a per-workspace watermark and a digest derived from the existing `history_payload`: N transitions since you looked, M reviews landed, these need you; a "caught up" action moves the watermark. [[FEAT-0072]] — the REL flow gets its minimal surface: what shipped, what is done-but-unshipped, the acceptance-tests gate rendered where a release is cut. [[FEAT-0073]] — the consistency residue, spent deliberately: one empty-state voice, the collapse-completed toggle's retirement or defence, the desk-and-Library exceptions written into the design system note, and the mode-1 decision taken as an ADR rather than re-litigated per change.

Design: [[DES-0008]] — the returning human's first minute.

## Out of Scope

- **Notifications.** The digest is pulled when the human arrives, never pushed. A tool for a person who was away must not follow them there.
- **Multi-user watermarks.** One human per cockpit today; per-person watermarks are speculative machinery.
- **Deciding mode 1's fate here.** The phase's task is to *author the ADR* with usage evidence; the decision is the ADR's, made once, wherever it lands.

## Exit Criteria

- [x] Opening a workspace after time away answers "what happened" in one screen — evidence: the digest band, `Since you looked — 13h ago`, needs-you above the news ([[FEAT-0071]]). Its `Caught up` now advances the watermark to an **instant** rather than a day, so it works on a day someone is committing ([[ISS-0134]])
- [x] "Done but not shipped" is a number somewhere true — evidence: `Unreleased · 70` on the record column, *"70 features done, none in a shipped release yet"*. True because only a `released` release ships anything: REL-0001 is `draft`, so it subtracts nothing ([[TASK-0315]])
- [x] Every empty state speaks in one voice and says what would appear there — evidence: nine rewritten, including the three that named nothing (`(no items)`, `(no children)`, `All clear.`); `tests/test_empty_state_voice.py` sweeps the literals and requires both halves ([[TASK-0318]])
- [x] Mode 1's cost has an owner: an ADR that either retires it, funds it, or scopes it — evidence: [[ADR-0021]], `proposed`. It takes the **fourth** option the task added — share the contract — on the evidence that a fourth drift arrived on 2026-08-11 and was *not* caught by review ([[TASK-0321]])
- [x] The deliberate exceptions (desk headings, Library file rows) are recorded in the design system note — evidence: [[DES-0002]]'s `Deliberate exceptions` section, which also defends the collapse-completed eye rather than retiring it ([[TASK-0319]], [[TASK-0320]])

## FEAT-0071 pulled forward 2026-08-10

This phase has no dependencies and gates nothing formally, so it read as deferrable. It is not, in one respect: **[[FEAT-0071]] is the named mitigation for [[PHASE-030]]'s one accepted cost.**

[[ADR-0020]] retires the review desk and concedes that discharging judgments becomes up to four visits instead of one, answered by this phase's landing digest. So `FEAT-0071` must land **before** [[TASK-0378]] removes the route, and [[TASK-0378]] now carries that dependency explicitly.

The rest of this phase — [[FEAT-0072]]'s release surface and [[FEAT-0073]]'s one-voice sweep — keeps its original position and can follow later.
