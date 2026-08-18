---
type: "[[task]]"
id: TASK-0525
aliases: ["TASK-0525"]
title: "Restore the `ISS-*` link on the 73 Tier 2 checks that lost it"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0131-The-Suite-Is-Refined]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Restore the `ISS-*` link on the 73 Tier 2 checks that lost it

TESTING.md already requires it — each Tier 2 test *"references the \`ISS-*\` that created it"*. Measured 2026-08-18: **85 of 158 do**, so 73 have lost the one field that says why they exist.

This is what makes Tier 2 groupable by issue rather than by 46 one-off scenario names, and it is the prerequisite for [[TASK-0526]] — a check cannot rest with its issue if it does not name one.

**Per check, from the note's own text.** A Tier 2 check whose issue cannot be identified is a finding, not a blank to fill: it may be the evidence that the check should be retired ([[TASK-0518]]).
