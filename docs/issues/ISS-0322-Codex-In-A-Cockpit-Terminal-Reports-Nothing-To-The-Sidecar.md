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

Found in TST-0095 step 10 on 2026-10-14. Edwin started `codex` in a new project-os-deck terminal (tmux session created 16:48:11 local) and pressed Implement. The deck sidecar had no Codex session, so the cockpit treated the terminal as a plain shell and typed `codex 'Work on TASK-0083. …'`. Codex submitted that line as Edwin's message, wrapper and all. With the session known, the cockpit would have pasted the prompt and pressed Return separately.

## What was checked

- `codex` ran through the cockpit's wrapper: its command line carries the ten `-c hooks.<Event>=…` flags pointing at `instrument/1713681131ab04b9/codex-hook-forward.sh`.
- `hook-env` in that folder names `http://127.0.0.1:8766`, the deck sidecar's address after the restart, and the forwarder reads it on every call. The file was rewritten at 16:50, two minutes after Codex started.
- No Codex event reached the deck sidecar, even while Codex worked on the prompt afterwards.
- Codex's log has a `hooks/list` and a hooks `config/batchWrite` at 16:48:39–41, which is Codex's hook review.
- `~/.codex/config.toml` trusts seven session-flag hooks, keyed only by event (`/<session-flags>/config.toml:session_start:0:0`, …) with one hash each. Each project's hook command names that project's own instrument folder.

## Likeliest cause, not confirmed

If Codex's trust hash covers the command text, a trust given in one project does not match another project's command, and Codex skips the hooks there without reporting it. This has not been verified. Next step: start `codex` in a cockpit terminal in a project, and compare its hook review with the trusted hashes; or check whether `your-applications.com`, whose terminal also runs Codex, reports to its sidecar.
