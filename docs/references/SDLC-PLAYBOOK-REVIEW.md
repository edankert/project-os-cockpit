---
type: "[[reference]]"
id: SDLC-PLAYBOOK-REVIEW
aliases: ["SDLC-PLAYBOOK-REVIEW"]
title: "The AI-Native SDLC Playbook, read against this project — where project-os is ahead, where it is thin, and why six stages is three stages halved"
status: active
owner: user:edwin
created: 2026-08-23
updated: 2026-08-23
scope: "project"
source: ["https://claude.com/blog/the-ai-native-sdlc-playbook", "Session 2026-08-23: Edwin asked for a review of the article against project-os and the cockpit, then for a type/state mapping, then for a cockpit mapping, then rejected the first cockpit answer as uncreative and asked for one built from existing types, states and properties"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0038]]", "[[ADR-0009-The-Principal-Is-A-Role]]", "[[ADR-0022]]", "[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]", "[[FEAT-0102-Publication-Becomes-A-View]]", "[[INTENT]]", "[[TESTING-MODEL]]", "[[ISS-0068]]", "[[ISS-0077]]", "[[ISS-0122]]", "[[ISS-0253]]"]
---

# The AI-Native SDLC Playbook, read against this project

## Purpose

A record of a review performed on 2026-08-23 comparing Anthropic's *The AI-Native SDLC Playbook* against this repo's project-os notes and the cockpit's implemented surfaces. It exists because the article names a **six-stage lifecycle in industry-standard vocabulary** (Plan, Design, Build, Test, Deploy, Maintain) that this project has arrived at independently under different names, and the overlap is close enough that the differences are informative in both directions.

This is a reference note, not a decision. Nothing here is settled; the section *"What would have to be decided"* lists what an ADR would need to answer if any of it is pursued.

## What the article proposes

Six stages, each ending by committing a version-controlled artifact that triggers the next, with the chain of commits serving as the audit trail:

| Stage | Artifact | Named practices |
| --- | --- | --- |
| Plan | `intent.md` | brainstorm to a markdown proto-spec; product owner commits it |
| Design | `spec.md` | Claude writes the spec under org skills for brand/security/compliance/UX |
| Build | `plan.md` + code | plan mode; `CLAUDE.md`; skills; hooks as build-time guardrails; parallel sessions and subagents; self-verifying feedback loop; continuous evals in CI |
| Test | PR with test results | evals woven through implementation rather than gated at a boundary |
| Deploy | merged code + review findings | AI in the PR review loop (`REVIEW.md` defining Bugs/Security/Compliance passes); hooks as approval gates; tiered CI/CD autonomy |
| Maintain | incident record + a new `intent.md` | monitoring with response tiers in `bands.yaml` (1σ log, 2σ diagnose read-only, 3σ act); Claude Tag for work arrival |

Every stage carries a **leading** and a **lagging** metric, and every one of them is a duration or a rate: time from conversation to committed `intent.md`, elapsed time between `intent.md` and `spec.md`, share merging from the first implementation pass, first-pass CI success rate, time to first review, DORA measures.

Six governance principles: humans accountable for judgment; controls enforced as the AI acts rather than discovered in review; separation of duties (the agent that writes code cannot approve it); deterministic enforcement via hooks with skills as guidance; everything logged and auditable; repeated violations codified back into `CLAUDE.md`.

## The comparison, in one sentence

**The playbook is flow-shaped and project-os is record-shaped.** The playbook's unit is a transition — an artifact commits, a stage begins, a clock runs. project-os's unit is a state — a typed note with a status, validated against invariants. project-os can say what is true now with far more precision than the playbook attempts; it says nothing about how fast anything moved. Every gap found in this review is a consequence of that one difference.

## Where project-os is ahead

- **Intake and specification are typed.** The playbook has one filename for `intent.md` and one for `spec.md`. project-os has `ISS-*`/`REQ-*`/`FEAT-*`/`DES-*`/`ADR-*`, each with its own status vocabulary, link obligations and validator gates — plus an impact-analysis step that checks a new requirement against existing constraints, which the playbook has no equivalent of.
- **The plan is decomposed and individually statused.** `plan.md` is a document; `plan/PLAN.md` plus `TASK-*` notes carrying `parent:`, `depends:` and `blocks:` is the same content as a graph, guarded by `PLAN-FOLLOWS`, `PLAN-ID` and `PLAN-STATE`.
- **Verification is observed, not declared.** `.github/workflows/observed-coverage.yml`: *"A claim that a machine covers an acceptance check is produced by a RUN. The standing `covered_by:` field it replaces rotted silently."* The playbook's evals have no equivalent concern, and `command_targets.py` goes further by detecting when a `command:` names a target that no longer exists.
- **Separation of duties is far deeper.** The playbook states the principle. [[ADR-0009]] makes the principal a role, [[REQ-0029]] states that *delegation without distinguishability is impersonation*, [[ADR-0022]] forbids the agent pushing at all, and the delegation policy defaults to **no delegation** because a default that grants authority is authority nobody granted.
- **Multi-vendor configuration.** `CLAUDE.md` is one adapter among four; `generate-adapters.py --check` runs in CI so the Codex, Cursor and generic surfaces cannot silently drift.

