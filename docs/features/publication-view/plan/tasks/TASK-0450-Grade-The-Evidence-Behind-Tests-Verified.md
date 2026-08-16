---
type: "[[task]]"
id: TASK-0450
aliases: ["TASK-0450"]
title: "Grade the evidence behind tests_verified — walked, witnessed, and whether the note was ever verified at all"
status: backlog
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0109-A-Shipped-Release-Reports-What-It-Kept]]", "Measured against ../your-trainer on 2026-08-16"]
parent: "[[FEAT-0109-A-Shipped-Release-Reports-What-It-Kept]]"
effort: S
depends: []
blocks: []
related: ["[[FEAT-0107-Publication-Is-A-List-Of-Releases]]"]
tests: []
---

# Grade the evidence behind tests_verified

## Why

The shipped-release page renders `tests_verified:` as links under the heading **Acceptance tests as executed**. `REL-0012` names `TST-0011`, which has **18 checkboxes, all unticked, and 18 blank `Evidence: ___` slots**, at `status: ready`.

And `last_verified` equals `created` in **15 of the 16** TST notes in `../your-trainer` that carry it. The one exception differs by a day and is TST-0011 itself. The field is written by the template at authoring time and has never recorded a verification anywhere.

## What

Each `tests_verified` entry renders a grade instead of a bare link:

```
TST-0011  Android BLE hardening    0/18 walked · 0 evidence · never verified   ⚠
TST-0014  Edge-to-edge insets     12/14 walked · 12 witnessed                  ✓
```

Three reads of the linked note: ticked over total, rows carrying a filled evidence slot or a `✅ (…)` witness, and whether `last_verified` differs from `created`. Nothing new is stored and no status changes.

## Cases

- entry resolves to **no note** → say so; do not render a dead link
- note has **no checkboxes** → `no checks` rather than `0/0`
- `tests_verified` **empty** — 5 of 12 release notes → a stated absence, not an empty section
- note has **no `last_verified`** → omit that clause rather than claiming never-verified

## Done when

- [ ] walked / total and evidence count rendered per entry
- [ ] `last_verified == created` reports **never verified**, in those words
- [ ] unresolvable entry, no-checkbox note, and empty `tests_verified` each have their own rendering and their own test
- [ ] the evidence-slot detector does not count a blank `Evidence: ___` as filled — the mutation that must fail
- [ ] asserted live against `../your-trainer`'s REL-0012 → TST-0011 as 0/18
