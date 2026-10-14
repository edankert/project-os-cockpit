---
type: "[[task]]"
id: TASK-0653
aliases: ["TASK-0653"]
title: "The findings of FEAT-0156's first independent review are fixed: every event and the SessionEnd limit are tested, and an event is not counted twice in either order"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]], ## Review, round 1"]
parent: "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
effort: "S"
due: ""
depends: []
blocks: []
related: ["[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]]"]
tests: []
---

# The first review's findings are fixed

Round 1 of FEAT-0156's independent review returned `changes-requested`. The findings are in the feature note's `## Review` section. Each is about code this feature changed, so each is fixed here (QUALITY.md, "A finding is fixed in the feature that caused it").

## Definition of Done

- [x] A plugin test raises PostToolUse, Notification, PermissionRequest, SubagentStart and SubagentStop, and checks that each is posted with the field the sidecar reads. Removing any one registration fails it.
- [x] A plugin test shows SessionEnd returns after one second when the post hangs, and not before. Removing the limit fails it.
- [x] When `$.clock.sleep` fails, SessionEnd stops waiting instead of waiting for the post with no limit. A test shows it.
- [x] The sidecar's two-second duplicate check ignores the plugin's mark. An event the external hook posts first and the plugin posts second is counted once, and the plugin's copy still claims the session. A pytest shows it, and fails without the change.
- [x] The comment in `register()` counts the events it registers correctly.
- [x] `claude plugin validate`, `claude plugin test`, the targeted pytest and node tests, and `validate-docs.sh` are green.

## Result, 2026-10-14

- **Five events.** `cockpit.test.ts`, "the other five events are posted with what the sidecar reads". Removing any one of the five registrations fails it; each was tried.
- **SessionEnd's limit.** Two tests under "SessionEnd holds an exiting session for at most a second". With a sidecar that never answers, SessionEnd has not returned after 999 ms on `mock.clock` and has returned at 1000 ms. With a clock that cannot sleep, it returns at once. Replacing the race with `await posting` fails both; restoring the old fallback fails the second.
- **The failed sleep.** `postWithin` now ends the wait at once when the sleep fails or cannot start, instead of waiting for the post. This means a failed clock can drop SessionEnd's post; the limit wins over delivery, as the criterion says. The existing test "SessionEnd is delivered before the hook returns" had passed only through the old fallback, because nothing answers `$.clock.sleep` in a test without a stand-in clock. It now stands one in, so only the delivered post can end the wait.
- **Counted once, in either order.** `agent_hooks.py` leaves the plugin's mark out of the duplicate comparison, and a marked copy dropped as a duplicate still claims the session. Writing the test found a bug in the first version of this fix: the external hook's copy, dropped because the session was claimed, was still remembered, so the plugin's own copy of the next event was then dropped as its duplicate and the event was lost. A post is now remembered only once it is kept. `test_an_event_the_external_hook_posts_first_is_counted_once` fails when the mark is compared again, when a dropped marked copy does not claim the session, and when a post is remembered before the claim check.
- **The comment.** `register.ts` now says eight events go through `forward` and SessionEnd is the ninth.
- **Runs.** `python3 -m pytest -q -p no:randomly`: 2144 passed, 11 skipped. `claude plugin test`: 13 passed. `claude plugin validate`: passed with warnings. `node --test desktop/tests/*.test.mjs`: 196 passed.