## Where project-os is thin

- **No evals of the configuration.** The article's sharpest idea: 20–50 real tasks with expected outcomes, gated so any change to `CLAUDE.md`, skills or hooks must pass, with each production incident becoming a permanent case. Nothing in this repo verifies its own instruction set. `project-os-bench` exists next door and holds cases drawn from real issues, but it gates nothing.
- **No flow metrics.** `SNAPSHOT.yaml`'s `metrics.counts` is an inventory — `features_total`, `tasks_done`, `issues_open`. Every playbook metric is a rate or a duration, and none is computed anywhere.
- **No named review passes.** `reviewed_by`/`review_date`/`review_verdict`/`review_response` record *that* a review happened and its verdict. `REVIEW.md`'s Bugs/Security/Compliance split records *what was examined*, which is the difference between "reviewed" and "reviewed for what". This also bears on [[ISS-0253]]: a verdict is sticky and nothing refreshes it, and a single undifferentiated flag cannot show which part of a review went stale.
- **Nothing observes a running product.** The `bands.yaml` loop — a deterministic watcher that files work back into intake — has no analogue. Everything the cockpit watches is the record.
- **`CLAUDE.md` is not one page.** This repo's is 13.6 KB, and the growth is structural rather than careless: at least three sections state outright that they live there only because their natural home under `tools/instructions/` is template-owned and a sync would report the edit as divergence. A sync-contract problem manufacturing a context-budget problem.

## Where the playbook should not be followed here

- **Blocking gates on unautomatable judgment.** The playbook enforces through hooks that allow, ask or block. [[INTENT]] states the opposing position and gives the reason: *"a blocking gate on an unautomatable judgment gets cleared to unblock the build rather than because somebody looked."* `ACCEPT-STALE`, `DESIGN-GATE` and independent review warn on purpose.
- **Tiered production autonomy.** "dev free / staging intermediate / production gated" is reasonable for a team pipeline and weaker than [[ADR-0022]]'s flat rule in this fleet, where one repo's only remote is a live web server.

## The main finding: six is three, halved

The cockpit already has a stage model. [[ADR-0028]] (accepted 2026-08-16, implemented as [[FEAT-0101]]/[[FEAT-0102]]) establishes **three phases — design, implementation, publication** — and routes an obligation to the phase that owns its *subject*, decided per item rather than fixed per type. `Obligation.route` is a `Callable[[record], str]` in `src/project_os_cockpit/obligations.py`.

Each of those three phases is exactly two playbook stages, and in all three cases the cut is the same: **the first stage decides what should be true, the second establishes that it is.**

| ADR-0028 phase | Playbook pair | Discriminator already in the corpus |
| --- | --- | --- |
| design | Plan → Design | the single approval transition each design-phase type has |
| implementation | Build → Test | `covers:` — [[ADR-0032]]'s one direction of the verification link |
| publication | Deploy → Maintain | `subject_is_in_flight()` — travelling forward against coming back |

### The Plan/Design line is already written down

`Obligation.states` lists, per type, the statuses that make a note owed. For every design-phase type that tuple is precisely its pre-approval state:

```
"adr":         ("proposed",)          proposed = Plan, accepted = Design
"design":      ("proposed",)          proposed = Plan, accepted = Design
"requirement": ("draft", "proposed")  draft    = Plan, approved = Design
"issue":       ("triage",)            triage   = Plan, open    = past it
```

Four verbs the registry treats as four kinds of judgment — *Decide*, *Accept*, *Approve*, *Triage* — are one act: crossing from Plan into Design. The boundary has existed since the registry did; it was never named.

The derivation that follows is `stage = (phase, half)` where `phase` is `view_for(record, ob)`, already computed, and `half` is `record.status in ob.states`. It is total by construction: a completeness test asserts every type in the corpus has a registry entry, and the `NONE(...)` entries carry a `view` too, so non-owed types are classified alongside owed ones.

### Triage is the return edge

[[ADR-0028]] names `triage` as the one obligation owed in **all three** phases. Under a six-stage reading that is exactly right — triage *is* stage 1, and stage 6 feeds it. The obligation that spans every phase is the loop closing.

## Type and state, per stage

Statuses below are from `tools/instructions/STATUSES.md`, the normative source.

