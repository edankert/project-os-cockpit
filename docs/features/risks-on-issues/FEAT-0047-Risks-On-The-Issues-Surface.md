---
type: "[[feature]]"
id: FEAT-0047
aliases: ["FEAT-0047"]
title: "Risks join the Issues surface — what's wrong and what could go wrong, read together"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
goal: "Risks get the only navigable home they have ever had. They group by severity in the Issues mode — the same vocabulary issues already use — and the dead Risks stat tile finally has somewhere to go."
requirements: []
tasks: ["[[TASK-0237-Risks-Group-In-Issues-Mode]]", "[[TASK-0238-Risks-Tile-Destination]]"]
release: ""
related: ["[[PHASE-010-Surface-Ownership]]", "[[ISS-0063-Dead-Stat-Tiles]]", "[[FEAT-0050-Library-Reduction]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
---

# FEAT-0047 — Risks on the Issues surface

## Goal

Library's Risks group is the only place risks appear in the whole cockpit. Nothing else lists them; the overview counts them in a tile that navigates nowhere ([[ISS-0063]]).

"What is wrong" and "what could go wrong" are the same question in different tenses, read at the same moment, and both types already carry `severity:` in the same vocabulary — `_issues_groups` buckets by exactly that field.

## Scope

- A Risks group in the `issues` nav mode, grouped by severity alongside the issue buckets.
- Risks visually distinguishable from issues in the pane — same surface, not the same thing.
- The overview's Risks stat tile navigates to the Issues mode.

## Out of Scope

- **A risks nav mode.** Four notes here, and the fleet's largest count is also four. A top-level surface for that is the mistake this phase is undoing, not repeating.
- Renaming the mode to "Issues & risks". The mode strip is tight and the group heading says it; revisit if risks ever outnumber issues.
- Mitigation tracking or `mitigation_tasks:` rendering. Out of scope — this is a reachability change.

## Acceptance

- Every `[[risk]]` note in the corpus appears in the Issues mode, grouped by its severity.
- A risk row is distinguishable from an issue row without opening it.
- The Risks tile navigates; the Reqs tile deliberately still does not (see [[PHASE-010]] Out of Scope).
- Issues-only behaviour is unchanged when a corpus has no risks.

## Links

- Issue: [[ISS-0063-Dead-Stat-Tiles]]
- Tasks: [[TASK-0237-Risks-Group-In-Issues-Mode]], [[TASK-0238-Risks-Tile-Destination]]
## Independent review — 2026-07-30, approved

Fresh session, `model:claude-opus-5`, from the notes and the diff for `bed48ea`; no access to the authoring session's reasoning.

Mutation-tested rather than re-read. Removing `'issues'` from the `buildStatTile('Risks', …)` call fails `test_the_dead_stat_tiles_gained_a_destination[Risks-issues]`; pointing the tile at `'features'` instead also fails, so the assertion pins the destination and not merely the presence of one. `test_risks_get_their_own_groups_not_the_issue_buckets` genuinely separates the populations (no group mixes types; every risk group key is prefixed `risk:`), and `test_a_corpus_with_no_risks_is_unchanged` holds. Measured live: `mode=issues` yields `critical/high/medium/low` plus `risk:high`, `risk:medium`, `risk:low`.

One limit, disclosed in [[TST-0022]] and not a defect here: the tile assertions read the call site, so a `buildStatTile` that stopped honouring `navMode` altogether would pass. The manual step covers the behaviour. No findings.
