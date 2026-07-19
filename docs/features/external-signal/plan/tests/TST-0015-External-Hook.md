---
type: "[[test]]"
id: TST-0015
aliases: ["TST-0015"]
title: "External agent-state hook — no-op scoping, state mapping, sidecar POST, fallback"
status: passing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
scope: feature
kind: automated
level: integration
entrypoint: ".venv/bin/python -m pytest tests/test_external_hook.py"
features: ["[[FEAT-0027-External-Session-Signal]]"]
tasks: ["[[TASK-0141]]", "[[TASK-0143]]"]
---

# TST-0015 — External hook

## What it verifies

`tests/test_external_hook.py` (4 tests) extracts the exact hook script embedded in `desktop/src/ipc/app-settings.ts` and runs it as Claude Code would (payload on stdin): no-op outside project-os repos (SNAPSHOT.yaml walk-up from a nested cwd); the busy/needs-input/waiting/idle state mapping written atomically with `source: external-hook`; unknown events leave state untouched; a stale `.cockpit/url` falls back to the file write; a live sidecar URL routes the payload into the full FEAT-0019 pipeline (session + prompt recorded, not just a dot). Desktop discovery-file behaviour is covered in `tests/test_sidecar_contract.py`.

## Evidence

- 2026-07-06: `4 passed`; full suite `189 passed, 1 skipped`.
- 2026-07-06: live manual run against this repo — stale 8899 discovery file fell back to a clean `agent-state.json` write; SessionEnd reset to idle.
