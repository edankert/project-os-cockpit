---
type: "[[issue]]"
id: ISS-0125
aliases: ["ISS-0125"]
title: "Eight singleton project documents carry a lifecycle status they do not have and reach no surface — 94% of them are stale fleet-wide, and a style guide has been `active` for six months"
status: triage
phase: ""
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["Edwin 2026-08-10: 'some notes are required but they are one-off notes, similar to glossary, we never need more than one and there is not really a state associated with them, it would be good to identify these notes and give them a home in the projects and not in the library section'"]
severity: medium
component: "docs-taxonomy"
parent: ""
related: ["[[ISS-0124-Four-Note-Types-Have-No-Status-Table]]", "[[ISS-0122-Active-Modes-Doing-Column-Counts-Notes-Nobody-Is-Working]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]", "[[TASK-0379-Architecture-Becomes-A-Design]]"]
tests: []
---

# The singleton documents have no lifecycle and no home

## The class

There is a kind of note this taxonomy has never named: **one per project, no lifecycle, written for a human to read.** Not work, not a decision, not a record of something that happened — a standing description of the project.

Every member sits at `docs/` root:

| note | type | status | last touched |
|---|---|---|---|
| `README.md` | `reference` | `active` | 2026-05-08 |
| `INDEX.md` | `reference` | `active` | 2026-05-08 |
| `OWNERSHIP.md` | `reference` | `active` | 2026-05-07 |
| `GLOSSARY.md` | `glossary` | `active` | 2026-05-07 |
| `ARCHITECTURE.md` | `architecture` | `draft` | 2026-05-07 |
| `DESIGN.md` | `reference` | `active` | **2026-01-26** |
| `STYLEGUIDE.md` | `reference` | `active` | **2026-01-26** |
| `PHASES.md` | *(no frontmatter at all)* | — | — |

Three different type values for one kind of thing, and `DESIGN.md` and `STYLEGUIDE.md` have not been touched since the day they were created — six and a half months.

## Why the status is not merely useless

`active` is not a neutral value. It is in the **`active` band — "work in flight"** (`statuses.py`), so these documents are coloured, sorted and counted as work somebody is doing.

That is the same defect [[ISS-0122]] measured from the other end: Active mode reports `Doing · 44`, of which **18 are `reference` notes and 1 is the glossary**, against exactly one item anybody is working. [[ISS-0122]] proposed fixing the bucketing. This is the cause — the notes should not have a lifecycle status to be bucketed by.

A status field on a document with no lifecycle can only ever say something false or say nothing. `STYLEGUIDE.md` reading `active` after six untouched months is the first; `DASHBOARD.md` carrying no status at all is the second, and is the more honest of the two.

## The fleet already has them, and does not maintain them

Measured across all 12 repos, 2026-08-10. The set is not missing — it is **present and abandoned**:

| | |
|---|---|
| documents present | **90** of a possible 96 (only `yourtrainer-mcp` is thin, missing 5) |
| stale (`updated` > 90 days) | **74** |
| carrying no `updated:` at all | **11** |
| **stale or undated** | **85 of 90 — 94%** |
| still recognisably template stubs | 12 |

Every repo tells the same story: 7 or 8 of these documents present, 7 of them stale. `obsidian-supernote-sync` has 8 present and 8 stale.

So "all projects should have them" is already true; what is missing is that **nothing names the set, nothing checks it, and nothing shows it** — and a document nobody is ever asked about is a document nobody updates. That is the case for prominence, and it is measured rather than asserted.

## `reference` is doing three unrelated jobs

Of the 18 `reference` notes:

- **5 are singletons** — `README`, `INDEX`, `DESIGN`, `OWNERSHIP`, `STYLEGUIDE` (the class above)
- **9 are container boilerplate** — `docs/*/README.md` directory signposts nobody reads as documents
- **4 are templates** — under `__templates__/`

Leaving one genuine reference document: `docs/references/COCKPIT-API.md`. [[REQ-0025]] already recorded the split ("13 of 21 `reference` notes are outside the Docs tree") as a gap to be aware of; this issue is that the type itself is the reason.

## And they reach no surface

[[REQ-0025]] records it verbatim: *"`ARCHITECTURE.md`, `GLOSSARY.md`, `DASHBOARD.md` reach no surface, having never been in a `rare:` or `by-type:` group either."*

So the documents describing what the project **is** are the ones a reader cannot navigate to. Edwin's framing: they belong "in the projects and not in the library section" — the Intent view ([[FEAT-0087]]), which is where the project's description and constraints go.

## This changes the answer to ISS-0124

[[ISS-0124]] asked whether four types need status tables. If this class is real, the answer is **not more tables** — it is an explicit *status-free* category, which is the second option that issue already floated on the evidence that `dashboard` carries no status and always has.

## Settled: architecture is not a design

[[TASK-0379]] would have converted `ARCHITECTURE.md` into a design. **Cancelled** (Edwin, 2026-08-10: *"Architecture should not be a design type"*). A design carries `proposed` → `accepted`, revisions and verdicts; a standing description of how the system is built has none of those, and giving it a lifecycle would reproduce the very defect measured above.

`ARCHITECTURE.md` is a member of this class.

## Next Actions

- [ ] **Remove `DASHBOARD.md`** — decided (Edwin, 2026-08-10). An Obsidian artifact whose six `.base` embeds are all dead; only `NAVIGATION.base` and `CONTEXT.base` survive, and those are the two that matter (left-hand nav, right-hand context). It names neither correctly.
- [ ] Name the class and decide its carrier — a new type, or `reference` narrowed to it with the boilerplate and templates moved off
- [ ] Decide the status question: no `status:` field at all, or an explicit status-free set the validator knows about ([[ISS-0124]])
- [ ] Give the class a home in the Intent view ([[FEAT-0087]]), not the Library tree
- [ ] Fix `PHASES.md` — it has no frontmatter and claims to be *"consumed by Bases / dashboards"*, which the dashboard removal makes false
- [ ] Fix the two stale `updated:` dates — `GLOSSARY.md` and `ARCHITECTURE.md` were both edited long after the date they claim
- [ ] Consider proposing upstream: this is a template-owned taxonomy question, and every project-os repo has the same eight documents
