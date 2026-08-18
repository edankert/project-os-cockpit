---
type: "[[issue]]"
id: ISS-0201
aliases: ["ISS-0201"]
title: "\"Walk\" and \"Run\" are two words for one act, and the release page still offers the whole suite instead of what is outstanding"
status: triage
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: ui
phase: "[[PHASE-999-Future]]"
related: ["[[TESTING-MODEL]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[FEAT-0116-A-Release-Can-Be-Finished]]"]
---

# Walk, run, and what the release page should show

Edwin, 2026-08-18: *"The current UX functionality feels wrong, why did you use the term walk/run? The release page shows all the clickable items again, it should probably now just show a list of unchecked/open acceptance tests and link to this?"*

## Two words, one act

The corpus uses **walk** for an acceptance test and **run** for an executable one, and the registry's verb for the `test` obligation is `Run`. That split made sense while they were different types. Under [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] they are one type on a scale, so the surface now has two words for the same act separated by a field the reader cannot see.

It shows up directly: the Tests view has a group called **`Needs a run`** which contains only *non-acceptance* manual tests, while the acceptance population — the thing a person actually walks — sits under `Tier 1/2/3` with no verb at all. A reader looking for "what do I have to do by hand" finds one of the two populations under a heading that names the other's verb.

## The release page

It renders the acceptance rows as clickable items again — a second copy of the suite, on a page whose job is to say **what stands between this release and shipping**. Since [[FEAT-0114]] the suite has its own view at `~checks`, so the release page is now duplicating a surface that did not exist when it was written.

Edwin's proposal, which reads correctly: **show the outstanding set and link to the walk.** The gate's number is already computed (`gate_payload`); what the page owes is the list behind it, not a re-render of all 579 rows.

## What would settle it

- [ ] One verb for one act, chosen deliberately, and applied to the registry, the group headings and the buttons.
- [ ] The release page shows unsettled Tier 1/2 rows only, each linking into `~checks` at that row — with the settled majority reachable but not rendered.
