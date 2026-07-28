---
type: "[[task]]"
id: TASK-0231
aliases: ["TASK-0231"]
title: "A design system note and living style guide for each project with a UX"
status: backlog
phase: "[[PHASE-999-Unscheduled]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0044-Fleet-Design-Systems]]"]
parent: "[[FEAT-0044-Fleet-Design-Systems]]"
effort: "L"
depends: ["[[TASK-0230-Project-Stylesheet-Route]]"]
blocks: []
related: ["[[DES-0002-Cockpit-Design-System]]"]
tests: []
---

# Roll the design systems out

## Scope

Six projects, seven surfaces — the table in [[FEAT-0044]]. Four have a `draft` note to upgrade; two have nothing.

## Definition of Done

- [ ] `edankert.com` and `obsidian-supernote-sync` gain a design note; the four existing `draft` notes are brought to the same shape
- [ ] Each note declares `stylesheets:` and carries an artifact that reads them — no palette table is load-bearing
- [ ] `obsidian-supernote-sync` is **one note, two sections**: the plugin inherits its host's theme tokens, the dashboard owns its palette
- [ ] Each note states what its project's system actually is, including the gaps — an invented scale is worse than a recorded absence
- [ ] The your-* notes point at the family palette ([[ADR-0008]] upstream in `your-applications.com`) rather than restating its nine values
- [ ] Each artifact is verified **rendering in a sandboxed frame**, not by reading it
- [ ] Each note leaves `draft` only once its page renders, matching what [[DES-0002]] required of itself

## Notes

The shape is [[DES-0002]]'s, and so is the discipline: read from the implementation, state the gaps as gaps, and let the page be the checkable thing. Copying its *prose* would be the mistake — each project's principles are its own, and a system nobody follows is worse than none.
