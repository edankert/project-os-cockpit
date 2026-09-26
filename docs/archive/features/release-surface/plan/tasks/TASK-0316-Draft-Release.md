---
type: "[[task]]"
id: TASK-0316
aliases: ["TASK-0316"]
title: "Drafting a release becomes an action"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0072-The-Release-Surface]]"]
parent: "[[FEAT-0072-The-Release-Surface]]"
effort: M
depends: ["[[TASK-0315]]"]
blocks: []
related: []
tests: []
---

# Drafting a release becomes an action

## Definition of Done

- `Draft release note` scaffolds the REL from its template with the unreleased list, `status: draft`, for the actuator row to advance; nothing is published by drafting.

## Done — 2026-08-11

`Draft release note` on the Unreleased card. It prompts for a title, POSTs `{type: "release"}` to `/api/notes/create`, and navigates to what it wrote.

**It publishes nothing, and that is the whole risk surface.** It allocates an id and writes one file with `status: draft` and an **empty `date:`** — the date records when a release *shipped*, and a drafted note has not. No tag, no push, no deploy. FEAT-0055's line already says a commit is local while publishing is a person's deliberate act; REL-0001 adds that pushing one fleet repo deploys a live website. A `test_drafting_writes_one_file_and_ships_nothing` reads every `.md` in the corpus before and after and asserts nothing else moved.

**The allow-list widened, deliberately and visibly.** `CREATABLE_TYPES` was `{"issue"}` with a recorded rule that *"each further type earns its own review of what 'next id' and 'which template' mean"*. That review is written into the constant: `next_release_id` off the index (same reasoning as `next_issue_id` — the counter is confirmation, not source), the release template's fields, always `draft`, always dateless. A test asserts the set is exactly `{"issue", "release"}`, so the next widening is a visible decision rather than a diff nobody reads.

**The feature list is computed once.** The route calls the same `unreleased_payload` the card reads and hands the ids to `create_release`, so the note carries the number the human saw. Deriving it a second time inside the writer is how the card and the record would come to disagree.

Exercised over HTTP against a throwaway copy of the corpus rather than the live record: `POST /api/notes/create {"type":"release","title":"Smoke test release"}` returned `REL-0002`, `status: draft`, 70 features, and the file carried `date: ""`. The scratch sidecar and its docs copy were removed afterwards; `docs/releases/` still holds only REL-0001.

The write path is the guarded one — `_serve_note_create` calls `_require_loopback()` before reading the body, and the desktop sidecar binds `127.0.0.1` only, so it is not LAN-reachable at all.
