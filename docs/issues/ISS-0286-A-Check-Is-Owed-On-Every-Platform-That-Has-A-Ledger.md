---
type: "[[issue]]"
id: ISS-0286
aliases: ["ISS-0286"]
title: "A check is owed on every platform that has a ledger, with no way to say where it applies — one application built from one codebase has to answer for its whole suite once per operating system, or mark each check `na` by hand"
status: triage
phase: ""
owner: user:edwin
created: 2026-09-06
updated: 2026-09-06
source: ["Edwin, 2026-09-06, on project-os-deck's ledger: 'do we have different applications or not for different os's. If we don't then I think we should not replicate the acceptance tests for all oss, instead we should have a place to capture the acceptance tests and have os specific kick the tire tests.'"]
severity: medium
component: server
parent: ""
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[REQ-0054]]", "[[ISS-0285-The-Mark-Dialog-Offers-Verdicts-The-Write-Path-Refuses]]", "[[project-os-deck#PHASE-0001]]"]
tests: []
---

# A check is owed on every platform that has a ledger

## Problem

**A verdict's arity is right and its default is wrong for a portable application.** `ledger.resolve` says so in its own words:

> A check with no surviving verdict simply has no key, and *that absence is the answer*: no entry for a platform means owed on that platform, with no field anywhere declaring applicability ([[REQ-0054]]).

That default was decided on `your-trainer`, where Android and iOS are separately built, separately shipped applications and a pass on one is genuinely no evidence about the other. It does not hold for an application with one codebase.

## The case that breaks it

`project-os-deck` is one Electron application: one renderer, one main process, one build. Its six acceptance walks include *Spread lists the same notes as the cockpit* and *an address copied out and pasted back restores the same state*. Those are facts about Deck. Walking them again on Windows would tell nobody anything.

Under the current default, the day that repository gains a second ledger, all six read as owed there, and the only way to say otherwise is to record `na` on each one, per platform, by hand. Nobody will, so the gate reads as blocking and stops being read.

## What is genuinely per-operating-system

Edwin's framing, and it is a good one: **one place for the acceptance suite, and small kick-the-tires checks per operating system.** For Deck those would be that it launches, that a window lands on the display it was left on with that system's arrangement, that the sidecar interpreter is found, and that the host binds. A handful, not a suite.

## Why a workaround is not enough

`project-os-deck` names its ledger `WORKING-app.json`, so the platform names the surface a verdict was earned on rather than the operating system it was typed on. That holds only while it has exactly one ledger. The moment a real per-operating-system check needs its own, the suite is owed there too — the same trap, arrived at from the other side.

## What a fix has to decide

- Can a check say where it applies, and is that a field on the note or a property of the suite? [[REQ-0054]] said no field, and this is the evidence for revisiting it rather than a bug against it.
- Or does the gate compute what is owed from something other than the presence of a ledger.
- Either way `na` stays: it says *this surface exists and the check cannot run here*, which is different from *this check was never about that surface*.
