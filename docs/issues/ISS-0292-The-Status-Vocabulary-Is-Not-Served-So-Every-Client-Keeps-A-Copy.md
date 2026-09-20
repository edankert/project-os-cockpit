---
type: "[[issue]]"
id: ISS-0292
aliases: ["ISS-0292"]
title: "Another app that reads the same notes has to keep its own copy of the status groups, the severity list and the note types, and its copy has already gone wrong once"
status: fixed
phase: ""
owner: user:edwin
created: 2026-09-09
updated: "2026-09-20"
reported_by: agent
source: ["Filed from project-os-deck on 2026-09-09, by TASK-0044 of FEAT-0012, which is the task that had to copy the vocabulary"]
severity: medium
component: api
parent: ""
related: []
tests: []
fixed_by: "[[TASK-0632-Fix-The-Seven-Defects-From-The-Issue-Review]]"
---

# Other apps must copy the status groups, severities and note types, and the copies go wrong

A second app over the same notes, such as project-os-deck, cannot ask the cockpit which statuses belong to which group, which severities exist, or which note types are known. It has to copy those lists into its own code. Deck's copy put `draft`, `proposed` and `ready` in the wrong group within two days, and Deck asks for an issue's severity in a free text box because it cannot ask for the four allowed values.

## Problem

**`statuses.py` is the single source of truth for which statuses exist and which band each belongs to, and nothing serves it.** Inside this repository that is fine: `test_status_vocabulary.py` parses `static/cockpit.js`, the two stylesheets and the Electron renderer so no surface here can fall behind. Outside it there is no such rope. A second application over the same corpus has to write the table down again, and nothing tells it when the table changes.

**It has already drifted once, in under two days.** project-os-deck copied the bands on 2026-09-07 and put `draft`, `proposed` and `ready` in its "doing" band, where `BANDS` puts all three in `pending`. Nothing caught it; it was found on 2026-09-09 while writing the task that reads the description's `band` section. Deck now pins its copy with a fixture recorded from `statuses.py` by a script, which turns the drift into a failing test — but a fixture is a workaround for the absence of an endpoint, not an answer to it.

**The same is true of two more vocabularies.** The severity order that bands the Issues view, and the set of known note types. A client that wants to draw either has the same choice: copy it, or do without.

## What would fix it

One read endpoint carrying the vocabulary as data — the bands with their members, the completed set, the legacy mapping, the severity order, the known types — so a client can ask instead of copying. It is a read, so it fits behind the existing guards and needs no new write surface.

## A second consequence, measured on 2026-09-09

**Deck now asks for a severity in a free text box, because the four values are not available to ask for.** `/api/notes/transition` accepts a `severity` while an issue leaves `triage`, and refuses anything outside `SEVERITIES` — `critical`, `high`, `medium`, `low`. `/api/notes/actions` returns the verbs for that transition and says nothing about the severities, so the surface offering the verb cannot offer the values that go with it.

Deck's choice was a text box and the sidecar's refusal quoted back, rather than a picker with the four values written into Deck. A picker would have been better for the person using it, and it would have been a fifth copy of a table this issue is about. That trade is the cost of the missing endpoint, stated as a thing somebody sees rather than as a principle.

## Why this is filed rather than worked around

`docs/reference/cockpit-capability-register.md` describes what the cockpit can do, and Deck's `docs/reference/cockpit-adoption.md` tracks what it has adopted. A capability that exists only as a Python module cannot be adopted, only duplicated. This is the issue the Deck task was required to file on the day it started copying, following the same pattern as the whole-edge-list endpoint.

## Where the copy lives now

- `project-os-deck/desktop/src/shared/statuses.ts` — the copy.
- `project-os-deck/desktop/fixtures/cockpit-statuses.json` — recorded from `statuses.py` on 2026-09-09 at commit `11ded07`.
- `project-os-deck/tools/scripts/record-sidecar-fixture.py` — what records it.
- `project-os-deck/desktop/tests/band-and-face.test.mjs` — what fails when the two diverge.

