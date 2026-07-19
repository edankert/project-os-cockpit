---
type: "[[task]]"
id: TASK-0106
aliases: ["TASK-0106"]
title: "Manual add via directory picker"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
parent: "FEAT-0016"
---

# Manual add via directory picker

## Definition of Done
- [ ] Rail `+` opens a native directory picker.
- [ ] If selected dir has `SNAPSHOT.yaml`, add as single workspace.
- [ ] Else walk descendants; if any `SNAPSHOT.yaml`-bearing dirs
      are found, confirm with the user (count + list preview) and
      add all on confirm.
- [ ] Duplicates (by id = sha1 of resolved path) are silently
      skipped, surfaced in a status-bar message.
- [ ] Auto-discovery on first launch is removed.
