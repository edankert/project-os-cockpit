---
type: "[[issue]]"
id: ISS-0041
aliases: ["ISS-0041"]
title: "A design with no artifact is unreadable inside the cockpit"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28: 'DES-0002 cannot be opened as a text file'"]
related: ["[[FEAT-0042-Design-Bench]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
fixed_by: []
---

# The design system was the one thing you could not read

Edwin, while deciding what a style-guide page should cover: *"I am not sure what the note describes since I cannot open it in the tool."*

## What happened

DES-0002 declares `asset: ""` — deliberately, because its own body says the living style-guide page does not exist yet. Selecting it in Design mode routes to `~design/DES-0002`, which renders "DES-0002 declares no artifact yet — nothing to render" and stops.

The note banner points from a design **note** to the bench. Nothing pointed back. So the design system — a note whose entire content is prose, and the reference every other design is supposed to conform to — was readable only outside the application built to display it.

## Fix

Two doors, because one was what caused this:

1. The empty stage offers **"Read DES-0002 as a note"**.
2. The id chip in every design header is a link to the note, artifact or not — keyboard-reachable, since it is a styled span rather than an anchor.

## The pattern, for the fourth time

This is the fourth reachability defect on this surface in two days: nothing linked to the bench; `extractRel` discarded `~design/...`; the identity band's link 404'd; and now a design that renders nothing offers nowhere to go. Each passed its tests. Each was found by Edwin opening the app.

The common shape is not "a missing link" — it is **a surface that answers one question well and treats every other state as an absence.** A stage with no artifact is a state, not an error, and a state needs somewhere to go.
