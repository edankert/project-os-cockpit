---
type: "[[issue]]"
id: ISS-0033
aliases: ["ISS-0033"]
title: "The identity band's only link is a dead click that replaces the surface"
status: fixed
severity: high
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review 2026-07-28 (FEAT-0043)"]
related: ["[[TASK-0223-Brief-Payload-And-Identity-Band]]", "[[FEAT-0043-Design-Top-Level-Surface]]", "[[CHG-20260727-Design-Bench-Reachability]]"]
fixed_by: []
---

# The identity band's link is dead

## What happens

`buildIdentityBand` wires "Read the full brief" / "Open LLM_BRIEF.md" to `navigateTo(brief.rel)` where `rel` is `LLM_BRIEF.md`. That is not a `~` virtual page, so it fetches `/api/render?path=LLM_BRIEF.md`, which resolves against `docs_root` (`<workspace>/docs`). The brief lives at the repo root and is not in `PROJECT_SUPPORT_ROOT_FILES` (README, ROADMAP, SECURITY).

Verified live: `{"ok": false, "error": "not a markdown file: LLM_BRIEF.md"}`. A 404 sends the renderer into `mountPlaceholder`, which **replaces the design surface** with "No note here".

## Why it matters more than a broken link normally would

This is the same defect class as the two reachability bugs FEAT-0043's own "Why" section cites as its reason for existing: a control pointing where the server never claimed. Shipping it inside the feature written to end that pattern is the finding.

It also falsifies a DoD bullet that was ticked with named evidence — TASK-0223's "The band links to the file so editing is one click". The evidence named a behaviour nobody had exercised end to end.

## Fix direction

Add `LLM_BRIEF.md` to `PROJECT_SUPPORT_ROOT_FILES` — it is exactly what that allowlist is for — and assert the link target actually resolves, rather than asserting the button's label.

## Resolution (2026-07-28)

Adding `LLM_BRIEF.md` to `PROJECT_SUPPORT_ROOT_FILES` looked like the whole fix and **was not** — the file still 404'd on the first curl, because `_serve_render` never consulted that allowlist at all. It resolved every path against `docs_root` and rejected anything above it. So the Library's `/README.md`, `/ROADMAP.md` and `/SECURITY.md` rows had been dead clicks since FEAT-0010, for the same reason, unnoticed.

Fixed in three places:

1. `PROJECT_SUPPORT_ROOT_FILES` gains `LLM_BRIEF.md`.
2. `_serve_render` resolves an exact-match allowlisted filename against `project_root` before falling back to `docs_root`. Exact-match on a name with no separators, and `..` is already rejected above it, so this widens nothing else — verified by curl: `CLAUDE.md` still refuses, `../SECRETS.md` still blocks.
3. `extractRel` routes `/<file>.md` (one path segment) instead of discarding it. Routing is the renderer's job; authorising is the server's, and the server holds the allowlist.

Guarded by `test_the_brief_link_resolves_over_http` — a **real server on an ephemeral port**, because the one-line version of this fix passed inspection and failed the wire. Mutating the server check back to `if False:` fails that test.

The lesson is the one this issue is about: a link is only verified by following it.
