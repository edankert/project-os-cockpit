---
type: "[[design]]"
id: DES-0011
aliases: ["DES-0011"]
title: "Publication is an obligation — unpushed work joins Needs you, the push lives with the commits, and the overview button carries the number"
status: draft
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'let's add the git status to the needs you section instead and have the actual push solution in the overview history. Can we then have an indication of having to push using a number on the overview icon?'"]
asset: ""
implements: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[PHASE-030-Obligations-Go-Home]]"]
supersedes: ""
superseded_by: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ADR-0025]]", "[[ADR-0022]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0098]]", "[[FEAT-0055]]", "[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]", "[[DES-0004-Attention-In-The-Squares]]"]
---

# Publication is an obligation

> **Draft, and it must stay draft until its artifact exists.** `DESIGN-ASSET` exempts a draft from declaring an artifact, which is the only reason this note validates with an empty `asset:`. A design offered for review renders; this one does not yet. That is [[TASK-0418]], and until it is done this note cannot leave `draft` honestly.

## Problem

Three surfaces already tell you about unpushed work — a band on the overview, a group on the Agents screen, a line in the rail tooltip — and **all three are silent for the repo you have open**, because `ahead` is computed only by a pass that skips live sidecars ([[ISS-0156]]). Measured 2026-08-13: this repo, two commits ahead of an ordinary GitHub remote, reported nothing anywhere.

Fixing the data would restore three surfaces that were already the wrong shape. None of them is where a person looks to find out what needs them, and two of them exist only if you navigate there. Meanwhile the tool has a mechanism for exactly this question — the obligation registry, its `Needs you` groups, and the badges that are always on screen — and publication was outside it, because the registry counted only judgments about the record.

[[ADR-0027]] widened that. This design says what the widening looks like.

## Approach

**One fact, three appearances, no second mechanism.** The count comes from the registry like every other obligation, so the badge, the `Needs you` group and the row cannot disagree — that is the property `obligations.py` exists to hold, and the reason for widening the registry rather than running git beside it.

- **The number lives on the overview button.** Existing machinery: `refreshObligationBadges()` already paints `.mode-badge` on `.top-bar-btn[data-mode]` from `/api/cockpit/obligations`, and `overview` is one of the five views. Registering the obligation makes the number appear with **no new UI**. Its tooltip comes from the payload's `breakdown` + `nouns` + `verbs`, so it reads `3 · commits to push`, not `3 items here need a person`.
- **The row lives in `Needs you`.** Existing machinery: `_needs_you_group()` builds the leading group for every view except `issues` and `tests`, which already lead with their own. Overview qualifies today.
- **The action lives in history, with the commits.** [[ADR-0020]]: an obligation surfaces where its subject lives, and the subject of *not pushed* is those specific commits — which the overview's history tile and `~history` already draw. The push button belongs next to them, and the unpushed commits are marked so a person sees **which** work is unpublished, not only how much.

[[ADR-0025]] is what permits the row to be in two places: the `Needs you` group is a shortcut list, and the commits stay in their structural place. Same rule, same reason.

## The ladder History already half-draws

History renders as `[uncommitted band] → [commit divider] → [transition rows] → [commit divider] → …`. A commit **is** a divider, with the notes it saved listed beneath it, and the band above the first divider exists because *"the question 'is this written down yet' should not require leaving the page"*.

That is a ladder in time with its middle rung missing:

1. **not saved** — the uncommitted band. Exists.
2. **saved, not published** — nothing says it.
3. **published** — every other divider.

**So an unpushed commit says so on its own divider** (Edwin, 2026-08-13: *"should this not be shown as a not pushed commit?"*). Not a separate boundary element: git guarantees the unpushed commits are a **contiguous run at the top** — everything after `@{u}` — so marking each one produces the boundary for free, and a second mechanism drawing a line would be a thing that could disagree with the marks beneath it.

The band and the marks then read as one scale, which is the point: *in flight → saved → published*, top to bottom, in the order they happen.

## Regions

*(Named now so the artifact can anchor annotations to them; the artifact is [[TASK-0418]].)*

