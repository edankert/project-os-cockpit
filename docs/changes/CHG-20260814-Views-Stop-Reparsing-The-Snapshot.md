---
type: "[[change]]"
id: CHG-20260814-Views-Stop-Reparsing-The-Snapshot
title: "View selection stops re-reading an unchanged snapshot seven times — Intent 1.26s → 0.10s"
status: merged
owner: user:edwin
created: 2026-08-14
updated: 2026-08-14
source: ["Edwin 2026-08-14: 'the view selection is very slow now, can you check why this is, seems to have been introduced recently enough'"]
commit: ""
pr: ""
impacts: ["nav payloads are 4×–12× faster", "the standing manifest is memoised per project, keyed on the snapshot's content digest", "standing.clear_manifest_cache() exists for tests and moved workspaces", "Index.get() no longer calls Path.resolve() on a hit"]
issues: ["[[ISS-0166-Every-View-Selection-Reparses-The-Snapshot]]"]
features: ["[[FEAT-0091-The-Standing-Documents]]"]
related: ["[[ADR-0025]]", "[[FEAT-0094]]", "[[TASK-0380]]", "[[CHG-20260814-One-Walk-For-Publication]]"]
---

# Views stop re-parsing the snapshot

## Measured, warm, three-run average, this repo's corpus

| mode | before | after |
|---|---|---|
| issues | 0.033s | 0.006s |
| features | 0.433s | 0.051s |
| library | 0.443s | 0.030s |
| **intent** | **1.262s** | **0.102s** |
| active | 0.431s | 0.031s |
| recent | 0.429s | 0.032s |

`issues` was the control that found this: the only mode that never resolves the standing manifest, and the only fast one.

## Three costs, none of them doing any work

1. **`standing.manifest()` parsed `SNAPSHOT.yaml` on every call** — 204 KB, 117 ms, for one field holding two entries. Intent called it **seven times per view selection**.
2. **`standing.resolve()` walked the docs tree once per manifest entry** — `glob("**/<file>")` inside the loop, ten entries, ~900 notes, seven times over.
3. **`Index.get()` called `Path.resolve()` on every lookup** — a realpath syscall chain at ~12 `lstat`s a call, 2816 calls per `features` payload: **33,000 `lstat`s** to answer questions the dict already held. The keys *are* resolved paths and nearly every caller passes one it got from the index, so the dict is tried first and the filesystem only on a miss.

## Why it appeared now

Two changes four days apart compounded. [[TASK-0380]] (2026-08-10) made the standing set data and added the per-call snapshot parse; [[ADR-0025]] / [[FEAT-0094]] then put *What needs a person* in front of **every** view, which is the right rule and turned a per-call cost into a per-view one. `SNAPSHOT.yaml` also grew 192 KB → 209 KB over twenty commits, so the parse was getting slower on its own.

**Not the publication work of the same day**: `git_state` does not appear in the nav profile at all, and the registry's own git read is cached for 10 seconds.

## The cache, and the question it does not have

`manifest()` is memoised per project root and stamped with a **sha1 of the snapshot's bytes**, so there is no staleness question to answer — the file changing is exactly and only what invalidates it.

The first version stamped `(mtime_ns, size)`. That is wrong in a way worth recording: two writes inside one filesystem timestamp tick, to the same length, would serve the older parse — rare, silent, and unreasonable-about from the wrong answer alone. Read-and-digest costs **0.114 ms against a 117 ms parse**, a tenth of a percent of what caching saves, so the exact answer was affordable and taken.

## Guards

`tests/test_standing_documents.py` gains three, all mutation-tested against the pre-fix module (the first and third fail on it):

- one Intent payload parses `SNAPSHOT.yaml` **zero** times after warm-up;
- an edited snapshot **is** re-read — written as two same-length bodies, which is the case the rejected `(mtime_ns, size)` stamp would have missed;
- one `resolve()` performs at most one recursive walk, and still reports a rival copy as `ambiguous`.

Counts rather than durations: a timing assertion on a shared machine is a flake, and the number of parses is what actually regressed.
