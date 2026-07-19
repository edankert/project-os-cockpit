---
type: "[[change]]"
id: CHG-20260706-Agent-Verbs
aliases: ["CHG-20260706-Agent-Verbs"]
title: "Agent verbs — drive the docs system from any note, with a dispatch queue"
status: merged
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
impacts:
  - "src/project_os_cockpit/agent_actions.py (new)"
  - "src/project_os_cockpit/server.py (/api/cockpit/actions)"
  - "desktop/src/main.ts (Agent submenu)"
  - "desktop/src/renderer/* (verb dispatch, queue, strip chip)"
features: ["[[FEAT-0024-Agent-Verbs]]"]
related: ["[[PHASE-007-Agent-Instrumentation]]", "[[TST-0013]]", "[[CHG-20260705-Agent-Instrumentation]]"]
---

# Agent verbs: notes are the nouns, skills are the verbs

## What shipped

**Verb registry (Python).** New `agent_actions.py`: per-type action tables — task (implement/refine/review/close-out), issue (fix/triage/reproduce), feature (break-down/implement-next/refine/close-out), requirement (implement/refine/verify), phase (groom/status-sweep/close-out), risk (mitigate/reassess) — each a prompt template with `{id}`/`{rel}` slots that sends the agent to the note first and to the relevant `tools/skills/*/SKILL.md`. Workspaces can override per type via `tools/adapters/cockpit/actions.yaml` (wholesale replace, malformed files ignored). Served by `GET /api/cockpit/actions`.

**Verb UI (desktop).** Context menus on nav rows, doc wikilinks, and scoped-overview feature rows grow an "Agent ▸" submenu listing the note type's verbs plus Claude Code / Codex preference radios. The top-bar ▶ now appears on TASK/ISS/FEAT/REQ/PHASE/RISK notes — click fires the default verb, context-click opens the full menu. `dispatchToAgent` resolves the verb template; the old hardcoded implement/fix prompt remains the fallback when the registry is unavailable.

**Dispatch queue.** Dispatching while the agent is busy or needs input enqueues (per-workspace) instead of pasting. Delivery is driven by the hook feed: at `Stop` the interactive CLI is still open, so the queued item is typed into the REPL as the next message; after `SessionEnd` it runs as a fresh `claude`/`codex` shell command. The activity strip shows a "queued N" chip (click to clear) and stays visible while work is queued.

## Why

The 2026-07-06 proposal: drive the LLM directly from the project-os docs — select a note, pick an action, the agent starts. The design insight is that project-os already defines the verbs: the skills playbooks are the action vocabulary. See [[FEAT-0024-Agent-Verbs]].

## Verification

- [[TST-0013]] passing (defaults, YAML override, malformed fallback, endpoint); full suite 179 passed, 1 skipped; `tsc` + build clean; live endpoint check against this repo's docs.
- Interactive pass (menus, ▶, queue delivery timing) rides on [[TST-0011]] step 11.
