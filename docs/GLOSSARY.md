---
type: "[[reference]]"
id: GLOSSARY
owner: user:edwin
created: 2026-05-07
updated: 2026-09-27
tags: [glossary]
---

# Glossary

Words this project uses in a particular way. Where a word has a single source in code, that source is named — the vocabulary living in one place is a rule here, not a convenience ([[ISS-0023]]).

## The pieces

- **Sidecar** — one Python process serving one repo's `docs/`. Loopback-bound for writes, `0.0.0.0` for reads. The shell runs one per workspace.
- **Shell** — the Electron app (mode 3). Hosts the sidecars and owns everything a browser cannot do: terminal, git, workspace rail, agent instrumentation.
- **Mode 1 / mode 3** — the two front doors. Mode 1 is the render server's own HTML, readable from a tablet; mode 3 is the shell. See [[ADR-0010]].
- **Workspace** — a discovered repo: any directory with a `SNAPSHOT.yaml`. Ten on this machine.
- **Project id** — a repo's stable, writable identity: `project.id` in its snapshot, defaulting to its directory name. What `[[project#NOTE-ID]]` matches ([[ADR-0024]]). **Not** `project.name`, which is a display string.
- **Fleet** — every discovered workspace, together. The fleet view reports each one's validator verdict, agent session and git state.

## The record

- **Note** — one Markdown file with project-os frontmatter. Its `type` names its template.
- **Standing document** — one of the eight per-project documents this glossary belongs to. A manifest, not a lifecycle: they have no status, and `updated:` carries the meaning ([[FEAT-0091]]).
- **Obligation** — something owed to a person: a decision to take, a requirement to approve, an issue to triage, a test to run. The registry (`obligations.py`) says what is owed, of what kind, and **which view owns it** ([[ADR-0020]]).
- **Owed / settled** — a row is owed while it needs a person. Settled covers both tested and reconciled.
- **Reconciled** — a check closed by a decision rather than by being performed: `- [~]`. It does not block, and it is counted and named rather than dropped ([[ISS-0141]]).
- **Decision record** — the `## Decision record` section on a note, holding one dated, attributed Obsidian callout per human verb ([[ADR-0020]] upstream).
- **Watermark / digest** — the moment you last said *Caught up*, and the band of what changed since ([[FEAT-0071]]).

## Verification

- **Acceptance suite** — `docs/tests/ACCEPTANCE_TESTS.md`: manual checks a person tests by hand, in three tiers. Distinct from `TST-*` notes, which are formal specifications, mostly automated.
- **Tier 1 / 2 / 3** — feature tests, regression tests, and temporary verification checks. **A release is blocked while any Tier 1 or Tier 2 check is unsettled**; Tier 3 never gates.
- **The gate** — that rule, computed. It fired green for the first time on 2026-08-11.
- **Evidence** — what a ticked criterion carries: `— evidence: … (actor, date)`. A tick without it is refused.

## Agents

- **Session** — one agent run, tracked live from Claude Code hooks: state, cost, context, the notes it touches.
- **Work note** — a note the running session has edited. Drives the `agent` chip in the navigator.
- **Delegate / worker** — an agent acting without a human in the loop. [[ADR-0022]] decides what it may publish; [[RISK-0006]] is why that is watched.
- **Dispatch** — asking an agent to do something from the cockpit, with the request recorded.

## Rules that have names here

- **Absent, never zero** — a count of nothing is not shown. A permanent `0` is a thing readers learn to skim past.
- **One item, one home** — narrowed by [[ADR-0025]] to *one obligation, one owning view*: a row may appear in a `Needs you` shortcut list **and** in its structural place.
- **The machine gathers; the human decides** — no verdict, acceptance or review outcome is ever written by an agent.
- **Loopback-only** — every write. The check *is* the authorisation model, not a layer over one ([[REQ-0027]]).
- **Publishing is a person's act** — the tool commits and never pushes on its own initiative; deploy remotes are refused everywhere ([[FEAT-0055]]).

## Elsewhere

