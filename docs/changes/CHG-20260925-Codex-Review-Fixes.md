---
type: "[[change]]"
id: CHG-20260925-Codex-Review-Fixes
title: "A queued Codex prompt is not lost when its terminal closes, and the Codex rules the review found untested now have tests"
status: merged
owner: user:edwin
created: 2026-09-25
updated: 2026-09-25
source: ["[[TASK-0638-Fix-The-Codex-Review-Findings]]"]
commit: ""
pr: ""
impacts: []
issues: []
features: ["[[FEAT-0019]]", "[[FEAT-0027]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0638-Fix-The-Codex-Review-Findings]]", "[[ISS-0312]]"]
---

# A queued Codex prompt is not lost when its terminal closes, and the Codex rules the review found untested now have tests

## Summary

A prompt queued for Codex now goes back in the queue if its terminal closes between the paste and the Return. Before this change the prompt was pasted, the Return failed, and the item was dropped from the queue with only a warning. This was found by the FEAT-0019 and FEAT-0027 review on 2026-09-25.

The other changes:

- **A multi-file Codex patch reports one file.** The agent strip's activity named the last file in `file`, but could keep an earlier file's docs path in `rel`. Now `rel` is dropped when the current file is outside `docs/`.
- **A child agent's id is capped at 128 characters,** like the session id.

Five rules had no test that failed when they were removed, and now each has one:

- a manual `cockpit signal` clears the hook-fed sessions
- the headline session is chosen by state (needs-input, then busy, then waiting), in both places that choose it
- a Codex session is never shown a Claude cache reading
- a decayed busy headline keeps another session's waiting row in Needs you until that row goes cold
- the queued prompt is re-queued after a failed Return

The capability register gains `shell.agents.codex` and the external Codex toggle on `shell.settings`. Both describe work from 2026-09-16 and 2026-09-23 that had no row.

## Impact

No screen changes. A queued Codex prompt now survives its terminal closing mid-submission.

## Evidence

Eight new tests: six in `tests/test_agent_hooks.py` and `tests/test_cockpit_state.py`, one in `desktop/tests/codex-dispatch.test.mjs`, and one in `desktop/tests/cache-temperature.test.mjs`. Each was checked by removing its code in a copy and seeing it fail. The results of the full runs are recorded in [[TASK-0638-Fix-The-Codex-Review-Findings]].

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated
- requirements: not-applicable
- tasks: new
- issues: not-applicable
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated

## Follow-ups
- [ ] Round 2 of the FEAT-0019 and FEAT-0027 review verifies these fixes.
