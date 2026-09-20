---
type: "[[issue]]"
id: ISS-0184
aliases: ["ISS-0184"]
title: "Clicking a checkbox in a Markdown document can tick a different line if the page shows fewer checkboxes than the file holds"
status: "fixed"
phase: ""
owner: user:edwin
created: 2026-08-17
updated: "2026-09-20"
reported_by: user:edwin
source: ["Edwin 2026-08-17: 'I thought we would have the checkboxes in the acceptance-tests.md to have 3 states and we would allow to add text there'", "Reproduced against a throwaway copy of ../your-trainer's suite on 2026-08-17"]
severity: medium
component: cockpit-server
parent: ""
related: ["[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[FEAT-0103-The-Gate-Is-Walkable]]", "[[FEAT-0111-The-Marks-The-Record-Already-Uses]]", "[[ISS-0177-An-Exception-Mark-Drops-A-Check-With-No-Justification]]"]
tests: []
fixed_by: "[[TASK-0632-Fix-The-Seven-Defects-From-The-Issue-Review]]"
---

# Clicking a checkbox can tick a different line than the one clicked

When a document shows fewer checkboxes than its source file contains, clicking one can write the tick to a later line, and the cockpit still reports success. This does not happen today on any known file; nothing stops it from happening.

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


## WITHDRAWN 2026-08-17, same day — the reproduction was against a file being edited

**The headline claim above is wrong and I am striking it rather than quietly softening it.**

Re-run against the suite as it stands:

```
box index 257  ->  source box 257  ->  line 414 "Per-Rider Export Lives On Profile → Data"
write landed   ->  line 414
```

That is **correct**. And the counts agree:

```
app renderer (renderer.render_markdown_text) : 579 checkboxes
source task lines                            : 579
data-raw attributes emitted                  : 579
```

So there is no divergence, nothing is mis-addressed, and every box is labelled.

**Where the wrong number came from.** `docs/tests/ACCEPTANCE_TESTS.md` in `../your-trainer` was written at **08:58:28** on 2026-08-17 — while this session was running, by Edwin, adding rows. My 542 was read out of that file mid-edit. I then built an argument on it, wrote a reproduction that appeared to confirm it, and filed and committed the result inside about ten minutes without re-reading the source of the number.

The reproduction "confirmed" it because I checked *which line changed* and matched it against **my own earlier index table**, not against a fresh one. Both were computed from the same stale read, so they agreed with each other and with nothing else. A reproduction that only ever consults its own premise is not a reproduction.

## What is still true, and why this stays open rather than being deleted

**The write path has no guard, and the labelling path does.** `renderer._annotate_checkbox_source` refuses to attach `data-raw` when rendered boxes and source task lines disagree, precisely because the ordinal correspondence is then unknowable ([[ISS-0175]]). `check-toggle` performs the same ordinal walk with no such check. Today the counts agree; nothing makes them keep agreeing.

The failure mode is exactly what I incorrectly claimed had already happened: one absorbed task list, and every box after it writes one row off, silently, reporting `ok`. [[FEAT-0103]] declined to build the acceptance walker on this endpoint for that reason and recorded it; the reasoning was never applied back to the toggle.

So the fix is unchanged and is now justified by fragility rather than by a live defect: **address a check by something that fails to resolve rather than resolving to the wrong row** ([[TASK-0456]]). It is needed anyway, because the mark cycle has to carry a reason to a specific check.

**Severity dropped high → medium.** Latent, not live.

## The lesson, recorded because it is the second time this session

A number measured once and then reused across several steps is a single point of failure, and mine was read from a file somebody else was editing. Measurements that a decision rests on get re-taken at the moment of the decision — and a reproduction has to derive its expectation independently of the claim it is testing.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** In a document where one task list is swallowed by the paragraph above it (no blank line between them), every checkbox after that point ticks the line below the one clicked. The page says the write worked.

