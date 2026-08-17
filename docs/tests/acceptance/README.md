---
type: "[[reference]]"
id: ACCEPTANCE-TESTS
aliases: ["ACCEPTANCE-TESTS", "ACCEPTANCE_TESTS"]
title: "Acceptance checks — where they live and how to read their history"
status: active
owner: user:edwin
created: 2026-08-10
updated: 2026-08-17
scope: tests
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
---

# Acceptance checks

**One note per check**, in this directory, named `CHK-####-Slug.md`. `status:`
is the lifecycle (`draft`/`active`/`retired`) and **`mark:` is the verdict** —
ticking a check never touches its status. The suite is read as a list by the
cockpit's acceptance view; there is no document to open, because the document
*was* the display and that is the thing [[ADR-0030]] changed.

## Reading history from before the migration

Until `7de1a86` this whole suite was one file, `docs/tests/ACCEPTANCE_TESTS.md`, and every
check was a line in it. That file was **deleted** rather than kept as a
tombstone: two copies of one record is the dual-source trap this project has
paid for twice, and git holds the file intact at every ref before the cut.

- The suite as it stood at any earlier ref: `git show <ref>:docs/tests/ACCEPTANCE_TESTS.md`
- One check's full line-by-line history: `git log -L '/<the check name>/',+1:docs/tests/ACCEPTANCE_TESTS.md`
- Each note carries `migrated_from:` — its old `#section.ordinal` address and
  the sha above — because blame does not cross the migration commit (~2%
  similarity; rename detection will not fire). Traceability is preserved by the
  record, deliberately, rather than by git plumbing that cannot carry it.

## What the file said, kept verbatim

Everything below is the migrated document's own prose, unchanged. The tier
sections became the notes; this is everything else it held.

# Acceptance Test Suite: project-os-cockpit

## Test Tiers

- **Tier 1 — Feature Tests (permanent):** verify core user-facing capabilities; one or more per feature; never removed.
- **Tier 2 — Regression Tests (permanent):** guard previously-broken behavior; each references the `ISS-*` that created it.
- **Tier 3 — Verification Tests (temporary):** one-time checks for a specific build or fix; promoted to Tier 2 or removed after a verified release.

Full tier rules: `tools/instructions/TESTING.md`.

## Rules

1. New feature implemented → add Tier 1 test(s) under the feature's area heading.
2. Bug fixed → add a Tier 2 test referencing the `ISS-*`.
3. Any code change unchecks overlapping Tier 1/Tier 2 tests (mark for re-run).
4. A release is blocked while any Tier 1/Tier 2 test is unchecked (exceptions must be documented in the release note).
5. Tier 3 tests are removed or promoted after each verified release.

## Why this document exists, and what it is not

The tier contract has existed since the template was written. **No repo had ever instantiated it** — measured 2026-08-10 across the twelve the cockpit renders: 92 `TST-*` notes between them, zero tier classification, and a release gate that had never been able to fire. This is the first instance, created by [[TASK-0373]].

**It is not a second test register.** `TST-*` notes are formal specifications with frontmatter, procedure and evidence; 22 of this repo's 23 are automated pytest modules that CI runs on every commit. This document is the **manual acceptance checklist** — the things a person has to look at, which no pytest run can answer. `TESTING.md` is explicit that both coexist, and that is the reason the two populations are grouped separately in the Tests view rather than merged into one list.

**Tier lives here, not in `TST-*` frontmatter.** A `tier:` field on the notes was the obvious alternative and is wrong twice over: it would tier the wrong objects (Tier 1 is *"one or more per feature"* covering user-visible behaviour, while a `TST-*` is usually one pytest module covering an internal contract), and it would leave the checkbox — which is what the gate actually reads — with nowhere to live. Recorded here because the alternative is the one a reader will think of first.

**Created unchecked, deliberately** — nothing had been walked, which is the honest starting state for a checklist created the same day, and it meant the gate on [[REL-0001]] was firing rather than passing vacuously.

