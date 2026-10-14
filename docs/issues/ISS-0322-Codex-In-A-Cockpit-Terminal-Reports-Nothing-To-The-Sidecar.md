---
type: "[[issue]]"
id: ISS-0322
aliases: ["ISS-0322"]
title: "A Codex session in project-os-deck's cockpit terminal reported nothing to the sidecar, so a dispatch was typed as a shell command into Codex"
status: fixed
phase: ""
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]], step 10, run on 2026-10-14"]
reported_by: agent
question: ""
severity: medium
component: desktop
parent: ""
related: ["[[FEAT-0019]]", "[[ISS-0312]]", "[[ISS-0321-The-Dispatch-Agent-Is-Chosen-By-Hand-Not-From-The-Running-Agent]]"]
tests: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"]
---

# Codex in a cockpit terminal reports nothing

Found in TST-0095 step 10 on 2026-10-14. Edwin started `codex` in a new project-os-deck terminal (tmux session created 16:48:11 local) and pressed Implement. The deck sidecar had no Codex session, so the cockpit treated the terminal as a plain shell and typed `codex 'Work on TASK-0083. …'`. The line sits in Codex's composer: at 16:58 Codex showed "Context 0% used" and had written no session record, so no turn had run. With the session known, the cockpit would have pasted the prompt and pressed Return separately.

## What was checked

- `codex` ran through the cockpit's wrapper: its command line carries the ten `-c hooks.<Event>=…` flags pointing at `instrument/1713681131ab04b9/codex-hook-forward.sh`.
- `hook-env` in that folder names `http://127.0.0.1:8766`, the deck sidecar's address after the restart, and the forwarder reads it on every call. The file was rewritten at 16:50, two minutes after Codex started.
- No Codex event reached the deck sidecar. Codex had not been prompted, so the only event due was `SessionStart`.
- Codex's log has a `hooks/list` and a hooks `config/batchWrite` at 16:48:39–41, which is Codex's hook review.
- `~/.codex/config.toml` has a trust entry for all ten session-flag hooks, keyed only by event (`/<session-flags>/config.toml:session_start:0:0`, …) with one hash each. Each project's hook command names that project's own instrument folder.

## Cause, verified 2026-10-14

**Codex runs its `SessionStart` hook when the first turn starts, not when it opens.** In Codex 0.162.1 the only caller of `run_pending_session_start_hooks` is `run_turn` (`codex-rs/core/src/session/turn.rs`, lines 322 and 643, tag `rust-v0.162.1`). Nobody had prompted the deck Codex, so no hook had run, and the sidecar had no session. `routeFor` in `desktop/src/ipc/dispatch-queue.ts` treats "no session" as "a shell is waiting", so it typed `codex '<prompt>'` into Codex.

**The hooks were trusted, so trust is not the cause here.** Codex hashes a hook as sha256 over sorted, compact JSON of `{event_name, hooks: [{command, timeout, type}]}` (`codex-rs/hooks/src/engine/discovery.rs`, `hook_hash`; `codex-rs/config/src/fingerprint.rs`, `version_for_toml`). Reproduced here: all ten trusted hashes in `~/.codex/config.toml` match deck's commands (`instrument/1713681131ab04b9`), and no other project's. Astra found the same.

**A second defect follows from that hash.** The trust entry is keyed by event alone, but each project's command names its own folder. So trusting Codex's hooks in one project marks them `Modified` in every other project, and Codex excludes them there until the person reviews them again. Right now Codex hooks are trusted only in project-os-deck.

Found with Astra (`gpt-6-astra`, read-only `codex exec`), whose answer was checked against the Codex source above before it was written here.

## Fix (Astra's recommendation; Edwin: "yes, implement both parts")

1. Before typing a shell command, the shell asks tmux what is in the foreground of that project's terminal (`#{pane_current_command}`). It reads `codex` for Codex and Claude Code's version number, `2.1.299`, for Claude. Only a recognised shell gets a shell command. A running Codex gets the prompt pasted with a separate Return. Anything else is held and shown as not delivered. This is the same check ISS-0321 needs.
2. Every project uses one identical Codex hook command. The forwarder finds the project's sidecar through `COCKPIT_INSTRUMENT_DIR`, which every cockpit terminal already has. One trust then covers every project. Files: `desktop/src/ipc/agent-instrument.ts`.

## Next Actions

Both parts are built and tested, on 2026-10-14: [[TASK-0660-A-Dispatch-Checks-What-Runs-In-The-Terminal-Before-Typing]] and [[TASK-0661-Every-Project-Uses-One-Codex-Hook-Command]]. The issue stays open until TST-0095 steps 9 and 10 pass in the running application:

1. Restart the cockpit, so its main process loads the new dispatch code and writes the shared forwarder.
2. Step 9 again, under the kill switch: the dispatch is held, nothing typed.
3. Step 10 again: in a new terminal, run `codex`, answer its hook review once (trust), and press a verb button without prompting Codex first. The prompt is pasted and submitted, and the dispatch history names `codex`.

## Notes

- Ruled out: the address file and the forwarder. `hook-env` names the right sidecar and the forwarder reads it on every call.
- Not done, on purpose: no experiment that trusts a new hook command. The trust entries in `~/.codex/config.toml` are keyed by event alone, so trusting a scratch command could replace the cockpit's own trusted hash in Edwin's config.
- Not done, on purpose: no test hook POSTed to the deck sidecar. It would put a made-up Codex session into Edwin's running cockpit.
- Six guessed hash formats matched nothing at first; the identity Codex really hashes was then read from its source and matched deck's ten commands.

## Verified, 2026-10-14

TST-0095 steps 9 and 10 passed in the running application after TASK-0660 and TASK-0661. An unprompted Codex in project-os-deck got the dispatch pasted and submitted, and the dispatch history named `codex` although the Agent menu was not touched. A Codex started in your-trainer after the fix went straight to its prompt, without a hook review.
