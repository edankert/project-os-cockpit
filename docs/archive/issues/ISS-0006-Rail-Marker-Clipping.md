---
type: "[[issue]]"
id: ISS-0006
aliases: ["ISS-0006"]
title: "Rail agent-state dot clipped by ws-square overflow; active bar never visible; busy/done greens indistinguishable"
status: fixed
severity: medium
component: renderer-rail
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-18
updated: 2026-07-18
parent: "[[FEAT-0020-Agent-Activity-Surfaces]]"
related: ["[[TASK-0100]]", "[[TASK-0120]]"]
---

# ISS-0006 — rail agent-state marker clipping

## Problem

The agent-state dot overlaying each workspace square in the mini-rail renders as a truncated wedge (user report 2026-07-18). `.ws-square` carries `overflow: hidden` (needed to round project icons), while `.ws-dot` sits at `bottom/right: −2px` with a 2px content-box border — the part of the dot outside the rounded corner is clipped. Two more defects share the root cause: the active-workspace accent bar (`.ws-square.active::before` at `left: −8px`) is fully clipped and has never been visible, and the dot's `--bg-elevated` border — meant to fake a punched-out notch against the rail — lands on top of icon artwork where it reads as a stray halo. Separately, busy (`--status-active`, hsl 140) and done (`--status-done`, hsl 160) are indistinguishable greens at 10px.

## Fix (chosen from mockup review, option A + ring hybrid)

Move clipping off the square onto the icon: drop `overflow: hidden` from `.ws-square`, give `img.ws-icon` `border-radius: inherit`. The dot becomes a 10px circle at `bottom/right: −3px` with a `box-shadow` ring in `--bg-elevated` that punches a clean notch against the rail on both letter tiles and icon artwork. The revived active bar moves to `left: −6px` so it hugs the rail edge inside the list's clip. State colors: busy switches to `--accent` (agent actively driving), done stays green, waiting amber pulse, idle faint, error critical; `needs-input` keeps the fast dot pulse and additionally gets a pulsing red ring around the whole square — urgency alone earns the loud treatment. Verified visually in the running app; CSS-only, no DOM or payload changes.
