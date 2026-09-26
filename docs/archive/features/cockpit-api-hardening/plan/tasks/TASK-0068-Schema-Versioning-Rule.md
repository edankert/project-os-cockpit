---
type: "[[task]]"
id: TASK-0068
aliases: ["TASK-0068"]
title: "Codify schema-versioning rule + X-Cockpit-Schema header assertion test"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0008"
effort: ""
due: ""
depends: ["[[TASK-0066]]"]
blocks: []
related: []
tests: []
---

# Schema-versioning rule + header assertion

## Definition of Done
- [ ] `docs/references/COCKPIT-API.md` includes a "Schema versioning"
      section stating: any breaking change to a JSON endpoint bumps
      `cockpit.SCHEMA_VERSION`; clients refuse to render when their
      cached schema differs from the server's `X-Cockpit-Schema`
      header.
- [ ] Every JSON response (GET **and** POST) emits
      `X-Cockpit-Schema: <int>` matching `cockpit.SCHEMA_VERSION`.
- [ ] Test asserts the header is present + correctly valued on every
      JSON endpoint inventoried in TASK-0066.

## Steps
- [ ] Confirm `_respond_json` already emits the header for GETs;
      patch if any POST handler skips it.
- [ ] Add "Schema versioning" section to the contract doc.
- [ ] Add a parametrised pytest case iterating every JSON endpoint;
      assert 2xx response + `X-Cockpit-Schema` header.

## Notes
The point of this task is to make schema drift loud rather than
silent. Today only `_respond_json` emits the header; this task
verifies that the contract doc and the code agree, and gives us a
single test that breaks if either side regresses.
