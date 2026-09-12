---
type: "[[task]]"
id: TASK-0611
aliases: ["TASK-0611"]
title: "Upstream in `~/Dev/repos/project-os`: the validator stops requiring an HTML artifact, the template and the authoring skill say Markdown with pictures first, and OBSIDIAN.md carries both the `__attachments__` convention and the rules for HTML in a note"
status: done
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[REQ-0065-A-Design-Is-Markdown-First]]"]
parent: "[[FEAT-0147-Pictures-Beside-The-Note]]"
effort: M
depends: []
blocks: ["[[TASK-0612-Convert-The-Largest-Embedded-Artifact]]", "[[TASK-0615-Remove-The-Bench]]"]
related: ["[[FEAT-0143-The-Fleet-Runs-One-Validator]]", "[[ADR-0043-How-A-Note-Marks-HTML-To-Render]]"]
tests: ["[[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]"]
tags: [task, upstream, validator]
---

# Upstream the markdown-first contract

## Why this is a blocker and not a documentation chore

`tools/scripts/validate-docs.py:1773` raises an **error** for any design note that is not `draft` and declares no `asset:`. Markdown-first makes that the normal case, so the first design written the new way fails CI — here and in every repo that syncs the validator. Nothing markdown-first can land anywhere until this is amended.

And `tools/skills/design-authoring/SKILL.md` opens with *"The artifact is HTML, and self-contained"*. Every agent in every repo reads that before authoring a design. If it is not flipped before the bench is removed, agents keep producing 4.6 MB pages for a surface that no longer exists.

## Definition of Done

Work is done in `~/Dev/repos/project-os` and committed there, then pulled here with `tools/scripts/sync-project-os.sh ../project-os`. **These files cannot be edited in this repo and pushed** — `tools/sync/MANIFEST.yaml` marks them `template`-owned, this repo has no generator, and `sync-project-os.sh` would report the local edit as divergence.

- [x] `DESIGN-ASSET` no longer errors on a non-`draft` design with no `asset:`. What replaces it is stated in the check's own docstring — the proposal is *"a design past `draft` must have something to look at"*: an `asset:`, **or** an image reference in the note body. Edwin decides whether the replacement check exists at all.
- [x] `DESIGN-ORPHAN` re-examined. It warns about any unclaimed `.html` under `docs/designs/`; once pages and images live beside notes, unclaimed files are ordinary. Either narrow it or retire it, with the reason in the docstring.
- [x] `docs/__templates__/design.md`: `asset:` optional and commented as such; the note body with images presented as the normal form; `## Regions` reduced or removed, since it exists to scaffold `data-design-region` annotation and that mechanism is being removed.
- [x] `tools/skills/design-authoring/SKILL.md`: Markdown with pictures first; a named list of when an HTML page is actually worth it; the region/token/viewport machinery cut back to what survives.
- [x] `tools/instructions/OBSIDIAN.md` gains an **Attachments** section: `__attachments__/` beside the note is where a picture goes, a **relative path** is how a note references it, and Obsidian's own `![[name.png]]` also resolves — by filename, vault-wide — which is why the fallback exists.
- [x] `tools/instructions/OBSIDIAN.md` gains an **HTML in a note** section. Edwin, 2026-09-12: *"Obsidan (as long as this is read by any LLM reading a project-os repo), we probably need to define Q2 there as well?"* — one file carries both conventions, because it is the file an agent reads for how notes are written. **Write this section only after Edwin settles [[ADR-0043-How-A-Note-Marks-HTML-To-Render]]**, which is still open; the rest of this task does not wait for it.
- [x] `docs/__templates__/SCHEMAS.md` updated for any `[[design]]` field change — it is `merge`-owned, so expect a hand-merge downstream.
- [x] Sync down here; `tools/scripts/sync-project-os.sh ../project-os` reports no divergence on any of these files.
- [x] Run `bash tools/scripts/validate-docs.sh` in **this** repo and in at least two others after the sync, since a validator change reaches all twelve.

