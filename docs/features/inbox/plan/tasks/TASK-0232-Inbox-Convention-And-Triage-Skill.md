---
type: "[[task]]"
id: TASK-0232
aliases: ["TASK-0232"]
title: "The inbox convention and its triage skill, upstream"
status: done
phase: "[[PHASE-014-Project-Inbox]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0045-Project-Inbox]]"]
parent: "[[FEAT-0045-Project-Inbox]]"
effort: "M"
depends: []
blocks: ["[[TASK-0233-Drop-And-Paste-Into-The-Inbox]]"]
related: []
tests: []
---

# The convention, and the instructions for emptying it

## Definition of Done

- [x] `inbox/` is documented as a project-os concept: what belongs there, what it is not, and that it is gitignored
- [x] A triage skill tells an LLM what to do with an item: **read it, decide, act, remove it** — file into an existing note, split across several, create something new, or discard
- [x] The skill states plainly that **nothing may be left**, and that an item is not a record — a fresh clone has an empty inbox
- [x] The skill covers the case that makes triage hard: an item that is *partly* useful, where filing the useful half and discarding the rest is the correct outcome rather than keeping the whole thing
- [x] `.gitignore` gains `inbox/` without disturbing existing rules
- [x] Owned upstream (`project-os-dev`), released, and synced to the fleet — evidence: `project-os-dev@f6c8407`; released and synced below

## Notes

Its sibling is `ad-hoc-intake`, which triages an unstructured **prompt**. This triages an unstructured **artefact**, and the decision tree is nearly the same — which is an argument for the skills reading alike, not for merging them: the inputs arrive by different routes and one of them has a directory that fills up.
