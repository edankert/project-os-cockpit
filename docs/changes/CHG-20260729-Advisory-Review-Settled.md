---
type: "[[change]]"
id: CHG-20260729-Advisory-Review-Settled
aliases: ["CHG-20260729-Advisory-Review-Settled"]
title: "ADR-0007 settled: review stays advisory permanently, and the desk's outcomes tally is removed"
status: merged
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: ["[[ADR-0007]]", "[[ISS-0064-Two-Reviewed-Sections]]"]
related: ["[[TASK-0247-Drop-The-Advisory-Tally]]", "[[TASK-0246-Desk-Section-Order-And-Naming]]", "[[FEAT-0041-Review-Desk]]", "[[FEAT-0049-Review-Desk-As-Record]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
---

# Advisory review, settled

## The decision

**[[ADR-0007]]'s gating question is closed. Review stays advisory, permanently.** Decided by Edwin on 2026-07-29. No lifecycle change — the same outcome the advisory phase already had, now by decision rather than by default.

The ADR set two exits: promote to gated-by-type if review regularly changes plans, or "stay advisory and say so here" if it rubber-stamps. The evidence takes the second exit **for a third reason neither branch anticipated**, and that reason is the point of recording it.

It is not that review rubber-stamps. It is that **the flow the gate would govern does not happen.**

| Mechanism | Where it sits | Count |
|---|---|---|
| The gate ADR-0007 designed | Before implementation, on proposal sets entering the desk queue | **1** |
| Review as actually practised | At close-out, stamping `review_verdict` into the note (`QUALITY.md`) | **62** |

Gating the first would have governed 1 of 63 review events, adding a bottleneck to a path nobody walks while the 62 real reviews continued past it. Review is not rare in this project — it is pervasive, and it happens somewhere else.

## How it surfaced

Not from the revisit, which had already run at PHASE-008 close-out (2026-07-26) and honestly concluded "there is nothing yet to decide with" against a count of zero. It surfaced by accident three days later.

[[TASK-0242]] added a Reviewed register sourced from note frontmatter, and put it a few rows below the pre-existing tally — which was also headed `Reviewed`. `Reviewed · 1` above `Reviewed · 62` read as a bug, was filed as [[ISS-0064]], and got renamed to `Outcomes` by [[TASK-0246]]. Edwin then asked what the Outcomes block was for, given there was nothing in it to select.

That question got further than the bug report. **Renaming made two sections legible; asking what one was for made it unnecessary.** The two numbers had always been measuring the gap this decision rests on — nothing rendered them side by side until now.

## What changed in the code

- The `Outcomes` block is gone from the desk's nav pane, and `.review-tally*` is gone from the stylesheet ([[TASK-0247]]).
- Pane order is now **Queue → Reviewed → Tests**.
- **The recording survives.** `ReviewStore.resolve()` still stamps outcomes and `review_queue_payload` still exposes `outcomes`/`reviewed`. That is the ledger's own account of what the desk did, it costs nothing, and it is what a reopened gating question would read. What was retired is the obligation to watch it, not the data — so `test_queue_reports_the_advisory_phase_tally` keeps asserting the payload while [[TST-0022]] asserts the surface is gone.
- No contract removal: the payload keeps both fields, so no `SCHEMA_VERSION` change and no consumer breaks.

## Verification

552 passed, 1 skipped; `tsc` clean. Live DOM after a restart: `tallyPresent: false`, pane headings exactly `Queue`, `Reviewed · 62`, `Tests · 22/22`.

Three guards, one of them deliberately redundant: the tally's absence is checked in **both** the renderer and the stylesheet (a stylesheet keeping selectors for a deleted block is how CSS rots); the pane order is pinned because both registers append at the tail of one function and the next append would reshuffle it silently; and the single-`Reviewed`-heading assertion is kept even though the collision is now gone by subtraction, so it stays gone.

## Not done here

- **The independent review pass** on this note and on [[CHG-20260729-Surface-Ownership]]. QUALITY.md wants one; the validator's REVIEW warnings on both are accurate rather than noise.
- **Nothing upstream.** ADR-0007 is this repo's decision about its own lifecycle; the fleet template is untouched, exactly as the advisory phase promised.

## If this is ever reopened

The trigger would not be "~20 sets" again — that trigger failed twice by never firing. It would be evidence that pre-implementation proposal review is *being used*: a real count of sets amended or sent back through the desk. Until then, gating a path with no traffic is legislating for a hypothetical, which is what [[ADR-0006]] and upstream ADR-0008 were both written about.
