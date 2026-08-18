---
type: "[[feature]]"
id: FEAT-0121
aliases: ["FEAT-0121"]
title: "The verification link normalises — `covers:` on the test is the only encoding, VERIFY inverts, and the path stops meaning anything"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
goal: "Replace three encodings of one relationship with one: the test's `covers:`, in the direction test → subject. A feature stops listing its tests, VERIFY builds a reverse index instead of reading a field, and a test's location on disk becomes a filing decision with no semantic weight."
requirements: ["[[REQ-0040-One-Verification-Link]]"]
tasks: ["[[TASK-0486-Backfill-Covers-On-The-Ten]]", "[[TASK-0487-Invert-VERIFY]]", "[[TASK-0488-Drop-The-Feature-Tests-Field-And-The-Path-Fallback]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ISS-0199-Twenty-Of-Sixty-One-Feature-To-Test-Edges-Are-Not-Reciprocated]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]"]
---

# The verification link normalises

**Independently true, and it is also the thing that closes [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]'s last hole.** VERIFY reads a feature's `tests:` and demands `passing`; an acceptance test rests at `active`. Deleting the field means an acceptance test can never reach that lookup — by construction, not by an exemption for `level: acceptance`, which is the standard this whole phase is being held to.

**The measurement that decides the direction**: 20 of 61 feature→test edges are already unreciprocated, and 112 of 669 checks fan out to more than one subject. The many side is where the key belongs.

**Order matters here.** Backfill the ten first, then invert VERIFY, then delete the fields — inverting before the backfill would make ten features look unverified for the length of a commit, and deleting before inverting would take the gate offline.
