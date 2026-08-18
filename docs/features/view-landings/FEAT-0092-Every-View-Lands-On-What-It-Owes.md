---
type: "[[feature]]"
id: FEAT-0092
aliases: ["FEAT-0092"]
title: "Every view lands on what it owes — the badge stops being a number you cannot act on, and four views stop opening on whatever you were reading"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["Edwin 2026-08-11, using the app: 'Not all views have their own landing desk/page, overview and intent have one but none of the others, I thought this part of this release?'", "Edwin 2026-08-11: 'The badges with numbers on the view icons are great but when selecting the view it is very unclear what they relate to (apart from the issues page) these items need to be immediately visible so the user can resolve them.'"]
goal: "Clicking a view opens that view's page, and the page leads with the items its badge counts — named, with their verb, and one click from being discharged."
requirements: []
tasks:
  - "[[TASK-0387-The-Landing-Payload]]"
  - "[[TASK-0388-The-Landing-Pages]]"
  - "[[TASK-0389-The-Badge-Leads-To-Its-Items]]"
related: ["[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ISS-0145]]", "[[ADR-0023]]"]

---

# Every view lands on what it owes

## Goal

**Two observations, one cause.** `MODES_WITH_VIRTUAL_LANDING` holds exactly `{overview, intent}` — so four of the six view buttons change the navigator and leave the centre pane on whatever you were reading. And the badges, which [[FEAT-0089]] made honest and complete, count things the view then never gathers: Issues works only because its *navigator* happens to open on `Needs triage`.

[[ADR-0020]]'s claim was that obligations live with their subject. They do — the marks are on the rows. What is missing is the **place the subject's view opens on**, so a person who sees `4` on a button can act on the four without hunting.

## Out of scope

- **The Library.** It carries no obligations and is a file browser; landing it on a page would put a summary in front of a tree, which is the thing people open the tree to avoid.
- **Any new obligation kind.** The registry is the source ([[FEAT-0089]]); this renders what it already knows, including `change` dropping out of it under [[ADR-0023]].
- **Discharging in bulk.** Each row leads to the note where its verb lives. A surface that approves five requirements at once is a different decision and nobody has asked for it.

## Acceptance

- [x] Clicking **Features**, **Issues** or **Tests** opens that view's own page; Overview and Intent keep theirs. Nothing lands on the note you were last reading. — evidence: driven in the live harness, `~features` / `~issues` / `~tests` in the footer after each click, including the return trip that exposed the route collision (user:edwin, 2026-08-11)
- [x] Each page **leads with what its badge counts**, grouped by kind and named with the registry's own verb — `Approve requirement`, `Triage issue`, `Run test` — never the word "items". — evidence: rendered `TRIAGE 8 ISSUES` over 8 rows, `Approve 1 requirement`; `test_every_row_carries_its_verb_and_a_destination` asserts no label contains "item" (user:edwin, 2026-08-11)
- [x] The number on the page and the number on the badge are **one computation**. A page that disagreed with its own button is the failure [[FEAT-0089]] exists to prevent. — evidence: `test_the_page_and_the_badge_are_one_computation` over every view; badge `8` and lead `8 need you here` observed together (user:edwin, 2026-08-11)
- [x] A view that owes nothing says so in its own words and shows the view's summary instead — not an empty panel, and not a `0`. — evidence: Tests renders `Nothing owed on tests.`; three distinct sentences asserted by `test_a_view_that_owes_nothing_says_so_in_its_own_words` (user:edwin, 2026-08-11)
- [x] Every owed row navigates to the note that carries its actuator, so the verb named on the page is the verb available when you arrive. — evidence: clicked the third row, landed on `docs/issues/ISS-0123-…md` with its `Triage / …` actuator row rendered (user:edwin, 2026-08-11)
- [x] A workspace opening on one of these views does not send the reader to `README.md`. — evidence: `MODES_WITH_VIRTUAL_LANDING` widened and re-pinned in `test_the_boot_path_does_not_race_a_virtual_landing_mode`, which fails if a landing mode is added without joining the boot guard (user:edwin, 2026-08-11)

## Notes

**Why this was not in [[REL-0001]].** It was never claimed: no feature in that release promises a landing page per view. Overview and Intent have theirs because [[FEAT-0071]] and [[FEAT-0087]] each built one for their own reasons. A reasonable expectation the release did not meet is worth recording as exactly that rather than as a regression.
