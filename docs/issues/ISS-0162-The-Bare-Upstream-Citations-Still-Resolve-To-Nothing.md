---
type: "[[issue]]"
id: ISS-0162
aliases: ["ISS-0162"]
title: "48 bare `[[ADR-0011]]`-style citations resolved to nothing, and no standing document says where that namespace lives"
status: "fixed"
owner: user:edwin
created: 2026-08-13
updated: "2026-08-14"
source: ["The one part of [[ISS-0148]] its own text called 'cheaper than both' and which the syntax did not deliver"]
severity: low
component: docs-namespace
parent: ""
related: ["[[ISS-0148-A-Cross-Repo-Reference-Has-No-Syntax]]", "[[ADR-0024]]", "[[FEAT-0093]]"]
tests: []
---

# The bare upstream citations still resolve to nothing

## Problem

[[ADR-0024]] gave the fleet `[[project#ID]]` and [[FEAT-0093]] made the cockpit follow it. Neither back-fills what was already written: **48 citations across 37 files name `ADR-0011` or `ADR-0013` as bare IDs**, and both notes live in `project-os-dev`. Every one is a dead link in the cockpit and in Obsidian.

[[ISS-0123]] was closed because those notes exist; [[ISS-0148]] was closed because the syntax exists. What neither closed is the reader arriving at `[[ADR-0011]]` and finding nothing — which is how this repo once came within an afternoon of *writing a replacement for a decision that already existed*.

## The cheap half, which is the point

`ISS-0148` named it and nobody did it: **one sentence in a standing document** saying where the upstream ADR namespace lives fixes comprehension for all 48 today, whatever else is decided. `CONTEXT.md` currently mentions `project-os-dev` zero times.

## The expensive half, which may not be worth it

Sweeping 37 files to `[[project-os-dev#ADR-0011]]`. Mechanical, and it touches notes whose `updated:` would then lie about why they changed. Worth deciding deliberately rather than doing because it is possible.

## Expected

A reader who meets a bare upstream citation can find out, from the record, where it points.

## Correction — 2026-08-14

Filed yesterday reading *"45 files"*, which was neither figure: it is **48 citations across 37 files**. Counted `grep -ro` for occurrences and `grep -rl` for files; the original conflated the two and matched neither. Corrected in place rather than left, because an issue about citations that cannot be resolved should not itself carry a number that cannot be reproduced.

## Fixed — 2026-08-14: both halves, and the scope was twice what this note said

Edwin chose the full sweep. Doing it required measuring first, and the measurement moved twice:

| | filed 2026-08-13 | corrected 2026-08-14 | swept |
|---|---|---|---|
| upstream ids cited | 2 | **6** — ADR-0011/0012/0013/0014/0019 | 5 |
| occurrences | "45 files" | **77**, of which 61 bare | **54 rewritten** |
| files | 45 | 38 | 38 |

`ADR-0012`, `ADR-0014` and `ADR-0019` were never in this note. They were found by enumerating every `[[ADR-nnnn]]` in the corpus and subtracting the ids that have a note in `docs/decisions/` — which is also the rule the guard now enforces, so the next upstream id cannot be missed by whoever writes the list.

**44 in prose bodies, 10 in frontmatter.** Both are consumers `wikilinks.py` names, and [[CHG-20260812]] verified the form renders in each.

### Four occurrences were deliberately left bare, and that mattered

[[ADR-0024]], [[ISS-0148]], [[FEAT-0093]] and [[CHG-20260812]] all **quote** the bare form to explain what it means or why the slash lost. `FEAT-0093`'s acceptance criterion is literally *"`[[ADR-0011]]` with no prefix keeps its current meaning exactly"* — rewriting that would have made the criterion assert the opposite of what it verifies. The sweep skips inline code and fenced blocks for this reason, and the guard carries the same exemption rather than an allowlist of filenames.

`[[ADR-9999]]` is also left alone: it is a *deliberately* broken link, used by [[TASK-0225]] and `FEAT-0093` to assert that an unresolvable link is reported rather than silently dropped.

Two frontmatter rewrites needed correcting afterwards — this note's own title (which names the bare form as the defect) and `DES-0003`'s `source:`, which then said `project-os-dev` twice. The frontmatter pass had no inline-code awareness; the prose pass did.

### The cheap half, done at last

`CONTEXT.md` now names the namespace: two upstream repos, `project-os-dev` holds the ADRs, cite them as `[[project-os-dev#ADR-0011]]`, a bare id always means this repo. It had mentioned `project-os-dev` **zero times** while 77 citations pointed there. Called *"cheaper than both"* by [[ISS-0148]] on 2026-08-12 and skipped twice since.

### Guarded

- `test_no_bare_citation_names_an_upstream_decision` — **self-maintaining**: any ADR id with no note in `docs/decisions/` must carry a project prefix, so adding a local ADR satisfies it and citing a new upstream one bare fails. No list to keep current.
- `test_a_standing_document_names_the_upstream_namespace` — CONTEXT.md must name both the repo and the citation form.
