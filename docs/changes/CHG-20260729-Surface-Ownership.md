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
reviewed_by: ""
review_date: ""
review_verdict: ""
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

`549 passed, 1 skipped`. [[TST-0022]] adds 17 assertions, counted against the corpus rather than checked for non-emptiness — ISS-0062's type-based lookup returned 14 entirely convincing rows and passed every shape assertion in the suite.

[[TST-0022]]'s six manual steps were run on 2026-07-29 over CDP against a restarted app on a fresh sidecar, and all pass: 38 plan rows (untyped included), risks grouped in Issues, both tiles navigating, the Changes tile with 5 recent rows over 3 collapsed buckets, `Tests · 22/22` and `Reviewed · 62` on the desk, Library reduced to the Docs tree with `workflows/` in it.

**That run found one defect the whole automated suite passed over**: the Changes tile's count rendered as `Changes97`, glued to the title, because tile `h3`s are `display: block` and the count's `margin-left: auto` does nothing there. Fixed (`.ov-changes h3 { display: flex }`) and re-verified. It is the exact class of failure the manual steps exist for.

What the pass did **not** establish: that the new surfaces look right. It asserted structure and geometry — presence, counts, computed `display`, click destinations — not appearance. That remains a human judgement.

**The independent review pass has not run.** QUALITY.md requires one for this note and for the features reaching `done`; the validator's REVIEW warning here is accurate rather than noise.

## Not done here

- **The upstream workflow template.** Eight of eleven fleet repos carry only the untouched template three (`status: draft`, `updated: 2026-01-29`); the three repos that authored their own deleted the template ones and every authored workflow is `status: active`. The type earns its keep; the shipped drafts do not. That fix belongs in `~/Dev/repos/project-os/`.
- **Removing the Library mode button.** At Pinned + Docs tree it is a file browser, and opening a file by name is still a real need.
- **The Reqs stat tile**, still deliberately dead — requirements nest under features, so it has no single destination. Asserted as a decision in [[TST-0022]] so it does not read as an oversight.
