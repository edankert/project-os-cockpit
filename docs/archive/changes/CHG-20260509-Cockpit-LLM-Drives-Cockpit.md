---
type: "[[change]]"
id: CHG-20260509-Cockpit-LLM-Drives-Cockpit
aliases: ["CHG-20260509-Cockpit-LLM-Drives-Cockpit"]
title: "Cockpit: agent drives cockpit — focus endpoint, CLI helper, Following toggle, discoverable URL"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: ["[[TASK-0048]]", "[[TASK-0049]]", "[[TASK-0050]]", "[[TASK-0051]]", "[[TASK-0052]]"]
commit: "19746cc..3044dc0"
pr: ""
impacts:
  - "src/project_os_cockpit/server.py"
  - "src/project_os_cockpit/cli.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "tools/instructions/COCKPIT.md"
  - "tools/skills/cockpit-driving/SKILL.md"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260523-Cockpit-Bi-Directional-State]]"]
---

# Cockpit: agent drives cockpit

> **Back-fill note (2026-05-23).** This CHG was not written at the time the work shipped (2026-05-09..05-22). Created retroactively to close the link graph — TASK-0048..0052 stub notes and CHG-20260523 reference this CHG. Authoritative record is git history (commit range `19746cc..3044dc0`).

## Summary
The cockpit became driveable by an LLM. The agent can broadcast a "focus here" instruction to every open cockpit tab via a small CLI (`cockpit focus <target>`), discoverable from any terminal under the project tree. Each tab can opt in or out via a Following / Manual toggle. When following, the cockpit auto-switches its left-nav mode so the agent's focus is also highlighted in the nav.

## Implementation roll-up

### Server (TASK-0048)
- New `POST /api/cockpit/focus` accepting `{target}` — resolves the target (note ID, docs-relative path, or cockpit URL) and broadcasts a `cockpit:focus` SSE event.
- `ControlEvent` dataclass added to the event bus alongside the existing `FileEvent`; SSE dispatcher branches on event type.

### CLI (TASK-0049)
- Tiny `cockpit` console script (`src/project_os_cockpit/cli.py`) registered via pyproject entry point.
- v1 had only `cockpit focus <target>`; `state` / `history` came later in TASK-0054.
- Discovery via `COCKPIT_URL` env (auto-set inside the embedded ttyd) with no fallback.

### Following toggle (TASK-0050)
- Header pill flips between Following / Manual. State persists in `localStorage`.
- Manual tabs ignore incoming `cockpit:focus` events.

### Discoverable URL + LLM directives (TASK-0051)
- Server writes `<project_root>/.cockpit/url` on startup, removes on shutdown via `atexit`.
- CLI walks up from CWD looking for the discovery file, falling back to `COCKPIT_URL` env. Multi-project safe.
- `tools/instructions/COCKPIT.md` + `tools/skills/cockpit-driving/SKILL.md` teach the LLM when to focus and when to stay silent.

### Follow-mode auto-switches nav (TASK-0052)
- When a `cockpit:focus` event arrives, the cockpit infers the appropriate left-nav mode from the target (TASK→tasks, FEAT/REQ/PHASE→features, ISS→issues, ADR/CHG/REL/RISK/TST/WF/PLAN→library) and switches to it before highlighting + scrolling the active item into view.

## What this unlocked
The bi-directional sync extension ([[CHG-20260523-Cockpit-Bi-Directional-State]]) layered the reverse direction on top of this same foundation: the agent could now also **read** what the user was looking at via `cockpit state`.

## Documentation Coverage (back-fill, 2026-05-23)
- features: covered (FEAT-0006)
- requirements: not-applicable
- tasks: TASK-0048..0052 (stub notes also back-filled 2026-05-23)
- issues: not-applicable
- tests: not-applicable (no dedicated tests landed at the time; manual browser verification)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: this note (back-fill)
- snapshot: TASK counter advanced 47→52, focus.task transitioned through TASK-0048..0052
