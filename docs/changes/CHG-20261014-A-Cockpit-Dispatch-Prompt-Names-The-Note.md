---
type: "[[change]]"
id: CHG-20261014-A-Cockpit-Dispatch-Prompt-Names-The-Note
title: "A prompt sent with `cockpit dispatch` names the note's file and verb, an unknown ID is refused, and the note's history gets one entry, not two"
status: merged
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TASK-0663-A-Cockpit-Dispatch-Request-Names-The-Notes-File]]"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/server.py", "src/project_os_cockpit/agent_hooks.py", "desktop/src/renderer/renderer.ts", "tests/test_dispatch_ledger.py", "desktop/tests/delivery-row.test.mjs", "docs/reference/cockpit-capability-register.md"]
platforms: [macos]
issues: ["[[ISS-0320-A-Cockpit-Dispatch-From-The-Command-Line-Loses-The-Notes-Path]]"]
features: ["[[FEAT-0025-Dispatch-Runtime]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[CHG-20261014-A-Prompt-Dispatched-To-Claude-Is-Submitted-Not-Typed]]"]
---

# A cockpit dispatch prompt names the note

## Summary

`cockpit dispatch TASK-0084` now sends the same prompt as the note's Implement button: "Work on TASK-0084. Read docs/features/…/TASK-0084-….md first". Before, unless the quick switcher had been opened since the window loaded, it said "Read docs/ first".

## What a person notices

- **The prompt names the note's file**, whether or not the quick switcher has been opened.
- **The note's dispatch history names the verb**, for example `implement`, even when `--verb` was not given. It used to say "default".
- **One history entry per dispatch.** The request used to write its own entry, with no agent, beside the one the delivery writes.
- **A mistyped ID is refused.** `cockpit dispatch TASK-9999` prints "dispatch failed: no note with ID TASK-9999 in this project" instead of sending a prompt about a note that does not exist.

## How it works

The sidecar looks the ID up in the project's index when the request arrives and puts the note's docs-relative path on it. The window uses that path; it reads the quick switcher's list only for a sidecar too old to send one.

## What was checked

`.venv/bin/python -m pytest -q -p no:randomly` (2173 passed, 11 skipped) and the desktop node suite (215 passed). Not yet seen in the running application.
