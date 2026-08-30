---
type: "[[issue]]"
id: ISS-0267
aliases: ["ISS-0267"]
title: "`~tests/<TST>/run` and `~accept/<FEAT>` are still evicted — the owned-pages table lists one page per view, and the Tests view has two others that a reader walks step by step"
status: triage
owner: user:edwin
created: 2026-08-30
updated: "2026-08-30"
severity: medium
component: ui
phase:
source: ["Independent review of 46d6593..c861414, 2026-08-30, model:claude-opus-5, fresh context"]
related: ["[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]", "[[TASK-0589-A-View-Knows-Which-Pages-It-Owns]]", "[[FEAT-0092-The-Views-Get-A-Page]]"]
tests: []
---

# The fix names one owned page and the view owns three

## What happens

[[ISS-0263]] states the rule correctly — *"a view with two pages was landed as though it had one"* — and then enumerates one page. `VIEW_OWNED_PAGES` is `{ tests: ['~checks'] }`, and `~checks` is not the only page the Tests view owns.

`renderTestRunPage` sets the mode itself, and says why in the source: *"The left pane stays the Tests navigator rather than becoming a queue. A run is one row of that list being walked, not a separate place."* So `~tests/<TST>/run` **is** the Tests view by the same argument `~checks` is. `onOwnedPage('tests', '~tests/TST-0075/run')` returns `false`.

`~accept/<FEAT>` — the acceptance runner, walked one criterion at a time — sets no mode at all, so it inherits whichever view opened it, normally `features`. `onOwnedPage('features', '~accept/FEAT-0011')` returns `false`.

Evaluated directly against the shipped predicate:

```
tests     ~checks                      onOwnedPage=true
tests     ~checks/tier/2               onOwnedPage=true
tests     ~checks/area/Monetization    onOwnedPage=true
tests     ~tests/TST-0075/run          onOwnedPage=false
features  ~accept/FEAT-0011            onOwnedPage=false
```

## Why it is the same defect and not a smaller one

The trigger ISS-0263 identifies is generic: *"anything that refreshes the navigator while `~checks` is open does it, including an edit made in another editor."* Both runner pages are open for as long as a person is working through them, and both end in a write — `POST /api/notes/test-run` at `finish`, `POST /api/notes/acceptance-run` on **Record run**. The write fires `file-changed`, `scheduleSoftReload` calls `loadWsNav`, and the reader is thrown to the view landing 150 ms later, taking the run summary and the issue draft the endpoint just returned with it.

## Expected

A view's owned-page table lists the pages the view actually claims. `tests: ['~checks', '~tests/']` needs care because `~tests/` is a prefix of the landing's own family, so the honest shape is probably an explicit list including the `/run` suffix, or the `startsWith('~release')` treatment Publication and Design already use.

`~accept/` needs a decision first: it belongs to a view (it is reached from a feature and is about a feature) but claims none, so it is evicted under every mode.

## Next Actions

- [ ] Decide which view owns `~accept/<FEAT>` and record it, rather than leaving it mode-less.
- [ ] Add the runner pages to `VIEW_OWNED_PAGES` and pin each with a guard that fails when the entry is removed (`B3` in [[ISS-0266]] shows that shape of guard does work).
