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
fixes: ["ISS-0104"]
release: ""
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0020-Agent-Activity-Surfaces]]", "[[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]"]
tests: []
---

# What a session costs to keep alive

## Goal

Edwin asked whether cache staleness could be identified, highlighted, or automated away. Measuring first changed the answer, and the feature is shaped by what the measurement found rather than by the original worry.

Across 38 transcripts (21,607 deduplicated assistant turns, measured 2026-08-06):

| | | |
|---|---:|---|
| Cache **reads** | ≈$5,287 | 79% of input-side spend — the cost of carrying context |
| Cache **writes** | ≈$1,444 | 21% |
| — of which TTL expiry (idle >60 min) | ≈$236 | 41 events, 19.0M tokens |
| — of which sub-hour invalidation | ≈$100 | 17 events, 11 of them model switches ([[ISS-0104]]) |

**Staleness is real and it is ~3.5% of the input bill.** The 20× larger number is the weight of the context itself, and nothing in the cockpit says what that weight is in tokens — `ctx 62%` is a fill ratio against a window, not a cost.

So the feature is *session economics*, not *cache warnings*: what this session weighs, what state its cache is in, and what the next turn costs under each.

## The automation that must not be built

A keep-warm ping costs **2× the full prefix, every ping**. Going cold and paying on return costs 2× **once**. Re-warming an idle session is therefore strictly more expensive than letting it expire, for any idle period longer than the TTL — there is no cheap keep-alive, and `max_tokens: 0` pre-warming does not change the arithmetic (it pays the same write).

Recorded here because "just refresh the cache in the background" is the obvious feature request, it sounds like a saving, and it would raise the bill. The honest lever is **behavioural**: knowing the prefix is cold and large *before* deciding to resume it, so starting fresh stays on the table.

## Scope

### In scope
- A reader over the session transcript (`transcript_path`, already stored per session since [[FEAT-0019]]) that yields prefix weight, cache state, last-turn model, and full-prefix re-write events. Tail-read for live state, full scan for the retrospective, both cached against mtime.
- The strip says **warm / cooling / cold**, carries the prefix weight in tokens, and when cold names the cost of resuming.
- Model-switch invalidation named at the point it happens ([[ISS-0104]]).
- A retrospective per-repo figure: what full-prefix re-writes cost here, split by cause.

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
- Reading a 30MB transcript for live state does not read 30MB: the live path reads a bounded tail.
- No code path in this feature issues an API request, warms a cache, or schedules one.

## Links
- Fixes: [[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]
- Tasks: [[TASK-0343-The-Cache-Reader]], [[TASK-0344-Warm-Cooling-Cold-In-The-Strip]], [[TASK-0345-Model-Switch-Named-Where-It-Happens]]
- Repo paths: `src/project_os_cockpit/session_cache.py`, `src/project_os_cockpit/agent_hooks.py`, `desktop/src/renderer/renderer.ts`
