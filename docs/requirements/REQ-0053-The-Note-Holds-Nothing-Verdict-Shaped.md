---
type: "[[requirement]]"
id: REQ-0053
aliases: ["REQ-0053"]
title: "The check note holds intent only — nothing verdict-shaped and nothing platform-shaped"
status: implemented
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
priority: high
scope: "acceptance note schema"
implements: "[[FEAT-0134-The-Note-Sheds-The-Verdict]]"
acceptance:
  - "[x] No acceptance note in a migrated repo carries `mark`, `verdict_date`, `verdict_reason`, `invalidated_by`, `automation`, `covered_by` or `evidence`."
  - "[x] The validator refuses one that does, and its message names the ledger as the place the value belongs."
  - "[x] `covers:`, `tier:`, `area:` and `level:` are untouched — they state intent, not outcome."
  - "[x] The 203 automation annotations in your-trainer survive the removal in a form FEAT-0138 can seed from."
  - "[x] The migration refuses a second run and lists what it could not convert rather than skipping silently."
covers: []
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]"]
tags: [requirement]
---

# Note = intent

## Statement

A check note **shall** state what the behaviour is, how it is grouped and what it gates. It **shall not** state who verified it, when, on what platform, with what result, or whether a machine covers it.

## The removal is smaller than it reads

Four of the seven fields are empty on **all 671** acceptance notes fleet-wide (`verdict_date`, `verdict_reason`, `invalidated_by`, `covered_by`). Two carry data: `mark` (671) and `automation` (203 non-`manual`, `your-trainer` only). `evidence` is empty everywhere it is not decorative.

**The one thing that must be carried across is `automation:`'s prose provenance.** The field's values were themselves backfilled from 203 parenthesised annotations naming 54 JVM classes ([[ISS-0198]]); those annotations are [[FEAT-0138]]'s seed and the only record of which machine covers which check.

## Acceptance criteria

- [x] Seven fields gone from schema, template and validator.
- [x] Validator refuses them and points at the ledger.
- [x] Intent fields untouched.
- [x] Automation provenance preserved.
- [x] Migration is idempotent and reports what it skipped.
