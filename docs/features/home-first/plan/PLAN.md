---
type: "[[plan]]"
title: "Delivery plan — Home first"
status: draft
owner: user:edwin
created: 2026-09-17
updated: 2026-09-17
source: ["[[FEAT-0152-Home-First]]"]
implements: ["[[FEAT-0152-Home-First]]"]
related: ["[[PHASE-045-The-Cockpit-In-Layers]]", "[[DES-0015-The-Cockpit-In-Layers]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:` — see docs/__templates__/plan.md. -->
# Delivery plan — Home first

Written before acceptance, as a sketch of the order the work would take. Tasks are minted only once [[DES-0015-The-Cockpit-In-Layers]] is accepted and D1 and D3 are decided.

## Delivery sequence

1. **Measure the budget on the fleet.** A script reads every discovered repository's obligations, landing, focus, history and release payloads and prints the composed size, so the 30 KB claim is checked on twelve repos before a line of page is written.
2. **The Home payload.** One sidecar route composed from existing functions in `cockpit.py`, `obligations.py`, `publication.py` and `git_state.py`; no new computation, no new state.
3. **The Home page.** A new virtual route in the renderer drawing the three cards from that payload; the overview's existing builders move behind a Record link unchanged.
4. **The four facts on the rail.** The rail square's existing health marks gain the needs-you count and the gate state from the same payload.
5. **The Dock badge**, once D3 is decided.
6. **The acceptance check**: the ten-second test on Edwin's real data, with the payload size recorded as evidence.

## Dependencies

- **Hard:** [[DES-0015-The-Cockpit-In-Layers]] accepted; D1 (replace or sit beside) and D3 (what the badge counts) decided.
- **Soft:** [[ADR-0025-An-Owed-Row-May-Appear-Twice]] already permits the Needs you card as a shortcut list; no decision needed.

## Open questions

- Whether Home's left pane is collapsed (as drawn) or shows the same three groups as a list. The design draws it collapsed; a walk on real data decides.
- Which repositories have no release and how their Shipping card collapses to the commits line.
