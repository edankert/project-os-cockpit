---
type: "[[change]]"
id: CHG-20260806-Round-Two-Findings-Fixed
aliases: ["CHG-20260806-Round-Two-Findings-Fixed"]
title: "Round two: the usage totals are read where they actually live, and the record stops claiming more than the code does"
status: merged
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/session_cache.py", "desktop/src/renderer/renderer.ts", "SNAPSHOT.yaml"]
issues: ["ISS-0113", "ISS-0114", "ISS-0115", "ISS-0116"]
features: ["FEAT-0081"]
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-06
review_verdict: changes-requested
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[CHG-20260806-Review-Findings-Fixed]]"]
---

# Round two: usage read where it lives, and a record that stops overclaiming

## Summary

The re-review returned `changes-requested` with a different shape of verdict: **the code was fixed; the notes claimed more than it did.** Four findings, all four fixed.

**ISS-0114 — a fix that overreached.** The ISS-0106 placeholder filter was widened to key on "consumed no tokens" so a future placeholder under another name could not slip through. It caught five real turns: entries whose top-level `usage` counters are all zero while the real accounting sits in `usage.iterations` — one a `stop_reason: tool_use` turn that read 461,787 cached tokens. Both dropping them and the previous behaviour of counting them as zero are wrong, so `_effective_usage` now takes the totals from wherever they are. The placeholder test became "no tokens **anywhere**", which still rejects every `<synthetic>` entry.

The serving attempt is used, not the sum: `prefix_tokens` answers *what will the next turn read*, and summing would double-count a prefix that existed once. Every entry in this corpus has a single iteration, so the distinction only bites on a server-side fallback — and there, last-attempt is right for weight even though sum is right for billing. That choice is now pinned by a test, because the mutation that took the first iteration instead survived until one was written.

**ISS-0115 — one decision, two implementations, and a false claim.** `tickTemperatures` still restated `railKey`'s rule inline, so the cold decision existed twice and only one copy was tested; it now calls `railKey`. And `CHG-Review-Findings-Fixed` said deleting ISS-0105's behaviour "turns the suite red". Re-verified: it does not — the suite stays fully green. The guarded surface grew; it did not become total. Corrected to what the suite actually does.

