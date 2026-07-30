---
type: "[[phase]]"
id: PHASE-013
aliases: ["PHASE-013"]
title: "Fleet surfaces — the cockpit reports on every repo it can see, not just the open one"
status: done
order: 13
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Finish the work that treats the fleet as the unit rather than the workspace: roll the design-system convention across the repos that have a UX, and surface per-repo validator health without opening each one. Both already have one leg built."
features:
  - "[[FEAT-0028-Fleet-Health-Surface]]"
  - "[[FEAT-0044-Fleet-Design-Systems]]"
requirements: []
issues:
  - "[[ISS-0055-Deferred-Findings-From-The-Design-Bench-Reviews]]"
depends: ["[[PHASE-009-Design-Surfaces]]"]
related: ["[[DES-0002-Cockpit-Design-System]]", "[[FEAT-0032-Agents-Screen]]", "[[PHASE-011-Unproven-Claims]]"]
tags: [fleet, design]
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "changes-requested"
---

# Fleet surfaces

## Goal

Two features here are half-built, and both were paused rather than abandoned.

[[FEAT-0044]] is `doing` with [[TASK-0230]] `done` and [[TASK-0231]] outstanding: the per-project stylesheet route shipped, the rollout across the fleet did not. [[FEAT-0028]] is `backlog` with no tasks — per-workspace validator badges, which the `~agents` screen already proves is possible because it aggregates per-workspace state across repos.

The reason to do them together is that they need the same thing: a reliable read of *another* repo's docs from this one. `~agents` does it for agent state, `validate-fleet.sh` does it for validation, and neither is wired into a surface.

## Scope

- **[[TASK-0231]]** — roll the design-system convention out across the fleet repos that have a UX, finishing [[FEAT-0044]]. [[DES-0002]] is the template and is `implemented`, so this is application rather than design.
- **[[FEAT-0028]]** — per-workspace validator badges across discovered repos. Needs task breakdown; there are none yet.
- **[[ISS-0055]]** — the deferred design-bench findings (at-rule descent, a dead token, others). Grouped here because they are the residue of the machinery this phase leans on, and fixing them in isolation would mean opening the design bench twice.

## Out of Scope

- **The MCP server** ([[FEAT-0029]]). Also cross-boundary, but a different boundary — exposing this cockpit outward rather than reading other repos inward. Stays in [[PHASE-999-Future]].
- **The downstream pilot** ([[FEAT-0005]] / [[PHASE-003]]). It has its own phase, untouched since PHASE-002. Whether it is still wanted is a decision, not scope to absorb here.
- **Distribution** ([[TASK-0065]] — signing, notarization, auto-update). Deliberately parked until sharing outside this machine matters.
- **Fixing other repos' corpora.** If the rollout finds a fleet repo whose docs do not conform, that is an issue filed against that repo, not work in this phase.

## Exit Criteria

- [x] Every fleet repo with a UX has a design-system note and a living style guide read from its own CSS — evidence: the seven-row table in [[TASK-0231]], with measured token counts and the five skipped repos named with reasons
- [x] The cockpit shows validator health for every discovered workspace without opening it — evidence: ten workspaces, one deliberately drifted, badge and roll-up verified live ([[TASK-0250]], [[TASK-0251]])
- [x] [[FEAT-0028]] has tasks before implementation starts — evidence: TASK-0248..0251, written and committed (`718a3ac`) before any code
- [x] [[ISS-0055]]'s findings are each fixed or explicitly declined with a reason — evidence: the note, item by item; §1 was already fixed and said so, §2–4 fixed, and the closing observation acted on in new code

## Notes

Sequenced last of the three. Nothing here is wrong today — it is unfinished, which is a weaker claim on attention than [[PHASE-011]]'s misleading surfaces or [[PHASE-012]]'s duplicated section.

