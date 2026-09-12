---
type: "[[feature]]"
id: FEAT-0147
aliases: ["FEAT-0147"]
title: "A picture is a file beside the note that shows it, and a design is Markdown with pictures by default"
status: done
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12, three messages in one thread"]
goal: "Let an agent put a picture in front of Edwin by writing a file and a line of Markdown — images in `__attachments__` beside the note, referenced from the note or from an HTML page, instead of pasted into a document as base64."
requirements:
  - "[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]"
  - "[[REQ-0065-A-Design-Is-Markdown-First]]"
tasks:
  - "[[TASK-0608-Pin-Image-Resolution-To-The-Note]]"
  - "[[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]]"
  - "[[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]]"
  - "[[TASK-0611-Upstream-The-Markdown-First-Contract]]"
  - "[[TASK-0612-Convert-The-Largest-Embedded-Artifact]]"
release: ""
issues:
  - "[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]"
acceptance_exception: ""
acceptance: ""
design: ""
related:
  - "[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]"
  - "[[ADR-0042-What-May-Be-Framed]]"
  - "[[ADR-0043-How-A-Note-Marks-HTML-To-Render]]"
  - "[[FEAT-0148-One-HTML-Viewer]]"
  - "[[REQ-0023-Design-Is-A-Project-Record]]"
tags: [feature, images, attachments, upstream]
---

# Pictures beside the note

## Goal

An agent that has a picture — a screenshot, a photo, a sketch, a rendered chart — should be able to show it to Edwin by saving a file and writing one line of Markdown. Today it cannot: the only surface that displays anything is the design bench, which frames an HTML file, and that file cannot load an image from disk. So pictures get base64-encoded into documents, and one of those documents is now 4.6 MB.

This feature makes the file on disk the normal case: `__attachments__/` beside the note, referenced from the note's body or from an HTML page in the same folder.

## Scope

### In scope

- Image resolution order pinned and documented: the path as written relative to the note, then `__attachments__` beside it, then the other accepted directory names, then the existing fleet-wide filename search as a **named** last resort.
- An HTML page in the record may reference a file beside it, under [[ADR-0042-What-May-Be-Framed]]. This is the fix for [[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]].
- A marker that says "render this block of HTML", decided by [[ADR-0043-How-A-Note-Marks-HTML-To-Render]].
- The upstream flip: template, authoring skill, validator (see below).
- One migration, as proof: `your-health` DES-0002, 4.6 MB and 51 inline PNGs, becomes a page with files beside it.

### Out of scope

- The viewer itself, and the bench's removal — [[FEAT-0148-One-HTML-Viewer]].
- Migrating every embedded artifact in the fleet. One is the proof; the rest are converted when someone edits them.
- Any change to what a design means as a record. [[REQ-0023-Design-Is-A-Project-Record]] is **not** superseded by this work and must not be. Read it: it requires that a design, its revisions and its verdicts live in the repo and stay readable without the tool that renders them. Markdown with sibling images satisfies that requirement *better* than a 4.6 MB HTML file does. Nothing in it mentions the bench.

## What must be upstreamed, and what stays here

The boundary is mechanical, not a judgement call: `tools/sync/MANIFEST.yaml` marks `tools/instructions/`, `tools/skills/`, `tools/scripts/` and `docs/__templates__/` as `template`-owned, with `docs/__templates__/SCHEMAS.md` as `merge`. A local edit to any of them shows up as divergence on the next `tools/scripts/sync-project-os.sh`. And this repo carries no generator, so those files **cannot** be edited here and pushed — the change is made in `~/Dev/repos/project-os` and synced back.

### Upstream — `~/Dev/repos/project-os`

