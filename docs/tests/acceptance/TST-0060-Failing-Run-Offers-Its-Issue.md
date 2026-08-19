---
type: "[[test]]"
id: TST-0060
aliases: ["TST-0060"]
title: "A failing run offers its issue"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Tests"
covers: ["[[FEAT-0086]]"]
related: []
level: acceptance
---

# A failing run offers its issue

fail a step and record. Expect: an offer naming the step, quoting what the note expected and what you observed; nothing is filed until you press Enter in the capture box. — 2026-08-11, **rendered**, isolated clone: with one step failed the runner said *"1 step failed — the test will be recorded as failing"* and *"Recording the run offers an issue draft for the first failing step — **filing it stays your call**"*. `Record run (failing)` produced `Draft an issue ›`, which opened the capture box **pre-filled and editable** (*Enter files it at triage · Esc closes*). Enter filed a note carrying, verbatim: **Step 1** (the step's own text), **Expected:** (quoted from the checklist) and **Observed:** (what I typed), `related: ["[[TST-0011]]"]`, `status: triage`. The draft is an offer at every stage — the button says *Draft*, the box says *Enter files it*. (user:edwin, 2026-08-11)
