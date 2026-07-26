---
type: "[[change]]"
id: CHG-20260726-State-And-Review-Surfaces
aliases: ["CHG-20260726"]
title: "Overview rework + review desk — state-first dashboards, ~review, and the cockpit's first note writes"
status: merged
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
features: ["[[FEAT-0040-Overview-Rework]]", "[[FEAT-0041-Review-Desk]]"]
related: ["[[REQ-0022-Overview-State-Above-History]]", "[[ADR-0007-Planning-Artifact-Approval-Gate]]", "[[ADR-0006-Retire-Delivered-Band]]", "[[FEAT-0036-Live-Work-Views]]", "[[FEAT-0018-Verification-Health-Surface]]"]
design: ["[[REF-0001-Overview-Redesign-Dossier]]"]
tests: ["[[TST-0020-Overview-Payloads]]", "[[TST-0021-Review-Desk]]"]
reviewed_by: model:claude-fable-5
review_date: 2026-07-26
review_verdict: approved
---

# State & review surfaces

PHASE-008 in one change: the overview screens were rebuilt around current state instead of accumulated history, and a new `~review` desk gives the agent a place to put proposals, questions, and manual test runs where a human will actually see them.

## What changed for you

**The overview leads with state.** A focus band at the top reads the SNAPSHOT `focus:` chain — usually terminal, so it says what just finished rather than pretending something is live, with the note's age shown because a stale focus note is worth seeing. Six stat tiles replace the old hero-plus-donuts pair: same numbers at half the height, each with its status composition inline, and Requirements finally rendered (the sidecar had been computing it all along). Below that, phases are an accordion — any row expands — with live phases first and finished ones folded into a **Completed** band. Then "Waiting on you", which lists only states this corpus actually holds, and finally activity and a new **Commits** panel.

**Commits are documentation events.** Each row shows the notes a commit touched with their current statuses, completions ticked, and a "no doc items" flag on commits that left no documentation trace — FEAT-0022's guardrail, applied per commit.

**The phase page answers phase questions.** Fraction and a gates chip in the header, a one-line health band instead of a repeated dashboard, feature rows that name the item in flight and the one queued behind it, exit criteria with a progress bar and evidence chips, and a Remaining list that spells out what would finish the phase.

**The right pane became the record column.** Decisions, Verification (with validator state), and Library — always populated, unlike the live state a "meanwhile" column would have shown. On a phase it scopes down and adds in-flight/attention cards, with the raw link graph demoted to disclosures rather than deleted.

**`~review` is new.** Its queue groups Decisions / Proposals / Questions / Test runs; the mode button carries a count badge and takes the slot Active and Recent vacated. A proposal set reviews as one unit (per-item ticks, then Accept set / Request changes / Reject); questions round-trip through the dispatch queue; and manual tests run as a stepper that writes its results back into the test note.

**Design input is part of the record.** Dossiers live in `docs/references/design/`, wrapped by reference notes and linked from a feature via a `design:` field. They surface as a strip on the note render, a Library group, and first in the record column.

## Two nav modes retired

**Active** and **Recent** lost their buttons. Active was a whole mode for a state this corpus rarely holds — work is bursty, `doing` clears at close-out — and the overview now carries in-flight work ambiently while the progress rail carries it live. Recent is superseded by the commits panel. Both server modes remain (`nav?mode=active` still feeds the Now board and the strip's work tab; FEAT-0008's stability rule), a stored preference pointing at either migrates to Overview, and phase-less projects fall back to Overview rather than Active. This partially supersedes FEAT-0036's UI, recorded in that note.

## For the API

`SCHEMA_VERSION` is **4**. Additive: `stats` gains `focus` and `status_buckets`, slim issue items gain `severity`, and four endpoints join the surface — `GET /api/cockpit/commits`, `/review-queue`, `/review/<id>`, `/scope-tests`, plus `POST /api/cockpit/review-request`, `/review-resolve`, `/api/notes/review`, `/api/notes/test-run`. The bump was not strictly required by the add-vs-remove table; it was taken because the desktop renderer caches payload shapes across restarts and the bump is the cheap signal that a stale bundle is running (the ISS-0024 §6 lesson). `docs/references/COCKPIT-API.md` carries the contract.

## The cockpit now writes notes

