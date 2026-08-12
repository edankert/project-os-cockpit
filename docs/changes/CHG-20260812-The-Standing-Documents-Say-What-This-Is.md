---
type: "[[change]]"
id: CHG-20260812-Standing
title: "The eight standing documents are brought current — two were the template's own defaults, one contradicted the enforced taxonomy, and the architecture described a May-era system under an August date"
status: merged
date: 2026-08-12
owner: user:edwin
related: ["[[FEAT-0091-The-Standing-Documents]]", "[[ISS-0153]]", "[[ADR-0010]]", "[[ADR-0024]]", "[[ISS-0123]]"]
tags: [change, docs]
---

# The standing documents say what this is

## What was found

Surveyed by age before touching anything:

| document | `updated` | age | state |
|---|---|---|---|
| `DESIGN.md` | 2026-01-26 | **198d** | the template's four generic bullets, never adapted |
| `STYLEGUIDE.md` | 2026-01-26 | **198d** | the template's, **and wrong about statuses** |
| `OWNERSHIP.md` | 2026-05-07 | 97d | named 5 features of 98, one of which never existed |
| `README.md` / `INDEX.md` | 2026-05-08 | 96d | accurate about project-os, silent about this project |
| `ARCHITECTURE.md` | 2026-08-10 | 2d | **a May-era system under a two-day-old date** |
| `GLOSSARY.md` | 2026-08-10 | 2d | 9 terms, none from the last three months |
| `PHASES.md` | 2026-08-10 | 2d | current |

**The worst was `STYLEGUIDE.md`**, which listed status vocabularies that the validator refuses:

> Issues: `triage|open|in-progress|blocked|fixed|closed`
> Features: `backlog|planned|in-progress|in-review|done`

`closed` was deleted by ADR-0008 and `fixed` is the single terminal issue status; `in-progress` and `in-review` were retired by ADR-0012. A standing document spent 198 days telling a reader the opposite of what the build enforces. It now names the two canonical sources and restates nothing — the rule this project already had, applied to the file that was breaking it.

**And `ARCHITECTURE.md` is the more interesting failure.** Its `updated:` said two days; its content described the Python server of May — five routes (one of them, `/events`, already wrong; the route is `/_events`), no Electron shell, no per-workspace sidecars, no fleet, and a terminal that was still *"ttyd invoked separately"*. **A date was touched without the content being brought with it**, which defeats the one field [[FEAT-0091]] made carry meaning.

## What changed

- **`ARCHITECTURE.md`** — rewritten around what exists: two processes and a fleet, the 40 sidecar modules and 13 IPC modules by what they own, the guarded write path, cross-repo resolution, 63 API routes counted rather than listed (a list here is stale within a week — which is what happened).
- **`GLOSSARY.md`** — 9 terms to ~35, in five groups, covering the vocabulary the project has actually used since May: sidecar, workspace, project id, obligation, owed/settled, reconciled, decision record, watermark, tier, evidence, delegate, and the rules that have names here.
- **`STYLEGUIDE.md`** — statuses removed and *pointed at*; frontmatter, ids, cross-repo links, callouts, decisions and prose rules stated, including *never hard-wrap*.
- **`DESIGN.md`** — this project's principles, organised under the sentence [[REL-0001]] serves, each clause carrying the note that decided it.
- **`OWNERSHIP.md`** — stops enumerating. Listing features was tried and did not survive contact with 93 more of them.
- **`INDEX.md`** — gains a *this project specifically* section, including that **upstream is two repos and no citation says which** ([[ISS-0123]]).
- **`README.md`** — one line locating this repo, since it otherwise describes project-os and never says whose docs these are.

**Every standing document now reports current** — the staleness check is silent for the first time since it was built.

## Three tests broke, all for the same reason

They asserted the corpus's *neglect*: DESIGN and STYLEGUIDE being 198 days stale, and `ARCHITECTURE.md` containing a particular code sample. Bringing the documents current removed the evidence.

Each now **constructs** what it asserts — a document stamped 400 days old, a stub written into a temporary corpus. **A test that waits for neglect fails when the project stops being neglectful**, which is the seventh instance of this class today and the reason the fixtures are worth the lines.

## Documentation Coverage (All Types Considered)

- features / requirements / tasks / issues / workflows / decisions / risks: not-applicable
- tests: updated (three, moved onto constructed fixtures)
- changes: new (this note)
- snapshot: updated (metrics)
