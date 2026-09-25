---
type: "[[test]]"
id: TST-0011
aliases: ["TST-0011"]
title: "Live-session instrumentation + activity surfaces — manual checklist"
status: "passing"
covers: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0020-Agent-Activity-Surfaces]]", "[[FEAT-0021-Task-Dispatch]]", "[[FEAT-0022-Session-Insight-And-Traceability]]", "[[FEAT-0023-Overview-Scopes]]", "[[FEAT-0024-Agent-Verbs]]", "[[FEAT-0025-Dispatch-Runtime]]", "[[FEAT-0026-Verb-Polish]]", "[[FEAT-0027-External-Session-Signal]]"]
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: "2026-09-25"
scope: feature
level: e2e
entrypoint: ""
tasks: ["[[TASK-0115]]", "[[TASK-0116]]", "[[TASK-0118]]", "[[TASK-0119]]", "[[TASK-0121]]", "[[TASK-0124]]", "[[TASK-0129]]", "[[TASK-0130]]", "[[TASK-0132]]", "[[TASK-0133]]", "[[TASK-0134]]", "[[TASK-0138]]", "[[TASK-0142]]"]
last_verified: "2026-09-25"
last_run: "2026-09-25"
---

# TST-0011 — Live-session instrumentation (manual)

## Why manual

The automated suite (TST-0010) proves the ingestion pipeline with synthetic payloads; this checklist proves the *injection* — a real `claude` (and `codex`) launched in the embedded terminal must feed the pipeline with zero manual `cockpit signal` calls — and the visual surfaces.

## Checklist

