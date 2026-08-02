---
type: "[[change]]"
id: CHG-20260802-Cards-Everywhere
title: "The navigators look like cards, not just behave like them: coloured ids, no icons, inline expand affordances and a consistent pill"
status: merged
reviewed_by: model:claude-opus-5
review_date: 2026-08-02
review_verdict: approved
date: 2026-08-02
owner: user:edwin
component: [static, desktop-renderer]
related: ["[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[ISS-0088-The-Card-Is-A-Style-Not-Just-A-Behaviour]]", "[[FEAT-0058-One-Shape-Per-Navigator]]"]
---

# Cards everywhere

## What changed

- **Group heads** show a type-coloured ID and a name. The icon is gone — it encoded a fact the coloured ID already carries.
- **The pill is on every group**, not some. It used to hide when the item summary happened to end in the same word, which made it look random.
- **A feature's expand affordance sits on the feature's own row**, and its presence is what tells you the feature has requirements or a plan. It used to be a second row underneath reading `2 requirements · plan`.
- **Nested lists lost their border rules.** Indentation already says what they were saying.
- **Nav groups are framed like the context pane's cards** — same border, radius and surface. The completed band is a heading *over* cards rather than a card around cards.
- **The design view** says `Completed · 1 · 1 design`, not `1 item`.
- **The phase-scoped record cards** are `Verification`, `Decisions`, `In flight`, `Attention` — the `here` suffix is gone.
- **The overview's completed band** takes the same card frame.

## Where each navigator lands

| view | live | completed |
|---|---|---|
| Tasks | `Deferred`, `Unset` open | `Done · 268`, `Cancelled · 2`, `Superseded · 2` shut, no divider |
| Issues | open severities and risks | divider, then a card per severity |
| Features | phases in flight | divider, then 17 phases → features → reqs/plans |
| Design | `Designs` | `Completed · 1` |
| Review | `Queue`, `Changes requested · 10`, `Tests` | `Completed · 2` |

## The review desk is deliberately unchanged

Its sections are **kinds of obligation**, not collections you open and close, and a card invites collapsing something you always want to see — an empty queue is the point of looking. Reasoning recorded in [[ISS-0088]].

## Restart required

Mode 3 is a built bundle. The change is live after the desktop app restarts.
