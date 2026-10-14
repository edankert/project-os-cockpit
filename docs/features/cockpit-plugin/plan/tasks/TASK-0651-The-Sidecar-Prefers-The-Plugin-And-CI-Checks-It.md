---
type: "[[task]]"
id: TASK-0651
aliases: ["TASK-0651"]
title: "The sidecar ignores a second capture of a plugin session, CI validates and tests the plugin, and the record is updated"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]], candidate tasks 6-7"]
parent: "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
effort: "S"
due: ""
depends: ["[[TASK-0649-The-Cockpit-Plugin-Posts-Every-Claude-Event-To-The-Sidecar]]"]
blocks: []
related: ["[[FEAT-0027]]", "[[RISK-0004-Hook-Injection-Surface]]"]
tests: []
---

# The sidecar prefers the plugin, and CI checks it

## Definition of Done

- [x] When the tracker has accepted a post marked `_cockpit_plugin` for a session, it ignores an unmarked Claude post for that session (open question 1, option b). The two-second window stays. A pytest shows both, and that a Codex post is unaffected.
- [x] The `observed-coverage` workflow installs `@anthropic-ai/claude-code@2.1.299` and runs `claude plugin validate` and `claude plugin test` on the plugin, failing the build on either.
- [x] `docs/reference/cockpit-capability-register.md` has a row and a maintenance line for the change, in the same commit as the change note.
- [x] A change note describes what a person notices: their own status line is back in a cockpit terminal, and the rail's figures update at the end of a turn.
- [x] RISK-0004 names the plugin path, the version pin and the `~/.claude` test.
- [x] The issue for the older-version warning is filed (plan, open question 2).
- [x] The acceptance check is `active`, its Setup and Steps matching what was built.
- [x] `python3 -m pytest -q`, `node --test desktop/tests/*.test.mjs`, `npm run typecheck` and `bash tools/scripts/validate-docs.sh` are green.

## Result, 2026-10-14

- **The claim.** `agent_hooks.py` `PLUGIN_MARK`. A marked post sets `plugin_claimed` on its session; after that an unmarked Claude post for the session returns `ignored` and `duplicate`. `tests/test_agent_hooks.py::test_plugin_session_ignores_the_external_hooks_second_capture` covers it, Codex and another session included, and fails when the drop is removed.
- **CI.** A step in `observed-coverage.yml` after the renderer build. Both commands exit 1 on failure (checked with a broken copy of the plugin) and run with an empty HOME and no login. It has not run on GitHub, because nothing is pushed.
- **Record.** [[CHG-20261014-Claude-Sessions-Report-Through-The-Cockpit-Plugin]], the register row `shell.agents.claude-plugin`, RISK-0004's 2026-10-14 section, and [[ISS-0318-An-Older-Claude-Code-Leaves-A-Cockpit-Session-Unreported-Without-A-Word]].
- **Suite.** `python3 -m pytest -q`: 2143 passed, 11 skipped. `node --test desktop/tests/*.test.mjs`: 193 passed. `npm run typecheck`: clean. `validate-docs.sh`: OK.
