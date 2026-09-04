---
type: "[[reference]]"
id: REFERENCE-FUNCTION-HOOKS-REVIEW
title: "Claude Code Function Hooks (issue #91870): what it would change for project-os and the cockpit"
status: active
owner: user:edwin
created: 2026-09-04
updated: 2026-09-04
scope: "project"
source:
  - "https://github.com/anthropics/claude-code/issues/91870"
  - "https://github.com/user-attachments/files/31802150/EXTERNAL.Function.Hooks.Core.Architecture.pdf"
related:
  - tools/instructions/HOOKS.md
  - tools/adapters/claude-code/ADAPTER.md
---

# Claude Code Function Hooks — review

## Purpose

Anthropic is asking whether to ship "function hooks", a fifth hook type for Claude Code plugins. This note records what the proposal says, which of this repo's current workarounds it would remove, and what it would not fix. Read it when the proposal ships, is closed, or when anyone proposes reshaping `tools/adapters/claude-code/hooks/`.

**Nothing here is a recommendation to change code now.** The proposal has no ship date and may not ship at all.

## What was proposed

Alice Poteat (Anthropic) opened [issue #91870](https://github.com/anthropics/claude-code/issues/91870) on 2026-09-03, titled "Function Hooks - make plugins 10x more powerful". It had 89 comments when this note was written. The issue states its own status plainly: "the response from the community likely dictates whether this ships or not." A linked 8-page PDF, *Function Hooks: Core Architecture*, carries the design.

A plugin's `hooks/hooks.json` gains one key, `modules: ["./my-hooks.ts"]`, naming a TypeScript file beside it. That file exports `register(on)`, and each hook has the signature `($, e, next)`. Hooks compose like Koa middleware: registration order is nesting, so the first plugin registered wraps every later one, and an administrator controls behaviour by deciding which plugins go first.

Three properties matter more than the syntax.

**`$` is the only door.** The environment running a plugin's hooks has no ambient filesystem and no network. Every effect is a call of the form `$.noun.event(input)`, and every method on `$` is itself a hookable event. What a plugin did is therefore exactly the calls it made, and `claude plugin validate` can list a plugin's events before any hook runs.

**Drawing is an event.** `ui.render` carries `e.component`, `e.props` and `e.surface` — `"terminal"`, `"desktop"`, or an artifact's own. A hook rewrites the props before rendering, wraps the returned node after, or replaces it outright. Buttons drawn this way report presses as `ui.press`, addressable by `{ plugin, element }`, and the same hook catches a press in the terminal and in the desktop app.

**One hook on `*` sees every event**, including the calls other plugins make on `$`. The PDF's audit-log example is four lines.

## What it would change for project-os

This repo implements the eight `HOOKS.md` contracts as 626 lines of POSIX shell plus one Python file under `tools/adapters/claude-code/hooks/`. Four costs in that design are structural rather than careless, and the function model removes them.

**The session marker file stops being necessary.** `close-out-check.sh` needs to know whether the session wrote anything since its last block. A `PostToolUse` process and a `Stop` process share no memory, so the answer travels through a file, and the path formula is factored into `hooks/shared/session-marker.sh` so both scripts agree on it. Inside one hooks-module that flag is a closure variable. The file goes, and so does the class of bug where two scripts disagree about a path.

**Pre and post collapse into one function.** `hooks.json` registers `document-first-gate.sh` and `verification-gate.sh` on `PreToolUse`, then `phase-alignment.sh` and `risk-scan-trigger.sh` on `PostToolUse`, all four matching `Write|Edit`. §2.2 of the PDF names this directly: `before` is your work then `return next(e)`, `after` is `await next(e)` then your work. Four scripts become one function on one event.

**Blocking gets a type.** A gate blocks today by printing `{"decision": "block", ...}` on stdout, so a malformed pipeline yields a hook that silently allows everything. That is not hypothetical. The comment at `tools/adapters/claude-code/hooks/close-out-check.sh:83` records that `echo "" | jq -r --arg f ... '$f'` never ran its filter, which meant the close-out hook never blocked at all until a test caught it. `return { deny: "..." }` is a return value a compiler checks.

**Advisory hooks would stop paying context rent.** This is the most valuable change for project-os. HC-008's delegation hint is capped at three lines and 600 characters, and `tools/scripts/test-hooks.sh` asserts the cap, because the hint is injected into the prompt and competes with everything else for the model's context. But the hint is written for the human: Edwin is the one who decides whether to route to the `planner` subagent. `phase-alignment.sh` and `risk-scan-trigger.sh` have the same shape — warnings for a person, delivered as tokens the model reads. Drawn through `ui.render` they would sit beside the prompt at no token cost and with no length cap.

**The validator would stop spawning a subprocess on every stop.** `close-out-check.sh` execs `validate-docs.sh` at each `Stop`, which re-reads and re-parses the whole snapshot and note tree. A resident hooks-module can hold that parse and drop it when a write event fires.

## What it would change for the cockpit

The cockpit instruments a Claude Code session by writing six files per workspace: a fabricated zdotdir whose `.zshrc` sources the user's real one and wraps `claude` in a shell function, a generated `claude-settings.json` carrying ten command hooks, `hook-forward.sh`, `statusline.sh`, `codex-notify.sh`, and a `hook-env` rewritten whenever the sidecar respawns (`desktop/src/ipc/agent-instrument.ts:1-30`). All six exist to move events from the CLI into `/api/agent-hook`. A plugin is one install, and since `$` carries the network, the sidecar URL becomes plugin `userConfig`. RISK-0004's rule — never write into the user's `~/.claude` — would then hold by construction rather than by generating a parallel config tree.

Three workarounds in this repo are direct consequences of command hooks, and each names its own cause in the code.

**The statusline is being used as a telemetry channel.** No event carries cost, context or rate limits, so the cockpit hijacks the statusline command, debounces it to one POST every five seconds, and echoes a status string back so the terminal still works. `agent_hooks.py:7` calls `Statusline` a "cockpit-defined" event, which is an honest way of saying it was invented because none existed. A hook on `*` reads whatever the engine actually knows.

**A two-second dedup window cancels a duplicate capture path.** A cockpit terminal session that also has the user's opt-in external hook enabled fires both paths, posting the same payload about 100 milliseconds apart, so `agent_hooks.py:60-67` drops identical `(session, event, payload)` tuples inside a 2s window. One plugin registered once has one path. (Two plugins could still duplicate; this removes the cause we actually have.)

**Dispatch is a robot typing into a terminal.** `desktop/src/ipc/dispatch-queue.ts:189` delivers a queued prompt as `item.prompt + '\r'` written into the pseudo-terminal. It works, and it is also why a dispatch cannot be confirmed, cancelled, or distinguished from a human keystroke.

The largest gap is permission prompts, and `approvals.py` states it in its own docstring: the cockpit detects `PermissionRequest` and shows an amber card, but answering still means finding the terminal and typing, and nothing survives a restart. It goes further. FEAT-0076's promise is that nothing waits silently without bound; every mechanism enforcing that promise watches the review queue; a tool-permission prompt is not a queue entry. So the most likely way an unattended worker stops — the agent asking whether it may run a command — is precisely the way the stall alarm cannot see.

Function hooks close that gap. A hook can return a decision for the permission event, and `on("ui.press", { component: "AskUserQuestion" })` reaches the real prompt on both surfaces. The cockpit's approve and deny buttons would *be* the answer rather than a simulation of one, and the answer would pass `delegation.py`'s policy check on the way through, which keystroke injection can never do.

Separately, `ui.render` with `e.surface` would let the cockpit draw the focus item, its phase and any open obligations inside the Claude Code window, rather than only in a separate Electron window the terminal knows nothing about.

## What it does not fix, and what it costs

**A file written through Bash stays invisible.** The gates match `Write|Edit`, so a file changed by `sed -i` inside a Bash call trips neither HC-001 nor HC-006's recorder. This is live, not theoretical: a session configured to prefer Bash for file edits runs with both hooks effectively off. A `*` hook at least sees every tool call in one place and can classify commands, but no hook can observe what a subprocess did to the disk. Closing that gap needs a different mechanism.

**Portability gets worse.** `HOOKS.md` is built on tool-agnostic contracts with per-tool adapters, and the Codex, Cursor and generic paths already implement only a subset, in prose. A TypeScript and React engine interface is the least portable adapter surface yet, so adopting it widens the distance between the Claude Code path and the others. That matters here because `tools/` syncs to twelve fleet repos, none of which needs a Node toolchain today.

**Recursion is skipped silently.** PDF §6.4: a hook is never re-entered while its own frame is dispatching. An audit hook on `*` therefore does not see its own calls on `$`. Harmless once known, confusing if not.

**Trust moves rather than disappearing.** `agent_hooks.py` treats every payload as untrusted because any local process can POST to the sidecar. A plugin talks to the engine instead of an open localhost port, which is an improvement, but it relocates the question to which plugins are installed and in what order.

## What to do

Nothing in this repo. The proposal may not ship, and reshaping the adapters against an unshipped design would be building on sand.

The useful action is to comment on the issue, because this repo is an unusually good witness: it holds two working examples of inventing a channel because none existed. The two asks worth making are a permission event a hook can resolve programmatically, and session cost and context as real events. Both are things the cockpit fakes today, with the code to show for it.

## Maintenance

Revisit when issue #91870 ships or is closed. If it ships, the concrete follow-ups are in "What it would change" above and should become `ISS-*` or a feature at that point, not before. If it is closed unshipped, mark this note `superseded` and keep it: the list of workarounds it catalogues is accurate regardless of what Anthropic decides, and it is the shortest existing statement of why they exist.
