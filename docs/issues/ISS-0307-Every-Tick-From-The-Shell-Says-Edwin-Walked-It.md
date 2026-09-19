---
type: "[[issue]]"
id: ISS-0307
aliases: ["ISS-0307"]
title: "Every check marked from the cockpit is recorded as walked by Edwin, even when an agent drove the page, so the record cannot say who checked it"
status: open
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-14
updated: "2026-09-19"
reported_by: review
source: ["Independent review of [[FEAT-0150-The-Walk-Page-Reads-As-A-Script]], 2026-09-14, finding 11"]
severity: medium
component: ledger
parent: ""
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[FEAT-0149-The-Walk-Page]]", "[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]"]
tests: []
tags: [issue, ledger, acceptance]
---

# Every check marked from the cockpit is recorded as walked by Edwin

Whoever marks a check in the cockpit, the record says `by: user:edwin`, so a reader of the ledger cannot tell a check Edwin walked from one an agent clicked through.

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

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** The history shown against a check lists Edwin as the walker for every entry written from the cockpit, including walks an agent drove. Anyone asking "did a person look at this?" gets a confident wrong answer.

Evidence: `postCheckVerdict` at `desktop/src/renderer/renderer.ts:9641` sends `by: 'user:edwin', method: 'manual'` (line 9663) on every write; the walk page's local copy of the event does the same at line 12927, and the ledger-seal call at line 8688. The server copies whatever it is sent (`server.py:2641`, `:3012`). Other writes from the shell also hard-code `actor: 'user:edwin'` or `reviewer: 'user:edwin'` (lines 2075, 2252, 7171-7441, 7960, 8113, 8487).

Bigger: the shell has no way today to know whether a person or an agent session is driving it, so a fix needs a source for that identity before the constant can go. Whether an agent-driven walk counts toward the acceptance gate is a separate decision for Edwin.

**Belongs to:** no open feature (the walk page, FEAT-0149 and FEAT-0150, is done). **Next:** decide where the shell learns who is acting, then replace the constant in `postCheckVerdict` first.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