Worth watching for scope creep: "the fleet" is 11 repos on one machine, and every surface that reads across them is a surface that can be wrong about ten codebases at once. [[FEAT-0028]] in particular should ship read-only and stay that way.

## Independent review — 2026-07-30, on the plan (model:claude-opus-5, fresh context, separate session) — approved

Approved as a plan. Scope, sequencing and the exclusions are defensible from the note alone: both features genuinely have one leg built, the shared prerequisite (a reliable read of another repo's docs) is the real reason to group them, and "fixing other repos' corpora" being out of scope is the boundary that keeps this from becoming unbounded. The `FEAT-0028`-needs-tasks criterion is the right gate on a feature with no breakdown, and the read-only caution in Notes is the one warning this phase needed.

No findings. One observation for whoever starts it: the fleet-wide leg of [[ISS-0069]] ("consider upstreaming", still open) and the `.gitignore` defect recorded in [[CHG-20260730-Two-Features-Closed]] are both cross-repo conventions that this phase's tooling will be reading across 11 corpora — worth knowing before the rollout, not after.


## Closed 2026-07-30

Both features done, the issue fixed, and the fleet re-validated: **12 of 12 repos OK**, unchanged from the baseline taken before any of this. Fresh clones of the six repos touched also validate clean — the check [[ISS-0070]] taught, because a machine that validates locally proves nothing about what was committed.

### What landed

- **[[FEAT-0028]]** — per-workspace validator badges and a fleet roll-up, live (SSE, no polling) for open workspaces and cold (bounded subprocess, 10-minute schedule, read-only asserted by test) for the rest. Four tasks, all verified against the real fleet.
- **[[FEAT-0044]]** — [[TASK-0231]]'s rollout finished. All seven surfaces across six projects now have a page that reads that project's own source, including the three native apps that were blocked when the note was written.
- **[[ISS-0055]]** — the four deferred design-bench findings.

### Written to other repositories, with a per-repo record

The user's go-ahead covered this; it is listed so it is auditable rather than implied.

| Repo | Change | Commit |
|---|---|---|
| your-health | DES-0001: family palette de-duplicated, stale "no single source" claim corrected, rollout recorded | `c8aafca` |
| your-sudoku | same | `b594d8f` |
| your-trainer | same | `f0af198` |
| project-os | `.gitignore`: `inbox/` → `/inbox/` | `9c8de68` |
| project-os-dev | ISS-0024/0025/0026 filed + the same `.gitignore` fix | one commit each |
| edankert.com, obsidian-supernote-sync, project-os-bench, your-applications.com, your-health, your-sudoku, yourtrainer-mcp | `.gitignore` anchoring | one commit each |

**Ten repositories, nine `.gitignore` anchorings, three design notes, three upstream issues.** (Corrected 2026-07-30 after review: this section originally said eight anchorings and nine repos. Nine repos carried the unanchored pattern and nine were fixed — `project-os` and `project-os-dev` included.)

**Nothing else in those repos was touched.** Two carry unrelated uncommitted work from 2026-07-28: `your-health` (six PLAN.md edits, a modified `SNAPSHOT.yaml` and a CHG note) and `your-trainer` (44 files). Both were left alone; each commit is a single file, and `git log -1 --stat` in either shows it.

`your-trainer` needed no `.gitignore` change because **it was already anchored** — `/inbox/` at line 41, since `2c3c8465` (2026-06-12). An earlier version of this section said it had no inbox entry at all, which was false, in the sentence offered to make the count auditable. `articles` is the repo with no entry.

### The `.gitignore` fix is fleet-wide because the defect was

[[ISS-0070]] fixed the unanchored `inbox/` here. The pattern is **template-owned**, so nine other repos carried the identical latent defect: any directory named `inbox` at any depth vanishes silently. Swept the fleet for live casualties — one hit, `your-applications.com/public/your-trainer/inbox/`, which turns out to be **deliberately** ignored by its own anchored rule three lines earlier. So this repo was the only victim, and the other nine were fixed before they could become one.

### Owed, and named rather than absorbed

- **The six downstream design notes are still `draft`.** They leave `draft` when Edwin has looked at the pages. A human gate, not outstanding work.
- **Upstream decisions are not made here.** project-os-dev ISS-0024/0025/0026 are filed with recommendations and evidence; deciding them is that repo's work.
- **[[TASK-0251]]'s roll-up has no automated test** — DOM code that cannot be imported outside a browser, covered by the live pass and marked `[~]`. The square encoding *was* extracted to a pure function after review (see below); the roll-up's builder was not, and pretending otherwise would repeat the mistake that review caught.

### [[ISS-0072]] — found here, diagnosed here, fixed here

The live pass turned up that the sidecar's `SNAPSHOT.yaml` observer never fired, so `METRICS` drift — the commonest validator error — could not clear without a restart. The cause was not in the observer: **FSEvents is case-sensitive on a case-insensitive filesystem**, so a watch registered as `/Users/edwin/…` matched no event reported as `/Users/Edwin/…`. The recursive docs watcher matches by prefix and was unaffected; only the exact-match SNAPSHOT watch broke — on **every app-spawned sidecar**, because the shell stores workspace roots as the path was typed.

Fixed by canonicalising the case of `ValidationRunner.project_root`, verified against the exact invocation that failed, and mutation-tested.

### Worth carrying forward

Three of this phase's findings came from **running the thing**, not reading it: [[ISS-0072]], [[ISS-0073]], and `your-trainer`'s zone ramp turning out not to be a designed scale. All three were invisible in the source and unavoidable the moment something rendered. Same lesson [[ISS-0069]] recorded — the surface catching what the validator could not — arriving three more times in one phase.

And a sharper version of it, from ISS-0072: **[[FEAT-0018]]'s acceptance was verified live and still missed this**, because the fault that pass induced took the working code path. A live check is only as good as the fault you induce, and inducing the convenient one is how a broken path stays green.

## Independent review — 2026-07-30, on the close-out (model:claude-opus-5, fresh context, separate session) — changes-requested

Scope reviewed: `718a3ac`, `3f03403`, `f6e8781`, and the notes for [[FEAT-0028]], [[TASK-0248]]–[[TASK-0251]], [[TASK-0231]] / [[FEAT-0044]], [[ISS-0055]], [[ISS-0072]], [[ISS-0073]] and this phase.

**What was independent, and what was not.** Fresh context, separate session, starting from the notes and the diff — never the author's reasoning trace. Same model family as the author (`model:claude-opus-5`), which per [[ADR-0013]] is not the gate and is recorded here as provenance. The session shares a scratchpad directory with the authoring session; I deliberately did not read the working files in it. Every claim below was re-derived by running or mutating the artifact rather than by reading the prose about it.

The verdict is `changes-requested` on two guarding failures. The implementation is sound; what does not hold is the claim that two of it is guarded.

### F1 — `unknown paints nothing` does not guard that (major)

[[TASK-0250]] says the encoding's central requirement is that `unknown` paints **nothing**, "guarded by `unknown paints nothing, and only failing gets a numeral` … mutation-verified by removing it".

The guard compares string indices in the built `renderer.js`. Mutation applied to `applyHealthToSquare`:

```ts
if (!row) return;
if (row.state === 'unknown') { li.classList.add('health-ok'); return; }
```

Every unchecked repo now renders `.ws-square.health-ok` — the "checked and clean" hairline ring — which is exactly the [[ISS-0065]] failure the task exists to prevent. **All 12 node cases and all 613 pytest cases stayed green.** A weaker variant (`li.classList.add(\`health-${row.state}\`)` before the return) also passed.

"Mutation-verified by removing it" is literally true and selects the one mutation a string-index guard can see: deleting the early return deletes the literal. Any mutation that keeps the literal and breaks the behaviour survives. This is the shape [[ISS-0055]]'s closing observation names, appearing in code written to act on that observation.

The property is testable without a DOM: `applyHealthToSquare`'s state→class/badge mapping is a pure function of the row and can be extracted and exercised the way `markStale` already is.

### F2 — ISS-0072's reproduction test does not exist (major)

[[ISS-0072]] ticks `[x] Reproduce in a test that drives the **observer**, not the bus — the existing coverage cannot see this`. No such test was added. The three new cases exercise `canonical_case()` and the constructor assignment; none starts an observer.

Mutation: delete the `observer.schedule(...)` call from `ValidationRunner.start()` — the reported symptom in its strongest form, a SNAPSHOT watch that does not exist at all. **The full suite passes.** The bug this issue is about remains completely unguarded end to end; what is guarded is the current *implementation choice*, so any future replacement of `canonical_case` re-opens it silently.

The test is cheap. A ~20-line probe that constructs a `ValidationRunner` on the lowercase path, stubs `schedule`, starts the observer and rewrites `SNAPSHOT.yaml` distinguishes the two states in about 4 seconds with no new dependency: fixed → fires once; reverted to `Path(...).resolve()` → fires zero times. That is the missing case, and it is the one the note claims.

### F3 — the `.gitignore` sweep arithmetic is wrong, and the your-trainer exemption is false (moderate)

The table in "Written to other repositories" is **correct**. The prose around it is not.

- "eight other repos carried the identical latent defect" — **nine** did. Verified: nine commits, each a `-inbox/` / `+/inbox/` pair (`edankert.com`, `obsidian-supernote-sync`, `project-os-bench`, `your-applications.com`, `your-health`, `your-sudoku`, `yourtrainer-mcp`, `project-os`, `project-os-dev`).
- "the eight-of-nine count reads as deliberate" — nine were fixed, so the ratio does not describe anything.
- `SNAPSHOT.yaml`'s focus note: "Wrote to 9 other repositories (3 design notes, 8 gitignore anchorings, 3 upstream issues)" — **ten** repos, **nine** anchorings.
- "`your-trainer` has no `.gitignore` inbox entry at all, so it needed none" — **false**. `your-trainer/.gitignore:41` is `/inbox/`, anchored since 2026-06-12 (`2c3c8465`). The conclusion holds; the reason given for it does not, and it is offered specifically as the thing that makes the count auditable.

### F4 — the mitigation that made the per-repo choice safe was dropped without a record (minor)

[[TASK-0249]]'s recommendation was per-repo "**with the repo's validator version surfaced in the tooltip so uniformity is visible rather than assumed**". The Decision section confirms per-repo and drops the clause; `healthSummary()` emits state, count, age and open/not-open only. The precedent that section cites — [[ISS-0026]], a bundled validator that drifted silently — is the case the tooltip was for. Either implement it or record that it was dropped and why.

### F5 — the read-only assertion proves less than it reads (minor)

Read-only holds today and I confirmed it: `fix_metrics` is the validator's only write path, it is behind `--fix-metrics`, the argv guard bites, and all twelve fleet validators are byte-identical by sha256. Two qualifications the notes state more strongly than the artifact supports:

- `test_validating_a_repo_does_not_modify_it` clones a **clean** corpus, so `fix_metrics` would rewrite nothing even if the flag were passed. Mutating `_run_validator` to append `--fix-metrics` leaves that test green; only the argv test catches it. "A fixture repo is compared byte-for-byte before and after a run" is true and is not the guard doing the work.
- The cold pass executes **each repo's own** script. Nothing asserts read-only for a repo that pins a different validator — which is precisely the case [[TASK-0249]]'s decision exists to honour.

### F6 — the per-repo audit is incomplete (minor)

The audit singles out `your-health`'s unrelated uncommitted work but omits `your-trainer`, which has **44** uncommitted files from the same date. `your-health`'s dirty set also includes a modified `SNAPSHOT.yaml` the note does not list. Nothing was touched in either (both commits are single-file, verified), but a section whose stated purpose is auditability should not name one and not the other.

### F7 / F8 / F9 — smaller, for the record

- **A failing node case hangs the runner.** A failed assertion skips the fake sidecar's `close()`, the server keeps the event loop alive, and `node --test` never exits — I hit a ten-minute wall on it. `test_desktop_node_suite.py`'s `timeout=180` turns this into a `TimeoutExpired` three minutes later rather than the intended assertion message. A `t.after()` teardown fixes it.
- **The staleness guard covers only `renderer.ts`.** `fleet-health.test.mjs` runs against `dist/ipc/fleet-health.js`; editing `fleet-health.ts` without rebuilding leaves everything green, so the one behavioural suite can test a stale artifact.
- [[TASK-0249]]'s DoD ticks "reports `unknown` with a reason"; the code reports `unavailable`. The notes treat that distinction as load-bearing ("never asked" vs "asked, got no answer"); the Done section uses the right word.

### Refutation attempts that failed — these claims hold

- **[[ISS-0072]]'s diagnosis is correct**, and was re-derived rather than accepted. A non-recursive `watchdog` observer on `/Users/edwin/…` receives **0** events for a `SNAPSHOT.yaml` write; the same watch on `/Users/Edwin/…` receives **1**. A *recursive* watch on the lowercase path receives 6, all reported with the canonical `Edwin` — which is the prefix-vs-exact-match asymmetry the note claims. The desktop's own log line (`[workspaces] module init: HOME=/Users/edwin`) corroborates "every app-spawned sidecar". `canonical_case()` behaves as documented, including degrading rather than raising.
- **Guards that do bite**, each confirmed by mutation: the identity root check, `degrade` keeping its last value, `--fix-metrics` in the argv, the [[ISS-0073]] Swift unit-interval parse, `_needs_human` against the reworked DES-0004 fixtures, and the build-staleness hash in **both** directions (no-op `touch` passes, real edit fails).
- **12/12 fleet OK**, re-run here. **Fresh clones validate clean for all ten written-to repos** — stronger than the "six" claimed.
- All four cited commits exist and each touches exactly one file. `check-family-palette.py` exits 0 with `your-sudoku` 6 agree / `your-trainer` 8 agree. The native-app token counts match the [[TASK-0231]] table exactly (`your-trainer` 1 resolved via `--zoneRecovery: #999999`, `your-sudoku` 3). `your-applications.com`'s `public/your-trainer/inbox/` is deliberately ignored by its own rule, as claimed (line 7, ~11 lines earlier rather than three).
- [[ISS-0055]]'s four items each verify individually, including §1's honest "already fixed, not by me".

### What would close this

F1 and F2 are the gate: both are guarding claims on the two things this phase advertises as mutation-verified, and this phase's own stated lesson is that string-shaped guards are the recurring defect here. F3 is a factual correction to a section written to be audited. F4–F9 are worth an [[ISS-*]] each rather than blocking.


## Review findings addressed 2026-07-30

Verdict was `changes-requested` on two guarding failures. Both were real and both were mine; the reviewer's mutations are reproduced below as regression cases.

### F1 — `unknown paints nothing` now guards that (fixed)

The reviewer's mutation — returning `classes: ['health-ok']` for `unknown`, so every unchecked repo renders as checked-and-clean — passed all 613 tests. My "mutation-verified" claim selected the one mutation a string-index guard can see.

The decision moved to `desktop/src/renderer/health-marks.ts` as a **pure function**, loaded as a second `<script>` (neither file is a module, which is what makes this work). `desktop/tests/fleet-health.test.mjs` evaluates the built file and calls it directly — no DOM, no bundle. Six cases, and the reviewer's exact mutation now fails three of them. The string-index guard it replaces was **deleted**, not kept alongside: a guard that cannot fail is worse than no guard, because it reads as coverage.

That the property was extractable at all is the reviewer's point, and it was available before: `markStale` had already been extracted for exactly this reason, in the same file, by me, in the same session.

### F2 — the observer test exists now (fixed)

`test_the_snapshot_observer_actually_fires_on_a_miscased_root` builds a runner on the miscased path, starts the real observer, writes `SNAPSHOT.yaml` at the canonical path, and counts reruns. It stubs `schedule` so it measures the **watch**, not the validator.

Mutation-verified both ways the reviewer named: deleting `observer.schedule(...)` fails it, and reverting `canonical_case` to `Path(...).resolve()` fails it. What was guarded before was the implementation choice; what is guarded now is the symptom.

### F3 — the arithmetic (fixed)

Corrected above and in `SNAPSHOT.yaml`. Nine repos, not eight; ten written to, not nine; and `your-trainer` was already anchored rather than exempt. The table was right throughout — only the prose around it was wrong, which is the more embarrassing half, since the prose is what a reader would take the count from.

### F4 — the dropped tooltip clause (implemented, not excused)

[[TASK-0249]]'s recommendation was per-repo *"with the repo's validator version surfaced so uniformity is visible rather than assumed"*, and the implementation quietly dropped it. `fleet_validate.summarise` now reports `validator: "repo" | "bundled"` and the tooltip says which — *"checked 4m ago, this repo's own validator"*.

Scoped to **cold** rows on purpose: a live row's report comes from that repo's own sidecar, which is by construction running that repo's own copy, so there is nothing to disclose. The disclosure is needed exactly where *we* chose.

### F5 — the read-only test was vacuous (fixed)

Correct: it cloned a **clean** corpus, where `fix_metrics` would rewrite nothing even if the flag were passed. The fixture now carries a real metrics mismatch, and `test_the_fixture_is_one_the_write_path_would_change` proves `--fix-metrics` rewrites *that* fixture — so the read-only assertion cannot go quietly vacuous again.

The second half of F5 stands as a **limitation, not a fix**: nothing asserts read-only for a repo that pins a *different* validator, which is precisely the case the per-repo decision exists to honour. All twelve fleet validators are byte-identical today; the day one is not, this test says nothing about it.

### F6 — the audit named one repo and not the other (fixed)

`your-trainer`'s 44 uncommitted files and `your-health`'s modified `SNAPSHOT.yaml` are both listed now. A section whose stated purpose is auditability does not get to be selective.

### F7 — a failing node case no longer hangs the runner (fixed)

Fake sidecars register in a set and close in the after-hook rather than at the end of each case body, so a failed assertion no longer leaves the event loop alive. One assertion failure turned into a three-minute `TimeoutExpired` with no message; now it fails in seconds with the message.

### F8 — the staleness hash covers every desktop source (fixed)

It hashed only `renderer.ts`, so editing `fleet-health.ts` without rebuilding left the repo's one **behavioural** suite testing a stale artifact and green. It now hashes every `.ts` under `desktop/src` — path then bytes, sorted, so a rename counts. Mutation-verified by appending a line to `fleet-health.ts` without rebuilding.

### F9 — `unknown` vs `unavailable` (fixed)

[[TASK-0249]]'s DoD said "reports `unknown` with a reason"; the code reports `unavailable`, and the distinction is load-bearing everywhere else in these notes. The DoD line now says `unavailable`.

### What this round is really about

Three of the nine findings — F1, F2, F5 — are the same defect: **a guard that could not fail, described in prose as verified.** One of them is in code written specifically to act on [[ISS-0055]]'s closing observation about exactly that.

The reviewer's method is the transferable part. Every finding came from mutating the artifact and running the suite, not from reading it — including the two claims that turned out to hold. "Mutation-verified" is only worth anything when the mutation is chosen by someone trying to defeat the guard rather than by the person who wrote it.
