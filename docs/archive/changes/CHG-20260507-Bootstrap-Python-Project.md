---
type: "[[change]]"
id: CHG-20260507-Bootstrap-Python-Project
aliases: ["CHG-20260507-Bootstrap-Python-Project"]
title: "Bootstrap Python project: pyproject.toml + src/docs_server/ scaffold"
status: merged
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: ["[[TASK-0001]]"]
commit: ""
pr: ""
impacts: ["pyproject.toml", "src/docs_server/"]
issues: []
features: ["[[FEAT-0001]]"]
related: ["[[TASK-0002]]", "[[TASK-0003]]"]
---

# Bootstrap Python project

## Summary
Adds the Python package scaffold required for every subsequent FEAT-0001 task.
A PEP 621 `pyproject.toml` declares the runtime dependencies (`markdown`,
`pymdown-extensions`, `python-frontmatter`, `pyyaml`, `watchdog`) and registers
a `docs-server` console script. The package itself lives under
`src/docs_server/` with stub modules (`server.py`, `renderer.py`, `index.py`,
`watcher.py`) and a working `__main__.py` that handles `--help` / `--version`.

## Impact
- New runtime dependency surface: `markdown`, `pymdown-extensions`,
  `python-frontmatter`, `pyyaml`, `watchdog`. Tracked under [[RISK-0002]] for
  schema-drift exposure.
- Minimum Python raised to 3.11 (declared in `pyproject.toml`,
  matches README). System Python 3.9 will not work.
- New entry points: `python -m docs_server` and the console script
  `docs-server` (both currently print `--help` and exit 0).
- Removed: `src/README.md` template placeholder — `src/docs_server/` now
  occupies that directory.
- No path/contract changes for downstream project-os consumers yet — the
  shim under `tools/docs-server/` in pilot repos has nothing to call into
  until TASK-0002 lands the render pipeline.

## Follow-ups
- [ ] TASK-0002 — implement the Markdown → HTML render pipeline; replace the
      `--help`-only stub with real CLI argument parsing.
- [ ] TASK-0003 — wikilink resolver.
- [ ] When the dep list stabilises (after TASK-0002 / TASK-0003), pin the
      lower bounds we actually rely on.
