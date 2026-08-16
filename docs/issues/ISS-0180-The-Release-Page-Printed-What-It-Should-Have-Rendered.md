---
type: "[[issue]]"
id: ISS-0180
aliases: ["ISS-0180"]
title: "The release page printed what it should have rendered — a known-issues table as pipe characters and a shipped release's features as raw `[[wikilinks]]` — and a release's content was one flat list rather than grouped by what each thing is"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: ["Edwin 2026-08-16: 'You didn't fix any of the actual page issues like the table and the feature links, for the completed features'", "Edwin 2026-08-16: 'can you please stop calling the acceptance tests suite'", "Edwin 2026-08-16: 'I would like the acceptance tests (and other documents, tests, issues etc …) to be accessible from the left pane. You can group the features and other such ticket types together?'"]
severity: medium
component: cockpit-server
parent: ""
related: ["[[ISS-0179-Six-From-Reading-The-Release-View]]", "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]"]
tests: []
---

# The release page printed what it should have rendered

## I fixed the note and not the page

[[ISS-0179]] fixed the *rendered note* — tables gained styling, the drifted wikilink resolved. Edwin was reporting the **release page**, which is a different surface built from a payload, and both defects were still there:

**The known-issues table was printed, not rendered.** `release_payload` returned the section as raw markdown and the page set it as `textContent` under `white-space: pre-wrap`, so a table displayed as a column of pipe characters. It is rendered server-side now, through the same markdown pipeline as everything else — so its wikilinks resolve through the same index too.

**A shipped release's features were raw frontmatter strings.** The frozen branch emitted `["[[FEAT-0085-BleHardening]]"]` verbatim while the *next* release's rows were fully resolved, so a completed release listed bracket-wrapped slugs with no titles and no links. Both branches resolve to id, title and path now.

The lesson is the one this phase keeps re-teaching: **fixing the thing I looked at is not fixing the thing that was reported.**

## A release's content is grouped by what it is

Edwin: *"I would like the acceptance tests (and other documents, tests, issues etc …) to be accessible from the left pane. You can group the features and other such ticket types together?"*

Each release now carries subgroups rather than one flat list where a play-store XML sat between a feature and a test:

```
REL-0012 · 2.1.6 · 2026-07-05
   Features · 1
   Issues · 2                 <- from `issues:` and the ISS-* in `related:`
   Acceptance tests · 3
   Documents · 2              <- the release note and its play-store listing
```

All of it was already in the record. The issues in particular were reachable from nowhere: a release note names what it closed and what it shipped around, and both are the reader's question.

## And it is not a "suite"

Edwin: *"can you please stop calling the acceptance tests suite. Just describe them as acceptance tests."* Every user-facing string now says so — the button, the empty states, the write refusals, the registry's own predicate.

## Two more from the same reading

**`Preparing` was in the Completed section again**, and for a new reason. `groupIsSettled([])` is **true** by design — an empty list has no unsettled member, and its docstring says so deliberately. Harmless while every group carried its rows directly; wrong the moment a release's content moved into subgroups, because `items` went empty and the whole group read as finished.

Edwin asked *"why is preparing in the completed section?"* twice. First because a row carried its feature's own status; then because there were **no rows to read at all**. One mistake underneath: asking the question of the wrong list. `allGroupItems` now flattens subgroups, and a guard forbids either caller going back to reading `items` alone.

**And there were two ways to the same release** — the group header opening the release page, and a `Release note` row underneath opening the raw note. Edwin: *"Keep only the top one, do not have a separate link underneath."* The row is gone; the header is the way in.

## Found while fixing

**A repo with nothing to release would have rendered a blank view.** Moving content into subgroups meant a group could have neither items nor subgroups, and `renderNavGroup` returns nothing for one of those. `articles` — no releases, nothing unshipped — would have shown an empty pane. It says *"Nothing unshipped"* instead.
