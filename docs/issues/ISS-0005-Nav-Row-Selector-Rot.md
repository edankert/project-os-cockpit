---
type: "[[issue]]"
id: ISS-0005
aliases: ["ISS-0005"]
title: "Row context menu + agent-touch trail never fired — selector matched a class the <li> doesn't carry"
status: fixed
severity: medium
component: renderer-nav
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0020-Agent-Activity-Surfaces]]"
related: ["[[TASK-0120]]", "[[TASK-0132]]"]
---

# ISS-0005 — nav row selector rot

## Problem

Right-clicking cards in the left nav and right context pane did nothing (user report 2026-07-06). Cause: the handlers select `li.nav-item[data-rel]`, but the `nav-item` class sits on the inner card `div` in all four item renderers — the `<li>` only carries the data attributes. The selector never matched, so the row context menu (FEAT-0012-era, extended with Agent verbs in TASK-0132) and the agent-touch flash trail (TASK-0120) were both silently dead.

## Fix

Selectors changed to `li[data-rel]` in the shared row context-menu handler and `flashAgentTouch`; the `.agent-touched` CSS rule follows. Verified by build; interactive check rides on TST-0011 (steps 4 and 10 exercise exactly these paths).
