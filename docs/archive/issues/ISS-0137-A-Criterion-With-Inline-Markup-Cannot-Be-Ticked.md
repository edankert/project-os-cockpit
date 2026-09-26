---
type: "[[issue]]"
id: ISS-0137
aliases: ["ISS-0137"]
title: "A criterion containing inline markup cannot be ticked — the renderer sends the rendered text and the server matches the raw line, so half the open criteria are unreachable from the note page"
status: fixed
severity: high
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
phase: "[[PHASE-023-Levers-For-The-Human]]"
features: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
tasks: []
related: ["[[REQ-0028-Evidence-Names-Its-Witness]]", "[[FEAT-0063-The-Acceptance-Runner]]", "[[REL-0001-The-Human-Has-Levers]]", "[[PHASE-023-Levers-For-The-Human]]"]
tags: [issue, writes, acceptance]
---

# A criterion with inline markup cannot be ticked

## What happens

Walking [[REL-0001]]'s check *"a criterion ticks with evidence"* on 2026-08-11 against an isolated clone. Ticking the first criterion on [[FEAT-0083]]:

> - [ ] Mode 1 exposes the project overview, rendering the same `/api/cockpit/stats` payload as the shell, with phases and scope rows

The evidence field accepts the text, `Tick` is pressed, and the write is **refused**:

```
no criterion on FEAT-0083 reads 'Mode 1 exposes the project overview, rendering the same /api/cockpit/stats payload as the shell, with phases and scope rows'
```

The next criterion on the same note — same list, same session, **no inline markup** — ticks first time and writes exactly one line.

## Cause

Two functions that are supposed to produce the same string, and one of them reads the wrong thing.

`renderer.ts :: criterionTextOf` takes `textContent` of the **rendered** `<li>`. Markdown has already turned `` `/api/cockpit/stats` `` into `<code>/api/cockpit/stats</code>`, and `textContent` drops the backticks.

`note_writes :: _criterion_text` matches against the **raw markdown line**, where the backticks are still there.

The two strings differ by exactly the markup, so the match fails and the endpoint answers correctly that no criterion reads that. **The server is not wrong; the caller is describing a different string.** The comment above `criterionTextOf` says *"Mirrors `note_writes._criterion_text`"* — it mirrors the rendered text, which is the bug in one sentence.

It is not specific to code spans. Anything Markdown rewrites inline hits it: `**bold**`, `*italic*`, `[[wikilinks]]` (rendered as anchor text without the brackets), and `[text](url)`.

## Blast radius, measured 2026-08-11

Across `docs/`, counting only unticked boxes under an `Acceptance` / `Exit Criteria` / `Acceptance Criteria` heading — the boxes the renderer actually intercepts:

- **53** unticked criterion boxes
- **26 of them — 49% — carry inline markup and cannot be ticked from the note page**, across 8 notes

Widening to every unticked checkbox line in `docs/` (a superset, since not all sit under a criteria heading): 649 of 994, 65%.

## Why `high`

[[FEAT-0060]]'s whole claim is that a human can discharge a judgment *in the place that owns it*. For half the open criteria the button is present, takes evidence, and then refuses — which is worse than not offering it, because the reader has already done the thinking. It also lands on the criteria most worth ticking: a criterion precise enough to name an endpoint or a note is the one most likely to carry markup.

**It very likely affects [[FEAT-0063]]'s acceptance runner too**, which resolves criteria through the same endpoint. Not yet confirmed — the runner path was not driven in this pass, and that check is stated here rather than assumed.

## The fix, and the trap in it

Send the **raw** criterion text, not the rendered text. The rendered `<li>` cannot recover the markup it consumed, so the source line has to reach the client — carried on the checkbox as a `data-` attribute when the note is rendered, which is where the raw line is still in hand.

**Do not fix it by normalising on the server** (stripping markup before comparing). That makes two criteria differing only in markup collide, and `resolve_criterion` treats ambiguity as a refusal *by design* — *"two criteria with the same prose is not a case to guess at"*. Loosening the match to fix a lookup would trade a visible failure for a silent wrong write.

## Verification

A test that ticks a criterion containing a code span, a bold run and a wikilink, and asserts the line is rewritten — driven through the same path the renderer uses, not by calling `resolve_criterion` with the raw string, which is exactly the assertion that would have passed while this was broken.

## Homed with the feature it broke

Filed under [[PHASE-999]] because it was `triage` and had no scheduled home; **re-homed to [[PHASE-023]] on being fixed** — the phase that delivered [[FEAT-0060]], which is what the defect was in. `test_no_terminal_note_sits_in_the_parking_lot` refuses a terminal note in the parking lot, and correctly: the lot is for work with no home *yet*, and a fixed defect's home is the phase that shipped its subject. The check caught this within a minute of the status changing.

## Fixed — 2026-08-11

**The raw line now travels with the box.** `renderer._annotate_checkbox_source` walks the rendered HTML and the source in the same document order — the correspondence `server._toggle_task_at` has always relied on — and stamps each checkbox with `data-raw`, the criterion's prose after `_criterion_text`. `criterionTextOf` reads that attribute and only falls back to `textContent` when an older sidecar does not send it.

**Fixed at the caller, not by loosening the match.** The alternative — normalising markup away on the server before comparing — was rejected in this note before the fix was written, and the reason held: it would make two criteria differing only in markup collide, and `stamp_tick` treats ambiguity as a refusal *by design*. Trading a visible failure for a silent wrong write is not a fix.

**Verified twice, and the second one is the real one.** `tests/test_criterion_raw_text.py` drives render → read the box → write, parametrised over a code span, a wikilink, a bold run and a plain control. Sabotaged to send rendered text instead, **all three marked-up cases fail and the plain one passes** — which is the bug's exact signature, so the test discriminates rather than merely covering. Then on the surface: the criterion that refused this morning —

> Mode 1 exposes the project overview, rendering the same `/api/cockpit/stats` payload as the shell, with phases and scope rows

— ticked first time through the harness, backticks intact, one line changed.

*The tempting test — call `stamp_tick` with the raw string and watch it work — would have passed throughout. It always worked. The defect was in what the caller sent, so the test has to include the caller.*
