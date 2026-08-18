---
type: "[[feature]]"
id: FEAT-0122
aliases: ["FEAT-0122"]
title: "The axes stop implying each other — `kind:` is deleted, one predicate answers who runs a test, and re-arming follows execution rather than level"
status: done
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
goal: "Separate execution from level: delete `kind:` because `command:` already answers it, collapse the two who-runs-this predicates into one, key `invalidated_by:` on execution rather than on level, and move the 22 notes to a level that describes what they exercise rather than who walks them."
requirements: ["[[REQ-0041-One-Answer-To-Who-Runs-This]]"]
tasks: ["[[TASK-0491-Tier-The-Twenty-Two]]", "[[TASK-0492-Retire-The-Manual-Run-Obligation]]", "[[TASK-0493-One-Who-Runs-This-Predicate]]", "[[TASK-0494-Change-Replaces-Time-As-Staleness]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]]", "[[ISS-0202-Needs-A-Run-Versus-The-Tiers]]", "[[ISS-0195-Two-Types-Carry-One-Act]]"]
---

# The axes stop implying each other

*(Re-scoped 2026-08-18 under [[ADR-0034-Three-Axes-Not-One-Word]], which supersedes ADR-0033. This feature was "collapse the manual population"; it is now "execution stops being implied by level". The 22 notes still move — as a consequence rather than as the point.)*

**The residue is small and the simplification is not.** 22 notes fleet-wide — 5 here, 15 in `your-trainer`, 2 in `your-health` — against a surface that currently carries two verdict fields, two re-arming models, two gates and two verbs for one act.

**The tiering is a judgement per note, not a bulk rewrite.** Tier 1 for a capability, Tier 2 for a regression guard that names its `ISS-*`, Tier 3 for a one-build verification — and Tier 3 is the real find here, because it is where the genuinely transient cases go and it retires them after a verified release exactly as TESTING.md already describes.

**`kind:` is deleted rather than constrained.** `command:` already answers who runs a test, and two fields answering one question is precisely how the reader and the registry came to disagree about 8 of 788 notes. A constraint would leave both fields and add a rule; deleting one leaves nothing to disagree with.

**Re-arming moves onto the right axis.** A machine re-runs on every commit, so currency is free; a person does not, so *"has something changed under this walk"* must be recorded. `invalidated_by:` therefore belongs to **any test with no `command:`** — at any level — and the 90-day threshold retires for that population. That is the cleanest thing to fall out of Edwin's argument and it was invisible while `acceptance` meant `manual`.

**The one thing this feature must not do** is move acceptance rows onto a badge. Retiring `Needs a run` means the manual population stops asking *individually*; it does not mean 669 rows start.