This is the first crossing of the "cockpit is a viewer" line PHASE-007 drew, and it is deliberately narrow. Mutation endpoints **refuse non-loopback callers** — a per-request peer-address check on the shared 0.0.0.0 socket rather than a second bind (the render port exists so a tablet can *read*; the guard is what keeps writing off it), a field allow-list bounds what can be written — the three review fields, the runner's `status`/`last_run`/`last_verified`, and `updated` (declared in `note_writes.ALLOWED_FIELDS`, not smuggled), and nothing else, transitions are validated against `statuses.py`, paths canonicalise through the index, and an `mtime` precondition refuses a note that changed underneath the reviewer. SNAPSHOT.yaml is never touched: ADR-0009 keeps notes as the authored source and `sync-snapshot.py` propagates at pre-commit.

## No new statuses

Owner constraint, and worth stating because it shaped the whole design. Proposal sets queue as **runtime review requests** while their notes stay at plain `backlog`; ADRs, requirements, and tests queue on their existing intake states; acceptance stamps the existing `reviewed_by` / `review_date` / `review_verdict` fields; rejection uses `cancelled`. The desk writes `plan-accepted` on acceptance and `plan-rejected` on rejection, and refuses close-out's own vocabulary (`approved` / `changes-requested`) outright. Refusing the string turned out to be only half a guard — the mechanical close-out check accepts any verdict that isn't `changes-requested`, so the endpoint also refuses to stamp **gate-bearing note types** (`test`, `change`) at all. A plan verdict therefore cannot reach a note whose review stamp the verification gate reads. The phases group is called **Completed** rather than "Delivered" because [[ADR-0006-Retire-Delivered-Band]] retired that band; the guard test would have caught its return.

One near-miss is worth recording: the first cut of the stat tiles classified statuses into buckets inside `renderer.ts`, which would have made the renderer a ninth surface restating the vocabulary — exactly the ISS-0023 failure mode. The bucketing moved into `stats_payload`, and the parity suite now fails if it comes back.

## Still open

[[ADR-0007-Planning-Artifact-Approval-Gate]] is at `proposed` and [[TASK-0205-Approval-Gate-Decision]] stays open: whether acceptance should *gate* dispatch is a lifecycle policy change for the owner to decide. Everything above ships advisory — nothing is blocked, the desk is a lens — which is the ADR's own recommendation pending measurement. `ReviewStore.outcome_counts()` records the outcomes that measurement needs.

## Independent review (2026-07-26)

Authored by a Claude-family session (Opus); reviewed by model:claude-fable-5 — same family, so this is not the different-family review QUALITY.md requires; record a cross-vendor or human pass to settle it.

Verdict **changes-requested** — the change is largely as described, but the safety paragraph overstates:

1. **"Mutation endpoints bind loopback-only" is inaccurate twice.** Enforcement is a peer-address check on the single 0.0.0.0-bound socket (`server.py:1155-1163`), not a loopback bind; and `POST /api/cockpit/review-request` (`server.py:1235`) has **no** loopback check at all — any host on the Wi-Fi can file review/question requests, which writes `.cockpit/review-requests.json`, records dispatch-ledger entries (`server.py:1258-1259`), and fires SSE events. If that endpoint is deliberately open for remote agents, say so and bound it; if not, guard it.
2. **"Only the three review fields plus a guarded status can ever be written"** — the writer also stamps `updated` on every mutation (`note_writes.py:203,257`), and the enforcing allow-list is duplicated in the handlers rather than derived from `note_writes.ALLOWED_FIELDS`.
3. **"The desk writes `plan-accepted` and refuses `approved` — so a plan approval can never satisfy the verification gate"** — the mechanical gate (`tools/scripts/validate-docs.py:977-985`) accepts any verdict except `changes-requested`, so a `plan-accepted` stamp on a TST/CHG note *would* satisfy it. The refusal narrows the hole; it does not close it.
4. Minor: rejecting a set stamps `review_verdict: plan-accepted` alongside `status: cancelled` (`renderer.ts:3004-3006`) — the durable record of a rejection reads as an acceptance verdict.

### Re-review (2026-07-26, second pass) — approved

All four findings verified fixed in code and covered by tests (loopback guard on every mutation endpoint including `review-request`; allow-lists consumed from `note_writes` with `updated` declared; gate-bearing note types refused outright so a plan verdict cannot reach a TST/CHG stamp; `plan-rejected` added), and this note's own paragraphs were amended to match — the loopback wording now correctly describes a per-request peer-address check, and the no-new-statuses section records both new verdict values and the type refusal. Suite 304 passed / 1 skipped, validate-docs OK, both re-run by the reviewer.

