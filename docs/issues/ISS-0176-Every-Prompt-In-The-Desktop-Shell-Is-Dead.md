---
type: "[[issue]]"
id: ISS-0176
aliases: ["ISS-0176"]
title: "Every `window.prompt` in the renderer is dead in Electron, so five controls across four shipped features do nothing when clicked — drafting a release, reconciling a criterion, filing an issue from a failure, and annotating a design"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-16
review_verdict: approved
source: ["Edwin 2026-08-16: 'the prepare button is not working'", "The app's own log, five times over — one per click"]
severity: high
component: desktop-renderer
parent: ""
related: ["[[FEAT-0063]]", "[[FEAT-0106-The-Release-Page]]", "[[PHASE-024-Acceptance-Witnessed]]", "[[PHASE-025-Design-Before-Code]]"]
tests: []
---

# Every prompt in the desktop shell is dead

## Problem

Electron removed `window.prompt` in v3. This app is on **32**. The renderer calls it five times, and the running app says so in as many words:

```
[renderer e] Uncaught (in promise) Error: prompt() is and will not be supported.
```

Five occurrences in the log — one per click, because Edwin pressed the button five times before reporting it.

| call site | control | shipped by |
| --- | --- | --- |
| `renderer.ts:6863` | Prepare release | today, [[FEAT-0105]] |
| `renderer.ts:15341` | **"Title for the release note?"** — the Draft release button | [[TASK-0316]] |
| `renderer.ts:16107` | **"Why is this criterion reconciled rather than met?"** | [[FEAT-0063]] |
| `renderer.ts:16117` | **"What failed?"** — files a pre-linked issue | [[FEAT-0063]] |
| `renderer.ts:16325` | Design annotation comment | [[PHASE-025]] |

## Why it went unnoticed

`window.prompt` works in **mode 1**, the browser cockpit. The desktop shell is where Edwin actually works, and there the call throws before anything is sent. Every one of these features has tests — on the payload, the write path and the endpoint — and none of them presses the button. The control is the one link in the chain no test touches and the only one a person uses.

So four features reached `done` with a dead control at the end of them: drafting a release ([[TASK-0316]]), two of the acceptance runner's three outcomes ([[FEAT-0063]], inside [[PHASE-024]] *"Acceptance witnessed"*), and annotate-to-request ([[PHASE-025]]).

## Expected

1. `window.prompt` appears **nowhere** in the renderer.
2. One in-page input, used by all five, so the next one cannot be written the broken way by copying a neighbour.
3. A guard that fails if `window.prompt` reappears — the mechanism is unavailable, not merely discouraged.


## Fixed 2026-08-16

One `askForText` component, five call sites converted, and `window.prompt` gone from the renderer. `test_the_renderer_never_calls_window_prompt` fails if it returns — the mechanism is unavailable now rather than discouraged, which a comment would not have achieved.

The four pre-existing conversions keep their endpoints, payloads and refusals; only the way the text is collected changed. Two of them gained a multiline field, which they should always have had — *"why is this criterion reconciled rather than met?"* is not a one-line question.
