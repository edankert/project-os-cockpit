---
type: "[[issue]]"
id: ISS-0123
aliases: ["ISS-0123"]
title: "ADR-0011 is cited in 26 files and ADR-0013 in 22, and neither note exists in this repo or upstream — the upstream decision namespace is quoted but unresolvable"
status: "fixed"
phase: ""
owner: user:edwin
created: 2026-08-10
updated: "2026-08-13"
source: ["Session 2026-08-10: allocating an ID for [[ADR-0020-Obligations-Live-With-Their-Subject]] surfaced the collision"]
severity: medium
component: "docs-namespace"
parent: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
tests: []
---

# The upstream ADR namespace is cited but absent

## Problem

This repo's notes and its template-owned instructions cite ADR IDs that resolve to nothing:

| ID | cited in | exists locally | exists upstream |
|---|---|---|---|
| ADR-0011 | **26 files** | no | no |
| ADR-0013 | **22 files** | no | no |
| ADR-0012 | 4 files | no | no |
| ADR-0014 | 2 files | no | no |
| ADR-0015 | 1 file | no | no |
| ADR-0018 | 1 file | no | no |

Local ADRs run `ADR-0001`..`ADR-0010`. `../project-os/docs/decisions/` contains only `README.md`. So every one of these citations names a decision the reader cannot open.

They are not decorative. `ADR-0011` is the independent-review deadline quoted in **every** validator `[REVIEW]` warning ("becomes an error on 2026-10-23 (ADR-0011)") — a date that gates the build. `ADR-0013` is the review-independence rule that `CLAUDE.md` and `tools/instructions/QUALITY.md` both lean on, and it is the reason a same-model reviewer is allowed. `ADR-0018` is cited as the authority for a snapshot field migration that has already happened.

## Repro

```
for n in 0011 0012 0013 0014 0015 0018; do
  echo "ADR-$n: $(grep -rlo "ADR-$n" docs tools --include='*.md' | wc -l) files, note: $(grep -rl "^id: ADR-$n" docs --include='*.md' | head -1 || echo NONE)"
done
```

## Expected

A cited decision ID resolves to a note, or the citation says where it lives.

## Actual

Six IDs cite nothing. The validator does not check ADR citations, so nothing has ever reported it.

## Consequences already visible

**The local ADR counter cannot be trusted for allocation.** `counters.ADR` stood at 10, making `ADR-0011` the next local ID — which would have made twenty-six existing references ambiguous between a local note and an upstream decision. [[ADR-0020]] was allocated at 0020 to clear the whole cited range, and 0011–0019 are now deliberately unusable locally. That is a workaround, not a fix.

## Next Actions

- [ ] Determine where these decisions actually live — an earlier upstream layout, a deleted directory, or never written
- [ ] **If they exist somewhere:** import or reference them so citations resolve; decide whether upstream ADRs share this repo's ID space or need a prefix
- [ ] **If they were never written:** the rules they authorise are still in force and being followed (the review deadline, the independence rule) — so they need writing, or the instructions need to stop citing an authority that does not exist
- [ ] Consider a validator check for unresolvable `ADR-####` citations, in the style of the existing wikilink checks — this went unreported across 26 files

## Measured upstream — 2026-08-11

`~/Dev/repos/project-os/docs/decisions/` contains **one file, `README.md`**, and upstream's `counters.ADR` reads **0**. The template has never written an ADR at all, so `ADR-0011` is not merely missing from this repo — **the namespace it belongs to is empty everywhere.**

It is cited in **41 files here and 6 upstream**, and the upstream six are all *code*, citing it by clause:

- `validate-docs.py`: *"ADR-0011 clause 2: a warning is legal ONLY as a dated migration state"*
- `grandfather.py`: *"ADR-0011 clause 3 says a check is promoted to error only once the fleet carries…"*
- `note_writes.py`: *"(ADR-0011 checks tests and changes for an independent-review stamp)"*

**So the rule is reconstructible only from the implementations that cite it**, and one of its clauses gates every repo's CI on 2026-10-23.

### And it now has a second obligation attached

[[ADR-0023]] retires the change-note review this decision's clause is what enforces. Because `tools/scripts/` is template-owned, the validator keeps warning — and will error — until the change lands upstream. **Two things are owed there, not one:** write `ADR-0011` (or retire the citation), and carry `ADR-0023` into `QUALITY.md` and the `[REVIEW]` gate. Neither is this repo's to do downstream.


## Corrected — 2026-08-12: they exist, in a third repo

**The notes are not missing. `ADR-0011` and `ADR-0013` are in `~/Dev/repos/project-os-dev/docs/decisions/`, along with sixteen others** — `ADR-0001` through `ADR-0018`, `counters.ADR: 18`. Found by looking there before writing a replacement, which is the only reason a duplicate was not created.

The topology nobody had written down:

| repo | what it holds | ADRs |
|---|---|---|
| `project-os-dev` | the design record for the system — *"features, requirements, decisions and tasks for evolving the documentation system"* | **all 18** |
| `project-os` | the distributable template every repo syncs `tools/` from | none (`counters.ADR: 0`) |
| this repo and nine others | downstream projects | their own, locally numbered |

**So this issue's subject changes rather than closes.** The defect was never *"the decision was not written"* — `ADR-0011` is a careful note with a measured context table, four rejected alternatives and six consequences. The defect is that **41 files here and 6 in the template cite an id with no indication of which repo holds it**, while the two repos a reader would look in — this one and the template — contain neither. Every citation is a dead reference for anyone who does not already know `project-os-dev` exists.

That is a smaller defect and a more annoying one, and it cost this session an hour of preparing to write a note that already existed.

### What it should be

A citation to an upstream decision should say so. **It can, as of 2026-08-12**: [[ADR-0024]] settled the notation and [[FEAT-0093]] built it, so this is now a link rather than a sentence about one — [[project-os-dev#ADR-0011]], and its sibling [[project-os-dev#ADR-0013]]. Clicking either switches workspace and opens the note.

The other half still stands: a line in `CONTEXT.md` naming where the upstream namespace lives costs one sentence and covers all 47 existing citations without rewriting any of them. The first is 47 edits across two repos; the second is one sentence and covers every future citation, which makes it the obvious first move.

### And ADR-0011 had already asked the question this repo answered

Its consequences include: *"REVIEW is the hardest case … it is either wired into close-out so it does run, or its scope narrows."* [[ADR-0023]] answered that here on 2026-08-11 without knowing the question had been asked upstream a year earlier; [[ADR-0019]] in `project-os-dev` now answers it there, and the template's `QUALITY.md` and `REVIEW_SETTLED_STATUSES` carry it. **The downstream decision was right and was made blind** — which is exactly what an unreachable citation costs.

## Closed — 2026-08-13: the premise is no longer true, and the remainder has a home

**Both notes exist.** `ADR-0011-No-Permanent-Warning-Tier` and `ADR-0013-Independence-Is-Clean-Context` are in `~/Dev/repos/project-os-dev/docs/decisions/`, with fifteen siblings. [[ADR-0023]] recorded that correction on 2026-08-12 in passing — *"Corrected 2026-08-12: it exists"* — and this note was never updated, which is its own small instance of the problem it describes.

What survives is **reachability**, not absence: 45 files here cite decisions that live in another repo, and nothing in this tool can resolve them. That is [[ISS-0148]]'s subject exactly — *"a note in another project cannot be referenced"* — and it carries the same 47-citation measurement.

Closed rather than left open beside it: two notes on one problem is how the second one goes unread, and ISS-0148 is the one whose title names the thing that needs building.
