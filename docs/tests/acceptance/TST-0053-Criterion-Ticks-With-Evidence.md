---
type: "[[test]]"
id: TST-0053
aliases: ["TST-0053"]
title: "A criterion ticks with evidence"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "The note page"
covers: ["[[FEAT-0011]]", "[[FEAT-0060]]"]
related: []
level: acceptance
---

# A criterion ticks with evidence

tick an acceptance criterion from the note page. Expect: the box fills, the line gains `— evidence: … (actor, date)`, and the rest of the file is untouched. — 2026-08-11, **rendered**, isolated clone: clicking an unticked criterion on [[FEAT-0083]] opens an inline field (*what shows this is met?*) with `Tick` / `Reconcile…` / `Cancel` — it will not tick without evidence. After `Tick`, `git diff` is **one line changed and nothing else**: `- [x] … — evidence: … (user:edwin, 2026-08-11)`. **The first attempt failed and the failure is the more valuable half — filed as [[ISS-0137]]:** a criterion containing inline markup cannot be ticked at all, because the renderer sends the *rendered* text and the server matches the *raw* line. 26 of this corpus's 53 open criteria are unreachable that way. (user:edwin, 2026-08-11)
