---
type: "[[task]]"
id: TASK-0001
aliases: ["TASK-0001"]
title: "Bootstrap Python project (pyproject.toml, deps, package layout)"
status: doing
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: S
due: ""
depends: []
blocks: [TASK-0002, TASK-0003]
related: []
tests: []
---

# Bootstrap Python project

## Definition of Done
- [ ] `pyproject.toml` with project metadata + runtime dependencies (`markdown`, `pymdown-extensions`, `python-frontmatter`, `pyyaml`, `watchdog`).
- [ ] Source layout under `src/docs_server/` with `__init__.py`, `__main__.py`, and stub modules for `server.py`, `renderer.py`, `index.py`, `watcher.py`.
- [ ] `python -m docs_server --help` prints usage and exits 0.
- [ ] `pip install -e .` installs cleanly into a venv.
- [ ] `.gitignore` covers `__pycache__/`, `*.egg-info/`, `.venv/`, `dist/`, `build/`.

## Steps
- [ ] Create `pyproject.toml` (PEP 621) with `name = "docs-server"`, entry point `docs-server = "docs_server.__main__:main"`.
- [ ] Create `src/docs_server/` with empty stub modules.
- [ ] Implement `__main__.main()` to parse `--help` only (real CLI parsing comes with TASK-0002).
- [ ] Add `.gitignore`.
- [ ] Smoke-test in a fresh venv.

## Notes
Pure scaffolding. Once this lands, every subsequent task has an importable package to extend.
