---
type: "[[design]]"
id: DES-0014
aliases: ["DES-0014"]
title: "The glass cockpit — depth is priority, every view is a re-arrangement rather than a page, and the console is furniture that floats over the notes"
role: proposal
decided: ""
status: "proposed"
phase: "[[PHASE-028-Borrowed-Capability]]"
owner: user:edwin
created: 2026-09-05
updated: "2026-09-05"
source: ["Edwin 2026-09-05: 'I assume this view allows for 360 degree turn around, allowing to see and store less important items out of sight?'", "Edwin 2026-09-05: 'The minority report view could work ... I do not consider this to be a vr view ... instead I would like you to design each of the current sets of views for this, these views should be selectable and each view should concentrate on the same details and notes currently in that view, making some note-types and states more important then others (directly in view)'", "Edwin 2026-09-05: 'The console is a view which sits at the bottom middle but can be moved anywhere and can be made smaller/bigger if needed and all the notes can be arranged around the console ... maybe the console should be slightly transparent'", "Edwin 2026-09-05: 'the console and usage view in the left pane need a different approach, possibly for the console statuses show some carousel where the current active ones or selected ones can be moved to the front? Also the repo/project selection could be handled similarly'", "Edwin 2026-09-05: 'When selecting a note it opens up more fully and also somehow brings the associated notes into view'"]
asset: "DES-0014-the-glass-cockpit.html"
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[DES-0013-Nine-Ways-To-Read-The-Record]]", "[[PHASE-028-Borrowed-Capability]]", "[[DES-0002-Cockpit-Design-System]]", "[[ADR-0025-What-Needs-A-Person-Goes-First]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[FEAT-0003-Embedded-Terminal]]", "[[DESIGN]]"]
tags: [design, glass, views]
---

# The glass cockpit

> **This is [[DES-0013]]'s GLASS treatment taken seriously as an application**, at Edwin's direction and with the headset dropped: a desktop surface, mouse and keyboard, one window. It is a whole cockpit — all eleven views, the console, the agent sessions, the workspace picker — not a decoration over the existing one.

## Problem

**The current cockpit sorts by position; a glass surface can sort by depth, and depth is the axis this record actually needs.**

The left pane is a list. A list has one dimension, so everything in it competes for the same scarce thing: vertical position. That is why [[ADR-0025]] had to be written — *what needs a person goes first, in every view* — and why `nav_payload` prepends `_needs_you_group` to all eleven modes and appends `suppressed_group` to most of them. The rule exists because a list cannot say *"this matters more"* except by putting it above something else.

Measured in `cockpit.py`: **every view is already three bands** — what needs you, the view's own subject, and what the in-flight rule quieted. The list flattens that into a scroll.

## Approach

**Depth is priority. One field, eleven arrangements.**

Notes are cards in a perspective field. A card's **z** is how much it wants you, and that is not decoration — it is the same predicate `obligations.owed_items` already computes:

- **Front plane** — what needs a person. Large, sharp, unavoidable, exactly the band [[ADR-0025]] forces to the top of every list today.
- **Mid field** — the view's own subject, arranged by the view's own rule.
- **Deep field** — the quiet: terminal work, suppressed items, the 70% of this corpus that is finished. Small, dim, blurred, still there.

Five consequences follow, and each answers one of Edwin's questions.

**0. The field is a cylinder, and you turn in it.** Edwin's question — *"I assume this view allows for 360 degree turn around, allowing to see and store less important items out of sight?"* — settled the shape. It does, and it changes what the quiet band **is**. Rendered small and dim in front of you, 70% of this corpus is still a thousand rectangles between you and the nine things that matter. Placed **behind** you it costs nothing, stays one gesture away, and is counted on screen so it cannot be quietly lost. An open card also offers *put behind me* — the direct-manipulation form of `suppressed_group`, per session, and never a write.

**1. A view is a re-arrangement, not a page.** Switching from Features to Issues does not navigate; the same cards fly to new positions under a new rule. You *watch* a note change importance, which is a thing the current cockpit cannot show at all. Eleven arrangements are specified: `overview`, `intent`, `features`, `tasks`, `issues`, `tests`, `publication`, `review`, `active`, `library`, `recent`.

