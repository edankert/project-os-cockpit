---
type: "[[plan]]"
title: "Plan — FEAT-0149 The walk page"
status: done
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
source: []
implements: ["[[FEAT-0149-The-Walk-Page]]"]
related: ["[[PHASE-043-The-Walk-Page]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:`; why, and how they are found,
     is stated once in tools/instructions/STATUSES.md, `[[plan]]`. -->
# Plan — FEAT-0149 The walk page

## Delivery sequence

1. **[[TASK-0618-The-Walk-Payload]] — the payload.** Bundle the template's walk module and expose `walk_payload`. **First**, because the feature's whole claim is that the rows are the ledger's owed set and the order is the consumer's, and both are properties of data that a test can prove before anything is drawn. Until the upstream module lands, build the payload behind the final signature with the rules copied from project-os-dev TESTING.md "The walk", and replace the body with the bundled import when the module exists.
2. **[[TASK-0619-The-Walk-Page]] — the page.** `~walk/<platform>` over that payload. Sittings, rows with the procedure inline, the existing mark dialog, place kept per workspace.
3. **[[TASK-0620-The-Survey]] — the survey.** The first section of the page, derived from invalidation events. Independent of 2 in code and lands after it so the page exists to render into.
4. **[[TASK-0621-The-Release-Rung-Points-At-The-Walk]] — the links.** The release rung, the release page and the checks page point at the walk while a release is `draft`. Last, because a link to an empty page is the blank button CLAUDE.md warns about twice.

2 needs 1. 3 needs 1 and 2. 4 needs 2.

## Dependencies

- **Hard:** project-os-dev FEAT-0029 ships `tools/scripts/walk-sheet.py` with the ordering and survey rules. The cockpit bundles it; it does not author those rules. If the cockpit prototypes ahead of upstream, the prototype is replaced, not kept beside the bundled copy, because two implementations of one predicate is how a badge and a gate come to disagree (`ledger.owed`'s own docstring).
- **Hard:** a consumer repo with a WALK.md to render. `your-trainer` FEAT-0119 authors one from its run plan. Without it the page shows the fallback, one sitting per area in id order labelled unordered, which is enough to build against but not enough to accept the feature on.
- **Soft:** project-os-dev ADR-0027's four headings in the test template. A row renders them when present and says "not stated" when absent, so the page works on day one; it reads well only as the corpus is rewritten on contact.

## Open questions

- **Bundle or import.** `validate_docs_bundled.py` is a verbatim copy synced from upstream and verified by a test. The walk module can follow the same path, or the cockpit can import `tools/scripts/walk_sheet.py` from the browsed repo when present and fall back to the bundled copy, the way `validation.py` locates the validator. Proposal: bundle only. The browsed repo's copy is for people generating markdown, and the cockpit reading a repo's own script would make the page's behaviour depend on how recently that repo synced.
- **Where the page lives.** `~walk/<platform>` as a route inside the publication view, or a section under the release rung's page. Proposal: a route, because a walk is long and the release page already carries the ladder, the gate and the settle section. The release page links to it and does not embed it.
- **How a repo declares its gallery.** Proposal: a `gallery:` field in WALK.md's frontmatter carrying the command to regenerate screenshots and the path to compare, rendered verbatim at the top of the survey. The template decides the field; the cockpit reads it.
- **No WALK.md.** Proposal: one sitting per `area:` in id order, the section heading reading "Unordered — this repo has no walk order", and a link to the template's WALK.md template. The page must never be blank in a repo with owed checks.
- **Multiple platforms.** `ledger.owed` is per platform and so is the page. A repo with two open ledgers gets two walks. Whether the publication view offers a picker or the release rung links to its own platform's walk is decided in [[TASK-0621-The-Release-Rung-Points-At-The-Walk]].
- **The check's own note.** A row links to the note as `~checks` rows do. Whether the walk page also opens the note's comment history inline, as the mark dialog does, is decided in [[TASK-0619-The-Walk-Page]] by cost; the dialog already shows it.

## What the open questions resolved to (2026-09-13)

- **Bundle or import** — bundle only, as proposed.
- **Where the page lives** — a route, `~walk/<platform>`, as proposed. The release page links to it and does not embed it.
- **The gallery** — a `gallery:` field in the walk order's frontmatter, printed verbatim at the head of the survey, as proposed. The template owns the field.
- **No WALK.md** — one sitting per surface in id order, a banner saying the order is nobody's, and a button opening the template. As proposed.
- **Multiple platforms** — no picker. Each surface links to the platform it already knows (see [[TASK-0621-The-Release-Rung-Points-At-The-Walk]]).
- **The check's own note** — the dialog's history only, and the walk payload carries history for its own rows so the dialog opens with it (see [[TASK-0619-The-Walk-Page]]).