Evidence: the client sends only the checkbox's position among the rendered boxes (desktop/src/renderer/renderer.ts:2851-2867, `Array.from(all).indexOf(tgt)`). The server's `_toggle_task_at` (src/project_os_cockpit/server.py:4266-4310) walks the source file's task lines and ticks the Nth one, with no check that the rendered and source counts agree. The labelling path does refuse in that case (`renderer._annotate_checkbox_source` omits `data-raw`, read at renderer.ts:2153), so the guard exists and the write path does not use it. This is a **small fix**: refuse the toggle in the client when the clicked box has no `data-raw` (or send `data-raw` and have the server compare it with the line it is about to change), with one test using a file whose task list follows a paragraph line.

**Belongs to:** no open feature (the acceptance checks moved to notes and no longer use this endpoint). **Next:** small fix in `_serve_check_toggle`/the renderer change handler, with a failing test first.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).

## Fixed 2026-09-20 (TASK-0632)

**What changed.** `_toggle_task_at` (`src/project_os_cockpit/server.py`) now refuses two ways instead of trusting the position.

1. **The counts must agree.** It renders the note's body and counts the checkboxes the page draws, then counts the `- [ ]` lines the file holds. When the two differ, the position names a different row in each, so the write is refused and the reply says why: *"this document's checkboxes cannot be addressed: the page draws N and the file holds M"*. This is the refusal `_annotate_checkbox_source` has made on the labelling side since [[ISS-0175]], applied to the write. It needs nothing from the client.
2. **The text must match.** The renderer now sends the box's `data-raw` prose beside its index (`desktop/src/renderer/renderer.ts`), and the server compares it — through `note_writes._criterion_text`, so evidence is stripped on both sides — with the line it is about to change. That catches the case the counts cannot: the file was edited after the page was drawn.

`renderer.rendered_checkbox_count` is the new helper that answers "how many boxes does this body draw", by rendering. There is no cheaper honest answer: pymdownx.tasklist's rules are the only authority on what draws a box. Measured at 66 ms on the largest checklist in the fleet (43 boxes, `your-trainer/docs/requirements/PRD-Original.md`), which is a click, not a page load.

**It was live, not latent.** The WITHDRAWN section above is still right that `your-trainer`'s suite agreed on the day it was measured. But any document with an absorbed task list diverges, and the divergence is silent: before this change, a POST of index 0 against such a file wrote to the first absorbed row and answered `{"ok": true}`. The test fixture is that document.

**Which test guards it.** `tests/test_check_toggle.py`:
- `test_a_click_is_refused_when_the_page_and_the_file_hold_different_boxes` — a file with three absorbed rows and two drawn ones. Asserts the 404, the message, and that the file is byte-identical afterwards.
- `test_a_click_is_refused_when_the_text_does_not_match_the_line` — asserts both directions: the wrong text is refused and does not write, and the right text writes.
- `test_the_renderer_sends_the_text_it_is_showing` — the client half, read off the source. Weak on its own, which is why the count refusal above needs no client at all.

**Run both ways.** With the fix: `13 passed`. With `server.py`, `renderer.py` and `renderer.ts` reverted: `3 failed, 10 passed`. `npx tsc --noEmit` is clean and the node suite passes.

**What is not done.** Expected #1 above wanted a checkbox addressed by something that survives an edit, and this is not that; it is the refusal Expected #2 asked for, which is what makes the endpoint safe. Expected #3 — naming the rows that render no checkbox so the repo that owns them can add the blank line — is now in the refusal message rather than in a report. A document-wide address scheme stays a design question and is not reopened here.

**Out of the parking lot.** `phase:` was `[[PHASE-999-Future]]` and is now empty. PHASE-999 is where work is parked, and a fixed issue sitting there makes the phase strip draw shipped work as unplanned (`tests/test_coverage_registers.py::test_no_terminal_note_sits_in_the_parking_lot`). No phase delivered this; it was worked under [[ISS-0313]]'s work order, which has none, and an empty `phase:` is what the other six issues in that order carry.
