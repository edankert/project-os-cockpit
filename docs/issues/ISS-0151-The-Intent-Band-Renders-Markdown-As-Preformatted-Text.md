---
type: "[[issue]]"
id: ISS-0151
aliases: ["ISS-0151"]
title: "The Intent band prints a markdown section as pre-wrapped plain text — the brief's own newlines render as hard breaks and its syntax renders as syntax"
status: fixed
severity: medium
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
phase: "[[PHASE-030-Obligations-Go-Home]]"
features: ["[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"]
tasks: []
related: ["[[FEAT-0091-The-Standing-Documents]]"]
tags: [issue, renderer, markdown]
---

# The Intent band renders markdown as preformatted text

## What was reported, and what is actually true

Edwin, 2026-08-12: *"The Intent page shows the information from the LLM_Brief.md but this seems to have hard line breaks which seems to have been introduced for readable line length."*

**The file has no hard line breaks.** Measured across all twelve repos on 2026-08-12: zero wrapped-prose pairs in any `LLM_BRIEF.md`, and none in this repo's other standing documents either. This one's longest prose line is 451 characters — a single continuous line, exactly as `MARKDOWN.md` requires.

**The breaks are the surface's.** `buildIdentityBand` takes the *"What it is for"* section and does:

```ts
det.textContent = forSection.body;          // raw markdown, as text
```

with `.design-identity-for { white-space: pre-wrap; }` in the stylesheet. So every newline the source uses to separate list items becomes a visible break, and the markdown renders as *syntax*: `1. **Where is this project now?** — …` appears with its asterisks.

The reported symptom is real and the diagnosis it invites is wrong — which matters, because acting on it means reflowing files that are already correct.

## The fix

The section arrives rendered. `brief_payload` gains `body_html` per section, produced by **the same markdown pipeline every other note goes through**, and the band inserts that instead of printing source. `white-space: pre-wrap` goes with it: it was compensating for text that should never have been text.

Rendering server-side rather than adding a markdown parser to the renderer is the same boundary the rest of the cockpit keeps — the sidecar renders, the shell arranges.

## What the tests hold

- The payload carries `body_html` and it is HTML, not the source string.
- The band inserts it as markup, and `.design-identity-for` no longer declares `pre-wrap` — the assertion that fails if someone reintroduces the compensation instead of the fix.
