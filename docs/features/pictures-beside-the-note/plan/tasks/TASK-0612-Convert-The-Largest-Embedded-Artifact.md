---
type: "[[task]]"
id: TASK-0612
aliases: ["TASK-0612"]
title: "Convert `your-health`'s 4.6 MB design page: 51 embedded images become files beside the note"
status: backlog
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]"]
parent: "[[FEAT-0147-Pictures-Beside-The-Note]]"
effort: S
depends: ["[[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]]", "[[TASK-0611-Upstream-The-Markdown-First-Contract]]"]
blocks: []
related: ["[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]"]
tests: ["[[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]"]
tags: [task, migration, cross-repo]
---

# Convert the largest embedded artifact

## Definition of Done

- [ ] `~/Dev/repos/your-health/docs/designs/DES-0002-recovery-and-food.html` is under 100 KB.
- [ ] Its 51 inline PNGs are files in `docs/designs/__attachments__/`, referenced by relative `src`.
- [ ] The page renders identically in the cockpit before and after — checked by eye, side by side, not asserted.
- [ ] Committed in `your-health`, in its own commit, with the reason in the message.
- [ ] If it is **not** converted, the reason is written into [[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]] and that issue stays open.

## Steps

- [ ] Extract, repoint, check by eye, commit in `your-health`. No further approval is needed — see below.
- [ ] Extract each `data:image/png;base64,…` to a file; name the files from the surrounding context, not `image-01.png`, so the folder is readable.
- [ ] Nine `## Revisions` entries exist on `DES-0002-Recovery-And-Food.md`. Add a tenth recording this conversion, per `tools/instructions/TRACEABILITY.md`.

## This task edits another repo's committed record, deliberately

`~/Dev/repos/your-health` is not this repo, and `tools/scripts/close-out-commit.sh` does not reach it. Rewriting a committed artifact there as part of **this** project's work is a departure from the usual rule that a change lives in the repo that owns it.

**Edwin approved it on 2026-09-12**, answering the question the first version of this task raised. The commit is made in `your-health`, in its own commit, and is not part of this repo's close-out commit. Its message names this task and says why the change came from another project.

## Notes

This is the proof that the convention works on a real case, which is why it is a task and not an afterthought. Measured 2026-09-12: the file is 4,607,604 bytes and `grep -c "data:image/png;base64"` returns 51.

The same repo already keeps 71 images under `docs/design/widgets-v2/` as plain sibling files with no note claiming them — so the pattern Edwin reaches for by hand is already "files on disk". This task makes the tool agree with him.
