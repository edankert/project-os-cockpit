---
type: "[[issue]]"
id: ISS-0052
aliases: ["ISS-0052"]
title: "The typography specimens interpolated a font token containing quotes"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review of FEAT-0042, 2026-07-28"]
related: ["[[ISS-0048-Token-Values-Interpolated-Into-Markup]]", "[[TASK-0228-Living-Style-Guide]]"]
fixed_by: []
---

# ISS-0048, fixed in one function only

[[ISS-0048]] established that a value read from a stylesheet is **data** and must never be interpolated into markup. That was applied to `swatchRow` and to the widget gallery — and not to the typography section, which still did:

```js
'<span style="font-family:' + v + ';font-size:15px">'
```

`--font-sans` is `-apple-system, BlinkMacSystemFont, "Segoe UI", …`. The quotes around `Segoe UI` closed the attribute, the declaration was invalid, and the specimen rendered **the inherited body font** — which happens to look almost right, so it demonstrated nothing while appearing to demonstrate something. That is the worst failure available to a type specimen.

## Fix

Built with DOM APIs like everything else: `style.setProperty('font-family', value)`. Verified in a sandboxed frame — 0 stray attributes, and the specimen now carries a properly escaped declaration.

## The lesson worth keeping

Fixing a class of defect in the function where it was *found* leaves the rest of the class alive. [[ISS-0048]] named the rule correctly and applied it to two of three sites. The test written to guard it inspected only `swatchRow`, so it certified the fix it was written beside.