**34 of 34 Tier 1/2 settled — 33 ticked and 1 reconciled** (16 on 2026-08-10, then four passes on 2026-08-11, less one deliberately unticked and re-earned) **and 36 of 36 counting Tier 3**, each carrying how. *(Those two Tier 3 items retired on 2026-08-14 — [[ISS-0143]] — so the suite now holds 34, all gating. The 36 stands as the figure at [[REL-0001]]'s gate; it is not restated downward, because what it records is what was settled that day.)* **The gate is green**, on its first firing, with no *release exception* claimed and nothing rounded up — which is the only version of that sentence worth writing. (33 walked and 1 settled by decision is not 34 walked, and the two are kept apart everywhere the figure appears.) *The line here used to read "17 of 34", which mixed the tiers: 17 was the whole-suite count and 34 is the Tier 1/2 denominator the gate actually reads. Corrected on the recount, and worth a sentence because a gate figure that is off by one in the reader's favour is the kind of drift this document exists to stop.* The second pass was the *eyes on a rendered pane* row of [[REL-0001]]'s table — the tree, the actuator row, the Intent brief, a design artifact, the validator's answer and the History rows — all through `desktop/harness/live-harness.html` against a live sidecar, so what was judged is this repo's real corpus rather than a fixture. **The last check fell on 2026-08-11 and the blocker turned out to be misnamed.** 1.10.1's chip clause was held for *"a relaunched shell"*; what it actually needed was a **current renderer against a current sidecar**, which the harness supplies without restarting anyone's window — and once walked there, the observation that had held it open turned out to have been correct all along (the two chips sat on notes that session had genuinely touched). The write-path four were walked the same day against an **isolated clone** of this repo, so a probe tick, a probe capture and a probe test run exercised the real endpoints without putting probe writes in the record. **Nothing in this suite is now owed except by decision:** the one Tier 3 deep-link check is reconciled as unwalkable-by-construction, with its reasoning on the line itself.

**2.3.1 left this list by being fixed rather than waived.** It was blocked on [[ISS-0138]] — the browser front door rendered an error box for two of its three panes — so the defect was fixed, guarded by a test, and the check walked on both doors. That is the honest way a blocked check clears.

**1.11.1 also left this list by being fixed.** It asked the health surface to name the notes it counts; the surface counted and did not name, so the card was changed to read the per-error `id`/`rel` the payload has carried since [[FEAT-0018]]. Re-walked against four real errors: same count, same notes.

**Four of those went to the running shell over CDP on 2026-08-11** — 1.2.2 and 1.10.2 walked there, and 1.10.1 driven far enough to observe two of its three clauses. That pass produced its own finding, which is why the last two stayed open a while longer: **the Electron shell had been running for 1 day 23 hours**, so its renderer predates every session that touched this code. Anything it says about recent behaviour is evidence about a two-day-old build, and the one clause that looked wrong (agent chips on notes nobody touched) is exactly the shape a stale renderer produces. *It was not that shape.* Re-walked on current code the same evening, the chip is correct, and `.cockpit/sessions.json` shows the two notes it chipped were both in that session's own `work_notes` — **the caution was right and the diagnosis was wrong**, which is the good failure mode: distrusting an observation you cannot attribute costs an hour, and trusting one costs a defect report. Filed as [[ISS-0140]], **and fixed the same day**: `GET /api/cockpit/runtime` compares the running process against the code on disk, and the Verification card says *"sidecar and window are older than the code — restart to trust this"* when either is behind. It reports and never reloads — a window reloaded under someone mid-session is worse than the staleness it fixes.

**That framing was wrong and was corrected on 2026-08-11.** The residue was described as *"two checks that need an agent CLI started in the app's embedded terminal, which spends real tokens"* — but reading the terminal buffer showed **this walk was already running inside that terminal**, many turns deep. No tokens were needed; the evidence was the session doing the asking.

What is actually left is smaller and differently shaped:

- **1.9.1** — **closed 2026-08-11.** Scrollback fell to sending the wheel events and the read over **one CDP connection**, so no output could land between them; the earlier attempts failed because they keyed on `scrollTop`, which xterm never moves. Copy from the native context menu was witnessed by Edwin.
- **1.10.1** — **closed 2026-08-11, and the wait was self-imposed.** The clause was held for a restarted shell on the ground that `renderer.ts` had 25 commits since that window opened. True, and the wrong conclusion: what a stale renderer invalidates is *that venue*, not the check. A sidecar off this working tree plus the built bundle in the harness is a current pair, and the walk took minutes there. **Read the blocker as a property the evidence needs, not as a thing somebody else has to do first** — the two are easy to confuse and only one of them is ever yours to fix.

**Four findings came out of the 2026-08-11 passes, all filed:** [[ISS-0136]] five dark-only design artifacts; [[ISS-0137]] a criterion with inline markup cannot be ticked, which is **half this corpus's open criteria**; [[ISS-0138]] the browser front door's nav and context panes throw on every page; [[ISS-0139]] the Changes tile's code outlived the tile. And one check turned out to describe a surface retired **eleven days before this suite was written** (1.5.2), which is a finding about the suite rather than the product. None was visible to the 1137-test suite, which is green. That is the argument for this document existing. **No release exceptions are claimed** — an unwalked check is unchecked, not excused. *Amended after re-review, which found this sentence still reading as though every settled check had been walked: **two were not.** 1.5.2 and 3.2 are reconciled, a mark meaning the check was closed by a decision recorded on its own line. That is a different thing from an exception and a different thing from a walk, and the second clause above was written when only the first two existed.*

One caveat shaped the first pass and was then removed: the running shell was on the current renderer but its Python sidecar predated the session, so payload-dependent views rendered stale, and anything whose evidence was a payload rather than pixels was left unchecked. `desktop/harness/live-harness.html` closes that gap — it runs the built bundle against a **real** sidecar in a plain browser, so the visual checks are walkable without restarting anyone's app. The two it has already settled are marked *rendered*.

---

# Test Execution Notes

Prerequisites: a built desktop shell (`npm run build` in `desktop/`), at least two discovered workspaces so the fleet and switching checks mean something, and an agent CLI on `PATH` for §1.9 and §1.10.

The automated half runs as `.venv/bin/pytest -q` and is not repeated here — this document is only the part a person has to look at.

# Release History

<!-- One line per verified release: version, date, exceptions granted. -->
