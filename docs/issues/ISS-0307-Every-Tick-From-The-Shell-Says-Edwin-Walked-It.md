---
type: "[[issue]]"
id: ISS-0307
aliases: ["ISS-0307"]
title: "Every verdict written from the shell records `by: user:edwin`, so a ledger cannot say whether a person or an agent walked the check"
status: triage
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["Independent review of [[FEAT-0150-The-Walk-Page-Reads-As-A-Script]], 2026-09-14, finding 11"]
severity: medium
component: ledger
parent: ""
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[FEAT-0149-The-Walk-Page]]", "[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]"]
tests: []
tags: [issue, ledger, acceptance]
---

# Every tick from the shell says Edwin walked it

## Problem

`postCheckVerdict` in `desktop/src/renderer/renderer.ts` sends `by: 'user:edwin'` on every write, whoever clicked. The ledger's `by:` is therefore not evidence of who walked a check — it is a constant. An agent driving the page through the harness, which is how [[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]] was walked on 2026-09-14, writes verdicts indistinguishable from Edwin's own.

Found by independent review, 2026-09-14, while checking who had walked TST-0089. The answer could not be read from the record, only from the prose somebody happened to write beside it.

## Why it matters

[[ADR-0037-A-Verdict-Is-An-Event]] made a verdict an event with an author precisely so a reader could ask who said so. A field that always says the same thing answers that question falsely rather than not at all, which is the worse of the two.

It also interacts with the review gate: if an agent can walk a manual check and the ledger records a person, the distinction between "somebody looked at this" and "a script clicked it" is not in the record.

## Evidence

`method:` already distinguishes `manual` from other origins, and it is correct — an agent driving the page IS performing a manual walk. What is missing is the author.

The one entry corrected by hand so far is TST-0089 in `docs/releases/ledgers/WORKING-macos.json`, now `by: model:claude-opus-5`. Every other shell-written entry in the fleet says `user:edwin` whether or not that is true.

## What would close this

- [ ] The shell sends the author it actually knows — the signed-in user for a human click, and the agent's own identity when a session is driving the page.
- [ ] A decision on what an agent-driven walk is worth against the acceptance gate. That is Edwin's, not the tool's.
- [ ] Existing entries are left alone. A backfill would be inventing history.
