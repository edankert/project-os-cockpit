---
type: "[[test]]"
id: TST-0062
aliases: ["TST-0062", "CHK-0019"]
title: "A real shell"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "The embedded terminal"
section: "1.9"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0003]]", "[[FEAT-0037]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.9.1 @ 7de1a86"
related: []
level: acceptance
kind: manual
merged_from: "CHK-0019 @ 4c02731"
---

# A real shell

open the terminal, run an agent CLI, complete a turn. Expect: it behaves like a terminal — resize, scrollback, copy and paste from the context menu. — 2026-08-11, all five clauses, against the running shell. **The agent CLI clause was already satisfied and I had asked Edwin to satisfy it again.** Reading the terminal buffer over CDP returned this session's own transcript — `❯ Why is the goal not met, why do you think you have to restart the shell?` — so the acceptance walk was being conducted *from inside the terminal it was testing*, dozens of completed turns deep. **Resize:** the pane driven 392px → 612px, xterm reflowed **26 rows → 40** and back to 26 on restore — the fit addon tracks the pane, not the window. **Scrollback:** real wheel events through CDP's `Input` domain, dispatched and read back **over one connection** so no output could land between them. Top row `can't.` → `❯ go` on scrolling up, unchanged on scrolling further (the buffer's top, ~11 lines), and live output again on scrolling down. *`scrollTop` never moves — xterm re-renders rows rather than scrolling a container, which is why two earlier attempts keyed on `scrollTop` read as static and were wrongly recorded as unproven. Corrected here.* **Copy and paste from the context menu:** the native Electron menu from [[FEAT-0054]] — not in the DOM, unreachable from CDP. **Edwin, in session: *"I have copied from the native context menu."*** *Precisely: copy is witnessed by the principal; **paste was not separately reported** and is recorded that way rather than assumed.* (user:edwin, 2026-08-11)
