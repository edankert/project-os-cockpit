---
type: "[[issue]]"
id: ISS-0059
aliases: ["ISS-0059"]
title: "Three fleet apps declare colour in Kotlin and Swift, so the living style guide cannot read them"
status: triage
severity: medium
phase: "[[PHASE-999-Unscheduled]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["fleet survey while implementing [[TASK-0231]], 2026-07-28"]
related: ["[[FEAT-0044-Fleet-Design-Systems]]", "[[TASK-0230-Project-Stylesheet-Route]]", "[[TASK-0231-Fleet-Design-System-Rollout]]"]
fixed_by: []
---

# Half the fleet's UX has no CSS to read

## What the survey found, after the route was built

`your-health`, `your-sudoku` and `your-trainer` contain **no application CSS at all**. They are native apps and declare colour in source:

```kotlin
val ghost = Color(0xFF232A35)          // your-health  app/.../ui/theme/Color.kt
```
```swift
// your-sudoku  ios/YourSudoku/App/Theme.swift
// your-trainer ios/YourTrainer/Utils/ZoneColorUtils.swift
```

The only `.css` in those repos belongs to the vendored cockpit, a venv, or a test report.

[[TASK-0230]]'s route is **CSS-only by deliberate narrowing** — that is what stops it becoming a general file read on a server that binds `0.0.0.0`, and it is tested. So the living style guide, which is the whole standard [[FEAT-0044]] set, cannot reach three of the six projects.

**This was not knowable before the route existed.** The survey that scoped the feature counted `.css` files per repo and found several in each — all of them vendored or venv noise. Counting files answered "is there CSS here" when the question was "does this project's UI have CSS", and those differ.

## Why it is not a small fix

- The route would need a second, non-CSS declaration and a different guard story. `.css`-only is currently load-bearing.
- The page parses CSS through the **CSSOM**, which does the hard part. Kotlin and Swift need a parser, in the browser, per language.
- A Swift file is not a palette: `ZoneColorUtils.swift` computes zone colours, so "read the tokens" means deciding what counts as one.

## What already exists, and is better than nothing

`your-applications.com` ships `tools/scripts/check-family-palette.py`, which **already parses `val X = Color(0xAARRGGBB)` from Kotlin** and compares it against the CSS upstream ([[ADR-0008]]). It exits clean today. So the fleet already has a working cross-language palette check — it just is not a *page*, and it covers the shared family palette rather than each app's whole system.

## Options

1. **A token-reader route** — declare `tokens:` alongside `stylesheets:`, serve the source files, parse in the page. Most faithful to the DES-0002 standard; most work, and needs a security story for serving source.
2. **Generate CSS custom properties from the native declarations at build time**, and declare the generated file. The page stays unchanged. But a generated artifact is a second copy of the palette, which is the drift this whole feature exists to prevent — unless the generation is checked, which is what `check-family-palette.py` already does for the family subset.
3. **Honest descriptive notes for the three**, pointing at `check-family-palette.py` for the part that *is* checked, and saying plainly that the rest is unchecked prose.

Not chosen. Option 3 is available immediately and option 1 is the real answer; whether the middle is worth building is Edwin's call.
