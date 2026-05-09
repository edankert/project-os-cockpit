---
type: instruction
id: INSTR-STATUSES
status: active
owner: group:maintainers
created: 2026-01-27
updated: 2026-01-27
tags: [instructions, statuses]
---

# Status taxonomies and transitions

This file defines the allowed `status` values and recommended transitions for each note type.

If a project needs different states, update this file and the templates in `../../docs/__templates__/`.

## `[[task]]`
- Allowed: `backlog`, `next`, `doing`, `blocked`, `done`
- Typical transitions:
  - `backlog` → `next` → `doing` → `done`
  - `doing` → `blocked` → `doing`

## `[[issue]]`
- Allowed: `triage`, `open`, `in-progress`, `blocked`, `fixed`, `closed`
- Typical transitions:
  - `triage` → `open` → `in-progress` → `fixed` → `closed`
  - `in-progress` → `blocked` → `in-progress`

## `[[feature]]`
- Allowed: `backlog`, `planned`, `in-progress`, `in-review`, `done`
- Typical transitions:
  - `backlog` → `planned` → `in-progress` → `in-review` → `done`

## `[[phase]]`
- Allowed: `planned`, `active`, `done`, `deferred`
- Typical transitions:
  - `planned` → `active` → `done`
  - `planned` → `deferred`

## `[[requirement]]`
- Allowed: `draft`, `approved`, `verified`, `retired`
- Typical transitions:
  - `draft` → `approved` → `verified`
  - `verified` → `retired`

## `[[risk]]`
- Allowed: `open`, `mitigating`, `monitoring`, `closed`
- Typical transitions:
  - `open` → `mitigating` → `monitoring` → `closed`

## `[[workflow]]`
- Allowed: `draft`, `active`, `deprecated`
- Typical transitions:
  - `draft` → `active` → `deprecated`

## `[[change]]`
- Allowed: `merged`, `reverted`

## `[[adr]]`
- Allowed: `proposed`, `accepted`, `rejected`, `superseded`
- Typical transitions:
  - `proposed` → `accepted`
  - `accepted` → `superseded`
  - `proposed` → `rejected`

## `[[test]]`
- Allowed: `draft`, `ready`, `passing`, `failing`, `blocked`, `deprecated`
- Typical transitions:
  - `draft` → `ready` → `passing`
  - `ready` → `failing` → `ready`
  - `ready` → `blocked` → `ready`
