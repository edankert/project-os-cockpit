---
type: "[[issue]]"
id: ISS-0244
aliases: ["ISS-0244"]
title: "The release page draws a static check mark on every blocking row — a control that was disarmed rather than removed, identical on every row of the list where it appears"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
source: ["user:edwin"]
severity: low
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0190-The-Acceptance-Tests-Sit-Last-On-Both-Release-Surfaces]]", "[[ISS-0224-The-Positional-Address-Outlived-The-Document]]"]
tests: []
---

# The mark stayed after the reason for it left

## Problem

Edwin, 2026-08-20, on the generated `your-trainer` release page: *"it shows the outstanding tests but it shows them with the check marks, just show them as a list of tst links like the features below."*

`gateGroup` puts `gateMark(item)` first on every row. That was correct when the mark was **the control** ([[ISS-0190]] put it in the row's left-hand column deliberately). [[ADR-0035]] then removed the click — [[ISS-0210]] found sixty live marks on the page whose entire purpose is to report that a release is *not* ready — and the glyph stayed behind as `is-static`.

**What is left is a decoration that is uniform where it appears.** The `Blocking` / `New` / `Chronic` / `Regressed` lists are, by construction, rows that are not settled — so every row shows the same glyph. It occupies the left-hand column and separates nothing from anything.

Two rows on the same page, for comparison:

```
feature   FEAT-0051   AI Workout Builder
gate      ☐  TST-0044  Paid, Key Configured — Generation …   AI Workout Builder
```

The feature row is what Edwin is pointing at: a typed id, a title, a click through to the note.

## The change is smaller than it looks

`item.number` **already resolves to `TST-0044`** on `your-trainer`. `Item.number` returns the positional address where one exists and the note id where it does not ([[ISS-0219]]), and those 89 checks carry no `number:` field at all — so the id is already on screen and already links to the check's own note.

So this is: drop `gateMark` on the unsettled lists, and give the id the features row's treatment (`scoped-row-id mono ov-typed`, `data-type="test"`).

## What must not be dropped with it

**`Quiet` and `Stale evidence` use the same `gateGroup`, and there the mark is not uniform.** A stale row is *ticked* — that is the whole of what makes it stale — so removing its glyph would erase the one thing distinguishing it from a blocking row. 53 of `your-trainer`'s ticked rows are in that group, and they are the reason its honest blocking number is 113 against a reported 60.

Proposal: drop the mark on `Blocking` / `New` / `Chronic` / `Regressed`; keep the distinction on `Quiet` and `Stale evidence`, in the row's meta text rather than as a glyph, so all six lists still read as one shape.

## Expected

```
TST-0044   Paid, Key Configured — Generation (Gemini)      AI Workout Builder
TST-0077   FREE at Cap Offers Nothing                      Monetization & Licensing
```

## Fixed

`gateMark` is **deleted**, on the rule this file already applied to `markGateRow`: *a live-looking helper is how the next caller re-acquires the behaviour a decision just removed.* The row is now a typed `TST-*` id, a title and its meta — the features row's own shape.

Where the mark carries information it survives as a **word** in the meta line: `withMark` is set on `Quiet` and `Stale evidence` and nowhere else, because a stale row is *ticked* and that is the whole of what makes it stale.

**A dead clause went with it.** The row's click handler opened with `if (ev.target.closest('.acc-mark')) return;` — an escape hatch so marking did not also navigate. With no mark on the row it could never fire again. That is the defect this phase has now shipped three times, each written while fixing the previous round, so it was deleted rather than left looking live.

**Three existing guards had to be re-anchored rather than deleted**, and one of them is a genuine supersession:

| guard | what happened |
|---|---|
| `test_a_gate_row_carries_a_token_and_never_a_control` | read `gateMark`'s body; now asserts on the row builder — **a stronger claim**, since there is no mark element to be static about |
| `test_a_gate_row_wears_the_documents_control_and_no_buttons` | its checkbox half is **superseded by Edwin's later instruction**; the ADR-0035 half (no buttons, no second vocabulary) stays |
| `test_one_walk_layer_and_now_exactly_one_surface` | stripped one known comment by exact text, so it broke when a second comment named `markGateRow`; now matches live code only |

That last failure mode appeared **twice in one sitting** — a text guard tripping on the comment that explains it — and both are now line-matched with comment lines excluded. A guard that fails on its own explanation is a guard somebody weakens to make it pass.

## Next Actions

- [x] Drop the mark on the four unsettled lists; align the id with the features row.
- [x] Carry the distinction in meta text for `Quiet` and `Stale evidence`.
- [x] Guards, comment-proof, on both front doors.

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

**The re-anchored guard is not stronger; it is anchored on a different name.** The note argues the guard *"moves up to the row builder … because each removal that anchored on a name left the next one unguarded."* `test_a_gate_row_carries_a_token_and_never_a_control` line-matches the class token `acc-mark`; `test_no_gate_row_draws_a_mark` matches `function gateMark` / `gateMark(`. Both are names.

Mutant executed — prepend to every gate row inside `gateGroup`:

```ts
const mk = document.createElement('span');
mk.className = 'gate-mark is-static';
mk.textContent = MARK_GLYPH[item.mark || ' '] ?? '?';
li.prepend(mk);
```

**165 passed.** The mark is back on every row of `Blocking`/`New`/`Chronic`/`Regressed` and nothing fires. `.gate-mark` is still a live CSS rule at `desktop/src/renderer/renderer.css:5700`, so the hook is pre-built and the mutation needs no new styling. A guard on the property claimed — no glyph in the row's gutter — would key on the row builder appending anything before `n`, or on `MARK_GLYPH`/`MARK_CLASS` being read inside `gateGroup`.

Deleting the dead `.acc-mark` clause is right and the `withMark: true` count of exactly two is correct. *"Guards … on both front doors"* is loose: `cockpit.js` renders no gate rows at all, so there is no second door here to guard.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: changes-requested.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

`.gate-mark` is deleted — the right call, and it did close my exact mutant: the `gate-mark` + `MARK_GLYPH` reintroduction now fails `test_a_gate_row_carries_a_token_and_never_a_control` (executed).

**But the guard's own claim is still false, and two fresh mutants walk past it.** The docstring says: *"the FIRST of them is the id. A mark in the gutter has to be appended before the id, and there is no way to do that without failing this."*

The shape check is `re.findall(r"^\s*li\.(append|appendChild)\((.*)$", body)` and then `appends[0]`. Executed against the current tree, both **165 passed**:

1. **The mark is back in the gutter.** `li.prepend(tok)` — `prepend` is not in the regex's alternation, so `appends[0]` is still `n, t, a, ...subjectLinks` and the shape assertion is satisfied while the glyph renders in the left-hand column, which is the literal thing Edwin asked to remove.
2. **The mark is back at the end of the row.** `li.appendChild(tok)` placed *after* `li.append(n, t, a, …)` — `appends[0]` is unchanged again.

Neither mutant needs the forbidden vocabulary: `tok.textContent = item.mark === 'done' ? '\u2611' : '\u2610'` uses no `MARK_GLYPH`, `MARK_CLASS`, `acc-mark` or `gate-mark`, so the belt-and-braces line does not fire either.

This is the fourth spelling of the same control walking past the fourth name-shaped guard. What would hold: assert on the *complete* child sequence of the `li` — that the only statements adding children are the single `li.append(n, t, a, ...subjectLinks)` — rather than on the first of a filtered list. `prepend`, `insertBefore`, `before` and `replaceChildren` all need to be in scope, or the assertion needs to be that no other add-a-child call exists at all.
