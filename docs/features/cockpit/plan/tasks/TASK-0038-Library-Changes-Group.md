---
type: "[[task]]"
id: TASK-0038
aliases: ["TASK-0038"]
title: "Cockpit: add Changes group to Project (Library) rare-types"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0016]]"]
fixes: []
effort: XS
due: ""
depends: []
blocks: []
related: ["[[TASK-0036]]", "[[TASK-0037]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0038 — Changes group in Project section

## Definition of Done
- [x] `"change"` added to `LIBRARY_RARE_TYPES`, leading the list so the Changes group renders first in Project mode.
- [x] Group label resolves to `"Changes"` via the existing fallback (`type_name.title() + "s"`); no change to `_pluralise_for_label`.
- [x] Items use the standard `_rare_item` shape (id + human title, no subtitle, type=change so the JS picks the git-commit type icon).
- [x] Test confirms the group exists with the expected label and that items carry CHG- ids and `type: "change"`.

## Steps
- [x] Edited `LIBRARY_RARE_TYPES` in `cockpit.py`.
- [x] Added `test_nav_payload_library_includes_changes_group` to `tests/test_cockpit.py`.

## Notes
Live confirmation against `your-trainer/docs`: 129 change items render in the new Changes group at the top of the rare-types section. Decisions / Releases / Risks / Tests / Workflows follow in their previous order.
