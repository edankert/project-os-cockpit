---
type: "[[issue]]"
id: ISS-0072
aliases: ["ISS-0072"]
title: "The validator never re-runs on a SNAPSHOT.yaml edit — its dedicated project-root observer does not fire, so METRICS drift never clears live"
status: fixed
severity: medium
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["found during TASK-0250's live pass, 2026-07-30"]
component: sidecar
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[TASK-0111-Validation-Runner]]", "[[FEAT-0028-Fleet-Health-Surface]]", "[[CHG-20260730-Two-Features-Closed]]"]
fixed_by: ["[[TASK-0248-Live-Workspace-Validation-Aggregate]]"]
tests: []
---

# SNAPSHOT.yaml edits do not re-trigger validation

## What

`ValidationRunner` owns two input paths. One works; one does not.

| edit | re-runs? |
|---|---|
| a real `.md` under `docs/` | **yes** — new report, fresh `checked_at` |
| `SNAPSHOT.yaml` | **no** — cached report, `checked_at` unchanged |

Measured on a live sidecar (`http://127.0.0.1:8765`, this repo, 2026-07-30) while verifying [[TASK-0250]]:

```
induced a METRICS error in SNAPSHOT.yaml  -> failing 1  checked_at 13:58:37
touch SNAPSHOT.yaml            (+4s)      -> failing 1  checked_at 13:58:37   (unchanged)
append a newline to SNAPSHOT.yaml (+4s)   -> failing 1  checked_at 13:58:37   (unchanged)
restore SNAPSHOT.yaml          (+26s)     -> failing 1  checked_at 13:58:37   (unchanged)
write docs/zz-probe.md          (+5s)     -> ok      0  checked_at 14:00:44   (re-ran)
delete docs/zz-probe.md         (+5s)     -> ok      0  checked_at 14:00:49   (re-ran)
```

Three separate SNAPSHOT edits, no re-run. One docs-tree write, immediate re-run.

## Why it matters more than it looks

**`METRICS` is the most common validator error, and it lives in `SNAPSHOT.yaml`.** So the single most likely way to go red is also the one way the surface will not notice you going green again. The badge stays red until something unrelated touches `docs/`, or until the sidecar restarts.

`ValidationRunner`'s own docstring names this as the reason the second observer exists: *"The main filesystem watcher only covers the docs root, so this runner owns a second, non-recursive watchdog observer on the project root to catch `SNAPSHOT.yaml` edits."* The mechanism is described; it is the thing that is not happening.

## How it survived

[[FEAT-0018]]'s acceptance says the badge "clears without restarting the shell", and [[CHG-20260730-Two-Features-Closed]] verified exactly that — with `performance.getEntriesByType('navigation').length` proving no reload. But the drift it induced was **a temporary note under `docs/`** carrying bad test fields. That goes through the main watcher. The SNAPSHOT path was never exercised, by that pass or by `tests/test_validation.py`, whose debounce/fan-out case also drives the bus with a `FileEvent` rather than through the observer.

So the claim is true as measured and narrower than it reads. Worth noting the shape: a passing live check whose induced fault took the working path.

## Diagnosed — it is the **case** of the watch path

None of the guesses above. macOS filesystems are case-**in**sensitive; FSEvents is case-**sensitive**. A watch registered on `/Users/edwin/…` receives events reported as `/Users/Edwin/…` and matches none of them. The observer starts, logs `validation: watching …/SNAPSHOT.yaml`, and never fires.

Isolated by running the **same repo with the same code** twice, differing only in how the path was spelled:

```
python -m project_os_cockpit /Users/Edwin/.../docs   →  touch SNAPSHOT.yaml  →  checked_at 14:18:16 → 14:18:18   RE-RAN
python -m project_os_cockpit /Users/edwin/.../docs   →  touch SNAPSHOT.yaml  →  checked_at 14:18:48 → 14:18:48   FROZEN
```

Two consequences that explain everything else:

- **The docs watcher was unaffected** because it is *recursive*, and watchdog's recursive emitter matches by prefix. Only the non-recursive SNAPSHOT watch is exact-match, so only it broke.
- **Every app-spawned sidecar had a dead SNAPSHOT watch.** The desktop shell stores discovered workspace roots as the path was typed, and this machine's home is `Edwin` while the stored roots are mostly `edwin`. A standalone sidecar started by `cd`-ing to the canonical path works, which is why this was never noticed from a terminal.

`Path.resolve()` does not help: it resolves symlinks and `..` and leaves case alone.

## Expected

Editing `SNAPSHOT.yaml` re-runs the validator within the debounce window, exactly as a docs-tree edit does.

## Next Actions

- [x] Reproduce in a test that drives the **observer**, not the bus — the existing coverage cannot see this
- [x] Fix, and keep the test
- [x] Re-check [[FEAT-0018]]'s acceptance wording once fixed

## Notes

Found because [[FEAT-0028]] made the same signal visible for ten repos at once. The fleet path itself is unaffected and was verified working in the same session: with the sidecar live, the docs-tree edit propagated `cockpit:validation` → main → renderer and cleared the rail badge without a restart. The cold pass re-runs the validator outright, so cold rows are also unaffected.


## Fixed 2026-07-30

`validation.canonical_case()` — resolve, then respell each component as the filesystem spells it, preferring an exact match so a genuinely case-sensitive filesystem is unaffected. A component that cannot be listed keeps its given spelling, so the failure mode is *exactly today's behaviour* rather than an exception in a constructor that runs on every server start.

`ValidationRunner.project_root` uses it, which puts the watch path, the validator's `--repo-root` and the deep-link rels on one value that cannot disagree with itself.

**Verified against the case that failed**: a sidecar invoked with the lowercase path now advances `checked_at` on `touch SNAPSHOT.yaml` (14:19:42 → 14:19:44), and logs the canonical path it is actually watching.

Three tests, mutation-verified by reverting to `Path(project_root).resolve()`. The main one skips on a case-sensitive filesystem, where the defect cannot occur.

### [[FEAT-0018]]'s acceptance wording

Re-read, and it does not need amending — "fixing the drift clears the badge without restarting the shell" was true, and is now true by both routes rather than one. What was narrow was the *evidence*, not the claim: the pass that verified it induced a fault under `docs/`, which took the working path. Worth carrying: a live check is only as good as the fault it induces, and inducing the convenient one is how a broken path stays green.
