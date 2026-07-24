---
type: "[[requirement]]"
id: REQ-0012
aliases: ["REQ-0012"]
title: "Muted greyscale palette, semantic-only color, dual light/dark themes"
status: verified
implements: ["[[FEAT-0001]]"]
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-07-24
amended: 2026-07-24
source: []
priority: high
scope: "FEAT-0001, FEAT-0004, FEAT-0006"
specifies: ["[[FEAT-0001]]", "[[FEAT-0004]]", "[[FEAT-0006]]"]
verifies: []
related: ["[[ADR-0003]]", "[[ISS-0023-Implemented-Status-Band-Drift]]"]
tests: ["[[TST-0019-Status-Vocabulary-Parity]]"]
---

# REQ-0012 — Visual style

## Statement
The project-os-cockpit UI is a developer's daily-driver tool, sitting alongside an editor and terminal. The visual style SHALL therefore be:

1. **Muted greyscale palette as the foundation.** Backgrounds, surfaces, borders, body text, and table chrome SHALL be drawn from a greyscale ramp. No brand-color fills or decorative accents.
2. **Color reserved for semantic signals only.** Color is permitted for: links, focus indicators, status chips, error/warning banners, the active/selected row in a pane. Color is NOT permitted for: backgrounds, dividers, headings, table stripes, decorative flourishes.
3. **Even semantic color SHALL be muted.** Hues SHALL be desaturated (target ≤60% saturation in HSL terms) — perceptually distinct but not "traffic light" bright. Status taxonomies stay readable via hue without dominating the page.
4. **Dual themes are mandatory.** Both light and dark themes SHALL be implemented. The default theme SHALL follow the OS-level `prefers-color-scheme`. The user MAY override via an explicit toggle in the UI; the override SHALL persist across sessions (e.g. localStorage).
5. **CSS custom properties are the single source of palette truth.** All colors used by the UI SHALL be defined as CSS custom properties on `:root` (light) and `[data-theme="dark"]` (dark). No hard-coded hex/rgb in component CSS. Theme switching is a class/data-attribute toggle, not a stylesheet swap.
6. **Status chips use a fixed 7-bucket palette.** Real-world project-os corpora (this repo + `../your-trainer`, ~1,200 notes) surface ~30 distinct status values across the type taxonomy. Mapping each to a unique hue would be visual noise; collapsing them all to 2–3 buckets erases meaningful distinctions. The palette SHALL therefore use exactly **7 buckets**, with all values ≤60% saturation:

| Bucket | Light HSL | Dark HSL | Member statuses |
|---|---|---|---|
| **Active** | 140 32% 38 | 140 32% 60 (green) | active, approved, accepted, ready, doing, in-progress, in-review, next, mitigating |
| **Pending** | 220 14% 48 | 220 14% 65 (cool grey) | planned, backlog, todo, open, pending, draft, proposed, triage |
| **Delivered** | 42 46% 34 | 42 46% 60 (amber) | implemented, staged, monitoring |
| **Done — positive** | 160 28% 38 | 160 28% 60 (teal-green) | done, merged, fixed, resolved, fulfilled, met, complete, verified, passing, published, released, closed |
| **Done — negative** | 0 0% 48 | 0 0% 58 (muted grey) | obsolete, retired, cancelled, superseded, wont-fix, reverted, rolled-back, deprecated |
| **Blocked** | 5 48% 46 | 5 50% 65 (red) | blocked, failing, reopened |
| **Reference** | 180 24% 40 | 180 24% 60 (cyan-grey) | reference, deferred |

Tokens live in `base.css` as `--status-active`, `--status-pending`, `--status-delivered`, `--status-done`, `--status-archived`, `--status-blocked`, `--status-reference`, plus a `--status-default` fallback for any unmapped value.

Bucket **membership** is canonical in `src/project_os_cockpit/statuses.py` (`BANDS` / `BAND_TOKEN`), not in the stylesheets: the CSS, the JS Hide-completed set, and the two Python ordering tables all derive from or are checked against it by [[TST-0019-Status-Vocabulary-Parity]]. Adding a new status alias to a bucket SHALL be a change to `statuses.py` plus the one-line CSS rules the parity test then demands. New buckets SHALL NOT be introduced unless the existing seven demonstrably collapse meaningfully different states.

7. **Delivered work SHALL NOT be treated as completed.** The Delivered bucket is non-terminal. Its members are excluded from the Hide-completed filter and from index-page default collapse, so that work which is built but not yet signed off stays on screen. Only the two Done buckets are terminal.

