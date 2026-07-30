---
type: "[[feature]]"
id: FEAT-0051
aliases: ["FEAT-0051"]
title: "Validator errors are session work while a session is running, and issues once it ends"
status: done
phase: "[[PHASE-016-Errors-Become-Work]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30, on the TASK-0250 rail badge: 'it was very difficult for me to understand what these errors were related to'"]
goal: "Show each validator error as a row in the running session's work list, closing as the agent fixes it, and file whatever survives the session as a real issue at close-out — so a validator result is always either work in progress or a record, never a standing number with nothing behind it."
requirements: []
tasks:
  - "[[TASK-0252-Validation-Errors-Reach-The-Session-Panel]]"
  - "[[TASK-0253-Error-Rows-In-The-Session-Summary]]"
  - "[[TASK-0254-Close-Out-Files-What-Survives]]"
release: ""
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[FEAT-0028-Fleet-Health-Surface]]", "[[FEAT-0020-Agent-Activity-Strip]]"]
tests: []
---

# Validator errors as session work

## Goal

The rail badge ([[TASK-0250]]) reports a count and nothing else. The place that explains a count — the drift panel from [[TASK-0112]] — exists only in the browser client, so in the desktop shell the number is unreachable. And most of what it counts, while a session is running, is that session's own half-finished work.

This feature puts the errors where the work is: **rows in the session summary panel**, above the console, in the same grammar the work rows already use — a square that fills when the item completes. You watch the list drain as the agent fixes things.

What the agent could not fix is, by that fact, what needs a person. At close-out it becomes an `ISS-*` note and joins the Issues view, where it can be prioritised, assigned and closed like anything else.

## Brief plan

1. **Get the errors to the renderer** ([[TASK-0252]]). The endpoint and the `cockpit:validation` SSE event already exist from [[FEAT-0018]] and the renderer already holds an `EventSource` on the sidecar — it just never subscribed to that event.
2. **Render them as rows** ([[TASK-0253]]) in `#agent-strip-detail`, closing as they resolve, each navigating to the note it names.
3. **File the survivors** ([[TASK-0254]]) — a close-out step, plus dedup so a recurring error updates one issue rather than minting a new one each session.

## Acceptance

- With a session running, inducing a validator error adds a row to the session summary within the debounce window; fixing it resolves the row, both without a reload.
- A row for an error naming a note navigates to that note.
- Close-out files what is still standing, and re-running it does not file the same thing twice.
- With no session running, nothing changes: the rail badge behaves exactly as it does today.

## Scope

- In: the desktop shell's session summary panel; the close-out step and its guard.
- Out: auto-filing in the background (declined — see [[PHASE-016]]); changing any validator rule; the browser client, which already has the drift panel.


## Done 2026-07-30

All four acceptance criteria verified against the running app, inducing real validator errors rather than synthetic payloads.

1. **An error adds a row while a session runs** — creating a bad note produced `COUNTER` and `METRICS` rows within the debounce window, over SSE.
2. **Fixing it resolves the row, no reload** — deleting the note flipped both to `fixed`, and the heading from *"2 to fix"* to *"all cleared"*.
3. **A row navigates** — clicking the `COUNTER` row went from `~overview` to the offending note.
4. **Nothing files twice** — dedup on `(code, subject)`, stated in the close-out rule and guarded.

`METRICS` correctly renders as **not** clickable: it is snapshot-level and names no note, and says so in its tooltip rather than offering a dead click.

## What the badge means now

For the repo you are working in, the errors are in the panel, so the pill is redundant while a session runs. For a repo with **no** session nobody is typing — so anything the pill shows there has already survived a session by definition. It stops meaning "something might be mid-edit" and starts meaning "this project has something nobody is fixing", which is worth a mark on the rail.

That was a consequence of Edwin's design rather than a goal of it, and it is the part that makes the rail badge honest.

## Owed

- The upstream half: whether the template should carry "fixed or filed" for every repo. Filed in `project-os-dev`.
- The `~agents` roll-up still shows counts only for cold repos. Unchanged and still correct — a repo nobody is in has no session panel to put rows in, and the pill plus the roll-up already say which repo. Reaching the detail there still means opening the workspace.
