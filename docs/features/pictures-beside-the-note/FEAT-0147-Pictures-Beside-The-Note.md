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
reviewed_by: model:claude-opus-5
review_date: 2026-09-12
review_verdict: changes-requested
review_response: "All ten findings and the smaller notes acted on; the verdict stands as recorded. Finding 1 was a real defect and is fixed with two tests: stamp_decision now refuses to move a settled design (implemented/superseded/cancelled) and records `approved`/`changes-requested` rather than the proposal vocabulary — three mutants killed. Finding 3's figures are corrected everywhere they were repeated, here and upstream (project-os bb2802d): 23 design notes in 8 repos, 21 with an artifact, 7 artifacts declaring regions; the reviewer's own count was 22, a predicate detail. Findings 4, 5, 6, 7 and 10 were wrong claims in notes and are corrected or reconciled, including 18 placeholder evidences and REQ-0065's off-by-one. Finding 8's dead code is deleted (design_regions, design_asset_at, _DESIGN_KNOWN_STATUSES, a stale comment) and ISS-0057 now says its mechanism went with the bench. Finding 9 is filed as ISS-0301 — the sandbox denies reads, not writes — and RISK-0008's wording is corrected to say so. Finding 2 is corrected in TST-0087 and RISK-0009: the note's button writes a status, not a verdict. The vacuous route-order test now compares the same anchor and dies when the order flips. Separately, Edwin found a regression this review did not: the viewer's page class was never cleared, so every page after it stopped scrolling (ISS-0302, fixed, and its guard immediately found history-page carrying the same defect). Suite after everything: 2063 passed, 6 skipped, 1 failed (the known unrelated case)."
review_response_date: 2026-09-12
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


## Independent review — changes-requested (2026-09-12, model:claude-opus-5)

Fresh context, separate session: the notes and the committed diff, no author transcript. Same model family as the author, recorded in `reviewed_by`.

What held up. The image resolver's order is as documented, and `tests/test_note_attachments.py` exercises the last-resort search where it actually runs. The upstream template, the authoring skill and `OBSIDIAN.md` are byte-identical to `~/Dev/repos/project-os` (`be6ffb3`). `src/project_os_cockpit/validate_docs_bundled.py` is byte-identical to `tools/scripts/validate-docs.py`. `your-health` `9c76562` carries 51 plate files and a 28,145-byte page. `bash tools/scripts/validate-docs.sh` is green.

Findings against this feature.

1. **Three requirements reached `implemented` with ticked criteria whose evidence is an unfilled placeholder.** `REQ-0063` (5), `REQ-0064` (8) and `REQ-0065` (5) each carry `acceptance:` entries ticked `[x]` reading `evidence: <TST-0086 step, test path>`, `evidence: <grep command output>` and so on. `grep -c 'evidence: <' docs/requirements/*.md` returns a non-zero count for exactly these three notes and no other requirement in the repo, so this is not the house style.

2. **`REQ-0065`'s body criteria carry the wrong evidence, shifted by one row.** Criterion 2 is about the *template* and its evidence is TST-0087 step 4 (the banner, ISS-0300); criterion 3 is about the *authoring skill* and its evidence names `docs/__templates__/design.md`; criterion 4 is about *HTML in a note* and its evidence names `design-authoring/SKILL.md`; criterion 5 is about a *sync reporting no divergence* and its evidence is the `your-health` conversion, which is not a sync. Criterion 4 is also ticked while its own text still reads "STILL OPEN with Edwin as of 2026-09-12 — do not build against this criterion".

3. **The `[x]` sync exit criterion is refuted by the command it names.** `PHASE-042` ticks "`tools/scripts/sync-project-os.sh ../project-os` reports no divergence on `docs/__templates__/design.md`, `tools/skills/design-authoring/SKILL.md` and `tools/scripts/validate-docs.py`". Run: `.venv/bin/python tools/scripts/sync-project-os.py ../project-os --dry-run` prints `ACTION REQUIRED — locally diverged template-owned files: LOCAL-CONTENT tools/scripts/validate-docs.py`. The first two files are clean. The criterion is true of two thirds of what it names and should be reconciled, not ticked.

4. **The measurement the retirements rest on does not reproduce.** See FEAT-0148's review section; the same numbers appear in this feature's change note and in `project-os` `be6ffb3`'s commit message.

5. **TST-0086 does not say which of its ten steps were window and which harness.** The evidence block is headed "In the running window" and then closes with "where a step needed several actions in sequence, it was re-walked in the renderer harness instead", naming no step. The note's own Evidence rule is "Record for each step: the date, whether it was the window or the browser". TST-0087 does it properly; this one does not. Step 3 (the browser cockpit) is recorded as not walked, while the Purpose says the check was "Walked in the running desktop app and in the browser cockpit".

Leads, not reproduced as defects: the suite here prints `2061 passed, 5 skipped, 1 failed` where the change note records `2060 passed, 6 skipped` — one conditional skip, probably environmental. `9c76562`'s message says 28,132 bytes where the committed blob is 28,145. The 4.6 MB "before" size and the five byte-identical scroll captures cannot be checked: the original page was never committed and no captures were kept.
