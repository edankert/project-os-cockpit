---
type: "[[plan]]"
title: "Plan — What a session costs to keep alive"
status: done
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
implements: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"]
related: ["[[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]"]
---

# Plan — What a session costs to keep alive

## Delivery sequence

1. **[[TASK-0343-The-Cache-Reader]]** — `src/project_os_cockpit/session_cache.py`. Pure read over the transcript JSONL: dedupe assistant turns by `message.id` (Claude Code writes one entry per content block, so a naive scan double-counts), pull `cache_read_input_tokens` / `cache_creation_input_tokens` / `cache_creation.ephemeral_{1h,5m}_input_tokens` / `model` / `timestamp`. Two entry points — a bounded tail read for live state, a full scan for the retrospective — both memoised against `(path, mtime, size)`. No I/O beyond the transcript; no network.
2. **[[TASK-0344-Warm-Cooling-Cold-In-The-Strip]]** — surface it. Merge cache state into the agent snapshot so the strip renders without a second fetch, add `GET /api/cockpit/session-cache` for the retrospective, and render weight + state in `renderAgentStripCost`'s neighbourhood.
3. **[[TASK-0345-Model-Switch-Named-Where-It-Happens]]** — the [[ISS-0104]] fix, riding on step 1's reader: classify each full-prefix re-write and name the model-switch ones specifically, live and retrospectively.

## Dependencies

- **Hard:** step 1 before 2 and 3 — both consume the reader. Nothing outside this feature blocks it: `transcript_path` has been on the session record since [[FEAT-0019]].
- **Soft:** 2 before 3, so the model-switch line lands in a strip that already has somewhere to put it.

## Design constraints carried from the feature

- **The live path must not read whole transcripts.** Measured here: 30MB and 34MB transcripts exist in this repo's own history. The strip re-renders on every snapshot; a full read there would be a performance bug shipped as a cost feature.
- **Cost figures are estimates and must read as estimates.** Model pricing is hard-coded per family and drifts; the token counts are exact but the dollars are derived. Round hard, prefix with `~`, never render more precision than the input justifies.
- **Nothing in this feature may issue an API request.** The reader is a file parser. See FEAT-0081, "The automation that must not be built".

## Open questions

- **Cooling threshold.** The 1-hour TTL is what this fleet's sessions use, but a cache entry can be evicted early — TTL is a maximum, not a guarantee, and 6 of the 17 sub-hour re-writes had no model change to explain them. So `warm` is a claim the reader cannot actually prove. Resolved for v1 by wording: the strip says what the *elapsed* time is against the known TTL, not that the cache is definitely present.
- **Where the retrospective figure is rendered.** The endpoint lands in TASK-0344; its home on the overview is deliberately unresolved until there is a number to look at. Not a blocker — the API is useful to the scan script regardless.
