---
type: "[[issue]]"
id: ISS-0065
aliases: ["ISS-0065"]
title: "The Library reduction emptied the overview record column — 8 of 9 ADRs are now unreachable, and the Verification card is gone"
status: fixed
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: []
severity: high
component: overview
parent: "[[FEAT-0050-Library-Reduction]]"
related: ["[[PHASE-010-Surface-Ownership]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]", "[[CHG-20260729-Surface-Ownership]]", "[[TST-0022-Surface-Ownership]]", "[[FEAT-0049-Review-Desk-As-Record]]"]
tests: []
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
---

# ISS-0065 — The record column lost its source

Filed by the independent review of `bed48ea` on 2026-07-30 ([[REQ-0025]], [[FEAT-0050]]).

## Problem

`fillRecordColumn` (`desktop/src/renderer/renderer.ts:10520`) builds every card in the overview's right-hand column from a single fetch:

```ts
const library = await fetchRecordNotes('library');   // GET /api/cockpit/nav?mode=library
const adrs = library.filter((n) => n.type === 'adr' || n.type === 'decision');
const tests = library.filter((n) => n.type === 'test');
const refs = library.filter((n) => n.type === 'reference');
```

[[FEAT-0050]] emptied that payload. `fetchRecordNotes` keeps only items with both an `id` and a `url`; the reduced `mode=library` emits `docs-tree` alone, whose items carry no `id`. Measured against this repo's corpus:

| | `bed48ea~1` | `bed48ea` |
|---|---|---|
| record-eligible items harvested | 149 | **0** |
| of which ADRs | 8 | **0** |
| of which tests | 21 | **0** |

Every card is behind a `length > 0` guard, so nothing errors — the Decisions card and the Verification card simply stop being built on the project-scope overview.

The dedup argument in [[FEAT-0050]] and [[CHG-20260729-Surface-Ownership]] ("the record column already renders every ADR inline; `buildRecordDisclosure` holds `sorted.slice(4)`") was correct about the function and wrong about its input. The record column was not a second copy of Library's Decisions group — it *was* that group, reshaped. Removing the duplicate removed the original.

## Consequences

- **Decisions have no navigation route.** 8 of this repo's 9 ADRs reach no surface (`ADR-0007` appears only transiently in `mode=recent` because it was edited recently). `decisions` is still in `DOC_TREE_EXCLUDED_ROOTS`, justified in its own comment by "the overview record column".
- **No search route either.** `QUICK_CORPUS_MODES` covers `features`, `tasks`, `issues`, `design`, `library` plus the tests register and the changes payload. None carries a decision, so Cmd+P cannot find an ADR by name.
- **The Verification card is gone from the project overview** — `passing/total`, the non-passing test rows, and `fillVerificationHealth` (waivers + validator state). The desk's new Tests register is a different surface answering a different question, and no note claims the overview card was moved.
- **Latent: the attention inbox.** `appendAsyncWaitingRows` (`renderer.ts:5852`) uses the same fetch for its `failing` and `ready` test rows. Currently a no-op because all 22 tests are `passing`; it will silently stay a no-op when one fails.
- The `Library` refs card was already empty before this change (no `reference`-typed items appeared in the pre-change harvest either), so that one is pre-existing rather than a regression.

## Repro

```
$ .venv/bin/python -m project_os_cockpit docs --port 8899 --bind 127.0.0.1 --no-open
$ curl -s "http://127.0.0.1:8899/api/cockpit/nav?mode=library"
  → groups: ['docs-tree'];  items carrying an id: 0
```

Then open the project-scope overview: no Decisions card, no Verification card.

## Why nothing caught it

This is the third consumer of `mode=library`. The `buildQuickCorpus` one was caught during implementation and is written up carefully in [[PHASE-010]] and [[CHG-20260729-Surface-Ownership]] as the near-miss that justifies [[REQ-0025]]; `grep -n "fetchRecordNotes\|mode=library"` over `renderer.ts` returns three call sites and one of the three was fixed.

