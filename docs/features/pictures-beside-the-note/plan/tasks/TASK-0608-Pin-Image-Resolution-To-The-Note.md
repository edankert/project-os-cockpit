---
type: "[[task]]"
id: TASK-0608
aliases: ["TASK-0608"]
title: "A relative path is the convention, image resolution prefers the note's own folder and `__attachments__` beside it, and the fleet-wide filename search is documented as Obsidian's fallback rather than an accident"
status: backlog
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]"]
parent: "[[FEAT-0147-Pictures-Beside-The-Note]]"
effort: S
depends: []
blocks: ["[[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]]"]
related: ["[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]"]
tests: ["[[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]"]
tags: [task, images]
---

# Pin image resolution to the note

## Definition of Done

- [ ] `__attachments__` is first in `ATTACHMENT_DIR_NAMES` (`src/project_os_cockpit/index.py:49`) and the tuple's order is stated as the resolution preference, not incidental.
- [ ] `Index.resolve_asset`'s final fleet-wide filename search carries two sentences: that it is a last resort and what it can get wrong, and **why it stays** — it is how Obsidian's own `![[plate-3.png]]` resolves, which is what a person gets by pasting a screenshot into a note.
- [ ] A test fixture with the same filename in two places proves the nearer one wins.
- [ ] A test proves an image in `__attachments__/` beside a note resolves, referenced both as `![](__attachments__/x.png)` — the stated convention — and as an Obsidian embed `![[x.png]]`, which reaches it through the fallback.

## Steps

- [ ] Read `resolve_asset`, `_explicit_asset_candidates`, `_asset_matches` and `_best_asset_match` before changing anything; the ordering is spread across four functions.
- [ ] Reorder and document; do not change behaviour beyond ordering.
- [ ] Add the tests above to `tests/` beside the existing asset-resolution tests.

## Notes

The behaviour mostly exists already. Measured 2026-09-12: `ATTACHMENT_DIR_NAMES` has accepted `__attachments__` for months and **zero** such directories exist anywhere in the fleet, because the convention is documented nowhere. This task makes the code's preference explicit so the documentation written upstream ([[TASK-0611-Upstream-The-Markdown-First-Contract]]) is describing something real.

**Amended 2026-09-12.** The first version of this task left the fallback's future open and offered its removal as a one-liner. Edwin settled both halves: *"this needs to work in obsidian, so simply use the relative path???"* — relative paths are the convention — and the fallback is **kept**, because Obsidian writes `![[plate-3.png]]` when a user pastes an image and resolves it vault-wide by filename. Removing it would break the behaviour a person gets by pasting a screenshot, which is the likeliest way an image ever enters one of these repos.

So the corpus carries two spellings on purpose: an agent writes the relative path, a person pasting into Obsidian gets the wikilink, and both resolve. The code should say that, in those words, at the fallback.
