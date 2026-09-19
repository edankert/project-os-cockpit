---
type: "[[issue]]"
id: ISS-0273
aliases: ["ISS-0273"]
title: "Cursor sessions are not given the writing rules, because the adapter generator has no entry for WRITING.md"
status: fixed
owner: user:edwin
reported_by: agent
created: 2026-08-31
updated: "2026-09-19"
severity: low
component: docs
phase:
source: ["Deferred deliberately during CHG-20260831-Writing-Rules-Reach-The-Fleet, 2026-08-31, with Edwin's agreement"]
related: ["[[CHG-20260831-Writing-Rules-Reach-The-Fleet]]"]
tests: []
---

# Cursor sessions are not given the writing rules

A Cursor session in any fleet repo gets no `writing.mdc` rule, so it never sees tools/instructions/WRITING.md.

## What is missing

`tools/scripts/generate-adapters.py` holds a table mapping instruction files to Cursor rule files:

```python
# instruction file -> (rule name, globs, always-apply)
    ("MARKDOWN.md", "markdown", ["**/*.md"]),
```

`WRITING.md` has no entry, so `.cursor/rules/` never gains a `writing.mdc`. A Cursor session in any of the twelve repos reads the formatting rule and not the clarity rule.

Claude Code and anything else that reads `CLAUDE.md` or `AGENTS.md` is unaffected — both were updated in all twelve repos.

## Why it was left

Adding the entry is one line. Shipping it is not. `generate-adapters.py` is template-owned, `.cursor/rules/` is generated, and CI runs `generate-adapters --check` — so the entry only works once every repo has both the new generator and freshly regenerated output. Several repos are behind on that generator: a dry-run sync of `edankert.com` showed it twenty files behind with four diverged files awaiting hand-merge.

Doing it during a one-file convention change would have dragged unrelated generator changes into those repos, and a `--check` failure in CI is a hard stop rather than a warning.

## What fixing it looks like

1. Add `("WRITING.md", "writing", ["**/*.md"])` to `CURSOR_RULES` upstream in `project-os`.
2. Do it as part of the next full template sync, per repo, so the generator and its output move together.
3. Confirm `generate-adapters --check` passes in each repo before pushing, since it gates CI.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** Someone using Cursor in a fleet repo gets agent output that ignores the plain-writing rules Claude Code sessions follow.

Evidence: `grep -n WRITING ~/Dev/repos/project-os/tools/scripts/generate-adapters.py` finds nothing; the rule table still ends at line 39 with `("MARKDOWN.md", "markdown", ["**/*.md"])`. `.cursor/rules/` in project-os and project-os-cockpit holds eight `.mdc` files and no `writing.mdc`.

**Belongs to:** no feature; the fix is upstream in project-os (template-owned generator). **Next:** Small fix: add the WRITING.md entry to `CURSOR_RULES` in project-os, regenerate, and let the next template sync carry the generator and its output together.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).

## Fixed in the template, 2026-09-19

`generate-adapters.py` now writes `.cursor/rules/writing.mdc` from `WRITING.md` (project-os `01031af`). Synced here as `36c9bf9`, and every fleet repo carries the rule. Recorded upstream as project-os-dev TASK-0143.
