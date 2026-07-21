---
type: "[[change]]"
id: CHG-20260720-Usage-Freshness
aliases: ["CHG-20260720-Usage-Freshness"]
title: "Usage block account-global + self-refreshing — freshest wins, poll, as-of caption"
status: merged
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
impacts: ["statusline cost snapshot (+captured_at)", "fleet proxy (+rate_limits/rateLimitsAt)", "budget block (as-of + poll + persistence; refresh button removed)"]
issues: []
features: ["[[FEAT-0035-Account-Budget-Surface]]"]
related: ["[[TASK-0169]]", "[[TASK-0170]]", "[[TASK-0171]]", "[[TASK-0172]]"]
---

# Usage freshness (FEAT-0035 / TASK-0169)

## Summary

Fixes two reports: the Usage block froze when idle, and it showed *different* numbers per project even though rate limits are account-global. Root cause: the block took the active workspace's last statusline reading and overwrote on every workspace switch.

Fix (freshest-wins + poll): the tracker stamps `captured_at` on each statusline cost snapshot; the fleet proxy exposes the full `rate_limits` + `captured_at` per workspace. The renderer keeps one account-global reading behind an **adopt-if-newer** gate — the live statusline AND a new 2-minute fleet poll only replace the displayed reading when their `captured_at` is newer, so switching projects can never downgrade to an older number and the value is identical everywhere. A —» button (right of the "Usage" title, spins while fetching) forces an immediate cross-workspace re-read; an "as of Xm ago" caption greys past 10 minutes. Constraint acknowledged: the statusline is the only rate-limit source, so a refresh surfaces the freshest reading any session emitted, not a live account query.

**Always-visible (TASK-0170).** The freshest reading is persisted to localStorage on every adopt and loaded on launch, so the account-global block shows immediately on start and whenever the active workspace has no session (with an honest aged "as of"); it hides only when no reading has ever been received. A startup poll refreshes it from any live sidecar.

**Freshest-across-sessions source (TASK-0171).** Rate limits are account-global, but the snapshot/fleet had exposed only the last session's reading — so a later session without a statusline masked an earlier one that had the real numbers (displayed 48/19, real 19/59). The tracker now exposes `latest_rate_limits()` — the newest `captured_at` across ALL sessions — as top-level `rate_limits`/`rate_limits_at` on the snapshot; the fleet and renderer adopt that through the same freshest-wins gate. (A test-seeded persisted reading was cleared as a one-off.)

**Refresh button removed (TASK-0172).** With no API endpoint for account usage and the statusline as the only source, the manual refresh button could never fetch anything newer than the last reading — it was decorative, so it was removed. The 2-minute fleet poll (silent backstop) and the "as of" freshness caption stay.

## Verification

CDP: block renders 55% with "as of just now"; a newer statusline (61%) is adopted; after TASK-0172 the block renders with the as-of caption and no refresh button. `tests/test_agent_hooks` green (16); `tsc` clean.

Independent review (opus) approved; three minor hardening findings folded in: only strictly-newer readings adopt (no burn-sample dilution while idle), a NaN captured_at can never poison the as-of, and a reading without captured_at counts as oldest (legacy snapshots can't falsely-freshen).

Files: `src/project_os_cockpit/agent_hooks.py`, `desktop/src/ipc/agents-fleet.ts`, `desktop/src/renderer/{renderer.ts,renderer.css}`.
