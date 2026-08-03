---
type: "[[phase]]"
id: PHASE-026
aliases: ["PHASE-026"]
title: "The returning human — the cockpit addresses the person who was away: what happened, what needs you, what shipped, in one voice"
status: planned
order: 26
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
goal: "Give the docs-first human a daily entry point: a since-you-looked digest with a watermark, a release surface that distinguishes done from shipped, and one voice across the panes' remaining inconsistencies."
features:
  - "[[FEAT-0071-Since-You-Looked]]"
  - "[[FEAT-0072-The-Release-Surface]]"
  - "[[FEAT-0073-One-Voice]]"
requirements: []
issues: []
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

- [ ] Opening a workspace after time away answers "what happened" in one screen — evidence: <the digest>
- [ ] "Done but not shipped" is a number somewhere true — evidence: <the release card>
- [ ] Every empty state speaks in one voice and says what would appear there — evidence: <the sweep's diff>
- [ ] Mode 1's cost has an owner: an ADR that either retires it, funds it, or scopes it — evidence: <the ADR id>
- [ ] The deliberate exceptions (desk headings, Library file rows) are recorded in the design system note — evidence: <the section>
