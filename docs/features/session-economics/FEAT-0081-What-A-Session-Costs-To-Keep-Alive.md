---
type: "[[feature]]"
id: FEAT-0081
aliases: ["FEAT-0081"]
title: "What a session costs to keep alive — context weight, cache state, and the invalidations nobody sees"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
goal: "The strip already shows ctx% and a dollar total; neither says what the next turn will cost. Read the transcript the cockpit already knows the path to, and say whether the cache is warm, what the prefix weighs, and what resuming cold would cost."
requirements: []
tasks:
  - "[[TASK-0343-The-Cache-Reader]]"
  - "[[TASK-0344-Warm-Cooling-Cold-In-The-Strip]]"
  - "[[TASK-0345-Model-Switch-Named-Where-It-Happens]]"
  - "[[TASK-0346-Cold-Reads-Grey-And-Actually-Ticks]]"
  - "[[TASK-0347-Cold-Sessions-Leave-The-Needs-You-List]]"
  - "[[TASK-0348-Synthetic-Entries-Are-Not-Turns]]"
  - "[[TASK-0349-The-Switch-Announcement-Expires]]"
  - "[[TASK-0350-Guards-For-The-Bounded-Read]]"
  - "[[TASK-0351-Pure-Decisions-For-The-Rail-And-The-Badge]]"
  - "[[TASK-0352-The-Scan-Committed-And-The-Figures-Corrected]]"
  - "[[TASK-0353-The-Feature-Note-Catches-Up-And-Links-Are-Checked-Both-Ways]]"
  - "[[TASK-0354-Usage-Is-Read-Where-It-Lives]]"
  - "[[TASK-0355-The-Record-Stops-Overclaiming]]"
  - "[[TASK-0356-The-Snapshot-Membership-Gate]]"
