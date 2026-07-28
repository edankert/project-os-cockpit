# LLM Brief

## Project Identity
- Name: project-os-cockpit
- Purpose: A three-pane desktop cockpit that renders project-os Markdown notes on the fly — no build step — so a project's state, its agent sessions, and the decisions waiting on a human are readable at a glance. It is the tool the fleet is steered from, and the upstream that downstream repos consume through a thin shim under their own `tools/project-os-cockpit/`.
- Canonical runtime state: `SNAPSHOT.yaml`

## What it is for

Answering four questions without opening a file:

1. **Where is this project now?** — `~overview`: focus, counts, phases, and what is waiting on a human, all above the fold in a 900px window (REQ-0022).
2. **What is an agent doing right now?** — live session tracking from agent hooks: rail dots, activity strip, dispatch queue.
3. **What needs my decision?** — `~review`: proposals, questions, and manual test runs a human must actually perform.
4. **What should this look like?** — `~design`: design artifacts framed at the viewport the app runs at, with their revisions and the reasoning behind each.

## Read Order
1. `CONTEXT.md` — the operating contract
2. `SNAPSHOT.yaml` — what is active *right now*; read this before deciding anything
3. `docs/designs/DES-0002-Cockpit-Design-System.md` — what the UI should look like, and why
4. `docs/PHASES.md` and the active `docs/phases/PHASE-*.md`
5. `docs/ARCHITECTURE.md`

## High-Value Paths
- **Sidecar (Python):** `src/project_os_cockpit/` — `server.py` (routes), `cockpit.py` (payloads), `index.py` (the note index), `statuses.py` (the status vocabulary, single source), `note_writes.py` (guarded write-back)
- **Desktop shell (Electron/TS):** `desktop/src/main.ts`, `desktop/src/renderer/renderer.ts`, `desktop/src/ipc/`
- **Seeing the UI without Electron:** `desktop/harness/overview-harness.html` loads the real built bundle in a browser with the bridge stubbed
- Templates: `docs/__templates__/` · Playbooks: `tools/skills/` · Rules: `tools/instructions/`

## Invariants
- `SNAPSHOT.yaml` is canonical for active work state, and **notes are the authored source** (ADR-0009) — write a status once, in the note; `sync-snapshot.py` propagates it.
- **One vocabulary, one source.** The status palette lives in `statuses.py` and reaches CSS by generation, never retyping. This is the project's founding scar (ISS-0023) and the reason TST-0019 exists.
- **The render server binds `0.0.0.0`** so a tablet on the same Wi-Fi can read it; **every mutation endpoint is loopback-only.** Anything that writes, commits, or runs a command must call `_require_loopback()`.
- **Guarded write-back only.** Note edits go through `note_writes.py` — a field allow-list plus mtime preconditions. Widening the allow-list is a reviewed change, and a test asserts its exact contents.
- **The machine gathers; the human decides.** No verdict, review outcome, or acceptance box is ever stamped by an agent on a human's behalf.
- Do not introduce secrets or proprietary binaries.

## Typical Commands
- Run the desktop app: `cd desktop && npm start` (builds, then launches Electron)
- Run the sidecar alone: `python -m project_os_cockpit <docs-dir>`
- Tests: `.venv/bin/pytest -q` — **note the venv**; the system Python lacks the dependencies
- Typecheck / build the renderer: `cd desktop && npx tsc --noEmit -p .` / `npm run build`
- Validate the corpus: `bash tools/scripts/validate-docs.sh`
- Sync from upstream: `tools/scripts/sync-project-os.sh ../project-os`

## External Dependencies
- Python 3.11+ (sidecar), Node + Electron (shell), `git` (commits, design revisions and capture all shell out to it)
- No runtime dependency on a network service. The cockpit renders local Markdown and never phones home.

## Fast Failure Checks
- **Edited the renderer and the UI looks unchanged?** The bundle is stale — `cd desktop && npm run build`. A test guards this (`test_desktop_build_is_not_stale`) precisely because it is the easiest mistake to make here.
- **A payload looks right but the surface is empty?** Check the surface is *reachable*. The design bench shipped twice with no working route to it, and every test passed both times.
- Run `bash tools/scripts/validate-docs.sh` before committing; the same validator runs at pre-commit and in CI.
- After changing anything template-owned (`tools/instructions/`, `tools/skills/`), run `python3 tools/scripts/generate-adapters.py` or the pre-commit hook will refuse the commit.

## Things that will surprise you
- **`tools/` is template-owned.** Edits there belong upstream in `~/Dev/repos/project-os/` and are overwritten by the next sync. A cockpit-local skill placed in `tools/skills/` is silently lost.
- **The validator ships twice** — `tools/scripts/validate-docs.py` and `src/project_os_cockpit/validate_docs_bundled.py`, kept byte-identical so the app can validate a repo carrying no copy of its own.
- **`statuses.py` keeps retired values on purpose** (`LEGACY_STATUS_BAND`) so an unmigrated downstream repo still renders in the right colour while still failing validation. Membership and rendering are deliberately different questions (ADR-0008).
