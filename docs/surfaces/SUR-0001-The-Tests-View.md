---
type: "[[surface]]"
id: SUR-0001
aliases: ["SUR-0001"]
title: "The tests view — the suite as sections, and what a person still owes"
status: active
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
kind: screen
platforms: []
parent: ""
related: ["[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[ISS-0242-Two-Different-Things-Are-Both-Called-Automated-Tests]]", "[[ISS-0243-The-Automated-Checks-Page-Is-A-Walk-Page]]"]
tags: [surface]
---

# The tests view

## What it is

The left pane's Tests mode and the generated checks page behind it. A person opens it to answer one question — *what do I still have to do* — and leaves having walked a check or having decided not to.

It is the first `SUR-*` because it is the surface this phase spent itself on: four of PHASE-037's issues are about what its section heads say, and every one of them was a sentence retyped rather than derived.

## Boundaries

**Not the release page.** That answers *can I ship*, over the same checks, and the two were confused often enough that [[ADR-0035]] exists. A check's steps live here; a release reports and records nothing.

**Not the obligations badge.** *What needs a person right now* is [[ADR-0027]]'s question and has its own registry — this view shows the suite whether or not anybody is being asked.

## Coverage

Derived from `area:`. Nothing is listed here on purpose: a second, hand-maintained copy of a relationship is what [[ADR-0032]] spent a decision removing, and this note exists precisely so the name is written once.
