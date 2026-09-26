---
type: "[[change]]"
id: CHG-20260719-Terminal-Survivability-And-Identity-Guard
aliases: ["CHG-20260719-Terminal-Survivability-And-Identity-Guard"]
title: "tmux-backed terminal survivability + sidecar identity guard (agents outlive the app; hooks can't cross workspaces)"
status: merged
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
commit: ""
pr: ""
impacts: ["embedded terminal", "sidecar /api/agent-hook", "new /api/cockpit/identity", "desktop startup", "app quit flow"]
issues: ["[[ISS-0007-Stale-Url-Cross-Workspace-Poisoning]]", "[[ISS-0008-Terminal-Sessions-Die-With-App]]"]
features: ["[[FEAT-0007-Desktop-Shell]]", "[[FEAT-0027-External-Session-Signal]]"]
reviewed_by: "model:claude-opus"
review_date: 2026-07-19
review_verdict: approved
related: ["[[TST-0017]]"]
---

# Terminal survivability + identity guard (ISS-0008, ISS-0007)

## Summary

**Survivability (TASK-0144/0145):** workspace terminals are now tmux clients on a dedicated socket (`tmux -L cockpit`, generated conf, sessions named `cockpit-<workspace-id>`), so the tmux server — not the Electron app — owns the shell. App death (crash, kill, quit) merely detaches; relaunch runs `new-session -A` and lands back in the still-running session, so an in-flight claude keeps working headless across app restarts. Instrumentation env rides `new-session -e` (tmux ≥ 3.2 required; discovery probes homebrew/system paths since GUI apps lack shell PATH; `COCKPIT_NO_TMUX=1` or no tmux → previous direct spawn). Explicit terminal dispose kills the tmux session; app shutdown deliberately kills only clients. `before-quit` now warns when a busy/needs-input agent sits in a *fallback* (non-tmux) terminal; fallback spawns print a display-only `claude --resume <id>` hint when the workspace's session index shows a recent unended session. Verified end-to-end via the exact node-pty spawn path: session survives client kill with its process running, reattach replays the live screen, env injection confirmed. tmux was installed via Homebrew as part of this change.

**Identity guard (TASK-0146):** closes ISS-0007's cross-workspace poisoning. `POST /api/agent-hook` now rejects (409 `wrong-cockpit`) payloads whose `cwd` resolves outside the sidecar's project root (case-normalised); the external hook's existing fallback then writes agent-state into the correct repo — misrouted events self-heal instead of poisoning a sibling's tracker, session index, and rail dot. Also stops foreign attribution when a user `cd`s out of a workspace inside its terminal. New `GET /api/cockpit/identity` returns `{root, docs_root, pid}`; the desktop app runs a startup janitor that probes every discovered workspace's `.cockpit/url` against it and unlinks dead or wrong-root files (live standalone sidecars with matching roots are untouched). First live run removed four stale url files. Covered by `tests/test_identity_guard.py` (TST-0017, 7 tests incl. a full ISS-0007 replay through the shipped external-hook script); suite green (24 passed with adjacent hook suites).

Independent review (opus) caught that `os.path.normcase` is a no-op on macOS — the guard's case-insensitivity was illusory and the test mangled a below-root component that couldn't detect it. Folded in: explicit `.casefold()` on both sides of the containment check (aligning with the janitor's `toLowerCase`), a root-component case-mangling test that fails if the folding is removed, and a janitor retry so a just-spawning sidecar's fresh url isn't unlinked on a single failed probe.

Files: `desktop/src/ipc/terminal.ts`, `desktop/src/ipc/agent-state-poller.ts`, `desktop/src/main.ts`, `src/project_os_cockpit/server.py`, `tests/test_identity_guard.py`.
