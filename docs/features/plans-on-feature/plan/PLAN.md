---
type: "[[plan]]"
title: "Plans on the feature — delivery plan"
status: done
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
implements: ["[[FEAT-0046-Plans-On-The-Feature]]"]
related: ["[[ISS-0062-Most-Plans-Are-Invisible]]"]
---

# Plans on the feature — delivery plan

## Delivery sequence

1. **[[TASK-0235]]** — `_feature_plan_path()` in `cockpit.py`: given a feature record, look for `plan/PLAN.md` in its own directory. Path-derived, so frontmatter is not a precondition. Test asserts 33 across the corpus.
2. **[[TASK-0236]]** — `_features_groups` attaches the plan as a child item; the renderer's existing `children` handling picks it up with no change. Status chip when the plan has one, omitted when it does not.

## Sequencing note

Both tasks land before [[FEAT-0050]] removes the Library group — the destination has to exist first ([[REQ-0025]]).
