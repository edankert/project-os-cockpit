---
type: "[[phase]]"
id: PHASE-007
aliases: ["PHASE-007"]
title: "Agent instrumentation (hooks-aware terminal)"
status: done
order: 7
owner: user:edwin
created: 2026-07-05
updated: 2026-09-25
goal: "The embedded terminal understands the agent running inside it: lifecycle hooks feed agent state, activity, cost, and needs-input signals into the cockpit automatically, and the cockpit dispatches project-os tasks back to the agent."
features:
  - "[[FEAT-0019-Agent-Hook-Ingestion]]"
  - "[[FEAT-0020-Agent-Activity-Surfaces]]"
  - "[[FEAT-0021-Task-Dispatch]]"
  - "[[FEAT-0022-Session-Insight-And-Traceability]]"
  - "[[FEAT-0023-Overview-Scopes]]"
  - "[[FEAT-0024-Agent-Verbs]]"
  - "[[FEAT-0025-Dispatch-Runtime]]"
  - "[[FEAT-0026-Verb-Polish]]"
  - "[[FEAT-0027-External-Session-Signal]]"
  - "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
  - "[[FEAT-0030-Agent-Inbox]]"
  - "[[FEAT-0031-Ambient-Status-Consolidation]]"
  - "[[FEAT-0032-Agents-Screen]]"
  - "[[FEAT-0033-Agent-Signal-Hygiene]]"
  - "[[FEAT-0034-Agents-Tab-And-Follow-Control]]"
  - "[[FEAT-0035-Account-Budget-Surface]]"
  - "[[FEAT-0036-Live-Work-Views]]"
  - "[[FEAT-0037-Context-Menus-And-Clipboard]]"
  - "[[FEAT-0038-Console-Progress-Rail]]"
  - "[[FEAT-0039-Model-Routing-Subagents]]"
tasks: ["[[TASK-0633]]", "[[TASK-0634]]", "[[TASK-0635]]", "[[TASK-0636]]", "[[TASK-0637]]", "[[TASK-0114]]", "[[TASK-0115]]", "[[TASK-0116]]", "[[TASK-0117]]", "[[TASK-0118]]", "[[TASK-0119]]", "[[TASK-0120]]", "[[TASK-0121]]", "[[TASK-0122]]", "[[TASK-0123]]", "[[TASK-0124]]", "[[TASK-0125]]", "[[TASK-0126]]", "[[TASK-0127]]", "[[TASK-0128]]", "[[TASK-0129]]", "[[TASK-0130]]", "[[TASK-0131]]", "[[TASK-0132]]", "[[TASK-0133]]", "[[TASK-0134]]", "[[TASK-0135]]", "[[TASK-0136]]", "[[TASK-0137]]", "[[TASK-0138]]", "[[TASK-0139]]", "[[TASK-0140]]", "[[TASK-0141]]", "[[TASK-0142]]", "[[TASK-0143]]", "[[TASK-0144]]", "[[TASK-0145]]", "[[TASK-0146]]", "[[TASK-0147]]", "[[TASK-0148]]", "[[TASK-0149]]", "[[TASK-0150]]", "[[TASK-0151]]", "[[TASK-0152]]", "[[TASK-0153]]", "[[TASK-0154]]", "[[TASK-0155]]", "[[TASK-0156]]", "[[TASK-0157]]", "[[TASK-0158]]", "[[TASK-0159]]", "[[TASK-0160]]", "[[TASK-0161]]", "[[TASK-0162]]", "[[TASK-0163]]", "[[TASK-0164]]", "[[TASK-0165]]", "[[TASK-0166]]", "[[TASK-0167]]", "[[TASK-0168]]", "[[TASK-0169]]", "[[TASK-0170]]", "[[TASK-0171]]", "[[TASK-0172]]", "[[TASK-0173]]", "[[TASK-0175]]", "[[TASK-0176]]", "[[TASK-0177]]", "[[TASK-0178]]", "[[TASK-0179]]", "[[TASK-0180]]", "[[TASK-0181]]", "[[TASK-0188]]", "[[TASK-0189]]", "[[TASK-0190]]", "[[TASK-0191]]", "[[TASK-0192]]", "[[TASK-0193]]", "[[TASK-0194]]", "[[TASK-0195]]", "[[TASK-0196]]", "[[TASK-0197]]", "[[TASK-0198]]", "[[TASK-0213]]", "[[TASK-0343]]", "[[TASK-0344]]", "[[TASK-0345]]", "[[TASK-0346]]", "[[TASK-0347]]", "[[TASK-0348]]", "[[TASK-0349]]", "[[TASK-0350]]", "[[TASK-0351]]", "[[TASK-0352]]", "[[TASK-0353]]", "[[TASK-0354]]", "[[TASK-0355]]", "[[TASK-0356]]", "[[TASK-0628]]", "[[TASK-0638]]"]
issues:
  - "[[ISS-0312]]"
  - "[[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]"
  - "[[ISS-0105-The-Rail-Pulses-The-Same-For-Two-Minutes-And-Two-Hundred-Hours]]"
  - "[[ISS-0002]]"
  - "[[ISS-0003]]"
  - "[[ISS-0004]]"
  - "[[ISS-0005]]"
  - "[[ISS-0006]]"
  - "[[ISS-0007]]"
  - "[[ISS-0008]]"
  - "[[ISS-0009]]"
  - "[[ISS-0010]]"
  - "[[ISS-0011]]"
  - "[[ISS-0012]]"
  - "[[ISS-0013]]"
  - "[[ISS-0022]]"
  - "[[ISS-0023]]"
  - "[[ISS-0032]]"
