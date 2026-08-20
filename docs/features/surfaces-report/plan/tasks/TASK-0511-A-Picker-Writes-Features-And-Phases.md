---
type: "[[task]]"
id: TASK-0511
aliases: ["TASK-0511"]
title: "A preparing release can add and remove features and phases, written to its note"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
parent: "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# A preparing release can add and remove features and phases, written to its note

Writes `features:` on the release note through the existing write service, with its refusals. A phase contributes its features rather than being stored separately.

Opt-in: a release naming nothing keeps derived contents (REQ-0048 criterion 4). Eleven historical releases depend on that.

## Done 2026-08-20 — the picker

Add and remove on a preparing release, on the release page, through `POST /api/notes/release-contents` ([[TASK-0558]]). Fourteen tests across the two tasks, two more mutants run here.

### The candidate list is server-owned, and that is the point

*"Without the candidate list the control is a text box, and a text box for an id is how [[ISS-0142]] happened."* `publication.contents_candidates` returns done-but-unshipped, minus what this release names, minus anything **another open release on the same platform** claims.

It lives on the server because that last rule is the same one the write path refuses on. Two implementations of one question is [[REQ-0059]]'s forbidden shape, and this phase has already found three — `_covers_an_issue`, `_verdict_is_owed`, and the validator's *preparing*. Not a fourth.

### The first add is a semantic jump, and the page says so before the click

**[[REQ-0048]] criterion 4**: a release naming nothing keeps **derived** contents, and eleven historical releases depend on it. Naming one feature switches the release to chosen — so the other rows *stop being in it*. On `your-trainer` today that is 32 rows becoming 1.

A control that made that switch silently would be the worst kind of convenience, so the derived case carries a warning in the contents section, and a test asserts the sentence is there.

### Remove is offered only on rows the release names

A derived row is not a choice anybody made, so there is nothing to take back — and a remove there would have to name the whole contents first, silently, which is exactly the jump the warning exists to make explicit. Mutant run: offering it on derived rows fails.

### The renderer re-decides nothing

All three refusals stay in `note_writes`. A rule enforced in the renderer is a rule the other front door does not get ([[ISS-0230]]), so this posts and reports, and repaints from the server rather than patching the DOM — the candidate list, the contents and the gate move together, and three hand-patched lists are how two of them come to disagree.

## Still open

**The browser cockpit does not have this control.** [[ISS-0230]]'s lesson is *both front doors, or the difference is decided and recorded* — this records it: the write path is shared and loopback-only, so the browser can gain the same control without new server work, and it is a deliberate follow-up rather than an oversight.

**A phase does not yet contribute its features.** [[REQ-0048]]'s second criterion — *a phase contributes features; no second encoding* — is unbuilt. The write path takes a feature id; adding a phase means expanding it to its features at the moment of the click, which is a decision about whether the expansion is remembered or re-derived, and that has not been made.
