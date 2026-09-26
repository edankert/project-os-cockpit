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
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
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

Gating the first would have governed **1 of 62** review events, adding a bottleneck to a path nobody walks while the other 61 continued past it. (Corrected 2026-07-30 from "1 of 63": the sets overlap by one, since the desk interaction is [[DES-0002]] and that note carries a verdict.) Review is not rare in this project — it is pervasive, and it happens somewhere else.

Narrowing the ratio honestly: 10 of the verdicts read `CLOSE`, not a QUALITY.md value, so conforming reviews number nearer 51; and the windows differ (verdicts span 11 days, the desk 3), making the rate comparison ~17:1 rather than 62:1. One event in seventeen is still a path nobody walks.

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

## Independent review — 2026-07-30, changes-requested

Fresh session, `model:claude-opus-5`, from the notes and the diff only. **The decision is upheld.** The code change is correct and well-guarded. What needs correcting is the arithmetic in the sentence the settlement rests on, which is repeated in [[ADR-0007]]'s new section, in that ADR's frontmatter `consequences`, and in the commit message.

**The two populations overlap; they are not 1 + 62 = 63.** The single desk interaction is the [[DES-0002]] acceptance on 2026-07-28, and `docs/designs/DES-0002-*.md` carries `review_verdict: "accepted"` — so it is *inside* the 62 (it is the only `accepted` verdict in the register; the other 61 are 51 `approved` and 10 `CLOSE`). The correct framing is **1 of 62 review events came through the desk**, not 1 of 63, and "the 62 real reviews continued past it untouched" is wrong by one. This strengthens the conclusion rather than weakening it, which is why it is worth fixing rather than leaving.

**"62 notes carrying a `review_verdict`" is literally true but is not 62 close-out reviews.** Ten of the 62 carry `review_verdict: CLOSE`, which is not a value in QUALITY.md's vocabulary (`approved` | `changes-requested`). That is a pre-existing corpus-hygiene problem this change did not introduce — but the new register is what surfaces it, and the ADR now leans on the count. By the documented vocabulary the comparable figure is 52.

**The windows are not comparable, and the note does not say so.** All 62 `review_date` values fall in 2026-07-18..2026-07-28, an 11-day span; [[FEAT-0041]] shipped 2026-07-26, so the desk's window is 3 days. Rate-normalised the gap is roughly 17:1, not 62:1. The conclusion still holds by a wide margin — the point is that the table presents two raw counts as commensurable when they are not, and the note's own better sentence ("they count different populations") is the one that should carry the argument.

**The load-bearing "1" is not verifiable from the repo.** It lives in `.cockpit/review-requests.json`, which `.gitignore:32` excludes. I confirmed it locally (one request, `subject: DES-0002`, `status: resolved`, `outcome: accepted`, `resolved_at: 2026-07-28T15:31:03+00:00`), but a future reader deciding whether to reopen a *permanent* settlement cannot. Transcribe the resolved-request record into [[ADR-0007]] so the evidence outlives the untracked file.

**Also worth fixing on the ADR itself.** Its frontmatter still reads `review_date: "2026-07-26"` / `reviewed_by: "user:edwin"`, three days older than its most consequential section. I deliberately did not overwrite those fields — that provenance is Edwin's own review of the original decision and is stronger than mine — but the settlement section is unreviewed by that stamp, and the note should say which review covers which part.

**What survived refutation.** The code change is clean. `test_the_advisory_tally_is_gone_from_the_desk` fails when `.review-tally` rules are put back in the stylesheet; `test_the_desk_pane_order_is_queue_reviewed_tests` fails when the two register appends are swapped; the payload guard (`test_queue_reports_the_advisory_phase_tally`) does still assert `outcomes`/`reviewed`, so "the recording survives" is accurate rather than aspirational. No `SCHEMA_VERSION` change is needed and none was made.

## Re-review — 2026-07-30, changes-requested upheld (one item)

The arithmetic is fixed, and fixed better than I asked: "1 of 62" with the overlap explained, the `CLOSE`-verdict narrowing to ~51 conforming reviews, and the differing windows stated as a ~17:1 rate. The conclusion is stronger for being stated precisely. Nothing else here is open.

**The one item I am upholding, because you asked for the judgement: yes, a permanent settlement needs its evidence committed.**

The shape is small — transcribe the single resolved request into [[ADR-0007]] verbatim: subject `DES-0002`, kind `review`, status `resolved`, outcome `accepted`, `resolved_at 2026-07-28T15:31:03+00:00`, with the sentence that this is the entire population as of 2026-07-30. One row, four lines. No mechanism, no committing the store, no new obligation.

The argument for it is not mine, it is already in this repo. [[TASK-0242]] sourced the Reviewed register from note frontmatter rather than from `ReviewStore` **precisely because** `_MAX_REQUESTS = 200` trims oldest-first on every save, so "a store-sourced register would silently lose its tail". That reasoning applies with full force to the datum this decision rests on: it lives in a gitignored file, in a store that is designed to forget, and the reopen trigger is defined as *evidence that pre-implementation review is being used* — which is unreadable without the baseline it is measured against. A permanent decision whose evidence a fresh clone cannot see, and whose own store will eventually drop it, is exactly the handoff failure this review exists to catch. It is also the cheapest finding in either pass to close.

Everything else about this change is sound, and the reasoning that neither of the ADR's two exits applied is the right call on this evidence.

## Independent review, round three — 2026-07-30, approved

The store row is transcribed into [[ADR-0007]] and I checked it against the file rather than against the note: `.cockpit/review-requests.json` holds one request, `subject: DES-0002`, `kind: review`, `status: resolved`, `outcome: accepted`, `resolved_at: 2026-07-28T15:31:03+00:00`. The table matches exactly, is labelled as the entire population as of 2026-07-30, and gives a reopener something to compare a future count against.

The reasoning recorded alongside it is the part worth keeping: [[TASK-0242]] avoided this store *because* `_MAX_REQUESTS = 200` makes it forget, and the settlement was resting on it anyway. A decision described as permanent now has evidence that outlives the file it came from.

Nothing further. The arithmetic corrections from the second pass are sound and the caveats are stated more precisely than I asked for.
