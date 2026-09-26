---
type: "[[task]]"
id: TASK-0088
aliases: ["TASK-0088"]
title: "Cmd+P quick-switch — fuzzy note search palette"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0012"
effort: ""
due: ""
depends: ["[[TASK-0083]]"]
blocks: []
related: []
tests: []
---

# Cmd+P quick-switch

## Definition of Done
- [ ] ⌘P opens a centred overlay over the cockpit window.
- [ ] Input field at the top; live fuzzy-search results below.
- [ ] Corpus: every note returned by `/api/cockpit/nav?mode=library`
      (or a flat aggregation across all modes). Match on `id`,
      `title`, `rel_path`, frontmatter `aliases`.
- [ ] Enter navigates the centre pane to the selected note; Esc
      closes; arrow keys move selection.
- [ ] Mouse hover + click also work.

## Steps
- [ ] Renderer: overlay component with input + result list.
- [ ] Fuzzy matcher — small custom implementation or a tiny
      dependency (e.g. `fuzzysort`). v1 keeps it dep-free; substring
      + score-by-prefix-match is enough for the corpus sizes we see.
- [ ] Menu accelerator + standalone keydown listener.
