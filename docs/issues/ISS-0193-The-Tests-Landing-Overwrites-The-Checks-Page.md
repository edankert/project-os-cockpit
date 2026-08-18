---
type: "[[issue]]"
id: ISS-0193
aliases: ["ISS-0193"]
title: "Opening the acceptance checks from any view but Tests lands on the Tests landing page instead — the view switch fires its own landing over the page that requested it"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: desktop-renderer
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
related: ["[[FEAT-0114-The-Suite-Is-A-View]]", "[[ISS-0190-The-Acceptance-Tests-Sit-Last-On-Both-Release-Surfaces]]", "[[ISS-0194-A-Virtual-Page-Never-Refreshes-The-Nav-Highlight]]"]
---

# The Tests landing overwrites the checks page

## What happens

Edwin, from use: *"Sometimes when selecting the acceptance tests in the left hand pane this brings me to the TST view but the acceptance tests are not selected."*

In the Publication view the left pane's first subgroup is the errand — confirmed live against `../your-trainer` at `GET /api/cockpit/nav?mode=publication`:

```
GROUP release-next | Preparing · 2.1.7
   SUB rel-tests | Acceptance tests · 60 unchecked
      row: 'Acceptance checks' -> url= ~checks
```

Clicking that row paints the checks page and then, a fetch later, **replaces it with the Tests landing page**.

## Why

`renderChecksPage` switches the navigator as a side effect (`desktop/src/renderer/renderer.ts:8268`):

```ts
if (currentNavMode !== 'tests') setNavMode('tests');
```

`setNavMode` calls `loadWsNav()`, whose first synchronous act is the [[FEAT-0092-Every-View-Lands-On-What-It-Owes]] view landing (`renderer.ts:10944`): `~tests` is in `VIEW_LANDING_RELS`, and the only guard is `currentRel !== '~tests'`. At that instant `currentRel` is still the rel you came *from* — the `~checks` branch assigns it only after `renderChecksPage()` resolves (`renderer.ts:1284-1293`). The guard passes, `navigateTo('~tests')` is kicked off, and its fetch lands after the checks page has painted.

**Not a race — an ordering defect.** `renderChecksPage` has already awaited its own fetch by the time it calls `setNavMode`; everything after that call is synchronous. So the landing navigation always starts second and always finishes last. From a non-Tests mode the outcome is deterministic: checks page, then Tests landing, `currentRel = '~tests'`.

The guard was written for a real case — *"reselecting a mode while a note is open is not a request to lose your place"* — and it only knows about the landing rel itself. `~checks` is a page **inside** the Tests view (the comment at `renderer.ts:1268` says so in as many words: *"a page rather than a nav mode … a ninth mode would put one corpus in two places"*), and the landing logic has no way to know that.

## The mechanism to fix it already exists

`suppressLandingOnce` (`renderer.ts:834-841`), built for exactly this shape and carrying its own history: *"This is the third time this exact shape has been got wrong here"* — [[ISS-0040-Design-Frame-Width-And-Boot-Race]] first, then the guard that named only `overview` while Review and Design inherited the bug. A jump that must beat an arriving landing **cannot win by being fast, so it suppresses, once**.

This is the fourth instance, and it is the first where the arriving landing belongs to the same view as the page being suppressed.

## Expected

Opening `~checks` from any view leaves the reader on the checks page, with the Tests navigator beside it.

## Scope

The renderer only. The nav payload is correct — `cockpit.py:4369` emits `~checks` deliberately, because the migration left no document to open (ADR-0030). The browser front door (`static/cockpit.js`) does not have this defect: it has no view landings.

## Next actions

- [ ] Suppress the landing across the mode switch in `renderChecksPage`, or teach the landing which virtual pages belong to which view — one map, not a special case per page. `~sweep/<FEAT>` will want the same answer.
- [ ] A guard that arrives at `~checks` from a non-Tests mode and asserts what the centre pane is showing **after** the landing would have fired. Asserting immediately would pass against the defect.

## Fixed 2026-08-18

`renderChecksPage` arms `suppressLandingOnce` **before** `setNavMode('tests')`, using the mechanism built for exactly this shape. Arming it afterwards would not work — `loadWsNav` has already read the flag by then — so `test_the_checks_page_suppresses_the_arriving_view_landing` asserts the *ordering*, not the flag.

This was the fourth instance of the shape, and the first where the arriving landing belonged to the same view as the page it overwrote.
