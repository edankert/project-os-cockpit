---
type: "[[test]]"
id: TST-0093
aliases: ["TST-0093"]
title: "The draft window lists owed work, a phase's state and the AIs"
status: active
phase: "[[PHASE-045-The-Cockpit-In-Layers]]"
owner: user:edwin
created: 2026-10-13
updated: 2026-10-13
source: ["[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"]
scope: feature
level: acceptance
entrypoint: "File, Home (draft), or Shift-Command-H"
command: ""
last_verified: ""
covers: ["[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"]
issues: []
tasks: ["[[TASK-0648-Harness-Unit-Tests-And-A-Register-Row-For-The-Draft-Window]]"]
artifacts: []
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
review_round: ""
related: []
area: ""
after: []
tags: [test, acceptance, draft-window]
---

# The draft window lists owed work, a phase's state and the AIs

## Purpose

Proves that Edwin can open the draft window beside the present cockpit window, see what is owed across his projects, where one project's active phase stands and what each project's AI session is doing, and reach the place to act in the present window from any row.

The window was built on 2026-10-13 and had not been run inside the application when this check was set to `active`; this check is the first run.

## Setup

The desktop application rebuilt from these sources (`npm run build` in `desktop/`) and restarted, running on this machine's real projects, with the present window open on any project. At least one project must owe something; on 2026-09-20 the projects together owed 84 decisions, so no preparation is expected. For the third area, have an AI session running in at least one project's console.

## Steps

1. In the present window, open any note and leave it showing.
2. Choose File, Home (draft), or press Shift-Command-H.
3. Go back to the present window, open a different note and type in its console.
4. In the draft window, look at the board without hovering over anything.
5. Hover over one mark for something owed, then choose a mark in a row for a project other than the one the present window shows.
6. Hover over a phase bar's marks and dots, then choose one feature mark.
7. Click in the present window, then in another application.
8. Close the draft window.

## Expect

- After step 2 a second window opens and the present window still shows the note from step 1.
- In step 3 the present window opens the note and its console takes the typing, as it did before the draft window was open.
- Without hovering, the board shows which projects want you first, how much each owes and of what kind, and how far each active phase is. The top line gives each mark with its count and its one word.
- Every project is one row with one mark for its AI session. The project with the running session shows the working mark or the needs-your-answer mark, matching what the present window shows for it.
- Hovering over a mark names its subject. After choosing one in step 5 the present window comes to the front, switched to that project and showing that item.
- A phase bar has one mark per feature, a divider, and one dot per exit criterion. Hovering names each. After step 6 the present window shows that feature.
- In step 7 the draft window stays in front of the present window and of the other application.
- A project the draft window could not read is named as not read. No project is shown as owing nothing unless it owes nothing in the present window too.
- After step 8 the present window keeps working and the application stays open.

## Not this check

- That the board is the right picture. That is Edwin's judgement, given in words and not as a verdict here.
- That an act can be performed in the draft window. It cannot; every act is done in the present window and is covered by that page's own checks.
- Where a single feature stands. The draft answers for a phase, and shows a release in preparation as one row.
- Several AI sessions in one project, or a console in the draft window. Neither is part of [[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]].
- The correctness of the owed list itself. The draft shows what the sidecar reports; the owed rules are covered by the checks on the Needs you group in each view.
