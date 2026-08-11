---
type: "[[issue]]"
id: ISS-0134
aliases: ["ISS-0134"]
title: "`Caught up` cannot clear the digest — the needs-you half is never filtered by the watermark at all, and the watermark it writes is a commit date rather than a moment"
status: triage
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["Edwin, 2026-08-11: 'The overview since you looked section is great but does not update after selecting caught up, it shows the same info again.'"]
severity: high
component: "cockpit-api"
parent: ""
related: ["[[FEAT-0071-Since-You-Looked]]", "[[PHASE-026-The-Returning-Human]]", "[[REL-0001-The-Human-Has-Levers]]"]
tests: []
---

# `Caught up` cannot clear the digest

## Problem

Clicking `Caught up` removes the band, and the next time the overview renders the same digest is back. Edwin has clicked it three times — `.cockpit/last-seen.json` records `caught_up_count: 3` — and the watermark still reads `2026-08-10` while the digest reports 109 transitions and 93 needs-you rows.

There are **two independent causes**, and only the second is a documented trade-off.

### 1. The needs-you half is never filtered by the watermark (the real defect)

`digest_payload` filters the *transitions* half against `seen_at`. It then builds `needs_you` by walking the entire index:

```python
for path in index.paths():
    ...
    flag = _owed_flag(record)
    if flag.get("owed"):
        needs_you.append({**_slim_note(record), **flag})
```

No comparison against `seen_at` occurs anywhere in that loop, or in the `review_verdict` loop after it. **The needs-you half is therefore identical before and after `Caught up`, by construction** — 93 rows either way.

This is the half [[DES-0008]] deliberately lifts *above* the news, on the reasoning that a reader who stops halfway should have seen the obligations. It is the half that cannot be dismissed.

Arguably an obligation *should* persist until discharged rather than until read — but then `Caught up` should not appear to dismiss it, and the band should not return looking unchanged. The current behaviour promises an action it does not perform.

### 2. The watermark is a commit date, not a moment

```python
"computed_at": (history.get("commits") or [{}])[0].get("date", ""),
```

`computed_at` is the newest **commit's date at day granularity** (`2026-08-11`), not the moment the digest was computed. `Caught up` posts it verbatim and it becomes `seen_at`. Combined with the deliberate strictly-less comparison —

```python
if marker and when and when < marker[:10]: continue
```

— the watermark's own day is always included. The code documents this and defends it: re-showing a seen commit is corrected by reading, whereas hiding a commit made after catching up is invisible. That reasoning holds.

What it does not survive is a **working day**: while commits are still landing on today's date, no click can advance past them, so the digest is permanently unclearable exactly when it is most active. Three clicks produced no visible change for that reason.

## Repro

1. Commit anything today.
2. Open the overview; the `Since you looked` band lists today's transitions and the needs-you rows.
3. Click `Caught up`. The band disappears.
4. Navigate away and back. The band returns with the same contents.

## Expected

`Caught up` visibly changes the digest, or does not offer to.

## Actual

`caught_up_count: 3`, `seen_at: "2026-08-10"`, 109 transitions and 93 needs-you rows still reported.

## Evidence

- `src/project_os_cockpit/cockpit.py:4875` onward — `needs_you` built with no `seen_at` comparison.
- `src/project_os_cockpit/cockpit.py:4908` — `computed_at` from the newest commit's date.
- `src/project_os_cockpit/cockpit.py:4872` — `when < marker[:10]`, with the trade-off documented above it.
- `.cockpit/last-seen.json` 2026-08-11: `{"seen_at": "2026-08-10", "caught_up_count": 3}`.
- `GET /api/cockpit/digest` 2026-08-11: `computed_at='2026-08-11'`, `seen_at='2026-08-10'`, 109 transitions, 93 needs-you.

## Next Actions

- [ ] Decide what `Caught up` means for the needs-you half — dismiss-until-changed, or leave it and stop implying the button covers it. This is a design decision, not a code fix; [[DES-0008]] is where it belongs.
- [ ] Give the digest a real `computed_at` (an actual timestamp) and store watermarks at that precision, so a same-day catch-up can advance. The day-granularity commit date is the source of the "working day" failure, not the comparison operator.
- [ ] A test that clicks catch-up twice and asserts the second digest differs from the first — the assertion that would have caught this on the day it shipped.
