---
type: "[[issue]]"
id: ISS-0022
aliases: ["ISS-0022"]
title: "Repo is behind the project-os template: its vendored validator cannot see 8 real errors, and it never adopted the generated adapter surface"
status: fixed
severity: medium
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["self-discovered"]
related: ["[[FEAT-0039-Model-Routing-Subagents]]"]
---

# ISS-0022 — behind the template

## Symptom

`bash tools/scripts/validate-docs.sh` reports OK here, but running the **current** upstream validator against this repo reports 8 errors. The repo's own copy is simply older and lacks the checks:

- `DEFER-ORIGIN` / `DEFER-PARENT` ×2 each — TASK-0045 and TASK-0065 are `deferred` while still carrying `parent:`. `STATUSES.md` "Deferral and re-adoption" requires descoping: `parent` becomes `origin` provenance while the item is parked.
- `METRICS` ×4 — `features_total`/`features_done`/`tasks_total`/`tasks_done` drifted (the FEAT-0039 model-routing work landed after they were last computed).

This is the same class of blind spot as [[ISS-0021-Model-Routing-Review-Findings]]: enforcement that exists upstream cannot fire in a repo that has not synced.

## Cause

The whole fleet was synced from the template on 2026-07-24, but this repo was deliberately given a *narrow* adoption instead — only the model-routing hook and subagents were copied in, because the upstream working tree was carrying unrelated in-flight changes at the time (see [[TASK-0197-Upstream-And-Adopt]]). Upstream is now committed and clean, so the full sync can proceed.

Consequently this repo also never adopted the generated native adapter surface (`.claude/skills/`, `.cursor/rules/`) that `tools/scripts/generate-adapters.py` produces, and has no copy of the generator or the manifest-driven sync script.

## Special handling

Upstream vendors a copy of this project under `tools/cockpit/`, and the manifest marks that path template-owned. Syncing it into **this** repo would create a vendored duplicate of this very codebase inside itself, which would immediately drift from `src/project_os_cockpit/`. project-os-dev's TASK-0049 already records the standing hazard: *"the canonical file otherwise carries newer unrelated work — do not wholesale-copy over it when syncing."* `tools/cockpit/` is therefore removed after the sync; this repo is the canonical source for that code.

## Resolution

Full manifest sync from the committed upstream, `tools/cockpit/` dropped, adapters generated, and the 8 errors remediated. See [[CHG-20260724-Full-Template-Sync]].
