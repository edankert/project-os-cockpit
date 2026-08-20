---
type: "[[task]]"
id: TASK-0517
aliases: ["TASK-0517"]
title: "Resolve the 66 Tier 3 checks in `Moved from Tier 1 / Tier 2 — Fully Automated`"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
parent: "[[FEAT-0131-The-Suite-Is-Refined]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Resolve the 66 Tier 3 checks in `Moved from Tier 1 / Tier 2 — Fully Automated`

TESTING.md's unit-test-replacement rule put them there and says *"remove after the next release"*. The removal never happened. Each is promoted, retired with its reason, or explicitly kept.

State the gate delta per repo BEFORE it lands (REQ-0050 criterion 3).

## Done 2026-08-20 — excavated, on Edwin's call

**The count depends on the basis, and my first correction of it was wrong.**

| basis | notes carrying `area: "Moved from Tier 1 / Tier 2 — Fully Automated"` |
|---|---|
| `your-trainer` **HEAD** | **66** |
| `your-trainer` **working tree**, 2026-08-20 | **60** |

So this task's **66 was right all along** — at `HEAD`, which is the basis a task written before the migration would use. The six-note difference is `TST-0592`..`TST-0597`: at `HEAD` they carry the dead area properly, and Edwin's **uncommitted** migration has already re-homed all six to `area: "iOS device pass"`.

