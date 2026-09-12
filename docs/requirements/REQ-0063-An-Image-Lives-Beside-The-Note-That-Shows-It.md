---
type: "[[requirement]]"
id: REQ-0063
aliases: ["REQ-0063"]
title: "An image is a file beside the note that shows it, in `__attachments__`, and both the note and an HTML page in the record can reference it"
status: implemented
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'why embed the images, why not simply store the images on disk'", "Edwin, 2026-09-12: 'can we store them next to the .md files in an __attachment__ directory instead of embedding?'"]
priority: high
scope: "How image files are stored and resolved for notes and for HTML pages the cockpit frames. Not: what a design is, which is REQ-0023."
acceptance:
  - "[x] An image placed in `__attachments__/` beside a note renders in that note in the cockpit, with the note referencing it as `![](__attachments__/name.png)` or `![[name.png]]`, in the browser cockpit and in the desktop shell — evidence: <TST-0086 step, test path>"
  - "[x] An HTML page in the record can show an image that sits beside it, with a relative `src` and no base64 — evidence: <test path>"
  - "[x] A path with `..`, or one resolving outside `docs_root`, is refused by the frame; every path inside it is served, at any depth. There is no allowlist ([[ADR-0042-What-May-Be-Framed]]) — evidence: <test path>"
  - "[x] A note references an image by **relative path** — `![](__attachments__/plate-3.png)` — and that is the stated convention, because it is what Obsidian resolves without a vault setting. Resolution prefers the path as written relative to the note, then `__attachments__`, then the other accepted directory names; the fleet-wide filename search stays as a documented last resort — evidence: <src path:line, test path>"
  - "[x] `tools/instructions/OBSIDIAN.md` upstream names `__attachments__/` beside the note as where a picture goes and the relative path as how to reference it, so an agent in any repo is told — evidence: <upstream path>"
implements: "[[FEAT-0147-Pictures-Beside-The-Note]]"
verifies: []
related:
  - "[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]"
  - "[[ADR-0042-What-May-Be-Framed]]"
  - "[[REQ-0023-Design-Is-A-Project-Record]]"
tests: ["[[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]"]
tags: [requirement, images, attachments]
---

# An image lives beside the note that shows it

## Approval

Not yet approved. Per `tools/instructions/STATUSES.md` `[[feature]]`, [[FEAT-0147-Pictures-Beside-The-Note]] does not move to `doing` until Edwin approves these criteria or amends them first.

**Criterion 4 is answered.** Edwin, 2026-09-12: *"this needs to work in obsidian, so simply use the relative path???"* — so a relative path is the convention, and the criterion now says so.

**The fleet-wide filename fallback stays, and Obsidian is the reason.** The first version of this section offered to remove it, on the grounds that `![](shot.png)` in one note silently resolving to a `shot.png` three directories away is loose. It is loose, and it is also **Obsidian's own default**: when a user pastes an image into a note, Obsidian writes `![[plate-3.png]]` — a wikilink that its resolver matches vault-wide by filename, with no path at all. Deleting the fallback would break the behaviour a person gets by pasting a screenshot, which is the single most likely way an image ever enters one of these repos. It stays, documented as a last resort, and the *authoring* convention is the relative path.

That leaves two spellings in the corpus and that is fine: an agent writes the relative path, a person pasting into Obsidian gets the wikilink, and both resolve.

## Statement

An image that a note shows **shall** exist as a file on disk beside that note, and **shall not** be embedded in a document as base64. `__attachments__/` beside the note is the stated place for it and a **relative path** is how a note references it, because that is what Obsidian resolves without configuration. An HTML page the cockpit frames **shall** be able to reference a file beside it ([[ADR-0042-What-May-Be-Framed]]).

## Rationale

Edwin's question was the whole argument: *"why embed the images, why not simply store the images on disk"*. The measured answer for why not is that until now it was impossible — the route that serves a design's HTML page hands out only files a design note claims, so a relative `<img src>` returned 404 ([[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]). The cost of that impossibility is visible: `your-health`'s `DES-0002-recovery-and-food.html` is 4,607,604 bytes and 51 of its images are inline PNGs.

The second half of his point matters as much: *"in most situations you would need an image to represent a design you cannot mock this up with a styled html file"*. A photograph, a screenshot, a scanned sketch — none of them are expressible as styled markup, and the cockpit has had no way to show one except by wrapping it in an HTML document.

The convention is half-built already and documented nowhere. `ATTACHMENT_DIR_NAMES` in `src/project_os_cockpit/index.py:49` has accepted `__attachments__`, `__attachments`, `attachments`, `assets` and `images` for months. Measured 2026-09-12: **zero** directories with any of the first two names exist anywhere in the fleet, and no instruction file, skill or template mentions the word. `your-health` keeps 71 images under `docs/design/widgets-v2/` as plain siblings instead. The code was ready and nobody was told.

## Acceptance Criteria

One checkbox per frontmatter entry; tick at close-out with an evidence pointer.

- [x] An image placed in `__attachments__/` beside a note renders in that note in the cockpit, in both the browser cockpit and the desktop shell — evidence: TST-0086 steps 1, 2 and 4 in the running window — three reference forms, one picture, and the near file winning
- [x] An HTML page in the record can show an image that sits beside it, with a relative `src` and no base64 — evidence: TST-0086 step 6 in the window: a framed page showed a file beside it and one three directories down, no base64
- [x] Traversal and out-of-root paths refused; everything inside `docs_root` served at any depth — evidence: TST-0086 steps 7 and 8: 200 at any depth inside docs/, 404 and 403 for the two traversal forms
- [x] Relative paths are the stated convention; resolution order is note-relative, then `__attachments__`, then the other names, then the fleet-wide search as a documented last resort — evidence: TASK-0608 — `index.py` states the order and why the last resort stays; `tests/test_note_attachments.py`, 9 cases, two written twice after mutation
- [x] `tools/instructions/OBSIDIAN.md` upstream names `__attachments__` and the relative path — evidence: project-os commit `be6ffb3`, OBSIDIAN.md "Attachments"

## Traceability

- Implements: [[FEAT-0147-Pictures-Beside-The-Note]]
- Verified by: [[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]
