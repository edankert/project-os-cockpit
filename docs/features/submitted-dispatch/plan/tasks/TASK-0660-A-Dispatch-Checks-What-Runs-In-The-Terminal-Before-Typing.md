---
type: "[[task]]"
id: TASK-0660
aliases: ["TASK-0660"]
title: "Before a dispatch types anything, the shell asks tmux what program runs in the project's terminal, and only a shell gets a shell command"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[ISS-0322-Codex-In-A-Cockpit-Terminal-Reports-Nothing-To-The-Sidecar]], proposed fix 1", "[[ISS-0321-The-Dispatch-Agent-Is-Chosen-By-Hand-Not-From-The-Running-Agent]]", "Edwin 2026-10-14: 'yes, implement both parts'"]
parent: "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
effort: "S"
due: ""
depends: []
blocks: []
related: ["[[TASK-0661-Every-Project-Uses-One-Codex-Hook-Command]]"]
tests: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"]
---

# A dispatch checks what runs in the terminal before typing

TST-0095 steps 9 and 10 typed `claude '<prompt>'` and `codex '<prompt>'` into a running Claude and a running Codex. The cockpit had no session for either (the kill switch; a Codex nobody had prompted, whose `SessionStart` waits for the first turn), and `routeFor` in `desktop/src/ipc/dispatch-queue.ts` reads "no session" as "a shell is waiting".

## What changes

- `terminal.ts` gains `foregroundCommand(workspaceId)`: tmux's `#{pane_current_command}` for the project's session, or node-pty's process name without tmux, or `null` when there is no terminal or it cannot be read.
- `dispatch-queue.ts` classifies it: a shell (`zsh`, `bash`, `sh`, `fish`, `dash`, `ksh`, `tcsh`), `codex`, Claude (`claude`, or a bare version number such as `2.1.299`, which is how Claude Code names its process), or something else.
- `routeFor` takes the classification. A live Claude session with a plugin is unchanged: it gets a delivery. Otherwise, when no turn is running:
  - a shell gets `<agent> '<prompt>'`, as now;
  - Codex gets the prompt pasted and a separate Return, whether or not it has reported to the cockpit yet;
  - Claude that the cockpit cannot reach (no plugin, or the kill switch) is held in the queue with "Claude is running in this terminal but the cockpit cannot reach it";
  - anything else, or a terminal that cannot be read, is held with what is running.
- The prompt goes to the agent that is running. The ledger names that agent, and the "sent there instead of" warnings go: following the running agent is the rule now (ISS-0321). The Agent menu only says which agent to start when none runs.

## Known risk

A Codex that has just started may still show a startup dialog, such as its hook review or the project-trust question. A pasted prompt and Return would land in that dialog. Nothing the cockpit can read tells the composer from a dialog before Codex's first turn. TASK-0661 makes the hook review a once-only event, which narrows this.

## Definition of Done

- [x] Unit tests for the classification and for every `routeFor` row, including a running Codex with no session and a running Claude with no session.
- [x] A test through the built `dispatch-queue.js`: with the terminal's foreground program reported as Codex and no session, the prompt is pasted and Return sent separately, and `codex '` is never written; with Claude and no session, nothing is written and the item stays queued.
- [x] The desktop suite passes; `tsc` is clean.
- [x] TST-0095 steps 9 and 10 say what now happens.

## Result, 2026-10-14

- `terminal.ts`: `foregroundCommand` reads `#{pane_current_command}` with `tmux display-message`, or node-pty's `process` without tmux.
- `dispatch-queue.ts`: `classifyForeground` and a three-argument `routeFor`. A held dispatch goes back to the front of the queue with the reason as its warning, and the poller offers it again about every five seconds while the project is idle or waiting, so a Codex or shell that is still starting gets it once it is up. The "sent there instead of" warnings are gone; a pasted prompt's ledger entry says `agent: codex`.
- Tests in `desktop/tests/submitted-dispatch.test.mjs`: an unprompted Codex gets a paste and never `codex '`; an unreachable Claude is held with nothing written; `vim` and an unreadable terminal are held; a shell beats a stale Codex session; the classification; and the routing table. With unknown programs sent back to the shell route, three of them fail. `codex-dispatch.test.mjs`'s stand-in terminal gained `foregroundCommand`.
- Desktop suite: 210 passed. `tsc` clean.

Not seen in the running application yet; that is TST-0095 steps 9 and 10.
