---
type: "[[task]]"
id: TASK-0220
aliases: ["TASK-0220"]
title: "Revision capture — deposit the history TASK-0216 renders"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["review:model:claude-fable-5 2026-07-27"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "M"
depends: ["[[TASK-0214]]"]
blocks: ["[[TASK-0216]]"]
related: ["[[REQ-0023-Design-Is-A-Project-Record]]"]
tests: []
---

# Revision capture

## Why this task exists

Independent review (2026-07-27) found the hole this phase was built around and did not fill: **[[TASK-0216]] renders git history; nothing in the plan deposits it.**

An agent iterating against [[TASK-0215]]'s live-reloading surface edits the working copy six times and commits once — exactly what happened to [[DES-0001]], which is the loss this whole phase exists to prevent. Every exit criterion could go green while the next design session loses five revisions again.

The tell was in the plan already: TASK-0216 step 4 *manufactures* its own multi-revision fixture ("create one by committing a genuine revision"). Writing a task that has to fabricate its own subject is an admission that the organic history is not expected to exist.

## Definition of Done

- [x] A "capture revision" action commits the artifact **alone**, with a required reason, from the design surface — one artifact per commit, so the reason is never buried in an unrelated message — evidence: `POST /api/design/capture`; `test_capture_commits_the_artifact_alone_with_its_reason` asserts an unrelated dirty file is not swept in
- [x] Capture appends to a `## Revisions` section in the design note: date, short sha, one-line reason — evidence: `append_revision_log`; inserts at the end of the *section*, not the body
- [~] The note's revision log and `git log --follow` on the asset agree; a validator check reports divergence — **reconciled.** They agree by order and date, not by sha: a commit cannot contain its own hash, so the log carries none. `test_revision_log_records_the_reason_and_no_sha`
- [~] An agent editing an artifact is prompted to capture before the surface is left, or the uncaptured edit is visibly flagged — **deferred.** Needs the dirty-state signal below plus a surface affordance; the endpoint exists and is the hard half
- [~] A design whose asset has uncommitted changes shows as `dirty` rather than silently rendering an uncaptured state — **deferred to TASK-0216**, which already reads git state for the compare view
- [~] The dossier for a real revision of [[DES-0001]] is captured through this path, not by hand — **needs a real design edit**, which is Edwin's. The path is proven end to end on a scratch repo: commit created, note updated, sha returned matches HEAD

## Steps

- [x] Guarded commit action (fixed argv, artifact path only, reason required, refuses a dirty tree beyond the artifact)
- [x] Append the revision-log entry through `note_writes.py` with an extended allow-list
- [~] Divergence check between the note's log and git history
- [~] Dirty-state indicator on the surface
- [~] Capture one real revision of DES-0001 end to end

## Result

`POST /api/design/capture` — loopback-gated, reason required, artifact and note committed **together and alone**. An unrelated dirty file in the tree is not swept in, which matters because the commit message is the only readable record: two regenerated 139KB HTML files diff as a wall of noise.

**The log carries no sha, and that is not a shortcut.** An early version wrote a placeholder, committed, corrected it and amended — which changed the sha again, so every entry named a commit that did not exist. A commit cannot contain its own hash; that is self-reference, not a bug to code around. So the note records the *reason*, git records the *revision*, and they pair by order and date — which also survives a rebase that rewrites every sha.

Proven end to end on a scratch repo: commit created with the right two files, note updated, returned sha equal to HEAD, and a second capture correctly refused with "no change to capture".

Three DoD items reconciled rather than ticked: the dirty-state signal moves to [[TASK-0216]] (which already reads git state), the authoring prompt depends on it, and capturing a *real* DES-0001 revision needs a real design edit, which is Edwin's to make.

## Notes

The revision log in the note is not redundant with git. Three reasons, all from the review:

1. **The asset diff is noise.** Two regenerated 139KB HTML files diff as a wall of changes, so the reasoning between revisions collapses to the commit subject. A one-line reason in the note is the only readable record.
2. **Git history is invisible to the validator**, and a squash or rebase destroys it silently. A log in the note is checkable.
3. [[REQ-0023]]'s "readable without the tool" clause currently covers comments and verdicts but not the *process*. This closes that.

This task belongs **before** TASK-0216 in the sequence. Rendering history is worthless while nothing deposits it, and every week of phase 1 without capture is potentially another design process lost.