**2. The console is furniture, not a pane.** It defaults to bottom-centre, drags anywhere, resizes, and is translucent — so the field reads through it. The layout treats it as an **obstacle**: cards flow around its footprint rather than under it, except the deep field, which is allowed to sit beneath the glass because that is what the transparency is for.

**3. Consoles and sessions are one carousel, not a left-pane list.** Every running thing — a workspace shell, an agent session — is a card on an arc at the lower left. The front card is the one the console slab is showing. Bringing another forward switches what the slab is attached to, which is the operation the current agents panel makes you do in two places.

**4. The workspace picker is the same mechanic at a different radius.** Twelve repos on a slow ring at the upper left, edge-on, the current one facing you and carrying its owed count. One gesture, one metaphor, learned once.

**5. Selecting a note pulls its neighbourhood with it.** The card comes to the front plane and opens; every note it links to, and every note linking to it, flies into a ring around it; everything else recedes and dims. This is the corpus's 16148 wikilinks doing work in the reading surface rather than in a graph view nobody opens.

## What this does not change

The **write path**, the **verbs** and the **guards** are the cockpit's, unchanged. A human-only verdict is still refused server-side to an agent ([[REQ-0026]]); the registry still owns the verb ([[ISS-0153]]); obligations still live with their subject ([[ADR-0020]]) — the front plane is *where the subject is*, not a central queue.

The **reader** is also the cockpit's. An opened card renders the note with the existing renderer. A second Markdown parser is the mistake [[ISS-0151]] names, and a glass surface is not a reason to make it.

## Regions

- `masthead` — what this is, and that it is one window rather than a mode
- `stage` — the live prototype: the field, the view rail, the console, the carousel, the ring
- `depth-rule` — the three bands and what decides a card's distance
- `views` — the eleven arrangements, each with its own rule and what it brings forward
- `console` — the slab: default position, drag, resize, transparency, and the obstacle rule
- `carousel` — consoles and sessions on one arc
- `ring` — the workspace picker
- `focus` — selecting a note, and the neighbourhood that arrives with it
- `chrome` — search, tabs, back/forward, the validator, the inbox: where the rest of the cockpit went
- `objections` — what is wrong with this, including the two things depth is bad at
- `chrome` is listed above; `views` carries the eleven arrangements as a table

## Tokens

**Status and severity are the implementation's, verbatim** from `src/project_os_cockpit/static/base.css`, declared light-first so `design_tokens.read_tokens` compares like with like.

The glass chrome — the cyan instrument palette, the depth fog, the slab tint — is this artifact's own and specifies nothing beyond itself. **It carries a known cost, recorded in [[DES-0013]] and unchanged here:** washing the status bands toward one instrument colour collapses four of the six into 25 degrees of hue. This design's answer is that **depth, not hue, carries priority** — hue is left to say only what the note *is*, and the alarm red is held out for `blocked`.

## The strongest version of this is smaller than the pitch

The document opens by calling this a replacement, and the prototype earns most of that. But **depth is bad at counting and bad at comparing**: "how many issues are open" is answered instantly by a list and badly by a field, and two cards at different depths are different sizes, so they cannot be compared. A list is uniform on purpose.

So the version I would defend is not the whole cockpit. It is **a twelfth view inside the cockpit that exists**, sharing its reader, its verbs and its guards — good at *what wants me* and *what is this connected to*, and honest that a list is better at the rest.

## Out of scope

- **VR and hand tracking.** Explicitly dropped at Edwin's direction. Mouse, keyboard, one window.
- **Building it.** No feature, task or phase is allocated.
- **The nine other designs.** [[DES-0013]] holds those; this is one of them taken further because it was the one worth taking further.

## Revisions

- 2026-09-05 — written; the eleven arrangements, the console slab, the carousel, the ring, the focus ring
- 2026-09-05 — the field became a cylinder you turn in, after Edwin asked whether it would. The quiet band moved from *far and dimmed* to *behind you*, which is a different claim and a better one; a compass keeps the count on screen so nothing is silently lost.

## Review

<Region-anchored comments land here. Verdicts go in the frontmatter, transcribed from a review that actually happened — never anticipated.>