| What changes | Upstream file | Why it is upstream |
| --- | --- | --- |
| The rule that a non-`draft` design must declare an `asset:` stops being an error; what replaces it is stated | `tools/scripts/validate-docs.py` (`DESIGN-ASSET`, ~line 1741) | Template-owned, and [[FEAT-0143-The-Fleet-Runs-One-Validator]] made every repo run this one file. A new or retired check is upstream by construction. |
| `DESIGN-ORPHAN` re-examined: an unclaimed `.html` beside a note stops being suspicious once pages and images live beside notes | same file, ~line 1783 | Same reason. |
| `asset:` becomes optional; the note body with images is presented as the normal form; `## Regions` stops being scaffolding for a mechanism being removed | `docs/__templates__/design.md` | Template-owned. Note that **three repos' copies already carry a stub `## Revisions` entry**, so the sync will report divergence on those and they need a hand-merge. |
| The authoring contract flips: not "The artifact is HTML, and self-contained" but Markdown with pictures first, HTML when Markdown will not do | `tools/skills/design-authoring/SKILL.md` | Template-owned. If this is not changed, every agent in every repo keeps being told the old way — which is why it must land **before** the bench is removed. |
| `__attachments__` is named as where a picture goes, and a **relative path** as how a note references it | `tools/instructions/OBSIDIAN.md` | Template-owned, and the convention is fleet-wide documentation, not a cockpit feature. **Checked 2026-09-12: no instruction file, skill or template mentions `__attachments__` anywhere** — it exists only in `src/project_os_cockpit/index.py:49`. Edwin picked this file on 2026-09-12. |
| The rules for **HTML inside a note** | `tools/instructions/OBSIDIAN.md` | Same file, by Edwin's decision the same day: *"Obsidan (as long as this is read by any LLM reading a project-os repo), we probably need to define Q2 there as well?"* It is the file an agent reads for how notes are written, so a notation convention belongs there rather than in a skill. Blocked on [[ADR-0043-How-A-Note-Marks-HTML-To-Render]], which is still open. |
| Any change to the `[[design]]` type's fields | `docs/__templates__/SCHEMAS.md` (`merge`) and upstream's own schema | This repo's CLAUDE.md records that the type was defined upstream first (project-os-dev FEAT-0019); a schema change follows the same route. |
| The notation for HTML in a note, once [[ADR-0043-How-A-Note-Marks-HTML-To-Render]] is settled | `tools/instructions/OBSIDIAN.md`, and whatever follows in `tools/skills/design-authoring/SKILL.md` | It is an authoring convention every repo's notes may use, not a cockpit-only syntax. **Still open with Edwin**; the research changed the recommendation, so do not write it until the ADR is settled. |

### Stays local — this repo

| What changes | File | Why it stays |
| --- | --- | --- |
| Image resolution order and the named last resort | `src/project_os_cockpit/index.py` | The cockpit's own render behaviour. |
| Serving a file beside a framed page | `src/project_os_cockpit/server.py` | This application's route table. |
| The renderer that honours the render-marker | `src/project_os_cockpit/renderer.py`, `desktop/src/renderer/renderer.ts` | Same. |
| [[ADR-0042-What-May-Be-Framed]] | `docs/decisions/` | A decision about **this application's** render surface, not about the record format. |
| The capability register and Deck's notification | `docs/reference/cockpit-capability-register.md` | Project-owned by the manifest, and required by CLAUDE.md in the same commit as any capability change. |

**Deck** (`~/Dev/repos/project-os-deck`) is not upstream and not downstream — it is a second consumer of this sidecar. It is affected and must be told, not synced: its adoption table at `docs/reference/cockpit-adoption.md` tracks the register rows this work changes. That notification is [[TASK-0617-Register-And-Deck]] under [[FEAT-0148-One-HTML-Viewer]].

### Ordering forced by the upstream boundary

1. **Upstream validator first.** Until `DESIGN-ASSET` is amended, the first markdown-only design fails CI in every fleet repo. [[TASK-0611-Upstream-The-Markdown-First-Contract]] is therefore a **hard blocker**, not a documentation chore.
2. **Upstream skill before the bench is removed.** Otherwise agents author 4.6 MB HTML pages for a surface that no longer exists.
3. Everything else in this feature can land locally in either order.

## Acceptance

- An image in `__attachments__` beside a note, referenced by relative path, shows in that note — in the browser cockpit, in the desktop shell, and in Obsidian.
- An HTML page in the record shows an image beside it, with a relative `src`.
- A path with `..` in it, or one resolving outside `docs_root`, is refused; everything inside it is served. There is no allowlist ([[ADR-0042-What-May-Be-Framed]]), so containment and the sandbox are the whole boundary.
- A design note with no `asset:` passes `bash tools/scripts/validate-docs.sh`.
- `your-health` DES-0002 is under 100 KB with its images as files.

## Links

- Requirements: [[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]], [[REQ-0065-A-Design-Is-Markdown-First]]
- Tasks: [[TASK-0608-Pin-Image-Resolution-To-The-Note]], [[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]], [[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]], [[TASK-0611-Upstream-The-Markdown-First-Contract]], [[TASK-0612-Convert-The-Largest-Embedded-Artifact]]
- Check: [[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]
- Repo paths: `src/project_os_cockpit/index.py`, `src/project_os_cockpit/server.py`, `src/project_os_cockpit/renderer.py`, `desktop/src/renderer/renderer.ts`
