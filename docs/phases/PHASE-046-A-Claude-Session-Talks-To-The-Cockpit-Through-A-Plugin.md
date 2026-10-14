---
type: "[[phase]]"
id: PHASE-046
aliases: ["PHASE-046"]
title: "A Claude session talks to the cockpit through a plugin — no generated shell files, no hijacked status line, no typed keystrokes"
status: active
order: 46
owner: user:edwin
created: 2026-10-08
updated: 2026-10-14
goal: "A Claude Code session started from the cockpit is connected to it through Claude Code's mod interface, so everything the cockpit learns from the session, shows in it or sends to it travels over a supported channel, while Codex sessions keep working exactly as they do today."
features:
  - "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
  - "[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"
  - "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
  - "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"
requirements: []
tasks: ["[[TASK-0649]]", "[[TASK-0650]]", "[[TASK-0651]]", "[[TASK-0652]]", "[[TASK-0653]]"]
issues: ["[[ISS-0319]]"]
related:
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]]"
  - "[[PHASE-007-Agent-Instrumentation]]"
  - "[[PHASE-040-The-Agent-Session-Is-Not-A-Terminal]]"
  - "[[PHASE-031-The-Supervised-Week]]"
  - "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]"
  - "[[PHASE-045-The-Cockpit-In-Layers]]"
  - "[[FEAT-0019-Agent-Hook-Ingestion]]"
  - "[[FEAT-0027]]"
  - "[[FEAT-0029-Cockpit-MCP-Server]]"
  - "[[FEAT-0079-Supervision-From-A-Phone]]"
  - "[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]"
  - "[[ISS-0277-Nothing-Detects-A-Stale-Or-Broken-Vendored-Cockpit]]"
  - "[[RISK-0004-Hook-Injection-Surface]]"
  - "[[RISK-0006-The-Unattended-Worker]]"
  - "[[REQ-0026-Only-Human-Owned-Transitions]]"
  - "[[REQ-0027-Every-Write-Guarded]]"
  - "[[ADR-0009-The-Principal-Is-A-Role]]"
tags: [phase, agents, claude-code, plugin, instrumentation]
---

# A Claude session talks to the cockpit through a plugin

## Goal

When this phase is done, a Claude Code session started in a cockpit terminal is connected to the cockpit by a plugin that Claude Code itself loads. Today the connection is three improvised channels: shell files the shell generates for every workspace, a status-line script used to smuggle cost and context out, and a robot that types prompts into the terminal. Every piece of information that crosses between the two moves to Claude Code's supported plugin interface instead. Codex sessions keep the current mechanism and must not notice the change.

The interface is Claude Code **mods**, which shipped in v2.1.287; the installed version on 2026-10-08 is 2.1.292. A mod is a plugin whose `hooks/hooks.json` names a TypeScript module. That module runs inside Claude Code's own process with the user's permissions, sees session events, can draw above the prompt, and can submit a prompt or answer a permission check. The documentation is at https://code.claude.com/docs/en/plugins/mods/overview.

**Why this is a phase and not an issue.** The goal is one sentence that does not list its parts: the session reaches the cockpit over a supported channel. The exit criteria below are about what the person sees and what the machine refuses, not about tasks being done (CLAUDE.md, "When to open a phase"). It holds four features, and it can close on a refusal: if the mods interface proves too unstable to pin, the phase closes `deferred` and the shell-script path stays.

**Why now.** [[REFERENCE-FUNCTION-HOOKS-REVIEW]], written on 2026-09-04 against the pre-release proposal, said to revisit when it shipped and to turn its follow-ups into issues or a feature at that point. It has shipped, and both things that note asked Anthropic for now exist: a permission event a hook can resolve (`tool.check`), and cost and context as events (`session.measure` and `$.session.usage`).

## Scope

Four features, in delivery order. Each is filed at `backlog` with its feature note only, because this phase is `planned` (feature-scaffold, "A feature filed for later"). Each note's Findings section carries the candidate task list; tasks, requirements, a plan and the acceptance check are written when that feature starts.