[[REQ-0025]] criterion 5 is the criterion this falsifies, and it was the only one of eight with neither an automated test nor a manual step — its whole evidence was a source-line pointer, which itself does not resolve (it cites `renderer.ts:10269-10273`; `sorted.slice(4)` is at `10572-10573`). No step in [[TST-0022]]'s manual checklist reads the overview's right-hand column.

## Expected

Decisions reachable by navigation from at least one page, per [[REQ-0025]]'s Statement, and the overview's Verification card fed by something the reduction does not empty.

## Suggested direction

Give the record column a source of its own rather than a by-product of a nav mode — the same move [[FEAT-0048]] made for changes (`GET /api/cockpit/changes`) and [[FEAT-0049]] made for tests (`registers`). A `decisions` register or payload would also give Cmd+P something to enumerate. Whatever the shape, the guarding test should assert the *source* reaches the column, not the shape of the function that would render it: that distinction is the entire lesson here.

## Traceability

- Parent: [[FEAT-0050-Library-Reduction]]
- Falsifies: [[REQ-0025-No-Type-Loses-Its-Surface]] criterion 5, [[PHASE-010-Surface-Ownership]] exit criterion 6
- Blocks: [[FEAT-0050]] at `done`, [[REQ-0025]] at `implemented`, [[TST-0022]] at `passing` (it declares `verifies: [[REQ-0025]]`)

## Fix — 2026-07-30

Taken in the suggested direction, and the suggestion about what to guard was the load-bearing part.

**Source.** New `GET /api/cockpit/decisions` (`cockpit.decisions_payload`) answers "what decisions exist" directly. Tests now come from the desk's existing `registers.tests` rather than a second harvest. Both are purpose payloads, matching what [[FEAT-0048]] did for changes and [[FEAT-0049]] for tests.

**Root cause removed, not just the symptom.** `fetchRecordNotes(mode)` is deleted. It had no callers left, and it is the abstraction that caused this: a helper that converts "a navigation surface" into "a list of notes" invites callers to depend on a nav mode's *contents*, which is a UI decision and free to change. It changed; three consumers broke; two stayed broken through a full review of the phase that broke them.

**Third consumer fixed too.** `appendAsyncWaitingRows` (`renderer.ts:5851`) read the same emptied harvest for its `failing`/`ready` test rows — latent only because every test in this corpus currently passes. It was already fetching the review queue in the same `Promise.all`, so it needed no extra request: fair evidence it was the wrong source from the start.

**A fourth, older instance of the same class, found while fixing this.** The record column's third card (`Library`, from `library.filter(n => n.type === 'reference')`) never rendered at all, and not because of PHASE-010: `fetchRecordNotes` keeps only items with an `id`, and references inline in the Docs tree are emitted with `id: ""` by design ([[TASK-0036]]). Measured against the pre-PHASE-010 payload, the harvest carried design/change/adr/risk/test/workflow/plan items and **zero** references. Removed rather than repaired — design inputs are reachable from the Design mode and references browse in the tree. A `length > 0` guard hid it for as long as it existed.

### Verified

Live pane after a restart, project scope: `Decisions 8 · all accepted` with 8 rows and a `4 older` disclosure; `Verification 22/22`. Both were absent before this fix.

Guards, each mutation-tested rather than assumed:

- `test_decisions_have_a_payload_of_their_own` — payload set-equality with `notes_by_type("adr")` ∪ `notes_by_type("decision")`. Fails when the payload drops ADRs.
- `test_the_record_column_does_not_harvest_a_nav_mode` — asserts the *source*, per the suggestion above. Fails when `fillRecordColumn` reaches for a nav harvest again.
- `test_the_nav_harvest_helper_is_gone` — fails if `fetchRecordNotes` returns.
- `test_the_quick_palette_covers_every_type_bearing_mode` — the Cmd+P near-miss had no test at all, only prose. Now pinned.

