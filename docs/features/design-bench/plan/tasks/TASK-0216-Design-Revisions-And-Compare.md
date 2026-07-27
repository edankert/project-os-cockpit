---
type: "[[task]]"
id: TASK-0216
aliases: ["TASK-0216"]
title: "Revisions from git, side by side, with the reason for each"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[DES-0001-Overview-Redesign]]"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "M"
depends: ["[[TASK-0214]]"]
blocks: []
related: ["[[REQ-0023-Design-Is-A-Project-Record]]"]
tests: []
---

# Revisions and compare

## Definition of Done

- [x] The surface lists an artifact's revisions from git history, newest first, each with date, commit and subject — evidence: `design_revisions_payload` via `git log --follow`; DES-0001 shows 3 real revisions
- [x] Any two revisions render **side by side** at the same viewport — evidence: `is-compare` renders working copy against the chosen revision at one viewport; `test_compare_renders_both_sides_at_the_same_viewport`
- [x] The reason for a revision is visible next to it — sourced from the commit subject/body, so the record exists whether or not the cockpit is running — evidence: extracted from the commit subject, so the record exists whether or not the cockpit runs; `test_the_reason_is_extracted_from_the_commit_subject`
- [x] Selecting a revision renders that revision, not the working copy — evidence: `/design-asset-at/<id>/<sha>` via `git show`
- [x] An artifact with a single revision shows the list without offering a meaningless comparison — evidence: the rail always lists Working copy; compare only engages on selection
- [x] Reading a historical revision never mutates the working tree — evidence: `test_historical_asset_reads_without_touching_the_tree` leaves an uncommitted edit in place and asserts it survives

## Steps

- [x] Add a revisions endpoint (`git log --follow` over the asset path, argv-fixed, clamped)
- [x] Serve an artifact at a given commit (`git show <sha>:<path>`) without checking anything out
- [x] Build the side-by-side view reusing the viewport switcher from [[TASK-0215]]
- [ ] Verify against a real multi-revision artifact — create one by committing a genuine revision of REF-0001's dossier

## Result

`--follow` is the load-bearing flag. DES-0001's asset moved from `references/design/` to `designs/` when the design type landed; without it the history would truncate at the rename and a design with real history would look new.

**Dirty state is reported.** An uncaptured edit is a revision the compare view cannot see and the note does not record, so the rail says so rather than showing "3 revisions" and quietly meaning "3 plus whatever you have not committed". This is the dirty signal [[TASK-0220]] deferred here.

`git show <sha>:<path>`, never a checkout — tested by leaving an uncommitted edit in place and asserting it survives a historical read. A compare view that stashed the user's work to render a diff would be data loss wearing a feature's clothes.

Compare renders both sides **at the same viewport**: two renders at different sizes would show the layout changing rather than the design.

The original step 4 planned to *manufacture* a multi-revision fixture — which Fable read, correctly, as an admission that organic history was not expected to exist. It was not needed: capture landed first, and DES-0001 already had three real revisions.

## Notes

This is the task that addresses the actual loss. The overview dossier went through six revisions in one session; the sixth is committed and the reasoning for the other five is in a transcript. Going forward the commit *is* the record, which is why the reason comes from the commit message rather than a field the cockpit owns — it survives the tool.

`git show <sha>:<path>` rather than a checkout is deliberate: reading history must never touch the working tree. The commits endpoint added in [[TASK-0199]] is the model for the subprocess handling (fixed argv, timeout, clamped limit).
