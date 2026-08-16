---
type: "[[issue]]"
id: ISS-0179
aliases: ["ISS-0179"]
title: "Six from reading the release view — the next release filed under Completed while shipped ones sorted as open, no dates, no acceptance tests or artifacts in the navigator, unstyled tables, a broken feature link, and a badge counting what the view no longer shows"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: ["Edwin 2026-08-16, reading the rebuilt Publication view"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[FEAT-0107-Publication-Is-A-List-Of-Releases]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[ISS-0173]]", "[[ISS-0174]]"]
tests: []
---

# Six from reading the release view

## 1. The ordering was exactly inverted

*"the current / next release is hidden at the end below all existing releases and in the completed releases section and completed releases are in the open release section at the top???"*

`groupIsSettled` folds a group whose every item is terminal. The next release's rows carried **each feature's own status** — and a next release is by definition full of `done` features — so the whole group read as finished and went to the `Completed` band. Shipped releases' rows carried **no status at all**, so they read as open and sorted to the top.

The status a row carries is its state **in this release**: unshipped work is `ready` from the release's point of view, and shipped work is `released`.

## 2. Releases carried no dates

*"Also releases need dates etc"*. `date:` was in the note and in the payload and on no label. `REL-0012 · 2.1.6 · 2026-07-05`, and the next release says what it accumulated since.

## 3-4. The acceptance tests and the release files were not in the navigator

*"The acceptance tests are not available in the left hand"* and *"the other release files are also not available there"*.

A release's content is not only its features — it is what verified it and what it published. Both were already in the record and reachable only from the page. Each release group now carries its features, the tests it names, and its artifacts; the next release also carries the **living** suite.

## 5. Every table in the desktop app was unstyled

*"The releases .md file does not render correctly … and the table"*.

`base.css` styles `.content table`. That class is the **browser cockpit's** wrapper; `#doc-view` carries `.doc-view` and never `.content`. So every table rendered in the desktop shell has been borderless and uncollapsed **since the native panes landed** — not a release-note problem at all. Now styled, and scrolling inside its own box rather than widening the pane, because a known-issues table carries a full sentence per cell.

## 6. A feature link that was a rename, not a bug

`REL-0012` cites `[[FEAT-0085-BleHardening]]`; the note is `FEAT-0085-BleReliabilityLayer`. The feature was renamed and the citation was not updated, so it rendered as a broken wikilink.

The **id** is the identity and the slug is decoration, so a wikilink whose id resolves now resolves — tried **last**, after every exact table, so an exact filename match still wins and this can never override one. Same family as [[ISS-0173]] and [[ISS-0162]]: the record said the right thing in a form the reader refused.

## 7. And the badge outlived what it counted

*"you have removed the commits and pushes from this page … if you remove it then it should no longer be included in the badge in the view icon."*

Right, and it is the sharper version of the point. [[ADR-0028]] routed the publication obligations to the `publication` view when that view was a **ladder** whose rungs were their subject's home. [[FEAT-0107]] made it a list of releases and the rungs went back to `~history` and the overview — where the Push control has always actually lived — and the badge did not follow.

A count on a button that opens a view not containing what it counts is worse than no count: it sends the reader somewhere the work is not. Both kinds are back on `overview`.

## Found while fixing

**A second name collision this phase.** `_first_link` already existed 1200 lines below the one added here and silently shadowed it, so every test row rendered its raw `[[…]]` string. `create_release` was the first. Renamed to `_wikilink_target`, which says what it does.
