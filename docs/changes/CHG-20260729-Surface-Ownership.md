---
type: "[[change]]"
id: CHG-20260729-Surface-Ownership
aliases: ["CHG-20260729-Surface-Ownership"]
title: "Library reduces to Pinned + Docs tree; plans, risks, changes, tests and reviewed items move to the surfaces that own their question"
status: merged
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: ["[[PHASE-010-Surface-Ownership]]"]
related: ["[[FEAT-0046-Plans-On-The-Feature]]", "[[FEAT-0047-Risks-On-The-Issues-Surface]]", "[[FEAT-0048-Changes-On-The-Overview]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[FEAT-0050-Library-Reduction]]", "[[ISS-0062-Most-Plans-Are-Invisible]]", "[[ISS-0063-Dead-Stat-Tiles]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
---

# Surface ownership

## What changed

Library held eight by-type groups. Measured against this repo's corpus, three were duplicates or dead ends and one was rendering 42% of its own contents. Each type moves to the page that answers the question it is read for; Library becomes **Pinned + Docs tree**.

| Type | Was | Now |
|---|---|---|
| Plans | `rare:plan`, 14 of 33 files | Nested under their feature in the Features mode, resolved by path — all 38 |
| Risks | `rare:risk`, the only surface they had | Severity groups in the Issues mode; the Risks stat tile navigates there |
| Changes | `rare:change` | A Changes tile in the overview history band — recent expanded, the existing week/month buckets collapsed beneath |
| Tests | `rare:test` | A full register on the review desk beside the queue; the Tests stat tile navigates to `~review` |
| Decisions | `rare:adr` | Removed as a duplicate — the overview record column already rendered every ADR inline |
| Designs | `design` group | Removed as a duplicate — the Design mode owns the same `~design/<id>` routes |
| Workflows | `rare:workflow` | The Docs tree, via `DOC_TREE_INLINE_TYPES` |
| — | — | **New:** a Reviewed register on the desk, from note frontmatter |

## Contract changes

- **New endpoint** `GET /api/cockpit/changes` → `{total, recent[], buckets[]}`.
- **`/api/cockpit/review-queue` gains `registers`** → `{tests[], reviewed[]}`. Additive; the four queue groups and the outcome tally are unchanged.
- **`nav_payload(mode="library")`** no longer emits `rare:*` or `design` groups.
- **`nav_payload(mode="issues")`** gains `risk:<severity>` groups.
- **`nav_payload(mode="features")`** feature items may carry a `plan`-typed child.
- `DOC_TREE_EXCLUDED_ROOTS` no longer contains `workflows`.

Nothing was removed from the schema, so an older renderer against a newer sidecar degrades to fewer groups rather than erroring. The reverse — newer renderer, older sidecar — drops the Changes tile rather than showing an empty box, which was observed rather than assumed (see [[TST-0022]]).

## Two things found by measuring rather than reading

**19 of 33 plans were invisible** ([[ISS-0062]]). `notes_by_type("plan")` reads frontmatter; 19 `PLAN.md` files have none. They were not merely absent from the group — `features/` is a `DOC_TREE_EXCLUDED_ROOTS` root, so they reached no surface at all. The fix reads the path, which already encodes the relationship. Retyping the 19 files was rejected: it would pass the count while leaving the mechanism dependent on frontmatter nobody is required to write.

**Cmd+P would have quietly lost half the corpus.** `buildQuickCorpus` fetched `mode=library` on the documented assumption that it was "the broadest single fetch". After the reduction that is pins and loose files — a still-populated palette, nothing visibly broken, and half the notes no longer findable. It now enumerates five modes plus the two registers and the changes payload. This is the same reachability failure [[REQ-0025]] gates the nav against, reached through search instead, and it is the reason that requirement exists.

## Verification

`552 passed, 1 skipped` at the time of the commit (`556` after ISS-0065). [[TST-0022]] adds 24 assertions, counted against the corpus rather than checked for non-emptiness — ISS-0062's type-based lookup returned 14 entirely convincing rows and passed every shape assertion in the suite.

[[TST-0022]]'s seven manual steps were run on 2026-07-29 (six at first; step 7 was added the same day after ISS-0064) over CDP against a restarted app on a fresh sidecar, and all pass: 38 plan rows (untyped included), risks grouped in Issues, both tiles navigating, the Changes tile with 5 recent rows over 3 collapsed buckets, `Tests · 22/22` and `Reviewed · 62` on the desk, Library reduced to the Docs tree with `workflows/` in it.

**That run found one defect the whole automated suite passed over**: the Changes tile's count rendered as `Changes97`, glued to the title, because tile `h3`s are `display: block` and the count's `margin-left: auto` does nothing there. Fixed (`.ov-changes h3 { display: flex }`) and re-verified. It is the exact class of failure the manual steps exist for.

What the pass did **not** establish: that the new surfaces look right. It asserted structure and geometry — presence, counts, computed `display`, click destinations — not appearance. That remains a human judgement.

**The independent review pass has not run.** QUALITY.md requires one for this note and for the features reaching `done`; the validator's REVIEW warning here is accurate rather than noise.

## Not done here

- **The upstream workflow template.** Eight of eleven fleet repos carry only the untouched template three (`status: draft`, `updated: 2026-01-29`); the three repos that authored their own deleted the template ones and every authored workflow is `status: active`. The type earns its keep; the shipped drafts do not. That fix belongs in `~/Dev/repos/project-os/`.
- **Removing the Library mode button.** At Pinned + Docs tree it is a file browser, and opening a file by name is still a real need.
- **The Reqs stat tile**, still deliberately dead — requirements nest under features, so it has no single destination. Asserted as a decision in [[TST-0022]] so it does not read as an oversight.

## Independent review — 2026-07-30, changes-requested

Fresh session, `model:claude-opus-5`, starting from these notes and `git show bed48ea` with no access to the authoring session's reasoning. Same model family as the author, different context (ADR-0013). Findings in full on [[REQ-0025]]; the corrections this note needs:

**1. The Decisions row of the table is wrong, and the change it describes stranded a type.** "Removed as a duplicate — the overview record column already rendered every ADR inline" is false as of this commit. `fillRecordColumn` (`renderer.ts:10520`) gets its ADRs, tests and references from `fetchRecordNotes('library')` → `GET /api/cockpit/nav?mode=library`. That harvest yielded 8 ADRs and 21 tests at `bed48ea~1`; it yields **0** at `bed48ea`, because the reduced payload emits only `docs-tree` and those items carry no `id`. The Decisions card is therefore never built on the project-scope overview, and 8 of 9 ADRs have no navigation route and no Cmd+P route. The record column was not a duplicate of Library's Decisions group — it was that group, reshaped.

**2. A third consumer of `mode=library` was missed.** The note's account of the `buildQuickCorpus` near-miss is exactly right, and the same failure recurs twice more in the same file: `fillRecordColumn` (line 10520) and `appendAsyncWaitingRows` (line 5852). The Verification record card is now empty on the project overview; the attention inbox's `failing`/`ready` test rows are latent only because all 22 tests currently pass. Neither is mentioned in the contract-changes list, and both belong there.

**3. The verification figures are stale relative to the commit they ship in.** This note says `549 passed, 1 skipped` and "[[TST-0022]] adds 17 assertions"; the committed suite is `552 passed, 1 skipped` with 20 assertions in `tests/test_surface_ownership.py` (both reproduced). It also says "six manual steps" where [[TST-0022]] carries seven.

**4. What survived refutation.** Everything else. The plan-by-path fix, both stat-tile destinations, the risk groups, the changes partition, both desk registers and the Library skip-set were mutation-tested rather than re-read, and each has at least one assertion that fails when the implementation is broken — including the specific revert this note claims to guard against (`_feature_plan` → `notes_by_type("plan")` fails 2 tests). The degradation claim in "Contract changes" is sound. `tsc` clean; validator clean; the one full-suite failure I saw (`test_desktop_build_is_not_stale`) was an mtime artefact of my own checkout, not a defect.
## Re-review — 2026-07-30, approved

All three findings addressed. The verification figures now read `552 passed` at commit time (`556` after [[ISS-0065]]) and 24 assertions; "seven manual steps" replaces "six", with the six-then-seven history noted. The reachability defect is fixed and tracked in [[ISS-0065]], and a corpus-wide sweep confirms no canonical type is unreachable ([[REQ-0025]]).

**One line still to change.** The `Decisions` row of the table reads "Removed as a duplicate — the overview record column already rendered every ADR inline". That is true again *now*, but by a different mechanism than the one the row describes, and it was false for the life of the commit. Point it at [[ISS-0065]] so a reader is not led back to the reasoning that caused the defect. Not blocking — the substance is right and the correction is on the record above.
