---
type: "[[issue]]"
id: ISS-0051
aliases: ["ISS-0051"]
title: "A re-injected stylesheet has no href, so the spacing measurement silently found nothing"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review of FEAT-0042, 2026-07-28"]
related: ["[[ISS-0043-Sandboxed-Artifact-Cannot-Read-CSS]]", "[[TASK-0228-Living-Style-Guide]]"]
fixed_by: []
---

# The ISS-0043 pattern, one function from its own fix

The spacing counter selected its input with:

```js
if (!rule.style || !(sheet.href || '').includes('cockpit.css')) return;
```

[[ISS-0043]]'s repair fetches the blocked stylesheets and re-injects them as `<style>` elements — whose `href` is **null**. So in the sandboxed runtime, which is the only runtime the app uses, that filter matched nothing: **zero bars**, beneath prose asserting *"the counts below are computed, not quoted … this one is the live measurement."*

`shellPresent` had been taught to look at `data-reinjected-from`. The spacing counter and the override attribution had not — the same fix, applied in one place and not the other, in the same file.

## Fix

One `sheetOrigin(sheet)` helper — `href`, else `data-reinjected-from`, else empty — used everywhere a sheet's provenance is asked for. Verified in a sandboxed frame: **9 bars** where there were 0, topped by 14px×32, 6px×25, 8px×19.

## Found while fixing it

`element.append()` returns `undefined`. A line reading `valRow.append(document.createElement('span')).className = 'lbl'` threw, and took every section below Typography with it — spacing, icons, widgets, motion, accessibility. The page still looked plausible, because what is missing from a page is invisible. Caught by *measuring* the rendered page rather than reading the source, which is the only reason it was caught at all.
