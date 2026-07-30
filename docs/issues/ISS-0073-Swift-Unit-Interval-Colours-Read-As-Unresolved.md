---
type: "[[issue]]"
id: ISS-0073
aliases: ["ISS-0073"]
title: "SwiftUI's 0–1 Color(red:green:blue:) reads as unresolved, so a real colour renders as a source expression"
status: fixed
severity: low
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["verifying TASK-0231's rollout against the three native apps, 2026-07-30"]
component: sidecar
related: ["[[ISS-0059-Native-Apps-Have-No-CSS]]", "[[TASK-0231-Fleet-Design-System-Rollout]]", "[[FEAT-0044-Fleet-Design-Systems]]"]
fixed_by: ["[[TASK-0231-Fleet-Design-System-Rollout]]"]
tests: []
---

# A resolvable Swift colour is reported as unresolvable

## What

`token_sources._SWIFT_RGB` only matches the `/ 255.0` form:

```swift
static let brandPurple = Color(red: 0x74 / 255.0, green: 0x74 / 255.0, blue: 0xB0 / 255.0)   // matched
static let zoneRecovery = Color(red: 0.6, green: 0.6, blue: 0.6)                              // NOT matched
```

SwiftUI's `Color(red:green:blue:)` takes **0–1 doubles**; the `/ 255.0` spelling is one way of writing them, not the only one. The bare form falls through to `_SWIFT_OTHER` and is emitted as `--zoneRecovery: Color(red: 0.6, green: 0.6, blue: 0.6);` — a token the page can name but not draw, when `#999999` was available.

Measured live against `your-trainer` (`ios/YourTrainer/Utils/ZoneColorUtils.swift`, port 8903).

## Why it is small but not cosmetic

The unresolved path exists for colours with **no honest hex** — `Color.blue`, `Color.red.opacity(0.3)`, which depend on platform and appearance. That is a good rule. Using it for a colour that is fully specified in the source weakens it: a reader who sees several unresolved tokens learns to skim past them, including the ones that genuinely could not be read.

`your-trainer` has exactly one such token and six genuine system colours, so today the page reports 1 avoidable unknown out of 7.

## Expected

`Color(red: 0.6, green: 0.6, blue: 0.6)` resolves to `#999999`. `Color.blue` and `Color.red.opacity(0.3)` stay unresolved, because they still have no honest value.

## Next Actions

- [x] Match the unit-interval form, keeping the `/ 255.0` form
- [x] Test both forms plus the two that must stay unresolved


## Fixed 2026-07-30

`_SWIFT_UNIT` matches the bare 0–1 form and rejects anything outside `[0, 1]`, so a value that is not this spelling falls through rather than being coerced. `your-trainer` now reads:

```
--zoneRecovery: #999999;      (was: Color(red: 0.6, green: 0.6, blue: 0.6))
--zoneEndurance: Color.blue;  (unchanged — still no honest hex)
… five more system colours, unchanged
```

Three tests: the new form, both spellings side by side (neither steals the other's matches), and — added to the existing derived-colour case — that `Color.blue` and `Color.green` still emit **no** `#`. That last one is the one that matters: the fix must not reach system colours, because inventing a swatch for one is worse than reporting it.

Mutation-verified by disabling the new branch.
