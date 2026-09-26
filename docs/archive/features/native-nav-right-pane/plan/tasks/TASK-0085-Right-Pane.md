---
type: "[[task]]"
id: TASK-0085
aliases: ["TASK-0085"]
title: "Right pane — linked + backlinks via /api/cockpit/context"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0010"
effort: ""
due: ""
depends: ["[[TASK-0080]]", "[[TASK-0083]]"]
blocks: []
related: []
tests: []
---

# Right pane

## Definition of Done
- [ ] `<aside id="right-pane">` exists; `.app` grid extends to
      `52px 240px 1fr 240px`.
- [ ] On centre-pane navigation, renderer fetches
      `/api/cockpit/context?this=<rel>` and renders:
      - `linked[]` (outbound) as grouped item rows
      - `backlinks[]` (inbound-only) as grouped item rows
      - Active note's severity / status chip in the pane header
- [ ] Right-pane toggle (chevron) button — collapses to a thin
      strip showing only the chevron. State persisted to userData.
- [ ] Default state: **collapsed** on first launch (saves
      horizontal space on smaller windows; user can expand).
- [ ] Click any linked / backlinked item → centre nav.
- [ ] Re-fetches on every centre navigateTo call.

## Steps
- [ ] HTML + CSS: new column + collapsed/expanded states.
- [ ] `right-pane.ts` (new) — render module mirroring `ws-nav.ts`.
- [ ] Hook into `navigateTo` (renderer.ts) so right pane fetches
      alongside centre.

## Notes
The frontmatter card is already mounted **inside** the centre pane
(via `data.metadata_html` from `/api/render`), so the right pane is
*just* outbound + backlinks. No duplication with mode 1's right
pane (which DID host both, but in our native shell the frontmatter
lives at the top of the centre doc).
