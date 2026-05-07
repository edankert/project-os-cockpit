---
type: "[[requirement]]"
id: REQ-0012
aliases: ["REQ-0012"]
title: "Muted greyscale palette, semantic-only color, dual light/dark themes"
status: approved
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
priority: high
scope: "FEAT-0001, FEAT-0004, FEAT-0006"
specifies: ["[[FEAT-0001]]", "[[FEAT-0004]]", "[[FEAT-0006]]"]
verifies: []
related: ["[[ADR-0003]]"]
tests: []
---

# REQ-0012 — Visual style

## Statement
The docs-server UI is a developer's daily-driver tool, sitting alongside an editor and terminal. The visual style SHALL therefore be:

1. **Muted greyscale palette as the foundation.** Backgrounds, surfaces, borders, body text, and table chrome SHALL be drawn from a greyscale ramp. No brand-color fills or decorative accents.
2. **Color reserved for semantic signals only.** Color is permitted for: links, focus indicators, status chips, error/warning banners, the active/selected row in a pane. Color is NOT permitted for: backgrounds, dividers, headings, table stripes, decorative flourishes.
3. **Even semantic color SHALL be muted.** Hues SHALL be desaturated (target ≤60% saturation in HSL terms) — perceptually distinct but not "traffic light" bright. Status taxonomies stay readable via hue without dominating the page.
4. **Dual themes are mandatory.** Both light and dark themes SHALL be implemented. The default theme SHALL follow the OS-level `prefers-color-scheme`. The user MAY override via an explicit toggle in the UI; the override SHALL persist across sessions (e.g. localStorage).
5. **CSS custom properties are the single source of palette truth.** All colors used by the UI SHALL be defined as CSS custom properties on `:root` (light) and `[data-theme="dark"]` (dark). No hard-coded hex/rgb in component CSS. Theme switching is a class/data-attribute toggle, not a stylesheet swap.

## Acceptance Criteria
- A grep for `#[0-9a-fA-F]{3,6}` and `rgb(`, `rgba(`, `hsl(`, `hsla(` in the served CSS returns matches *only* inside the `:root` / `[data-theme="dark"]` definition blocks. Component rules use `var(--token)` exclusively.
- The UI renders correctly with `prefers-color-scheme: light` and `prefers-color-scheme: dark` without user intervention.
- A theme-toggle control is present in the cockpit header and persists across reloads.
- Status chips for the project-os taxonomy (`active`, `doing`, `done`, `verified`, `blocked`, `backlog`, `triage`, `closed`, etc.) are perceptually distinguishable in both themes but no chip is more saturated than ~60% HSL S.
- No greyscale-vs-color contrast in the rendered page comes from anything other than: a link, a focus ring, a status chip, an error/warning banner, or the active row indicator.
- A page with frontmatter, body, status chip, backlinks panel, and code block looks visually quiet — color used <10% of the page area by quick visual estimate.

## Rationale
docs-server runs alongside the user's editor and terminal. A bright, saturated UI competes for visual attention with the work surface; a muted UI fades into the workspace. Light/dark preference varies by user and time-of-day, so picking one is a usability cliff for half the time the tool is in use. The hue-but-desaturated rule preserves the information value of color (you can tell `done` from `blocked` at a glance) without leaning on it as a primary visual driver.

See [[ADR-0003]] for the decision context.

## Traceability
- Implements: [[FEAT-0001]], [[FEAT-0004]], [[FEAT-0006]]
- Related decision: [[ADR-0003]]
- Verified by: visual review against this repo's own `docs/` (the dogfood tree); a CSS lint check for hard-coded color values outside the theme-token block.
