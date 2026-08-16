---
type: "[[issue]]"
id: ISS-0178
aliases: ["ISS-0178"]
title: "A test has no terminal status, so a test whose subject was deleted must either keep claiming to verify it or be deleted — and this project's own rule forbids deleting completed notes"
status: "open"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: 2026-08-16
source: ["Found 2026-08-16 retiring TST-0029/TST-0030 when FEAT-0107 deleted the acceptance stepper they guarded"]
severity: medium
component: docs-template
parent: ""
related: ["[[FEAT-0107-Publication-Is-A-List-Of-Releases]]", "[[ADR-0008]]"]
tests: []
---

# A test cannot be retired

## Problem

`STATUSES.md` allows a `[[test]]` exactly `ready`, `passing`, `failing`. **There is no terminal status.** Every other type has one — `superseded` for phases and designs, `cancelled` for tasks and features, `retired` for requirements, `declined` for issues.

So when a test's subject is deleted, there are three moves and all are wrong:

1. Leave it `passing` — it claims to verify something that no longer exists, and `test_every_test_named_in_a_note_exists` then fails on the missing file.
2. Write `superseded` — the validator refuses it (`NOTE-STATUS`).
3. Delete the note — forbidden by LIFECYCLE.md: *"Do not delete completed notes; use status + links to preserve history."*

Hit while retiring [[TST-0029]] and [[TST-0030]], whose stepper [[FEAT-0107]] deleted. Both were `passing` against a real run; the run happened and the surface is gone.

## Why `ready` is the workaround and not the answer

`ready` means *defined but not yet executed*, which is true of a test whose subject was deleted — but it says nothing about **why**, and it puts a retired test back in the "Needs a run" bucket where somebody may pick it up. The supersession currently lives in prose, and prose is not what any tool reads — the same shape as [[ISS-0155]], where a never-run manual test had to assert a verification date it had not earned.

## Expected

A terminal status for a test — `superseded` would match every other type — proposed **upstream**, since `STATUSES.md` is template-owned and a local addition would report as divergence on the next sync.

Until then the workaround is `ready` plus a section saying what happened, which is what [[TST-0029]] and [[TST-0030]] now carry.
