---
type: "[[issue]]"
id: ISS-0072
aliases: ["ISS-0072"]
title: "The validator never re-runs on a SNAPSHOT.yaml edit — its dedicated project-root observer does not fire, so METRICS drift never clears live"
status: open
severity: medium
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["found during TASK-0250's live pass, 2026-07-30"]
component: sidecar
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[TASK-0111-Validation-Runner]]", "[[FEAT-0028-Fleet-Health-Surface]]", "[[CHG-20260730-Two-Features-Closed]]"]
fixed_by: []
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

## Not diagnosed

Whether `start()` is not called, the observer is not started, `on_any_event` does not match, or watchdog's macOS backend does not deliver events for a non-recursive watch on a directory whose children are mostly ignored. The evidence above is behavioural only.

## Expected

Editing `SNAPSHOT.yaml` re-runs the validator within the debounce window, exactly as a docs-tree edit does.

## Next Actions

- [ ] Reproduce in a test that drives the **observer**, not the bus — the existing coverage cannot see this
- [ ] Fix, and keep the test
- [ ] Re-check [[FEAT-0018]]'s acceptance wording once fixed

## Notes

Found because [[FEAT-0028]] made the same signal visible for ten repos at once. The fleet path itself is unaffected and was verified working in the same session: with the sidecar live, the docs-tree edit propagated `cockpit:validation` → main → renderer and cleared the rail badge without a restart. The cold pass re-runs the validator outright, so cold rows are also unaffected.
