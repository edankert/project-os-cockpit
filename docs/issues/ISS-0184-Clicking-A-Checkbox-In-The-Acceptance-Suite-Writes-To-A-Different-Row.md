---
type: "[[issue]]"
id: ISS-0184
aliases: ["ISS-0184"]
title: "Clicking a checkbox in your-trainer's acceptance suite writes to a different row — every box from the 258th onward is mis-addressed, and the write reports ok"
status: "open"
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: ["Edwin 2026-08-17: 'I thought we would have the checkboxes in the acceptance-tests.md to have 3 states and we would allow to add text there'", "Reproduced against a throwaway copy of ../your-trainer's suite on 2026-08-17"]
severity: high
component: cockpit-server
parent: ""
related: ["[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[FEAT-0103-The-Gate-Is-Walkable]]", "[[FEAT-0111-The-Marks-The-Record-Already-Uses]]", "[[ISS-0177-An-Exception-Mark-Drops-A-Check-With-No-Justification]]"]
tests: []
---

# Clicking a checkbox in the acceptance suite writes to a different row

## Reproduced, not reasoned

Against a throwaway copy of `../your-trainer/docs/tests/ACCEPTANCE_TESTS.md`, driving the real endpoint:

```
POST /api/notes/check-toggle  {"index": 257, "checked": false}
→ {"ok": true}  HTTP 200
```

The box a person sees at that position is **§1.20.2 "Export Gating — Free Tier"**. The line that changed was **413 — "Per-Rider Export Lives On Profile → Data"**, a different check in a different section. The endpoint reported success.

## Cause: two counts that stopped agreeing

`check-toggle` addresses a box by its **zero-based ordinal among the rendered checkboxes** and the server walks the **source** `- [ ]` tokens in order to find the Nth. That works only while the two counts match.

Measured on that file today:

```
source checkbox lines : 579
RENDERED checkboxes   : 542
difference            :  37
```

The 37 are [[ISS-0175]]'s cause — Markdown lazy continuation. A task list opening immediately after a paragraph line, with no blank line between them, is absorbed into that paragraph and renders **no checkbox at all**, while a line-based reader counts every one.

The first such row is source line 413, source index **257**. From that point on every DOM index is one behind, and it slips further at each subsequent site — 37 times.

## Why it was not seen

[[ISS-0175]] fixed the *labelling* half: `renderer._annotate_checkbox_source` now refuses to attach `data-raw` when the counts disagree, so nothing is mislabelled. **The write path was never given the same guard.** It still trusts the index.

[[FEAT-0103]] declined to build the acceptance walker on this endpoint for exactly this reason, and recorded why: *"A walker addressed by global checkbox index would write to whichever row had moved into that position."* That reasoning was applied to the new walker and never applied back to the existing toggle.

## Blast radius

Any `.md` whose rendered and source checkbox counts diverge. Measured across the fleet, only `your-trainer`'s acceptance suite currently diverges — but it is the largest checklist anyone actually clicks, and it is the document this work is trying to make interactive.

## Expected

1. **A checkbox is addressed by something that survives an edit, or the write is refused.** `acceptance.locate()` already resolves a check by section-and-ordinal (`1.25.3`) and fails to resolve rather than resolving to something else; that asymmetry is the whole reason it exists. The document's boxes should carry their address rather than their position.
2. **Where an address cannot be established, the checkbox is not interactive** — and says so, rather than silently writing somewhere.
3. **The 37 rows that render no checkbox** are a source-formatting problem in the repo that owns the suite (a blank line before each absorbed list). The cockpit should name them rather than pretend they are clickable.

## Notes

Not fixed here because it is one half of a design question Edwin has re-opened — whether the acceptance document itself is the surface for marking checks, with a cycle and a justification. See the review filed alongside this. **The addressing must be fixed either way**; the cycle is the part that needs a decision.
