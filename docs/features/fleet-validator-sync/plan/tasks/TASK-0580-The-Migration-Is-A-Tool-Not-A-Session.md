---
type: "[[task]]"
id: TASK-0580
aliases: ["TASK-0580"]
title: "The migration is a tool, not a session — force-sync the template files and reconcile the parent/tasks relationship from the notes that declare it"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0579"]
blocks: ["TASK-0581", "TASK-0582", "TASK-0583", "TASK-0584"]
related: []
tests: ["[[TST-0080]]"]
---

# The migration is a tool, not a session

## Definition of Done
- [x] `tools/scripts/migrate-fleet-validator.py <repo>` reconciles `PARENT-BACKLINK` and `SNAPSHOT-MEMBERSHIP` by writing each feature's `tasks:` to the set of tasks whose `parent:` names it.
- [x] It has a `--dry-run` that reports every write it would make and touches nothing.
- [x] It is **idempotent** — a second run reports zero changes.
- [x] It refuses to invent membership: a task naming a parent that does not exist is **reported**, not silently dropped or silently added.
- [x] Existing `tasks:` entries that no task claims are **reported and kept**, never removed, because removal is the direction that loses information. *(This box read "reported before removal" until independent review pointed out it described behaviour the tool deliberately does not have.)*
- [x] Guarded by [[TST-0080]] before it is pointed at a repo.

## Notes

Four repos and 1044 findings is past the size where hand-editing is honest. The reason this is a tool and not a session transcript is that it has to run a fifth time, on whichever repo drifts next.

`sync-project-os.py` already handles the file copy — the tool wraps it with `--force` for the template-owned validator rather than reimplementing the sync.
