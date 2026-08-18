---
type: "[[requirement]]"
id: REQ-0041
aliases: ["REQ-0041"]
title: "One answer to 'who runs this' — the reader and the registry must never disagree about a test"
status: implemented
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: "obligation registry"
implements: "[[FEAT-0122-One-Human-Walked-Population]]"
acceptance:
  - "[x] One predicate decides who runs a test — `obligations._is_owed` calls `cockpit._is_manual_test`. 788 tests fleet-wide, 0 disagreements; it was 8."
  - "[x] `kind:` is gone from every note AND from all four `test.md` templates — the three fleet templates still carried it when this was first ticked."
  - "[x] `automation:` stopped answering who-runs-this too. Set on 671 of 788 notes and reading `manual` on 466, it would have become the second declaration the moment `kind:` went."
  - "[x] The predicate is `not command:`, with no fallback: four heuristics collapsed to the one question the corpus can answer."
  - "[~] The badge is not larger than the number it replaced — reconciled at TWO rises, both true: your-sudoku 0 -> 1 (TST-0013) and obsidian-supernote-sync 0 -> 1 (TST-0004). Both claimed to be automated with no `command:`, so nothing could run them. The second went unrecorded until the second independent review found it."
  - "[x] No acceptance row reaches a badge in any repo."
covers: []
related: ["[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
---

# One answer to who runs this

Two predicates decide this today and they are written in different places: the reader asks `command:` first, and the registry asks whether `kind`/`level`/`runner` contains the word *manual* and never reads `command:` at all. **The registry's is the one that fills `Needs a run` and the badge** — so the surface a person acts on is driven by the weaker rule.

Eight tests disagree between them fleet-wide. None involves a `command:`, which is why nothing has broken yet and also why nothing would announce it when it does.

## Acceptance criteria

- [x] **One predicate decides who runs a test.** `obligations._is_owed` calls `cockpit._is_manual_test`. Verified across the fleet: 788 tests, **0 disagreements** — it was 8.
- [x] **`kind:` is gone** from every note fleet-wide and from **all four** `test.md` templates. *Ticked prematurely on 2026-08-18 and corrected: the three fleet templates still carried it, so the scaffold went on creating the field the decision deleted.* The note counts are **727** demonstrable from history rather than the 731 first written — `your-trainer` is 593, not 597, because four notes were untracked when the script ran.
- [x] **And `automation:` stopped answering it too.** Deleting `kind:` while `_is_manual_test` still read `automation:` would have **moved** the ambiguity rather than removed it: that field is set on 671 of 788 fleet notes and reads `manual` on 466. It answers *does a machine cover this check*, beside `covered_by:` — a coverage claim, not a declaration of who walks it. Found by independent review.
- [x] **The predicate is now `not command:`, with no fallback at all.** Four heuristics collapsed to the one question the corpus can actually answer: a note with no `command:` cannot be run by anything but a person.
- [~] **The badge is not larger than the number it replaced.** Reconciled at **two** rises, and I recorded only one. `project-os-cockpit` **1 → 0** (TST-0024 correctly quieted by the ISS-0202 fix), `your-trainer` 5 → 5, `your-health` 2 → 2, **`your-sudoku` 0 → 1** (TST-0013) and **`obsidian-supernote-sync` 0 → 1** (TST-0004) — the second found only by the second independent review. TST-0013 declared `kind: automated` with no `command:` — precisely the state the old entrypoint guard existed to flag — so under a rule with no heuristics it is correctly owed to a person until somebody gives it a way to run. *The committed pre-change figure for `your-trainer` was **3**, not 5; 5 was true of that day's working tree and is not reproducible from the repository.* It *did* move — `your-trainer` went to 8 the moment the predicates were unified, because three frozen per-release suites at `status: ready` started asking to be walked. They are `retired` now, which is what they are.
- [x] **No acceptance row reaches a badge** in any repo.

## Advanced 2026-08-18

The third criterion is the one worth reading. Unifying the predicates **raised a badge before it settled it**, and the rise was correct — the reader was right that those three notes are human-walked, and the registry had been hiding them behind a weaker rule. The fix was to say what the notes actually are, not to re-weaken the predicate.

## A third field, found and deliberately not read

`obsidian-supernote-sync`'s TST-0004 carries `entrypoint: "pytest tests/test_markdown_to_pdf.py -v"` — a runnable command in a field `_is_manual_test` does not read, which is why it moved onto the badge.

**`entrypoint:` is not made a second who-runs-this field, and the corpus is why.** 37 notes carry one without a `command:`, and the values are a mix: some are commands, others are prose — *"the discovered fleet under ~/Dev/repos"*, *"Publication → Release gate, against a t…"*. Reading it would reintroduce exactly the ambiguity ADR-0034 removed, on a field where half the values cannot be executed.

The honest fix is per note: if it is runnable, it belongs in `command:`. Filed as [[ISS-0207-Entrypoint-Is-Two-Fields-Wearing-One-Name]] rather than guessed at across four repos.