| Stage | Type | State in stage | Gate on leaving |
| --- | --- | --- | --- |
| 1 Plan | `ISS-*` | `triage` → `open` | triage decision, or `declined`/`deferred` |
| | `REQ-*` | created `draft` | none — approval is stage 2 |
| | `FEAT-*` | created `backlog` | none |
| | `RISK-*` | created `open` | — |
| 2 Design | `REQ-*` | `draft` → `approved` | human owner (`REQ-OWNER`); `acceptance:` written |
| | `DES-*` | `draft` → `proposed` → `accepted` | `DESIGN-GATE` (warns); `asset:` present |
| | `ADR-*` | `proposed` → `accepted` | human decision — the only human-written status |
| | `FEAT-*` | `backlog` → `planned` | — |
| 3 Build | `[[plan]]` | `draft` → `active` | `PLAN-STATE`, `PLAN-FOLLOWS`; follows the feature |
| | `TASK-*` | `backlog` → `doing` → `done` | linked tests `passing`; parent gates |
| | `FEAT-*` | `planned` → `doing` | — |
| | `REQ-*` | stays `approved` | deliberately does not advance here |
| | `TST-*` | created `ready` | — |
| | `DES-*` | `accepted` → `implemented` | terminal-but-alive; keeps parity checkable |
| 4 Test | `TST-*` manual | `ready` → `passing`/`failing` | author writes it; needs `last_verified:` |
| | `TST-*` with `command:` | `active`, **no verdict at all** | [[ADR-0038]] — CI is the verdict |
| | `TST-*` `level: acceptance` | rests at `active`; verdict is a ledger entry | adding `command:` discharges it |
| | `ISS-*` | `fixed` → `open` on regression | no separate `reopened` status |
| 5 Deploy | `TASK-*` | `done` | tests `passing` and not stale |
| | `ISS-*` | `open` → `fixed` | `fixed` is terminal; there is no second step |
| | `REQ-*` | `approved` → `implemented` | every criterion ticked-with-evidence or reconciled (`REQ-BOXES`); never gated on tests |
| | `FEAT-*` | `doing` → `review` → `done` | tasks scope-resolved, tests `passing`, `FEATURE-REQ` |
| | `CHG-*` | created `merged` | — |
| | `REL-*` | `draft` → `released` | release verification |
| | `PHASE-*` | `active` → `done` | `PHASE-BOXES`, `PHASE-CHILDREN` |
| 6 Maintain | `ISS-*` | new, at `triage` | the loop closing |
| | `CHG-*` / `REL-*` | `merged` → `reverted` / `released` → `reverted` | — |
| | `TST-*` | stale via `last_verified:`; → `retired` | staleness is computed, never a status |
| | `ADR-*` | `accepted` → `superseded` | human decision |
| | `FEAT-*` / `PHASE-*` | `done` → `superseded`, or reopened to `active` | `superseded_by:` required |

Types with no stage: `SUR-*` (a place in the product, not work), `WF-*` (documents the tooling), `[[reference]]` (standing documents, whose state is freshness). `[[check]]` is a retired type — an acceptance check is a `[[test]]` at `level: acceptance` ([[ADR-0031]]).

## Cockpit surfaces, per stage

| Stage | Surface | Notable machinery |
| --- | --- | --- |
| 1 Plan | Issues view, inbox | *Triage* obligation; inbox store/discard with an allow-list and a 25 MB cap; `agent_actions.py` verb registry |
| 2 Design | Intent view, Features view | anchored design comments, `/api/design/verdict`, `/api/design/capture`, revisions; *Approve*/*Accept*/*Decide*; `criteria.py`'s three criterion states |
| 3 Build | Features, Tasks, Active | dispatch, delegation policy, approvals, escalation, per-turn checkpoints, worker |
| 4 Test | Tests view | acceptance debt, `test-run`/`acceptance-run`, ledger seal/mark/retire, `command_targets.py`, observed-coverage CI |
| 5 Deploy | Publication view, Review desk, Overview | the publication ladder (commit 12/12 repos, push 8, deploy 2, release 3, measured 2026-08-16); unpushed/undeployed obligations; deploy-remote refusal |
| 6 Maintain | Overview, Fleet | validation rows, digest against a watermark, fleet validate/git, standing-document manifest |

**Maintain is the one stage that cannot be an obligation**, and this is a finding rather than an omission. Its subjects — validator codes, staleness, `reverted`, standing-document freshness — re-arm by the calendar, and [[ADR-0027]] excludes exactly that population for a stated reason: *"counting it is a badge that re-arms itself forever, which is the permanent nag this project has been bitten by twice."* Admitting Maintain to the registry would break the registry's charter.

