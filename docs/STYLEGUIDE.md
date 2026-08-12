---
type: "[[reference]]"
id: STYLE
owner: user:edwin
created: 2026-01-26
updated: 2026-08-12
tags: [styleguide]
---

# Styleguide

## Statuses are not listed here

This document used to carry them:

> Issues: `triage|open|in-progress|blocked|fixed|closed`
> Features: `backlog|planned|in-progress|in-review|done`

**Every one of those lines was wrong.** `closed` was deleted by ADR-0008 — `fixed` is the single terminal issue status. `in-progress` and `in-review` were retired by ADR-0012 in favour of `doing` and `review`. The document sat unchanged for 198 days telling a reader the opposite of what the validator enforces.

That is the failure this project has a rule about, so the rule applies to this file too: **the vocabulary lives in one place and is read, never restated.**

- **Canonical taxonomy:** `../tools/instructions/STATUSES.md` — allowed values and legal transitions, per type.
- **In code:** `statuses.py` — bands, palette and the completed set, checked against five other surfaces by `tests/test_status_vocabulary.py`.

If you want to know what a status may be, open one of those two. A third copy is how the first two come to disagree.

## Frontmatter

- Every note carries `type`, `id`, `title`, `status`, `owner`, `created`, `updated`.
- `type` is a wikilink to its template — `type: "[[issue]]"` — and `tags` are topical labels only.
- `aliases: ["ISS-0042"]` on every note, so `[[ISS-0042]]` resolves.
- **Standing documents carry no status.** They are a manifest, not a lifecycle; `updated:` is what means something ([[FEAT-0091]]).

## Ids

`PHASE-####`, `ISS-####`, `FEAT-####`, `TASK-####`, `REQ-####`, `RISK-####`, `TST-####`, `ADR-####`, `DES-####`, `REL-####`, `CHG-YYYYMMDD-Short-Description`.

Counters only rise. An id is allocated, not owned: deleting a note never frees its number.

**A note in another project** is `[[project-os-dev#ADR-0011]]` — project id, `#`, note id ([[ADR-0024]]). A bare id always means *this* repo.

## Prose

- **Never hard-wrap.** One paragraph is one line; the reader's application decides where it breaks. Structural breaks — between paragraphs, list items, around code and tables — are expected and are not wrapping.
- Write what was found and why it matters, not only what was done. A note whose value is the finding should lead with it.
- Say the number. *"76 of 116 unreviewed"* survives; *"many"* does not.
- When a decision is reversed, **keep the old reasoning and say what overtook it**. A record that erases its first answer is not one.

## Callouts

Obsidian callout syntax is part of the vocabulary, not decoration:

```markdown
> [!note] Accept — 2026-08-12 (user:edwin)
> The reasoning, in the decider's own words.
```

Both readers render it — Obsidian natively, the cockpit since [[FEAT-0095]]. Used by the decision record; available anywhere prose needs setting apart.

## Decisions

- A decision offering a choice states it under `## Options`, numbered `1..N`, and names the one it proposes in `## Decision`. **This is checked** — `DECISION-OPTIONS` errors on a section that cannot be read.
- A decision with open threads may carry an `## Acceptance` section; its criteria are tickable one at a time with evidence.

## Links

- Prefer wikilinks to ids over paths: `[[FEAT-0093]]`, not a filename.
- Link the note that owns the fact, not the nearest note that mentions it.
- Broken wikilinks render as broken **on purpose**. If a link cannot resolve, the surface says so rather than hiding it.

## Where the rest lives

`../tools/instructions/MARKDOWN.md` (authoring), `OBSIDIAN.md` (conventions), `TRACEABILITY.md` (required link graphs), `QUALITY.md` (gates). This file is this project's additions to those, not a replacement for them.
