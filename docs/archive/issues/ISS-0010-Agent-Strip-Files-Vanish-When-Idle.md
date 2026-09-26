---
type: "[[issue]]"
id: ISS-0010
aliases: ["ISS-0010"]
title: "Agent strip (and its files view) vanishes the moment a session ends — regression from the ISS-0009 strip-hide"
status: fixed
severity: medium
component: renderer-chrome
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
parent: "[[FEAT-0020-Agent-Activity-Surfaces]]"
related: ["[[ISS-0009-Popovers-Never-Hide]]", "[[FEAT-0030-Agent-Inbox]]"]
---

# ISS-0010 — agent strip files view vanishes when idle

## Problem

User report 2026-07-19: the "updated files" functionality in the agent strip above the console disappeared. Cause: before ISS-0009, `.agent-strip` set `display:flex` with no `[hidden]` rule, so the strip stayed painted permanently (the CSS bug). The ISS-0009 sweep added `.agent-strip[hidden]{display:none}`, which is correct in isolation — but `showAgentStrip()` sets `agentStrip.hidden = true` as soon as the session is no longer `live`, so the strip (and its expandable files-touched detail) now vanishes the instant a session ends. The reviewer had flagged the always-on strip as a bug; it was in fact behaviour the user relied on to keep seeing what the agent last did here.

## Fix

The strip now persists the most-recent session between runs instead of only showing a live one. The tracker snapshot (`/api/cockpit/state`) gains `last_session` = the newest session when none is live (slim, `live:false`, files included). `showAgentStrip()` renders `session ?? last_session`: a live session behaves as before; an ended one shows muted with a "last session — …" label (`.agent-strip.is-ended`) and its files stay expandable. The strip hides only when a workspace has never run a session (and nothing is queued) — so the empty-band noise ISS-0009 targeted stays gone. Verified end-to-end over CDP: during a session the strip shows `working — Edit · widget.py` with the file listed; after `SessionEnd` it stays visible as `last session — refactor the widget` with `widget.py` still in the detail.