## Notes

**Amended 2026-09-12.** The first version left "which instruction file owns `__attachments__`" as an open question, and scoped the instruction change to attachments alone. Edwin answered both: OBSIDIAN.md, and it carries the HTML-in-a-note rules too. His reason is worth keeping — OBSIDIAN.md is read by any LLM working in a project-os repo, so it is where a notation convention is actually found.

**Three repos' copies of `docs/__templates__/design.md` already carry a stub `## Revisions` entry** (measured 2026-09-12 across `articles`, `edankert.com`, `obsidian-supernote-sync`, `project-os-bench` and others — every template copy has one). They will be reported as diverged on sync and need a hand-merge rather than `--force`.

This is the one task in the phase whose blast radius is the whole fleet. Do it deliberately, in its own commit upstream, and re-run the validator in more than one repo before believing it.

## Outcome (2026-09-12)

Upstream commit `be6ffb3` in `~/Dev/repos/project-os`, synced down here.

**`DESIGN-ASSET` asks for something to look at.** An `asset:`, or an image embedded in the note — `design_shows_something` reads the body for a Markdown image or an Obsidian embed with an image suffix. A design past `draft` with neither is still an error, and a declared `asset:` must still resolve. Run against seven repos before committing: zero DESIGN errors anywhere, and the failures that remain in `your-health` and `edankert.com` are the pre-existing `PARENT-BACKLINK` / `SNAPSHOT-MEMBERSHIP` drift [[FEAT-0143-The-Fleet-Runs-One-Validator]] documented.

**`DESIGN-ORPHAN` counts a page a note links**, not only one it declares, so a page beside a note is not reported as a leftover.

**The template and the skill lead with pictures.** `docs/__templates__/design.md` has a `## The design` section holding images from `__attachments__/` and comments `asset:` as optional. `design-authoring/SKILL.md` was rewritten around it: the three reasons an HTML page earns its keep, and a closing section recording what was retired with the bench and the measurements behind it.

**`OBSIDIAN.md` carries both conventions** — Attachments, and HTML in a note with its four rules. `TRACEABILITY.md`'s `[[design]]` section was updated too; it stated the old rule in one line and would have contradicted the new one.

## Two things that did not go as the task assumed

**The validator did not arrive by sync.** `tools/scripts/validate-docs.py` is locally diverged in this repo — 1,583 diff lines of local checks — so `sync-project-os.sh` reported `LOCAL-CONTENT` and skipped it, as it is designed to. The change was hand-merged here and copied to `src/project_os_cockpit/validate_docs_bundled.py`, which a test pins byte-identical. **Anyone repeating this upstream should expect the same**: a validator change reaches this repo only by hand.

**The sync pulled another session's uncommitted upstream edit.** `tools/skills/independent-review/SKILL.md` was modified but not committed in `~/Dev/repos/project-os`, and `sync-project-os.sh` copies the working tree. It was reverted here. The sync also brought down several legitimately-committed template changes that had not been pulled before (`SNAPSHOT.md`, `HOOKS.md`, `install-git-hooks.sh`, the validate-docs workflow, `MANIFEST.yaml`, a new `pre-push` hook).

**Two planning notes were moved** while verifying: [[TST-0086-A-Note-Shows-The-Pictures-Beside-It]] and [[TST-0087-An-HTML-Page-Opens-In-The-Viewer]] were written under `docs/features/*/plan/tests/`, where the suite loader does not see them — `acceptance.load` reads `docs/tests/acceptance/` when it has no index, so the checks view counted 38 and the suite 36. They also listed `issues:`, which `section_of` reads as "this is a regression check" ([[ADR-0039]] decision 4); those links moved to `related:` with a comment in each note saying why. Four tests were failing on this before the move and pass after it.

Suite after the change: 2248 passed, 6 skipped, 1 failed — the known unrelated `test_release_evidence` case.
