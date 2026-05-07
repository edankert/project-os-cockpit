---
type: "[[risk]]"
id: RISK-0002
aliases: ["RISK-0002"]
title: "Project-os ID/schema drift outpaces the resolver"
status: open
severity: medium
likelihood: medium
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
related: ["[[FEAT-0001]]", "[[FEAT-0004]]", "[[REQ-0002]]"]
mitigations: []
---

# RISK-0002 — Schema drift

## Hazard
Project-os evolves upstream. New note types (e.g. a future `NOTE-*` type proposed in the `your-applications.com` marketing README), new frontmatter conventions, or changes to the ID prefixes can outpace the resolver's hardcoded list. Result: links go dark, indexes miss whole categories, the renderer silently shows fewer notes than exist.

## Likelihood
Medium — the upstream `project-os` template is itself a living thing.

## Severity
Medium — silent under-coverage is worse than a visible error because the user doesn't know what they're missing.

## Mitigations
- ID-prefix list lives in one configurable location, not spread across files.
- Resolver logs a warning at startup when it encounters a frontmatter `type:` it doesn't recognise, suggesting an update to the prefix list.
- Sync mechanism: `tools/scripts/sync-project-os.sh` keeps the upstream-owned files current; the resolver should track the upstream's TAXONOMY.md when adding new types.
- Tests: add a unit test that walks a known fixture tree and asserts every note is reachable / categorised.

## Residual risk
The upstream may add types we don't immediately learn about. The startup warning + the sync script reduce the window; new types still require a code change here, but the change is a one-liner.
