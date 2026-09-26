---
type: "[[task]]"
id: TASK-0066
aliases: ["TASK-0066"]
title: "Document existing cockpit API contract (docs/references/COCKPIT-API.md)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0008"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0068]]"]
related: []
tests: []
---

# Document existing cockpit API contract

## Definition of Done
- [ ] `docs/references/COCKPIT-API.md` exists, with frontmatter
      `type: "[[reference]]"`.
- [ ] Every endpoint currently served by `server.py` is listed,
      grouped as: cockpit JSON API, SSE channel, health, terminal,
      HTML pages (mode 1 only), static assets.
- [ ] For each JSON endpoint: method, path, request shape (params /
      body), response shape (JSON keys), response headers, status
      codes, which clients consume it.
- [ ] Schema-versioning rule documented at the top.
- [ ] Mode-1 vs mode-3 expectations called out per endpoint where
      they differ (`/api/terminal`, `.cockpit/url` discovery file).

## Steps
- [ ] Inventory by reading `src/project_os_cockpit/server.py` route
      table + `src/project_os_cockpit/cockpit.py` payload shapes.
- [ ] Cross-reference `src/project_os_cockpit/static/cockpit.js`
      for which endpoints the browser client actually calls.
- [ ] Cross-reference `desktop/src/ipc/*.ts` for which endpoints
      the desktop shell calls.
- [ ] Cross-reference `src/project_os_cockpit/cli.py` for what
      the `cockpit` CLI hits.
- [ ] Draft the doc with one section per endpoint.

## Notes
This is the contract that PHASE-006 builds against. Keep it terse
and exact — the doc is read more than it's written. Where the
response shape is dynamic (e.g. `/api/cockpit/nav` shape depends
on `mode` param), document each variant.