## Acceptance Criteria
- A grep for `#[0-9a-fA-F]{3,6}` and `rgb(`, `rgba(`, `hsl(`, `hsla(` in the served CSS returns matches *only* inside the `:root` / `[data-theme="dark"]` definition blocks. Component rules use `var(--token)` exclusively.
- The UI renders correctly with `prefers-color-scheme: light` and `prefers-color-scheme: dark` without user intervention.
- A theme-toggle control is present in the cockpit header and persists across reloads.
- Status chips render in their bucket's hue per the table above; e.g. `fulfilled` (Done-positive) reads teal-green, `wont-fix` (Done-negative) reads muted grey, `planned` (Pending) reads cool-grey, `implemented` (Delivered) reads amber, `blocked` reads red. All chips are ≤60% saturation in HSL.
- Every status in the canonical vocabulary resolves to its own bucket's token on all palette surfaces — chips, group icons, both ordering tables, and the Hide-completed set — with no status unmapped and none mapped to a bucket it does not belong to.
- Turning on **Hide completed** removes only terminal work; items in the Delivered bucket remain visible.
- No greyscale-vs-color contrast in the rendered page comes from anything other than: a link, a focus ring, a status chip, an error/warning banner, or the active row indicator.
- A page with frontmatter, body, status chip, backlinks panel, and code block looks visually quiet — color used <10% of the page area by quick visual estimate.

## Rationale
project-os-cockpit runs alongside the user's editor and terminal. A bright, saturated UI competes for visual attention with the work surface; a muted UI fades into the workspace. Light/dark preference varies by user and time-of-day, so picking one is a usability cliff for half the time the tool is in use. The hue-but-desaturated rule preserves the information value of color (you can tell `done` from `blocked` at a glance) without leaning on it as a primary visual driver.

The status palette balances information density and visual quietness. (This paragraph records the original 6-bucket derivation; the Delivered bucket added on 2026-07-24 is argued under "Amendments".) The earlier 8-bucket scheme collapsed `planned` / `proposed` / `draft` / `todo` / `open` / `pending` / `triage` onto one cool-grey hue (one bucket too coarse for status scanning) but gave `verified`, `triage`, and `closed` their own hues (one bucket too fine for the muted aesthetic). Empirical analysis of the `your-trainer` corpus produced the bucket boundaries — `closed` collapses into Done-positive (terminal = off your radar), `wont-fix` / `cancelled` / `superseded` / `reverted` / `obsolete` / `retired` form the Done-negative bucket (terminal-without-success, desaturated grey), and `in-review` rejoins Active because PR-up-awaiting-review is in flight, not "needs sorting".

See [[ADR-0003]] for the decision context.

## Amendments

### 2026-07-24 — seventh bucket: Delivered

Amends clause 6 (6 buckets → 7) and adds clause 7. Driven by [[ISS-0023-Implemented-Status-Band-Drift]], raised from `../your-sudoku` where 97 of 106 requirements sit at `implemented`.

The original clause 6 folded `implemented` into Done-positive. That collapse is the failure mode the clause's own escape hatch anticipated ("New buckets SHALL NOT be introduced unless the existing six demonstrably collapse meaningfully different states"): project-os defines `implemented` as *built but not yet formally verified* and gates `implemented → verified` on passing test notes, so treating it as done both mis-colours it and — had the Hide-completed set been made consistent in the obvious direction — would have hidden the entire population that still owes a verification record.

The evidence for "demonstrably": across the nine project-os repos on this machine, 276 notes sit at `implemented` against 77 at `verified`. Delivered-but-unverified is not a rounding error in the corpus; it is the single largest terminal-looking state.

Amber was chosen over a further green because the bucket means *awaiting sign-off*, matching the amber waiver chips already specified for [[FEAT-0018]].

Also folded in: statuses observed in real corpora but never mapped to any bucket — `resolved` (14 notes), `released` (10), `mitigating` (1) — plus the taxonomy members `staged`, `rolled-back`, `monitoring`, and `deprecated`, which had no chip rule at all.

## Traceability
- Implements: [[FEAT-0001]], [[FEAT-0004]], [[FEAT-0006]]
- Related decision: [[ADR-0003]]
- Implemented by: [[TASK-0016]] (palette overhaul + Hide-completed expansion); [[TASK-0198-Delivered-Status-Band]] (Delivered bucket + canonical vocabulary).
- Verified by: [[TST-0019-Status-Vocabulary-Parity]] (`tests/test_status_vocabulary.py`) for bucket membership, token mapping, theme coverage, and the ≤60% saturation rule; visual review against this repo's own `docs/` and `../your-trainer/docs/` (1,175 notes) for the aesthetic clauses.

## Verification
- 2026-05-23: marked `verified` — Visual style shipped — base.css + cockpit.css use CSS-var token palette with light/dark themes per ADR-0003.
- 2026-07-24: re-verified after the Delivered amendment — [[TST-0019-Status-Vocabulary-Parity]] `passing` (13 tests; full suite 245 passed, 1 skipped). The mechanical clauses (bucket membership, per-status token mapping, both-theme token definitions, ≤60% saturation) are now automated; the aesthetic clauses (colour <10% of page area, greyscale foundation) remain human visual review, unchanged since 2026-05-23. The amber `--status-delivered` hue has not yet had a browser visual pass — see [[TST-0019-Status-Vocabulary-Parity]] "Adequacy".
