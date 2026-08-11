---
type: "[[issue]]"
id: ISS-0140
aliases: ["ISS-0140"]
title: "Nothing says the Electron shell is running old code — the sidecar's staleness trap has a twin in the renderer, and it cost a false observation twice"
status: fixed
severity: medium
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
phase: "[[PHASE-026-The-Returning-Human]]"
features: ["[[FEAT-0007]]", "[[FEAT-0018-Verification-Health]]"]
tasks: []
related: ["[[REL-0001-The-Human-Has-Levers]]", "[[ISS-0130]]", "[[TST-0011]]"]
tags: [issue, staleness, desktop]
---

# The shell goes stale silently

## What happened, twice

**2026-08-11, walking [[REL-0001]]'s check 1.10.1** against the running app: the workspace dot and the activity strip behaved exactly as the check describes. The third clause — *"the notes it touches show the agent chip"* — did not. Two `nav-agent-chip`s sat on FEAT-0087 and TASK-0385 across polls minutes apart, neither touched by the session, while a real edit to a note whose row was visible produced none.

Before filing that as a defect, the process was checked:

```
Electron shell started  Sun 9 Aug 19:46      elapsed 01-23:02
```

**1 day 23 hours.** Its renderer bundle predates every session that touched this code. So the observation says nothing about today's build, and the finding is *"the app is old"*, not *"the chip is broken"*.

**This is the second time in two days.** The release note already records the first: a Python sidecar running since 2026-08-09 19:47 against code from 2026-08-10 20:48, which produced **two bug reports that were not bugs** — a Tests view that appeared to show phases, and tasks that appeared to be missing.

## Why it is worth an issue rather than a habit

Both times the cost was the same and it was not the stale code: it was **hours spent investigating a defect that did not exist**, then having to distrust the observation afterwards. On the one repo whose code *is* the cockpit, the developer reads today's record through a tool built two days ago and nothing on screen says so.

The record already states the mechanism: *"sidecars are an editable install, so they need no rebuild — but a running process never re-imports, and the SSE soft-reload refreshes documents only, never Python modules."* The renderer has the same shape with a different cause: `dist/renderer/*.js` is loaded once at window creation and the shell does not reload it when `npm run build` rewrites the files underneath.

**Nothing restarts either, and nothing says either is stale.**

## What would fix it

The cheap, honest version: **the shell knows when it was started and the bundle knows when it was built.** If the newest `dist/renderer/*` mtime is later than the window's creation time, say so — one line on the health surface, in the same voice as `validator: N errors`. The same comparison works for the sidecar against `src/project_os_cockpit/*`.

Deliberately **not** an auto-reload: reloading a window under someone mid-session is worse than telling them. The obligation vocabulary already has a place for *"a thing you should do"*, and this is one.

## Verification

Start the shell, rebuild the renderer, and expect the health surface to say the running window is behind — without restarting anything to find out.

## Homed with the surface it changed

Filed under [[PHASE-999]] at `triage` — no scheduled home — and **re-homed to [[PHASE-026]] on being fixed**, the phase whose subject is *the returning human*: somebody coming back to a window that has been open for two days is exactly who this line is for. `test_no_terminal_note_sits_in_the_parking_lot` caught the parking-lot residue within a minute of the status changing, which is the second time today that check has done its job.

## Fixed — 2026-08-11

**`GET /api/cockpit/runtime`** answers the comparison rather than leaving it to memory: when this process started, the newest mtime under the package, whether that makes it stale, and the newest mtime under the shell's asset directory when one was passed. The sidecar's own answer needs no client help; the window's does, because only the window knows when it read its bundle — `performance.timeOrigin`, which *is* that moment.

The Verification card gains one line when either is behind, in the voice it already uses for `validator: N errors`:

> *sidecar and window are older than the code — restart to trust this*

It names **which**, because the two need different actions: a sidecar comes back on reopen, a window needs relaunching.

**Reports, never reloads**, and that is a decision rather than an omission. Reloading a window under someone mid-session is worse than the staleness it fixes — the reader loses their place to solve a problem they had not noticed. This is an obligation they discharge.

## What the tests hold

`tests/test_runtime_freshness.py` drives a real server rather than mocking a clock: the comparison is between a *process* and a *filesystem*, and mocking either end would test the arithmetic instead of the question.

- A fresh process is **not** stale — the case that must not cry wolf.
- A source file touched into the future **is** stale, and **clears again** when the touch is undone. A staleness signal that latches is a signal people learn to stop seeing, which is how the surface got here.
- No `--shell-assets` still answers, so a client can tell *no assets* from *assets are current* without special-casing a missing key.

Suite 1152 → 1156.

## What it does not do

It does not make the two remaining acceptance checks (1.9.1, 1.10.1) walkable — those still need an agent CLI started in the app's own terminal. What it does is make the answer **trustworthy when they are walked**: the surface will say if the window is behind, instead of leaving it to somebody remembering to check `ps`.
