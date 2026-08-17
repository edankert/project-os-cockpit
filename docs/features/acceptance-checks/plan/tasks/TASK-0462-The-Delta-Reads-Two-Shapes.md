---
type: "[[task]]"
id: TASK-0462
aliases: ["TASK-0462"]
title: "The delta reads two shapes — file-shape at old refs, ls-tree + cat-file at new ones, parity at every real tag"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
parent: "[[FEAT-0113-The-Check-Type-And-The-Migration]]"
effort: S
depends: ["[[TASK-0461-Pilot-This-Repo]]"]
blocks: []
related: ["[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]"]
tests: []
---

# The delta reads two shapes

`suite_at` grows a permanent two-line branch: try `git show <ref>:docs/tests/ACCEPTANCE_TESTS.md` — that answers for every ref before the cut, which is all twelve of `your-trainer`'s current tags — and on `None`, read the note shape. The note-shape read is **two subprocesses, not N**: `git ls-tree -r <ref> docs/tests/acceptance/` piped into `git cat-file --batch`. The residual cost is ~579 frontmatter parses × 12 tags on a cold delta; the `_at_ref` cache exists — measure it rather than assuming it.

## Done when

- [ ] `gate_payload` at every real `your-trainer` tag returns the same blocking numbers after the cut as before it — asserted against the recorded series, not eyeballed.
- [ ] The cold-delta cost is measured and recorded in this note; the cache holds it inside the current budget.
