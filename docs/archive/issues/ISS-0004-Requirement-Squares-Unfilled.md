---
type: "[[issue]]"
id: ISS-0004
aliases: ["ISS-0004"]
title: "Overview squares for fulfilled/met requirements render unfilled"
status: fixed
severity: low
component: cockpit-stats
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0017-Overview-Dashboard]]"
---

# ISS-0004 — requirement squares unfilled

## Problem

The Overview's phase/feature squares fill when an item's status bucket is "done", but `DONE_PHASE_BUCKET` in `stats_payload` lacked the requirement-specific done vocabulary — `fulfilled` and `met` (which the hero counters' `DONE_REQ` set already recognised). Requirements with those statuses rendered as outlined (open) squares.

## Fix

Added `fulfilled` and `met` to `DONE_PHASE_BUCKET` in `src/project_os_cockpit/cockpit.py`. Full suite green (186).
