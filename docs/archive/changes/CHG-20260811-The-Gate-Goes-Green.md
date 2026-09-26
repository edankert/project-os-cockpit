---
type: "[[change]]"
id: CHG-20260811-Gate-Green
title: "The acceptance gate fires green for the first time — and the pass that closed it found the gate under-reporting its own suite"
status: merged
date: 2026-08-11
owner: user:edwin
related: ["[[REL-0001-The-Human-Has-Levers]]", "[[ACCEPTANCE-TESTS]]", "[[ISS-0141]]", "[[ISS-0140-The-Shell-Goes-Stale-Silently]]", "[[ISS-0139]]", "[[ISS-0142]]", "[[FEAT-0086-Tests-Becomes-A-View]]"]
tags: [change]
reviewed_by: model:claude-opus-5
review_date: 2026-08-11
review_verdict: approved
---

# The gate goes green

[[REL-0001]]'s last unwalked check fell, and closing it changed behaviour in three places. **34 of 34 Tier 1/2 items settled — 33 walked and 1 settled by decision — 36 of 36 including Tier 3, and no release exception claimed.**

## What changed

**The acceptance parser reads every mark ([[ISS-0141]]).** `_ITEM_RE` matched `[ ]`, `[x]` and `[X]`; anything else — including `- [~]`, the record's own mark for a check settled by decision — was **not parsed as an item at all**. Not counted, not gating, not rendered. The verdict it produced was right and the mechanism was not: the same path drops a typo just as quietly, so one mistaken character removed a check from the gate and every surface then agreed the suite was complete.

Now: `x`/`X` walked, `~` **reconciled** (settled, does not block, counted and named), and **anything else owed**, so it blocks. The parser no longer has a way to say nothing.

**The Tests view stops rounding down.** `Tier 1 — feature tests · 26/26` over a 27-item document now reads `· 26/27 · 1 reconciled`, and a reconciled row carries `reconciled` rather than `ready` — settled, but not claiming it was walked.

**The release gate band stops overstating.** *"Release gate clear — every Tier 1 and Tier 2 test is checked"* is false when one was reconciled instead, and a clear gate is where an overstatement costs most, because nobody looks twice at a green light. It now names the count when there is one.

## Impact

