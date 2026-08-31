---
type: "[[issue]]"
id: ISS-0273
aliases: ["ISS-0273"]
title: "Cursor sessions do not receive tools/instructions/WRITING.md, because the adapter generator's rule table was not extended and regenerating it everywhere would pull unrelated generator changes into repos that are behind"
status: triage
owner: user:edwin
created: 2026-08-31
updated: "2026-08-31"
severity: low
component: docs
phase:
source: ["Deferred deliberately during CHG-20260831-Writing-Rules-Reach-The-Fleet, 2026-08-31, with Edwin's agreement"]
related: ["[[CHG-20260831-Writing-Rules-Reach-The-Fleet]]"]
tests: []
---

# Cursor does not receive the writing rules

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