- **Upstream** — `project-os` is the template every repo syncs `tools/` from; **`project-os-dev` holds the design record**, including every upstream ADR. Neither is obvious from a citation, which is [[ISS-0123]].
- **Downstream consumer** — any repo the cockpit renders. Nothing is installed into one.
- **release test**: Testing a release by hand, one platform at a time, from the page the generator prints (`tools/instructions/TESTING.md`, "The release test"). It was called the walk until 2026-09-27.
- **release test sheet**: The generated page a release is tested from: a table of sections, then each section's changes, setup and numbered checks, each one action and one expected line. The cockpit draws the same page at `~release-test/<platform>`.
- **section**: A group of checks that share one setup state — one build, one account tier, one piece of hardware on the bench — tested in one go. It was called a sitting.
- **what changed**: The screens a release changed on one platform, one line per change, with the screen at the last release beside the screen now. Each section starts with the ones it tests. It was called the survey.
- **result**: What a tester records for a check: pass, fail, partial, question, blocked, N/A or excused.
- **test kind**: Feature tests, regression tests and automated tests, the three kinds a test note is sorted into (ADR-0039 called them sections).
- **procedure**: A written script for one section — setup items, then numbered steps in groups, each group with a `Start:` line. One file per section under `docs/tests/acceptance/release-test/`.
- **section order**: `docs/tests/acceptance/RELEASE-TEST.md`, the one file per project that sets the order of the sections.

## Proposed words for the levels (not agreed yet)

**Nothing in this section is agreed.** It is the vocabulary proposed on 2026-09-27 for [[PHASE-045-The-Cockpit-In-Layers]], decision D11. Edwin said that the words in [[DES-0015-The-Cockpit-In-Layers]] and [[DES-0016-Levels-Of-Abstraction]] had drifted from the ones defined earlier, and that he no longer knew exactly what each meant. Once agreed, each word moves into the sections above and both designs are revised to use only these words. Until then, the rest of this glossary wins.

The principle is to keep the words the cockpit already uses and add as few new ones as possible.

| word | means | replaces, or collides with | recommendation |
| --- | --- | --- | --- |
| **level** | how close a person stands to the work: Fleet, Project, View, Note, Evidence, Trace | "layer" L0 to L4 (DES-0015), "level" A0 to A6 and "altitude" (DES-0016) | use "level" only; drop "layer" and "altitude" |
| **Fleet** level | all workspaces at once: which project needs me | "Glance" (DES-0015), "Portfolio" (DES-0016) | keep **fleet**, already defined above |
| **Project** level | one workspace's summary: what needs me, what is in flight, how far from shipping | "Home" (DES-0015), "A1 Project" (DES-0016) | the level is Project; the page keeps its name, **Overview** |
| **View** level | one kind of note, listed in the navigator and grouped by state | "flow" and "flow view" (both designs) | keep **view**, meaning one kind of note ([[ADR-0028-Work-Has-Three-Phases]]: "a view is a corpus") |
| view names | Overview, Intent, Features, Issues, Tests, Publication, Library | Home, Design, Build, Verify, Issues, and no Library (DES-0015) | keep the built names; Intent is the name Edwin agreed in TASK-0385 |
| **Note** level | one note: a summary at the top (status, bars, next verb), the body below, the frontmatter folded | "subject" (L3, A3) and "ticket" (A4); both are the same page scrolled | say **note**; do not use "subject" or "ticket" |
| **Evidence** level | what proves a note's claims: ledger results, screenshots, commits, validator and test runs | part of "L4 Record" (DES-0015), "A5 Evidence" (DES-0016) | keep "evidence"; it widens the word above, which means a ticked criterion's proof |
| **Trace** level | the agent's turns, tool calls and the raw payload a page was drawn from | part of "L4 Record", "A6 Trace" | new word; glossed here |
| **flow** | one of the activities a person does: design and review, implementation, verification, issue triage | used for navigator tabs in both designs | an activity, not a tab. A flow decides the order of rows inside a view and the rows in Needs you |
| **record** | all the notes of a project (the section "The record" above) | "L4 Record" as a level name (DES-0015) | keep the existing meaning; never a level name |
| **phase** | a `PHASE-*` note | also [[ADR-0028-Work-Has-Three-Phases]]'s three phases (design, implementation, publication) | open question: call ADR-0028's three **stages**, which needs an amendment to it, so "phase" means only a `PHASE-*` note |
| **Needs you** | the list of what is owed to a person, first in each view and in the left pane | "the minimum up front", "what needs you by verb" | keep; "owed" stays the word for a row's state |
| **release test**, **section** | as defined above (renamed 2026-09-27) | "walk", "sitting" in both designs until 2026-09-27 | the designs now say release test; the pictures of past notes keep those notes' titles |
| **Shipping** | — | DES-0015's card for commits, the gate and the release test | say **Publication**, the view's name |