fixes: ["ISS-0104", "ISS-0105", "ISS-0106", "ISS-0107", "ISS-0108", "ISS-0109", "ISS-0110", "ISS-0111", "ISS-0112", "ISS-0113", "ISS-0114", "ISS-0115", "ISS-0116", "ISS-0117", "ISS-0118", "ISS-0119"]
release: ""
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-06
review_verdict: approved
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0020-Agent-Activity-Surfaces]]", "[[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]", "[[ISS-0105-The-Rail-Pulses-The-Same-For-Two-Minutes-And-Two-Hundred-Hours]]"]
tests: []
---

# What a session costs to keep alive

## Goal

Edwin asked whether cache staleness could be identified, highlighted, or automated away. Measuring first changed the answer, and the feature is shaped by what the measurement found rather than by the original worry.

Reproduce any figure here with `python3 tools/scripts/scan-cache-economics.py` — it imports the shipped reader, so these numbers and the product's cannot drift apart. Run 2026-08-06 over 42 transcripts (21,862 deduplicated assistant turns):

| | | |
|---|---:|---|
| Cache **reads** | ≈$5,340 | 79% of input-side spend — the cost of carrying context |
| Cache **writes** | ≈$1,448 | 21% |
| — **staleness**: TTL expiry, >60 min idle | ≈$250 | 44 events, **3.7%** of input-side spend |
| — model switch ([[ISS-0104]]) | ≈$61 | 8 events |
| — no discoverable cause | ≈$25 | 6 events |
| **All avoidable re-writes** | ≈$336 | **4.9%** of input-side spend |

**Staleness means TTL expiry** — the cache lapsing on its own clock — and it is 3.7% of the input bill. A model switch is *invalidation*, not staleness. An earlier draft of this note quoted one word for both and the ratio of only one of them ([[ISS-0111]]).

Either way the shape holds: the 20× larger number is the weight of the context itself, and nothing in the cockpit says what that weight is in tokens — `ctx 62%` is a fill ratio against a window, not a cost.

So the feature is *session economics*, not *cache warnings*: what this session weighs, what state its cache is in, and what the next turn costs under each.

## The automation that must not be built

A keep-warm ping costs **2× the full prefix, every ping**. Going cold and paying on return costs 2× **once**. Re-warming an idle session is therefore strictly more expensive than letting it expire, for any idle period longer than the TTL — there is no cheap keep-alive, and `max_tokens: 0` pre-warming does not change the arithmetic (it pays the same write).

Recorded here because "just refresh the cache in the background" is the obvious feature request, it sounds like a saving, and it would raise the bill. The honest lever is **behavioural**: knowing the prefix is cold and large *before* deciding to resume it, so starting fresh stays on the table.

## Scope

### In scope
- A reader over the session transcript (`transcript_path`, already stored per session since [[FEAT-0019]]) that yields prefix weight, cache state, last-turn model, and full-prefix re-write events. Tail-read for live state, full scan for the retrospective, both cached against mtime.
- The strip says **warm / cooling / cold**, carries the prefix weight in tokens, and when cold names the cost of resuming.
- Model-switch invalidation named at the point it happens ([[ISS-0104]]), as a **recent event that expires** rather than a permanent label ([[ISS-0107]]).
- A retrospective per-repo figure: what full-prefix re-writes cost here, split by cause. Per-workspace — `tools/scripts/scan-cache-economics.py` is the cross-fleet measurement, and the two answer different questions.
- **The rail and the NEEDS YOU list learn the same age** ([[ISS-0105]]): a session past the TTL reads grey rather than pulsing amber, and leaves the list, so amber-pulse means *waiting and still cheap to resume*. Reusing the existing grey, never a new colour or animation.

### Out of scope
- **Any background keep-warm, pre-warm, or cache-refresh mechanism** — see above; it costs more than it saves.
- Blocking or intercepting a model switch. The cockpit does not own the Claude Code session; it reports.
- Cross-fleet roll-up of the retrospective figure. Per-repo first; the fleet view is a later call once the per-repo number has proven it earns its space.
- Changing how Claude Code itself caches. Not ours.

## Acceptance

- Given a live session, the strip shows its prefix weight in tokens and one of `warm` / `cooling <n>m` / `cold`.
- Given a cold live session, the strip names the estimated cost of the next turn's re-write, and that estimate is derived from the transcript's own last-turn token counts rather than a guess.
- Given a session whose last turn changed model while discarding ≥50k cached tokens, that event is reported with the discarded token count.
- Given a repo with transcripts, the retrospective figure reports full-prefix re-writes split into session-start / TTL-expiry / sub-hour-invalidation, and the sub-hour bucket distinguishes model-switch from other.
- Given a session past its TTL, the rail square reads grey rather than pulsing, and the transition happens **on a clock** with no inbound event — the premise is a session where nothing is occurring.
- Given a session past its TTL, it is absent from the NEEDS YOU list, and present again if it takes another turn.
- Given an API-error placeholder in a transcript, it is not counted as a turn, does not become the previous turn, and cannot produce a model-switch classification. A turn whose totals live in `usage.iterations` rather than at the top level is **not** a placeholder and keeps its real figures.
- Given a session whose last turn switched model, the switch is announced while it is fresh and then gives way to the standing warm / cooling / cold state; the badge's colour always follows the actual temperature.
- Given a turn with no usable timestamp, no badge is rendered at all — absence is never reported as a confident `cold`.
- Reading a 30MB transcript for live state does not read 30MB: the live path reads a bounded tail.
- No code path in this feature issues an API request, warms a cache, or schedules one.

## Links
- Fixes: [[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]
- Fixes, second round (independent review, 2026-08-06): [[ISS-0106-Synthetic-API-Error-Entries-Are-Counted-As-Turns-And-Reported-As-Model-Switches]], [[ISS-0107-A-Model-Switch-Permanently-Suppresses-The-Cold-Warning]], [[ISS-0108-A-Transcript-Entry-With-No-Timestamp-Reads-As-Confidently-Cold]], [[ISS-0109-The-Bounded-Tail-Read-Has-No-Guard]], [[ISS-0110-The-Whole-Cold-Reads-Grey-Behaviour-Can-Be-Reverted-With-A-Green-Suite]], [[ISS-0111-The-Measured-Figures-Do-Not-Reproduce-And-No-Scan-Script-Was-Committed]], [[ISS-0112-FEAT-0081-Was-Never-Updated-For-Its-Second-Surface]]
- Tasks: TASK-0343 … TASK-0356 (see frontmatter)
- Repo paths: `src/project_os_cockpit/session_cache.py`, `src/project_os_cockpit/agent_hooks.py`, `desktop/src/renderer/cache-temperature.ts`, `desktop/src/renderer/renderer.ts`, `tools/scripts/scan-cache-economics.py`

## Independent review — 2026-08-06 (changes-requested)

Reviewed by `model:claude-opus-5` from a fresh session with no access to the authoring session's reasoning; authored by `model:claude-opus-5` (same model family, different context — ADR-0013). Suites re-run green: `pytest` 764 passed / 1 skipped, `validate-docs.sh` OK. Verdict is **changes-requested** on the findings below, filed as issues.

Seven issues filed: [[ISS-0106]] (high, `<synthetic>` entries misread as turns and as model switches), [[ISS-0107]] (a model switch suppresses the cold warning permanently), [[ISS-0108]] (a missing timestamp reads as confidently cold), [[ISS-0109]] (the bounded-tail acceptance criterion has no guard), [[ISS-0110]] (the ISS-0105 behaviour can be reverted with a green suite), [[ISS-0111]] (the measured figures do not reproduce and no scan script was committed), [[ISS-0112]] (this note was never updated for its second surface).

Two acceptance criteria above are not met as written. *"Reading a 30MB transcript for live state does not read 30MB"* is true of the code and untested — see ISS-0109. *"Given a cold live session, the strip … one of `warm` / `cooling <n>m` / `cold`"* fails after any model switch, which replaces the state word indefinitely — see ISS-0107. A third is met but on contaminated input: *"Given a session whose last turn changed model while discarding ≥50k cached tokens"* fires for `<synthetic>` API-error placeholders too.

Nothing found argues against the feature's shape. Measuring before building, and recording the keep-warm arithmetic as an explicit non-goal, are the two best decisions in this change and both survive the review intact.

## Independent review — 2026-08-06, round 4 (approved)

Reviewed by `model:claude-opus-5` from a fresh session that started from these notes and the diff `4281c53..HEAD`, never saw any authoring session's reasoning, and performed none of rounds 1–3; authored by `model:claude-opus-5` (same model family, different context — [[project-os-dev#ADR-0013]]). **This verdict supersedes the `changes-requested` recorded above**, which was round one's and was answered by ISS-0106 … ISS-0112; rounds two and three were answered by ISS-0113 … ISS-0119. What was independent here: the context and the session. What was not: the model family, recorded in `reviewed_by` as provenance. No `status:` field was changed by this pass.

Suites re-run: `pytest` **793 passed / 1 skipped**, `validate-docs.sh` **OK**, desktop node suite **93 passed**. The full reasoning, the mutation results, and six recorded caveats are in [[CHG-20260806-Round-Two-Findings-Fixed]] under "Independent review — round 4"; the short form:

- Every acceptance criterion above that an earlier round called unmet is now met, and the two the first round named specifically were re-checked: the bounded tail read is guarded, and the switch announcement expires back to the standing state.
- The measured figures reproduce from `tools/scripts/scan-cache-economics.py` on a fresh run — 42 transcripts, 8 / 6 / 44 re-write events, 3.7% staleness, 4.9% avoidable — allowing for a corpus that has grown to 21,957 turns.
- `_effective_usage` and `railKey` were re-attacked rather than taken on the previous rounds' word. Round three's five mutations reproduce at exactly its recorded kill counts; a sixth survives, so "the last **non-zero** iteration" is unguarded — latent only, since every entry in this corpus has one iteration.
- `SNAPSHOT-MEMBERSHIP` fires on the defect it was written for and dies under five of six mutations.

**What is approved with a caveat, not silently:** ISS-0118's third next action is ticked while the clause it names in [[TASK-0351-Pure-Decisions-For-The-Rail-And-The-Badge]] is unchanged; the new validator gate carries no task and is absent from every `impacts:` list; and the Links section below still reads "TASK-0343 … TASK-0353" for a feature that owns through TASK-0355, and names only round one's fixes. All are understatements or one-line edits, all belong to close-out, and none makes anything shipped wrong — which is why they are follow-ups rather than a fourth round.
