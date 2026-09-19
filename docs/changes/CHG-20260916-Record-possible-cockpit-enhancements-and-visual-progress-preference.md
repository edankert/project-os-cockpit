---
type: "[[change]]"
id: CHG-20260916-Record-possible-cockpit-enhancements-and-visual-progress-preference
title: "Record possible cockpit enhancements and visual progress preference"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Edwin 2026-09-16: record the review as possible future enhancements; retain percentages, progress bars, colours and status badges."]
commit: ""
pr: ""
impacts: []
issues: []
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[REFERENCE-FUTURE-COCKPIT-ENHANCEMENTS]]"]
---

# Record possible cockpit enhancements and visual progress preference

## Summary
Record the cockpit review in a dedicated future-enhancements reference section. Incorporate Edwin's preference for percentages, progress bars, colours and status badges, with short explanations for blockers and decisions. These are ideas for later design work, not approved implementation scope.

## Impact

- No screen changed: documentation only; add the reference and index links, and record this work in the snapshot.
- Preserve existing snapshot context and escape unescaped quotation marks inside its focus note so the updated YAML parses.

## Documentation Coverage (All Types Considered)
- features: not-applicable — possible enhancements are not committed features.
- requirements: not-applicable — capture the user's preference in the reference without creating a product requirement.
- tasks: not-applicable — no implementation is scheduled.
- issues: not-applicable — retain dated review observations without opening or changing issue state.
- tests: not-applicable — no runtime behavior changes; run documentation validation.
- workflows: not-applicable — proposed journeys are discussion material.
- decisions: not-applicable — no ADR is accepted or superseded.
- risks: not-applicable — reference the existing design-approval risk without changing its state.
- changes: new — this documentation change note.
- snapshot: updated — record the documentation work and its change note, preserving the existing issue focus.

## Validation

- `bash tools/agents/check-docs-first.sh` — passed.
- `bash tools/scripts/validate-docs.sh` — passed with existing corpus warnings.
- Strict YAML parsing of SNAPSHOT.yaml and reference frontmatter — passed; ISS-0312 remains the issue focus.
- `git diff --check` — passed.

## Follow-ups
Any enhancement selected later needs its own design and documentation intake. The reference does not authorize implementation.
