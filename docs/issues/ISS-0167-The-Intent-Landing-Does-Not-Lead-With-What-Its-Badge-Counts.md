---
type: "[[issue]]"
id: ISS-0167
aliases: ["ISS-0167"]
title: "The Intent landing does not lead with what its badge counts, and its rows speak a second vocabulary — the one view FEAT-0092 recorded as already landed"
status: "fixed"
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-14
updated: "2026-08-15"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-15
review_verdict: changes-requested
source: ["Edwin 2026-08-14: 'One more thing on the designs landing page, the list of design items looks totally different to for instance the list of to be approved features and it does not seem to have the same philosophy as the other landing pages, although not sure if that is a bad thing. Review this and suggest approach.'"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[FEAT-0092-Every-View-Lands-On-What-It-Owes]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[ADR-0025-An-Owed-Row-May-Appear-Twice]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ISS-0089-A-Card-Head-Names-A-Category-Not-A-Thing]]", "[[ISS-0068-Waiting-On-You-Is-A-Workaround]]", "[[DES-0008-The-Returning-Human]]", "[[CHG-20260814-The-Intent-Landing-Joins-The-Other-Three]]"]
tests: []
---

# The Intent landing does not lead with what its badge counts

## Edwin's observation, and what it turned out to be

*"The list of design items looks totally different … and it does not seem to have the same philosophy as the other landing pages, although not sure if that is a bad thing."*

It is two things, and only one of them is bad.

## Measured, before touching anything

`landing_payload(index, view)` over this repo's corpus, 2026-08-14:

| view | badge | what its page leads with |
|---|---|---|
| features | 4 | `4 need you here.` → `APPROVE 4 REQUIREMENTS` |
| issues | 0 | `Nothing owed on issues.` |
| tests | 1 | `1 needs you here.` → `RUN 1 TEST` |
| **intent** | **1** | **`Designs`, then eleven design rows** |

The one Intent owes is [[ADR-0026-Remote-Workspace-Transport]], at `proposed`, verb `Decide`. Nothing on the page it opens mentions it. What it shows instead is all eleven designs, flat, in ID order — including a `superseded` one sitting between two `accepted` ones at identical weight.

*(Corrected during the walk: an earlier draft of this note said nine of the eleven were "finished work". Nine are `accepted` or `implemented`, but only **three** are terminal — `accepted` is in the **`active`** band in `statuses.py`, not `done`. That is correct and load-bearing: a design that has been decided and not yet built is live work, and it is why the fix folds on the status band rather than on how settled a status sounds.)*

That is the exact defect [[FEAT-0092]] was built to fix. It survived because FEAT-0092's first acceptance criterion reads *"Overview and Intent **keep theirs**"* — true as a statement about which views had a page, and never checked as a statement about whether that page answered the badge. Intent's page was built by [[FEAT-0087]] for a different purpose and predates the registry.

It sits inside [[PHASE-030]], whose goal is *"the count is always on screen"*.

## The two vocabularies, side by side

`renderViewLanding()` and `buildDesignRegisterList()` render the same object — an id, a title, a status — in two grammars:

| | view landings | the design register |
|---|---|---|
| heading | `VIEW_LABELS`, read from the top bar's own `title` | hardcoded `'Designs'` — so the page and the button disagree, the button says *Intent* |
| row element | `<button type="button">` | `<a href="#">` with a `preventDefault` |
| id | mono chip, `--accent-link` | inline in the title text, `"DES-0001 — …"` |
| status | `statusChip()` — the shared colour vocabulary | plain 11px `--text-faint`, joined with `·` |
| grouping | by obligation kind, verb-labelled head | flat, id order |
| settled work | n/a — only owed rows appear | at equal weight, `superseded` between two `accepted` |
| type scale | 900px column, h1 20px, *"the same as the overview's bands"* | no max width, h1 18px, full-bleed rules |

[[ISS-0023]] is the standing lesson about a vocabulary living in more than one place. This is it, at row scale.

## What is *not* wrong

**A register is the right shape for Intent.** Decisions, risks and the design system are reference material you browse; requirements awaiting approval are a queue you drain. Making Intent look like Issues would be the wrong fix. Overview also leads with a band rather than a list, so "obligations first, then the view's own content" is already the house pattern — Intent simply never got the first half.

**The identity band belongs.** The button's own title is *"Intent — what this project is, and what it should look like"*, and the band answers the first clause.

## Fix

The page becomes: **head (from `VIEW_LABELS`) → what needs you → what this project is → what it should look like.**

1. The obligation block is rendered by the same function the other three landings use, from the same `/api/cockpit/landing?view=intent` payload, so the page and the badge stay one computation by construction rather than by agreement.
2. Obligations sit **above** the identity band, per [[DES-0008]]'s rule — *"a reader who stops halfway should have seen the obligations, not the news."*
3. The register keeps its place beneath, split **live / settled**, settled folded behind a disclosure.
4. Every row — owed or register — is built by one function: mono id chip, title, `statusChip()`.
5. A row whose design is **owed** goes to the note, where `Accept` lives; every other row goes to the bench, which is what the bench is for.

## Two parts of the proposed approach were withdrawn at preflight

Recorded because both were proposed to Edwin in the review that preceded this note, and both were answered by decisions already on the record.

