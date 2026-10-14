---
type: "[[test]]"
id: TST-0094
aliases: ["TST-0094"]
title: "A Claude session in a cockpit terminal reports through the plugin, and your own status line is back"
status: active
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"]
scope: feature
level: acceptance
entrypoint: "A new cockpit terminal, then `claude`"
command: ""
last_verified: 2026-10-14
covers: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"]
issues: ["[[ISS-0319-Every-Cockpit-Terminal-Inherits-The-Environment-Of-The-Claude-Session-That-Started-Tmux]]"]
tasks: ["[[TASK-0651-The-Sidecar-Prefers-The-Plugin-And-CI-Checks-It]]", "[[TASK-0652-A-New-Cockpit-Terminal-Starts-Without-Another-Sessions-Variables]]"]
artifacts: []
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
review_round: ""
related: ["[[RISK-0004-Hook-Injection-Surface]]"]
area: ""
after: []
tags: [test, acceptance, cockpit-plugin, claude-code]
---

# A Claude session in a cockpit terminal reports through the plugin

## Purpose

Proves that a Claude session started in a cockpit terminal still lights the rail and the agent rows, and still shows cost, context and rate limits, now that it reports through the cockpit plugin instead of generated shell files. It also proves that your own Claude status line is drawn again, and that the kill switch still works.

Set to `active` on 2026-10-14, when the work was built. The plugin was tried in a real headless session and a real interactive session against a stand-in sidecar ([[CHG-20261014-Claude-Sessions-Report-Through-The-Cockpit-Plugin]], "What was checked"). It has not been run inside the cockpit application; this check is that run.

## Setup

The desktop application rebuilt from these sources (`npm run build` in `desktop/`) and restarted. A project whose cockpit terminal is new: if its terminal was open before the restart, close it with the terminal's restart button so its tmux session is created again. A terminal opened before the update keeps the old `claude` wrapper until it is closed, and does not test this change.

## Steps

1. Open the project's terminal in the cockpit and run `echo $CLAUDE_CODE_PLUGIN_DIRS`.
2. Run `claude`, and ask it to read one file and edit one note.
3. Watch the rail dot and the agent row while it works, and after it finishes.
4. Look below Claude's prompt box. That is where Claude Code draws a status line: the output of a command named under `statusLine` in your settings. Before this change the cockpit replaced it with its own.
5. Look at the cost, context and rate-limit figures for the session in the cockpit.
6. Exit Claude.
7. Quit the application, start it from a terminal with `COCKPIT_NO_INSTRUMENT=1`, open a terminal in a project whose tmux session you have closed, and run `echo $CLAUDE_CODE_PLUGIN_DIRS` and `claude`.

## Expect

- Step 1 prints a path ending in `desktop/plugin/claude-code`, after any value you set yourself, and only once.
- In step 2 Claude starts as it does in any other terminal; your `claude` alias, if you have one, applies. Claude asks nothing about a plugin.
- In step 3 the dot goes busy while Claude works and waiting when it finishes. The agent row shows the prompt, the tool and the file it edited.
- In step 4 there is no cockpit `model · $cost` line below the prompt. If you have set a status line of your own, it is drawn as usual; if you have none, Claude Code shows only its normal footer.
- In step 5 the figures appear after the first turn ends, and match what `/cost` and `/context` say in the session.
- After step 6 the session shows as ended.
- In step 7 the variable is empty, and the plugin reports nothing: the session has no `plugin_claimed` mark and no cost, context or rate-limit figures. If your own `~/.claude/settings.json` registers the cockpit's external hook (FEAT-0027), the session still appears, with its prompts only. That hook reports every Claude session on the machine, in or out of the cockpit, and the kill switch does not cover it.
- The instrument folder for the project (`$COCKPIT_INSTRUMENT_DIR` in the terminal, a folder under `~/Library/Application Support/project-os-cockpit-desktop/instrument/` named by a hash, not the project) gains no `claude-settings.json`, `hook-forward.sh` or `statusline.sh` with a newer date than the restart.

## Run on 2026-10-14: passing

Edwin rebuilt and restarted the application at 12:38 and opened a new terminal in this repository. The Claude session in it (`2f121e6f`) read its own state from the sidecar:

- Step 1 passed: the variable held the plugin path once, with nothing else.
- The sidecar marked the session `plugin_claimed`, recorded its prompts, and showed cost, context and both rate limits, with no `statusline.sh` involved.
- The generated Claude files in the instrument folder all date from 11:24, before the restart.
- Steps 2 to 5 passed (Edwin, 11:52 UTC: "all correct"). Claude started without asking about a plugin. The agent row showed the edit to this note, which the sidecar recorded under the session's files. No cockpit line appeared below the prompt; Edwin has no status line of his own. `/context` said 89.3k of 1M, 9%, and the sidecar held 9% of 1M with cost $1.02.
- Step 6 passed. Edwin exited the session with `/exit`; the sidecar recorded it as ended at 11:54:29 UTC, state `idle`. The next session (`810e5c6f`), started in the same terminal three seconds later, was picked up as a new plugin-claimed session.

Step 7 took three tries. The application was restarted with `COCKPIT_NO_INSTRUMENT=1` at 12:56.

- The first try, in your-applications.com, does not count. Its terminal had not been closed with the restart button, so the shell dated from 12 October and still started Claude with the old generated settings. The sidecar recorded that session (`0c46a997`) through the old `statusline.sh` and hooks, which is what an unclosed terminal is expected to do.
- The second try, at 13:00 after the restart button, failed: `echo $CLAUDE_CODE_PLUGIN_DIRS` printed the plugin path. The cockpit's tmux server, started on 11 October, gave every new terminal the environment it started with, including another terminal's `ZDOTDIR`. That is [[ISS-0319-Every-Cockpit-Terminal-Inherits-The-Environment-Of-The-Claude-Session-That-Started-Tmux]].
- The third try passed at 13:19, after [[TASK-0652-A-New-Cockpit-Terminal-Starts-Without-Another-Sessions-Variables]] fixed ISS-0319 and the application restarted on that build at 13:11 with `COCKPIT_NO_INSTRUMENT=1`. Edwin restarted the project-os-deck terminal (new tmux session 13:18:32) and the variable was empty. The shell started with none of another session's variables. Claude (`d493f361`) started and answered a prompt. The sidecar recorded that session with its prompt only: no `plugin_claimed`, no cost figures. The prompt came from the external hook registered in Edwin's `~/.claude/settings.json` (FEAT-0027), not from the cockpit terminal. The step's expectation was reworded to say so.

## Not this check

- `~/.claude` staying byte-identical. A node test runs that against a stand-in home on every build.
- Codex sessions. TST-0011's Codex rows cover them, and nothing they use was changed.
