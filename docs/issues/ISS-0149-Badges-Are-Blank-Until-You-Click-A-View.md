---
type: "[[issue]]"
id: ISS-0149
aliases: ["ISS-0149"]
title: "The obligation badges are blank on a freshly launched window — the sidecar-ready path refreshes seven surfaces and not that one, so nothing is owed until you click a view button"
status: fixed
severity: medium
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
phase: "[[PHASE-030-Obligations-Go-Home]]"
features: ["[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0092]]"]
tasks: []
related: ["[[ISS-0040]]"]
tags: [issue, renderer, startup]
---

# Badges are blank until you click a view

## What was found

Restarting the app for Edwin on 2026-08-12 and checking what he would see: the window came up on the overview, on the current bundle, with all ten workspaces — and **every view button bare**. The sidecar was serving `{intent: 5, features: 1, issues: 9}` at the same moment.

`refreshObligationBadges` is called from exactly three places: `setNavMode`, and two write handlers. Its first line is `if (!sidecarBaseUrl) return;`.

**On a fresh window the mode is restored from `localStorage` before any sidecar exists**, so that call returns silently and there is nothing to retry it. The sidecar-`ready` handler then refreshes seven surfaces — nav, inbox, agent snapshot, agent actions, agent registry, queue, dispatches — and not this one.

So the badges appear on the *first mode click* and look correct forever after, which is why this survived: nobody launches the app and then does nothing.

## Why it matters more since yesterday

[[FEAT-0092]] made the badge the way into each view's landing page. A blank badge is now not just a missing count — it is the entry point to the surface that lists what a person owes, absent at exactly the moment they open the app to find out.

It is also the failure this whole area is about, one layer down: **a surface saying nothing where it should say something**, and saying it convincingly.

## The fix

`void refreshObligationBadges();` in the sidecar-`ready` handler, beside the seven that were already there.

## What the tests hold

`test_the_ready_path_refreshes_the_badges` reads the `case 'ready'` block and requires the call. That block already carries [[ISS-0040]]'s guard for the same class of bug — a surface the ready path forgot — which is the argument for asserting membership of it rather than trusting a reviewer to notice the eighth omission.
