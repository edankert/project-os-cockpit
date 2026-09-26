---
type: "[[task]]"
id: TASK-0078
aliases: ["TASK-0078"]
title: "`cockpit signal <state>` CLI subcommands"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0013"
effort: ""
due: ""
depends: ["[[TASK-0077]]"]
blocks: ["[[TASK-0079]]"]
related: []
tests: []
---

# `cockpit signal <state>` CLI

## Definition of Done
- [ ] New `signal` subparser on the `cockpit` CLI with nested
      choices: `busy`, `waiting`, `done`, `error`, `idle`.
- [ ] Common flags:
      - `--target ID` (any state) — note ID / path the agent is
        working on or blocked by.
      - `--agent NAME` (any state) — `claude`, `codex`, `aider`,
        etc.; freeform string.
      - `--message TEXT` (mainly `waiting` / `error`) — short human
        reason.
- [ ] Each subcommand POSTs to `/api/cockpit/agent-state` with the
      composed body; the existing `_post_json` helper is reused.
      Discovery follows `COCKPIT_URL` / `.cockpit/url` (existing
      behaviour).
- [ ] Output mirrors `cockpit focus` style:
      `cockpit signal -> busy` (single-line ack) on 2xx; non-zero
      exit on failure with the server's error string on stderr.
- [ ] Parser-level tests in `tests/test_cli_signal.py` confirm the
      body composed for each subcommand matches the spec.

## Steps
- [ ] Extend `_build_parser` / the existing subparsers block in
      `src/project_os_cockpit/cli.py`. Look at how `focus` and
      `state` subparsers are wired; mirror that pattern.
- [ ] Implement `cmd_signal(args)`.
- [ ] Tests with monkeypatched `_post_json` to capture body.

## Notes
The CLI lives in `cli.py`; the server lives in `server.py`. The CLI
is shipped as a `[project.scripts]` entry already (`cockpit =
project_os_cockpit.cli:main`), so the new subcommand becomes
available system-wide once the package is reinstalled (or via
`pip install -e .`).
