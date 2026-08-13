---
type: "[[issue]]"
id: ISS-0156
aliases: ["ISS-0156"]
title: "The workspace you have open is the one whose unpushed count is never computed — `ahead` is a cold-pass-only field, and the cold pass skips live sidecars"
status: "open"
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'Can you double check this because I don't think the project-os-cockpit project is fully up to date?'"]
severity: high
component: desktop-fleet-health
parent: ""
related: ["[[FEAT-0098]]", "[[FEAT-0055]]", "[[ADR-0022]]", "[[PHASE-021-Git-Is-Not-The-Users-Job]]"]
tests: []
---

# The open workspace is the one whose unpushed count is never computed

## Problem

`ahead` and `remoteKind` are populated in exactly one place — the **cold pass** — and the cold pass **skips every workspace with a live sidecar**. A workspace you have open therefore has no unpushed count, on any surface, ever. So does any repo running a standalone cockpit, because `liveSidecarUrl()` also trusts a verified `.cockpit/url`.

The result is that [[FEAT-0098]]'s entire purpose fails for the repo most likely to need it: **the one you are working in**, which is the one accumulating commits.

## Repro (measured 2026-08-13)

1. `project-os-cockpit` is 2 commits ahead of `origin/main`; remote is `https://github.com/edankert/project-os-cockpit.git`, so `remote_kind` would be `backup` and the push would be offered.
2. Its sidecar is live: `.cockpit/url` → `http://127.0.0.1:8765`, whose `/api/cockpit/identity` returns this repo's root, so the shell subscribes to it.
3. Overview: **no unpushed band.** Agents → Docs health: **not in the "Not pushed" group.** Rail square tooltip: **no "commits not pushed" line.**

## Evidence

- `desktop/src/ipc/fleet-health.ts:364` — `const cold = getWorkspaces().filter((ws) => !subs.has(ws.id));` — live-subscribed workspaces are excluded from the batch by design (they "have a better answer already", which is true of *validator* state and false of *git* state).
- `desktop/src/ipc/fleet-health.ts:384-388` — `row.ahead` and `row.remoteKind` are assigned **only** inside `refreshColdWorkspaces()`.
- `desktop/src/ipc/fleet-health.ts:113-135` — `rowFromReport()`, the live path, never sets either field.
- `desktop/src/ipc/fleet-health.ts:239` and `:293` — the live path does `health.set(ws.id, rowFromReport(...))`, replacing the **whole row**. So a cold `ahead` learned before the sidecar came up is not merely un-refreshed, it is **erased** the moment a live report arrives.
- `src/project_os_cockpit/fleet_validate.py:118-150` — the git probe lives in the cold-pass script alone. The sidecar's `/api/cockpit/validation` payload carries no git state, so the live path has nothing to read even if it wanted to.

## Consequences

Three surfaces go quiet together, because all three read the same field:

- `renderer.ts:3852-3856` — `mountUnpushedBand()` computes `ahead = 0` from the missing field and returns before building the band.
- `renderer.ts:12923` — the fleet screen's group filters on `typeof r.ahead === 'number' && r.ahead > 0`.
- `renderer.ts:553-558` — the rail tooltip's `behind` string is empty when both fields are absent.

**The "no remote" half is lost the same way.** `remoteKind === 'none'` is also cold-only, so *"No remote — nothing here is backed up"* — the worse of the two facts, deliberately given its own sentence — never appears for a live workspace either.

The push itself is unaffected: `desktop/src/ipc/git.ts` re-derives the remote classification from `git remote get-url` and does not trust anything that arrived over IPC. This is a **visibility** failure, not a safety one.

## Why it matters more since 2026-08-12

[[ADR-0022]] lets the delegate push to non-deploy remotes, and [[FEAT-0098]] exists because *where it does not, the human has to be told* — Edwin, accepting it: *"if not pushed automatically then this should clearly be identified in the tool."* The surface built to tell him is blind in exactly the case it was built for.

## Expected

An open workspace reports its unpushed count and its remote kind like any other, and those fields survive a live validator report.

## Candidate fixes (not yet chosen)

1. **Probe git in the shell for live workspaces.** `git.ts` already runs `git -C <root>`; the process that owns the push button would then own the count. Cheapest, and keeps git state out of the validator payload.
2. **Split the cold pass in two** — validator state skips live workspaces, git state does not. Small change to `refreshColdWorkspaces()`, but keeps a subprocess in the loop for a question `git` answers in milliseconds.
3. **Teach the sidecar's `/api/cockpit/validation` to carry git state**, factoring `fleet_validate.py`'s probe out. Most uniform, largest blast radius, and it puts git state on a validator endpoint where it does not obviously belong.

Whichever is chosen, **the row merge must stop clobbering**: a live report should update validator fields and leave git fields alone (or refresh them), rather than replacing the row wholesale.

## Note on the class

`renderer.ts:589-594` already records this shape — *"data arriving after the surface that needs it has already painted"* — and counts it as the third occurrence that day. This is a fourth, but a different mechanism: not late data, **absent data**. The comment's confidence that "the band correctly renders nothing" is what kept it invisible; the band renders nothing correctly, from a field that is wrong.
