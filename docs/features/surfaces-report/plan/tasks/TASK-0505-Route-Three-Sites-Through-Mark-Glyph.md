---
type: "[[task]]"
id: TASK
aliases: ["TASK"]
title: "Render glyphs at the picker token, the canceled-row test and the gate tooltip, and guard against raw words"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0126-A-Rendered-Mark-Is-A-Check-Mark]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Render glyphs at the picker token, the canceled-row test and the gate tooltip, and guard against raw words

`renderer.ts:2341` (`[done]` → `[x]`), `renderer.ts:8524` (`=== '-'` is dead, canceled rows lost their strikethrough), `renderer.ts:4569` (tooltip).

The guard is the point: assert no surface emits a raw mark word. Two of the three sites fail silently, so a visual check would not have found them.