depends: ["[[PHASE-006-Native-Cockpit-UI]]"]
related: ["[[RISK-0004-Hook-Injection-Surface]]", "[[FEAT-0013-Agent-State-Signal]]"]
---

# Phase 7: Agent instrumentation (hooks-aware terminal)

## Goal

Today the cockpit's agent awareness is voluntary: the LLM must remember to run `cockpit signal` / `cockpit focus` (FEAT-0013, prompted via COCKPIT.md). Meanwhile Claude Code and Codex CLI expose the same signals automatically and structured — Claude Code hooks can POST JSON to a localhost URL on every lifecycle event (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Notification`, `Stop`, `SessionEnd`), and Codex has an equivalent `hooks.json` plus a `notify` hook (`agent-turn-complete`, `approval-requested`). Because the desktop shell spawns the PTY itself, it can inject this instrumentation invisibly — no agent cooperation required, works even when the model forgets.

On top of that push feed, this phase builds the surfaces that make the cockpit an agent cockpit rather than a docs viewer with a terminal: a live activity strip, a cross-workspace needs-input inbox, dispatching TASK notes to the agent from the task board, and doc-traceability features (undocumented-work badge, session↔CHG linking) that only a tool that knows the project-os contract can offer.

## Scope

### In scope
- **FEAT-0019 — Agent hook ingestion.** New sidecar endpoint (`POST /api/agent-hook`), hook injection at PTY spawn for Claude Code (http hooks via settings injection) and Codex (`hooks.json` + `notify`), statusline forwarder for cost/context/rate-limit data, mapping hook events into the existing `CockpitState` agent-state machine and SSE fan-out. `cockpit signal` stays as the fallback for external terminals.
- **FEAT-0020 — Agent activity surfaces.** Activity strip above the terminal (current prompt, current tool + file, context-fill and cost meters), cross-workspace needs-input inbox with jump-to-terminal, live attribution trail in the nav (badge the note the agent just touched).
- **FEAT-0021 — Task dispatch.** "Start with agent" on TASK/ISS notes: type a templated prompt into the workspace PTY (agent choice: Claude Code / Codex), wired to follow mode so the dispatched work is visible end-to-end.
- **FEAT-0022 — Session insight and traceability.** Per-workspace session history browser (transcript JSONL on disk), undocumented-work badge (code edited but no TASK/ISS/CHG note touched this session), stamping session id/cost into CHG notes.

