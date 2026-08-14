---
type: "[[issue]]"
id: ISS-0166
aliases: ["ISS-0166"]
title: "Every view selection re-parses the 204 KB snapshot up to seven times, and re-walks the docs tree ten times per parse — Intent costs 1.25s where Issues costs 0.03s"
status: "fixed"
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-14
updated: "2026-08-14"
source: ["Edwin 2026-08-14: 'the view selection is very slow now, can you check why this is, seems to have been introduced recently enough'"]
severity: medium
component: render-server
parent: ""
related: ["[[FEAT-0091-The-Standing-Documents]]", "[[TASK-0380]]", "[[ADR-0025]]", "[[FEAT-0094]]", "[[CHG-20260814-Views-Stop-Reparsing-The-Snapshot]]"]
tests: []
---

# Every view selection re-parses the snapshot

## Measured

Building one nav payload for this repo's corpus, warm process, no HTTP:

| mode | time | `SNAPSHOT.yaml` parses |
|---|---|---|
| issues | **0.033s** | 0 |
| library | 0.428s | 2 |
| features | 0.482s | 2 |
| **intent** | **1.245s** | **7** |

`issues` is the control: the only mode that never resolves the standing manifest, and it is **14× to 38× faster** than the others. `SNAPSHOT.yaml` is 204 KB and `yaml.safe_load` costs 0.123s on it, so seven parses of one unchanged file is ~0.9s of Intent's 1.25s.

Every parse arrives by the same path — `standing.resolve()` → `manifest()` → `_extensions_from_snapshot()` — from three callers: `standing.entries`, `standing.check` and `cockpit._standing_rel_paths`.

## Two costs, one function

1. **`manifest()` re-reads and re-parses `SNAPSHOT.yaml` on every call.** It is read for one field, `docs_system.standing`, which holds two entries.
2. **`resolve()` walks the docs tree once per manifest entry** — `docs_root.glob("**/<filename>")` inside the loop, ~10 entries — so a single resolve does ten recursive walks of ~900 notes, and Intent does seven resolves. That is the other ~0.4s.

Neither is cached, and nothing in either depends on the request.

## Why now

Both arrived within the last four days and compound:

- **[[TASK-0380]] (2026-08-10)** made the standing set data and added `_extensions_from_snapshot` — the per-call YAML parse.
- **[[ADR-0025]] / [[FEAT-0094]]** prepend *What needs a person* to every view that does not already gather it, so the standing resolution moved from one surface onto **all of them**. That is the right rule; it just made a per-call cost a per-view cost.
- `SNAPSHOT.yaml` grew 192 KB → 209 KB over the last twenty commits, so the parse gets slower on its own.

Nothing about the 2026-08-14 publication work is implicated: `git_state` does not appear in the nav profile, and the registry's own git read is cached for 10 seconds.

## Expected

A view selection should not re-read an unchanged file seven times, and resolving ten filenames should take one walk rather than ten. Neither fix needs a cache with a staleness question: the manifest is keyed on the snapshot's own bytes, and the walk is one pass.

---

## Fixed — 2026-08-14 ([[CHG-20260814-Views-Stop-Reparsing-The-Snapshot]])

| mode | before | after |
|---|---|---|
| issues | 0.033s | 0.006s |
| features | 0.433s | 0.051s |
| library | 0.443s | 0.030s |
| **intent** | **1.262s** | **0.102s** |
| active | 0.431s | 0.031s |
| recent | 0.429s | 0.032s |

**A third cost turned up in the profile of what was left** and is fixed with the other two: `Index.get()` called `Path.resolve()` on every lookup — ~12 `lstat`s a call, 2816 calls per `features` payload, **33,000 `lstat`s** to answer what the dict already held. The keys are resolved paths and nearly every caller passes one it got from the index, so the dict is tried first and the filesystem only on a miss. That is most of the remaining gap between `features` at 0.28s after the first two fixes and 0.05s now.

**The manifest cache is stamped with a digest, not `(mtime_ns, size)`** — the first version used the stat, which would serve an older parse for two writes inside one filesystem timestamp tick at the same length. Read-and-digest is 0.114 ms against a 117 ms parse. The guard for it writes two same-length snapshots in succession, which is the case the rejected stamp would have missed.

Three guards added, all mutation-tested against the pre-fix module; the parse-count and single-walk assertions both fail on it. Counts, not durations — a timing assertion on a shared machine is a flake, and the parse count is what regressed.
