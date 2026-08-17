---
type: "[[check]]"
id: CHK-0001
aliases: ["CHK-0001"]
title: "Serve a repo"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Render server and the browser front door"
section: "1.1"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0001]]", "[[FEAT-0002]]", "[[FEAT-0006]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.1.1 @ 7de1a86"
related: []
---

# Serve a repo

`python -m project_os_cockpit <repo>/docs` and open the printed URL. Expect: the three-pane cockpit, README rendered, wikilinks resolving to other notes. — 2026-08-10, `--port 8791`: `GET /` 200, `GET /api/cockpit/nav?mode=tests` 200 with four groups.
