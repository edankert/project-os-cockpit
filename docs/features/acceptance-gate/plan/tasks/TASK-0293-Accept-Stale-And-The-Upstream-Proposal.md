---
type: "[[task]]"
id: TASK-0293
aliases: ["TASK-0293"]
title: "The ACCEPT-STALE warning, and the convention proposed upstream"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0064-The-Acceptance-Gate]]"]
parent: "[[FEAT-0064-The-Acceptance-Gate]]"
effort: S
depends: ["[[TASK-0291]]"]
blocks: []
related: []
tests: []
---

# The ACCEPT-STALE warning, and the convention proposed upstream

## Definition of Done

- Local validator warning when `done` + `requested` exceeds the age threshold; warning not error, per the phase's rubber-stamp argument.
- The upstream proposal note files the field, the stamp discipline and the warning with project-os — the close-out-rule route.

## Done — 2026-08-11

`ACCEPT-STALE` in `validate-docs.py`: a `done` feature carrying `acceptance: requested` for longer than the staleness window (90 days here, `verification.staleness_days`) gets a **warning**.

**A warning, never an error, and that is the phase's whole argument.** Acceptance is the one judgment that cannot be automated, and a gate that *blocks* on it becomes a rubber stamp — somebody clears it to get the build green rather than because they looked. So it nags, visibly and indefinitely, and never stops the work. Same shape independent review took: warning first, [[project-os-dev#ADR-0011]]'s deadline mechanism only if it earns one.

Proven both ways rather than asserted: it fires on a crafted `done` + `requested` + `updated: 2025-01-01` feature (*"has asked for acceptance for 587 days (threshold 90)"*), and is **silent** when the same feature's request is fresh.

Age comes from `updated:` — the only date every note carries — read through the file's own `_parse_date`/`_today`, so a malformed date is skipped rather than raising on a validator that walks the whole corpus.

**One thing this task taught, at some cost.** `validate-docs.py` takes `--repo-root`, not a positional path. An earlier verification in [[TASK-0288]] passed a positional path, the script exited on a usage error, and `grep -c ERROR` returned zero — which reads exactly like a clean run. Corrected there; worth naming here because the same shape would silently pass any future check written the same way.
