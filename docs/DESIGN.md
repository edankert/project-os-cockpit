---
type: "[[reference]]"
id: DESIGN
owner: user:edwin
created: 2026-01-26
updated: 2026-08-12
tags: [design]
---

# Design

The principles this cockpit is actually built on. The design *system* — type, colour, spacing, the pane grammar — is [[DES-0002]]; the artifacts are in `docs/designs/`. This is the shorter thing: the rules that decide arguments.

*This document previously held four bullets of generic documentation advice from the template, unchanged for 198 days. It described no decision this project has taken.*

## The sentence the tool serves

> The cockpit is how a person governs a project they did not write. It must not be able to say something false about that project without saying so — and everything it shows as owed must be theirs to discharge.

Assembled from [[ADR-0009]], [[ADR-0020]], [[DES-0003]] and [[PHASE-028]], and quoted in [[REL-0001]]. Every rule below is a clause of it.

## It must not say something false

- **Absent, never zero.** A count of nothing is not rendered. A permanent `0` is a thing readers learn to skim past, and this surface has been taught that lesson three times.
- **Unknown is not fine.** A repo nobody validated is listed separately from one that passed. *"No suite"* and *"nothing blocking"* are different sentences ([[FEAT-0086]]).
- **A number says what it counts.** The badge carries its kinds and verbs from the registry; *"N items"* is not a description ([[ISS-0133]]).
- **Stale is stated, never hidden.** The window says when it is older than the code; it reports and never reloads, because a window reloaded under someone mid-session is worse than the staleness ([[ISS-0140]]).
- **One vocabulary, one source.** Statuses live in `statuses.py`, obligations in `obligations.py`, and every consuming surface is checked against them. Eight copies is how [[ISS-0023]] happened.

## What is owed must be discharge-able

- **Obligations live with their subject** ([[ADR-0020]]). What is owed on a feature appears in the features view, not in a central queue you visit.
- **A door must lead somewhere.** A row marked `acceptance: requested` with no runner behind it teaches the reader the feature works. If a verb is offered, the thing it does exists.
- **The verb is the registry's.** `Approve`, `Triage`, `Decide`, `Write` — read, never invented by the surface, and never the same word for four different acts ([[ISS-0153]]).
- **Not every obligation is a button.** A stub is written, not confirmed: the honest surface says `Write` and opens the file.

## The machine gathers; the human decides

- **No agent writes a verdict.** Acceptance, review outcome and design approval are human-only, enforced server-side ([[REQ-0026]]).
- **A judgment may carry its reasoning**, in the note, dated and attributed ([[FEAT-0095]]).
- **Publishing is a person's act.** The tool commits; it never pushes on its own initiative, and deploy remotes are refused everywhere ([[FEAT-0055]]).

## How surfaces are built

- **The sidecar renders; the shell arranges.** Markdown is never parsed in the renderer — a second parser is a second thing to keep in step ([[ISS-0151]]).
- **Payload, not URL, across a boundary the sender cannot see.** A sidecar serves one repo, so a cross-repo link carries its parts and lets the shell resolve them ([[FEAT-0093]]).
- **Quiet first.** The overview leads with what changed and what is owed, not with everything that exists.
- **Data arrives late.** Anything computed asynchronously must re-render the surface that needs it. Three separate features shipped broken this way in one day; assume it rather than discover it.

## How this project argues

- **Measure before deciding.** *"Three ADRs, two formats"* ends an argument that *"we should standardise"* would not.
- **A blocker is a property the evidence needs, not a task belonging to someone else.** The two are easy to confuse and only one of them is ever yours to fix.
- **Read the code before building the feature.** Twice in one week a feature turned out to be a convention the machinery already supported.
