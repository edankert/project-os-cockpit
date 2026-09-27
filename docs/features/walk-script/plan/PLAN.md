---
type: "[[plan]]"
title: "Delivery plan — the release test page as a script"
status: draft
owner: user:edwin
created: 2026-09-14
updated: 2026-09-27
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"]
implements: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"]
related: ["[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]", "[[FEAT-0149-The-Walk-Page]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:` — see docs/__templates__/plan.md. -->
# Delivery plan — the release test page as a script

## Delivery sequence

0. **Nothing here starts until project-os-dev TASK-0119 has fixed the procedure format** (Edwin's start order, 2026-09-14). Upstream TASK-0116 to TASK-0120 go first, and your-trainer TASK-0900 runs beside them.
1. **[[TASK-0624-A-Tick-Per-Step]] first.** It is the part with a correctness claim (step ticks equal check ticks), built against a fixture procedure in the fixed format.
2. **[[TASK-0623-Each-Sitting-As-Its-Procedure]]** once project-os-dev TASK-0121 fixes the payload shape. Until then, render from the fixture and keep the shape behind one adapter function.
3. **[[TASK-0622-The-Survey-As-Screen-Cards]]** once project-os-dev TASK-0118 lands the new payload for what changed.
4. **[[TASK-0625-The-Checks-Page-Groups-By-Screen]]** once project-os-dev TASK-0116 states the surface rules. Independent of 1 to 3.
5. **[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]** last, after your-trainer TASK-0906 writes real procedures.

## Dependencies

- **Hard:** project-os-dev TASK-0119 fixes the procedure format before any task here starts. project-os-dev ADR-0044 and ADR-0045 were accepted on 2026-09-14. project-os-dev TASK-0123 syncs the module so `walk_sheet_bundled.py` stays byte-identical.
- **Hard:** your-trainer TASK-0906 before TASK-0626.
- **Soft:** your-trainer TASK-0904 (captures) before TASK-0622 is checked on real images.

## Decided 2026-09-14

Edwin: "v2.2.0 should wait. go with your recommendations for the others, will I start the project-os-dev and cockpit phase first?"

- Step ticks live in the cockpit's per-workspace browser storage, never in the repo or the ledger (TASK-0624).
- The worst step mark decides the check's verdict (TASK-0624).
- A pass from a procedure step is within ADR-0041, because each expectation line quotes the check's Expect text word for word and the upstream validator checks it.
