# Plan — FEAT-0024 Agent verbs

1. **TASK-0131 (Python).** `agent_actions.py` registry + YAML override + `GET /api/cockpit/actions`; tests (TST-0013).
2. **TASK-0132 (renderer/main).** Fetch registry on sidecar ready; Agent submenu (verbs + agent radio) on nav rows / doc links / scoped feature rows; verb-aware ▶ button; `dispatchToAgent` gains verb resolution.
3. **TASK-0133 (renderer).** Per-workspace dispatch queue; auto-type on hook-fed Stop (REPL paste) / SessionEnd (shell command); queue chip in the strip.
