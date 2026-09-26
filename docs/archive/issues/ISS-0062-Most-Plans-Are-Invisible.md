---
type: "[[issue]]"
id: ISS-0062
aliases: ["ISS-0062"]
title: "19 of 33 plans are invisible in the cockpit — the Library group shows only the typed ones"
status: fixed
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
severity: medium
component: cockpit-nav
parent: "[[FEAT-0046-Plans-On-The-Feature]]"
related: ["[[PHASE-010-Surface-Ownership]]", "[[TASK-0037-Exclude-Canonical-Container-Dirs]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
---

# ISS-0062 — Most plans are invisible

## Problem

Library's Plans group is populated by `index.notes_by_type("plan")`, which reads `type: "[[plan]]"` from frontmatter. Only 14 of this repo's 33 `PLAN.md` files carry any frontmatter at all. The other 19 have none — they open straight into an `# Plan — …` H1.

Those 19 are not merely missing from the group. They are unreachable from anywhere in the UI: `features` is listed in `DOC_TREE_EXCLUDED_ROOTS` (`cockpit.py:175`, [[TASK-0037]]), so untyped notes under `docs/features/` never join the Docs tree either. The index holds them — it derives a title from the H1 — and nothing renders them.

## Repro

```
$ find docs -name PLAN.md | wc -l
33
$ grep -rl 'type: "\[\[plan\]\]"' docs --include=PLAN.md | wc -l
14
```

```
$ .venv/bin/python -c "
import sys; sys.path.insert(0,'src')
from pathlib import Path
from project_os_cockpit.index import Index
from project_os_cockpit import cockpit
idx = Index.build(Path('docs'))
p = cockpit.nav_payload(idx, mode='library', project_root=Path('.'))
g = [x for x in p['groups'] if x['key'] == 'rare:plan'][0]
print(len(g['items']))
"
14
```

## Expected

Every delivery plan is reachable from the feature it plans.

## Evidence

The index does hold them — an untyped plan resolves to a `NoteRecord` with `note_type=None` and a title derived from the H1:

```
NoteRecord(rel_path='features/agent-verbs/plan/PLAN.md', frontmatter={},
           title='Plan — FEAT-0024 Agent verbs', note_id=None, note_type=None, status=None)
```

## Actual

14 rendered, 19 unreachable.

## Next Actions

- [ ] Associate plans with features **by path** (`features/<slug>/plan/PLAN.md` beside `features/<slug>/FEAT-*.md`) rather than by frontmatter type, so typing is not a precondition for visibility — [[TASK-0235]]
- [ ] Render the plan as a child of its feature in the Features mode — [[TASK-0236]]

## Notes

Counts above are as measured at filing (2026-07-29, before [[PHASE-010]] created its own five features, which took the corpus to 38 plans / 19 typed). The fix and its test assert against the filesystem rather than these figures — the property is "every plan on disk resolves", and a frozen number would fail on the next feature anyone adds.

Deliberately **not** fixed by adding `type: "[[plan]]"` to the 19 files. That would make the count pass while leaving the mechanism dependent on frontmatter nobody is required to write — and it would hide whether the path-based lookup works. The path already encodes the relationship; reading it is the fix.
## Independent review — 2026-07-30, approved

Fresh session, `model:claude-opus-5`, from the notes and the diff for `bed48ea`.

The diagnosis reproduces exactly. At `bed48ea~1`: 33 `PLAN.md` files on disk, 14 visible through `notes_by_type("plan")`. At `bed48ea`: 38 on disk, 19 typed, 38 reachable. The compounding claim is also true — `features` is in `DOC_TREE_EXCLUDED_ROOTS`, so the 19 reached no surface at all rather than merely missing one group. Reverting `_feature_plan` to a type-based lookup fails two assertions, so the fix is guarded and not just present. No findings.
