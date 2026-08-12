---
type: "[[issue]]"
id: ISS-0148
aliases: ["ISS-0148"]
title: "A note in another project cannot be referenced — 47 citations of upstream ADRs name an id with no repo, and the reader has to already know which of twelve repos holds it"
status: triage
severity: medium
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
phase: "[[PHASE-999-Future]]"
features: []
tasks: []
related: ["[[ISS-0123]]", "[[ADR-0023]]", "[[ADR-0019]]", "[[FEAT-0016]]"]
tags: [issue, traceability, fleet]
---

# A cross-repo reference has no syntax

## What raised it

Edwin, 2026-08-12, on learning where `ADR-0011` actually lives: *"Aha, do we need a way to reference notes in other projects by maybe prefixing the ID?"*

The measurement behind the question ([[ISS-0123]]): **41 files in this repo and 6 in the template cite `ADR-0011` or `ADR-0013`.** Both notes exist, in `project-os-dev`, which no citation names. A reader in this repo sees `[[ADR-0011]]`, finds nothing, and either gives up or — as this session did — prepares to write a replacement for a note that already exists.

**Every one of those 47 is a dead link in the cockpit and in Obsidian.** The wikilink resolver is per-repo by construction, because a workspace is a repo.

## Why the answer is probably yes

The fleet is twelve repos that genuinely reference each other: downstream repos cite upstream decisions, the template cites its own, and this repo's notes cite `project-os-dev` constantly without saying so. The cockpit **already has the fleet** — it discovers every `SNAPSHOT.yaml`-bearing repo and runs a sidecar per workspace ([[FEAT-0016]]) — so resolution is a lookup it is uniquely placed to do. Nothing else in the toolchain can.

## The two separable pieces

**1. A syntax** — cheap, and adoptable for new citations the day it is chosen.

| form | reads as | Obsidian, vault = one repo | Obsidian, vault = `~/Dev/repos` |
|---|---|---|---|
| `[[project-os-dev/ADR-0011]]` | a path | unresolved | **resolves natively** |
| `[[project-os-dev:ADR-0011]]` | a namespace | unresolved | unresolved |
| `[[ADR-0011@project-os-dev]]` | an address | unresolved | unresolved |

**The slash form is the recommendation**, on the strength of the last column: it is the only one that costs nothing in Obsidian if the vault is ever opened at `~/Dev/repos`, and it needs no new grammar — it is what a relative path already looks like.

**2. Resolution in the cockpit** — a feature, not a convention. A cross-repo link would open the owning workspace at that note, which is the one thing this tool can do that a text editor cannot.

## And a third thing, which is cheaper than both

Neither piece back-fills the 47 existing citations. One sentence in `CONTEXT.md` naming where the upstream ADR namespace lives fixes comprehension for every one of them, today, and is worth doing whatever is decided here.

## Not decided

Whether to sweep the 47, whether the syntax is template-owned (it is — `OBSIDIAN.md` and `TRACEABILITY.md` would carry it, so it is an upstream decision in `project-os-dev`), and whether the cockpit resolves or merely renders them legibly. Filed at `triage` because the first two are Edwin's and the third depends on them.
