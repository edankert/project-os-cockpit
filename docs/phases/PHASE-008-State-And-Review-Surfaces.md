---
type: "[[phase]]"
id: PHASE-008
aliases: ["PHASE-008"]
title: "State & review surfaces"
status: done
order: 8
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
goal: "The cockpit's overview surfaces carry maximum project state above the fold (state before history), and the agent's asks — proposals, decisions, questions, manual test runs — get a first-class human surface (~review) instead of living in terminal scrollback."
features:
  - "[[FEAT-0040-Overview-Rework]]"
  - "[[FEAT-0041-Review-Desk]]"
requirements:
  - "[[REQ-0022-Overview-State-Above-History]]"
depends: ["[[PHASE-007-Agent-Instrumentation]]"]
related: ["[[ADR-0007-Planning-Artifact-Approval-Gate]]", "[[ADR-0006-Retire-Delivered-Band]]", "[[FEAT-0017-Overview-Dashboard]]", "[[FEAT-0023-Overview-Scopes]]"]
design: ["[[REF-0001-Overview-Redesign-Dossier]]"]
---

# Phase 8: State & review surfaces

## Goal

PHASE-007 made the cockpit agent-aware: hooks feed state in, dispatch sends work out. This phase makes the two human-facing halves of that loop first-class. The overview surfaces (FEAT-0017/FEAT-0023) are rebuilt around a single organizing rule — state above the fold, history below it — per the approved design dossier (https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be). And a new ~review virtual page gives the agent's asks (proposal sets, decisions, questions, manual test runs) a place where a human can act on them, with the overview only announcing the queue.

## Scope

- FEAT-0040 — Overview rework: sidecar payload additions (focus block, issue severity, commits endpoint), state-first project overview (focus band, mix-bar stat tiles, phase accordion + Completed band, Waiting-on-you, full-width activity + commits), phase-detail rework (health band, next-action feature rows, exit-criteria evidence, Remaining list), record column right pane, retirement of the Active/Recent nav-mode buttons, and the design-input reference convention + surfaces (TASK-0212 — in-repo dossiers wrapped by reference notes, `design:` links, attachment strip, Library Design group).
- FEAT-0041 — Review desk: governance ADR (approval-gate policy), ~review virtual page with grouped queue and Review mode badge, proposal-set review with review-field write-back, question/revise dispatch round-trip, manual test runner with note write-back, typed announce rows on the overview, and the durable per-scope verification panel (TASK-0211 — acceptance tests with run affordances on feature/phase/release renders, extending FEAT-0018).
- Queue-vs-record rule (Edwin, 2026-07-26): ~review stays the pure transient queue; the durable records live on the scope pages (verification) and in the library (design input) — acting on a queue row writes into a durable home.

## Out of Scope

