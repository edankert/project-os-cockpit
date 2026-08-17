---
type: "[[issue]]"
id: ISS-0184
aliases: ["ISS-0184"]
title: "The checkbox write path addresses by position and nothing guards it — the reproduction was against a transient file state and is WITHDRAWN, the latent fragility is real"
status: "open"
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: ["Edwin 2026-08-17: 'I thought we would have the checkboxes in the acceptance-tests.md to have 3 states and we would allow to add text there'", "Reproduced against a throwaway copy of ../your-trainer's suite on 2026-08-17"]
severity: medium
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