- `overview-button-badge` — the count on the Overview view button, and its hover text.
- `needs-you-row` — the git row inside the overview's leading `Needs you` group: subject, count, verb, and where it goes when clicked.
- `history-unpushed-marker` — the mark an unpushed commit divider carries, and how it sits against the uncommitted band above it.
- `history-push-action` — the button and its label. **Where it attaches is the artifact's to settle** — the topmost unpushed divider, or a small header over the run — and it is a layout question, not a design fork.
- `no-remote-state` — the different and worse message, which must not be folded into the unpushed sentence.
- `deploy-remote-state` — counted, named, and not offered.

## The four states, which must not collapse into two

1. **Ahead, backup remote** — `N` on the badge, a row in `Needs you`, `Push N` offered in history.
2. **Ahead, deploy remote** — **counted** (Edwin, 2026-08-13: *"deploy remote should count"*), shown, and the push **refused**, with the refusal reading as a decision rather than a broken button. One fleet repo's only remote is a server path and pushing it publishes a live website.

   It counts under a **kind of its own** — `commits to deploy`, not `commits to push` — so the badge's breakdown can say `2 · commits to push, 3 · commits to deploy` rather than merging two things a person must treat differently. One number, two nouns, and the verb the row names is not one the cockpit performs: [[ADR-0027]] test 3 requires an action the cockpit can *offer **or** name*, and this is the case that clause was written for.
3. **No remote at all** — *"nothing here is backed up"*. Worse than unpushed and deliberately its own sentence, as the current overview band already has it. Not a count; there is no number of commits that fixes it.
4. **Unknown** — **not permitted.** [[ADR-0027]] admission test 4: absent-at-zero means unknown renders exactly like nothing-owed. This design is inert and quietly wrong until [[ISS-0156]] is fixed, which is why that fix is the first task and not a footnote.

## What this does not do

- **It does not put a push button on the rail square.** [[DES-0004]]'s budget problem: the square's corners and colour are spent on validator state and agent state, and a publishing action on a 44px target is a mis-click waiting to happen. The rail keeps its tooltip line and gains nothing.
- **It does not add a header button beside the project name.** Considered and dropped by Edwin on 2026-08-13 in favour of this shape. Recorded because it is the obvious idea and will be re-proposed: a permanently visible publish control 22px from the settings kebab, on the one action in this app that publishes.
- **It does not retire the Agents-screen group.** That surface answers *which of my twelve repos*, which no per-project surface can. This design answers *this project, and do it now*.

## Settled 2026-08-13

- **A deploy remote counts** — Edwin's call, under its own kind and its own verb. A badge that omitted it would make *nothing owed* false about a repo with a real backlog, and the alternative — one kind covering both — would merge two things a person must treat differently.
- **An unpushed commit says so on its own divider.** Edwin: *"should this not be shown as a not pushed commit?"* The three-option question that preceded this was badly posed: because the unpushed commits are always a contiguous run, per-commit marking yields the boundary as a side effect, so there was never a real choice between marking commits and drawing a line.

- **The count is per project only** — Edwin's call. The registry payload is per-sidecar, so this is also what the machinery does by construction. The fleet question stays where it already lives, on the Agents screen, which is the only surface that can answer *which of my twelve repos*.

## The artifact comes from the built surface, not before it

Edwin, 2026-08-13: *"probably easier to build it and we can change then."* Taken, and it is compatible with the design gate rather than an exception to it:

- `DESIGN-GATE` fires only once a feature has **left** the pending band (`backlog`, `planned`, `deferred`, `cancelled`, `superseded`). [[FEAT-0100]] is `backlog`, so building breaks nothing; the gate bites when the feature would close, which is where it is meant to bite.
- **Three of the four tasks contain no layout decision at all.** [[TASK-0415]] is data, [[TASK-0416]] is a refactor of existing code, and [[TASK-0417]] makes the badge and the row appear through machinery that already exists. Only [[TASK-0418]] touches pixels.
- `POST /api/design/capture` exists precisely because *"an agent iterating against the live surface edits the working copy six times and commits once"*. So the built surface is deposited as this design's artifact, with its reason, and the design is accepted **on evidence rather than on a drawing** — which for a change of one mark and one button is the truer artifact anyway.

The two remaining layout questions are therefore not blockers, and are recorded as things to look at rather than decide in advance:

- Where the push button attaches within the unpushed run — topmost divider, or a header line above it.
- What the deploy row's words are. They matter more than usual: too imperative and it reads as a button that is broken, too soft and a real backlog reads as a footnote.
