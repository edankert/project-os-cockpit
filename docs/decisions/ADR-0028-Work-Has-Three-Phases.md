---
type: "[[adr]]"
id: ADR-0028
aliases: ["ADR-0028"]
title: "Work has three phases, an obligation belongs to the phase that owns its subject, and it asks only while that subject is in flight"
status: "accepted"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16, instructing the build: 'Okay, plan this fully, I would suggest a new phase to capture it all' then 'Implement and test Phase 34 fully' — the acceptance", "Edwin 2026-08-16, from use of ../your-trainer: 'the your-trainer application has created some acceptance-tests I need to execute but these are currently not very clearly visible'", "Edwin 2026-08-16: 'it seems like the items which need my attention are still a little bit invisible in the tool, hidden by all the other stuff which is mainly handled by the LLM'", "Edwin 2026-08-16, rejecting the first proposal: 'I am not sure that if we implement that that acceptance tests and releases are then very much first class citicens of the tool yet. And I am also afraid that this could overwhelm my attention'", "Edwin 2026-08-16, naming the model: 'at the moment I see 3 clear phases, the design phase (intent) the actual implementation phase (features, issues, TSTs?) and the publication phase (TSTs/Acceptance tests, releases, etc ..)'"]
decision: "Work has three phases — design, implementation, publication. Publication is a first-class phase with its own view, and its subject is the publication ladder: commit, push, deploy, versioned release. An obligation is routed to the phase that owns its SUBJECT, decided per item rather than fixed per note type. An obligation asks only while its subject is in flight; otherwise it is a resting state that marks and does not count. `deferred` remains as the explicit override."
context: "The obligation registry has five views and no phase model. Mapping the five onto Edwin's three leaves exactly two things unplaced, and both are live defects: publication's obligations sit on `overview` because publication has no home, and `test` straddles implementation and publication. A model that predicts the known defects is describing the structure rather than decorating it."
alternatives: ["Add acceptance rows to the registry as 60 individual obligations (proposed, then withdrawn — it contradicts the registry's own re-arming rule)", "A `Releases` nav mode (rejected — empty in 9 of 12 repos)", "A manual `defer` flag on requirements (rejected as the primary mechanism — the status already exists and is used by 6 of 523 requirements fleet-wide)", "Key the in-flight rule on phase status (rejected — lossy, and inert in 3 of 12 repos)"]
consequences: ["`Obligation.view` becomes derivable per item, deliberately breaking the one-type-one-view invariant", "An unchecked acceptance row stops being a debt and becomes the resting state of a checklist", "Derived silence must be inspectable, or it is a second invisibility problem", "The nav gains a third phase mode; renaming the existing two is explicitly NOT part of this decision"]
supersedes: ""
superseded: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0022]]", "[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]", "[[FEAT-0102-Publication-Becomes-A-View]]", "[[ISS-0172-A-Manual-Test-With-Subsections-Has-No-Runnable-Steps]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
tags: [adr, obligations, publication]
---

# Work has three phases

## Context

Edwin, using the fleet on 2026-08-16: *"the items which need my attention are still a little bit invisible in the tool, hidden by all the other stuff which is mainly handled by the LLM"* — reported against `../your-trainer`, where a fresh pair of acceptance tests had been written for the feature in flight and neither was findable.

Measured there: **64 items** on the badges, and separately **60 unchecked Tier 1/2 acceptance rows** that appear in no count, on no badge, in no digest and on no fleet card. `obligations.py:139` declares `release` as owing nothing on the grounds that *"the release GATE is a test obligation … so it surfaces in Tests."* It does not. The Tests badge reads 15, from `TST-*` notes only.

**The first proposal was to add the 60 to the registry, and it was wrong.** Edwin refused it on two grounds — that it would not make releases first-class, and that it would overwhelm his attention — and the registry's own charter agrees with him. `ADR-0027` excludes staleness from the standing-document count for a stated reason: *"counting it is a badge that re-arms itself forever, which is the permanent nag this project has been bitten by twice."* Acceptance rows re-arm **in bulk, by rule** — the suite's own rule 3 says code changes must uncheck every overlapping row. They are the most self-re-arming population in the corpus, and the proposal was to admit them to a registry whose charter excludes exactly that behaviour.

### The model, and the test it passes

Edwin then named the structure: *"3 clear phases, the design phase (intent), the actual implementation phase (features, issues, TSTs?) and the publication phase (TSTs/Acceptance tests, releases, etc)"* — including the question mark on tests, which turns out to be the load-bearing part.

### A view is a corpus, and a phase is not

The first attempt at this section tried to map the registry's five views onto the three phases one-for-one, and Edwin refused it: *"I thought we agreed that TSTs, and issues were across design work and publication?"* He is right, and the correction is the most useful thing in this decision.

**A view is a corpus** — the population of notes it owns. **A phase is when a judgment on one of them is owed.** They are two axes, and they do not partition each other. Some corpora happen to sit wholly in one phase; two plainly do not:

| view | the corpus it owns | phases its work belongs to |
| --- | --- | --- |
| `intent` | ADRs, decisions, designs, standing documents | design |
| `features` | features, requirements, tasks | design → implementation (a requirement approval is the design of the thing about to be built) |
| `issues` | issues | **all three** |
| `tests` | the test corpus | **implementation and publication** |
| `publication` *(new)* | commits, remotes, releases, tags, the gate | publication |
| `overview` | — | — it holds `unpushed commit` and `undeployed commit` because publication has no home |

`issues` spans by demonstration, in this repo's own record: [[ISS-0168]] is a publication-phase bug (a push leaves its own surface stale), [[ISS-0172]] is about the test surface, [[ISS-0152]] was about how a decision is reasoned. One corpus, three phases.

**The registry has only ever had the corpus axis.** An obligation's phase is implicit in its note *type*, which works for the corpora that sit in one phase and silently fails for the ones that span. That is why `tests` had to straddle and why publication had nowhere to go — not two exceptions, but the same structural gap seen twice.

### What decides the phase, then

**The subject.** A test verifying work in flight gates the feature closing — implementation. The same test re-verifying shipped behaviour gates the release — publication. An issue at `triage` is owed because **nobody has read it yet**; its subject is the issue itself, which is why triage is owed in every phase and is the one obligation this decision does not shrink.

That is `ADR-0020` stated exactly, not amended. Its rule is *"an obligation surfaces in the view that owns its subject."* Today `Obligation.view` is a fixed string per note **type**, which is an approximation: a test verifying `FEAT-0104` has `FEAT-0104` as its subject; a test re-run for `v2.1.7` has the release. Same type, different subject, different view.

**So per-item routing is not an exception mechanism — it is the only correct one.** The fixed-per-type view was never right; it merely happened to give the right answer for the corpora that do not span, which is why it survived this long without failing loudly.

### The ladder, measured

There is no single "release". Across the twelve repos the cockpit renders:

| rung | who acts | repos | live on 2026-08-16 |
| --- | --- | --- | --- |
| commit | agent (close-out commits its own work) | **12 / 12** | — |
| push | the human, from the cockpit | 8 (backup remotes) | 7 commits: project-os 2, your-health 3, your-sudoku 1, your-trainer 1 |
| deploy | the human, elsewhere — named, refused | 2 (server remotes) | your-applications.com at **34** |
| versioned release | the human, gated on acceptance | 3 (`REL-*` notes) | your-trainer 11 + 12 tags; this repo 1 + 1 tag; your-applications.com 1 |

`edankert.com` is the fourth case — a deploy remote with no upstream, so `ahead` is `None`, which `FEAT-0100` already renders as a row rather than a zero.

A **Releases** view would be empty in 9 of 12 repos — a permanent blank button, the failure `CLAUDE.md` records twice. The **ladder** is universal: every repo commits, ten have a remote. And `history_payload` already carries `remote_kind`, `unpublished_count`, `publication_known` and a per-commit `unpublished` flag — three of the four rungs. It knows nothing about tags or `REL-*` notes; `git_state.py` mentions "tag" once, in a comment.

## Decision

**1. Work has three phases: design, implementation, publication.** Publication is first-class and gets a view. Its subject is the ladder above, not the versioned release alone — which is why the view is named for publication and not for releases.

**2. An obligation is routed to the phase that owns its subject, decided per item.** `Obligation.view` becomes derivable rather than a fixed string per type. This deliberately breaks the invariant at `obligations.py:34` (*"one type, one view — otherwise the badges count it twice or neither"*), and safely: the discriminator is the subject's own status, one item still yields one row, and `counts_by_kind` remains asserted against `owed_items` so the badge and the page cannot disagree.

**What routes is the obligation row, never the note.** A `TST-*` lives in the Tests view because that is the corpus of what this project verifies, and it stays there whichever phase currently owes it. When it gates a release, its **row** appears under Publication — [[ADR-0025]]'s existing pattern, *"a shortcut list, not a second home"*, which exists precisely so a note does not disappear from its own view at the moment a reader needs it. No note changes address under this decision, and the view set is **unchanged plus one**: nothing is renamed, merged or removed.

**3. An obligation asks only while its subject is in flight.** Otherwise it is a resting state — it marks its row and does not count. This is the rule `ADR-0027` already applies to risks (*"`open` is a risk's resting state … carrying one is not a debt"*) and to staleness, applied to the populations that have the problem.

It applies where an obligation's status can sit indefinitely while the thing it attaches to is dormant. Measured across all twelve repos:

| kind | fleet | rule applies | why |
| --- | --- | --- | --- |
| requirement | 62 | **yes** | attaches to a feature via `implements:`; sits at `draft` for years |
| test | 18 | **yes** | attaches to a feature, or to a release |
| issue | 36 | no | triage **is** deciding whether it matters; deferring before triage is deciding without reading |
| feature | 0 | n/a | `acceptance: requested` is an explicit opt-in — in flight by construction |
| unpushed commit | 7 | n/a | a commit that is ahead is ahead now |
| undeployed commit | 35 | n/a | named and refused ([[ADR-0027]] admission test 3) |
| standing document | 5 | already done | `stale` is already excluded for the re-arming reason |
| adr | 9 | no | a proposed ADR blocks whatever it decides, and nine across twelve repos never becomes a wall |

**4. The discriminator is the subject's status, not its phase.** Checked against your-trainer's own record: `PHASE-019` is `active` and holds two features already `done` — phase-keying would wake their requirements back up. `PHASE-017` and `PHASE-018` read `planned` while holding `done` features, because a phase's status is authored and is not a roll-up of its children. Nineteen features carry no phase at all, and three of twelve repos have no `PHASE-*` notes whatsoever. The mapping is many-to-one and lossy: features roll **up** into a phase; a phase does not derive **down** into a feature.

**5. Derived silence must be inspectable.** What the rule quiets is shown collapsed, with the reason, and opens in one click. Silence that cannot be opened is indistinguishable from a bug, which is the same complaint this decision answers.

**6. `deferred` stays, as the override.** The derived rule is a *default* — quiet because nothing is happening yet. `deferred` is a *decision* — quiet because a person decided. The distinction earns its keep the moment a backlog feature moves to `doing`: its requirements light up automatically, **except** one explicitly deferred, which stays quiet. The status already exists (`STATUSES.md`) and the registry already excludes it; fleet usage is **6 of 523 requirements**, which is the argument for deriving rather than declaring — buying a quiet badge by hand costs 23 separate acts of bookkeeping in your-trainer alone.

## Alternatives

- **Admit the 60 acceptance rows to the registry as obligations.** Proposed first, withdrawn. It contradicts `ADR-0027`'s re-arming rule, and takes your-trainer's card from 64 to 124 in answer to a complaint about too much noise.
- **A `Releases` nav mode.** What was asked for initially. Empty in 9 of 12 repos, and it would make commits and pushes look like they belong to something rarer than they are.
- **A manual `defer` flag on requirements.** Already exists and is unused. Kept as the override (decision 6) rather than as the mechanism.
- **Key the in-flight rule on phase status.** Rejected on the evidence in decision 4.
- **Rename the existing nav modes to match the phases.** Deliberately excluded. `MODE_ALIASES` records what a mode-id change costs — a stale client asked for `tests`, silently got the features tree, and the view looked broken for 33 hours. This decision changes where obligations *route*; nav labels are a separate call.

## Consequences

- **The badge goes down, not up.** your-trainer measured: 26 requirements → 3, 15 tests → 5, 22 triage unchanged, 1 push unchanged. **64 → 31**, distributed across three phases instead of piled into one number. Twenty-one of the twenty-six requirements belong to a phase literally named `PHASE-999-Future`; the record already said *future* and the badge asked anyway.
- **An unchecked acceptance row is no longer a debt.** It is the resting state of a checklist that unchecks itself whenever code changes, and becomes owed when a release is in preparation — one campaign, one card, in the one repo with a `draft` release. With none in preparation it asks for nothing.
- **A corpus spanning phases is the normal case, not a soft spot.** `issues` spans all three and `tests` spans two; only `intent` and `publication` sit wholly in one. An earlier draft filed issues under implementation "by convention" and Edwin refused it. Nothing about that is awkward once the two axes are separated — it is precisely why routing must be decided per item, and a design that needed every corpus to belong to one phase would have been describing the buttons rather than the work.
- **Triage is owed in every phase, and the reason is the subject.** An issue at `triage` is owed because nobody has read it yet — its subject is the issue itself, not the thing the issue is about. That is why it is the one obligation the in-flight rule does not shrink, and it follows from the model rather than being an exception carved out of it.
- **The registry's completeness burden widens.** A type or source with no routing rule must fail a test, exactly as an undeclared type does now — otherwise per-item routing becomes the place a kind goes missing quietly.
- **Nothing about write paths changes.** `REQ-0026`/`REQ-0027` continue to gate every mutating route; this decision changes what is *counted* and *where it is shown*, never what may be written.

## Accepted 2026-08-16

Edwin's instruction to build the phase is the acceptance: *"Implement and test Phase 34 fully."* Recorded here rather than left `proposed` with the work shipped around it, which is the state [[PHASE-030]]'s close was criticised for.

**What implementation changed about the decision.** Two things, both found by running against the fleet rather than against fixtures:

1. **Decision 3's resting set must be derived, not listed.** The first implementation hand-listed the terminal statuses of *features* and missed `implemented`, `retired` and `fixed` — the terminals of the other two types a subject can be. It reads `statuses.COMPLETED_STATUSES` now, so a status added upstream is resting on arrival.
2. **A `draft` release that a shipped version has overtaken is not "in preparation".** `your-trainer` carries one at 2.0.2 with 2.1.6 shipped, and gating on it would have produced exactly the permanently re-arming badge this decision's consequences forbid. Named as a stale draft, and it does not gate.

Neither changes the decision; both are the decision surviving contact with twelve real repositories.
