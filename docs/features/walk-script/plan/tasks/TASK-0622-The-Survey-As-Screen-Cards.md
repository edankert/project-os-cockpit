---
type: "[[task]]"
id: TASK-0622
aliases: ["TASK-0622"]
title: "The walk page's survey renders one card per changed screen: its name, each change's rider-facing sentence, and the before and after captures side by side, with no test id"
status: backlog
phase: "[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]", "project-os-dev ADR-0045 decision 1"]
parent: "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]"]
related: ["[[TASK-0620-The-Survey]]", "[[FEAT-0148-One-HTML-Viewer]]", "[[FEAT-0147-Pictures-Beside-The-Note]]"]
tests: ["[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]"]
tags: [task, acceptance, publication, renderer]
---

# The survey as screen cards

## Why

Edwin's first step on a release is to look at the screens that changed. The survey [[TASK-0620-The-Survey]] built lists surfaces with invalidating task ids and quoted "Acceptance checks reopened" sections. After project-os-dev TASK-0118 the payload carries screens, sentences and capture paths instead. This task draws them.

## Definition of Done

- [ ] `acceptance.walk_payload` passes through the bundled module's new survey structure unchanged: surface id, title, parent, sentences with their change ids, before capture path, after capture path, and a "new" flag.
- [ ] Each changed screen renders as a card. Children render inside their parent's card.
- [ ] The before and after images sit side by side at the same width. A card with only an after image says "new". A card with neither shows its sentences only.
- [ ] Images are served through the existing framed viewer route, confined to the workspace's `docs/` or the capture directory the consumer declares. No new route reads outside a workspace.
- [ ] The survey DOM contains no `TST-` string. A test asserts it.
- [ ] The line saying no release tag was found renders when the payload says so.
- [ ] Built and tested against a fixture repo before real captures exist.

## Notes

- The change ids behind each sentence can link to the change note. That is not a test id.
- Where captures live in your-trainer is its TASK-0904's open question. Read the path from the payload; do not assume a directory.
