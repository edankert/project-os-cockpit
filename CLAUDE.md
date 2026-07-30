# Project: project-os-cockpit

Read SNAPSHOT.yaml at session start to understand current project state and focus.
Read CONTEXT.md for the full project-os contract, edit policy, and invariants.

## What this repo is

`project-os-cockpit` is a small Python server that renders project-os Markdown notes as a three-pane cockpit UI — on the fly, no build step — plus an Electron shell (mode 3) that hosts one server per repo.

**Repos are consumed by discovery, not by a shim.** The shell finds every `SNAPSHOT.yaml`-bearing repo under `~/Dev/repos/` (12 at present) and spawns a sidecar per workspace; from a terminal, `python -m project_os_cockpit <repo>/docs` does the same for one repo. Nothing is installed into a downstream repo.

*(Corrected 2026-07-30, [[ISS-0078]]. This paragraph used to say the tool was consumed "via a thin shim under their own `tools/project-os-cockpit/`" and named `your-applications.com` as the pilot integration point. **That directory has never existed in any fleet repo.** The shim was [[PHASE-003]]'s plan, and workspace discovery ([[PHASE-005]]) replaced the need before it was built — so this file spent months pointing every session at something that was not there.)*

## project-os documentation system (core rules -- always active)

@tools/instructions/LIFECYCLE.md

## Reference instructions (read when relevant)

These files contain detailed rules. Read them when performing the related operation:
- Status values and transitions: tools/instructions/STATUSES.md
- Quality gates and close-out checks: tools/instructions/QUALITY.md
- Snapshot structure and update rules: tools/instructions/SNAPSHOT.md
- Allowed taxonomy values: tools/instructions/TAXONOMY.md
- Required link graphs: tools/instructions/TRACEABILITY.md
- ADR conventions: tools/instructions/DECISIONS.md
- Ownership rules: tools/instructions/OWNERSHIP.md
- Obsidian conventions: tools/instructions/OBSIDIAN.md
- Handoff/recovery: tools/instructions/HANDOFF.md
- Importing from existing projects: tools/instructions/IMPORTING.md
- Syncing template updates: tools/instructions/SYNCING.md
- Hook contracts: tools/instructions/HOOKS.md
- Cockpit driving (LLM in any terminal): tools/instructions/COCKPIT.md

## Skill playbooks (read before performing these operations)

- Issue intake: tools/skills/issue-intake/SKILL.md
- Feature scaffold: tools/skills/feature-scaffold/SKILL.md
- Task breakdown: tools/skills/task-breakdown/SKILL.md
- Close-out: tools/skills/close-out/SKILL.md
- Change note: tools/skills/change-note/SKILL.md
- Status transition: tools/skills/status-transition/SKILL.md
- Snapshot sync: tools/skills/snapshot-sync/SKILL.md
- ADR authoring: tools/skills/adr-authoring/SKILL.md
- Risk scan: tools/skills/risk-scan/SKILL.md
- Independent review: tools/skills/independent-review/SKILL.md
- Docs audit: tools/skills/docs-audit/SKILL.md
- Ad-hoc intake: tools/skills/ad-hoc-intake/SKILL.md
- Backlog grooming: tools/skills/backlog-grooming/SKILL.md
- Risk mitigation: tools/skills/risk-mitigation-planning/SKILL.md
- Impact analysis: tools/skills/impact-analysis/SKILL.md
- Adapter sync: tools/skills/adapter-sync/SKILL.md
- Cockpit driving: tools/skills/cockpit-driving/SKILL.md

## Model routing (lifecycle phase → model)

Models are pinned to lifecycle phases via subagents (FEAT-0039, upstreamed as project-os HC-008). The main session runs on Opus (`model` in `.claude/settings.json`) and does the implementation. Preflight/planning (LIFECYCLE steps 1–5) is delegated to the `planner` subagent (`.claude/agents/planner.md`, pinned to `claude-fable-5`). Close-out review (LIFECYCLE step 8) and ad-hoc review requests are delegated to the `independent-reviewer` subagent (`.claude/agents/independent-reviewer.md`, same pin). The `UserPromptSubmit` hook `tools/adapters/claude-code/hooks/model-routing-hint.sh` injects a routing hint derived from the SNAPSHOT focus item's status; follow it unless the prompt clearly says otherwise.

**Independence is clean context, not model family** ([[ADR-0013]], QUALITY.md line 49). A session that starts from the notes and the diff alone — never the author's reasoning trace, never the session that authored the work — satisfies the review gate regardless of which model runs it. A human pass also satisfies it and remains the strongest option. There is **no cross-vendor requirement**; the rule that there was one was retired after an experiment refuted its premise. Keeping the reviewer on a different pin is therefore a preference, not a gate.

Watch out on resume: a resumed session keeps the model its transcript was saved with, *regardless* of the `model` pin above. Resuming a Fable session leaves you on Fable. That is a **routing** surprise, not a review problem — per ADR-0013 the reviewer's model is not the gate, so sharing a model with the reviewer breaks nothing. Check with `/model` after resuming, or start a fresh session to get the pinned default.

Canonical ownership of these files is upstream in `~/Dev/repos/project-os/`: the hook is a hand-written adapter hook under `tools/adapters/claude-code/hooks/`, and both agent files are emitted by upstream's `tools/scripts/generate-adapters.py`. Edit them upstream, not here. The copies here are byte-identical to upstream's, but note that `sync-project-os.sh` copies `tools/` and never touches `.claude/`, and this repo carries no generator — so the agent files can only be refreshed by re-copying them, and nothing here detects drift.

## When to open a phase — and when not to (ISS-0077)

`LIFECYCLE.md` says when a phase note is **needed**. It never says when one is **too small**, and on 2026-07-30 that gap produced nine phases in a day against nine in the preceding twelve weeks, at a fifth of the size (median 4 items against 21).

The cause is structural, not careless: the document-first rule needs a focus item before code changes, and an open phase is the cheapest way to get one. So every new request minted a phase.

**Open a phase when both hold:**

1. You can state its goal **without listing its parts**. "Fleet surfaces — the cockpit reports on every repo it can see" passes. "Show the phase ID next to the title" does not; that is a sentence about one change.
2. Its exit criteria are something other than **"the tasks are done"**. A phase whose criteria restate its task list is a task list with a heading.

**Do not open one for** a single request, a single issue, or anything you will finish in the same session. Those get an `ISS-*` or a task inside a **standing phase** for the surface they touch.

**A standing phase is the mechanism that prevents this** — one *known* phase per durable surface (the overview, the fleet, the record itself) that small fixes join, so minting a phase is the exception rather than the only move.

**A standing phase is `done` when idle and reopened when work arrives.** It is *not* left permanently `active`. That was the first formulation, and it lasted about an hour: `PHASE-015` was converted to a standing phase, immediately rendered `unclosed: true` — every item resolved, phase not closed — and so displayed a permanent **"close out"** nag on the overview. A phase that never closes but whose work is finished will always look like a phase someone forgot.

Reopening is cheap and honest: set it back to `active`, add the issue, close it again. The status then means what it says at every moment, and the home is still known.

**A phase closing with ≤3 items is a signal**, not a small success: it should probably have joined something. Check before closing, not after.

### Merging, when it has already happened

Do not delete. `superseded` is a terminal phase status ([[ADR-0008]]) and expresses this exactly:

1. **Re-home the children first** — a superseded phase with unresolved children fires `PHASE-CHILDREN`.
2. Set the absorbed phases to `superseded` with `superseded_by:`, and keep their notes as the record of each leg.
3. Widen the surviving phase's goal, `features:`/`issues:`, and add `supersedes:`.
4. Update `docs/PHASES.md` and the `phase:` entries in `SNAPSHOT.yaml` — `sync-snapshot.py` propagates status but **not** `phase`.

Worked example: PHASE-016 absorbed PHASE-017/018/019 on 2026-07-30.

## Close-out commits its own work (FEAT-0055)

Git is not the user's job. After the validator is green, **commit**:

```
bash tools/scripts/close-out-commit.sh <paths…> [-m "extra context"]
```

- **Name the paths.** The script refuses with none, because that is `git add -A` wearing a different name. Measured 2026-07-30: `your-trainer` carried 44 uncommitted files and `your-health` 8, none of them the work in hand — automation that stages everything makes somebody else's afternoon part of your commit.
- **Dirty files outside those paths are reported and left alone**, and the commit still happens. They are usually legitimate parallel work, and a close-out that refuses to finish because an unrelated file is dirty is an automation people disable.
- The message is built from the project-os IDs among the staged notes.
- The pre-commit hook is the gate. **Never `--no-verify`.**

**It does not push, and nothing else does either.** A commit is local and reversible; a push is publishing, and once a forge has cached and indexed it, deleting does not unpublish. Pushing is a person clicking the action on the fleet roll-up, which refuses deploy remotes — one fleet repo's only remote is a server path, and pushing it deploys a live website.

## Close-out: file what the validator reports and you cannot fix (FEAT-0051)

LIFECYCLE step 7 and the close-out skill both say to run `bash tools/scripts/validate-docs.sh` and **fix** what it reports. Neither says what to do when you cannot — and "cannot fix" is precisely the case that needs a human, so it is the one that must leave a record.

**At close-out, every validator error is either fixed or filed.**

1. Run the validator. Fix what you can; most of what appears mid-session is your own half-finished work (`METRICS` is corrected automatically by `sync-snapshot.py` at pre-commit).
2. For anything still failing that you cannot or should not fix, **create an `ISS-*`** carrying the error's `[CODE]` and message verbatim, linking the note it names.
3. **Dedup on `(code, subject)`** — where subject is the error's note ID, or its repo-relative path, or the literal `SNAPSHOT.yaml` for snapshot-level errors. If an open issue already has that key, update it and note the recurrence; do not file a second.
4. Closing that issue is what fixing it looks like. There is no separate bookkeeping.

**Why this and not an automatic filer.** Issues appearing without anyone asking is a worse failure than one occasionally missed (Edwin, 2026-07-30), and close-out is where the check already runs. The dependency on the agent performing the step is the same one every other close-out obligation carries, with the same mitigation: the validator gates pre-commit and CI, so an unfixed error is loud whether or not anyone filed it. What filing adds is a place to record **why** it is still there.

This lives here rather than in `tools/instructions/LIFECYCLE.md` because that file is template-owned and a sync would report the edit as divergence. The rule is proposed upstream so every repo can carry it; until then it is this project's.

## Project-specific notes

Stack: Python 3.11+. Dependencies live in `pyproject.toml`. Source under `src/project_os_cockpit/`. Run with `python -m project_os_cockpit <path-to-docs-dir>` or the installed console script `project-os-cockpit <path-to-docs-dir>`. The render server binds to `0.0.0.0` (so a tablet on the same Wi-Fi can read), the optional terminal endpoint binds to `127.0.0.1` only (Mac-local).

Upstream relationship: this repo is downstream of `~/Dev/repos/project-os/` (the canonical project-os template). Run `tools/scripts/sync-project-os.sh ../project-os` to pull template-owned files (`tools/instructions/`, `tools/skills/`, `docs/__templates__/`, `docs/__bases__/`) when the upstream changes.
