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
last_verified: ""
covers: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"]
issues: []
tasks: ["[[TASK-0651-The-Sidecar-Prefers-The-Plugin-And-CI-Checks-It]]"]
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
4. Look at Claude's status line at the bottom of the terminal.
5. Look at the cost, context and rate-limit figures for the session in the cockpit.
6. Exit Claude.
7. Quit the application, start it from a terminal with `COCKPIT_NO_INSTRUMENT=1`, open a terminal in a project whose tmux session you have closed, and run `echo $CLAUDE_CODE_PLUGIN_DIRS` and `claude`.

## Expect

- Step 1 prints a path ending in `desktop/plugin/claude-code`, after any value you set yourself, and only once.
- In step 2 Claude starts as it does in any other terminal; your `claude` alias, if you have one, applies. Claude asks nothing about a plugin.
- In step 3 the dot goes busy while Claude works and waiting when it finishes. The agent row shows the prompt, the tool and the file it edited.
- In step 4 the status line is your own, or Claude's default if you have none. It is not the cockpit's `model · $cost` line.
- In step 5 the figures appear after the first turn ends, and match what `/cost` and `/context` say in the session.
- After step 6 the session shows as ended.
- In step 7 the variable is empty, and the session does not appear in the cockpit.
- The instrument folder for the project (`~/Library/Application Support/project-os-cockpit/instrument/<project>/`) gains no `claude-settings.json`, `hook-forward.sh` or `statusline.sh` with a newer date than the restart.

## Not this check

- `~/.claude` staying byte-identical. A node test runs that against a stand-in home on every build.
- Codex sessions. TST-0011's Codex rows cover them, and nothing they use was changed.
