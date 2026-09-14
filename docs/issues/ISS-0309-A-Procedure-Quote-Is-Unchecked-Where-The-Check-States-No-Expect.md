---
type: "[[issue]]"
id: ISS-0309
aliases: ["ISS-0309"]
title: "A procedure's expectation quote is checked against nothing when its check states no `## Expect`, which is 25 of your-trainer's 39 owed rows"
status: triage
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["Independent review of [[FEAT-0150-The-Walk-Page-Reads-As-A-Script]], 2026-09-14, finding 8"]
severity: medium
component: upstream
parent: ""
related: ["[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"]
tests: []
tags: [issue, acceptance, walk, upstream]
---

# A procedure quote is unchecked where the check states no Expect

## Problem

The walk page is allowed to pass a check from a step tick because each expectation line quotes that check's own `## Expect` text word for word and the upstream validator checks the quote. That is the argument recorded on [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]] and repeated in [[FEAT-0150-The-Walk-Page-Reads-As-A-Script]].

The argument is wider than the code. `audit_procedure` in the bundled walk module reports no problem when the check it is quoting states no `## Expect` section at all — there is nothing to compare against, so the quote passes by default.

Measured by independent review on 2026-09-14: **14 of `your-trainer`'s 39 owed rows carry Expect lines. For the other 25 the quote is unchecked**, and a step tick could pass them on a sentence the procedure's author invented.

## Why this is filed here and fixed upstream

`walk_sheet_bundled.py` is a byte-identical copy of the template's `tools/scripts/walk-sheet.py`, guarded by a test. **It must not be patched locally** — a local patch to a bundled copy is how one rule becomes two. The fix belongs in `~/Dev/repos/project-os-dev` and arrives here by sync.

## What would close this

- [ ] Upstream decides what a quote against an absent `## Expect` means. The two honest answers are to refuse the procedure, or to accept it and mark the tag as unverified so the page can say so.
- [ ] Until then, the walk page's ADR-0041 justification is accurate for checks that state an expectation and optimistic for those that do not. Whether that is acceptable is Edwin's call, not the tool's.
- [ ] A count of unchecked quotes per sitting, wherever it lands, so a walker can see how much of a procedure is attested.
