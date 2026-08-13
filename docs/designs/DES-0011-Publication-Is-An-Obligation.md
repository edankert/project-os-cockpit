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

## Regions

*(Named now so the artifact can anchor annotations to them; the artifact is [[TASK-0418]].)*

- `overview-button-badge` — the count on the Overview view button, and its hover text.
- `needs-you-row` — the git row inside the overview's leading `Needs you` group: subject, count, verb, and where it goes when clicked.
- `history-unpushed-marker` — how the history list distinguishes published from unpublished commits.
- `history-push-action` — the button, its label, and its three refusal states.
- `no-remote-state` — the different and worse message, which must not be folded into the unpushed sentence.

## The four states, which must not collapse into two

1. **Ahead, backup remote** — `N` on the badge, a row in `Needs you`, `Push N` offered in history.
2. **Ahead, deploy remote** — counted and shown, **push refused**, and the refusal must read as a decision rather than a broken button. One fleet repo's only remote is a server path and pushing it publishes a live website. Whether this even counts as an obligation is an open question below.
3. **No remote at all** — *"nothing here is backed up"*. Worse than unpushed and deliberately its own sentence, as the current overview band already has it. Not a count; there is no number of commits that fixes it.
4. **Unknown** — **not permitted.** [[ADR-0027]] admission test 4: absent-at-zero means unknown renders exactly like nothing-owed. This design is inert and quietly wrong until [[ISS-0156]] is fixed, which is why that fix is the first task and not a footnote.

## What this does not do

- **It does not put a push button on the rail square.** [[DES-0004]]'s budget problem: the square's corners and colour are spent on validator state and agent state, and a publishing action on a 44px target is a mis-click waiting to happen. The rail keeps its tooltip line and gains nothing.
- **It does not add a header button beside the project name.** Considered and dropped by Edwin on 2026-08-13 in favour of this shape. Recorded because it is the obvious idea and will be re-proposed: a permanently visible publish control 22px from the settings kebab, on the one action in this app that publishes.
- **It does not retire the Agents-screen group.** That surface answers *which of my twelve repos*, which no per-project surface can. This design answers *this project, and do it now*.

## Open questions

- **Is a deploy remote an obligation?** It needs a person (nobody else may push it), it has a subject, it is countable — but the verb is not `Push`; it is something closer to *deploy deliberately, elsewhere*. Counting it makes the badge include work the cockpit will not let you finish; not counting it hides a real backlog. Leaning: **count it, with its own verb**, since a badge that omits it makes "0 owed" false.
- **Does the count survive a fleet, or only the active workspace?** The registry payload is per-sidecar, so the badge is inherently per-project. That is right for this design and leaves the fleet question where it already lives.
- **What marks an unpushed commit in history** — a dividing line above them, a per-row mark, or a bounded group? The artifact decides; the note names the region so the decision is annotatable.
