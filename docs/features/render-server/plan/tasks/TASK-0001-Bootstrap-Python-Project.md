---
type: "[[task]]"
id: TASK-0001
aliases: ["TASK-0001"]
title: "Bootstrap Python project (pyproject.toml, deps, package layout)"
status: done
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
- [x] `pyproject.toml` with project metadata + runtime dependencies (`markdown`, `pymdown-extensions`, `python-frontmatter`, `pyyaml`, `watchdog`).
- [x] Source layout under `src/docs_server/` with `__init__.py`, `__main__.py`, and stub modules for `server.py`, `renderer.py`, `index.py`, `watcher.py`.
- [x] `python -m docs_server --help` prints usage and exits 0.
- [x] `pip install -e .` installs cleanly into a venv.
- [x] `.gitignore` covers `__pycache__/`, `*.egg-info/`, `.venv/`, `dist/`, `build/`.

## Steps
- [x] Create `pyproject.toml` (PEP 621) with `name = "docs-server"`, entry point `docs-server = "docs_server.__main__:main"`.
- [x] Create `src/docs_server/` with empty stub modules.
- [x] Implement `__main__.main()` to parse `--help` only (real CLI parsing comes with TASK-0002).
- [x] Add `.gitignore` (already in place from repo bootstrap — no changes needed).
- [x] Smoke-test in a fresh venv.

## Notes
Pure scaffolding. Once this lands, every subsequent task has an importable package to extend.

Verified on Python 3.13.13 (Homebrew `python@3.13`). System Python is 3.9.6;
the project requires 3.11+, so a versioned interpreter must be used. The
verifying venv lives at `.venv/` (already gitignored).

`__main__.main()` also accepts `--version` for free — printing it is the
cheapest non-trivial signal that the package is wired up correctly.

The placeholder `src/README.md` left over from the project-os template was
removed — `src/docs_server/` now occupies that directory.
