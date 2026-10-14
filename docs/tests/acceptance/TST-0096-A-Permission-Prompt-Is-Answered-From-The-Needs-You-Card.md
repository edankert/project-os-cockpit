---
type: "[[test]]"
id: TST-0096
aliases: ["TST-0096"]
title: "A Claude permission prompt is answered from the Needs you card, falls back to the terminal after the wait, and a deny is never widened"
status: active
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"]
scope: feature
level: acceptance
entrypoint: "The Needs you card, with a new cockpit terminal running `claude`"
command: ""
last_verified: ""
covers: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"]
issues: []
tasks: ["[[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]", "[[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]", "[[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]"]
artifacts: []
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
review_round: ""
related: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]", "[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]]"]
area: ""
after: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"]
tags: [test, acceptance, cockpit-plugin, approvals, claude-code, security]
---

# A permission prompt is answered from the Needs you card

## Purpose

Proves that a person can answer a Claude Code permission prompt with the cockpit's Approve and Deny buttons, that the terminal gets the prompt as today when nobody clicks within the wait, that a refusal from the person's own hook is never turned into a permission, and that a request made outside the cockpit window cannot answer.

Set to `active` on 2026-10-14, when the feature started. All four tasks were built the same day; this walk is the first time it runs in the application.

## Setup

The desktop application rebuilt from these sources (`npm run build` in `desktop/`) and restarted. A project whose cockpit terminal is new, so it loads the plugin. The project's Claude permission settings leave `Bash` commands to ask (the default). **Claude in manual mode**: press Shift+Tab until the footer says "manual mode on". In auto mode the classifier answers, and the cockpit is deliberately not asked (TASK-0665's live run). For step 7, a PreToolUse hook in that project's `.claude/settings.local.json` that denies any Bash command containing `cockpit-deny-me`; remove it after the check.

## Steps

1. In the project's terminal run `claude`. Ask it to run `ls -la` with Bash. Watch the Needs you list.
2. Press Approve on the card.
3. Ask it to run `echo hello` with Bash. Press Deny on the card.
4. Ask it to run `date` with Bash, and do not touch the cockpit. Watch the terminal for ten seconds, then look at the card.
5. Press Approve on that card anyway. Then choose Yes in the terminal.
6. Ask it to run a Bash command longer than one line, for example a `for` loop over ten file names with `echo` in the body. Read the card before answering.
7. Add the deny hook from Setup. Ask Claude to run `echo cockpit-deny-me`. Watch the Needs you list.
8. In a plain terminal, find the sidecar's port (`cat .cockpit/url` in the project). Ask Claude to run another command, and while its card is showing, run `curl -s -X POST -H 'Content-Type: application/json' -d '{"approval_id":"<the id from GET /api/cockpit/approvals>","decision":"granted","actor":"user:edwin"}' <url>/api/cockpit/approve`.
9. In the same plain terminal, run `~/Dev/repos/project-os-cockpit/.venv/bin/cockpit dispatch <a note ID>` while `claude` is idle in the cockpit terminal.

## Expect

- In step 1 a card appears within a second, naming the project, Claude, `Bash` and the full command `ls -la`, with Approve and Deny. The terminal shows no permission dialog while the card is up.
- In step 2 the card leaves the list, the status line says "Approved Bash", and Claude runs `ls -la` without asking in the terminal.
- In step 3 Claude does not run the command and reports that it was denied in the cockpit by you.
- In step 4 the terminal's own permission dialog appears about 5 seconds after Claude asked. The card stays, without buttons, and says "Answer in the terminal: the cockpit's 5 s wait ran out".
- In step 5 the cockpit says the same sentence and nothing changes in the terminal. Answering in the terminal works as it always has, and the card leaves the list when the command has run. (A prompt refused in the terminal with No or Esc leaves its card until your next message to Claude, because Claude Code reports nothing on a refusal.)
- In step 6 the card shows every line of the command. Nothing is cut off.
- In step 7 no card appears, and Claude reports that a hook blocked the command. The command never runs.
- In step 8 `curl` gets 403 and the card is still there, waiting. The request did not answer it.
- In step 9 the prompt arrives in Claude as in TST-0095 step 8. `cockpit dispatch` still works without the secret.

## First run on 2026-10-14: steps 1, 2 and 4 pass; the rest not yet run

Edwin rebuilt the application at 21:33 local and restarted it at 21:34, after the last FEAT-0159 commit (21:31). The app ran without a debugging port. Every sidecar reported `sidecar_stale: false`. The walk ran in this repository's own cockpit terminal, in the Claude session that was guiding it (`3c410600`), not in deck as Setup suggests. The records are in `.cockpit/approvals.json` in this repository.

- The session was first in bypass permissions mode, and then in plan mode. In both, commands ran without a card and without any approval record, which is the intended behaviour outside manual and acceptEdits mode. `ls -la` was never tried in manual mode, so whether it asks there is still unknown. The probes used `touch /tmp/tst-0096-*.txt` instead, which does ask.
- Steps 1 and 2 pass. In manual mode, eleven calls (Bash, Write and Edit) were approved from the card by `user:edwin`, each 1 to 4 s after its offer, for example approval `302e609311bc` at 20:46:16 to 20:46:17 UTC. None of them showed a terminal dialog. Edwin: "It all works".
- Step 4 passes, three times. `touch /tmp/tst-0096-2.txt` was offered at 20:46:01, handed to the terminal at 20:46:06, answered there, and closed at 20:46:13. The same happened at 20:50:16 to 20:50:28 and at 20:54:45 to 20:55.
- Step 3 has not run. Both attempts to Deny ended without a deny: `touch /tmp/tst-0096-3.txt` was granted (approval `6488c88d8a71`, 20:46:35), and `tst-0096-3c` ran out the 5 s wait.
- On the first sight of the card, Edwin did not like the full-width buttons or the bordered box. [[TASK-0670-A-Permission-Prompt-Sits-In-The-Needs-You-List-Like-Its-Other-Rows]] made it a plain row with "Approve · Deny" on the session line. Edwin saw it after a window reload and approved it ("I have seen it, all good for now!"). Approve on the new row works (approval `f97dfde3bdd1`, 20:54:57 to 20:54:59).
- Not yet run: steps 3, 5, 6, 7, 8 and 9. The step 7 deny hook was put in `project-os-deck/.claude/settings.local.json` for this run and removed when the walk paused, so it has to be added again before step 7.

## Not this check

The tests in [[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]] cover the cases that are hard to walk by hand: every wrong form of the secret, an agent actor, and the secret not appearing in any file or environment. This check is what a person sees.
