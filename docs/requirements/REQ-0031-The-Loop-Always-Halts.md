---
type: "[[requirement]]"
id: REQ-0031
aliases: ["REQ-0031"]
title: "The loop always halts"
status: "approved"
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-11"
source: ["[[DES-0009-The-Standing-Worker]]"]
priority: high
scope: "The standing worker's every loop and budget"
specifies: ["[[FEAT-0074-The-Standing-Worker]]"]
acceptance:
  - "Budgets bound every loop: sessions per day, wall-clock per session; exhaustion halts and files why"
  - "Failure compounds toward stopping, never toward retrying: two failed close-outs park the item, three parked items halt the worker"
  - "The human's stop switch halts from the landing card without shell access, and a halted worker is an obligation on the desk"
  - "Every halt path exercised by drill before any repo runs unattended — brakes are tested before the hill"
---

# The loop always halts

An autonomous loop's failure mode is not doing nothing — it is doing the wrong thing repeatedly at machine speed. Every path out of the loop is cheap, loud, and proven.
