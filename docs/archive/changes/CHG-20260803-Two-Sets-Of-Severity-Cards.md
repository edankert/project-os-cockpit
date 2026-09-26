---
type: "[[change]]"
id: CHG-20260803-Two-Sets-Of-Severity-Cards
title: "Severity cards split into open and completed sets, phases lose the rules between them, and the completed band becomes a card"
status: merged
reviewed_by: model:claude-opus-5
review_date: 2026-08-03
review_verdict: approved
date: 2026-08-03
owner: user:edwin
component: [server, static, desktop-renderer]
related: ["[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[ISS-0092-Severity-Buckets-Straddled-The-Completed-Split]]"]
---

# Two sets of severity cards

## What changed

**Issues** now render two sets of severity cards — `Open · 3` above the divider, `Completed · 4` below. A severity holding both open and fixed issues appears in **both**, with only its open items in the first card and only its fixed ones in the second.

That was a real bug, not just layout: buckets were keyed on severity alone, so the live/completed split had to place each bucket whole. One open medium issue would have kept fifty-six fixed ones above the divider under a card headed `Medium · 57`. It is invisible in this corpus because every issue is fixed.

**Features** lose the hairlines between phases — the rows are separated by being rows — and the completed section gains a card frame, matching the overview's and the right pane's.

## The rule that replaced two

The band used to be deliberately frameless, so that a card containing cards would not nest two identical borders. That held where its children are framed (tasks, issues) and failed in the features view, where the phases inside are *things* and carry no frame — leaving the completed section reading as whatever was left at the bottom.

**One border per object.** The band has it; its children do not.

## Paths

- `src/project_os_cockpit/cockpit.py` — `_severity_cards`, splitting on completion before severity
- both stylesheets — the band's frame, its children's absence of one, and the removed rules

## Restart required

Mode 3 is a built bundle, and the issue grouping is served by the per-workspace Python sidecar — both pick the change up when the app restarts.
