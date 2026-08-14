---
type: "[[change]]"
id: CHG-20260814-A-Push-Refreshes-What-It-Published
title: "A push repaints the surface it was clicked on, and declines the ten-second publication cache first"
status: merged
owner: user:edwin
created: 2026-08-14
updated: 2026-08-14
source: ["Edwin 2026-08-14, using the app: 'I used the push button and this kinda worked but it does not removed the # commit not pushed section from the page and the push button says pushed. It is currently visible on the screen'"]
commit: ""
pr: ""
impacts: ["`GET /api/cockpit/history` accepts `fresh=1`, which reads publication state uncached", "`cockpit.history_payload()` gained a `fresh: bool = False` keyword", "after a successful push the overview's History block, the History page and the obligation badges repaint without a reload", "no new route, no new write path — REQ-0027's guard set is unchanged"]
issues: ["[[ISS-0168-A-Successful-Push-Leaves-Every-Surface-Saying-It-Is-Unpublished]]"]
features: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"]
related: ["[[TASK-0418-The-Push-Lives-With-The-Commits]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ISS-0165-The-Attention-Card-Reads-A-Second-Git-Walk]]", "[[CHG-20260814-One-Walk-For-Publication]]"]
---

# A push refreshes what it published

## Summary

The push worked and the screen did not move. `git status -sb` read `0 0` against the upstream while the overview still showed `N commits not pushed`, each commit below it still marked unpublished, and the button inside that block said **Pushed** — two elements on one screen disagreeing about one fact.

## Two causes

**`runPush` refreshed the wrong surface.** Its success path called `cockpitApi.fleetHealth.recheck()`, which lands in `applyFleetHealthPayload` and repaints the workspace squares and the attention cards. The block the button lives inside is `buildPublicationBlock`, drawn by `fillHistory` from `/api/cockpit/history`, and nothing re-ran it. `refreshOverviewInPlace()` already existed and was never called.

[[TASK-0418]] made the push control **one builder for three surfaces** so they could not drift in what they *offer*. What it did not unify is what happens **after** — so the refresh stayed pointed at whichever surface the first implementation happened to live on.

**The sidecar would have answered stale anyway.** `git_state.read()` caches per repo for `CACHE_SECONDS = 10.0`, and `git push` runs in the **Electron main process** (`ipc/git.ts`) — the sidecar has no event telling it the cached answer just became false. A renderer-only fix would have been right on a slow click and wrong on a fast one.

## What changed

`GET /api/cockpit/history` accepts **`fresh=1`**, routing the publication read through `git_state.read_fresh` instead of `read`. A GET declining a cache is an ordinary GET: nothing is written, no route was added, and [[REQ-0027]]'s loopback set is untouched.

`refreshPublicationSurfaces(workspaceId)` runs after a successful push and does three things in order:

1. one `history?limit=1&fresh=1` call whose payload is **discarded on purpose** — `read_fresh` re-stamps the shared in-process cache, so this single walk makes History *and* the badges correct rather than giving each surface its own git walk, which is the duplication [[ISS-0165]] spent a day removing;
2. repaints whichever block is on screen — `refreshOverviewInPlace()` no-ops off the overview, and the History page is re-rendered at its current scroll;
3. `refreshObligationBadges()`.

It is **guarded on `activeId`**, and that guard is the point rather than a detail: the fleet screen pushes *other* repos, so repainting the open workspace because a different one was published is the same bug pointing the other way — and it would have looked like a fix in every manual test done on the workspace you happen to have open.

## The button still says "Pushed"

Kept. It is true and local to the control, and the refresh replaces it along with the block that contains it. The defect was never the label — it was that the label was the only thing that moved.

## Verification

Walked against a real sidecar on a throwaway repo with a local bare remote, driving the real `runPush` path on the built bundle: `1 commit not pushed` → click → the block, the unpublished marks and the badge all clear, with no reload. Deliberately **not** walked by pushing this repository: publishing is the user's act, and the mechanism does not need a real publication to be proven.

Four guards, each mutation-tested — removing the refresh, dropping `fresh=1`, moving the invalidation after the repaint, and dropping the `activeId` scope all fail. The server half is proven end to end in `test_history_can_decline_the_publication_cache`, which pushes to a real bare repo behind the server's back and asserts the cached reading is still wrong before `fresh=True` corrects it. That test also fails if `CACHE_SECONDS` ever stops mattering, which is the condition under which this flag should be reconsidered rather than kept out of habit.
