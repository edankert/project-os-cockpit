---
type: "[[task]]"
id: TASK-0441
aliases: ["TASK-0441"]
title: "The release page, and an input that works — the centre pane acts, and `window.prompt` leaves the renderer for good"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0106]]", "[[ISS-0176]]"]
parent: "[[FEAT-0106-The-Release-Page]]"
effort: L
depends: ["[[TASK-0440-The-Release-Payload]]"]
blocks: []
related: ["[[ISS-0176-Every-Prompt-In-The-Desktop-Shell-Is-Dead]]"]
tests: ["[[TST-0033-The-Release-Page]]"]
---

# The release page, and an input that works

## Definition of done

- [ ] `~release/next` and `~release/<id>` render in the centre pane; the navigator rows link to them
- [ ] The version field and `Start` live on the page; no dialog anywhere in the flow
- [ ] A refusal is shown **on the page**, next to the field that caused it, not in a toast that vanishes
- [ ] One reusable in-page input replaces **all five** `window.prompt` call sites ([[ISS-0176]])
- [ ] `window.prompt` appears nowhere in `renderer.ts`, and a guard asserts it
- [ ] The four pre-existing conversions keep their existing behaviour otherwise — same endpoints, same payloads, same refusals
- [ ] Walked by hand in the app: start a release, see the page update, and reach the suite from the gate
