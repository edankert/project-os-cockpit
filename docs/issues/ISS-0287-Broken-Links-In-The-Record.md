---
type: "[[issue]]"
id: ISS-0287
aliases: ["ISS-0287"]
title: "25 wikilinks in the record resolve to nothing and three task notes are zero bytes — the weekly link-check only looks at external URLs and the validator only checks frontmatter relationships, so nothing has ever read a link in a note's body"
status: fixed
phase: "[[PHASE-015-Phase-Hygiene]]"
owner: user:edwin
created: 2026-09-07
updated: 2026-09-07
source: ["Edwin, 2026-09-07: 'In that case, can you make sure they are all fixed because many are failing atm.'"]
severity: medium
component: docs
parent: ""
related: ["[[ISS-0162-The-Bare-Upstream-Citations-Still-Resolve-To-Nothing]]", "[[ISS-0078-Claude-Md-Named-A-Directory-That-Never-Existed]]", "[[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]]"]
tests: []
---

# Broken links in the record

## Problem

Links in note bodies resolve to nothing, and every one of them renders in the cockpit as a `broken-wikilink` span. Nothing checks them: the weekly `link-check` workflow reads external URLs only, and `validate-docs.py` validates frontmatter relationships — `parent:`, `covers:`, membership — never a link in prose.

> [!quote] As reported — 2026-09-07 (user:edwin)
> In that case, can you make sure they are all fixed because many are failing atm.

## What is actually broken, measured

Three populations, and only the first was being watched.

| population | count | checked by |
| --- | --- | --- |
| external URLs (`http(s)://`) | 28 unique, **0 broken** | `link-check` workflow, weekly |
| wikilinks in note bodies | **25 broken**, 18 distinct targets | nothing |
| relative Markdown links | **0 broken** | nothing |

**The external half is clean.** Every real URL returns 200; the only non-200 results are `localhost` and placeholder examples written into prose (`http://127.0.0.1:<port`, `http://192.168.x.x`, `https://…`). The weekly run agrees — 43 successful, 0 errors, most recently 2026-09-07 06:00 UTC.

**Count the way the renderer counts, and the first two counts were both wrong.** A pass over raw text found 232 unresolved `[[…]]` occurrences: wrong, because 206 sit inside fenced blocks or inline code, where Markdown never makes a link. They are notes *about* the syntax — `[[FEAT-...]]`, `[[ISS-…]]`, `[[CHK-*]]` — written correctly.

Stripping code **line by line** then gave 26: also wrong, by one. An inline span may wrap across a line break, and a per-line pass pairs the stray backticks either side of the break into a span that was never opened — which reported the correctly backticked ``[[X]]`` in `docs/references/COCKPIT-API.md` as broken. Stripping over the whole document gives **25**, and that is the number of links a reader could click and get nothing.

The same correction applies to the relative links. The first scan said 7; all seven are `![Alt](./image.png)`-style examples inside fenced blocks, documenting the syntax the renderer supports. **None were broken.**

## The 25, by cause

**Three task notes are zero bytes** (4 links). `TASK-0182`, `TASK-0183` and `TASK-0187` exist as filenames and hold nothing — no frontmatter, no body, 0 bytes since 21–22 July. So every citation of them dangles, and the notes are absent from the snapshot, the navigator and every count. Their work landed: `git log` shows the commits that delivered them.

**Four point at a note under a different name** (8 links). `[[CHG-20260812]]` and `[[CHG-20260730]]` are dates without the title the filename carries; `[[PHASE-0002]]` is the four-digit id the project stopped using; `[[reference/HOSTED-COCKPIT]]` names a directory that is called `references/`.

**Eight name a real file the resolver cannot see** (10 links). `[[CLAUDE]]`, `[[INTENT]]`, `[[LIFECYCLE]]`, `[[STATUSES.md]]`, `[[TESTING]]`, `[[independent-review]]` and `[[PHASES.md]]` are all real files — at the repository root, under `tools/instructions/` or under `tools/skills/`. The resolver walks `docs/` and nothing else, so a wikilink is the wrong form for them however the file is spelled.

**Two are prose that happened to be bracketed** (2 links). `[[ADR]]` and `[[ISS-*]]` are placeholders that escaped the backticks their neighbours have.

**One cites a note in another repository** (1 link). `[[TASK-0780]]` is `your-trainer`'s; the cross-repo form `project#ID` exists for exactly this ([[FEAT-0093]]).

## Why nothing caught it

`validate-docs.py` is thorough about the *graph* — a task's `parent:`, the backlink, snapshot membership — and reads no link in a body. The `link-check` workflow was written for external URLs and says so in its own first comment. So the population that a reader actually clicks through, 7,078 live wikilinks in `docs/`, has never been checked by anything.

[[ISS-0162]] fixed 48 bare upstream citations by hand in August and is `fixed`; nine more have appeared since. That is the shape of a defect with no guard: it is repaired and it returns.

## Fix

1. Restore the three empty notes from what their commits actually did, marked as reconstructed — never invented.
2. Repoint the mistargeted links to the names the notes have.
3. Turn the file references outside `docs/` into inline code carrying the real path, and backtick the three placeholders.
4. `[[TASK-0780]]` becomes a cross-repo reference.
6. **Add the guard**, in `tests/` rather than in `tools/scripts/validate-docs.py`: that file is template-owned (`tools/sync/MANIFEST.yaml` lists `tools/scripts/` as `template`), so a check added there would report as drift on the next sync. The same reasoning that put the `review_response` rule in `CLAUDE.md`.

## Risk scan

No trigger applies: no dependency, env var, path or contract changes. The guard reads files the suite already reads.

## Done

Zero unresolved wikilinks across 7,076 live ones, zero broken relative links, zero zero-byte notes.

- [x] **TASK-0182, TASK-0183 and TASK-0187 restored** from their delivering commits (`15d732c`, `3536687`) and the issues they closed, each carrying a line saying it was reconstructed and on what date. Nothing was invented: where no test note existed, the note says so rather than claiming one. Their `parent:` backlinks and snapshot membership went in with them, which is what `PARENT-BACKLINK` and `SNAPSHOT-MEMBERSHIP` then asked for.
- [x] **22 links repointed or re-formed.** `[[CHG-20260812]]` → `[[CHG-20260812-Cross-Repo-Links]]`; `[[CHG-20260730]]` → `[[CHG-20260730-Two-Features-Closed]]` (both citations are about that note's two closed features); `[[PHASE-0002]]` → `[[project-os-dev#PHASE-0002]]`, since both sentences already say *upstream*; `[[TASK-0780]]` → `[[your-trainer#TASK-0780]]`; `[[reference/HOSTED-COCKPIT]]` → `[[HOSTED-COCKPIT]]`, the directory being `references/`; `[[PHASES.md]]` → `[[PHASES]]`, the extension being what stopped it.
- [x] **The files outside `docs/` became inline code carrying their real path** — `CLAUDE.md`, `INTENT.md`, `tools/instructions/LIFECYCLE.md`, `tools/instructions/STATUSES.md`, `tools/instructions/TESTING.md`, `tools/skills/independent-review/SKILL.md`. A wikilink is the wrong form for them however they are spelled: the resolver walks `docs/` and nothing else, so making these resolve would mean widening what the cockpit serves, which is a security boundary and not a typo.
- [x] **The guard is `tests/test_record_links.py`** — three tests: every wikilink resolves, every relative link points at a file, no note is zero bytes. Each was mutation-checked by planting the defect it describes and watching it fail.

## Next Actions

- [ ] Propose the wikilink check upstream, so `validate-docs.py` carries it for every repo in the fleet rather than this one having a private copy.