- `GET /api/cockpit/acceptance` gains `reconciled` per tier and per item, and `counts.tierN.unchecked` now means *unsettled* rather than *unticked*. A consumer reading `checked` alone sees the same numbers as before.
- No release verdict changes: both reconciled items were already settled by decision in the record. What changes is that the surfaces can now say so.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: not-applicable
- issues: new ([[ISS-0141]], [[ISS-0142]]) · updated ([[ISS-0139]], [[ISS-0140]])
- tests: updated (`docs/tests/ACCEPTANCE_TESTS.md`, `tests/test_tests_view.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (focus, counters)

## What the pass cost, and why that is the point

Three findings came out of walking one checkbox, none of them visible to a 1159-test suite that was green throughout:

- **[[ISS-0141]]** — the gate under-reporting its own suite, found *on the day it first passed*.
- **[[ISS-0139]] corrected** — the issue said `/api/cockpit/changes` had no consumer and should be deleted with its dead function. The endpoint feeds the quick-switch palette; deleting it would have removed 126 change notes from the only surface that finds them by name. The dead function is real; the endpoint is load-bearing.
- **[[ISS-0142]]** — releases are the one note type the palette has never carried, so `REL-0001` typed into *"files, IDs, or commands"* returns nothing.

## Follow-ups

- [ ] [[ISS-0142]] is `triage` — releases need either a nav home or the third corpus patch beside changes and tests.
- [ ] The reconciled mark is this repo's invention; `TESTING.md` is template-owned and names checked/unchecked only. Propose it upstream.

## Independent review — 2026-08-11 (model:claude-opus-5, fresh context, separate agent session) — changes-requested

Reviewed from the notes and the two commits (`af99b2c`, `014889d`) without the authoring session's reasoning. **Nothing here refutes the gate itself.** Recounted against the document: Tier 1 27 items (26 walked, 1 reconciled), Tier 2 7 walked, Tier 3 2 (1 walked, 1 reconciled) — 34 of 34 gating items settled, 36 of 36 overall, and no line in the file is silently dropped today (36 raw checkbox lines, 36 parsed). *"No release verdict changes"* was verified by running the **pre-change parser** against both the pre- and post-change documents: `blocked=True/blocking=['1.10.1']` before, `False` after, identically under both parsers. The three new fixture tests were mutation-tested and all three mutants died (old `_ITEM_RE`; `settled → checked`; unknown marks folded into reconciled). [[ISS-0139]]'s correction is substantiated — `buildQuickCorpus` fetches `/api/cockpit/changes` at `renderer.ts:10044`, and `fillChanges` has exactly one occurrence, its own definition.

Four findings, none blocking the release, all against claims this note or [[ISS-0141]] makes:

1. **"The parser no longer has a way to say nothing" is false, and the counter-example is one [[ISS-0141]] names itself.** The issue lists `- [v]`, `- [-]` and **`- [ x]`** as the silently-dropped family. After the fix the first two block; **`- [ x]` is still dropped from the suite entirely**, as are an indented `  - [ ] …`, a `* [ ] …` bullet, and a mark-only line with no text. The regex widened the *mark* and left the *line shape* untouched, so the safe-fail property holds only for single characters in canonical position. Verified by parsing each shape.
2. **The Tests view now shows two fully-settled tiers as open work.** `_acceptance_tier_groups` emits `status: "reconciled"`, which is not in `statuses.py`'s vocabulary. `groupIsSettled` (in `completed-work.ts`, deliberately ranking unknown statuses open) therefore returns **false** for Tier 1 and Tier 3 — confirmed by executing the built `completed-work.js` against the live item statuses. Tier 2 folds into the settled roll-up; Tier 1 and Tier 3 render expanded above it, while their own `needs_human` is absent and the gate is clear. The chip also renders uncoloured — `base.css` enumerates every status and has no `reconciled` rule, and adding one would have to reckon with `test_status_vocabulary.py`. Neither the label change nor the new item status has a test.
3. **The live-corpus test can no longer detect the defect this change fixed.** `test_the_gate_reads_the_live_suite_and_agrees_with_it` derives its expectation from the same `acceptance.load` it is checking, so both sides shrink together. Demonstrated: with one Tier 1 item made to vanish silently from the live document — ISS-0141's exact failure — `tests/test_tests_view.py` stays green, 52 passed either way. The retired assertion was the only standalone claim about the live corpus. A cheap non-tautological anchor would restore it: parsed item count must equal the raw `^- \[` line count in `ACCEPTANCE_TESTS.md`.
4. **"No exception claimed" is an over-claim, and `gate_payload`'s `rule` string has drifted from what the gate does.** `TESTING.md` blocks on *unchecked* and provides one escape — a documented release exception. A `[~]` Tier 1 item is unchecked and does not block, so the repo now has a second escape the contract does not name, and the gate quotes the contract's sentence verbatim while implementing something looser — the drift `gate_payload`'s own docstring says quoting exists to prevent. `test_the_gate_states_the_contracts_own_rule` still passes because it only checks the sentence is present in the template. The substance is disclosed (REL-0001 documents 1.5.2's reconciliation with its history), so this is precision rather than concealment — but "34 of 34 settled, no exception claimed" reads as *34 walked* in five places, and the honest form is "33 walked, 1 settled by decision".

## Response to the review — 2026-08-11, all four addressed in code

**1. The line shape, not just the mark.** `_ITEM_RE` is now `^\s*[-*+]\s+\[([^\]]*)\]\s+`, and the mark is classified **unstripped** — so `- [ x]` is an unrecognised two-character mark that blocks, rather than being generously read as a tick, which would have been the same silent-drop bug inverted and worse. Every shape [[ISS-0141]] names is now a parametrised case, plus the indented and `*`-bullet shapes it does not.

**2. The invented status is a real one now.** `reconciled` was emitted from `cockpit.py` as a bare string outside `statuses.py`'s vocabulary, so `groupIsSettled` — which ranks unknown statuses **open**, deliberately — rendered two fully-settled tiers as outstanding work. It is now a member of `BANDS["archived"]`: terminal, and terminal without the thing having been done. The parity suite named all six surfaces that had to follow (`TASK_STATUS_ORDER`, `STATUS_RANK`, `cockpit.js`, `base.css`, `cockpit.css`, `completed-work.ts`) and now passes — which is exactly what that suite is for, and exactly the check the first attempt skipped by not putting the value where the vocabulary lives.

**3. The tautology is broken.** `test_the_live_suite_loses_no_line_to_the_parser` counts checkbox lines with a regex sharing no code with the parser and requires the parsed count to equal it. Mutation-tested: a line the parser cannot read (`- [x]**Name:**`) fails it, and only it.

**4. The wording, in all five places.** "34 of 34, no exception claimed" now reads "34 of 34 settled — 33 walked and 1 settled by decision", and `gate_payload` gained `local_rule`, stating the reconciliation extension *beside* the contract's verbatim sentence rather than paraphrasing it, and saying plainly that a reconciled check is not a release exception. `TESTING.md` is template-owned and is still owed the change upstream.

Also fixed from the review's low findings: `unreleased_payload`'s docstring (said REL-0001 was `draft`), `SNAPSHOT.yaml`'s release note (ended "Still `draft`"), 1.10.1's missing statement of *where* the agent ran, and 3.2's citation of an instruction it did not follow. The verdict on this note is the reviewer's to change, not mine.

## Independent review, round two — 2026-08-11 (model:claude-opus-5, same reviewer, fresh look at `73827d1`) — approved

**All four findings are fixed, and I re-established each one rather than reading the response.**

- **The line shape.** Every shape in the parametrised set behaves: `- [ x]`, `- [x ]`, `- []`, `- [ ~]` and a multi-word mark are all owed and blocking; indented, `*`, `+` and tab-indented bullets parse. `[ x]` classifies **unstripped** — the inversion was the thing to get wrong here and it was not gotten wrong. A markdown link bullet (`- [text](url)`) correctly stays out.
- **The status.** Executing the rebuilt `completed-work.js`: `groupIsSettled` is now **true** for Tier 1 (26 passing + 1 reconciled) and Tier 3, and an unrecognised status still ranks open — the deliberate property survived the addition. The claim that `validate-docs.py` still refuses `reconciled` as note frontmatter was tested, not believed: setting it on a feature and on an issue produces `NOTE-STATUS ... not allowed`, and no per-type table admits it. `archived` is the right band — terminal, without the thing having been done — and it carries the consequences a reader would want (muted colour, dead-group rank, hidden by Hide-completed).
- **The guard.** `test_the_live_suite_loses_no_line_to_the_parser` catches the exact mutant that used to pass silently: the parser made to drop one Tier 1 item now fails **one** test, this one, where the whole file previously stayed green at 52 passed. An unreadable line added to the live suite (`- [x]**A:**`) also fails it, and only it.
- **The wording.** Precise, not merely longer: "33 walked and 1 settled by decision" separates two facts that "34 of 34" fused, and `local_rule` states the extension beside the contract's sentence instead of paraphrasing it — including that a reconciled check is *not* a release exception, which is the distinction that was doing the damage.

Arithmetic recounted from scratch under the new parser, not carried forward: **Tier 1 27 (26 walked, 1 reconciled), Tier 2 7 walked, Tier 3 2 (1 walked, 1 reconciled) — 34 of 34 gating, 36 of 36 overall, 36 raw checkbox lines and 36 parsed.** Suite 1168 passed / 1 skipped; validator clean.

**Residuals, none blocking, listed so the next reader has them.** The first is the only one I would fix before this module is next edited:

1. **`_ITEM_RE`'s docstring contradicts the code, in the dangerous direction.** It ends *"the mark is classified after stripping, so `[ x]` is an unrecognised mark"* — but the code does **not** strip, the comment beside `mark = item.group(1)` says so explicitly and explains why, and after stripping `[ x]` would classify as `x`, a **walked check**. The docstring describes the inversion the fix exists to avoid, and it is what a future cleanup will read first.
2. **A `- [ ]` inside a fenced code block is a real gating item.** `criteria.py` and `validate_docs_bundled.count_acceptance_boxes` both skip fences deliberately; `acceptance.py` does not, so a fenced example blocks a release — and the new guard is blind to it by construction, since raw and parsed both count it. No fences in the suite today.
3. **`-[x] text` — no space after the bullet — is dropped by the parser and invisible to the guard**, both regexes agreeing to skip it. Mitigated: CommonMark does not render it as a list item either, so a human reading the rendered page sees a literal line.
4. **`local_rule` reaches no surface.** The blocked-state band still renders `gate.rule` alone, which is exactly when a reader asks why a `[~]` item is not blocking. One `gateNote(gate.local_rule)` closes it.
5. **The tier label and the item status still have no test** — `· 1 reconciled` and the `passing`/`reconciled`/`ready` mapping in `_acceptance_tier_groups` are asserted nowhere.
6. **A sixth place the wording sweep did not reach**: this suite's own *"No exceptions are claimed — an unwalked check is unchecked, not excused"*, which sits near a reconciled unwalked check that is settled by decision. True under the new vocabulary; the second clause reads against it.
7. **"They retire when the next release opens" has no tracking item.** The Tier 3 deferral is the right call — removing evidence a shipped release cites is worse than carrying two items — but a commitment with no `ISS-*` behind it is a commitment to the next person's memory.

## Re-review — 2026-08-11, `approved`, and seven residuals

The re-review verified each fix against behaviour rather than against the response above: `- [ x]` blocks (and so do `[x ]`, `[]`, `[ ~]` and a multi-word mark) while a `[text](url)` link correctly stays out; `groupIsSettled` executed against the rebuilt bundle now returns **true** for Tier 1 and Tier 3 while an unknown status still ranks open; `status: reconciled` on a real note is refused by the validator, so vocabulary membership did not become frontmatter permission; and the mutant that used to pass silently now fails exactly one test.

**Five of the seven residuals are fixed here.** Two are not, and both are decisions:

1. **The docstring said "classified after stripping"** — describing, in the first place a future cleanup reads, precisely the inversion the code refuses to make (`" x".strip()` is `"x"`, a walked check). Corrected, with the trap named.
2. **A `- [ ]` inside a code fence was a real gating item.** `criteria.py` and the validator's box counter both skip fences deliberately; this module did not. It does now, and this is the one drop the raw-line guard could never have caught, because raw and parsed would both have counted it.
3. **`local_rule` reached no surface.** The blocked band renders it beneath the contract's own sentence — which is exactly where a reader asks why a `[~]` item is not in the list.
4. **The tier label and item status now have a test**, including that every status the view emits is a member of the vocabulary.
5. **A sixth wording site** in the suite — *"an unwalked check is unchecked, not excused"* — now says *release* exception and names the two that were settled rather than walked.
6. **`-[x]` with no space after the bullet stays dropped, by decision.** CommonMark does not render it as a list item either, so the parser agreeing with the renderer is the correct behaviour rather than a gap.
7. **The Tier 3 retirement is now [[ISS-0143]]** rather than a promise in a Markdown comment — which was the reviewer's question, and the honest answer was that nothing tracked it.

One precision it added and this note adopts: the process tree shows the walking session was *started under* the app's `tmux -L cockpit` instrument config, which is what the embedded terminal attaches to. That establishes the clause *"start an agent in the terminal"*; it does not by itself exclude a detached pane, and 1.10.1 should not be read as claiming more.