1. [[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]. **First, and everything else depends on it.** The shell puts a plugin shipped with the cockpit on `CLAUDE_CODE_PLUGIN_DIRS`. The plugin posts the same payloads the shell scripts post today to `/api/agent-hook`, and reads cost, context and rate limits from Claude Code directly instead of through `statusline.sh`. The Claude half of the generated instrument directory is retired.
2. [[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]. The cockpit's facts join the project line above the Claude Code prompt: what needs the person here and in the other projects, with an "Open in cockpit" button. A few prefixed commands answer from the sidecar in a pane without starting a turn. Since 2026-10-14 the line itself, its project facts and the wrong-model warning belong to project-os ([[project-os-dev#FEAT-0041-Project-Os-Mod]]), because they can be read from the repo and should appear outside cockpit terminals too.
3. [[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]. A prompt dispatched from the cockpit reaches a Claude session through `$.prompt.submit` and is confirmed when its turn starts. Codex keeps the keystroke path.
4. [[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]. **Last, and blocked on [[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]].** The cockpit's approve and deny buttons become the actual answer to a Claude permission prompt, within a bounded wait, after which the terminal prompt appears as it does today.

Features 2 and 3 can be built in either order once feature 1 is done.

## Out of Scope

- **Porting the project-os gates to a mod (the suggested leg 5).** A mod would let the close-out hook see files edited through Bash by running `git status --porcelain` at `turn.complete`, hold HC-006's session marker in memory, and count HC-010's review budget from `agent.spawn` and `tool.call`. All of these hooks are owned upstream in `~/Dev/repos/project-os` (`tools/adapters/claude-code/hooks/`, HOOKS.md, CLAUDE.md "Model routing"), and they run in every session in all twelve fleet repos, not only in cockpit terminals. Building them here would fork a template-owned file. **Filed in project-os-dev on 2026-10-14 as [[project-os-dev#FEAT-0041-Project-Os-Mod]]**, together with leg 6, because leg 6 is how such a mod would reach the fleet. HC-001 and HC-003 should stay shell scripts in any case: they work today and they keep Codex parity.
- **project-os as a plugin marketplace (the suggested leg 6).** It would ship this mod, the skill wrappers and the agent files together, and give them a version. It also renames every skill to `plugin:skill`. The reason first given, that `sync-project-os.sh` never refreshes `.claude/`, was stale: the template sync has regenerated `.claude/agents/` and `.claude/skills/` since 2026-07-18. This is project-os's decision, not this repository's. **Filed in project-os-dev on 2026-10-14 as [[project-os-dev#ISS-0106-Project-Os-As-A-Plugin]].** This phase ships the cockpit's plugin inside the cockpit app and loads it by environment variable, which needs no marketplace.
- **The cockpit MCP server, [[FEAT-0029-Cockpit-MCP-Server]].** It stays an MCP server so Codex and other MCP hosts can use it. A mod's `$.mcp.connect` could consume it later; nothing here absorbs it.
- **Codex, Cursor and generic adapters.** Codex keeps `-c hooks.*`, `codex-external-hooks.ts`, the zdotdir wrapper and the keystroke dispatch, unchanged.
- **Sessions outside a cockpit terminal.** The plugin loads only where the shell sets the environment variable. A Claude session in another terminal keeps [[FEAT-0027]]'s opt-in user hook, and gets no band.
- **Remote workspaces, [[PHASE-033-The-Workspace-Is-Not-Always-Local]].** This phase does not help them: the mod runs on whichever machine runs `claude`, and the loopback sidecar is on this Mac.

## Exit Criteria

- [ ] A Claude session started in a cockpit terminal lights the same rail dots, agent rows, cost, context and rate-limit figures as before, with no `claude-settings.json`, Claude `hook-forward.sh` or `statusline.sh` generated, and the user's own status line drawn unchanged.
- [ ] `~/.claude` is byte-identical before and after a spawn, a session and a teardown in a cockpit terminal ([[RISK-0004-Hook-Injection-Surface]]'s test, run against the plugin path).
- [ ] With `COCKPIT_NO_INSTRUMENT=1`, a Claude session in a cockpit terminal loads no cockpit plugin and posts nothing.
- [ ] Every Codex row of the TST-0011 live walk passes unchanged.
- [ ] No code path writes a prompt or an answer into a Claude session's terminal. A prompt dispatched to a Claude session is recorded as delivered only after its turn started.
- [ ] A permission prompt answered in the cockpit is answered in the session; a request without the shell's secret is refused, and a test shows that a `deny` from the user's own PreToolUse hook survives every cockpit answer.
- [ ] `claude plugin validate` and `claude plugin test` run in CI and fail the build, against a pinned Claude Code version that the plugin declares.
- [ ] Each change note that adds or changes capability updates `docs/reference/cockpit-capability-register.md` in the same commit (CLAUDE.md, "A sibling application tracks this cockpit's capability"). This applies when the work lands, not now.
- [ ] Or, if the mods interface changes faster than it can be pinned: the phase closes `deferred`, the shell-script path is still the one that runs, and the reason is written here.

## Risks found by the scan

The risk scan (LIFECYCLE, "Risk scan triggers") applies on four counts. Per feature-scaffold's short path, the `RISK-*` notes are written when the first feature starts, not now. Each is listed here so it is not lost.

1. **A new external dependency with a version constraint.** The mods interface is weeks old and may change between Claude Code releases. A change can silently stop events arriving, which shows the person a green dot that is wrong. Mitigation: the plugin declares the version it was tested on, CI runs `claude plugin test`, and the sidecar flags a session that started but never reported. This extends [[RISK-0004-Hook-Injection-Surface]]'s schema-drift mitigation, so it may be a section there rather than a new note.
2. **Unsandboxed code running with the user's permissions.** A mod runs inside Claude Code's process with no sandbox. A defect in it runs in every cockpit Claude session, and a mod can approve calls that the user's own PreToolUse hooks would block. Mitigation: the plugin never turns a `deny` into an `allow`, its code is small enough to review whole, and it holds no secret it does not need.
3. **Approving through the cockpit becomes a way to run commands.** Today the answer route trusts any request from this machine and a self-declared `actor` field (`approvals.py` `answer`, `server.py:2404`). Once an answer actually approves a Bash call, any loopback POST that claims to be a person is a command-execution hole: a framed page ([[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]), or the agent itself through any tool it is already allowed that can reach localhost. Mitigation: a secret the shell holds and the agent cannot read, required on the answer route. This is a new `RISK-*` when [[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]] starts.
4. **A Claude-only adapter widens the gap to Codex, Cursor and generic.** After this phase the Claude path can draw, submit and answer, and the others cannot. Mitigation: the sidecar contract stays agent-neutral (the same `/api/agent-hook` payloads, the same approvals store), so a later Codex mechanism plugs into the same endpoints.

## Impact analysis

Run on 2026-10-08 against the features, requirements and ADRs that share these areas. No requirement is contradicted. Four constraints and one tension carry into the features:

- [[REQ-0019-Agent-Fleet-Visibility]] (cost, context and rate limits on one screen) is a constraint on [[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]: the new source must fill every field the statusline filled.
- [[REQ-0027-Every-Write-Guarded]] (writes are loopback-only and guarded) holds. The approval answer is runtime state under `.cockpit/`, not a note write, and the secret in FEAT-0159 is added on top of the loopback check, not in place of it.
- [[REQ-0026-Only-Human-Owned-Transitions]] and [[ADR-0009-The-Principal-Is-A-Role]] constrain FEAT-0159. `approvals.py` already refuses an `agent:` actor other than `agent:principal`. **Tension:** ADR-0009 lets a delegation policy hand the principal role to an agent, and `agent:principal` may answer today. Whether a delegated principal may approve a command that a cockpit answer will actually run is a decision for Edwin (FEAT-0159, open questions).
- [[FEAT-0025]]'s dispatch ledger and [[FEAT-0027]]'s external hook are changed by FEAT-0158 and FEAT-0156; both open questions are in those notes.
- **Phase relationships.** [[PHASE-040-The-Agent-Session-Is-Not-A-Terminal]] (deferred) would hand session ownership to T3 Code. It is not blocked: a mod runs inside `claude` whoever owns the process. Its structured session stream is now partly available from `session.append`, which could feed that phase if it is reopened. [[PHASE-031-The-Supervised-Week]] and [[RISK-0006-The-Unattended-Worker]] gain from FEAT-0159: a permission wait becomes a queue entry the stall alarm can see. [[FEAT-0079-Supervision-From-A-Phone]] would inherit the answer route and its secret.

## Notes

- **Order and dependencies.** FEAT-0156 first. FEAT-0157 and FEAT-0158 after it, in either order. FEAT-0159 last, after ISS-0301's secret exists (the open half of that issue).
- **Active since 2026-10-14**, when FEAT-0156 started (the goal set for that session: deliver FEAT-0156 up to its acceptance check). Its plan and tasks are written; FEAT-0157 to FEAT-0159 stay at `backlog`. Each feature's tasks are minted when that feature starts.
- **Follow-ups for project-os (upstream), filed in project-os-dev on 2026-10-14:** the project-os mod, which takes over the session-marker and review-budget hooks, the shell-edit check, the wrong-model warning and the project half of the line above the prompt (leg 5, [[project-os-dev#FEAT-0041-Project-Os-Mod]]); and how that mod reaches each repo (leg 6, [[project-os-dev#ISS-0106-Project-Os-As-A-Plugin]]).
- **[[ISS-0277-Nothing-Detects-A-Stale-Or-Broken-Vendored-Cockpit]]** could surface in FEAT-0157's band as a start-of-session warning. It is linked, not absorbed: ISS-0277 asks for a check that reads the files, and a warning is only where its answer would be shown.
