---
type: "[[feature]]"
id: FEAT-0044
aliases: ["FEAT-0044"]
title: "A design system for every project with a UX, each read from its own CSS"
status: done
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user request 2026-07-28", "measurement:2026-07-28 fleet UX survey"]
goal: "Give every fleet project that has a UX a design system document of one consistent shape — and make each one a living page that reads that project's own stylesheets, so none of them can drift."
requirements: []
tasks:
  - "[[TASK-0230-Project-Stylesheet-Route]]"
  - "[[TASK-0231-Fleet-Design-System-Rollout]]"
release: ""
design: ["[[DES-0002-Cockpit-Design-System]]"]
related: ["[[FEAT-0042-Design-Bench]]", "[[ISS-0023-Status-Vocabulary-Drift]]"]

---

# A design system per UX, read from its own CSS

## The survey it starts from

Measured 2026-07-28 across 11 repos. **Six have a real UX; seven surfaces between them:**

| Project | Surface | Stylesheet | Today |
|---|---|---|---|
| project-os-cockpit | desktop app | `static/base.css`, `static/cockpit.css`, `renderer.css` | [[DES-0002]] + living style guide — **the exemplar** |
| your-applications.com | website | `public/css/style.css` | DES-0001 `draft`, `asset: ""` |
| your-health | app | 4 stylesheets | DES-0001 `draft`, `asset: ""` |
| your-sudoku | app | 4 stylesheets | DES-0001 `draft`, `asset: ""` |
| your-trainer | app | 12 stylesheets | DES-0001 `draft`, `asset: ""` |
| edankert.com | website | `public/css/style.css` | **nothing** |
| obsidian-supernote-sync | Obsidian plugin **+** web dashboard | `obsidian-plugin/styles.css`, `web-dashboard/src/index.css` | **nothing** |

**Excluded, with the reason:** `yourtrainer-mcp` (its only CSS is the vendored cockpit and venv packages — no UX), and `project-os` / `project-os-dev` / `project-os-bench` (tooling and templates; nothing renders).

The four existing notes are exactly where [[DES-0002]] was on the morning of 2026-07-28: `draft`, no artifact, a hand-typed palette table. That table is the thing this feature exists to stop writing.

## The constraint that shapes the whole feature

The cockpit's living style guide works because the sidecar serves its stylesheets at `/_static/` and `/_shell/`. **Every downstream stylesheet lives outside `docs/`** — `public/css/style.css`, `obsidian-plugin/styles.css` — and the design-asset route reaches nothing above the docs root.

So a downstream living page is impossible without a route that serves project-relative stylesheets. That route is [[TASK-0230]] and everything else depends on it.

## Acceptance

- Every project in the table above has a design note of the same shape, and an artifact that reads **that project's** stylesheets rather than restating them.
- No design note's palette table is load-bearing anywhere: the page is the checkable artifact, the table is commentary, and each note says which it is.
- The route is an **allow-list derived from the corpus** — a note declares the stylesheets it reads and the sidecar serves exactly those. Not a directory share, and not a hardcoded list.
- A project whose stylesheets are unreachable degrades visibly, the way the widget gallery does when the shell stylesheet is absent.
- `obsidian-supernote-sync` gets **one note with two sections** (Edwin, 2026-07-28): the plugin inherits its host's theme tokens and the dashboard owns its own, so the constraints differ but the product is one.

## Out of scope

- **Making the fleet look alike.** ADR-0008 in `your-applications.com` already makes that repo the upstream for the *family palette* shared by the your-* apps, checked by `check-family-palette.py`. This feature documents each system honestly; it does not homogenise them, and a site is not obliged to match an app.
- **Retrofitting `## Revisions` history.** Existing artifacts start their log where this feature lands ([[TASK-0220]]'s rule: no rescuing history by hand).


## Done 2026-07-30

[[TASK-0230]] (the route) and [[TASK-0231]] (the rollout) both landed. The per-repo table with measured token counts is in [[TASK-0231]].

Against this feature's acceptance:

- **Every project in the table has a note of the same shape, and an artifact that reads that project's stylesheets** — met, seven surfaces across six projects, including the three that needed read-time synthesis from Kotlin and Swift.
- **No palette table is load-bearing** — met, and the last three restatements were deleted 2026-07-30 rather than maintained.
- **The route is an allow-list derived from the corpus** — met by [[TASK-0230]].
- **Unreachable stylesheets degrade visibly** — met; `your-sudoku` and `your-trainer` show it in production, naming the tokens they cannot resolve instead of inventing swatches.
- **`obsidian-supernote-sync` is one note with two sections** — met.

**Not met, deliberately:** the six downstream notes are still `draft`. They leave `draft` when Edwin has looked at the pages, which is a human gate rather than outstanding work — the same bar [[DES-0002]] held itself to before going `implemented`.
