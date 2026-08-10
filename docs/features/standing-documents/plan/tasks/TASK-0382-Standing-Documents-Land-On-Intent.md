---
type: "[[task]]"
id: TASK-0382
aliases: ["TASK-0382"]
title: "The Intent view opens on the standing documents, each showing when it was last confirmed"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[REQ-0033-Every-Project-Can-Say-What-It-Is]]"]
parent: "[[FEAT-0091-The-Standing-Documents]]"
effort: M
due: ""
depends: ["[[TASK-0380-The-Manifest-As-Data]]"]
blocks: []
related: ["[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]"]
tests: []
---

# Standing documents land on Intent

## Definition of Done
- [ ] The Intent view's landing is the standing set — the documents answering *what is this project*, in the order the manifest declares
- [ ] Each entry shows when it was last confirmed, and reads differently when stale, stubbed or missing
- [ ] A stale standing document is an obligation kind in [[FEAT-0089]]'s registry, owned by Intent and counted in its badge
- [ ] They are reachable here, not only through the Library file tree — closing the gap [[REQ-0025]] recorded
- [ ] The set is not listed anywhere else; Library keeps showing the *files*, which is a different question

## Steps
- [ ] Render the manifest as the Intent view's landing
- [ ] Register `standing document stale` as an obligation kind with Intent as owner
- [ ] Check against [[REQ-0025]]'s guard that nothing loses its only surface

## Notes
This is the "prominent place" Edwin asked for, and it also settles the empty-state question for the Intent view — the view about what the project *is* opens on the documents that say so. Two answers, one surface, which is why the landing is not a separate design decision.

**Not a second list.** Library shows these as files in a tree ([[ISS-0125]] keeps that overlap deliberately); Intent shows them as the project's own answer, with their freshness. One item, two addresses, on the boundary [[FEAT-0087]] already records.

Making staleness an obligation kind is what stops this being a decorative panel: it inherits the badge, and the badge is the thing that gets looked at.
