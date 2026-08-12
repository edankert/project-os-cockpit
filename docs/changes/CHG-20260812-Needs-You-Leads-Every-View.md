---
type: "[[change]]"
id: CHG-20260812-Needs-You
title: "Needs you leads every view and sits on the overview — plus the watermark that reported time since midnight and the brief rendered as raw markdown"
status: merged
date: 2026-08-12
owner: user:edwin
related: ["[[FEAT-0094]]", "[[ADR-0025]]", "[[ISS-0150]]", "[[ISS-0151]]", "[[ISS-0068-Waiting-On-You-Is-A-Workaround]]", "[[FEAT-0092]]"]
tags: [change]
---

# Needs you leads every view

Three more from Edwin using the shipped app.

## What changed

**`Since you looked` measured from midnight.** The header did `seen_at.slice(0, 10)`, so catching up at 08:52 read *8 hours ago* — a clock reading dressed as an elapsed time. The payload has always carried the instant and a test asserts it does; the consumer threw the precision away one line before using it ([[ISS-0150]]).

**The Intent band printed raw markdown as text.** Reported as hard line breaks in `LLM_BRIEF.md`. **The file has none** — measured across all twelve repos, zero wrapped-prose pairs, this one's longest prose line 451 characters. The band set `forSection.body` as `textContent` under `white-space: pre-wrap`, so the source's own newlines became breaks and its syntax showed as syntax. Sections now arrive rendered by the same pipeline every note uses, and the `pre-wrap` rule went with them ([[ISS-0151]]).

**`Needs you` leads Features and Intent**, matching Issues' `Needs triage` and Tests' `Needs a run`, and the same set is on the overview grouped by owning view. Every count comes from `obligations.owed_items` — the walk behind the badge and the landing page — so the four surfaces cannot disagree ([[FEAT-0094]]).

## The rule this required narrowing

A leading group means an owed row appears twice. [[ISS-0068]]'s *"one item, one home"* forbade that, which is why Issues **moves** triage items rather than copying them.

Edwin chose copy, and [[ADR-0025]] narrows the rule to **one obligation, one owning view**. The reason is that moving costs more than it saves here: a requirement that vanishes from under its feature *because* it needs approving makes the tree wrong at the moment the reader most needs it right — they are about to approve it and cannot see what it belongs to.

**The hazard it introduces was caught the same day.** Two tests counted owed *marks* across a view, which double-counts once a row can appear twice. They count distinct ids now, and that is the rule any future surface must follow.

## Impact

- `nav_payload` prepends a `needs-you` group for `features` and `intent`. **Not** for `issues` and `tests`: their existing groups gather the same set under names that say more, and a second would duplicate where it buys nothing.
- `brief_payload` sections gain `body_html`; `body` stays, so a caller wanting the source need not unparse HTML.
- The overview gains a band beneath the digest.

## Documentation Coverage (All Types Considered)

- features: new ([[FEAT-0094]] + TASK-0393/0394/0395)
- requirements: not-applicable
- tasks: new (three, all `done`)
- issues: new ([[ISS-0150]], [[ISS-0151]]) · updated ([[ISS-0068]] — the rule is narrowed at its source, not only in the ADR)
- tests: updated (11 assertions, and two that had to change meaning)
- workflows: not-applicable
- decisions: new ([[ADR-0025]])
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (counters, metrics)

## Eleven tests failed, and that is the part worth keeping

Nine were **positional** — `groups[0]` standing in for "the standing set" or "the designs list" — and broke the moment anything was prepended. They select by key now. A test that identifies a group by its position asserts the layout as well as the fact, and only one of those is the thing it means.

The other two were the real finding, and they failed for exactly the reason [[ADR-0025]] predicted rather than for a reason nobody had thought about.
