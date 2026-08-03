---
type: "[[feature]]"
id: FEAT-0065
aliases: ["FEAT-0065"]
title: "The acceptance-debt surface: which requirements have no verification, which criteria sit unticked, what was ticked without evidence"
status: planned
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Review 2026-08-03: the overview says 23/23 tests passing and never says which requirements have no test at all"]
goal: "A record-column card answering the coverage questions the Verification card cannot: REQs with no verifying TST, criteria unresolved on non-terminal notes, ticks carrying no evidence — each count opening to its rows."
requirements: []
tasks: []
release: ""
related: ["[[FEAT-0018-Verification-Health-Surface]]"]
tests: []
---

# Acceptance debt

## Goal

Three numbers that exist nowhere: unverified requirements (no TST names them in `verifies:`), unresolved criteria on live notes, evidence-free ticks. All derivable from frontmatter and the criteria parse the validator already does — this is a payload plus a record-grammar card, no new data.

## Out of Scope

- Enforcing anything. The surface makes debt visible; the gates stay where they are.
- Fleet-wide roll-up (a later fleet-surfaces item, if the per-repo card earns it).
