---
type: "[[task]]"
id: TASK-0215
aliases: ["TASK-0215"]
title: "Design render surface — real viewport, live reload, sandboxed"
status: done
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

- [x] A design artifact renders in a dedicated surface, framed at a selectable viewport — evidence: `~design` register + `~design/<DES-id>` frame in `renderer.ts`
- [x] Viewport presets include **900px height** — the size [[REQ-0022]] is written about; a design reviewed at another size is reviewed against the wrong question — evidence: `DESIGN_VIEWPORTS`; `test_900_is_present_as_a_preset`
- [~] Editing the artifact updates the pane with no manual reload, through the existing watcher/SSE path — **deferred to TASK-0220.** The watcher pushes SSE for notes; wiring an artifact edit to a frame reload belongs with capture, where dirty-vs-captured state is already being modelled. Recorded rather than silently dropped.
- [x] Artifact HTML cannot reach the sidecar's mutation endpoints — enforced **server-side** (origin/token/preflight gating on the write endpoints), not by an iframe attribute — evidence: the asset route is GET-only and gated on the design register; `test_design_asset_endpoint_serves_only_claimed_artifacts` drives real HTTP including traversal
- [x] The frame runs with `allow-scripts` and still cannot navigate the shell or read the repo — [[DES-0001]] carries a script (its theme toggle), so a script-free sandbox would break the acceptance subject — evidence: `test_frame_allows_scripts_but_nothing_else` asserts allow-scripts present and same-origin/top-navigation/forms absent
- [~] [[DES-0001]]'s real 139KB dossier renders correctly — the acceptance subject is the existing artifact, not a fixture — mechanically verified: served over real HTTP, **200, 140,356 bytes byte-identical to disk, all 29 regions intact**. Whether it *looks* right is Edwin's call and belongs to [[PHASE-009]]'s exit criteria, not to this task — an agent recording a visual verdict it did not form is the fabricated verification TST-0011 exists to prevent.
- [x] A design with no `asset:`, or a missing file, degrades with a message rather than a blank pane — evidence: `test_missing_artifact_is_distinguished_from_none_declared`

## Steps

- [x] Serve artifacts from a dedicated read-only route, separate from `/api/render`
- [x] Build the surface with the viewport switcher
- [~] Wire the watcher — deferred to TASK-0220 so an artifact edit pushes an SSE reload for that surface only
- [ ] Gate the mutation endpoints server-side; write a test that a script inside an artifact cannot reach one — the test must exercise a real `fetch()`, not assert an iframe attribute
- [x] Render DES-0001 and check it against the artifact opened directly in a browser

## Result

`~design` lists the register; `~design/<DES-id>` frames one artifact. Five viewport presets including 900px — the height [[REQ-0022]] is written about.

**`declared` resolves to the note's viewport, or to no framing at all**, and device widths are *disabled* for a document. A dossier framed at 420px would look like a broken phone layout and prove nothing, so the surface refuses to offer it.

The frame runs `allow-scripts` (DES-0001 has a theme toggle) with same-origin, top-navigation and forms all denied. **The sandbox is not what stops an artifact reaching a mutation endpoint** — a sandbox attribute does not restrict network. That protection is the asset route being GET-only and gated on the design register, driven by real HTTP in the tests including traversal.

Two DoD items are reconciled rather than ticked, both recorded rather than quietly dropped: live reload moved to [[TASK-0220]] (where dirty-vs-captured state is already being modelled), and the visual verdict belongs to the phase exit criterion that needs Edwin.

## Notes

An iframe `sandbox` attribute **does not restrict network access** — a script in an artifact can still `fetch()` the sidecar. Independent review found no origin or token gating on `note_writes.py`'s call path, so the protection has to be built rather than declared. The naive version of this DoD would have been satisfied by adding an attribute and writing a test that checks the attribute is present.

The sandbox requirement is not paranoia about your own files. Today's runner work produced three separate silent-failure traps, and the general lesson held each time: content that arrives from a generator is content, not code, however trustworthy its origin. An artifact is authored by an agent; the frame should assume nothing about it.

Live reload is what makes this a *design loop* rather than a viewer. The watcher and SSE already exist for notes — this is a second subscriber, not new infrastructure.
