---
type: "[[feature]]"
id: FEAT-0024
aliases: ["FEAT-0024"]
title: "Agent verbs — drive the docs system from any note"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
verification_waiver: "TST-0011 is a manual live-agent e2e checklist; user accepted automated verification in lieu of the manual pass (see 2026-07-20 sweep). Independent review verdict CLOSE."
goal: "Any project-os note becomes a command surface: select a phase/feature/requirement/task/issue/risk, pick a verb (implement, fix, refine, break down, groom, mitigate, …), and the agent starts that work in the terminal — with the verbs defined by the project-os skill playbooks, and dispatches queued automatically when the agent is busy."
requirements: []
tests: ["[[TST-0013]]", "[[TST-0011]]"]
tasks: ["[[TASK-0131]]", "[[TASK-0132]]", "[[TASK-0133]]"]
related: ["[[FEAT-0021-Task-Dispatch]]", "[[FEAT-0019-Agent-Hook-Ingestion]]"]
---

# Agent verbs

## Why

FEAT-0021 shipped the primitive: right-click a TASK/ISS → templated prompt into the PTY. This generalises it on two axes — all note types, multiple verbs — with the insight that project-os already defines the verbs: the skills under `tools/skills/` (task-breakdown, backlog-grooming, risk-mitigation-planning, close-out, …) are the action vocabulary, written as LLM playbooks. Notes are the nouns, skills are the verbs, the agent is the executor. Competing agent managers can't copy this because their cards carry no methodology.

## Scope

1. **Verb registry + endpoint** (TASK-0131). Built-in per-type action table (task: implement/refine/review/close-out; issue: fix/triage/reproduce; feature: break-down/implement-next/refine/close-out; requirement: implement/refine/verify; phase: groom/status-sweep/close-out; risk: mitigate/reassess) with prompt templates referencing the note and the relevant SKILL.md. Optional downstream override via `tools/adapters/cockpit/actions.yaml`. Served by `GET /api/cockpit/actions`.
2. **Verb UI** (TASK-0132). Context-menu "Agent ▸ <verbs>" submenu on nav rows, doc links, and scoped-overview feature rows; the top-bar ▶ dispatches the type's default verb (context-click for the menu) and appears on all dispatchable note types; agent preference (Claude Code / Codex) as radio entries in the submenu.
3. **Queue-on-busy** (TASK-0133). Dispatch while the agent is busy/needs-input enqueues instead of pasting; the hook feed's `Stop`/`SessionEnd` transitions auto-type the next queued prompt (into the live REPL after `Stop`, as a fresh shell command after `SessionEnd`); queue chip with count in the activity strip.

## Out of scope

- Headless (`claude -p`) execution — dispatch stays in the interactive PTY where the user can steer.
- Auto-status transitions from the dispatcher — the agent updates statuses per the lifecycle.
- Editing the verb registry in-app.

## Acceptance

- Right-clicking a FEAT note offers Break down / Implement next / Refine / Close out; picking one types the templated, skill-referencing prompt into the terminal.
- The registry endpoint serves built-ins and honours a `tools/adapters/cockpit/actions.yaml` override (verified by test).
- Dispatching while the agent is busy queues; when the session hits Stop the queued prompt is typed into the live REPL; after SessionEnd it runs as a fresh `claude`/`codex` command; the strip shows the queue count.
- The ▶ button appears on TASK/ISS/FEAT/REQ/PHASE/RISK notes and fires the default verb.
