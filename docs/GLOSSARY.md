---
type: "[[reference]]"
id: GLOSSARY
owner: user:edwin
created: 2026-05-07
updated: 2026-08-12
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
- **Owed / settled** — a row is owed while it needs a person. Settled covers both walked and reconciled.
- **Reconciled** — a check closed by a decision rather than by being performed: `- [~]`. It does not block, and it is counted and named rather than dropped ([[ISS-0141]]).
- **Decision record** — the `## Decision record` section on a note, holding one dated, attributed Obsidian callout per human verb ([[ADR-0020]] upstream).
- **Watermark / digest** — the moment you last said *Caught up*, and the band of what changed since ([[FEAT-0071]]).

## Verification

- **Acceptance suite** — `docs/tests/ACCEPTANCE_TESTS.md`: manual checks a person walks, in three tiers. Distinct from `TST-*` notes, which are formal specifications, mostly automated.
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
