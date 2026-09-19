---
type: "[[issue]]"
id: ISS-0308
aliases: ["ISS-0308"]
title: "Re-ticking a step whose check stays owed writes a second identical ledger event, so one walk can leave duplicate verdicts"
status: fixed
phase: ""
owner: user:edwin
created: 2026-09-14
updated: "2026-09-19"
reported_by: review
source: ["Independent review of [[FEAT-0150-The-Walk-Page-Reads-As-A-Script]], 2026-09-14, finding 4"]
severity: low
component: renderer
parent: ""
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[TASK-0624-A-Tick-Per-Step]]"]
tests: []
tags: [issue, acceptance, ledger, walk]
---

# Re-ticking a step writes a second identical verdict

## Problem

A `fail` or a `question` keeps a check owed, so its steps keep printing on the walk page and can be ticked again. Each re-tick writes another ledger event. Ticking one step twice with the same mark and the same reason produces two identical entries — same check, same mark, same reason, same date — from a single walk.

Found by independent review, 2026-09-14.

## Why it is low, and why it is still filed

The ledger is an event log and re-walking a check legitimately writes a new verdict; [[TASK-0624-A-Tick-Per-Step]]'s own note says a check is re-marked by re-walking. So a second event is not corruption, and `ledger.resolve` reads the latest, so no surface reports anything wrong.

What it costs is readability. The mark dialog shows every event ever recorded against a check ([[ISS-0281]]), and a walker who ticked a step twice by accident sees their history doubled with no way to tell the accident from a genuine second walk.

## What would close this

- [ ] Either the page declines to write when the combined mark and reason are identical to the check's standing verdict, or it asks — *"this records the same verdict again; walk it?"* Deciding which is the point of triage.
- [ ] Whatever is chosen, an intentional re-walk must still be possible: the fix must not make a check unre-markable, which would be worse than a duplicate line.

## Checked against the code, 2026-09-19: already done

Evidence: FEAT-0151 (commit 476ee97, 2026-09-17) added a guard to the walk page's step tick. `desktop/src/renderer/renderer.ts:12915-12918` finds the latest event for the check on this platform and skips the write when it has the same mark and the same reason and is not invalidated. An intentional re-walk still writes, because the guard is bypassed when `newRun` is set (`markWalkStep`, line 12823). Tests: `desktop/tests/walk-page.test.mjs:1892` ("partial and question corrections append history without an accidental duplicate"), with the assertions at lines 2138 ("retrying the identical result appended a duplicate event") and 2195.

**Belongs to:** FEAT-0151. **Next:** nothing.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