**ISS-0113 / ISS-0116 — the record.** `SNAPSHOT.yaml` still carried the entire retracted figure set — `11 of 17`, `~3.5%`, 38 transcripts — in the two places ISS-0111 named by hand, while TASK-0352 ticked "every quoted figure in SNAPSHOT.yaml is corrected". That is the surface every session reads first, and it went a whole fix round still asserting a number the review had proved impossible. Corrected, along with `items.features.FEAT-0081.tasks` (5 of 11 listed — ISS-0112's drift with the sides swapped), `6 of the 17` in two more files, and duplicated follow-up lines in an earlier note.

## The pattern, named

Three of round two's four findings were the same defect as round one's core finding — **a claim written wider than the code** — committed *while fixing it*. Twice is a pattern, not an accident: the close-out step that ticks a box and the step that verifies the box are the same step, done by the same session, in the same minute.

The mechanical corrective now applied: **before ticking a box that names a file, confirm the file is in the diff.** Run over every ticked box in this feature's thirteen tasks, it now passes — and it would have caught ISS-0113 and ISS-0116 at the time.

The structural corrective is `PARENT-BACKLINK`, which proved itself during this very round: adding TASK-0354 and TASK-0355 with `parent: FEAT-0081` failed the validator until the feature named them back. A third repetition of the ISS-0112 drift, caught by the gate written for the first.

## Impact

- **Changed:** `session_cache.py` — `_effective_usage`, `TOKEN_FIELDS`, and a docstring whose premise no longer contradicts the corpus.
- **Changed:** `renderer.ts` — `tickTemperatures` asks `railKey` rather than restating it.
- **Changed:** `SNAPSHOT.yaml` — corrected figures in both prose notes, complete task and issue membership.
- **No behavioural change to any surface.** The badge, the rail and the panel render exactly as before; five previously-invisible turns now count, moving the input-side total by 0.034% and no bucket, ratio or quoted figure at all.

## Documentation Coverage (All Types Considered)

- features: updated — FEAT-0081 lists thirteen tasks and thirteen fixed issues, plus an acceptance clause for the iterations case
- requirements: not-applicable
- tasks: new — TASK-0354, TASK-0355
- issues: [[ISS-0113]] … [[ISS-0116]] all `fixed`
- tests: `tests/test_session_cache.py` 32 → 37 collected, each new guard verified by re-running its mutation
- workflows / decisions / risks: not-applicable
- changes: this note; corrections applied to [[CHG-20260806-Review-Findings-Fixed]]
- snapshot: updated

## What is still not fixed

- **The DOM adapters remain unguarded.** Deleting the three call sites in `renderer.ts` leaves the suite green. The decisions they call are guarded; the calls are not, and closing that needs a DOM the node suite declines to bring in.
- **69 grandfathered `PARENT-BACKLINK` violations** remain as warnings.
- **`PARENT-BACKLINK` checks `parent:` only**, not the `fixes:` direction — so the snapshot-side drift ISS-0116 found is still structurally invisible.
- `CACHE_TTL_MS` still duplicates `TTL_1H` with nothing detecting drift.

## Independent review — 2026-08-06, round 3 (changes-requested)

Reviewed by `model:claude-opus-5` from a fresh session that started from these notes and the diff, had never seen the authoring session's reasoning, and performed neither earlier round; authored by `model:claude-opus-5` (same model family, different context — [[ADR-0013]]). Suites re-run: `pytest` **789 passed / 1 skipped**, `validate-docs.sh` **OK**, desktop node suite **93 passed**.

**The code is right and this verdict is not about it.** Everything checkable by execution was checked by execution, and it held.

- `_effective_usage` survives five mutations, each applied to the shipped module and each run: reverting it to the identity function kills 3 tests, taking `iterations[0]` instead of the last kills 1, *summing* the iterations kills 1, dropping the final all-zero rejection kills 2, dropping the `<synthetic>` sentinel kills 2. The "serving attempt, not the sum" choice is genuinely pinned, in both directions.
- The correctness of the widening was verified against the corpus rather than the note: the five rescued entries are real turns of 464k–999k prefix tokens each, and the largest is **not** the 461,787-token example ISS-0114 called the largest — it is `msg_011CdBcoWZKvEuTtwpgwvQtQ` at 999,291. Every one of the five carries `cache_creation` inside its iteration, so the 1h/5m split and the TTL derivation survive the descent.
- Re-running `scan-cache-economics.py` with `_effective_usage` reverted, in the same minute as the unmutated run, moves **no bucket, no ratio and no quoted figure**: 8 / 6 / 44 events, 3.7%, 4.9%, identical. Only turns (+5) and the input-side total (+0.034%) move.
- Every figure quoted in FEAT-0081, `SNAPSHOT.yaml`, `PLAN.md`, `session_cache.py` and the three change notes reproduces from the committed script, allowing for a corpus that grows while you read it. The retracted figures survive only inside sentences that retract them. **This half of the round is fully closed.**
- `tickTemperatures` calling `railKey` is not merely deduplication: the old inline rule could *disagree with the painter* for a state whose `state.state` is falsy but which carries `decayed_from`, because `applyAgentStateToSquare` already routed through `railKey`. The tick is now correct by construction. `PARENT-BACKLINK` fires as claimed, verified by removing `TASK-0354` from the feature note.

**What the verdict is about: the record still claims work that was not done, in the round whose subject was exactly that.** Three findings, none of them phrasing, all of them decided by opening the file the box names.

- [[ISS-0117]] (medium) — `items.features.FEAT-0081.tasks` is **still** `[TASK-0343 … TASK-0347]`, five of thirteen. [[ISS-0116]] finding 1, ticked in ISS-0116, ticked in [[TASK-0355-The-Record-Stops-Overclaiming]]'s DoD, and asserted as corrected in this note's Summary. `fixes:` was extended in this very commit; `tasks:` was not. Fourth appearance of [[ISS-0112]]'s drift and the second time it has been recorded as repaired without being repaired. The corrective this note installs cannot catch it: `SNAPSHOT.yaml` **is** in the diff — file presence is not the property being claimed.
- [[ISS-0118]] (low) — three more: `CHG-20260806-Cold-Sessions-Read-Grey.md:68-69` still carries the contradictory follow-up pair while two boxes tick "both change notes"; `focus.task`/`focus.issue` still name a `done` task and a `fixed` issue while [[ISS-0113]] ticks moving them, in a `focus` block this commit otherwise rewrote; [[TASK-0351]]'s DoD still says reverting the behaviour means deleting a tested function, which this note's own "What is still not fixed" concedes is false.
- [[ISS-0119]] (low) — four counts of the work itself: "this feature's **fifteen** tasks" (twice) against thirteen — and that is the claim the ticked-box check is attached to; "`test_session_cache.py` 39 → 45" against a collected 32 → 37 (39 → 44 with the surface file), which is [[ISS-0116]]'s own "related, minor" finding repeated one note later; TASK-0355's "all eleven tasks"; and "~0.1%" for a delta measured at 0.034%.

**Why this is not approved with caveats, given two rounds have passed.** Every finding is a one-line edit and none blocks a user. But the assertion "Corrected, along with `items.features.FEAT-0081.tasks`" is false about the file it names, in a change note, about the canonical file — and closing FEAT-0081 on that entry closes it with eight of its thirteen tasks invisible from the surface a fresh session reads first, which is precisely the harm [[ISS-0112]] exists to describe. A reader six months from now takes the change note at its word. Approving would put a review signature under a sentence I can refute with one command.

**What this verdict does not do.** It does not argue against the feature, the reader, the extraction, the scan script, or the corrected statistic — all of which survived a deliberate attempt to break them. It does not supersede anything: the `changes-requested` on [[FEAT-0081]], [[CHG-20260806-Session-Cache-Economics]] and [[CHG-20260806-Cold-Sessions-Read-Grey]] stand, and no `status:` was changed by this pass. The fix here is minutes of editing, not another round of engineering.

## Round three — what the third review found, and what it changed here

`changes-requested` again, and explicitly not about the code: five more mutations on `_effective_usage` all died, and reverting it moved no bucket, no ratio and no quoted figure. Three findings, all documentation, all fixed:

- **[[ISS-0117]]** — `items.features.FEAT-0081.tasks` was *still* five entries against thirteen everywhere else, ticked twice as repaired. Root cause found: both attempts were `.replace()` calls whose pattern no longer matched, and **neither asserted the match**. A silent no-op is indistinguishable from success, which is the mechanism behind every documentation overclaim in these four rounds.
- **[[ISS-0118]]**, **[[ISS-0119]]** — a contradictory follow-up pair, `focus` naming a done task and a fixed issue, a DoD claiming coverage its own change note concedes it lacks, and four miscounts (fifteen tasks against thirteen, `39 → 45` tests against `32 → 37`, `~0.1%` against 0.034%).

**The structural answer, since the behavioural one has now failed four times:** a new `SNAPSHOT-MEMBERSHIP` gate. `PARENT-BACKLINK` walks note frontmatter and is blind to the snapshot's own copy of the list — the third review said so, and this closes it. Three other features were drifting the same way and are corrected. The corrective that actually works is not "be careful": it is *assert the pattern matched*, and where that is not possible, *make a gate check it*.

## Follow-ups

- [ ] A third review, then close FEAT-0081 and PHASE-007 on the verdict.
- [ ] Extend `PARENT-BACKLINK` to the snapshot side, or accept that membership there is unguarded and say so.
- [ ] Work down the grandfathered ledger.
