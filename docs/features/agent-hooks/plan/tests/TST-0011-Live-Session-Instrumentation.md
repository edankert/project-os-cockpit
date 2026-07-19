---
type: "[[test]]"
id: TST-0011
aliases: ["TST-0011"]
title: "Live-session instrumentation + activity surfaces — manual checklist"
status: ready
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
scope: feature
kind: manual
level: e2e
entrypoint: ""
features: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0020-Agent-Activity-Surfaces]]", "[[FEAT-0021-Task-Dispatch]]", "[[FEAT-0022-Session-Insight-And-Traceability]]"]
tasks: ["[[TASK-0115]]", "[[TASK-0116]]", "[[TASK-0118]]", "[[TASK-0119]]", "[[TASK-0121]]", "[[TASK-0124]]", "[[TASK-0129]]", "[[TASK-0130]]", "[[TASK-0132]]", "[[TASK-0133]]", "[[TASK-0134]]", "[[TASK-0138]]", "[[TASK-0142]]"]
---

# TST-0011 — Live-session instrumentation (manual)

## Why manual

The automated suite (TST-0010) proves the ingestion pipeline with synthetic payloads; this checklist proves the *injection* — a real `claude` (and `codex`) launched in the embedded terminal must feed the pipeline with zero manual `cockpit signal` calls — and the visual surfaces.

## Checklist

1. **Claude Code injection (TASK-0115).** Open a workspace, open the terminal (⌘`), run `claude`, submit a prompt. Expect: rail dot flips to busy within ~1s, activity strip appears above the terminal showing the prompt; `~/.claude` untouched (`ls -la ~/.claude` mtimes unchanged); `claude` outside the cockpit behaves normally.
2. **needs-input (TASK-0114/0119/0120).** Trigger a permission prompt inside the session. Expect: red pulsing rail dot, OS notification, inbox bell with badge in the top bar; clicking the inbox row jumps to the workspace terminal.
3. **Statusline meters (TASK-0117).** During the session the strip shows ctx % and $ cost within ~10s of activity.
4. **Live nav trail (TASK-0120).** Have the agent edit a docs note; the matching nav row flashes an "agent" chip that decays after ~8s.
5. **Codex notify (TASK-0116).** Run `codex` in the embedded terminal, complete a turn. Expect: waiting state on turn complete; approval request → needs-input. Note the one-time trust prompt if Codex asks.
6. **Dispatch (TASK-0121/0122).** Right-click a backlog TASK row → "Start with Claude Code". Expect: terminal opens, templated command typed, agent focus set (strip shows the item). On a TASK/ISS note the top-bar ▶ button dispatches with the remembered agent.
7. **Sessions in Overview (TASK-0124/0127).** Switch to Overview mode: a live-session banner sits under the hero (state, prompt, ctx/$ meters, terminal button) and updates within ~1s of agent events; "Agent sessions" renders as a column beside Recent activity; clicking a row opens the session detail page (prompts, files, produced CHGs) and back/forward work.
8. **Undocumented badge (TASK-0125).** Have the agent edit a source file without touching any TASK/ISS/CHG note: amber "undocumented" chip on the strip; writing a CHG note clears it.
9. **Overview scopes (FEAT-0023).** In Overview, the left pane lists Project + phases with progress bars; selecting a phase renders its scoped dashboard (hero, feature squares, exit criteria, scoped activity) with the phase context + Now card in the right pane; back/forward restore the exact scope; a file change refreshes numbers without losing scroll.
10. **Agent verbs + queue (FEAT-0024).** Right-click a FEAT note → Agent ▸ shows Break down / Implement next / Refine scope / Close out (+ agent radios); picking one types the skill-referencing prompt. The ▶ button appears on PHASE/REQ/RISK notes too. Dispatch twice while the agent is busy: both queue (strip shows "queued 2"); when the session hits Stop, the first queued prompt lands in the live REPL; after quitting the CLI, the next runs as a fresh shell command.
11. **Dispatch runtime (FEAT-0025/0026).** Queue two dispatches in workspace A while its agent is busy, switch to workspace B: A's queued prompts still deliver on A's Stop/SessionEnd (check A's terminal after). Restart the app with items queued: the queue survives. The strip chip opens a popover with per-item ✕. A done task's Agent menu hides Implement; ⌘P "refine TASK-0115" dispatches; `cockpit dispatch TASK-0116 --verb refine` from an external terminal under the repo lands in the cockpit queue. A dispatched note shows its provenance line; the originating session row shows "← refine TASK-0115".
12. **External-session signal (FEAT-0027).** Settings gear → enable the external-terminal toggle: `~/.claude/settings.json` gains the cockpit's hook entries (backup file appears beside it). Run `claude` in a normal terminal under any project-os repo: the repo's rail dot tracks the session (full session record when the workspace's cockpit runs). Disable the toggle: the entries are gone, everything else in the file untouched. Kill a session mid-work: the dot decays to idle within ~10 minutes.
13. **Kill switch.** Relaunch the app with `COCKPIT_NO_INSTRUMENT=1`: no wrapper functions, `cockpit signal` works as before.

## Evidence

- (record results per run here)
