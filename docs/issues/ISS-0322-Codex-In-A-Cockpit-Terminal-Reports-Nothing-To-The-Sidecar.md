---
type: "[[issue]]"
id: ISS-0322
aliases: ["ISS-0322"]
title: "A Codex session in project-os-deck's cockpit terminal reported nothing to the sidecar, so a dispatch was typed as a shell command into Codex"
status: open
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

## Possible causes, not confirmed

1. Codex runs `SessionStart` only when the first turn starts, not when the TUI opens. Then a Codex session nobody has prompted is invisible to the cockpit whatever the trust state.
2. A trust problem, below. All ten events have a trust entry; whether one covers another project's command is unknown.

Astra (Codex's model) is reviewing both on 2026-10-14.

If Codex's trust hash covers the command text, a trust given in one project does not match another project's command, and Codex skips the hooks there without reporting it. This has not been verified. Next step: start `codex` in a cockpit terminal in a project, and compare its hook review with the trusted hashes; or check whether `your-applications.com`, whose terminal also runs Codex, reports to its sidecar.

## Next Actions

In flight on 2026-10-14, about 17:05 local. Edwin: "look into ISS-0322 first you can use the codex (astra) model to review and suggest the correct solution."

1. Astra (`gpt-6-astra`) is reviewing this issue from a read-only brief through `codex exec -s read-only`. The brief asks four things: when Codex 0.162.1's TUI runs `SessionStart`, how session-flag hook trust is hashed and whether it spans projects, the actual cause here, and the right fix. The brief and its answer are in the session's scratchpad, which is not durable; if the session is lost, rerun the review from this section.
2. Verify Astra's answer before acting on it. A claim about Codex's behaviour needs evidence: source, docs, or an experiment that posts only to a temporary file.
3. Bring the recommended fix to Edwin; then write a task and fix it. Step 10 of TST-0095 is rerun afterwards.

## Notes

- Ruled out: the address file and the forwarder. `hook-env` names the right sidecar and the forwarder reads it on every call.
- Not done, on purpose: no experiment that trusts a new hook command. The trust entries in `~/.codex/config.toml` are keyed by event alone, so trusting a scratch command could replace the cockpit's own trusted hash in Edwin's config.
- Not done, on purpose: no test hook POSTed to the deck sidecar. It would put a made-up Codex session into Edwin's running cockpit.
- Six guessed hash formats over each project's hook command matched none of the trusted hashes, so the hash input is unknown.
