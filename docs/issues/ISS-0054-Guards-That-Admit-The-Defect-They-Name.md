---
type: "[[issue]]"
id: ISS-0054
aliases: ["ISS-0054"]
title: "Two reachability guards admitted the defects they were named for"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review of FEAT-0043 round 3, 2026-07-28"]
related: ["[[ISS-0034-Design-Mode-Reachability-Untested]]", "[[ISS-0040-Design-Frame-Width-And-Boot-Race]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
fixed_by: []
---

# Both guards for "the design mode is reachable" had holes

## N1 — the widened polarity test admitted an inverted hoist

Round 2 asked for the guard-polarity test to tolerate a semantically identical refactor, on the reasoning that a test failing on correct refactors trains people to weaken it. The widening checked only that a hoisted boolean's definition *mentions* `currentRel.startsWith('~design')`. That admits:

```ts
const notOnDesign = !!currentRel && !currentRel.startsWith('~design');
if (!notOnDesign) { void navigateTo('~design', { replace: false }); }
```

which navigates when nothing is open or when already on Design, and **not** when any other note is open — clicking Design mid-session does nothing. [[ISS-0034]]'s defect exactly, suite green.

The reviewer's own words: *"The flexibility I asked for in round 2 is the hole."* Fixed by checking the definition's **polarity**: a hoisted name may mean "already on design", never its negation. Both variants exercised — the broken hoist fails, the correct hoist passes.

## N2 — the boot-race fix was unguarded

[[ISS-0040]] §2 fixed the sidecar-ready handler racing a virtual-landing mode to README. Nothing tested it: reverting `MODES_WITH_VIRTUAL_LANDING` to `{'overview'}` left the suite green.

So reachability had **one guarded path (the click) and one unguarded (the boot)** — and the unguarded one is the one that actually broke in use. Now asserted on the set's exact contents *and* on the ready handler consulting it; reverting either fails.

## What this says about the two approvals before it

The reviewer volunteered it: TASK-0224's DoD bullet *"reachable by click, keyboard, and a restored preference from a previous session"* was **untrue when reachability was approved in rounds 1 and 2**. It had quoted the `navigateTo('README.md')` line in its own notes without connecting it to the mode it was certifying — *"'the happy path reads correctly end to end' was exactly the failure — reading is what I did, and the boot path needed running."*

Edwin found it by using the app. That is the third time on this feature that reading passed something running would have caught, and it is the reason `tools/dev/cdp.py` now exists.
