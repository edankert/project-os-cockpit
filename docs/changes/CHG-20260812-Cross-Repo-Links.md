---
type: "[[change]]"
id: CHG-20260812-Cross-Repo
title: "`[[project#ID]]` reaches a note in another project, and the cockpit follows it — plus the project id that had to exist first"
status: merged
date: 2026-08-12
owner: user:edwin
related: ["[[ADR-0024]]", "[[FEAT-0093]]", "[[ISS-0148]]", "[[ISS-0123]]", "[[ADR-0019]]"]
tags: [change]
---

# Cross-repo links

## What changed

**A project id exists.** `project.id` in `SNAPSHOT.yaml`, defaulting to the repo's directory name, on the server (`cockpit.project_id`) and on every workspace in the shell. Neither of the two things that looked like an id could be one: `project.name` is a display string carrying spaces and capitals (`Obsidian-Supernote Sync`, `Your Health`) and reads **`REPLACE ME`** in the template, and the shell's workspace `id` is `sha1(absolute path)` — machine-local, so it can never appear in a committed note.

**`[[project-os-dev#ADR-0011]]` renders as a link** in both of the two consumers `wikilinks.py` names — the markdown body and the frontmatter strip. `#`, not `/`, because what follows the separator is an id rather than a path segment ([[ADR-0024]], which also withdraws the argument for `/` made the day before).

**It carries data, not a URL.** A sidecar serves one repo and cannot resolve another; emitting an `href` it could not honour would be the surface asserting something it does not know. The link carries `data-project` and `data-note-id`, and the shell — which discovers every SNAPSHOT-bearing repo — does the lookup.

**Clicking it switches workspace and opens the note.** The two legs are in different processes, so the jump is parked across the switch and consumed when the arriving sidecar reports ready, before the default landing wins the race. `GET /api/cockpit/locate?id=` is the arriving sidecar's half.

**A project that is not on this machine is reported**, never a dead click: *"No project 'x' on this machine — ADR-0011 is not reachable from here."*

## Impact

- New: `GET /api/cockpit/locate?id=<NOTE-ID>` → `{id, project, found, rel, title}`.
- `Workspace` gains `projectId` (optional in the renderer's copy, so a shell that has not been relaunched degrades to "no such project" rather than crashing).
- **No existing link changes meaning.** `[[ADR-0011]]` is still this repo or broken; `[[README#Edit policy]]` is still an ordinary Obsidian heading link, which is what the strict id half of the pattern buys.

## Documentation Coverage (All Types Considered)

- features: new ([[FEAT-0093]] + TASK-0390/0391/0392)
- requirements: not-applicable
- tasks: new (three, all `done`)
- issues: updated ([[ISS-0123]] — it now carries the first two real cross-repo links in the fleet)
- tests: new (`tests/test_cross_repo_links.py`, 14 cases)
- workflows: not-applicable
- decisions: new ([[ADR-0024]])
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (counters, metrics)

## Follow-ups

- [ ] Upstream: the notation is a fleet convention, so `OBSIDIAN.md` and `TRACEABILITY.md` should carry it and the decision belongs in `project-os-dev` beside [[ADR-0019]].
- [ ] [[ISS-0148]] still holds the sweep question for the 47 existing citations, and the one-sentence `CONTEXT.md` note that covers them without rewriting any.