**The register is not grouped `Design system · Live · Settled`.** [[ISS-0089]] removed exactly that split, in `TASK-0275`: *"The design view drops the `system`/`proposal` split"* — one note in a section of its own, three designs across two headings, for a `role:` field the reader never asked about. So: live and settled, which is also the navigator's own axis and `completed-work.ts`'s existing predicate.

*(Corrected 2026-08-15 by the independent review. This paragraph originally continued "The same issue names the replacement: **the live and completed split the navigator already applies is the one that matters here**" — and [[ISS-0089]] does not say that. **It is a code comment**, in `_design_groups` at `src/project_os_cockpit/cockpit.py:2872`, quoted here as if it were the issue's own reasoning. The first quotation is verbatim from ISS-0089 and its `TASK-0275` attribution holds; the withdrawal itself stands, and Edwin's words in that note's `source:` — "why do we need this design system section, why not just have these designs under completed?" — are the authority I should have cited. A citation that cannot be followed to what it claims is worse than none, because it looks checkable.)*

**Intent's other five nav groups do not get a counted roll-up on the page.** The proposal was to answer *"the page is called Designs but the view holds six groups"* by listing `Decisions 18 · Risks 7 · Releases 1 · Reference 3 · What this project is 10`. Those are the navigator's own groups, with the navigator's own counts, rendered three inches to the right of the navigator. That is [[ISS-0068]] — the overview's *Waiting on you*, removed for re-listing items that already had a home — and [[PHASE-030]] names it under *"what this phase must not do"*: *"a second list of the same items anywhere is the failure this phase inherits the lesson about."*

The naming mismatch is real, and it is fixed by the cheaper half: the page takes its heading from `VIEW_LABELS` like the other three, so it says *Intent* and the register carries a section head that says what it is **within** Intent.

Measured cost, had it been built the other way: reusing `_design_groups` to get honest counts is **70ms per landing fetch**, against a landing payload that costs 59ms — roughly doubling a call [[ISS-0166]] had just finished making fast, to restate what is already on screen.

## Evidence it is fixed

- Intent's page leads `1 needs you here.` over `DECIDE 1 ADR`, and the row is [[ADR-0026-Remote-Workspace-Transport]]. Badge and lead are one walk.
- `test_a_view_that_owes_nothing_says_so_in_its_own_words` extended from three quiet sentences to four, still all distinct.
- `test_the_landing_reads_the_top_bars_own_labels` now covers Intent: the page says *Intent — what this project is, and what it should look like*, not *Designs*.
- `test_one_row_grammar_across_every_landing` is new, and fails if a second row builder reappears.
- `test_the_register_is_not_split_by_role` is new, and fails if the `system`/`proposal` split ISS-0089 removed is reintroduced here.

## Independent review — 2026-08-15, `changes-requested`

Clean context: the reviewer started from this note, [[CHG-20260814-The-Intent-Landing-Joins-The-Other-Three]] and the diff at `da6a834`, never saw the authoring session's reasoning, and is not that session. `model:claude-opus-5`, same family as the author, which [[project-os-dev#ADR-0013]] does not gate on.

**The behaviour holds and I could not break it.** Four mutations against the four guards that carry the fix all fail correctly: putting the identity band back above the obligations fails `test_the_intent_landing_leads_with_what_its_badge_counts`; dropping the owed-row ternary fails `test_an_owed_design_opens_its_note_and_the_rest_open_the_bench`; replacing `statusChip` with grey prose fails `test_one_row_grammar_across_every_landing`; reading `d.role` again fails `test_the_register_is_not_split_by_role`. The correction about `accepted` being in the **active** band was checked against `statuses.py` and is right, and it is load-bearing exactly as this note says.

**Three things in the record do not hold**, all filed as [[ISS-0171]]:

1. *"`test_one_row_grammar_across_every_landing` is new, and fails if a second row builder reappears"* — it does not. A second builder emitting `<a href="#">` with a `preventDefault` and fresh class names, used for the settled fold, leaves all 43 tests green. The guard forbids the three **old** class-name literals, not a second grammar.
2. *"`test_the_landing_reads_the_top_bars_own_labels` now covers Intent: the page says Intent…, not Designs"* — it does not assert the page's heading text. `buildLandingHead('intent')` followed by `head.textContent = 'Designs'` is green. It does catch the likelier drift (a landing building its own `<h1>`), so the guard is useful and the sentence is wider than it.
3. The quotation attributed to [[ISS-0089]] — *"the live and completed split the navigator already applies is the one that matters here"* — **is not in ISS-0089**, or anywhere in `docs/` outside this note. The first quotation in that paragraph is verbatim and the `TASK-0275` attribution is supported by ISS-0089's own `fixed_by:`; the substance is supported by Edwin's words in that note's `source:` (*"why not just have these designs under completed?"*). So the withdrawal is right and its stated authority is not what it is stated to be.

The second withdrawal's citations were checked and hold: [[PHASE-030]] line 72 carries the quoted sentence verbatim, and [[ISS-0068]] is accurately characterised.

Also: `desktop/src/renderer/renderer.ts:5504` says *"Intent's badge read `1` (ADR-0022, `Decide`)"*. It was [[ADR-0026]]; ADR-0022 is `accepted` and owes nothing.