- Any new status vocabulary, anywhere (owner decision 2026-07-26) — the Completed band is a pure UI grouping over `done` phases (ADR-0006's `test_delivered_band_is_retired` guard stays green), and review pending-ness is dispatch-ledger runtime state, not note state, so STATUSES.md / TAXONOMY.md stay untouched here and upstream.
- Server-side removal of `nav?mode=active` / `mode=recent` — the FEAT-0008 API stability rule keeps both endpoints serving; only the mode buttons retire.
- Enforcement of the approval gate (dispatch refusing unaccepted sets) — ADR-0007 recommends starting advisory; gating is a separate future decision after measurement, and its predicate would be an accepting `review_verdict`, not a status.

## Exit Criteria

- [x] In a 900 px window, every ~overview section above the fold states current status; the activity sparkbar and commits panel are the only sections that scroll (REQ-0022). — evidence: measured stage offsets in `desktop/harness/overview-harness.html` against the built bundle — focus band 20–67 px, stat tiles 85–173, phases 191–556, Waiting-on-you 574–721; the four state sections close at 721 px inside a 900 px stage, with Activity at 739 and Commits at 867.
- [x] The Requirements stat tile renders — `hero.requirements` is no longer computed-but-unrendered. — evidence: `buildStatTiles()` in `renderer.ts`; visible as "REQS 21/22" in the harness captures.
- [x] The phase drill-down answers "how far, what gates it, what's left, what's next" without opening a note: header fraction + gates chip, health band, per-feature fractions with a next-action line, and a Remaining list. — evidence: `buildScopedHeader` (fraction + `scoped-gates`), `buildScopedHealthBand`, `buildFeatureNextLine`, `buildRemainingList`; all four verified rendering together on PHASE-007 in the harness.
- [x] ~review lists decisions, proposal sets, questions, and runnable manual tests from live index/ledger data; accepting a proposal set stamps the independent-review fields into its members through the guarded review write-back endpoint and clears the ledger request, and rejecting flips the set to `cancelled`. — evidence: [[TST-0021-Review-Desk]] (37 tests); confirmed against the live corpus, and ADR-0007 itself was accepted through the desk — its diff is exactly what `stamp_decision` writes.
- [x] TST-0011 has been executed at least once through the manual test runner, with the run log recorded under its `## Runs` section. — evidence: run of 2026-07-27 by `user:edwin`, recorded by the runner (TASK-0208) in TST-0011's `## Runs` section: 12 steps **pass**, 1 **skip**. The runner stamped `status: passing`, `last_run` and `last_verified` through the guarded write-back, and the snapshot was synced from the note per ADR-0009. The skipped step is Codex notify (TASK-0116) — recorded as skipped rather than folded into the total, so TASK-0116's injection path is verified by TST-0010's synthetic payloads but has still never been exercised end to end by a human. Carried forward in the Notes below rather than left implicit in a checkbox.
- [x] ADR-0007 is decided (accepted or superseded), and the mode strip carries Review in the slot Active/Recent vacated while `nav?mode=active|recent` still serve (FEAT-0008 rule). — evidence: ADR-0007 `accepted` 2026-07-26 (advisory-first), stamped through the desk; `data-mode="review"` in index.html; `test_retired_ui_modes_still_serve` asserts both server modes still answer.

## Notes

**Carried out of this phase (2026-07-27):** TST-0011 step 6, Codex notify (TASK-0116), was skipped in the acceptance run. Every other step passed. The Codex hook-injection path therefore rests on TST-0010's synthetic-payload coverage alone, with no end-to-end human observation. That is not a blocker for this phase — the phase's subject is the state and review surfaces, and they were exercised — but it is an unverified path in FEAT-0019 and should be picked up when Codex is next used in earnest.


- Sequencing: FEAT-0040's TASK-0199 (sidecar payload additions) first — it is the data pipe the overview stage, phase detail, and record column consume. FEAT-0041 is independently shippable except TASK-0210 (announce rows), which needs FEAT-0040's Waiting-on-you list; ADR-0007 (TASK-0205) should be decided before TASK-0207 hard-wires an accept flow.
- Design source: the dossier artifact above (plates C/D/E, the states audit, and the data-source table) is the canonical design record for both features; both FEAT notes link it.
- The dossier's states audit is a design constraint, not decoration: Waiting-on-you and the review queue may only surface states the corpus actually writes (open issues, in-review stalls, ready-never-executed tests, parked items, open risks, done-but-unclosed phases) — never assumed live states.

## Close-out (2026-07-26)

Both features are `done`: [[FEAT-0040-Overview-Rework]] (TASK-0199..0204, 0212) and [[FEAT-0041-Review-Desk]] (TASK-0205..0211). [[REQ-0022-Overview-State-Above-History]] is `implemented` with all four acceptance criteria ticked against evidence. Two test notes cover the work — [[TST-0020-Overview-Payloads]] and [[TST-0021-Review-Desk]] — and the suite stands at 314 passing. `validate-docs` is clean.

**The phase stays `active` on one criterion.** TST-0011 has still never been executed. That is the phase's own acceptance demo and it needs a human: its steps require launching an agent in the embedded console, provoking a permission prompt, and watching rail dots, strip meters and nav chips. An agent recording those observations would be manufacturing the evidence, which is the failure mode the criterion was written to catch. The runner is built and TST-0011 parses into 13 steps, so the remaining work is one sitting at the desk.

**What the phase actually delivered**, beyond its scope list:

* The overview leads with state because the states audit found this corpus is *bursty* — `doing` clears within a session, so the screen is mostly read in the quiet between them. Designing for the quiet state rather than the demo state was the decision that shaped everything else.
* The desk introduces no status anywhere. Queue membership is runtime state in the dispatch ledger; the durable outcome is the existing independent-review fields. That constraint (owner decision, 2026-07-26) turned out to make the feature *simpler*, not harder.
* Plans stopped being invisible. Chasing an unreviewable plan surfaced that plans were exempt from every mechanical check — all 14 typed plans here carried an `id:` the contract forbids, because the template taught them to. Four new validator rules and a template fix, upstreamed.
* The status vocabulary lost its hyphens (upstream ADR-0012), migrating 31 values across the fleet with all ten repos validating clean.

**What it cost in defects.** Independent review found nine across two passes — an unguarded endpoint, a decorative allow-list, rejections recorded as acceptances, a verification card that could never render, and more. Using the feature found four more, including two where the surface asked for a decision while showing nothing to decide on. Every one is fixed with a test. The pattern worth carrying forward: the desk was built as a queue, then as a set of actions, without asking what a reviewer needs *in front of them* — and no amount of test coverage catches that class of gap, only use does.

**Still owed:** the QUALITY.md different-family review. Everything here was reviewed by a Claude-family model against Claude-authored work, which is harm reduction rather than independence.

