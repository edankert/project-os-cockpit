---
type: "[[plan]]"
title: "Delivery plan — subject threads"
status: draft
owner: user:edwin
created: 2026-09-17
updated: 2026-09-17
source: ["[[FEAT-0154-Subject-Threads]]"]
implements: ["[[FEAT-0154-Subject-Threads]]"]
related: ["[[PHASE-045-The-Cockpit-In-Layers]]", "[[DES-0015-The-Cockpit-In-Layers]]", "[[project-os-deck#REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:` — see docs/__templates__/plan.md. -->
# Delivery plan — subject threads

Written before acceptance. Tasks are minted only once [[DES-0015-The-Cockpit-In-Layers]] is accepted, D5 is decided, and Edwin has said whether this is built here or in Deck.

## Delivery sequence

0. **Where it is built.** Cockpit or Deck, decided by Edwin and recorded in the phase's log before anything else.
1. **The timeline payload.** A sidecar route that filters the history payload to one subject and joins commits, verdicts and review fields; sessions from the sessions payload. Read-only, tested on this repository's own record.
2. **The header card for features**, the type with the most fields and the clearest next action, drawn from the frontmatter the renderer already strips.
3. **The thread page for features**: header card, timeline, folded sessions, the note, the frontmatter fold.
4. **The other subject types** one at a time: issue, design, release, test.
5. **The sidebar by recency and need**, last, because it is the only part that changes the pane grammar and the one most likely to belong to Deck.
6. **The acceptance check**: a feature's first screen on real data.

## Dependencies

- **Hard:** [[DES-0015-The-Cockpit-In-Layers]] accepted; D5 decided; the cockpit-or-Deck decision recorded.
- **Soft:** [[FEAT-0152-Home-First]] and [[FEAT-0153-Flows-As-Views]] first, so the thread page is reached from a Home card and a flow row rather than from today's navigator.

## Open questions

- Whether the sidebar-by-recency step belongs here at all, or is Deck's Spread.
- How a release's thread and the walk page relate: the walk page is already the release's layer 3 for one platform.
