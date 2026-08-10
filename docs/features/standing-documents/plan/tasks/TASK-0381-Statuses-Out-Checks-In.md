---
type: "[[task]]"
id: TASK-0381
aliases: ["TASK-0381"]
title: "The lifecycle status comes off the standing documents, and presence / singularity / stub / staleness are reported in its place"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[REQ-0033-Every-Project-Can-Say-What-It-Is]]"]
parent: "[[FEAT-0091-The-Standing-Documents]]"
effort: M
due: ""
depends: ["[[TASK-0380-The-Manifest-As-Data]]"]
blocks: []
related: ["[[ISS-0124-Four-Note-Types-Have-No-Status-Table]]", "[[ISS-0122-Active-Modes-Doing-Column-Counts-Notes-Nobody-Is-Working]]"]
tests: []
---

# Statuses out, checks in

## Definition of Done
- [ ] No standing document carries a lifecycle `status:`; `updated:` is the field that means something
- [ ] None of them appears in any in-flight count — the 18 references and the glossary leave [[ISS-0122]]'s `Doing` bucket by not having a status, not by being filtered
- [ ] Four checks, reported distinctly: **missing** required entry, **two files** for one entry, **still a stub**, **stale**
- [ ] Staleness is a **warning** with a stated horizon, never a build error
- [ ] The stub check reuses the placeholder counting `brief_payload` already does for `LLM_BRIEF.md`
- [ ] [[ISS-0124]] is answered: these types are recorded status-free rather than given status tables

## Steps
- [ ] Strip `status:` from the eight; leave `updated:` and correct it where it lies
- [ ] Add the checks to the validator against the merged manifest
- [ ] Pick the staleness horizon and write down why that number
- [ ] Re-run the fleet measurement afterwards — 85 of 90 stale is the before

## Notes
This removes [[ISS-0122]]'s **cause** rather than re-bucketing its symptom. That issue proposed excluding non-work types from the in-flight buckets; if these documents have no status at all, there is nothing to exclude. Worth resolving the two together so the fix is not applied twice in different shapes.

**Warning and not error** is deliberate and is the upstream ADR-0011 pattern: warn with a horizon, escalate only if the warning proves ignorable. A build that fails because a glossary is old gets the check disabled within a week.

The horizon needs a reason, not a round number. 90 days was the measuring threshold and is not automatically the right alarm.
