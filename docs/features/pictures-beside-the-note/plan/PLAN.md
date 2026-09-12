---
type: "[[plan]]"
title: "Plan — pictures beside the note"
status: done
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[FEAT-0147-Pictures-Beside-The-Note]]"]
implements: ["[[FEAT-0147-Pictures-Beside-The-Note]]"]
related: ["[[FEAT-0148-One-HTML-Viewer]]", "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"]
---

# Plan — pictures beside the note

## Delivery sequence

1. **[[ADR-0042-What-May-Be-Framed]] is accepted.** Nothing that widens a route starts before the rule exists. Edwin's decision.
2. **[[TASK-0611-Upstream-The-Markdown-First-Contract]]** — in `~/Dev/repos/project-os`: amend `DESIGN-ASSET`, flip `design-authoring/SKILL.md`, rework `docs/__templates__/design.md`, name `__attachments__` in an instruction file. Then sync down here. **Hard blocker on everything markdown-first.**
3. **[[TASK-0608-Pin-Image-Resolution-To-The-Note]]** — `index.py`: order, `__attachments__` first among the directory names, the fleet-wide search named as a last resort. Local, independent of step 2.
4. **[[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]]** — `server.py`: the reachability rule from ADR-0042, replacing the `claimed` set. Fixes [[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]. Needs step 1.
5. **[[TASK-0612-Convert-The-Largest-Embedded-Artifact]]** — `your-health` DES-0002: 51 base64 PNGs become files. Needs step 4 to be visible, and needs Edwin's go-ahead because it rewrites another repo's committed artifact.
6. **[[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]]** — the render marker, after [[ADR-0043-How-A-Note-Marks-HTML-To-Render]] is settled. Independent of the rest; can slip without blocking anything.

## Dependencies

- **Hard:** ADR-0042 before task 0609. The upstream validator change (task 0611) before any markdown-only design note exists anywhere in the fleet. ADR-0043 before task 0610.
- **Soft:** task 0608 before 0609 — resolution order and the reachable set share the same directory conventions, and doing them in the other order means writing the convention twice.
- **Cross-repo:** task 0611 touches `~/Dev/repos/project-os`; task 0612 touches `~/Dev/repos/your-health`. Neither is committed by this repo's close-out script. Each is its own commit in its own repo.

## Open questions

**Five of six were answered by Edwin on 2026-09-12.** They are kept here with their answers rather than deleted, because the answers are what the notes were rewritten against.

- **Which instruction file owns `__attachments__`?** — **`tools/instructions/OBSIDIAN.md`**, and it carries the HTML-in-a-note rules too: it is the file an agent reads for how notes are written.
- **Does the fleet-wide filename fallback stay?** — **Yes, and it is documented.** Obsidian writes `![[plate-3.png]]` when a user pastes an image and resolves it vault-wide by filename; removing the fallback would break what a person gets by pasting a screenshot. The authoring convention is the **relative path**.
- **How far does the conversion go?** — One artifact, `your-health` DES-0002, and it is **approved** ([[TASK-0612-Convert-The-Largest-Embedded-Artifact]]). The other 32 designs with an `asset:` are left alone.
- **Is there a rule about what may be framed?** — **No.** Any file inside the workspace's `docs/`, cross-repo included ([[ADR-0042-What-May-Be-Framed]], rewritten).
- **Does a design's ID open its note or a viewer?** — **The note** ([[TASK-0614-Links-Stop-Asking-For-The-Bench]]).

**Still open, and the only thing blocking [[TASK-0610-A-Note-Marks-A-Block-Of-HTML-To-Render]]:**

- **How does a note show HTML?** [[ADR-0043-How-A-Note-Marks-HTML-To-Render]] is with Edwin. The research moved the answer: Obsidian renders raw HTML in a note natively, and so does the cockpit's renderer — so a ` ```html render ` marker would render in the cockpit and show as **source** in Obsidian, which Edwin rejected outright. The likely decision is no marker at all, with raw HTML as the notation and four authoring constraints attached. Do not write the ADR, the OBSIDIAN.md section or the task against any of that until he confirms.
