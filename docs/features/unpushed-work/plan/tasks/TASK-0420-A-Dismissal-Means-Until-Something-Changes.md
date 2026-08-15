---
type: "[[task]]"
id: TASK-0420
aliases: ["TASK-0420"]
title: "A dismissal means until something changes — the ✕ holds against the project's whole state, releases when the user opens it, and survives a restart"
status: done
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["Edwin 2026-08-13: 'we need to honour the x button, which means the card will not be displayed until an actual state changes in that project or the user selects the project, this should be preserved across aplication start-ups.'"]
parent: "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
effort: M
depends: ["[[TASK-0419-Every-Card-Is-A-Full-Card]]"]
blocks: []
related: ["[[FEAT-0030]]", "[[ISS-0110]]"]
tests: []
---

# A dismissal means until something changes

## What it means today, and why that is not enough

Dismissal is keyed on **one field**, and which field depends on the card: an agent alert keys on the state timestamp, so a new transition mints a fresh key and the card returns; publication keys on the commit count, so a ninth commit brings it back. Both are right about their own fact and blind to every other one — a card dismissed for its agent state stays dismissed while the project's owed count doubles.

It also expires on a clock: `loadDismissedAlerts` drops anything older than 24 hours, so a dismissal quietly becomes undone by time rather than by anything happening.

## What it must mean

**The card is hidden until the project's state actually changes, or until the user selects that project — and nothing else brings it back.**

- **The whole state, not one field.** Dismissal keys on a fingerprint of everything the card displays: agent state and its timestamp, the owed count, the transition count, the unpublished count and its remote kind. Any of them moving is *something changing in that project*, which is precisely Edwin's phrasing, and a fingerprint is the only key that keeps that promise as the card grows another line.
- **Selecting the project clears it.** Opening a workspace is a stronger signal than any card: you are looking at it.
- **No clock.** The 24-hour prune goes. A dismissal ends because something happened, not because a day passed — the whole point of "until an actual state changes".
- **Across restarts.** Already persisted in `localStorage`; what changes is that it stops being quietly expired.

## Definition of Done

- [x] Dismissal is keyed on a fingerprint of the card's whole content, built in one place so a new line on the card cannot forget to join it. — evidence: `attentionFingerprint()` is the single builder, sited beside the entry it fingerprints; [[TASK-0421]] added the publication `unknown` case to it by editing that one function
- [x] Any change to that fingerprint brings the card back; nothing else does. — evidence: the store key IS `${wsId}::${fingerprint}`, so a changed fingerprint cannot match a stored key; and there is no clock anywhere in the path
- [x] Opening a workspace clears its dismissals. — evidence: `clearDismissalsFor(id)` is called from `openWorkspace`
- [x] The 24-hour expiry is gone, and the store is bounded some other way — dead keys are those whose workspace is no longer discovered, and those a newer fingerprint has replaced. — evidence: `a vanished workspace is still pruned once the fleet IS known` and `a superseded fingerprint is pruned while its workspace lives`, in `desktop/tests/attention-dismissal.test.mjs`
- [x] A dismissal survives quitting and relaunching the app, asserted rather than assumed. — **this box is why [[FEAT-0100]] came out of `done`.** It was unticked, no test existed, and the shipped behaviour was the opposite: `pruneDismissedAlerts` ran from a module-level `refreshAttention()` before discovery, so `workspaces` was `[]`, every restored key failed the liveness test, and the store was read back and wiped on the same tick. Evidence now: `a dismissal is not wiped before the fleet is discovered`, executing the real compiled function out of `desktop/dist/renderer/renderer.js`
- [x] The dismissed state is per workspace, and dismissing one card never hides another's. — evidence: the key is namespaced `${wsId}::…` and `clearDismissalsFor` matches on that prefix; `a live dismissal on a live workspace is kept` exercises a two-workspace store

## Steps

- [x] Build the fingerprint where the entry is built, so it cannot drift from what is rendered.
- [x] Replace the ts/count keys with it; keep the store's shape so existing entries expire harmlessly.
- [x] Clear on `openWorkspace`.
- [x] Replace the age prune with a liveness prune. — and the liveness prune's own defect (running before discovery) is the one this task shipped with; see the DoD box above.