### Out of scope
- Inline diff review, PR auto-fix/auto-merge, embedded preview browsers, cloud execution — Claude Desktop, Codex app, and Conductor own that space; the cockpit stays a docs-first surface.
- Parallel worktree sessions / multi-PTY per workspace. Real architectural lift; deferred until single-agent instrumentation proves out.
- Editing notes from the cockpit (standing constraint — the cockpit is a viewer).
- Driving agents headlessly (`claude -p` / `codex exec`) from the cockpit. Dispatch types into the interactive PTY; owning a headless loop is a possible future phase.
- Support beyond Claude Code + Codex in v1 (opencode/Gemini/aider adapters can follow the same endpoint contract later).

## Exit Criteria
- [x] Launching `claude` inside the embedded terminal flips the workspace rail dot busy/waiting/needs-input with zero manual `cockpit signal` calls, and a permission prompt raises an OS notification within a second. Evidence: TST-0011 rows 1 and 2, 2026-09-25.
- [x] The activity strip shows the agent's current prompt, the file it is editing, and live cost/context meters during a real session. Evidence: TST-0011 rows 1, 3 and 7, 2026-09-25.
- [x] The needs-input inbox aggregates blocked agents across at least two workspaces and jumps to the right terminal on click. Evidence: TST-0011 rows 2 and 11, 2026-09-25.
- [x] A TASK note can be dispatched to the agent from the nav context menu and the resulting work is observable via follow mode. Evidence: TST-0011 rows 6 and 10, 2026-09-25.
- [x] A session that edits `src/**` without touching any TASK/ISS/CHG note shows the undocumented-work badge. Evidence: TST-0011 row 8, 2026-09-25.
- [x] `cockpit signal` / external-terminal behaviour unchanged (mode 1 and non-instrumented agents keep working). Evidence: TST-0011 rows 12 and 13, 2026-09-25.

## Notes
- **Sequencing.** FEAT-0019 first — it is the data pipe everything else consumes (same pattern as FEAT-0013 before FEAT-0010 in PHASE-006). Then FEAT-0020 (visible payoff), then FEAT-0021 and FEAT-0022 in either order.
- **Trust boundary.** `/api/agent-hook` accepts unauthenticated localhost POSTs; payloads must be treated as untrusted input (validated, size-capped, never rendered as HTML). See [[RISK-0004-Hook-Injection-Surface]].
- **Config etiquette.** Hook injection must not mutate the user's own `~/.claude` / `~/.codex` configuration; injection is per-spawn (env/flags/generated files under the app's own state dir). Codex hooks may require a one-time trust prompt in the TUI — surface that honestly in the UI.
- **Prior art** (researched 2026-07-05): Crystal/Nimbalyst session status indicators, Antigravity's Inbox for blocked agents, vibe-kanban's board-as-queue, Warp's per-tab agent status, Sculptor's session history. Differentiator here: the project-os knowledge graph — dispatch from durable TASK notes and guardrails that know the documentation contract.

## Close-out (2026-07-20)

All in-scope features and tasks are complete (FEAT-0018..0037 done, tasks 0114..0173 resolved). The phase's exit criteria above are left unchecked deliberately: they correspond to TST-0011, the manual live-agent e2e checklist (launch a real claude/codex, trigger a permission prompt, observe OS notifications) that the user chose to waive in favour of the automated verification performed across the 2026-07-20 sweep (instrumentation-pipeline smoke test against the sidecar, CDP UI checks, 409 identity guard, 218 passing unit tests, per-feature independent reviews). The criteria remain the record of what a human pass would confirm.

## Reopened 2026-08-06 — session economics

Set back to `active` for [[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]] and [[ISS-0104-Model-Switch-Discards-The-Warm-Cache]], rather than minting a phase for a two-item request (`CLAUDE.md`, "When to open a phase — and when not to"). Reopening is the documented move: set `active`, add the work, close it again.

This phase is the right home because it already owns the surface being extended. FEAT-0019's scope names the "statusline forwarder for cost/context/rate-limit data"; FEAT-0020's names "context-fill and cost meters" in the activity strip. What the new work adds is the fact those meters never carried: `ctx 62%` is fill against the window, and the strip's dollar figure is spend-to-date. Neither answers what the **next turn** costs, which depends on the prefix weight and whether the cache behind it is still warm.

