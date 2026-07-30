---
type: "[[issue]]"
id: ISS-0037
aliases: ["ISS-0037"]
title: "Library rows for top-level project files are dead clicks"
status: fixed
severity: low
phase: "[[PHASE-012-Attention-In-The-Strip]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["found while fixing [[ISS-0033]], 2026-07-28"]
related: ["[[ISS-0033-Identity-Band-Link-Is-Dead]]", "[[ISS-0036-Root-File-Shadowed-Docs-Note]]"]
fixed_by: []
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "changes-requested"
---

# The Library's root-file rows do nothing

## What

`_project_support_items` emits `url: "/README.md"` for the top-level project files, and has since FEAT-0010. `extractRel` returns `null` for that shape, so the row gets no `data-rel` and the delegated click handler — which keys entirely off `data-rel` — ignores it. Clicking README, ROADMAP or SECURITY in the Library does nothing, and has never done anything.

Pre-existing and out of scope for FEAT-0043; recorded rather than fixed.

## Why the obvious fix is wrong

Routing `/X.md` by stripping the slash was tried while closing [[ISS-0033]] and reverted. `/docs/README.md` and `/README.md` both reduce to the rel `README.md`, so two distinct Library rows — a real note and a project file — collapse onto one fetch, and whichever file the server prefers wins. That is [[ISS-0036]] relocated into the client.

## What it actually needs

The rel must carry the disambiguator the url already has. Options, in rough order of preference:

1. A `~root/<file>` virtual-page prefix, matching the mechanism `~design` and `~review` already use, routed explicitly by `navigateToInner`.
2. Keep the leading `/` through `navigateToInner` as an explicit "project root" marker, and stop the API from stripping it. Cheaper but relies on a distinction the API has historically treated as noise ("accepts both forms").

Not urgent: the files are reachable in the editor, and nothing in the cockpit sends a user to them except the identity band, which navigates directly and is unaffected.

## Fixed 2026-07-30 — option 1, and the ambiguity was on both sides

Option 1 taken (`~root/<file>`), and implementing it turned up that this note's diagnosis was half the story.

The note said `extractRel` returns `null` for `/README.md`. True — but **`/api/render` also could not tell the two apart.** Measured before fixing: `?path=README.md`, `?path=/README.md` and `?path=%2FREADME.md` all returned `docs/README.md` ("Docs structure"). The server strips the leading slash exactly as the client did, and its project-root fallback only fires when *no docs file of that name exists*. Since `docs/README.md` exists, the top-level README was unreachable through that endpoint at all.

So option 2 ("keep the leading `/` through `navigateToInner`") could never have worked without a server change either. The rel had nowhere to carry a disambiguator the server would honour.

**What landed:**

- `_project_root_tree_items` emits `~root/<file>`. The `~` prefix already survives `extractRel` — that carve-out exists because of [[ISS-0033]] — so the rows get a `data-rel` and the delegated handler sees them.
- The server gained `explicit_root`, the mirror of the `explicit_docs` flag that already existed: `root/README.md` resolves against the project root and **never falls through to docs**, because that fallthrough is what made them indistinguishable. An unknown or non-allowlisted file 404s rather than silently serving the note.
- The renderer routes `~root/X` through the ordinary markdown path, translating it to `root/X` for the request. Deliberately not its own virtual-page branch: it really is just a markdown render, and a branch would have had to duplicate the fragment, history, 404 and error handling.

**Verified in the app:** the Library's Docs tree shows `~root/README.md`, `~root/LLM_BRIEF.md`, `~root/ROADMAP.md`, `~root/SECURITY.md`; clicking README opens the **project** README (`h1` = "project-os-cockpit"), not the docs note ("Docs structure"). Over HTTP: `root/README.md` → "README", `docs/README.md` → "Docs structure", `root/NOPE.md` → 404.

Guarded by `test_root_file_rows_are_distinguishable_from_docs_notes`, mutation-verified by reverting the url to a bare `/{rel}`.

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — changes-requested

The server half is correct and I could not break it. Probed live: `?path=root/README.md` → the project README, `?path=README.md` and `?path=docs/README.md` → the docs note, `?path=root/../SNAPSHOT.yaml` → "path traversal blocked", `?path=root/SNAPSHOT.yaml` and `?path=root/CLAUDE.md` → "not an allowlisted project file", `?path=root/docs/README.md` → 404. The allowlist plus the `_is_under(candidate, project_root)` check leaves no escape, and an explicit root request never falls through to docs.

**But the fix is mode-3 only, and it regresses modes 1 and 2.** This note's diagnosis is the desktop renderer's `extractRel`. The web client has no `extractRel`: `static/cockpit.js`'s delegated handler passes the raw `href` to `isInternalNoteLink` and then `navigateTo`, which does `fetch(url)` for an HTML page. Measured against a sidecar on this repo:

```
GET /README.md         -> 200   <h1>project-os-cockpit</h1>   (the PROJECT readme — correct)
GET /docs/README.md    -> 200   <h1>Docs structure</h1>       (the docs note — correct)
GET /~root/README.md   -> 404
```

So in the browser client the old `url: "/README.md"` **worked**, and `~root/README.md` — which resolves relative and is not an HTTP route, exactly like `/~design` — throws `HTTP 404` out of `navigateTo`. `_project_root_tree_items` feeds `nav_payload`'s Docs tree, which both clients render, so all four rows changed for both and only one client was checked. "Verified in the app" and "Over HTTP" in the section above are the desktop app and the `/api/render` endpoint respectively; neither is the browser client's page route.

`test_root_file_rows_are_distinguishable_from_docs_notes` cannot see this: it asserts the url prefix, greps `renderer.ts` for two literals and `server.py` for one, and never touches `static/cockpit.js` or the page route. A guard that reads only the surface that was fixed is the failure mode ISS-0024 §2 recorded.

**Asked for:** either serve `~`-prefixed paths from the page route, or give the web client the same translation the desktop renderer got — and extend the guard to assert both clients resolve the row.
