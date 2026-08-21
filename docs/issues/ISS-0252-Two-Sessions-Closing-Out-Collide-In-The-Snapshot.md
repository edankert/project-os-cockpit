---
type: "[[issue]]"
id: ISS-0252
review_verdict: approved
review_date: 2026-08-21
reviewed_by: model:claude-opus-5
aliases: ["ISS-0252"]
title: "Close-out requires naming `SNAPSHOT.yaml` and the snapshot is one hand-curated shared file, so two agent sessions closing out at once interleave in it — three collisions in one afternoon, two of which turned `--as-committed` red"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-21"
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

- [x] **Built 2026-08-21: `close-out-commit.sh` names what it changes in `SNAPSHOT.yaml`'s `items:` membership** — added, removed, and separately the **dangling** case, in stderr and in the commit message. *"Collision 2 was visible in `git diff` and nobody looked."*
- [x] **The collision was constructed and the report watched firing.** `tests/test_close_out_snapshot_report.py`: a real git repo, an entry registered against a note that is in no commit, the report naming it `DANGLING`.
- [~] **A lock does not close collision 1, and that is a measurement rather than a decision.** See below. Whether concurrent sessions are a supported mode remains Edwin's call, and the answer changes nothing about what was built.
- [~] **Whether a note with no snapshot entry should stay a warning** stays a question. Widening it is `tools/instructions/SNAPSHOT.md`'s retention rule and it would fire on every pruned terminal item — that is a template-owned change with a fleet-wide blast radius and it is not this issue's to make.


## Fixed 2026-08-21 — the reporting half, and why the lock is not the other half

### What the script now prints

When `SNAPSHOT.yaml` is among the staged paths, it diffs `items:` membership between `HEAD` and the **index** — what this commit will actually contain — and prints:

```
close-out-commit: SNAPSHOT.yaml items: membership changed (ISS-0252):
  added:   PHASE-0040
  DANGLING (the note is in no commit; --as-committed will fail ITEM-FILE and it does not self-heal):
    PHASE-0040 -> docs/phases/PHASE-0040-P.md
```

…and puts the same text in the commit message, so `git log` carries it.

**The dangling case is named separately because it is the one that does not self-heal.** Collision 1 was a metrics mismatch that cleared itself when the other session committed. Collision 2 left a reference that stays dangling until somebody notices, and **the local validator cannot see it**: it reads the working tree, where the note exists. Only the committed state is missing it.

**It reports and never refuses.** A close-out that stops because a shared file moved under it is automation people disable — the same reason dirty files outside the scope are reported and left alone rather than treated as an error. `test_it_reports_and_never_refuses` pins that.

### The lock would not have prevented collision 1, and this is measured rather than argued

Next Action 1 offered a lock as the cheap fix *"if concurrent sessions are not a supported mode"*. Working through it:

**A lock serialises COMMITS. The collision is in the WORKING TREE.** `sync-snapshot.py` computes `metrics.counts` from the files on disk at pre-commit, and the other session's uncommitted edits are on that disk whether or not anybody holds a lock. Collision 1 — `issues_open` computed over another session's unsaved status change — reproduces exactly the same way with a lock in place.

So a lock buys serialised commits and nothing else, and the failure it is offered against is not a commit-ordering failure. **That does not make concurrent sessions a decided question** — it makes the lock the wrong answer to it. If they are unsupported the fix is procedural, not a mutex; if they are supported the snapshot has to stop being one hand-curated file, which is [[project-os-dev#ADR-0009]]'s territory and a much larger change.

Recorded here rather than acted on: an ADR-shaped decision is Edwin's, and this issue closes on the half that is mechanical and unambiguous.

### Collision 3 is still the one to learn from

The repair for a stale diagnosis deleted a **valid** registration, and the local check was silent — a snapshot entry with no note is an error, a note with no entry is only a warning, so the asymmetry that caught the first mistake said nothing about the over-correction. `test_a_removed_entry_is_named_too` makes a removal visible for that reason; the asymmetry itself is the open question above.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: approved.**

- **The dangling case is genuinely guarded.** I replaced `if hit.returncode != 0:` with `if False:` in `tools/scripts/close-out-commit.sh`; `test_an_entry_whose_note_is_in_no_commit_is_named_as_dangling` failed with the DANGLING line absent. The membership report itself still printed, which is the right split — the two are reported independently.
- **`git ls-files` resolves correctly.** The script does `cd "$ROOT"` at line 23 before the Python block runs, so the relative `file:` paths are interpreted against the repo root rather than the caller's cwd.
- **Reports, never refuses** — `test_it_reports_and_never_refuses` pins it, and that is consistent with the existing treatment of dirty files outside scope. A close-out that aborts because a shared file moved is automation people disable.
- The line-oriented YAML reader is the right call inside a commit-hook path (no PyYAML dependency, degrades to silence on a parse failure).

Correctly left open as an ADR-shaped question: whether concurrent close-out sessions are supported at all. Reporting the collision is not the same as preventing it, and this note says so.

No changes requested.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**Approved, confirming the first-pass verdict.** No first-pass finding attached to this note; this commit added a review section only, and `close-out-commit.sh` is unchanged in `07602db..b635c39`. Not re-litigated in this pass.
