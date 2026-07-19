---
type: "[[task]]"
id: TASK-0146
aliases: ["TASK-0146"]
title: "Sidecar identity guard — reject foreign-cwd hook events, identity endpoint, stale-url janitor"
status: doing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: ["[[ISS-0007-Stale-Url-Cross-Workspace-Poisoning]]"]
parent: "FEAT-0027"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[ISS-0007]]", "[[TASK-0143]]"]
tests: ["[[TST-0017]]"]
---

# TASK-0146 — sidecar identity guard

## Goal

Close ISS-0007 (one workspace's hook events landing in another workspace's sidecar) at both ends:

1. **Server-side ingest guard:** `POST /api/agent-hook` rejects (409) payloads whose `cwd` does not resolve inside the sidecar's own project root (parent of the served docs root; case-normalised per the ISS-0001 lesson). The external hook treats the 409 as a failed POST and falls back to its atomic `agent-state.json` write in the *correct* repo, so misrouted events self-heal instead of poisoning the tracker, session index, and rail dot. Payloads without `cwd` stay accepted (forwarder/statusline compatibility). This also stops a second variant: `cd`-ing out of a workspace inside its embedded terminal no longer lets foreign sessions claim that workspace's marker.
2. **`GET /api/cockpit/identity`:** tiny endpoint returning `{root, docs_root, pid}` so callers can verify who they're talking to.
3. **Startup janitor (desktop):** at launch, for every discovered workspace with a `.cockpit/url`, probe the identity endpoint; unlink the file when the server is unreachable or reports a different root. Standalone (non-desktop) sidecars answer with a matching root and are left alone.

## Residual (accepted)

`cockpit focus/state` CLI calls between two *live* mismatched servers in the janitor's blind window are still possible in principle; the guard + janitor eliminate the observed failure mode (stale url after unclean app exit + port reuse).
