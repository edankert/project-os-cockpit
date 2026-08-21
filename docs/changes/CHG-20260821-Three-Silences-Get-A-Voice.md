---
type: "[[change]]"
id: CHG-20260821-Three-Silences-Get-A-Voice
review_verdict: changes-requested
review_response: "2026-08-21: the REVIEW-STALE figure of 43 was two errors agreeing. Corrected to the measured 51 at f5ca55b, with the note that the rule could not see CHG-* notes at all. || Second pass 2026-08-21: the corrected 51 reproduces at f5ca55b. No further change to this note."
review_response_date: 2026-08-21
review_date: 2026-08-21
reviewed_by: model:claude-opus-5
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

`REVIEW-STALE` reports a note at a terminal status carrying an owed verdict with no response. It fires on **51** notes at `f5ca55b`. Warned, promoting `2026-11-18`. **None of the 51 was flipped.**

*(It reported 43 for one commit and [[ISS-0253]] had filed 43, and the agreement was a coincidence of two errors: the issue's count was never re-measured, and the rule read `note_index`, which holds no `CHG-*` note — 8 of the 51 are change notes and every `merged` one is. It walks the files now.)*

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

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: changes-requested.** Two of the three sections are accurate; the third repeats a number as independent corroboration when it is not.

### Accurate

- *"21 distinct names over 34 checks"* — reproduces exactly. 21 warnings emitted, per-name counts summing to 34, which is every acceptance check in the repo.
- The [[ISS-0252]] section is accurate, and the dangling detection fails when mutated.
- *"None of the 43 was flipped"* — confirmed. `grep` finds no `review_verdict` change on those notes in this diff.

### Finding — *"it fires on exactly 43 notes, which is the number ISS-0253 measured by hand"*

The two numbers are not the same population and neither confirms the other.

`ID_PREFIXES` in `validate-docs.py` has no `CHG`, so `build_note_index` indexes no change note and `REVIEW-STALE` **cannot fire on one**. Measured against `git archive f5ca55b`: **56** owed verdicts, **51** terminal, **8** of them `CHG-*`. 51 − 8 = 43.

[[ISS-0253]]'s hand count was itself 49/43 against an actual 56/51, and its breakdown claims *7 merged* — a class the rule can never report, since every `merged` note here is a `CHG`. An undercount and a structurally-blind rule landing on the same integer is exactly the shape this change set was written to remove.

Correct the sentence, or fix `ID_PREFIXES` and restate the number. Detail on [[ISS-0253]].

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**This supersedes the first-pass verdict. The `review_response:` above is accurate**: the 43 was two errors agreeing, and 51 is the measured figure. I reproduced both independently against `git worktree add … f5ca55b`, driving the rule's own predicates (`OWED_VERDICTS`, `REVIEW_TERMINAL_STATUSES`, `has_value`) over the tree: **56** notes carry an owed verdict, **51** of them at a terminal status with no `review_response:`, broken down **30 `done` / 8 `merged` / 4 `implemented` / 9 `fixed`** — exactly the corrected claim. Walking `build_note_index` instead of the files over the same tree yields **43**, missing exactly the 8 `CHG-*` notes and nothing else. The file walk drops nothing that the index walk reported, and `__templates__` / `__bases__` are excluded. The claim is right and the fix is right.

**Finding F (low-medium) — three of the four numbers in that sentence were re-measured and the fourth was carried over unchecked, and the refuted figures survive in three other places.** The corrected `PROMOTIONS` comment reads *"**51 findings in this repo** … 30 `done`, 8 `merged`, 4 `implemented`, 9 `fixed`, **dating to 2026-08-02**"*. Measured at `f5ca55b`, the earliest `review_date` among those 51 is **2026-07-30**, on six notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`. The date came from the original filing and was the one field the re-measurement did not touch. Separately, the refuted breakdown is still asserted in the present tense at `tools/scripts/validate-docs.py:279` — *"the population it describes is 27 `done`, 7 `merged`, 4 `implemented` and 5 `fixed`"* — and the rule's own header comment still says *"49 notes carry `changes-requested`, 43 of them at a terminal status"* and *"Six of the 49 are that"*. Two sites were corrected and four were not, so the file now states both numbers about one population, twenty lines apart.
