---
type: "[[change]]"
id: CHG-20260811-Six-From-Use
title: "Six observations from using the app: the Caught-up overlay, the CHG review obligation, landing pages for three views, the duplicated standing documents, and the template's workflow stubs"
status: merged
date: 2026-08-11
owner: user:edwin
related: ["[[ADR-0023]]", "[[FEAT-0092]]", "[[ISS-0144]]", "[[ISS-0145]]", "[[ISS-0146]]", "[[ISS-0147]]", "[[ISS-0123]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[REL-0001-The-Human-Has-Levers]]"]
tags: [change]
---

# Six things from using it

Edwin, 2026-08-11, after [[REL-0001]] shipped. Every item below came from driving the app rather than from reading it, which is the second time in two days that has been the difference.

## What changed

**The status bar dismisses itself.** *"Creates some caught up overlay which cannot be clicked away."* It was not that button: `showStatus` never scheduled a hide, and **78 of 110 call sites** never did either, so the app's default was a permanent floating panel over the pane. The default now inverts — self-dismissing, click-to-dismiss, errors dwelling longer than info. ([[ISS-0144]])

**`Caught up` clears the section it heads.** The obligations half left the digest entirely, so removal is honest where re-rendering used to be. This **reverses [[ISS-0134]]**, whose reasoning was right about a design that no longer exists. ([[ISS-0145]])

**A change note no longer owes a review.** The overview badge read **87, and all 87 were change reviews** — enforced by a validator gate dated 2026-10-23 citing an `ADR-0011` that exists in no repo. Badge `87 → 0`. Independent review keeps the three gates where it changes an outcome. ([[ADR-0023]])

**Features, Issues and Tests land on what they owe.** `MODES_WITH_VIRTUAL_LANDING` held `{overview, intent}`; four views sent the reader to `README.md` and their badges counted things no view gathered. Each landing leads with its owed groups, named with the registry's verb — `Triage 8 issues` — from the same walk that produces the badge. ([[FEAT-0092]])

**Intent stops listing every standing document twice.** All eight appeared in `Reference` as well as the manifest, under different ids for the same file — `ARCHITECTURE`/`ARCH` — which is why an id-based duplicate check saw nothing. Matched on rel path now. ([[ISS-0146]])

**The three template workflow stubs are gone from `docs/`.** Measured across twelve repos: 24 notes, `draft`, `updated: 2026-01-29`, untouched in six and a half months, describing project-os's own machinery. **Eight further notes in three repos are real project workflows** and stay — deleting the category wholesale would have taken them. ([[ISS-0147]])

## Impact

- `GET /api/cockpit/landing?view=<view>` is new. `obligations.owed_items` is the walk behind it and behind the badge.
- `obligations.payload()` no longer declares `change` as owed; a client reading `views.overview` sees 0 where it saw 87.
- The digest band no longer renders `needs_you`; the payload still carries `needs_you_count` for the rail's per-workspace dot.
- `~tests` stopped being a mode-selecting route and became a page.

## Documentation Coverage (All Types Considered)

- features: new ([[FEAT-0092]] + TASK-0387/0388/0389)
- requirements: not-applicable
- tasks: new (three, all `done`)
- issues: new ([[ISS-0144]], [[ISS-0145]], [[ISS-0146]], [[ISS-0147]]) · updated ([[ISS-0123]])
- tests: updated (`test_view_landings.py` new; digest, boot-race and status-vocabulary suites updated)
- workflows: removed (three template stubs)
- decisions: new ([[ADR-0023]])
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (counters, focus)

## Two bugs the tests could not see

Both were in [[FEAT-0092]] and both were found by **looking at the screen**, after DOM assertions had passed:

- **A route claimed twice.** `~tests` already existed as *"selects the mode and returns"*. With a landing, `setNavMode` → `loadWsNav` → `navigateTo('~tests')` → `setNavMode` — an infinite loop that froze the renderer, while the landing branch a hundred lines below never ran and Tests silently showed the previous view's page. A duplicate route does not error; it takes whichever claim is written first.
- **A correct page in a hidden pane.** The section rendered into `#doc-view` with the right content while the stage still had it `hidden`. Every query said yes; the screenshot was blank.

Both are guarded now. The lesson is the one the acceptance suite exists for and it keeps being re-learned: *a surface is not verified until somebody looks at it.*

## Follow-ups

- [ ] Upstream ([[ISS-0123]]): write `ADR-0011` or retire the citation, carry [[ADR-0023]] into `QUALITY.md` and the `[REVIEW]` gate before **2026-10-23**, and stop the template shipping the three workflow stubs ([[ISS-0147]]).
- [ ] The seven other repos keep their stubs until the template stops shipping them.
