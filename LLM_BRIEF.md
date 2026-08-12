---
type: reference
id: LLM-BRIEF
owner: user:edwin
created: 2026-05-08
updated: 2026-08-12
tags: [llm, brief]
---

# LLM Brief

## Project Identity

- Name: project-os-cockpit
- Purpose: A three-pane desktop cockpit that renders project-os Markdown notes on the fly — no build step — so a project's state, its agent sessions, and the judgments waiting on a person are all visible from one surface. It renders **ten repos** on this machine, one sidecar each, and installs nothing into any of them.
- Canonical runtime state: `SNAPSHOT.yaml`

## What it is for

One sentence, and every feature serves a clause of it:

> The cockpit is how a person governs a project they did not write. It must not be able to say something false about that project without saying so — and everything it shows as owed must be theirs to discharge.

In practice, five questions answered without opening a file:

1. **Where is this project now?** — `~overview`: what changed since you looked, what is unpushed, focus, counts, phases.
2. **What needs me?** — the badge on every view button, the `Needs you` group at the top of its navigator, and the view's own landing page. One walk of one predicate feeds all three.
3. **What is an agent doing right now?** — live sessions from Claude Code hooks: rail state, activity strip, cost, context, the notes it is touching.
4. **What should this look like?** — `~intent`: the standing documents, designs, decisions and risks, with what each owes marked in place.
5. **Is it shippable?** — `~tests`: the `TST-*` register and the tiered acceptance suite whose gate blocks a release.

## Read Order

1. `CONTEXT.md` — the operating contract and edit policy
2. `SNAPSHOT.yaml` — what is active *right now*; read before deciding anything
3. `docs/ARCHITECTURE.md` — two processes and a fleet, and which module owns what
4. `docs/GLOSSARY.md` — the words this project uses in a particular way
5. `docs/DESIGN.md` — the rules that decide arguments here
6. `docs/PHASES.md` and the active `docs/phases/PHASE-*.md`

## High-Value Paths

- **Sidecar (Python, 40 modules):** `src/project_os_cockpit/` — `server.py` (63 API routes + the loopback guard), `cockpit.py` (payloads), `index.py` (the note index), `note_writes.py` (**the only write path**), `statuses.py` (the status vocabulary, single source), `obligations.py` (what is owed, of what kind, to which view), `acceptance.py` (the tier suite and the release gate)
- **Desktop shell (Electron/TS):** `desktop/src/main.ts`, `desktop/src/renderer/renderer.ts` (~15k lines, one module by design), `desktop/src/ipc/` (13 modules: workspaces, sidecar, terminal, git, agent state)
- **Seeing the UI without Electron:** `desktop/harness/live-harness.html` runs the built bundle against a **real** sidecar. Its sibling `overview-harness.html` stubs the sidecar with captured fixtures — right for a layout, useless for verifying anything, because it shows the payloads of the day it was written.
- Templates: `docs/__templates__/` · Playbooks: `tools/skills/` · Rules: `tools/instructions/`

## Invariants

- `SNAPSHOT.yaml` is canonical for active work state, and **notes are the authored source of state** (ADR-0009): write a status once, in the note; `sync-snapshot.py` propagates it at pre-commit.
- **One vocabulary, one source.** Statuses live in `statuses.py`, obligations in `obligations.py`, and `tests/test_status_vocabulary.py` checks six consuming surfaces against them. Eight independent copies is what ISS-0023 was.
- **The render server binds `0.0.0.0`** so a tablet can read; **every write is loopback-only** (REQ-0027), enumerated from the dispatch table so an endpoint that forgets the guard fails the suite by existing. ADR-0010 decided that parity across surfaces is the goal and **an authenticated write path (REQ-0034) is its precondition** — an accepted direction, not a licence to drop a guard early.
- **Guarded write-back only.** Every edit goes through `note_writes.py`: resolve by id, check loopback, check an mtime precondition, touch only the field or line in question.
- **The machine gathers; the human decides.** No verdict, review outcome or acceptance is ever written by an agent (REQ-0026).
- **Publishing is a person's act.** The tool commits and never pushes on its own initiative; deploy remotes are refused everywhere (FEAT-0055). ADR-0022 permits a delegate to push to non-deploy remotes; the deploy refusal is untouched.
- **Absent, never zero.** A count of nothing is not rendered.
- Do not introduce secrets or proprietary binaries.

## Typical Commands

- Run the desktop app: `cd desktop && npm start` (builds, then launches Electron)
- Run the sidecar alone: `python -m project_os_cockpit <docs-dir>`
- Tests: `.venv/bin/pytest -q` — **note the venv**; the system Python lacks the deps. 1235 tests, 69 modules.
- Typecheck / build the renderer: `cd desktop && npx tsc --noEmit -p .` / `npm run build`
- Validate the corpus: `bash tools/scripts/validate-docs.sh`
- Commit at close-out: `bash tools/scripts/close-out-commit.sh <paths…> -m "…"` — **name the paths**; it refuses none
- Sync from upstream: `tools/scripts/sync-project-os.sh ../project-os`

## External Dependencies

- Python 3.11+ (sidecar), Node + Electron (shell), `git` (commits, design revisions, fleet state)
- No runtime dependency on a network service. The cockpit renders local Markdown and talks to nothing off the machine.

## Fast Failure Checks

- **Edited the renderer and the UI looks unchanged?** The bundle is stale — `cd desktop && npm run build`. And the *running window* reads its bundle once at creation: `GET /api/cockpit/runtime` says whether the process is older than the code.
- **A payload looks right but the surface is empty?** Check the surface is *reachable* and that the stage is not still hidden — a correct page in a `hidden` pane renders blank while every DOM assertion passes.
- **A count is zero that should not be?** Data computed asynchronously must re-render the surface that needs it. Three features shipped broken this way in one day.
- Run `bash tools/scripts/validate-docs.sh` before committing; the same validator gates pre-commit and CI.
- After changing anything template-owned (`tools/instructions/`, `tools/skills/`, `tools/scripts/`), the edit belongs **upstream** — see below.

## Things that will surprise you

- **`tools/` is template-owned.** Edits there belong in `~/Dev/repos/project-os/`, and a local edit is reverted by the next sync.
- **Upstream is TWO repos and no citation says which.** `project-os` is the template; **`project-os-dev` holds every upstream ADR** — `ADR-0011`, `ADR-0013` and sixteen others live there, cited in 41 files here and absent from both repos a reader would look in (ISS-0123). A note in another project is `[[project-os-dev#ADR-0011]]` (ADR-0024).
- **The validator ships twice** — `tools/scripts/validate-docs.py` and `src/project_os_cockpit/validate_docs_bundled.py`, the second a verbatim copy so a repo without its own still gets a verdict.
- **`statuses.py` keeps retired values on purpose** (`LEGACY_STATUS_BAND`) so an unmigrated corpus still renders; rendering tolerance is not permission, and the validator still refuses them.
- **A reconciled check is `- [~]`** — settled by decision, not walked. It does not block a release and is counted and named separately (ISS-0141).
- **This session's own transcript is evidence.** The acceptance suite has been walked from inside the cockpit's embedded terminal, and `.cockpit/sessions.json` records what each session touched.
