---
type: "[[change]]"
id: CHG-20260831-Writing-Rules-Reach-The-Fleet
aliases: ["CHG-20260831-Writing-Rules-Reach-The-Fleet"]
title: "A new instruction file tells agents how to write prose a reader can follow, and it was hand-carried into all twelve project-os repos rather than synced"
status: merged
owner: user:edwin
created: 2026-08-31
updated: 2026-08-31
source: ["Edwin, 2026-08-31: the writing is 'at a very high level of abstraction, which makes it very difficult to understand', reported by more than one reader"]
commit: ""
pr: ""
impacts: ["tools/instructions/WRITING.md (new, all 12 repos)", "AGENTS.md startup step 6 (all 12 repos)", "CLAUDE.md reference list (all 12 repos)", "~/.claude/CLAUDE.md"]
issues: ["[[ISS-0273]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
---

# Writing rules reach the fleet

## Summary

Agents had a rule for how Markdown is **formatted** and none for whether a human could **read** it. This adds `tools/instructions/WRITING.md` — six rules, a before-and-after table, and a self-check — and puts it in every project-os repo.

The rule was authored upstream in `project-os`, because `tools/instructions/` is template-owned and that is where fleet-wide guidance belongs.

## Why it was hand-carried instead of synced

The obvious move was `sync-project-os.sh` in each repo. A dry run showed why that was wrong: `edankert.com` is twenty template files behind and carries four locally diverged files needing hand-merge, including `validate-docs.py`. Running a full sync there would have made a one-file convention change into a large unrelated one with manual conflict resolution attached.

So the rollout copied one new file and inserted one line into two existing files, in each of the twelve repos. `WRITING.md` did not exist anywhere, so the copy could not conflict. `AGENTS.md` was byte-identical across all twelve beforehand and the same line was added to each, so it stays identical and no divergence was introduced. `CLAUDE.md` is project-owned and never synced, so its line is a local edit by design.

The rollout script verified all twelve anchor points before changing anything, and was run once as a dry run first.

## Impact

Applies to chat replies, commit messages, and note prose. Nothing enforces it mechanically — no validator or schema changed — so it is guidance carried by review.

The same six rules were added to `~/.claude/CLAUDE.md`, which is outside every repo and loads in every session. That copy is what changes behaviour immediately; the in-repo copies are what make it durable and visible to anyone else.

## Not done

Cursor gets these instructions through a generated rule file, and `WRITING.md` is not wired into the generator. Filed as [[ISS-0273]].
