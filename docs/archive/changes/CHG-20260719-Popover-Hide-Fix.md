---
type: "[[change]]"
id: CHG-20260719-Popover-Hide-Fix
aliases: ["CHG-20260719-Popover-Hide-Fix"]
title: "Inbox + queue popovers actually close — [hidden] display rule restored"
status: merged
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
commit: ""
pr: ""
impacts: ["inbox popover", "dispatch queue popover"]
issues: ["[[ISS-0009-Popovers-Never-Hide]]"]
features: ["[[FEAT-0020-Agent-Activity-Surfaces]]"]
reviewed_by: "model:claude-opus"
review_date: 2026-07-19
review_verdict: approved
related: []
---

# Popover hide fix (ISS-0009)

## Summary

User report: clicking an inbox bell row navigated to the workspace but the popover stayed on screen. Root cause: an author `display` declaration beats the UA stylesheet's `[hidden] { display: none }`, so elements toggled via the `hidden` attribute whose class sets a display never visually hide. The independent review found four affected elements, two beyond the report: `.inbox-popover` and `.queue-popover` (`display: flex` — no close path worked), `#agent-strip` (`display: flex` — never collapsed without a live session or queue, a permanent 26px band), and `#top-bar-inbox` (`.top-bar-btn` `inline-flex` — the bell never hid when empty). One CSS rule in `desktop/src/renderer/renderer.css` now spells out the hidden state for all four plus a defensive `.settings-popover[hidden]` (that popover hides today only because it declares no display). Platform/project menus already carried their explicit rules. Verified by rebuild + relaunch.
