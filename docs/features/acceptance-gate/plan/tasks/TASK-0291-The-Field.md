---
type: "[[task]]"
id: TASK-0291
aliases: ["TASK-0291"]
title: "The acceptance field — absent / requested / accepted — in template and taxonomy, divergence recorded"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0064-The-Acceptance-Gate]]"]
parent: "[[FEAT-0064-The-Acceptance-Gate]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# The acceptance field

## Definition of Done

- `acceptance:` documented in the feature template and TAXONOMY; both are template-owned, so the local edit is recorded as deliberate divergence and the upstream proposal (TASK-0293) carries it home.
- Close-out guidance: an opted-in feature gets `requested` stamped at close-out — the agent asks, never answers.

## Done — 2026-08-11

`acceptance:` is in the feature template and documented in `TAXONOMY.md` with its three states and the reasoning:

| value | meaning |
|---|---|
| absent / `""` | **no gate** — the default, and it stays the default |
| `requested` | opted in; a human owes it a run. Stamped at **close-out** |
| `accepted` | written only by a completed run, with `accepted_by` / `accepted_date` |

**The agent asks; it never answers.** An agent may stamp `requested`. Only a completed acceptance run writes `accepted` — enforced in `stamp_acceptance_run`, which is loopback-only and refuses to stamp a feature that never requested it ([[REQ-0028]], [[TASK-0289]]).

Both files are **template-owned**, so this is deliberate local divergence ahead of upstream; [[TASK-0293]] carries the proposal home. Recorded in the TAXONOMY section itself so a `sync-project-os.sh` run reports it as a known edit rather than a surprise.