One residual nit: the write-back paragraph still says "only the three review fields plus a guarded status can ever be written" — `updated` (both paths) and the runner's `last_run`/`last_verified` are also written; they are declared in `note_writes.ALLOWED_FIELDS`, so the sentence undersells the (still narrow, still tested) surface. One new defect found during re-review, outside this note's claims: ready manual tests now appear twice in Waiting-on-you (an `appendTestAttentionRows` "ready" row plus a queue "run" row) — recorded against TASK-0210, see the review report. Same-family caveat: reviewed by model:claude-fable-5 against Claude-authored work; QUALITY.md's different-family requirement still calls for a cross-vendor or human pass.

### Post-re-review fix (2026-07-26)

The duplicate-row defect re-review found is fixed. `buildWaitingOnYou` now makes a single async pass (`appendAsyncWaitingRows`) that fetches the corpus tests and the desk queue together and dedupes by id, with the queue row winning because it deep-links into the runner. Verified in the harness: 8 rows, no repeated ids, TST-0011 present once as its `run` row. TASK-0210's DoD box is honest again.

The reviewer's remaining nits are also cleared: TST-0021's test count, the surviving "loopback-only binding" phrasings, the understated field list above, TASK-0203's waiver references, and TASK-0211's over-generous run-all wording.

### Plan checks and the review dead end (2026-07-26, follow-up)

Two defects reported from first use, fixed under [[ISS-0031-Plans-And-Lone-Notes-Unreviewable]]: the desk queued plan notes that by contract are not reviewable, and no lone queued note (a proposed ADR, a draft requirement) had any way to be decided. `POST /api/notes/decide` and per-type `DECIDE_TRANSITIONS` close the second; removing `plan` from the queue's intake states closes the first.

Chasing the plan half surfaced something larger, now fixed upstream in the project-os template and mirrored here: **plans were exempt from every mechanical check.** `build_note_index` is keyed by ID, and plans deliberately carry none — so no status check has ever reached them. Measured in this repo: **all 14 typed plan notes carried the forbidden `id:`** (a 100% violation rate for a rule `STATUSES.md` has always stated), and **19 further `PLAN.md` files had no frontmatter at all**, making them invisible to the docs system and to the cockpit alike. The template was the source: `docs/__templates__/plan.md` shipped `id: PLAN-FEAT-0000` and `aliases:`, teaching every plan to break the rule.

The fix is three new validator rules — `PLAN-ID` (error), `PLAN-STATE` (dated promotion to error on 2026-10-24, per ADR-0011 clause 3, because the debt is pre-existing), and `PLAN-FOLLOWS` / `PLAN-UNTYPED` (warnings) — plus the template correction. All 14 ID violations in this repo are cleared; 9 `PLAN-FOLLOWS` and 19 `PLAN-UNTYPED` remain as advisory warnings for grooming.

### Hyphen-free status vocabulary, migrated fleet-wide (2026-07-26)

Upstream [[ADR-0012]] (project-os-dev) removes the four hyphenated status values; [[ADR-0008-Legacy-Status-Tolerance]] here decides how the cockpit renders a corpus that has not migrated yet. `in-progress` and `rolled-back` merged into the `doing` and `reverted` that already meant the same thing; `in-review` and `wont-fix` became `review` and `declined`. The vocabulary went from 43 values to 41 and contains no hyphens.

Every palette surface moved together — `statuses.py`, both validators and the bundle, `base.css`, `cockpit.css`, `cockpit.js`, the Electron renderer, the verb registry, and STATUSES.md — and TST-0019's parity suite named all seven disagreeing surfaces the moment `statuses.py` changed, which is the whole reason it exists.

Retired values do **not** disappear from the cockpit's rendering: `LEGACY_STATUS_BAND` maps each to the band it used to occupy, so an unmigrated downstream repo still shows its statuses in the right colour while they remain illegal for validation, Hide-completed and the parity suite. Rendering tolerance is not permission (ADR-0008).

**Fleet migration:** 31 status values across 21 files in 4 repos (your-sudoku 16, your-trainer 9, yourtrainer-mcp 4, obsidian-supernote-sync 2); the other six carried none. All ten repos validate clean afterwards.

The migration itself is recorded in `tools/scripts/migrate-status-vocabulary.py` rather than a second script: ADR-0012's rows were added to the existing ADR-0008 table. That script already handled the trap this migration hit — SNAPSHOT items written as inline flow mappings (`ISS-0019: { …, status: wont-fix, … }`), which a line-anchored rewrite skips, leaving snapshot and note disagreeing. Its comment records finding that the same way this run did: via the validator's ITEM-STATUS drift. Keeping one tool is the point; the rewrite machinery is the part that is easy to get subtly wrong, and two copies is how one falls behind.