All four run against comment-stripped source: three of them initially failed on the comments explaining the very deletions they assert, which is its own small lesson about source-level guards.

### What this says about the phase

[[REQ-0025]] was written because this exact failure was foreseeable, and it still shipped. The gate asked "is each type reachable" and every criterion was checked against the type's *new* home — while the defect was in a surface that consumed the *old* one. Criterion 5 was the only one of eight with neither a test nor a manual step behind it, and it was the one that was false. That correlation is the finding worth carrying forward: a criterion ticked against a code-reading rather than an executable check is not evidence, and this phase's own notes say so about tests while doing it in a requirement.

## Independent review of the fix — 2026-07-30, changes-requested

Same fresh-context session that filed this issue, now reviewing the fix against the working tree. **The defect is genuinely fixed** — verified over HTTP, not read: `GET /api/cockpit/decisions` returns all 8 ADRs with `rel` and `status` populated, and a corpus-wide sweep across all nine nav modes plus the purpose payloads finds no canonical type with an unreachable note. Deleting `fetchRecordNotes` rather than repairing its callers is the stronger fix and there is no caller left.

Two claims in this note do not match the code or the corpus, and one guard gap is worth naming.

**1. "It needed no extra request" is false about the code as written.** The Fix section says `appendAsyncWaitingRows` "was already fetching the review queue in the same `Promise.all`, so it needed no extra request: fair evidence it was the wrong source from the start." The implementation calls `fetchTestsRegister()`, which issues its own `GET /api/cockpit/review-queue`, in parallel with `fetchReviewQueue()` — which fetches the same URL. Two identical requests, not zero extra. `grep -n "api/cockpit/review-queue" renderer.ts` returns three sites (2802, 7751, 10471), and rendering the overview now hits that endpoint three times: `fetchReviewQueue` and `fetchTestsRegister` in `appendAsyncWaitingRows`, plus `fetchTestsRegister` again in `fillRecordColumn`. The claim the note makes is available from `queue?.registers?.tests`; the code does not take it. There is also a dead alias (`const tests = testsRegister;`) left where the destructure was renamed.

The reason this matters more than a wasted request: it is the same defect class the whole issue is about — a note asserting a property the code does not have — appearing inside the fix for it.

