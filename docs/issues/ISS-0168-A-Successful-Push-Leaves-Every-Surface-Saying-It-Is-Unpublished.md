---
type: "[[issue]]"
id: ISS-0168
aliases: ["ISS-0168"]
title: "A successful push leaves History still saying N commits not pushed, under a button that now says Pushed — the one surface that offered the action is the one nothing refreshes"
status: "fixed"
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-14
updated: "2026-08-14"
source: ["Edwin 2026-08-14, using the app: 'I used the push button and this kinda worked but it does not removed the # commit not pushed section from the page and the push button says pushed. It is currently visible on the screen'"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[TASK-0418-The-Push-Lives-With-The-Commits]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]", "[[CHG-20260814-A-Push-Refreshes-What-It-Published]]"]
tests: []
---

# A successful push leaves every surface saying it is unpublished

## What Edwin saw

The push worked — `git status -sb` reads `## main...origin/main`, `0 0` ahead/behind, so the record is right. What is wrong is the screen: the `N commits not pushed` block is still there, each commit below it still carries its unpublished mark, and the button inside that block says **Pushed**.

The button and the header it sits inside now contradict each other, on one screen, about one fact. That is worse than not updating at all: a surface that had not moved would read as "not refreshed yet", and this reads as an answer.

## Two causes, and fixing either alone leaves it broken

**1. `runPush` refreshes a different surface from the one that was clicked.**

Its whole success path is `showStatus(...)`, `btn.textContent = 'Pushed'`, and `cockpitApi.fleetHealth.recheck()`. That recheck lands in `applyFleetHealthPayload`, which repaints the workspace squares and calls `refreshAttention()` — the **fleet** surfaces. The block Edwin clicked is `buildPublicationBlock`, rendered by `fillHistory` from `/api/cockpit/history`, and **nothing re-runs `fillHistory`**. `refreshOverviewInPlace()` exists, does exactly this, and is not called.

The push control was deliberately made one builder for three surfaces ([[TASK-0418]]) so they could not drift in what they *offer*. What was not unified is what happens **after**: the reporting is shared, the refresh is not, and it refreshes whichever surface the first implementation happened to be on.

**2. The sidecar would have served the pre-push reading anyway.**

`git_state.read()` caches per repo for `CACHE_SECONDS = 10.0`, and **the push does not go through the sidecar** — `ipc/git.ts` runs `git push` in the Electron main process. So the sidecar has no way to know its cached answer just became false, and a re-fetch inside those ten seconds returns the same numbers. A renderer-only fix would have looked correct on a slow click and wrong on a fast one, which is the worst kind of green.

`git_state.read_fresh()` already exists for precisely this — *"a one-shot process … has no such storm to damp, and a cached answer there would mean a reading older than the process asking for it"* — and had no caller that could be triggered by an event rather than by a new process.

## Fix

1. `/api/cockpit/history` accepts `fresh=1`, which routes the publication read through `read_fresh` instead of `read`. A GET declining a cache is an ordinary GET; no new route, and no write path widened ([[REQ-0027]] untouched).
2. `runPush` gains one after-push step, shared by all three surfaces exactly as the control itself is: invalidate, then repaint History **and** the badges.
3. `read_fresh` re-stamps the shared `_cache`, so the badge refresh that follows is correct for free rather than needing a second probe.
4. **Only when the pushed workspace is the open one.** The fleet screen pushes *other* repos; refreshing this workspace's History because a different one was published would be a second version of the bug, pointing the other way.

## Why the button still says "Pushed"

Kept. It is true, it is local to the control, and after the refresh it is replaced along with the block that contains it. The defect was never the button's label — it was that the label was the only thing that moved.

## Evidence it is fixed

- Pushed against the live app with the overview open: the `N commits not pushed` block disappears, the commit dividers lose their unpublished marks, and the overview badge drops — without a reload.
- `test_history_can_decline_the_publication_cache` — `fresh=1` calls `read_fresh`; without it, a push made behind the server's back stays invisible for ten seconds.
- `test_a_push_refreshes_the_surface_that_offered_it` — the success path repaints History and the badges, not only fleet health.
- `test_a_push_of_another_workspace_leaves_this_ones_history_alone` — the `activeId` guard, which is the half a naive fix would miss.
