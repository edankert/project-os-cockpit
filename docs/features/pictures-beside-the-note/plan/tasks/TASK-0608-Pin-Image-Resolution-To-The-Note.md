---
type: "[[task]]"
id: TASK-0608
aliases: ["TASK-0608"]
title: "A relative path is the convention, image resolution prefers the note's own folder and `__attachments__` beside it, and the fleet-wide filename search is documented as Obsidian's fallback rather than an accident"
status: done
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

- [x] `__attachments__` is first in `ATTACHMENT_DIR_NAMES` (`src/project_os_cockpit/index.py:49`) and the tuple's order is stated as the resolution preference, not incidental.
- [x] `Index.resolve_asset`'s final fleet-wide filename search carries two sentences: that it is a last resort and what it can get wrong, and **why it stays** — it is how Obsidian's own `![[plate-3.png]]` resolves, which is what a person gets by pasting a screenshot into a note.
- [x] A test fixture with the same filename in two places proves the nearer one wins.
- [x] A test proves an image in `__attachments__/` beside a note resolves, referenced both as `![](__attachments__/x.png)` — the stated convention — and as an Obsidian embed `![[x.png]]`, which reaches it through the fallback.

## Steps

- [x] Read `resolve_asset`, `_explicit_asset_candidates`, `_asset_matches` and `_best_asset_match` before changing anything; the ordering is spread across four functions.
- [x] Reorder and document; do not change behaviour beyond ordering.
- [x] Add the tests above to `tests/` beside the existing asset-resolution tests.

## Notes

The behaviour mostly exists already. Measured 2026-09-12: `ATTACHMENT_DIR_NAMES` has accepted `__attachments__` for months and **zero** such directories exist anywhere in the fleet, because the convention is documented nowhere. This task makes the code's preference explicit so the documentation written upstream ([[TASK-0611-Upstream-The-Markdown-First-Contract]]) is describing something real.

**Amended 2026-09-12.** The first version of this task left the fallback's future open and offered its removal as a one-liner. Edwin settled both halves: *"this needs to work in obsidian, so simply use the relative path???"* — relative paths are the convention — and the fallback is **kept**, because Obsidian writes `![[plate-3.png]]` when a user pastes an image and resolves it vault-wide by filename. Removing it would break the behaviour a person gets by pasting a screenshot, which is the likeliest way an image ever enters one of these repos.

So the corpus carries two spellings on purpose: an agent writes the relative path, a person pasting into Obsidian gets the wikilink, and both resolve. The code should say that, in those words, at the fallback.

## Outcome (2026-09-12)

**The order was already right; what was missing was saying so and proving it.** `resolve_asset` tries the explicit relative path beside the note, then `ATTACHMENT_DIR_NAMES` beside it, then the same path from the docs root, and only then the filename search across the tree — and `__attachments__` was already first in the tuple. No behaviour changed. The tuple now says the order is the convention, and `resolve_asset`'s docstring says what the last resort can get wrong and why it stays: Obsidian's `![[plate-3.png]]`, which is what a person gets by pasting, can only be found that way.

`tests/test_note_attachments.py` is new — there were **no asset-resolution tests at all** before this. Nine cases: the tuple's order, a picture in `__attachments__` by relative path, an Obsidian embed by bare filename, the nearer of two matches, an explicit path beating an attachment directory, and three refusals (a `.md`, a path climbing out, an external URL).

**Two things mutation testing caught**, both in the tests rather than the code:

- The first "nearer wins" case never reached the scoring it claimed to test. Each note had its own `__attachments__` copy, so both resolved a step earlier; dropping the proximity score left it green. A second case puts both pictures where only the fleet-wide search can find them, and that one dies when the score goes.
- Every test was building the index with `Index(docs)`, which indexes notes and **no assets** — `Index.build` is what walks the tree. Two tests passed anyway, for the same reason as above. The file now says this at the top, since it is a trap for the next person writing an asset test.
