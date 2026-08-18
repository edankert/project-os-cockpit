---
type: "[[task]]"
id: TASK-0487
aliases: ["TASK-0487"]
title: "Invert VERIFY — resolve a feature's tests from a reverse index over `covers:`"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0121-The-Verification-Link-Normalises]]"]
parent: "[[FEAT-0121-The-Verification-Link-Normalises]]"
effort: M
depends: ["[[TASK-0486-Backfill-Covers-On-The-Ten]]"]
blocks: []
related: []
tests: []
---

# Invert VERIFY

`validate-docs.py` reads `entry.get("tests")` and `fm.get("tests")` off the feature and demands each linked test be `passing`. It must instead build a reverse index over every test's `covers:` once at load, and look the feature up in it.

**The validator has no index of its own** — it works from `SNAPSHOT.yaml` plus note frontmatter, so it builds one. The cockpit's `Index` already has a backlink graph and is not available here; the bundled mirror must match the script exactly, as always.

**Prove the inversion is behaviour-preserving before it ships:** run both implementations over the current fleet corpus and assert the same VERIFY violations, note for note. An inversion that changes which violations fire is a silent gate change, and this gate is what keeps a feature from reaching `done` unverified.

Done when: both validators resolve by reverse index, the violation set on the fleet is identical to the field-based one, and twelve repos still validate green.