*(An earlier version of this section declared the note's 66 wrong and attributed the gap to those six notes' truncated **bodies** containing the phrase. Both halves were wrong, and the error is the one this session had just written a correction about: **a working-tree measurement presented as HEAD.** It is recorded rather than quietly replaced, because getting it twice in one session — once while fixing it — is the useful part. [[ISS-0238]]'s 67 remains unexplained by either basis.)*

**This excavation therefore covers the 60 in the working tree.** The other six need nothing: Edwin's tree has already answered them. If that uncommitted migration is ever reworked, they come back.

### The excavation needed almost no archaeology

`docs/tests/ACCEPTANCE_TESTS.md` was deleted at the migration and survives in history; its last living revision is 1017 lines and holds `## 3.5 Moved from Tier 1 / Tier 2 — Fully Automated` with **exactly 60 rows** under it — matching the 60 in the working tree exactly, which is itself a check on the join. Two things were written into those rows at the time they were parked:

- a `### sub-heading` grouping them thematically (31 distinct), and
- for most, the sentence **"Replaces §1.14"** / **"Replaces §2.39 row 1"** — the original section, in the row's own text.

So the real area was recoverable from the document rather than from `git log -L` over a file rewritten several times. All 60 matched a bay row by title:

| source of the recovered area | notes |
|---|---|
| a `§N.M` reference resolving to a real section heading | **47** |
| the `###` sub-heading it was parked under | **13** |
| unresolved | **0** |

**One trap, and it would have written the dead heading straight back.** `TST-0589` cites `§3.5` *and* `§1.19` — and §3.5 **is** the parking bay. Taking the first reference restores exactly what this task removes. The resolver skips any `§3.x` and takes the first real section.

### What it did to the corpus

- Suite **unchanged**: 581 items, 59 blocking, before and after — **re-measured with an INDEXED loader** after independent review caught [[ISS-0213]]'s simulation using an index-less one, where the numbers could not move and did not, and were reported as proof that nothing moved. Here the instrument can detect a change and reports none: `newly blocking: none`, `no longer blocking: none`. `area:` is not part of settledness.

  *(The earlier figures in this section read 579/57 — the index-less loader's. They were right about the conclusion and wrong about the corpus, which is exactly the pairing that made the ISS-0213 claim survive review-by-author.)*
- **20 of the recovered areas merge with surfaces that already exist** — `Ghost Riders` (15), `Monetization & Licensing` (27), `HR-Zone Structured Workouts` (32), `Per-Rider Data Export` (14) and more. That overlap is the strongest evidence the excavation is right: the recovered names are the corpus's own vocabulary, not invented ones.
- The automated section went from **15 distinct area names to 45**, drawn as **17 nav rows → 47** and **15 page blocks → 61**. All three are right and they count different things: a *name* is distinct, a *nav row* is one surface, and a *page block* is a contiguous run — so 61 blocks over 45 names means some areas are interleaved rather than sorted together. One bucket naming a document nobody can open became 45 surfaces naming places in the app.

**Distinct areas across the whole suite rose from 78 to 94, deliberately** — 17 recovered names added and the dead one removed. 17 of the recovered names are new — several from the sub-heading fallback (`Unit conversion`, `Sprint 2 VM-driven tests`, `Rider-rating math`) and those are groupings of *tests*, not surfaces of the *app*. Recovering the truth and consolidating it are different acts: this task restores what the document said, and [[TASK-0515]] is where 93 areas become 12–15 surfaces. Doing the second inside the first would have meant inventing a taxonomy while pretending to recover one.

Left **uncommitted** in `your-trainer`, which already carries 655 modified files.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: changes-requested.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

**The gate claim is sound and the instrument lesson was genuinely applied.** Verified with an indexed loader on a single-variable copy — same working tree, only the `area:` lines reverted: 581 items / 59 blocking before and after, `newly blocking: none`, `no longer blocking: none`, tier distribution identical. And the instrument here demonstrably *can* see the field: the blocking area breakdown moved (`Moved from Tier 1 / Tier 2 — Fully Automated` 6 → `iOS device pass` 6). That is the difference from `ISS-0213` and it is real.

**The count correction is itself wrong, in the direction that matters.** The note says 60 notes carry the `area:` field and that the extra six — `TST-0592`..`TST-0597` — carry the phrase only in their *bodies*: *"A `grep -rl` counts them; a `grep '^area:'` does not."* Measured at `your-trainer` HEAD:

- `git grep -l '^area: "Moved from Tier 1 / Tier 2 — Fully Automated"' HEAD` → **66 files**
- `git grep -l 'Moved from Tier 1 / Tier 2 — Fully Automated' HEAD` → the same **66 files**; there is no body-only set
- each of `TST-0592`..`TST-0597` carries the `area:` **field** and has **zero** body mentions — the exact reverse of the claim

So the original 66 in this task's own title, and `ISS-0238`'s 67, were not the error this section says they were. **And all 66 were rewritten** — the working tree now has zero parking-bay notes — so the excavation table (47 + 13 = 60, `unresolved: 0`) does not account for six of the notes it changed. Those six were all given `area: "iOS device pass"`, by a resolver whose stated inputs (a `§N.M` reference, or the `###` sub-heading) are precisely what the note says their truncated bodies do not contain. `unresolved: 0` is asserted over the wrong denominator.

**Three other figures do not reproduce:**

| claim | measured |
|---|---|
| automated section `15 area rows to 47` | 15 → **61 blocks / 45 distinct names** |
| distinct areas `~76 to 93` | **77 → 94** |
| `17 of the recovered names are new` | 38 distinct recovered = 20 pre-existing + **18** new |

The `20 … merge with surfaces that already exist` claim is **exact**, and it is the strongest evidence in the section — worth keeping as stated.

## Re-review corrections, 2026-08-20

The independent re-review put four numbers here in question. Three were wrong and are fixed above; one of its own claims does not hold.

**Fixed.** `15 → 47` was two different units glued together (names on one side, nav rows on the other) and is now stated as three separate figures. `~76 → 93` was an unmeasured guess and is **78 → 94**, measured on a single-variable copy with only `area:` differing. `17 new` is right; `78 + 17 − 1 = 94` reconciles, the `−1` being the dead heading itself.

**Not fixed, because it does not hold: the claim that the resolver rewrote all 66 and gave six of them `iOS device pass`.** It rewrote **60** — the working-tree population — and `TST-0592`..`TST-0597` are not among them. The evidence is in the diff rather than in the argument: my writer stamps `updated: "2026-08-20"` on every note it touches, and those six carry **`updated: 2026-08-19`**, unquoted, from Edwin's own uncommitted migration. The `66` the reviewer counted is `git diff` against `HEAD`, which sums my 60 and his 6 into one number — the same conflation of bases this note is otherwise about, arriving from the third direction in one day.

**And its other correction is right and already applied**: those six carry the dead heading in their `area:` **field** at `HEAD` with **zero** body mentions, which is the reverse of what an earlier version of this section claimed.
