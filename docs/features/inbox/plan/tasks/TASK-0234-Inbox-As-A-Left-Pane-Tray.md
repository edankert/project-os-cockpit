---
type: "[[task]]"
id: TASK-0234
aliases: ["TASK-0234"]
title: "Move the inbox into the left pane as a tray, with previews and per-item triage"
status: done
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0045-Project-Inbox]]"]
parent: "[[FEAT-0045-Project-Inbox]]"
effort: "M"
depends: ["[[TASK-0233-Drop-And-Paste-Into-The-Inbox]]"]
blocks: []
related: ["[[ISS-0061-Screenshot-Permission-Error-Was-Unreadable]]"]
tests: []
---

# The inbox is a tray, not a section

## Why it was top-level, and why that was wrong

Edwin: *"Can you tell me why the Inbox is a top level item? Why is it not just a box on the left-pane above the llm-status panels."*

The honest answer is that a top-level nav mode was the **cheapest thing to build**. The mode machinery already existed — `NAV_MODES`, a virtual landing page, a count badge, URL-state routing — so adding `'inbox'` to one array bought a whole surface for free. That is an implementation reason wearing a design decision's clothes, and nobody would have picked it starting from the content.

The design argument runs the other way, and it is not close:

- **Every other top-level mode is a view over the durable record.** Overview, features, tasks, issues, design, review — all read `docs/`. The inbox is explicitly *not* that: it is gitignored staging, and [[LIFECYCLE]] says its success condition is being **empty**. Giving it equal billing with the committed record states the opposite of what it is.
- **A permanent slot whose ideal state is empty is a permanent slot showing nothing.** The correct steady state of that nav button is a button you never press.
- **It is per-workspace transient state** — which is exactly what the left pane already holds, one element below, in the agent attention panel. The inbox belongs next to that, not next to `docs/`.

So the tray moves to `#ws-nav`, directly above `#ws-attention`.

## The tension this creates, and how it resolves

A left-pane tray is **narrow**, and the thing most often dropped into it is a screenshot — the one item type that wants width. Resolving that by shrinking the images would trade the feature's whole point for tidiness.

Instead the pane and the stage split the job: **the pane is the tray, the stage is the viewer.** Each row carries a small thumbnail (images) or a type icon (everything else), and clicking a row opens the item full-size in the centre. That is strictly more than the top-level page offered, where an image was only ever a thumbnail and there was no way to see it properly at all.

## Per-item triage

Right-click → **Triage this item** dispatches a prompt to the configured agent naming that one file and pointing at the `inbox-triage` skill. It reuses the existing dispatch path (`dispatch.execute`), so it inherits the agent preference, the terminal, and the ledger — no second mechanism.

This is the piece that makes the tray *do* something. Until now the only per-item action was Discard, so the inbox could be emptied but not triaged, and the one workflow the convention exists for was the one thing the UI could not start.

## Definition of Done

- [x] The inbox is a box in the left pane above the agent attention panel, and the top-level Inbox mode is retired via `RETIRED_NAV_MODES` so stored state does not break — evidence: in the running app, `#ws-inbox.nextElementSibling === 'ws-attention'` and `.top-bar-btn[data-mode="inbox"]` is gone; `test_..._virtual_landing` pins the mode set at `{overview, review, design}`
- [x] Images show a real thumbnail; every other type shows an icon chosen by suffix, never a generic blank — evidence: thumbnail measured in the app at 28×22 with `naturalWidth 1301`; icons reuse the app's existing Lucide `makeSvg` builder rather than a second idiom
- [x] Clicking an item opens it full-size in the centre stage — evidence: clicked in the app, the screenshot renders at **1132×536** beside a 28×22 tray thumbnail, which is the whole argument for splitting tray from viewer
- [x] Right-click offers Triage / Open / Reveal in Finder / Discard, and Triage dispatches a prompt naming that item and the skill — evidence: `test_every_inbox_menu_action_has_a_handler`, asserted **both ways** so a dead menu entry and an unreachable handler both fail. See Result for what this was **not** verified by
- [x] "Take a screenshot" survives the move and stays one click from the tray — evidence: camera button in the tray header; the failure path it exposed became [[ISS-0061-Screenshot-Permission-Error-Was-Unreadable]]
- [x] An empty inbox reads as resolved — evidence: *"Empty — nothing to triage."*, seen in the app on a workspace with an empty inbox
- [x] Verified in the running Electron app, not in a harness — evidence: every row above measured over CDP against the shipped build

## Amended: the header stays when the inbox is empty

The DoD originally said the box should *"not consume left-pane height when there is nothing in it"*, mirroring the attention panel. Building it, that turned out to be wrong: the header is one row, and hiding it hides the **screenshot button** — the one affordance that tells you the tray exists and the only way to start a capture. A surface you can only find once it already has something in it cannot be where you put things.

So the header persists whenever a workspace is open, and only the list is conditional. The original objection — a permanent slot whose ideal state is empty — was about a **top-level tab**, and one line at the foot of a pane that carries an action is not the same cost.

## Result

**The thumbnails had never worked, including the ones I reported working.** Verifying this task caught it: `img-src 'self' data:` in the renderer CSP did not include the sidecar origin, though `connect-src` and `frame-src` both did. A blocked image is just an image that never paints — no error, no console entry.

The reason it survived TASK-0233 is exact and worth keeping: `fetch()` of the same URL returned **200, `image/png`, 151296 bytes**. The bytes were reachable; the picture was not. I checked that the `<img>` element existed and that its URL served data, and called that "thumbnail rendered". What distinguishes the two is one property — `naturalWidth > 0` — and this task's verification asserted it.

That makes six for the day ([[ISS-0043]], [[ISS-0046]], [[ISS-0047]], [[ISS-0058]], [[ISS-0060]], and this) where the failure was checking the thing *next to* the thing.

**What I did not verify by doing.** The native right-click menu is asserted by wiring, not by clicking: popping a native menu over CDP runs a nested run loop in the main process and can hang it, and clicking **Triage** would start a real agent session against Edwin's repo — a side effect that is not mine to trigger. The cross-file test exists precisely because that boundary cannot be clicked from a test, and it is asserted in both directions. That is a weaker guarantee than the rest of this note and is labelled as one rather than blended in.

**A self-inflicted lesson.** Mutation-testing the menu wiring, I reverted the mutation with `git checkout desktop/src/main.ts` — which restored **HEAD**, silently deleting the uncommitted menu block I had just written. The test caught it immediately (`the inbox context menu is gone from main.ts`), which is the only reason it did not ship. Mutations get reverted from a copy, not from git, whenever the file has uncommitted work.
