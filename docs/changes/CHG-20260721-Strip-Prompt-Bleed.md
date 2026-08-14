---
type: "[[change]]"
id: CHG-20260721-Strip-Prompt-Bleed
title: "Agent strip clears sticky prompt/work state on workspace switch — no cross-project prompt bleed"
date: 2026-07-21
author: user:edwin
status: merged
related: ["[[ISS-0015]]", "[[TASK-0184]]", "[[FEAT-0030]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-21
review_verdict: ""
---

# CHG-20260721 — clear sticky agent-strip state on workspace switch

## What changed

`openWorkspace` in `desktop/src/renderer/renderer.ts` now clears `stripLastPrompt = ''` and `workTransitions.clear()` in the same reset block that already drops `lastAgentSnap` and calls `showAgentStrip(null, null)` on a workspace switch.

## Why

After switching to a workspace, the agent-state strip at the top of the console showed a prompt that belonged to a *different* project (user report 2026-07-21: project-os-dev's prompt appearing under project-os-cockpit). `stripLastPrompt` is a module-level string that `showAgentStrip` only ever assigns (from the live activity prompt or the session's `last_prompt`); it is intentionally sticky so the strip keeps showing what the agent last did between runs within a workspace. But the switch reset cleared `stripSession` (via `showAgentStrip(null, null)`) without clearing `stripLastPrompt`, so when the newly-active workspace's session carried no `last_prompt` of its own, the strip fell through to render the previous workspace's prompt. The `workTransitions` map (backing the session "work" tab) is the same leak class.

## Impact

- **Behaviour**: switching workspaces starts the strip clean; it only ever shows the active workspace's own prompt / touched notes. Sticky-within-a-workspace behaviour (prompt persists across a session ending) is unchanged — only cross-workspace carry-over is removed.
- **Scope**: renderer-only; requires a desktop rebuild (`npm run build`) — done, `tsc` clean.
- **Verification**: manual/CDP — switch from a workspace with an active-prompt session to one whose session has no `last_prompt`; the first workspace's prompt no longer appears. (No renderer unit-test harness exists; the change is a two-line state reset in the existing switch-reset block.)

## Files

- `desktop/src/renderer/renderer.ts` — `openWorkspace` resets `stripLastPrompt` and `workTransitions` on switch.

## Review verdict cleared — 2026-07-30

`review_verdict` read **`CLOSE`**, which is not a value QUALITY.md defines (`approved` | `changes-requested`). Cleared per [[ISS-0069]], on the principle that a verdict nobody can interpret is not a verdict and should not satisfy a gate.

**What is deliberately kept:** `reviewed_by: "opus-independent-review"` and `review_date`. A review demonstrably happened, by a named reviewer, on that date — that is real information and clearing it would destroy evidence rather than correct a claim. Only the uninterpretable value is gone.

The consequence is intended: this note is now `merged` without a verdict, so [[project-os-dev#ADR-0011]]'s REVIEW warning applies to it like anything else unreviewed, with the same 2026-10-23 deadline. It joins an honest backlog instead of reading as a satisfied gate.
