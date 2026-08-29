---
type: "[[issue]]"
id: ISS-0259
aliases: ["ISS-0259"]
title: "Six fleet repos are ten upstream rules behind — outside PHASE-041's scope because they hold no acceptance checks, and now measured rather than assumed"
status: open
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
severity: low
component: tooling
phase: "[[PHASE-999-Future]]"
related: ["[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[TASK-0585-Drift-Is-Measured-Not-Noticed]]"]
---

# Six more repos, ten rules each

[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]] scoped four repos — the ones holding acceptance checks. `tools/scripts/fleet-drift.py` walks every `SNAPSHOT.yaml`-bearing repo, and there are **twelve**. Measured 2026-08-29 after the four migrations:

| repo | upstream rules missing | line divergence | acceptance checks |
|---|---|---|---|
| `articles` | 10 | 619 | 0 |
| `edankert.com` | 10 | 619 | 0 |
| `project-os-bench` | 10 | 619 | 0 |
| `project-os-dev` | 10 | 619 | 0 |
| `your-applications.com` | 10 | 619 | 0 |
| `yourtrainer-mcp` | 10 | 619 | 0 |

The ten, read from `fleet-drift.py --json` rather than recalled: `ACCEPT-STALE`, `ACCEPTANCE-STATUS`, `DECISION-OPTIONS`, `DESIGN-GATE`, `FEATURE-UNCOVERED`, `PARENT-BACKLINK`, `SNAPSHOT-MEMBERSHIP`, `STATUS-TYPE`, `TEST-ENTRYPOINT` and `VERIFY-ACCEPTANCE`. Two of them — `PARENT-BACKLINK` and `SNAPSHOT-MEMBERSHIP` — have nothing to do with acceptance and are exactly the pair the four migrations turned out to be entirely about, so these six repos carry the same unreconciled backlink debt the other four just paid.

**Not a finding against PHASE-041's scope**, which was deliberate and stated: the phase is *"the gate runs where the checks are"*, and these repos hold none. It is a finding the drift check produced on its first run, which is what it is for.

`fleet-drift.py` reports them and does not fail on them ([[project-os-dev#ADR-0011]] clause 3 — a check promoted over existing debt fails every build the day it ships and gets switched off). `--gate-all` says otherwise for anyone who wants it.

## Done when

- [ ] Each of the six is migrated with `tools/scripts/migrate-fleet-validator.py`, or recorded as deliberately outside the fleet gate.
- [ ] `fleet-drift.py --gate-all` exits 0, at which point the default and the strict mode agree and the distinction can go.
