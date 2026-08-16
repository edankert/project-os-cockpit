---
type: "[[task]]"
id: TASK-0423
aliases: ["TASK-0423"]
title: "An obligation's view is decided per item rather than fixed per note type, and a kind with no routing rule fails a test"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[ADR-0028]] decision 2"]
parent: "[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]"
effort: M
depends: ["[[ADR-0028-Work-Has-Three-Phases]]"]
blocks: ["[[TASK-0424-The-In-Flight-Predicate]]"]
related: ["[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
tests: ["[[TST-0025-Obligation-Routing-Is-Per-Item-And-Complete]]"]
---

# An obligation's view is decided per item

## What

`Obligation.view` is a fixed string per note type, and both walks read it directly — `obligations.py:543` (`bucket = out[ob.view]`) and `:587` (`out[ob.view].append(...)`). `NoteLessObligation.view` is the same shape.

Make the view derivable from the record, keeping the declaration as the default. A type that routes one way always keeps declaring a plain string; a type whose view depends on its subject declares a resolver.

## Why it is its own task

**No behaviour changes here.** Every item routes exactly where it routes today, so the existing suite staying green at its current count is the proof. [[TASK-0424]] is where the numbers move, and keeping the two apart means the behavioural diff is small enough to read.

## Definition of done

- [ ] An obligation's view is resolved per item; the fixed-string declaration remains valid and is what every current type uses
- [ ] `counts_by_kind` and `owed_items` still perform **one** walk over one predicate, and the existing assertion that the page and the badge are one computation still passes
- [ ] A note type or note-less source reachable in the corpus with no routing rule **fails a test** — the completeness burden the registry already carries for undeclared types, extended to routing, so per-item routing cannot become the place a kind goes missing quietly
- [ ] `payload()` reports how each kind routes, so the registry stays self-describing rather than needing the code read
- [ ] `obligations.py:34`'s one-type-one-view comment is rewritten to state the invariant that actually holds now — one item, one row — and to name [[ADR-0028]] as what changed it
- [ ] Full suite green at its current count with no test modified except the routing-completeness addition; a diff that needed existing assertions relaxed means the refactor changed behaviour
