---
type: "[[task]]"
id: TASK-0390
aliases: ["TASK-0390"]
title: "The project id — a stable name a note can carry"
status: done
parent: "[[FEAT-0093]]"
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
---

# The project id — a stable name a note can carry

`project.id` in `SNAPSHOT.yaml`, defaulting to the repo's directory name when absent.

**Neither of the two things that look like an id can be one.** Measured across the twelve repos on 2026-08-12:

- `project.name` is a *display* string — `Obsidian-Supernote Sync`, `Your Health`, `Your Trainer` carry spaces and capitals, and the template's still reads `REPLACE ME`.
- The shell's workspace `id` is `sha1(absolute path)[:16]` — machine-local by construction, so it can never appear in a note that gets committed.

The directory name is clean and unique in all twelve (`your-health`, `obsidian-supernote-sync`, `project-os`), which makes it the honest default. The explicit field exists for the case the default cannot cover: a repo that gets renamed or cloned to a different folder name would otherwise silently change identity, and every reference to it would break with no error anywhere.
