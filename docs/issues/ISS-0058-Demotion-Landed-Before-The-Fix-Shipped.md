---
type: "[[issue]]"
id: ISS-0058
aliases: ["ISS-0058"]
title: "The demotion hazard landed for real: a running sidecar predated its own fix"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["Edwin's review of DES-0002, 2026-07-28"]
related: ["[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]", "[[DES-0002-Cockpit-Design-System]]", "[[TASK-0229-Offer-A-Design-For-Review]]"]
fixed_by: []
---

# The hazard was real, and it fired

Edwin accepted [[DES-0002]] and the note came back `status: "accepted"`. It had been `implemented`. That is exactly the demotion independent review found — `accepted` means *agreed, not yet built*, `implemented` means the code shipped — and it happened for real, on the one design in the repo.

## Why the fix did not protect him

**The running sidecar predated it.** The Python process serving his cockpit started at **15:58:34**; the guard shipped at **16:06:22** (`dbe8ec3`) and was completed at **16:16:41** (`1254960`). A sidecar is a long-lived child process spawned when a workspace opens — it does not pick up source changes, and nothing told anyone that.

I told Edwin the row was "safe to action now" on the strength of the code in the repository, having verified the fix with fixtures and a *fresh* interpreter. The claim was true of the code and false of his machine. **A fix is not deployed until the process running it restarts** — and I had restarted that app several times during the work without noticing that the last restart came before the fix.

## What was done

- `status` restored to `implemented` on the note. **The verdict was kept**: `reviewed_by: user:edwin`, `review_date`, `review_verdict: accepted`, `design_revision: 6eb6888` are Edwin's genuine review of a genuine revision, and the only wrong field was the one the old code wrote.
- The replay was proven against current code: the same call now leaves `status: implemented`.
- The app was restarted so its sidecar carries the fix.

## The general point

This is the third distinct shape of the same failure in one day. [[ISS-0043]]/[[ISS-0046]]/[[ISS-0047]] were *verified in a context the app never uses*. [[ISS-0056]] was *guards asserted rather than exercised*. This is *a fix verified in a process that was not the one running* — and the tell was available the whole time in `ps`.

The lesson is narrow and worth keeping: **when a fix protects a human from an action, confirm the running process has it before telling them the action is safe.**