The mechanism it needs is already built elsewhere. `escalation.py` holds the invariant *"everything either times out into a recorded assumption, or alarms"*: a kind with a `timeout` and a `default` lapses into a record, a kind with no policy alarms rather than passing silently. That is `bands.yaml` with the failure mode already reasoned about. Pointed at validator codes instead of queue entries it gives the response ladder directly, and *file* means creating an `ISS-*` at `triage`, which is stage 1.

The standing objection — *"issues appearing without anyone asking is a worse failure than one occasionally missed"* (Edwin, 2026-07-30) — is answered by the gate the delegation policy already uses: only an `approved` policy is consulted, and absence means nothing is filed.

## What composes without new types

- **Config evals are a `TST-*` at `level: acceptance`, `tier: 3`.** `tier: 3` is already defined as *"verification check for one build"*, which is what an eval on a configuration change is. With `area: "Agent configuration"`, `covers:` naming the instruction or skill note, and a `command:` running a bench case, it inherits the ledger, observed-not-declared coverage, and rot detection when the command's target is renamed — and it inherits [[ADR-0030]]'s exemption from being individually owed, which matters because 20–50 evals must not become 50 badge rows.
- **`REVIEW.md`'s named passes are a `[[workflow]]`.** A workflow is the canonical front door for a repo activity, and `entrypoints:` holds one dispatch action per pass. Bugs, Security and Compliance become three named, versioned, individually runnable entrypoints instead of one verdict.
- **Rework is already parsed.** `criteria.py`'s `- [~]` reconciled state means *deliberately not delivered, with the reason*. Counting reconciled criteria per requirement is the playbook's "changes made after the first `spec.md` commit", measured and attributed, by code proven identical to the validator's over the whole corpus.
- **Order of work is already stored.** `depends:` and `blocks:` on tasks encode `plan.md`'s ordering; rendering the plan topologically rather than flat matches the artifact without storing anything new.
- **Durations need no new field.** `history_payload` parses `+status:`/`-status:` pairs out of git diffs, groups them by commit, and distinguishes a note *born* at a status from one that *moved* there. Aggregating what it already returns yields intake→spec, spec→plan, plan→merged, review latency and rework counts.

## What would actually be new

Four things, none of them a type, a status or a view:

1. A derived `stage` — a function over `view_for()` and `status in ob.states`, not a stored field.
2. An `inbox` entry in `agent_actions.py` carrying an *Intake* verb, so the inbox's own success condition (empty) is reachable from the cockpit rather than only from a terminal.
3. A bands policy consumed by `escalation.py`, approved through the same gate as the delegation policy.
4. Duration aggregation over `history_payload`'s existing transition parser.

## What would have to be decided

- **Is `stage` allowed at all, given [[ISS-0068]]?** That issue forbids two lists of one obligation. A stage *facet* — ordering the obligation groups already on a page — does not create a second list. A stage *nav mode* would. The line between them is the decision.
- **Does `stage` collide with `phase:`?** A `PHASE-*` is *when* — a milestone, ordered, closable. A stage is *where in the loop* — every item passes through all six. [[ADR-0028]] already paid for this distinction once, rejecting a first attempt that mapped views onto phases one-for-one. A stage facet must not become a third thing competing for the word.
- **Whether automatic filing is acceptable under any tiering.** The 2026-07-30 objection was made before the tier ladder was available as an option; the objection may still stand.
- **Where a config eval's cases live.** In this repo beside the configuration they test, or in `project-os-bench` where they are today. Splitting them is the worst outcome.

## Corrections made in the course of the review

Recorded because a review that quietly revises itself is worth less than one that shows its working.

- The first pass stated that project-os stores no data supporting duration metrics. That is wrong: `history_payload` and `activity_payload` already reconstruct status transitions from git diffs for the history view and the contribution grid. The correct statement is that the transitions are **parsed and never aggregated**, which makes the flow-metrics gap considerably cheaper to close than first reported.
- The first cockpit mapping proposed a stage facet as a new concept. It is not new: [[ADR-0028]] is a three-stage model with per-item routing already implemented, and the six-stage vocabulary maps onto it by halving rather than by replacing it.
- An early draft referred to acceptance checks as `CHK-*` notes of type `[[check]]`. That type was retired by [[ADR-0031]]; the ids survive as aliases only.

## Maintenance

Update this note if the article changes materially, if [[ADR-0028]]'s phase model is amended, or if any of the four items under *"What would actually be new"* is built — at which point the relevant row should cite the feature that built it. If a decision is taken on any item under *"What would have to be decided"*, record it as an ADR and link it here rather than editing the question away.

Two directories hold reference notes in this repo — `docs/reference/` (which declares itself the area in its README) and `docs/references/` (which holds the substantive notes, including this one). That divergence is noted, not resolved, and is a candidate `ISS-*`.
