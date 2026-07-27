---
type: "[[task]]"
id: TASK-0215
aliases: ["TASK-0215"]
title: "Design render surface — real viewport, live reload, sandboxed"
status: backlog
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["user request 2026-07-27"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "M"
depends: ["[[TASK-0214]]"]
blocks: ["[[TASK-0217]]"]
related: ["[[REQ-0022-Overview-State-Above-History]]"]
tests: []
---

# Design render surface

## Definition of Done

- [ ] A design artifact renders in a dedicated surface, framed at a selectable viewport
- [ ] Viewport presets include **900px height** — the size [[REQ-0022]] is written about; a design reviewed at another size is reviewed against the wrong question
- [ ] Editing the artifact updates the pane with no manual reload, through the existing watcher/SSE path
- [ ] The render frame is **sandboxed**: artifact HTML is treated as content, cannot reach the sidecar's mutation endpoints, cannot read the repo, and cannot navigate the shell
- [ ] [[DES-0001]]'s real 139KB dossier renders correctly — the acceptance subject is the existing artifact, not a fixture
- [ ] A design with no `asset:`, or a missing file, degrades with a message rather than a blank pane

## Steps

- [ ] Serve artifacts from a dedicated read-only route, separate from `/api/render`
- [ ] Build the surface with the viewport switcher
- [ ] Wire the watcher so an artifact edit pushes an SSE reload for that surface only
- [ ] Sandbox the frame; write a test asserting a script in an artifact cannot reach a mutation endpoint
- [ ] Render DES-0001 and check it against the artifact opened directly in a browser

## Notes

The sandbox requirement is not paranoia about your own files. Today's runner work produced three separate silent-failure traps, and the general lesson held each time: content that arrives from a generator is content, not code, however trustworthy its origin. An artifact is authored by an agent; the frame should assume nothing about it.

Live reload is what makes this a *design loop* rather than a viewer. The watcher and SSE already exist for notes — this is a second subscriber, not new infrastructure.
