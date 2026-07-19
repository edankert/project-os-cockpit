---
type: "[[issue]]"
id: ISS-0007
aliases: ["ISS-0007"]
title: "Stale .cockpit/url + port reuse routes one workspace's hook events into another workspace's sidecar"
status: fixed
severity: high
component: agent-instrument
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-18
updated: 2026-07-18
parent: "[[FEAT-0027-External-Session-Signal]]"
related: ["[[ISS-0001-WatcherIndexedPathCaseMismatch]]", "[[RISK-0004]]"]
---

# ISS-0007 — stale discovery url poisons a sibling workspace's tracker

## Problem

Observed live 2026-07-18: after the desktop app was killed (unclean exit) and relaunched, a Claude session running in `project-os-cockpit` had its hook events ingested by the **your-sudoku** sidecar — sudoku's `.cockpit/sessions.json` gained a session with `cwd: /Users/Edwin/Dev/repos/project-os-cockpit`, and sudoku's rail square showed that session's busy/waiting states ("awaiting input" for a workspace with no live agent). Mechanism: sidecar ports are allocated by portfinder and reused across app restarts; `.cockpit/url` is only rewritten when that workspace's own sidecar spawns, and only unlinked on **clean** shutdown (`server.py:1747`). After a SIGKILL, every workspace keeps its old url; on the next launch another workspace's sidecar can claim the same port, so the external hook (`~/.claude/settings.json`, FEAT-0027) and the `cockpit` CLI walk up to a url file that now points at a *different project's* sidecar and POST there. The receiving tracker has no identity check — it ingests whatever arrives, poisoning its session index, agent-state file, and rail marker, and `cockpit focus`/`state` calls can hit the wrong cockpit the same way.

## Impact

- Wrong-workspace attribution of agent state (false "awaiting input"/busy dots) — directly misleads the at-a-glance rail.
- Session index pollution (foreign cwd sessions in `.cockpit/sessions.json`).
- CLI misrouting (`cockpit focus` targeting a sibling repo's UI).
- Not affected: main-process dispatch delivery (keyed on live workspaceId→url map, not the url file).

## Fix (TASK-0146, 2026-07-19)

Implemented directions 1 and a probe-based variant of 3 (see [[CHG-20260719-Terminal-Survivability-And-Identity-Guard]]): `POST /api/agent-hook` rejects foreign-`cwd` payloads with 409 `wrong-cockpit` (case-normalised containment against the served root), which flips the external hook onto its file-write fallback in the correct repo; new `GET /api/cockpit/identity` returns `{root, docs_root, pid}`; the desktop app's startup janitor probes every discovered workspace's `.cockpit/url` against the identity endpoint and unlinks dead or wrong-root files (its first live run removed four stale urls). Guarded by TST-0017 (`tests/test_identity_guard.py`, includes a full replay of this incident through the shipped external-hook script). Residual (accepted): a CLI `cockpit focus/state` between two live mismatched servers inside the janitor's startup window; the observed failure mode is closed.

### Original fix directions (for the record)

1. **Server-side identity guard (cheapest, closes the hole for all callers):** hook payloads already carry `cwd`; the tracker knows its own project root — reject (404/409) events whose `cwd` does not resolve inside the served root, so a stale-url POST fails and the hook falls back to its atomic `agent-state.json` write in the correct repo.
2. Identity handshake in the url file: write `{url, root, pid}` instead of a bare url; hook/CLI verify `root` matches the walk-up root before POSTing (belt-and-braces with 1).
3. Poller/janitor: on app launch, main process unlinks `.cockpit/url` for every discovered workspace whose sidecar it did not (yet) spawn — removes the stale window entirely.
