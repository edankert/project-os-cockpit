---
type: "[[change]]"
id: CHG-20260718-Rail-Marker-Notch
aliases: ["CHG-20260718-Rail-Marker-Notch"]
title: "Rail agent-state markers — corner notch, accent busy, needs-input ring, revived active bar"
status: merged
owner: user:edwin
created: 2026-07-18
updated: 2026-07-18
source: []
commit: ""
pr: ""
impacts: ["workspace mini-rail", "agent-state dot", "active-workspace indicator"]
issues: ["[[ISS-0006-Rail-Marker-Clipping]]"]
features: ["[[FEAT-0020-Agent-Activity-Surfaces]]"]
reviewed_by: "model:claude-opus"
review_date: 2026-07-18
review_verdict: approved
related: []
---

# Rail agent-state markers (ISS-0006)

## Summary
The workspace rail's agent-state dot no longer renders as a clipped wedge. Root cause: `.ws-square` used `overflow: hidden` to round project icons while `.ws-dot` sat 2px outside the square — the rounded corner cut the dot's outer arc, and the same rule silently clipped the active-workspace accent bar (`.ws-square.active::before`), which had never been visible. Chosen fix (option A + ring hybrid from a live mockup comparison): clipping moves off the square onto the icon itself (`img.ws-icon { border-radius: inherit }`, square overflow back to visible); the dot becomes a 10px circle overlapping the corner at −3px with a 3px `box-shadow` ring in `--bg-elevated`, punching a clean Discord-style notch against the rail on both letter tiles and icon artwork. The revived active bar moves from `left: −8px` to `−6px` so it lands inside the workspace list's own clip, flush with the rail edge.

State palette: **busy switches from `--status-active` green to `--accent`** — at 10px the busy/done greens (hsl 140 vs 160) were indistinguishable, and accent already means "actively driving" in the cockpit; done stays green, waiting keeps the amber slow pulse, idle faint, error critical. Busy is recolored on all three marker surfaces so the semantics stay consistent: rail dot, status-footer agent dot (`.sf-agent .sf-dot`), and activity-strip dot. **needs-input keeps the fast red dot pulse and additionally pulses a red ring around the whole square** (`box-shadow` animation, static ring under `prefers-reduced-motion`; the reduced-motion block also stills the waiting/strip/footer pulses) — urgency alone earns the loud treatment, calm states stay a quiet dot.

Independent review (opus) caught two follow-ons folded in here: the busy recolor initially missed the footer/strip surfaces, and `.workspace-list`'s `overflow-y: auto` clips on all sides — the first square's ring and the last square's overhanging dot needed `padding: 4px 0 6px` on the list.

CSS-only: `desktop/src/renderer/renderer.css`; no DOM, TypeScript, or payload changes. Verified by rebuilding the desktop bundle and seeding `busy` and `needs-input` agent-states against the running app — accent dot and pulsing ring render un-clipped.
