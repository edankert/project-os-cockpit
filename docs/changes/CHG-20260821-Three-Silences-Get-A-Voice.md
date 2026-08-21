---
type: "[[change]]"
id: CHG-20260821-Three-Silences-Get-A-Voice
aliases: ["CHG-20260821-Three-Silences-Get-A-Voice"]
title: "A held-back feature says why, an orphaned surface is reported, and a verdict nobody answered is counted — three states the record could not express"
status: merged
owner: user:edwin
created: 2026-08-21
updated: "2026-08-21"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[TASK-0576-An-Exclusion-Says-Why-And-What-It-Cost]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]", "[[ISS-0253-A-Verdict-Outlives-The-Work-It-Judged]]", "[[ISS-0252-Two-Sessions-Closing-Out-Collide-In-The-Snapshot]]", "[[ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"]
tags: [change, validator, release, review]
---

# Three silences get a voice

Four changes, one shape: **a number, a state or a decision that the record had no way to express, so it was expressed by nothing.**

## 1. An exclusion says why, and the page says what it cost ([[TASK-0576]])

`note_writes.release_contents` gains a **fourth refusal**: a removal with no reason is a 400. The reason lands in `held_back:` on the release note, beside `features:` — one file, one diff — and re-adding the feature retires the entry.

The release page reads `N feature(s) held back · M check(s) no longer gating`, in **one sentence**, with the cost read from `gate.deselection.checks` so the page cannot report a number the gate never computed. An exclusion with no recorded reason draws as *"no reason recorded (hand-edited)"* rather than being filled in.

**Two things were unreachable and are now not.** `Remove` was guarded on `c.kind !== 'derived'` and no third kind was ever emitted, so a feature could be added through the front door and never taken back out through it — `contents.kind` is `chosen` now when a release names its contents. And the held-back set was read with `index.by_id(release_id)`, which is `None` on `~release/next`, so the subtraction never fired on the page a person actually opens.

## 2. `SURFACE-ORPHAN` ([[ISS-0250]])

A check's `area:` naming no surface is now reported by the validator — **one finding per orphaned name, not per check**, guarded on *"this repo has surfaces"*, and warned with a promotion date of `2026-11-18`. **21 distinct names over 34 checks** in this repo at introduction; zero in the other eleven, which hold no `SUR-*` note.

Editing a surface's `title:` moved its coverage to zero and moved nothing else, and the two states rendered identically: a surface nobody has tested and a surface whose 91 checks were orphaned by one em dash retyped as a hyphen both read *"no checks"*.

The reverse direction is **not** reported: a surface no check names is the row [[FEAT-0130]] built the type to produce.

## 3. `review_response:` and `REVIEW-STALE` ([[ISS-0253]])

A new frontmatter field — `review_response:` with `review_response_date:` — where the author records **what was done about the findings**, without touching the verdict. `review_verdict` stays the reviewer's; self-clearing it turns an independent gate into a formality.

`REVIEW-STALE` reports a note at a terminal status carrying an owed verdict with no response. It fires on **exactly 43** notes, which is the number [[ISS-0253]] measured by hand. Warned, promoting `2026-11-18`. **None of the 43 was flipped.**

It deliberately does **not** trigger on `updated:` later than `review_date:` — [[ISS-0007]] records that heuristic re-arming a gate on any edit, and stamping a verdict *is* an edit, so 85 of 103 verdicts in this corpus have `updated <= review_date`.

The review desk's register rows now read `answered <date>` or `no response recorded`.

## 4. Two smaller ones

**`close-out-commit.sh` names its `SNAPSHOT.yaml` membership changes** ([[ISS-0252]]) — added, removed, and separately **dangling**: an entry whose note is in no commit, which turns `--as-committed` red and does not self-heal. Reported in stderr and in the commit message; never refused.

**`POST /api/notes/retire-check`** ([[ISS-0249]]) — `retire_check` was a complete, tested write path no front door reached. It is routed now, loopback-guarded like the other 27, with a `Retire` control on `~checks`. Wiring it found that it wrote `verdict_reason:`, a field this repo's validator refuses — so it would have failed the commit it was part of, and nothing caught it because nothing called it.

## Behaviour a caller can see

- `POST /api/notes/release-contents` with `action: "remove"` and no `reason` now returns **400**.
- `POST /api/notes/retire-check` exists; the guarded-route count moved 27 → 28.
- Two new validator codes, both warnings until `2026-11-18`: `SURFACE-ORPHAN`, `REVIEW-STALE`.
- `release_payload().contents.kind` can be `"chosen"`, which it never was before; `contents.held_back` and `gate.deselection` are new keys.