1. **Claude Code injection (TASK-0115).** Open a workspace, open the terminal (⌘`), run `claude`, submit a prompt. Expect: rail dot flips to busy within ~1s, activity strip appears above the terminal showing the prompt; `~/.claude` untouched (`ls -la ~/.claude` mtimes unchanged); `claude` outside the cockpit behaves normally.
2. **needs-input (TASK-0114/0119/0120).** Trigger a permission prompt inside the session. Expect: red pulsing rail dot, OS notification, inbox bell with badge in the top bar; clicking the inbox row jumps to the workspace terminal.
3. **Statusline meters (TASK-0117).** During the session the strip shows ctx % and $ cost within ~10s of activity.
4. **Live nav trail (TASK-0120).** Have the agent edit a docs note; the matching nav row flashes an "agent" chip that decays after ~8s.
5. **Codex lifecycle (ISS-0312).** Start a new cockpit shell or source its generated `.zshrc` so the updated wrapper is loaded, then run `codex` in the embedded terminal. Review its hooks with `/hooks` if Codex asks. Submit a prompt, trigger an approval, finish the turn, submit another prompt, and exit. Expect the project icon and strip to show busy → needs-input → waiting → busy → idle; Needs you includes a fresh waiting or approval state; the icon becomes old after the one-hour age boundary. The strip says `cache unknown` rather than claiming a Codex cache price. Repeat with a Claude session waiting in the same project and check that the Codex busy state remains visible while the Claude review item stays in Needs you.
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

The 2026-09-16 Codex follow-up has automated checks for the generated wrapper, hook forwarder, mixed-session state, patch paths, and attention eligibility. A live Codex walkthrough has not yet been recorded. The July 27 `passing` run below still has a skipped Codex row; its status does not certify the new path.

The 2026-09-16 repair added a narrow live CLI check in an ephemeral temporary directory. Codex fired `SessionStart`, `UserPromptSubmit`, `Stop`, and `SessionEnd` through the quoted command path. The check bypassed hook trust only for that isolated probe and did not walk the Electron project icon, Needs You, or a permission request. This does not complete checklist item 5.

Edwin then exited the old Codex process, refreshed the cockpit shell, resumed the conversation, and approved the hooks. The resumed process arguments contain all seven per-launch hooks. Its live sidecar session has `native_codex_hook_seen: true`; a Bash approval changed `.cockpit/agent-state.json` to `needs-input`, and the next tool event changed it to `busy`. The renderer's `railKey` returns `busy` for that payload. The actual icon and Needs You screen still need a visual check, and `Stop` will occur only after the current turn ends.

Edwin visually confirmed Busy / working on the project icon, but did not see a Codex item in Needs You during a Bash approval. The sidecar history held an approval transition for only 55 ms, shorter than the desktop's five-second file poll. A new Electron main-process SSE bridge sends every state transition to the renderer over IPC; a local stream test saw `needs-input` and `busy` in order. The live Needs You result after the app reload is still unverified.

### 2026-09-16 — failing (Codex lifecycle row, by user:edwin)

- **pass** · Busy / working is visible on the project icon during a live Codex turn.
- **fail** · Needs You did not show a Codex item during a Bash approval before the live-state bridge was installed.
- **pending** · Repeat the approval and turn-complete checks against the restarted app. The local bridge test passed, and the sidecar health endpoint recovered after restart; neither result is a visual pass.

Edwin then confirmed that Needs You showed the right icon and text after the Codex turn completed, but during the next busy turn it said “Claude - Claude is waiting for your input.” The sidecar had a busy Codex session and an older waiting Claude session in the same project. A focused renderer check now expects one card with Codex working first and Claude's waiting request below it; it also checks that a current Codex approval stays primary. The live mixed-session screen check is still pending after reload.

The rebuilt app was reopened with the same tmux-owned Codex process. A live screen capture during a Bash approval showed “Codex · wants to use Bash” as the Needs You message. The focused renderer checks passed the mixed busy/waiting case, the approval case, and dismissal stability as displayed duration changes. The older Claude entry crossed its one-hour age boundary before a clean live capture of the mixed busy card, so that visual result remains open.

After a later 21-second validation run, Edwin reported that the project card said only “working” while Codex was busy. The older Claude request had aged out, so the card came from record/publication work and used the shared `agentLine` text. The renderer now prefixes the active agent in that line, and a focused test covers the record-card path. The app was rebuilt and the same Codex process survived another Electron reload; Edwin's visual result for this exact fallback path is pending.

Edwin confirmed after that reload that the project-os-cockpit card reads “Codex · working…” while Codex runs. This closes the observed fallback-wording failure. The full Codex lifecycle row remains open because the mixed busy/waiting card, another live approval, and exit behavior have not all been walked after the latest change.

## Runs

### 2026-07-27 — passing (by user:edwin)
- **pass** · Claude Code injection (TASK-0115). Open a workspace, open the terminal (⌘`), run `claude`, submit a prompt
- **pass** · needs-input (TASK-0114/0119/0120). Trigger a permission prompt inside the session
- **pass** · Statusline meters (TASK-0117). During the session the strip shows ctx % and $ cost within ~10s of activity.
- **pass** · Live nav trail (TASK-0120). Have the agent edit a docs note; the matching nav row flashes an "agent" chip that decays after ~8s.
- **skip** · Codex notify (TASK-0116). Run `codex` in the embedded terminal, complete a turn
- **pass** · Dispatch (TASK-0121/0122). Right-click a backlog TASK row → "Start with Claude Code"
- **pass** · Sessions in Overview (TASK-0124/0127). Switch to Overview mode: a live-session banner sits under the hero (state, prompt, ctx/$ meters, terminal button) and updates within ~1s of agent events; "Agent sessions" renders as a column beside Recent activity; clicking a row opens the session detail page (prompts, files, produced CHGs) and back/forward work.
- **pass** · Undocumented badge (TASK-0125). Have the agent edit a source file without touching any TASK/ISS/CHG note: amber "undocumented" chip on the strip; writing a CHG note clears it.
- **pass** · Overview scopes (FEAT-0023). In Overview, the left pane lists Project + phases with progress bars; selecting a phase renders its scoped dashboard (hero, feature squares, exit criteria, scoped activity) with the phase context + Now card in the right pane; back/forward restore the exact scope; a file change refreshes numbers without losing scroll.
- **pass** · Agent verbs + queue (FEAT-0024). Right-click a FEAT note → Agent ▸ shows Break down / Implement next / Refine scope / Close out (+ agent radios); picking one types the skill-referencing prompt. The ▶ button appears on PHASE/REQ/RISK notes too. Dispatch twice while the agent is busy: both queue (strip shows "queued 2"); when the session hits Stop, the first queued prompt lands in the live REPL; after quitting the CLI, the next runs as a fresh shell command.
- **pass** · Dispatch runtime (FEAT-0025/0026). Queue two dispatches in workspace A while its agent is busy, switch to workspace B: A's queued prompts still deliver on A's Stop/SessionEnd (check A's terminal after). Restart the app with items queued: the queue survives. The strip chip opens a popover with per-item ✕. A done task's Agent menu hides Implement; ⌘P "refine TASK-0115" dispatches; `cockpit dispatch TASK-0116 --verb refine` from an external terminal under the repo lands in the cockpit queue. A dispatched note shows its provenance line; the originating session row shows "← refine TASK-0115".
- **pass** · External-session signal (FEAT-0027). Settings gear → enable the external-terminal toggle: `~/.claude/settings.json` gains the cockpit's hook entries (backup file appears beside it). Run `claude` in a normal terminal under any project-os repo: the repo's rail dot tracks the session (full session record when the workspace's cockpit runs). Disable the toggle: the entries are gone, everything else in the file untouched. Kill a session mid-work: the dot decays to idle within ~10 minutes.
- **pass** · Kill switch. Relaunch the app with `COCKPITNOINSTRUMENT=1`: no wrapper functions, `cockpit signal` works as before.

### 2026-09-25 — passing (by user:edwin)
- **pass** · Claude Code injection (TASK-0115). Open a workspace, open the terminal (⌘`), run `claude`, submit a prompt
- **pass** · needs-input (TASK-0114/0119/0120). Trigger a permission prompt inside the session
- **pass** · Statusline meters (TASK-0117). During the session the strip shows ctx % and $ cost within ~10s of activity.
- **pass** · Live nav trail (TASK-0120). Have the agent edit a docs note; the matching nav row flashes an "agent" chip that decays after ~8s.
- **pass** · Codex lifecycle (ISS-0312). Start a new cockpit shell or source its generated `.zshrc` so the updated wrapper is loaded, then run `codex` in the embedded terminal. Review its hooks with `/hooks` if Codex asks. Submit a prompt, trigger an approval, finish the turn, submit another prompt, and exit. Expect the project icon and strip to show busy → needs-input → waiting → busy → idle; Needs you includes a fresh waiting or approval state; the icon becomes old after the one-hour age boundary. The strip says `cache unknown` rather than claiming a Codex cache price. Repeat with a Claude session waiting in the same project and check that the Codex busy state remains visible while the Claude review item stays in Needs you.
- **pass** · Dispatch (TASK-0121/0122). Right-click a backlog TASK row → "Start with Claude Code"
- **pass** · Sessions in Overview (TASK-0124/0127). Switch to Overview mode: a live-session banner sits under the hero (state, prompt, ctx/$ meters, terminal button) and updates within ~1s of agent events; "Agent sessions" renders as a column beside Recent activity; clicking a row opens the session detail page (prompts, files, produced CHGs) and back/forward work.
- **pass** · Undocumented badge (TASK-0125). Have the agent edit a source file without touching any TASK/ISS/CHG note: amber "undocumented" chip on the strip; writing a CHG note clears it.
- **pass** · Overview scopes (FEAT-0023). In Overview, the left pane lists Project + phases with progress bars; selecting a phase renders its scoped dashboard (hero, feature squares, exit criteria, scoped activity) with the phase context + Now card in the right pane; back/forward restore the exact scope; a file change refreshes numbers without losing scroll.
- **pass** · Agent verbs + queue (FEAT-0024). Right-click a FEAT note → Agent ▸ shows Break down / Implement next / Refine scope / Close out (+ agent radios); picking one types the skill-referencing prompt. The ▶ button appears on PHASE/REQ/RISK notes too. Dispatch twice while the agent is busy: both queue (strip shows "queued 2"); when the session hits Stop, the first queued prompt lands in the live REPL; after quitting the CLI, the next runs as a fresh shell command.
- **pass** · Dispatch runtime (FEAT-0025/0026). Queue two dispatches in workspace A while its agent is busy, switch to workspace B: A's queued prompts still deliver on A's Stop/SessionEnd (check A's terminal after). Restart the app with items queued: the queue survives. The strip chip opens a popover with per-item ✕. A done task's Agent menu hides Implement; ⌘P "refine TASK-0115" dispatches; `cockpit dispatch TASK-0116 --verb refine` from an external terminal under the repo lands in the cockpit queue. A dispatched note shows its provenance line; the originating session row shows "← refine TASK-0115".
- **pass** · External-session signal (FEAT-0027). Settings gear → enable the external-terminal toggle: `~/.claude/settings.json` gains the cockpit's hook entries (backup file appears beside it). Run `claude` in a normal terminal under any project-os repo: the repo's rail dot tracks the session (full session record when the workspace's cockpit runs). Disable the toggle: the entries are gone, everything else in the file untouched. Kill a session mid-work: the dot decays to idle within ~10 minutes.
- **pass** · Kill switch. Relaunch the app with `COCKPITNOINSTRUMENT=1`: no wrapper functions, `cockpit signal` works as before.

## September 23 partial live run

See [Codex parity implementation and verification](../../../../reference/codex-parity-verification-2026-09-23.md) for the exact isolated build, CLI, workspaces and observations. Approval, completed turn, child lifecycle, background-workspace queue submission, interruption through late tool completion, recovery, same-shell exit and History were observed. The external Codex setting was enabled through Settings, persisted through restart, captured a real external CLI and was disabled again. The production user configuration was untouched.

A complete passing verdict is not recorded: the disposable Claude profile reported Not logged in, so the real waiting-Claude/busy-Codex check remains open. The full historical checklist has not been replayed. Task handoffs retain that gate; the July waiver does not certify this run.

### Added Codex procedures

- Run a parent with a child. Observe distinct parent/child identity on both child lifecycle events; child completion must not finish the parent or release its queue.
- Queue a task during a long Bash command, switch workspace and return; after normal Stop, verify the queued prompt produces its own UserPromptSubmit and reply.
- Interrupt a long command while a task is queued. Wait beyond the command's completion; Needs You must still say interrupted and the queue must stay held. Submit a new prompt deliberately and verify recovery.
- Enable the separate Codex setting in disposable configuration with pre-existing user hooks. Review hooks normally, run an external CLI and compare the correct workspace. Repeat while embedded telemetry is active; activity must not duplicate. Restart, then disable and confirm unrelated entries remain. Exercise the generated-hook fallback with no sidecar separately; this fixture does not claim a live CLI run.
