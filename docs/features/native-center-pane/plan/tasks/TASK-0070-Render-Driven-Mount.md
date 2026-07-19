---
type: "[[task]]"
id: TASK-0070
aliases: ["TASK-0070"]
title: "Replace iframe with /api/render-driven mount + ship cockpit.css to the renderer"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0011"
effort: ""
due: ""
depends: ["[[TASK-0067]]"]
blocks: ["[[TASK-0071]]", "[[TASK-0072]]", "[[TASK-0073]]", "[[TASK-0074]]"]
related: []
tests: []
---

# Replace iframe with `/api/render`-driven mount

## Definition of Done
- [ ] `<iframe id="sidecar-view">` removed from `index.html`;
      replaced by `<div id="doc-view">` styled to fill the same slot.
- [ ] After `sidecar:event` 'ready', renderer fetches
      `${url}/api/render?path=README.md` (or a "no README" placeholder
      if 404) and mounts the HTML into `#doc-view`.
- [ ] `dist/renderer/cockpit.css` exists, copied from
      `src/project_os_cockpit/static/cockpit.css` by `copy-assets.mjs`.
      Loaded via `<link rel="stylesheet">` in `index.html`.
- [ ] A `navigateTo(relPath)` function exists that fetches `/api/render`
      and re-mounts. (Linking, history, scroll handled in later tasks.)
- [ ] Mode-1 (browser) unaffected; this is purely renderer-side.

## Steps
- [ ] Patch `copy-assets.mjs` to copy `cockpit.css`.
- [ ] HTML: replace iframe element; add `<link rel="stylesheet" href="./cockpit.css">`.
- [ ] CSS: ensure `#doc-view` flexes correctly and scrolls.
- [ ] Renderer: stash the active sidecar `url` from the ready event;
      implement `navigateTo(relPath)` that POSTs-not POSTs/GETs
      `${url}/api/render?path=...`; mounts `response.html` via
      `innerHTML`.
- [ ] On `sidecar:event` 'ready', call `navigateTo('README.md')`;
      on 404, mount a placeholder.

## Notes
The cockpit's existing `[[wikilink]]` rendering will leave anchors in
the mounted HTML pointing at `/docs/<path>`. TASK-0071 intercepts
those. Until then, clicking such a link will likely do nothing
(no default browser to open) — that's fine for the mid-task
state.
