---
type: "[[issue]]"
id: ISS-0009
aliases: ["ISS-0009"]
title: "Inbox and queue popovers never visually close — CSS display:flex overrides the hidden attribute"
status: fixed
severity: medium
component: renderer-chrome
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
parent: "[[FEAT-0020-Agent-Activity-Surfaces]]"
related: ["[[FEAT-0030-Agent-Inbox]]"]
---

# ISS-0009 — popovers never hide

## Problem

User report 2026-07-19: clicking an inbox bell row navigates to the workspace but the popover stays on screen. Root cause: `.inbox-popover` (and `.queue-popover`) set `display: flex`, and an author `display` declaration beats the UA stylesheet's `[hidden] { display: none }` — so `closeInbox()` sets the `hidden` attribute correctly but the element keeps rendering. Every close path was affected (row click, outside click, bell re-click). Other popovers in the codebase already carry explicit `.x[hidden] { display: none !important }` rules; these two were missing theirs.

## Fix

Independent review widened the sweep: the same defect also silently affected `#agent-strip` (`display: flex` — the strip never collapsed when no session/queue existed, leaving a permanent 26px band) and `#top-bar-inbox` (`.top-bar-btn` `inline-flex` — the bell never hid when the inbox was empty). One rule now covers all of them plus a defensive entry for the settings popover (which hides only because it declares no display): `.inbox-popover[hidden], .queue-popover[hidden], .settings-popover[hidden], .agent-strip[hidden], .top-bar-btn[hidden] { display: none !important; }`. Verified by rebuild + relaunch: popover closes on row click/outside click/bell toggle; strip and bell collapse when empty.
