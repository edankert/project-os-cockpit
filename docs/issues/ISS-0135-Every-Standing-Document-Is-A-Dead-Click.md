---
type: "[[issue]]"
id: ISS-0135
aliases: ["ISS-0135"]
title: "Every one of the eight standing documents is a dead click — the group emits `/README.md` where the convention is `/docs/README.md`, and `extractRel` drops exactly that shape on purpose"
status: triage
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["Edwin, 2026-08-11: 'The design view what this project is section its items do not bring up the pages when selected.'"]
severity: high
component: "cockpit-api"
parent: ""
related: ["[[FEAT-0091-The-Standing-Documents]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[ISS-0037]]", "[[ISS-0125]]"]
tests: []
---

# Every standing document is a dead click

## Problem

The Intent view opens on `What this project is` — the eight standing documents, the landing [[FEAT-0091]] built. **None of the eight can be opened.** Clicking a row does nothing.

`_standing_group` builds each item's url relative to the docs root and prefixes a bare slash:

```python
rel = res.paths[0].relative_to(docs_root).as_posix() if res.paths else ""
item = { ..., "url": f"/{rel}" if rel else None, ... }
```

which yields `/README.md`, `/GLOSSARY.md`, `/PHASES.md`. Every other nav group emits the docs-rooted form — the Library emits `/docs/README.md` for *the same file*. The renderer's `extractRel` then discards the bare form deliberately:

```ts
if (url.startsWith('/docs/')) return url.slice('/docs/'.length);
if (url.startsWith('~')) return url;
// NOT routed here: `/README.md` and the other top-level project files …
// Those rows stay dead clicks (ISS-0037) until the rel carries the
// disambiguator the url has.
return null;
```

With no rel, the row gets no `data-rel`, and the delegated click handler keys entirely off `data-rel`.

**The comment names the trap and the trap was walked into anyway.** [[ISS-0037]] is the same defect in the Library, and it is `fixed` — the Library now emits `/docs/README.md` *and* `~root/README.md` to disambiguate the repo-root file from the docs one. The standing group, written later, reintroduced the discarded shape in a new surface. It is a recurrence of a class, not a duplicate: different subject, different builder, and the fixed issue's guard never covered it.

**Why it is severity high despite being one character.** These eight documents are the project's answer to *"what is this?"*, and the view exists to make them reachable — [[FEAT-0091]]'s stated deliverable is visibility. A surface whose entire landing is unclickable fails its one job, silently, and looks fine in a screenshot.

## Repro

1. Open the Intent / design view.
2. Click any row under `What this project is` — README, GLOSSARY, PHASES, any of the eight.
3. Nothing happens.

## Expected

The row opens the document in the centre pane.

## Actual

Dead click. No navigation, no error, no status message.

## Evidence

- `src/project_os_cockpit/cockpit.py:2500` — `"url": f"/{rel}"`.
- `desktop/src/renderer/renderer.ts:8869` — `extractRel` returns `null` for the bare form, with the reason recorded.
- Live payload 2026-08-11, `mode=design`, group `standing`: `/README.md`, `/INDEX.md`, `/ARCHITECTURE.md`, `/GLOSSARY.md`, `/OWNERSHIP.md`, `/DESIGN.md`, `/STYLEGUIDE.md`, `/PHASES.md` — all eight.
- Same run, `mode=library`: `/docs/README.md` and `~root/README.md` — the convention, and the disambiguator.
- The files are real: `docs/README.md`, `docs/GLOSSARY.md`, `docs/PHASES.md` all exist.

## Next Actions

- [ ] Emit `/docs/{rel}` from `_standing_group`. One-line fix, server-side, no renderer change.
- [ ] A test that asserts every nav item url in every mode either starts with `/docs/`, starts with `~`, or is null — the sweep that turns this class of bug from recurring into impossible. This is the third time it has appeared ([[ISS-0037]], the Library rows it fixed, and now this).
