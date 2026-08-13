---
type: "[[issue]]"
id: ISS-0162
aliases: ["ISS-0162"]
title: "45 bare `[[ADR-0011]]`-style citations still resolve to nothing, and no standing document says where that namespace lives"
status: "open"
owner: user:edwin
created: 2026-08-13
updated: "2026-08-13"
source: ["The one part of [[ISS-0148]] its own text called 'cheaper than both' and which the syntax did not deliver"]
severity: low
component: docs-namespace
parent: ""
related: ["[[ISS-0148-A-Cross-Repo-Reference-Has-No-Syntax]]", "[[ADR-0024]]", "[[FEAT-0093]]"]
tests: []
---

# The bare upstream citations still resolve to nothing

## Problem

[[ADR-0024]] gave the fleet `[[project#ID]]` and [[FEAT-0093]] made the cockpit follow it. Neither back-fills what was already written: **45 files here cite `ADR-0011` or `ADR-0013` as bare IDs**, and both notes live in `project-os-dev`. Every one is a dead link in the cockpit and in Obsidian.

[[ISS-0123]] was closed because those notes exist; [[ISS-0148]] was closed because the syntax exists. What neither closed is the reader arriving at `[[ADR-0011]]` and finding nothing — which is how this repo once came within an afternoon of *writing a replacement for a decision that already existed*.

## The cheap half, which is the point

`ISS-0148` named it and nobody did it: **one sentence in a standing document** saying where the upstream ADR namespace lives fixes comprehension for all 45 today, whatever else is decided. `CONTEXT.md` currently mentions `project-os-dev` zero times.

## The expensive half, which may not be worth it

Sweeping 45 files to `[[project-os-dev#ADR-0011]]`. Mechanical, and it touches notes whose `updated:` would then lie about why they changed. Worth deciding deliberately rather than doing because it is possible.

## Expected

A reader who meets a bare upstream citation can find out, from the record, where it points.
