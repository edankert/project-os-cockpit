---
type: "[[feature]]"
id: FEAT-0022
aliases: ["FEAT-0022"]
title: "Session insight — history browser, doc-traceability guardrail, CHG linking"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
verification_waiver: "TST-0011 is a manual live-agent e2e checklist (real claude/codex launch, permission prompt, OS notification). User accepted the automated verification in lieu of the manual pass on 2026-07-20: instrumentation-pipeline smoke test (generated scripts → sidecar tracker), CDP UI checks, 409 sidecar-identity guard, 217 passing unit tests, and an independent review verdict of CLOSE for all five."
goal: "Turn agent sessions into part of the project record: browse past sessions per workspace (prompts, duration, cost, files touched), flag undocumented work live, and link CHG notes to the sessions that produced them."
requirements: []
tests: ["[[TST-0010]]", "[[TST-0011]]"]
tasks: ["[[TASK-0123]]", "[[TASK-0124]]", "[[TASK-0125]]", "[[TASK-0126]]", "[[TASK-0127]]"]
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0018-Verification-Health-Surface]]"]
---

# Session insight and traceability

## Why

project-os's whole premise is that work leaves a durable, linked record — but agent sessions, where most of the work now actually happens, leave no trace in the system. The raw material exists: Claude Code writes transcript JSONL to disk continuously (the exact path arrives in every hook payload as `transcript_path`), and Codex keeps rollout files under `~/.codex/sessions/`. Most competing tools ignore session history (Sculptor and Nimbalyst are the strongest); none can connect it to a documentation contract. This feature also gives project-os teeth: the document-first rule is currently enforced only by convention.

## Goal

Sessions become browsable history connected to the project-os graph, and the cockpit notices — live — when agent work bypasses the documentation system.

## Scope

1. **Session index.** The sidecar (or shell) records per-session metadata as sessions run, keyed by hook events: session id, agent, start/end, prompts, files touched, cost (from the statusline feed), transcript path. Persisted under `.cockpit/` per workspace; transcript files themselves stay where the CLIs put them and are read lazily. Treat transcript schemas as version-unstable — parse defensively, degrade to metadata-only.
2. **Session history browser.** A "Sessions" section (library nav group or dedicated surface): list of past sessions with prompt summary, duration, cost, files touched; selecting one shows the detail view. Read-only.
3. **Undocumented-work badge.** Live rule evaluated per session: source files edited (outside `docs/`) but no TASK/ISS/CHG note touched → amber badge on the workspace rail square and activity strip. Clears when a docs note is touched or the session ends with docs updates.
4. **Session ↔ CHG linking.** When a CHG note appears during or shortly after a live session, record the session id + cost against it in the session index, and surface "produced by session … ($…)" in the CHG note's rendered metadata area. Cockpit-side enrichment only — the note file is not modified.

## Out of scope

- Rendering full conversation transcripts (v1 shows metadata + prompt summaries; full transcript rendering is a follow-up).
- Retention management of the CLIs' own transcript files (30-day default stays theirs).
- Blocking anything — the guardrail informs, never prevents.
- Cross-workspace session analytics/aggregate cost dashboards (possible later, needs the index first).

## Acceptance

- After two real sessions in a workspace, the browser lists both with prompt summary, duration, cost, and files touched; detail view opens for each.
- A session that edits `src/**` without touching any TASK/ISS/CHG note shows the amber badge within SSE latency; adding a CHG note clears it.
- A CHG note created during a session renders "produced by" session metadata without the note file being modified.
- Everything degrades gracefully when transcripts are missing, truncated, or schema-shifted (metadata-only fallback, no errors surfaced).

## Links

- Tasks: to be broken down (`plan/PLAN.md`)
- Feed: [[FEAT-0019-Agent-Hook-Ingestion]] (`transcript_path`, tool events, statusline cost)
- State home: `.cockpit/` per workspace (`src/project_os_cockpit/server.py`)
