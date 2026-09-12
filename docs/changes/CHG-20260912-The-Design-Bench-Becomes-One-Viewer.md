---
type: "[[change]]"
id: CHG-20260912-The-Design-Bench-Becomes-One-Viewer
aliases: ["CHG-20260912-The-Design-Bench-Becomes-One-Viewer"]
title: "The design bench is removed and replaced by one viewer that frames any file; a design is Markdown with pictures, and its pictures live beside it"
status: merged
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'html viewer vs bench, I don't think the current bench provides much ... so I would remove it and instead have a generic html viewer, if we need side by side comparisons of versions then we need the same for .md files but let's then implement that in the future.'", "Edwin, 2026-09-12: 'can we store them next to the .md files in an __attachment__ directory instead of embedding?'"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/server.py", "src/project_os_cockpit/cockpit.py", "src/project_os_cockpit/note_writes.py", "src/project_os_cockpit/review.py", "src/project_os_cockpit/index.py", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/deep-link.ts", "desktop/src/renderer/renderer.css", "docs/reference/cockpit-capability-register.md", "~/Dev/repos/project-os (tools/scripts/validate-docs.py, docs/__templates__/design.md, tools/skills/design-authoring/SKILL.md, tools/instructions/OBSIDIAN.md, tools/instructions/TRACEABILITY.md)", "~/Dev/repos/your-health (docs/designs/DES-0002)"]
issues: ["[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]", "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]"]
features: ["[[FEAT-0147-Pictures-Beside-The-Note]]", "[[FEAT-0148-One-HTML-Viewer]]"]
requirements: ["[[REQ-0063-An-Image-Lives-Beside-The-Note-That-Shows-It]]", "[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]", "[[REQ-0065-A-Design-Is-Markdown-First]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ADR-0042-What-May-Be-Framed]]", "[[ADR-0043-How-A-Note-Marks-HTML-To-Render]]", "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]", "[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]", "[[FEAT-0042-Design-Bench]]", "[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]", "[[CHG-20260911-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
---

# The design bench becomes one viewer

## Summary

**A design is now a note with pictures in it.** Put the images in `__attachments__/` beside the note, reference them with a relative path, and they render in the cockpit, in Obsidian and on GitHub. No HTML file, no `asset:`, no separate surface.

**The design bench is gone.** In its place is one viewer, `~view/<rel>`, that frames any file inside a workspace's `docs/` — for a note of any type, and across workspaces. A design that still has an HTML page opens it there.

The bench framed one thing: an artifact a design note claimed in `asset:`. Around it sat a review workflow — revisions, region-anchored comments, variants, a verdict bound to the revision it judged. Measured across thirteen repos before removing it: **33 of 47 design notes declared an artifact and 6 carried real revision entries, while 24 artifacts declared comment regions and 12 comments existed, all on one note from one reviewer in one pass; one note used `## Variant` and `chosen_variant` was set on none.** The frame was the feature; the rest was machinery for a workflow nobody ran.

## What a person sees

- A design note shows its pictures, in the reader and in Obsidian. A design with no HTML page **says nothing about it** — it used to say "This design has no artifact yet", which called the normal shape unfinished.
- A design that has a page says so and offers to open it. The page opens in the viewer, at `~view/<rel>`.
- `~design/<ID>` opens the design's **note**. So does a `cockpit://` link or a cross-repo link naming a design's ID — like every other ID.
- Accept and Decline are still on a design note, and still write the same frontmatter. They were never the bench's; only the endpoint behind them was.
- The Intent view still lists every design.
- A framed page can show an image file beside it. Before, it could not, which is why `your-health`'s DES-0002 was a 4.6 MB file carrying 51 base64 PNGs. It is now 28 KB with its plates in `__attachments__/`, pixel-identical at five scroll positions.

## What changed

**Gone from the sidecar:** `/api/design/verdict`, `/api/design/offer-review`, `/api/design/comment`, `/api/design/capture`, `/api/notes/choose-variant`, `/api/cockpit/design-revisions/`, `/api/cockpit/design-comments/` and `/design-asset-at/`. `/design-asset/<rel>` is now `/framed/<rel>`, and serves any file resolving inside `docs/` ([[ADR-0042-What-May-Be-Framed]]). `/api/cockpit/designs` stays — it is the register the Intent view is built from.

**Gone from the modules behind them:** `design_comments_payload`, `design_note_digest` and `design_revisions_payload` (`cockpit.py`); `append_design_comment`, `read_design_comments`, `stamp_design_verdict` and `stamp_chosen_variant` (`note_writes.py`); `resolve_anchor` (`review.py`); the whole of `design_tokens.py`, whose palette-parity contract the authoring skill retired.

**Gone from the shell:** the `~design/<ID>` page, its header and ID chip, the revision rail and compare view, the variant strip with its Choose button and ADR offer, `Ask for review`, the viewport presets and the sidebar.

**Changed rather than removed:** the review desk still routes a design away from the proposal path — that path stamps `plan-accepted` and rejects by writing `cancelled` onto a design that may be `implemented`, which is [[ISS-0056]] — but its buttons now post to `/api/notes/decide`, whose vocabulary already knows a design accepts to `accepted` and declines to `cancelled`.

**Upstream, in `~/Dev/repos/project-os`:** `DESIGN-ASSET` asks for *something to look at* — an `asset:` **or** an image in the note — instead of requiring an HTML file; `DESIGN-ORPHAN` counts a page a note links, not only one it declares; the design template leads with pictures; `design-authoring/SKILL.md` is rewritten around them; and `OBSIDIAN.md` gains the `__attachments__` convention and the four rules for HTML in a note.

## What was given up, deliberately

- **A design verdict no longer names the revision it judged** ([[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]). Edwin: *"Drop the binding for now!"*. An approval given to one revision can silently cover a later one, which is [[ISS-0056]]'s hazard. Markdown-first weakened that protection anyway — a design with no artifact has no artifact revision to bind to — and the way back is one task: a verdict naming the commit of whatever the design **is**.
- **Region-anchored comments.** The sixteen already written stay in their notes as Markdown. What is lost is a *new* comment's ability to say which part of a page it is about, except in its own words.
- **Side-by-side revision comparison.** Deferred by Edwin, with a condition: when it is built it must serve `.md` files too, not only HTML.
- **The sandbox is now the only boundary a framed file has** ([[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]), and a test fails if the same-origin flag is ever added.

## Not changed

- `REQ-0023-Design-Is-A-Project-Record` stands, and its four criteria were checked one by one against the new state: all four hold and two hold better. It is the clause that made this removal safe.
- Three notes still carry `design_revision:` — this repo's DES-0002 and DES-0004, and DES-0009. Nothing rewrote them.
- The Intent view, its badge and what it counts.

## Verification

- Full suite in the foreground: 2060 passed, 6 skipped, 1 failed — the known unrelated `test_release_evidence` case. The count fell from 2264 because the bench's tests went with it: `test_design_bench.py` (170), `test_design_variants.py` (11), `test_design_tokens.py` (10) and `test_annotations.py` (12).
- Validator green here and, for the upstream half, across seven repos before it was committed.
- The viewer, the banner, the old bench address and the cross-repo case were driven in the renderer harness on the built renderer.
- [[TST-0086-A-Note-Shows-The-Pictures-Beside-It]] and [[TST-0087-An-HTML-Page-Opens-In-The-Viewer]] are the walks, and they say a harness does not count for their window steps.
