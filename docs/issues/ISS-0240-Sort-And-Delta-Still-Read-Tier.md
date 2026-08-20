---
type: "[[issue]]"
id: ISS-0240
aliases: ["ISS-0240"]
title: "`sort_items` and `_delta_key` still read `tier:`, so removing the field would change 232 of 580 delta identities"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
severity: medium
component: cockpit
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[PHASE-039-A-Test-Says-Who-Executes-It]]", "[[CHG-20260820-The-Suite-Is-The-Verdict]]"]
---

# The field is unread where it decides, and read where it orders

[[PHASE-039]] closed on a criterion reading *"`tier:` is read by no code path"*. That is false, and independent review caught it.

**What is true**: no *section* and no *gate* decision reads `tier:`. `GATING_TIERS`, `PERMANENT_TIERS` and `TIER_LABELS` are deleted, and `blocking_for`, `missing_issue_refs` and both front doors read `section_of` instead.

**What still reads it**:

| site | what it uses the field for |
| --- | --- |
| `acceptance.sort_items` | the primary sort key — a check's canonical position in the suite |
| `acceptance._delta_key` | part of a row's IDENTITY across two release tags |
| `Suite.tier` | kept for the file-shape parser, which derives a tier from a document heading |
| `tools/scripts/migrate-acceptance-checks.py` | writes `tier:` into migrated notes and scopes its parity comparison |

## Why this matters, measured

Independent review simulated the announced follow-up — stripping `tier:` from the 671 notes carrying it — against `your-trainer`:

- **232 of 580 delta keys change identity**, so those rows would read as *removed* and *newly added* across a release tag. A release delta reporting 232 spurious changes is one nobody reads. This holds at `HEAD` and in the working tree.
- **Suite position**: 74 rows move — *in the working tree*. At `HEAD` **zero** move, because ids there were allocated in document order, so `(tier, id)` and `(id)` agree. **This note was filed to correct a working-tree measurement and repeated one**; caught by a second independent review.

The delta-key figure is the one that matters, and it is basis-independent.

[[ADR-0039]] deliberately deferred the strip so a bad derivation stayed recoverable. That reasoning holds; what it did not say is that the strip has a prerequisite.

## Done when

- [ ] `sort_items` orders on something stable that is not `tier:` — [[ISS-0224]] settled the canonical order as `(tier, id)`, so the replacement is a decision rather than a rename
- [ ] `_delta_key` no longer includes `tier:`, and a delta across the change is proved to report zero spurious rows
- [ ] Only then, the strip

## Not urgent

Nothing is broken today: the field is still written by the migration and present on every note, so both readers get what they expect. This is a prerequisite discovered early, not a defect in flight.
