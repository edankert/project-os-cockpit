---
type: "[[test]]"
id: TST-0015
aliases: ["TST-0015"]
title: "External agent-state hook — no-op scoping, state mapping, sidecar POST, fallback"
status: passing
covers: ["[[FEAT-0027-External-Session-Signal]]"]
command: ".venv/bin/pytest tests/test_external_hook.py -q"
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-09-25
scope: feature
level: integration
entrypoint: ".venv/bin/python -m pytest tests/test_external_hook.py"
tasks: ["[[TASK-0141]]", "[[TASK-0143]]"]
last_verified: "2026-09-25"

---

# TST-0015 — External hook

## What it verifies

`tests/test_external_hook.py` (4 tests) extracts the exact hook script embedded in `desktop/src/ipc/app-settings.ts` and runs it as Claude Code would (payload on stdin): no-op outside project-os repos (SNAPSHOT.yaml walk-up from a nested cwd); the busy/needs-input/waiting/idle state mapping written atomically with `source: external-hook`; unknown events leave state untouched; a stale `.cockpit/url` falls back to the file write; a live sidecar URL routes the payload into the full FEAT-0019 pipeline (session + prompt recorded, not just a dot). Desktop discovery-file behaviour is covered in `tests/test_sidecar_contract.py`.

## Evidence

- 2026-07-06: `4 passed`; full suite `189 passed, 1 skipped`.
- 2026-07-06: live manual run against this repo — stale 8899 discovery file fell back to a clean `agent-state.json` write; SessionEnd reset to idle.

## September 23 Codex extension

`test_codex_external_forwarding_and_fallback` runs the generated script in Codex mode, checks agent/session identity, offline state, interruption through late events, new-prompt recovery and deduplication against an embedded event. `cd desktop && npm run build && node --test tests/codex-external-hooks.test.mjs` checks surgical enable/refresh/disable, one-time backup, mixed user groups, spaces and apostrophes, untouched config.toml, and malformed-input refusal. Full-suite counts are recorded on FEAT-0027. TST-0011 separates real external CLI evidence from these fixtures.

## Run, 2026-09-25

`.venv/bin/pytest tests/test_external_hook.py -q -p no:randomly`: 6 passed. Run at FEAT-0019 and FEAT-0027's close-out, after Edwin's live TST-0011 run the same day.