## Next Actions
- [x] Decide whether the vocabulary is worth serving, or whether a pinned copy per client is the accepted answer
- [x] If it is served, name the endpoint and the shape, and tell Deck so its copy can go

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** In project-os-deck, choosing an issue's severity means typing it into a free text box and reading the refusal if it is wrong. When the cockpit's status groups change, Deck keeps showing the old groups until someone notices and re-records its copy.

Evidence: the lists still live only in Python modules: `src/project_os_cockpit/statuses.py:56` (`BANDS`), `:114` (`COMPLETED_STATUSES`), `:136` (`LEGACY_STATUS_BAND`), `cockpit.py:401` (`SEVERITY_ORDER`), `note_writes.py:225` (`SEVERITIES`), `callouts.py:39` (`KNOWN_TYPES`). `grep -n '"band"\|SEVERITY_ORDER\|SEVERITIES\|KNOWN_TYPES' src/project_os_cockpit/server.py` finds nothing, and none of the `/api/...` routes listed in `server.py` serves them.

Small fix: yes. One read-only route that returns these six constants as JSON, behind the existing guards, plus a test that fails if a constant is missing from the reply. Telling Deck to drop its copy is separate work in that repo.

**Belongs to:** no feature. **Next:** add one read route (for example `GET /api/cockpit/vocabulary`) and record it in `docs/reference/cockpit-capability-register.md` so Deck can adopt it.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).

## Fixed 2026-09-20 (TASK-0632)

**What changed.** `GET /api/cockpit/vocabulary` serves the tables. It is a read, so it sits behind the guards every other read sits behind and adds no write surface. The payload is built by `cockpit.vocabulary_payload()` from the modules that own each table, so there is still one authority and the route is a view of it rather than a seventh copy:

| key | what it carries | source |
| --- | --- | --- |
| `bands` | each band with its members | `statuses.BANDS` |
| `band_tokens` | the CSS custom property per band | `statuses.BAND_TOKEN` |
| `completed` | the terminal set, sorted | `statuses.COMPLETED_STATUSES` |
| `legacy_bands` | retired values mapped to the band they used to occupy | `statuses.LEGACY_STATUS_BAND` |
| `severity_order` | the ranking the Issues view bands by | `cockpit.SEVERITY_ORDER` |
| `severities` | the values a write will accept, sorted | `note_writes.SEVERITIES` |
| `callout_types` | the `> [!type]` names that render, sorted | `callouts.KNOWN_TYPES` |

**Two things a client should know.** `severity_order` and `severities` are separate on purpose — one is a ranking a view draws with, the other is a write-time refusal list — and they hold the same four values today only by coincidence. Everything derived from a Python set is sorted before it is sent, because a frozenset's iteration order is not stable across runs and Deck pins this kind of payload to a fixture.

**Which test guards it.** `tests/test_vocabulary_route.py`, four cases over the live route: every table present and equal to its source module; the three statuses Deck banded wrong are in `pending` and not in `active`; the served severities are exactly the ones `/api/notes/transition` accepts, asserted both ways; and two consecutive calls return byte-identical JSON with the set-derived lists sorted.

**Run both ways.** With the route: `4 passed`. With `server.py` and `cockpit.py` reverted: `4 failed`, all on the 404.

**Recorded where Deck will look.** `docs/reference/cockpit-capability-register.md` gains the row `api.read.vocabulary`.

**What is still owed, in the other repository.** Deck can now drop `desktop/src/shared/statuses.ts`, `desktop/fixtures/cockpit-statuses.json`, `tools/scripts/record-sidecar-fixture.py` and the fixture half of `desktop/tests/band-and-face.test.mjs`, and it can offer a severity picker instead of a text box. None of that is done here; it is work in `project-os-deck` and this issue closes on the endpoint existing.
