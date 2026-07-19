---
type: "[[task]]"
id: TASK-0059
aliases: ["TASK-0059"]
title: "Python sidecar contract: --no-open, /healthz, COCKPIT_DESKTOP env var"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: []
parent: "FEAT-0007"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0061]]"]
related: []
tests: []
---

# Python sidecar contract additions

## Definition of Done
- [ ] `python -m project_os_cockpit ... --no-open` runs the server but does not
      attempt any browser auto-launch.
- [ ] `GET /healthz` returns `200` once the index is built, `503` before.
- [ ] When `COCKPIT_DESKTOP=1` is in the environment, the sidecar does NOT
      spawn `ttyd` and does NOT write `.cockpit/url`.
- [ ] Mode 1 (browser, no flag, no env var) produces behaviour identical to
      today — verified by a new TST-* note.
- [ ] A test confirms the `/healthz` 503 → 200 lifecycle.

## Steps
- [ ] Add `--no-open` to the CLI parser; thread to wherever browser
      auto-launch currently lives (if anywhere — confirm).
- [ ] Add `/healthz` to `server.py`; return 503 until the index is populated.
- [ ] Gate `ttyd` spawn and `.cockpit/url` write on
      `os.environ.get("COCKPIT_DESKTOP") != "1"`.
- [ ] Add `TST-####-Sidecar-Contract.md` under `docs/features/desktop-shell/plan/tests/`.

## Notes
This is the only Python-side change required for the desktop shell. All
additions are gated; defaults are unchanged. The new TST-* belongs under
the desktop-shell feature (it verifies behaviour exclusive to mode 3) per
the hybrid test-storage rule.
