---
type: "[[issue]]"
id: ISS-0123
aliases: ["ISS-0123"]
title: "ADR-0011 is cited in 26 files and ADR-0013 in 22, and neither note exists in this repo or upstream — the upstream decision namespace is quoted but unresolvable"
status: triage
phase: ""
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
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
