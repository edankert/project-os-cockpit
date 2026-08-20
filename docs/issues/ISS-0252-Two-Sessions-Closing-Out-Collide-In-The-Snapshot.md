---
type: "[[issue]]"
id: ISS-0252
aliases: ["ISS-0252"]
title: "Close-out requires naming `SNAPSHOT.yaml` and the snapshot is one hand-curated shared file, so two agent sessions closing out at once interleave in it — three collisions in one afternoon, two of which turned `--as-committed` red"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["hit three times while closing out PHASE-037 alongside a second session, 2026-08-20"]
severity: medium
component: tooling
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0251-A-Test-Backdates-A-Shared-Source-File]]", "[[FEAT-0055-Git-Assist]]"]
tests: []
---

# One file, two sessions, and the close-out rule points both at it

## Problem

`close-out-commit.sh` refuses to run with no paths — deliberately, because staging everything is *"`git add -A` wearing a different name"* ([[FEAT-0055-Git-Assist]]). But **`SNAPSHOT.yaml` is a path every close-out must name**: `sync-snapshot.py` writes counters and metrics into it at pre-commit, and the validator errors if they are stale.

So every session commits the same file, and two properties make that unsafe:

1. **`sync-snapshot.py` computes derived fields from the WORKING TREE**, which contains the other session's uncommitted edits.
2. **Membership — which items the snapshot carries — is hand curation the script deliberately leaves alone** (`CLAUDE.md`). So an item another session registers by hand sits in the shared file until *somebody* commits it, and that somebody may not be the session holding its note.

## Actual — three collisions, 2026-08-20

| # | what happened | effect |
|---|---|---|
| 1 | Pre-commit `sync-snapshot` computed `metrics.counts.issues_open` from the other session's uncommitted `ISS-0248` status change | `--as-committed` **red** (`METRICS`); self-healed when they committed |
| 2 | `3f62631` swept in their hand-written `PHASE-040:` entry while the note was still untracked | `--as-committed` **red** (`ITEM-FILE`); does **not** self-heal — a dangling reference stays dangling |
| 3 | The fix for 2 removed the entry — but between diagnosis and fix they had committed the note, so the removal deleted a **valid** registration | `--as-committed` **green**, and wrong |

**Collision 3 is the one to learn from.** The repair for a stale diagnosis was applied against a `git log` sixty seconds old, in a repo where a second session was committing. And the local check could not catch it: a snapshot entry with no note is an **error**, a note with no entry is a **warning**, so the asymmetry that caught the first mistake was silent on its over-correction.

## Expected

Two sessions closing out concurrently either both succeed, or the second is told to rebase — not silently commit half of the other's state.

## Evidence

- `3f62631`, `b1ec653`, `9d66d89` and the commit restoring the entry, in that order.
- `close-out-commit.sh` refuses with no paths; `sync-snapshot.py` reads the working tree; `CLAUDE.md`: *"which items the snapshot carries … are curation the script deliberately leaves alone."*
- [[ISS-0251]] is the same class in the test suite — a shared mutable file, two processes, a false red.

## Next Actions

- [ ] Decide whether concurrent sessions are a supported mode at all. If they are not, the cheapest fix is a **lock**: `close-out-commit.sh` takes one, and the second session waits or is told why. If they are, the snapshot needs to stop being a single hand-edited file, which is a much larger change and is [[ADR-0009]]'s territory.
- [ ] Cheap and independent of that: **`close-out-commit.sh` should report what it is about to stage in `SNAPSHOT.yaml` that the session did not write** — a diff of `items:` membership against `HEAD`, named in the output. Collision 2 was visible in `git diff` and nobody looked.
- [ ] Consider whether a note with no snapshot entry should stay a warning. It is what made collision 3 invisible — though widening it is `tools/instructions/SNAPSHOT.md`'s retention rule and would fire on every pruned terminal item, so this is a question rather than a proposal.
- [ ] Whatever is built, **construct the collision and watch the check fire**: two close-outs interleaved, not one.