**2. "157 → 0" is not the harvest figure; it is 149.** Stated in three places (`cockpit.py:2567`, `renderer.ts:10557`, `test_decisions_have_a_payload_of_their_own`'s docstring). Measured at `bed48ea~1` against `fetchRecordNotes`'s actual filter (`if (!item.id || !rel) continue`): 161 items in the payload, 157 with a resolvable rel, **149 with both an id and a rel** — and both halves of that `if` were load-bearing. 157 counts the 8 items that pass the rel check but carry an empty `id`, which is exactly the population the second half of the filter existed to drop, and exactly why the references card never rendered. Getting that number from the rel check alone reproduces in miniature the reading error the issue is about.

**3. The new plumbing has no behavioural guard, and four realistic breakages reproduce the original symptom.** Each of these passes all 24 tests in `tests/test_surface_ownership.py`, and each empties a card silently behind its `length > 0` guard — the exact signature of this issue:

- `decisions_payload` emitting items without `rel` (the renderer's `.filter(d => d.id && d.rel)` drops them all)
- an endpoint-path typo on **either** side — `renderer.ts` fetching `/api/cockpit/decision`, or `server.py` routing `/api/cockpit/decisions-disabled` — since `if (!resp.ok) return []`
- `fetchDecisions` returning empty regardless of the response
- `fetchTestsRegister` reading `registers.reviewed` instead of `registers.tests`

Nothing asserts that the route string in `server.py:800` and the fetch string in `renderer.ts:10449` agree. That is a **new cross-process contract introduced by this fix**, and it is unguarded; `/api/cockpit/changes` has the same gap, pre-existing. `test_the_record_column_does_not_harvest_a_nav_mode` pins where the renderer looks, which is the right property to pin and is genuinely new — but it is a code-reading, and this note's own closing section says a criterion ticked against a code-reading rather than an executable check is not evidence. The cheapest closure is a test asserting the literal path appears in both files (the same source-level technique already in use), plus one exercising the HTTP handler so a route rename fails somewhere.

**What survived refutation.** `test_decisions_have_a_payload_of_their_own` fails when the payload drops ADRs. `test_the_quick_palette_covers_every_type_bearing_mode` fails when a mode leaves `QUICK_CORPUS_MODES`. `test_the_nav_harvest_helper_is_gone` and `test_the_record_column_does_not_harvest_a_nav_mode` both hold, and `_renderer_code()`'s comment stripping is the right call — the observation that three assertions initially failed on the comments explaining their own deletions is a real lesson about source-level guards and worth having kept. The references-card removal is correct: I confirmed zero `reference` items in the pre-PHASE-010 harvest, so the card never rendered and nothing was stranded by deleting it. One qualification — "references browse in the Docs tree" holds for 8 of 21 reference notes; the other 13 are 4 templates and 9 container-directory `README.md` files under excluded roots, pre-existing and not this fix's problem.

Fixing 1 and 2 clears this. 3 can be recorded as a limit instead of closed, but not silently.

## Re-review corrections applied — 2026-07-30

All three findings from the second pass were valid.

**1. The "no extra request" claim was false, and now the code makes it true.** `appendAsyncWaitingRows` called `fetchTestsRegister()` *alongside* `fetchReviewQueue()` — two identical `GET /api/cockpit/review-queue`, while the comment beside them asserted no second request was needed. It now reads the register off the queue payload it already has, via a new `testsFromQueue(payload)` helper that `fetchTestsRegister` also uses. The dead `const tests = testsRegister;` alias is gone.

Measured rather than asserted this time, by wrapping `window.fetch` in the live app and rendering the overview: **`/api/cockpit/review-queue` goes from 3 calls to 2**, `/api/cockpit/decisions` 1. The two remaining are two genuinely different consumers (`fillRecordColumn` via `fetchTestsRegister`, and `appendAsyncWaitingRows`) each fetching once — so the comment's claim is now scoped to the function it sits in, which is what makes it true.

This is the finding worth keeping visible: **a note asserting a property the code lacks, written inside the fix for that exact defect class.** The comment was describing the fix I meant to write rather than the one I wrote, which is precisely how criterion 5 of [[REQ-0025]] came to be ticked false.

**2. "157 → 0" was wrong; it is 149 → 0.** Corrected in `cockpit.py`, `renderer.ts` and the test docstring. `fetchRecordNotes` filtered on `if (!item.id || !rel) continue`, so the harvest was items with **both**: 161 in the payload, 157 with a resolvable rel, 149 with id *and* rel. Quoting 157 counted the 8 items with an empty `id` — the very population the second half of that filter existed to drop, and the reason the references card never rendered. Reading one half of a two-clause filter is the same species of error as the original defect.

**3. The cross-process contract now has guards.** **Two** of the four scenarios the re-review demonstrated are closed, plus a fifth it did not raise (a registered-but-broken handler). Round three caught the miscount, and how it happened is worth recording: crediting the HTTP-handler test as one of the four let the third scenario disappear from the tally, so it went from open-and-known to silently uncounted. Closed below; the two that remain open are named at the end.

- `test_the_record_columns_endpoints_exist_on_both_sides` — asserts each route literal appears in **both** `server.py` and the renderer. Verified by mutation: a renderer typo (`/api/cockpit/decision`) fails it, and a server rename (`/api/cockpit/adrs`) fails it *and* the HTTP test.
- `test_the_decisions_route_answers_through_the_http_handler` — spins the real handler on an ephemeral port and fetches the route, catching a registered-but-broken handler that literal matching cannot.
- `test_decisions_have_a_payload_of_their_own` now asserts every entry has a `rel` that resolves on disk. A payload returning ids with blank rels passed the id-only version of this test — confirmed by mutation before and after.

**Still open, and disclosed rather than papered over — two, not one:**

- Inverting `resp.ok` in `fetchDecisions` so it returns `[]` on **success** still passes all 27 tests. Round three found this one uncounted rather than accepted, which is worse than leaving it open.
- `fetchTestsRegister` reading `registers.reviewed` instead of `registers.tests` would still pass. Closing either means asserting a source string, which produces a guard that passes when the wiring is right *and* when it is wrong-but-spelled-right — worse than the gap, because it would look like coverage. Independent review agreed on that reasoning for both. The honest mitigation is that the payload tests assert contents and the desk renders the registers side by side, where a swap is immediately visible.

**Also fixed:** `desktop/dist/` was 7 minutes staler than `renderer.ts` when the first fix was verified, so `test_desktop_build_is_not_stale` was failing and the "live pane verified" claim was not reproducible from the tree. Rebuilt and re-verified.

## Independent review, round three — 2026-07-30, approved

All three findings verified as fixed, by mutation rather than by reading.

**1.** `appendAsyncWaitingRows` now takes the register off the queue payload it already holds. Confirmed structurally, and confirmed the comment is now true of the code beside it: `grep -n "api/cockpit/review-queue" renderer.ts` gives two sites, and `fetchTestsRegister` delegates to `fetchReviewQueue` rather than issuing its own GET. Splitting `testsFromQueue` out of the fetch is the right shape — the caller that has the payload uses it, the caller that does not still gets one call.

**2.** "149 → 0" is correct in all three places, and the accompanying explanation of *why* 157 was wrong — that it read one clause of a two-clause filter — is more useful than the corrected number.

**3.** Three mutations re-run against the new guards: a blank `rel` in the payload now fails (it passed before), a renderer route typo now fails, and a server route rename fails two tests. I added one the note did not claim: making `decisions_payload` raise inside the handler fails the HTTP test, so registered-but-broken is genuinely covered, and a `rel` pointing at a nonexistent file fails too.

**Two corrections, neither blocking.**

**"Three of the four scenarios are closed" is two of four, plus one I had not raised.** My four were: blank `rel`; a route typo on either side; `fetchDecisions` swallowing a good response; the wrong register key. The first two are closed. The third — inverting the `resp.ok` check so `fetchDecisions` returns `[]` on success — **still passes all 27 assertions and is not disclosed anywhere**, unlike the fourth, which is. It belongs in the same "still open, disclosed" paragraph as the register-key case, for the same reason and in one sentence. The HTTP-handler test is a genuine addition, but it closes a fifth scenario rather than one of the four, and counting it as one of them is how the third disappeared. That is this issue's own defect class, in its own arithmetic — small, but worth the sentence given how much of this note is about exactly that.

**The new parity test has a narrow hole.** `test_the_record_columns_endpoints_exist_on_both_sides` asserts `route in _renderer_code()`, and `_renderer_code()` strips only lines whose first non-space characters are `//`. A trailing comment on a code line survives, so a typo'd fetch plus `// was /api/cockpit/decisions` on the same line satisfies it — verified. Contrived as a scenario; a one-line fix if you want it airtight (strip trailing comments too, or require the literal to appear inside a `fetch(` call).

**On the fourth open mutation you asked about: I agree, leave it open.** Asserting `registers.tests` as a string in source would produce a guard that passes when the wiring is right *and* when it is wrong-but-spelled-right — worse than the gap, because it would look like coverage. The real closure is a DOM-level test of the record column, which is larger than this issue should carry, and [[TST-0022]]'s `## Adequacy` already names "the renderer is covered only by `tsc` and source-parsing assertions" as the standing limit. Naming it there is the correct disposition. Miss 3 above belongs in the same bucket.
