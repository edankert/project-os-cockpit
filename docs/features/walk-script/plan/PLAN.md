---
type: "[[plan]]"
title: "Delivery plan — the walk page as a script"
status: draft
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"]
implements: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"]
related: ["[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]", "[[FEAT-0149-The-Walk-Page]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:` — see docs/__templates__/plan.md. -->
# Delivery plan — the walk page as a script

## Delivery sequence

1. **[[TASK-0624-A-Tick-Per-Step]] first.** It is the part with a correctness claim (step ticks equal check ticks) and it can be built against a hand-written fixture procedure before upstream's format is final.
2. **[[TASK-0623-Each-Sitting-As-Its-Procedure]]** once project-os-dev TASK-0121 fixes the payload shape. Until then, render from the fixture and keep the shape behind one adapter function.
3. **[[TASK-0622-The-Survey-As-Screen-Cards]]** once project-os-dev TASK-0118 lands the new survey payload.
4. **[[TASK-0625-The-Checks-Page-Groups-By-Screen]]** once project-os-dev TASK-0116 states the surface rules. Independent of 1 to 3.
5. **[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]** last, after your-trainer TASK-0906 writes real procedures.

## Dependencies

- **Hard:** project-os-dev ADR-0044 and ADR-0045 accepted; project-os-dev TASK-0123 syncs the module so `walk_sheet_bundled.py` stays byte-identical.
- **Hard:** your-trainer TASK-0906 before TASK-0626.
- **Soft:** your-trainer TASK-0904 (captures) before TASK-0622 is checked on real images.

## Open questions

- Where step ticks live before a check's verdict is written (TASK-0624).
- How a step's mark combines when its checks' other steps carry different marks (TASK-0624).
- Whether a pass from a procedure step is acceptable under ADR-0041 when the step's wording is not the check's own (project-os-dev ADR-0045, Edwin's).
