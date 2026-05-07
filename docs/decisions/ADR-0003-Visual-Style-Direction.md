---
type: "[[adr]]"
id: ADR-0003
aliases: ["ADR-0003"]
title: "Visual style: muted greyscale, semantic-only color, dual themes"
status: accepted
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
deciders: [user:edwin]
related: ["[[REQ-0012]]", "[[FEAT-0001]]", "[[FEAT-0004]]", "[[FEAT-0006]]"]
---

# ADR-0003 — Visual style direction

## Context
docs-server is a developer's daily-driver tool. It will run side-by-side with the user's text editor and a terminal — three windows competing for attention on the same screen. We need a visual style that:

- Lives comfortably alongside an editor (which is itself usually muted and either light or dark).
- Stays out of the way during long reading sessions.
- Doesn't dictate light *or* dark; both must work because individual preference and time-of-day vary.
- Still uses color where color carries meaning — links must look like links, status chips must be distinguishable, errors must be obvious.

## Decision
The UI uses a **muted greyscale palette** as its foundation, with color reserved for **semantic signals only** (links, focus, statuses, errors, active selection). Even those semantic colors are **desaturated** — perceptually distinct hues, not pure RGB primaries.

Both **light and dark themes** are mandatory. The default tracks `prefers-color-scheme`; an explicit user toggle persists in localStorage. Themes are implemented as **CSS custom properties** on `:root` / `[data-theme="dark"]`, with component CSS referencing `var(--token)` exclusively — no hard-coded color literals outside the theme definition.

The normative version of this lives in [[REQ-0012]]; this ADR captures the why and the rejected alternatives.

## Alternatives considered

- **Brand-color forward (e.g. accent fills, coloured headings, a saturated primary).** Rejected — competes with the editor and terminal for attention; "branding" has no value on a personal/team developer tool.
- **Full-color status taxonomy (vivid red/amber/green/blue/etc).** Rejected as a default — readable but noisy. The desaturated variant keeps the semantic value of hue without the visual weight. (We can revisit per-status if a particular state genuinely needs to scream.)
- **Light-only theme.** Rejected — half of developers prefer dark, and even light-preferring developers want dark in low ambient light. Picking one is a usability cliff for the other half of usage time.
- **Dark-only theme.** Rejected for the same reason in reverse.
- **Per-feature color choices (each pane / each note type picks its own accent).** Rejected — fragments the visual language and makes accessibility/contrast review impossible. One palette, one set of tokens.

## Consequences

### Positive
- Visual consistency across all UI features is a token-level concern, not a per-component one. Adding a new pane or chip type means picking from the existing tokens, not minting new colors.
- Theme switching is a single attribute toggle. No stylesheet duplication.
- Accessibility/contrast review happens once per theme, not per page.
- The UI ages well — it's not bound to a 2026 brand fashion.

### Negative
- A new contributor's instinct to "make it pop" gets pushed back. Documented here so the pushback is reasoned, not arbitrary.
- Status chips in the desaturated palette have less colour distance than vivid versions, so the hue choices need care to stay perceptually distinguishable for users with common colour-vision deficiencies. (Mitigation: add a status icon glyph alongside the chip if hue alone proves insufficient — open enhancement, not a blocker.)
- CSS custom properties on the document root means a brief flash of the wrong theme on first paint if the user has overridden the OS preference. Mitigation: inline the theme-resolution script in `<head>` so the data-attribute is set before stylesheet apply.

## Status
Accepted. Reconsider if user testing reveals that desaturated status hues are not perceptually distinguishable enough, or if a non-developer audience becomes a primary user.
