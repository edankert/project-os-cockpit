---
type: "[[task]]"
id: TASK
aliases: ["TASK"]
title: "`Verified` requires a positive test; an unrecognised status gets a visible group"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0127-Every-Row-In-The-Tests-View-Is-A-Test]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# `Verified` requires a positive test; an unrecognised status gets a visible group

`_tests_groups` ends in `else: verified`, so `retired` — and any future status — reads as a pass. Invert: `verified` is entered by naming the statuses that mean it, and the fallback becomes a visible group.

Guarded on the fallback, not on the three ids `your-trainer` happens to hold (REQ-0046 criterion 4).
