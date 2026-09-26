---
type: "[[task]]"
id: TASK-0157
aliases: ["TASK-0157"]
title: "Seen-acknowledgement — pulse means unseen; focusing the workspace calms it to static"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0030"
effort: ""
due: ""
depends: ["[[TASK-0147]]"]
blocks: []
related: []
tests: []
---

# TASK-0157 — seen-acknowledgement

No surface distinguishes "unseen alert" from "known-and-pending": pulses run until the next hook event or the 10-minute decay regardless of the user looking. Add a renderer-side `ack` map keyed on `(workspaceId, state-ts)`: when the workspace is active, the window focused, and the terminal visible for ~2s, mark acknowledged — pulsing animations stop (rail dot pulse, needs-input square ring, attention-panel row emphasis) while colour is kept. New state timestamp ⇒ new alert ⇒ pulse resumes. Purely visual — state data, decay, and notifications unchanged. Verification: trigger needs-input, focus the workspace ≥2s → pulse stops, colour stays; new event re-pulses; unfocused workspaces keep pulsing.
