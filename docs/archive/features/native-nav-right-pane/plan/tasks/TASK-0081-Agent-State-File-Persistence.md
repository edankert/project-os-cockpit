---
type: "[[task]]"
id: TASK-0081
aliases: ["TASK-0081"]
title: "Persist agent-state to `<project-root>/.cockpit/agent-state.json` (FEAT-0013 amendment)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[FEAT-0013-Agent-State-Signal]]"]
parent: "FEAT-0010"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0082]]"]
related: []
tests: []
---

# Agent-state file persistence

## Definition of Done
- [ ] Every `CockpitState.record_agent_state(...)` call writes the
      same payload to `<project-root>/.cockpit/agent-state.json`
      (best-effort — log on failure, don't raise).
- [ ] On startup, `DocsServer.__init__` loads the file if present
      and seeds `CockpitState._agent_state` so a restart doesn't
      lose the last known state.
- [ ] The decay thread also rewrites the file on its synthetic
      flip to `idle` so external readers (the rail in TASK-0082)
      see the same observable state the SSE consumers see.
- [ ] `.cockpit/agent-state.json` written in **all** modes
      (including desktop — distinct from `.cockpit/url`, which is
      suppressed because of the multi-cockpit ambiguity; the
      state file has no such ambiguity, it's just last-known
      state).
- [ ] Tests in `test_agent_state.py`: file written on POST, file
      contents match the SSE payload, file rewritten on decay,
      restart re-loads.

## Steps
- [ ] Extend `CockpitState.__init__` to accept an optional
      `state_path: Path` it will use for read/write. Default `None`
      = no persistence (keeps unit tests simple).
- [ ] Wire `DocsServer.__init__` to pass
      `self.docs_root.parent / ".cockpit" / "agent-state.json"`.
- [ ] In `record_agent_state` + the decay path: `try: …
      write_text(json.dumps(payload)) except OSError: log.warning`.
- [ ] In `__init__`: if state file exists, `json.loads` and seed
      `_agent_state`. Tolerate junk JSON.

## Notes
The desktop rail polls these files (TASK-0082); no SSE round-trip
needed for cross-workspace state. The file is gitignored by the
same `.cockpit/` pattern that already exists for `.cockpit/url`
(repo's `.gitignore` already covers `.cockpit/`).

This is a small amendment to FEAT-0013, not a breaking change —
no schema bump required. The SSE event remains the source of
truth for live updates within a single workspace; the file is the
fallback / cross-workspace channel.
