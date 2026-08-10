---
type: "[[task]]"
id: TASK-0381
aliases: ["TASK-0381"]
title: "The lifecycle status comes off the standing documents, and presence / singularity / stub / staleness are reported in its place"
status: done
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
- [x] No standing document carries a lifecycle `status:`; `updated:` is the field that means something
- [x] None of them appears in any in-flight count — the 18 references and the glossary leave [[ISS-0122]]'s `Doing` bucket by not having a status, not by being filtered
- [x] Four checks, reported distinctly: **missing** required entry, **two files** for one entry, **still a stub**, **stale**
- [x] Staleness is a **warning** with a stated horizon, never a build error
- [x] The stub check reuses the placeholder counting `brief_payload` already does for `LLM_BRIEF.md`
- [x] [[ISS-0124]] is answered: these types are recorded status-free rather than given status tables

## Steps
- [x] Strip `status:` from the eight; leave `updated:` and correct it where it lies
- [x] Add the checks to the validator against the merged manifest
- [x] Pick the staleness horizon and write down why that number
- [x] Re-run the fleet measurement afterwards — 85 of 90 stale is the before

## Notes
This removes [[ISS-0122]]'s **cause** rather than re-bucketing its symptom. That issue proposed excluding non-work types from the in-flight buckets; if these documents have no status at all, there is nothing to exclude. Worth resolving the two together so the fix is not applied twice in different shapes.

**Warning and not error** is deliberate and is the upstream ADR-0011 pattern: warn with a horizon, escalate only if the warning proves ignorable. A build that fails because a glossary is old gets the check disabled within a week.

The horizon needs a reason, not a round number. 90 days was the measuring threshold and is not automatically the right alarm.

## Done 2026-08-10

`status:` removed from all seven standing documents that carried one (`PHASES.md` never had one). `check()` in `standing.py` reports four kinds distinctly — **missing · ambiguous · stub · stale** — plus `has_status`, which is how the first finding stays closed.

### The measurable result

| | |
|---|---|
| Active mode's `Doing`, before | **45** |
| after | **39** |

Six standing documents left the work-in-flight bucket **by not having a status**, not by being filtered. That removes [[ISS-0122]]'s cause rather than re-bucketing its symptom, which is what that issue's own Next Actions asked for.

Remaining findings are honest: `DESIGN` and `STYLEGUIDE` stale at 196 days, `ARCHITECTURE` and `OWNERSHIP` still holding template placeholders.

### A lie I nearly shipped

Stripping the status, I also bumped every `updated:` to today — which made `DESIGN` and `STYLEGUIDE` claim they had been confirmed on 2026-08-10 when nobody has read them since January. **That is exactly the defect this feature exists to catch**, introduced by the change that catches it.

Reverted from git. Removing a field that should not exist is a mechanical edit; it is not a confirmation that the content is true. `GLOSSARY` and `ARCHITECTURE` keep today's date because [[TASK-0383]] genuinely edited their content.

### The horizon, and why 180

Not round for roundness. These do not decay the way a manual test does (`MANUAL_TEST_STALE_DAYS = 60`, where *"it passed once"* stops being an answer) — a glossary can be right for a year. What is worth catching is **abandonment**, and [[ISS-0125]] measured what that looks like: two documents untouched since the day they were created. 180 flags those and leaves a document someone revisits twice a year alone. Recorded as a parameter, with the fleet's 94% as the thing to re-measure against.

### Where the rule lives

`standing.py`, not `validate_docs_bundled.py` — that file is template-owned and held byte-identical (ISS-0026). Guarded locally and proposed upstream is the split [[ISS-0069]] and the PHASE-999 rule both took; [[TASK-0384]] is the proposal.
