---
type: "[[feature]]"
id: FEAT-0045
aliases: ["FEAT-0045"]
title: "A project inbox: drop anything in, an LLM files it, nothing stays"
status: done
phase: "[[PHASE-014-Project-Inbox]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user request 2026-07-28"]
goal: "Make it trivial to get external information — a screenshot, a file, a pasted image — into the active project, so an LLM can read it, file it into the right notes, split it, or discard it. The inbox is staging, not storage: the measure of success is that it empties."
requirements: []
tasks:
  - "[[TASK-0232-Inbox-Convention-And-Triage-Skill]]"
  - "[[TASK-0233-Drop-And-Paste-Into-The-Inbox]]"
release: ""
design: []
related: ["[[FEAT-0041-Review-Desk]]"]
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "changes-requested"
---

# The project inbox

## What it is, in Edwin's words

> The project-os inbox concept stores external information and allows LLMs to review and take that information and store it with the correct documents / in the correct structure, or splits this up into multiple structures, or decides to throw the data away. The goal is to triage this inbox and not leave anything there.

So it is **pre-documentation**: a staging area whose success condition is being empty. That single property decides most of the design.

## Decisions taken, with the reasoning

**`inbox/` at the repo root, not `docs/inbox/`.** `docs/` is the curated, committed record — the validator walks it, the index walks it, and everything in it is expected to be a note or an asset a note references. A pile of untriaged screenshots inside `docs/` would make `docs/` mean two things at once, and would put untriaged material into the corpus an agent reads as *the record*. The inbox is what exists *before* that decision has been made, and root-level says so.

**Gitignored** (Edwin). It follows from being staging: an inbox item is either filed — at which point the filed artefact is what gets committed — or discarded. Committing the staging area would preserve exactly the thing the triage exists to resolve.

The consequence, stated because it is a real limit: **an agent in a fresh clone sees an empty inbox.** That is correct for staging and wrong if anyone ever treats the inbox as a record. The skill says so.

**Emptiness is the goal, so the cockpit must show what is waiting.** An inbox nothing displays is a pile that grows — and on this surface specifically, four separate defects this month were "a thing that existed and nothing pointed at it". A count is not decoration here; it is the whole mechanism by which triage happens at all.

## Acceptance

- Dropping or pasting a file or image anywhere on the cockpit stores it in the active project's inbox, without a dialog
- The cockpit shows what is waiting, and shows an empty inbox as a resolved state rather than a blank
- The inbox is gitignored, and adding it does not disturb any existing ignore rules
- Filing or discarding an item removes it — the surface makes emptying easy, not just filling
- An LLM has written instructions for triage: read, decide, act, remove; and never treat an item as a record
- Nothing can be written outside the inbox directory, and the write path is loopback-only like every other mutation

## Out of scope

- **Automatic triage.** The LLM decides; the cockpit stores and surfaces. An inbox that files things by itself is a filing system with opinions, and wrong guesses land in the durable record.
- **Syncing inboxes between machines.** It is gitignored local staging.

## Close-out — 2026-07-30

All three tasks were `done` while the feature sat at `doing`; this records the check rather than assuming it.

Verified against the running sidecar and the built renderer:

- `GET /api/inbox` returns `200` with `{"schema_version": 4, "items": []}` — the surface works and reports the **empty state, which is this feature's success condition**. `POST /api/inbox/store` and `/api/inbox/discard` are registered (`server.py`).
- The renderer carries the tray and the per-item view — 15 references to `renderInboxPanel` / `~inbox` — after [[TASK-0234]] moved it out of the top-level nav into a left-pane tray.
- `inbox/` is gitignored and the directory is empty, so a fresh clone sees no inbox and nothing here is a record.
- Triage instructions exist for an LLM: `tools/skills/inbox-triage/SKILL.md`, plus the LIFECYCLE section stating that a non-empty inbox is itself the trigger and that an item is not a record.

**`tests: []` — no test note, and that is a real gap rather than an oversight to paper over.** The drop/paste path is renderer-and-Electron behaviour (drag events, clipboard, an Electron 32 API change that [[ISS-0060]] was filed for), which the automated suite has no surface for; `tests/test_inbox.py` covers the sidecar half. Closed on the sidecar tests plus this manual check rather than under a `verification_waiver`, because the validator does not require one here and inventing a waiver to look rigorous would be worse than saying plainly what was and was not exercised.

What was **not** re-verified today: dropping an actual file onto the running app, and pasting an image. Both were verified when [[TASK-0233]] and [[ISS-0060]] landed. If either regresses, the API being healthy will not catch it.

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — changes-requested

**This note is not in the repository, and neither is this verdict.** `.gitignore:45` carries an unanchored `inbox/`, which matches any directory of that name at any depth — so `docs/features/inbox/` in its entirety (this note, `plan/PLAN.md`, `TASK-0232`, `TASK-0233`, `TASK-0234`) is untracked. `git log -- docs/features/inbox/` returns nothing; `git check-ignore -v` names the rule. `git status` reports clean because these files are ignored, not because they are committed.

Consequences:

- A fresh clone of `main` **fails `validate-docs.py` with 4 errors** — `features_done` 45 vs 44, `features_total` 50 vs 49, `tasks_done` 240 vs 237, `tasks_total` 247 vs 244 — because `SNAPSHOT.yaml`'s metrics count this feature and its three tasks. Locally the validator is green because the files are on disk. LIFECYCLE step 7 says the same validator runs in CI.
- The regression arrived with `afc4fa7` and a clone at `74a2187` already failed with 3 errors, so this predates the close-out. But [[CHG-20260730-Two-Features-Closed]] closes this feature under the heading "checked rather than assumed", and its check included "`inbox/` is gitignored and empty" without noticing that the same pattern hides this feature's own record.
- The `tests: []` closure cannot be judged independently at all, because the reviewer's inputs — this note and its three tasks — are not in the handoff surface. That is a stronger objection than the one the change note anticipated: the question is not whether `tests: []` was honest, it is that nothing about this feature can be reviewed from the repository.

**Asked for:** anchor the ignore rule (`/inbox/`) or rename this directory, get these five notes into git, confirm a fresh clone validates clean, and then re-close. On the merits of the `tests: []` decision I have no objection — declining to invent a `verification_waiver` the validator does not require is the right call, and the manual checks named are the right ones. It is the evidence being outside the repository that blocks the close-out, not the standard applied inside it.