The scope boundary added with this reopening: **no cache warming, ever.** A keep-warm ping costs 2× the full prefix each time against 2× once for letting it expire, so the obvious automation is a net cost. See FEAT-0081, "The automation that must not be built".

### Second round, same day — the rail learns an age

Reopened again for [[ISS-0105-The-Rail-Pulses-The-Same-For-Two-Minutes-And-Two-Hundred-Hours]]: the amber pulse meant "review this" with no notion of age, so a session waiting two minutes and one waiting 211 hours were the same pixels. Cold now reads grey and leaves the NEEDS YOU list, which gives the existing vocabulary a distinction rather than a third meaning.

The scope line this phase gained in the first round holds here too, and gained a sibling: **no new colour, animation or state class on the rail.** Cold takes the branch `decayed_from` already took. A surface that mints a state for each new fact is how a rail stops being readable, and ISS-0102 already recorded that lesson once.

### Closed 2026-08-06, after four review rounds

FEAT-0081 closed on an `approved` verdict from the fourth independent review, each round a fresh clean-context session. The arc is worth keeping because it is unusual and because the shape of it repeated:

- **Round 1** — seven findings, one high: API-error placeholders read as real turns, which corrupted the very statistic the feature was argued from. Also: eleven surviving mutants, and figures quoted as prose that could not be re-derived.
- **Round 2** — four findings. Judgment: *the code is fixed, the notes claim more than the code does.*
- **Round 3** — three findings, all documentation. Judgment: *the code is right and this verdict is not about it.*
- **Round 4** — approved, with six caveats written in as follow-ups rather than waived.

**The lesson is not "review more".** Every round after the first found the same defect — a claim written wider than the code — and it survived three attempts to fix it by being careful. What ended it was mechanical: `PARENT-BACKLINK`, then `SNAPSHOT-MEMBERSHIP`, and the discovery that the root cause was a string replace that silently no-opped because nothing asserted the match. A gate catches what diligence does not, and the review's own repetition was the evidence needed to justify building one.

## Reopened 2026-09-23 — Codex parity

The user's “Continue as suggested.” authorizes the bounded sequence in the [Codex parity review](../reference/codex-parity-review-2026-09-23.md). [[FEAT-0019]] and [[FEAT-0027]] reopen for [[TASK-0633]] through [[TASK-0637]]. The live Electron walk starts first. Existing terminal ownership remains unchanged, and [[PHASE-040]] stays deferred by the earlier decision. [[TASK-0631]] keeps its guided-walk handoff and status outside this phase.

The older unchecked criteria and their 2026-07-20 waiver remain historical evidence. They must be reconciled explicitly at the next phase close-out; this reopening does not convert them into a pass.

### Additional exit criteria for this follow-up

- [x] The complete live Codex lifecycle and dispatch walk is recorded, with any unrun rows still visible. Evidence: TST-0011 row 5 (2026-09-25) and the 2026-09-23 verification report.
- [x] Supported subagent and interruption events preserve parent state and queue safety. Evidence: [[TASK-0634]]; observed live 2026-09-23; TST-0010 passes.
- [x] External Codex instrumentation is an explicit settings opt-in with configuration preservation and duplicate suppression verified. Evidence: [[TASK-0635]]; observed live 2026-09-23; TST-0015 passes.
- [x] The usage-source investigation records a supported read-only path or a bounded unsupported conclusion. Evidence: [[TASK-0636]].
- [x] Guidance matches the delivered adapter, and enforcement differences are stated with evidence. Evidence: [[TASK-0637]].

## Exit criteria reconciled, 2026-09-25

The six July criteria were left unticked on 2026-07-20 because Edwin waived the live walk then; the 2026-09-23 reopening said that waiver would not count again. Edwin's live TST-0011 run on 2026-09-25 passed all 13 rows, and each criterion above now names the rows that meet it. The phase closes when FEAT-0019 and FEAT-0027 pass their fresh independent review.

## Closed again 2026-09-25

FEAT-0019 and FEAT-0027 are done after a shared review in two rounds. Round 2's one open item, a test that could not tell recency from priority, was answered and recorded on FEAT-0019. Every exit criterion above is ticked with its evidence, TST-0011 passed live on 2026-09-25, and nothing under this phase is open.

