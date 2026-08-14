---
type: "[[issue]]"
id: ISS-0148
aliases: ["ISS-0148"]
title: "A note in another project cannot be referenced — 47 citations of upstream ADRs name an id with no repo, and the reader has to already know which of twelve repos holds it"
status: "fixed"
severity: medium
owner: user:edwin
created: 2026-08-12
updated: "2026-08-13"
phase: "[[PHASE-030-Obligations-Go-Home]]"
features: []
tasks: []
related: ["[[ISS-0123]]", "[[ADR-0023]]", "[[project-os-dev#ADR-0019]]", "[[FEAT-0016]]"]
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

## Decision record

> [!note] Accept — 2026-08-13 (user:edwin)
> I think this one has been resolved and that we used the # notation? If resolved already please close and update the note with the resolution.

## Resolved — verified 2026-08-13

Edwin was right, and the answer is **`#`, not `/`**. [[ADR-0024]] decided `[[project#ID]]`, and [[FEAT-0093]] / [[TASK-0392]] built it: `wikilinks.split_cross_repo` parses the target, the renderer follows it, and the shell opens the owning workspace at that note — the thing this issue said only the cockpit could do, because only it has the fleet.

Verified rather than assumed:

```
'project-os-dev#ADR-0011'  ->  ('project-os-dev', 'ADR-0011')
'project-os#REQ-0001'      ->  ('project-os', 'REQ-0001')
'ADR-0011'                 ->  None          (a bare ID stays local)
```

Eight notes in this corpus already carry the form, including citations of `project-os-dev#ADR-0011`, `#ADR-0013`, `#ADR-0022` and `#ADR-0023`.

**Why the slash lost.** This note recommended `[[project-os-dev/ADR-0011]]` on the strength of one column: it resolves natively if an Obsidian vault is ever opened at `~/Dev/repos`. ADR-0024 chose `#` anyway, and the reason holds up — a slash reads as a path into *this* vault, so a wrong link fails silently as a missing file, where `#` is unambiguous about crossing a boundary and can be told apart from a typo. The recommendation here was made on a hypothetical vault layout nobody uses.

**What is still open, and it is this note's third suggestion.** The syntax back-fills nothing: `CONTEXT.md` still does not name where the upstream ADR namespace lives, and the bare `[[ADR-0011]]` citations across this repo remain unresolvable. That was called *"cheaper than both"* and is the only part left undone — filed separately rather than keeping this note open, because the thing it asked for exists and works.

**Re-homed out of [[PHASE-999]] on closing.** [[FEAT-0093]] delivered this and lives in [[PHASE-030]], so that is the phase that answered it. Leaving a fixed issue in the parking lot renders shipped work as unplanned on the phase strip — `test_no_terminal_note_sits_in_the_parking_lot` catches exactly that, and caught this.
