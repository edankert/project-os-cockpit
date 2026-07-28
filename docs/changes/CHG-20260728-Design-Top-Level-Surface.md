---
type: "[[change]]"
id: CHG-20260728-Design-Top-Level-Surface
aliases: ["CHG-20260728-Design-Top-Level-Surface"]
title: "Design becomes a top-level mode; the render endpoint serves top-level project files"
status: merged
date: 2026-07-28
owner: user:edwin
source: ["[[FEAT-0043-Design-Top-Level-Surface]]"]
related: ["[[PHASE-009-Design-Surfaces]]", "[[REQ-0024-Brief-Is-Maintained]]", "[[ISS-0033-Identity-Band-Link-Is-Dead]]", "[[ISS-0034-Design-Mode-Reachability-Untested]]", "[[ISS-0035-Brief-Payload-Placeholder-Contract]]"]
---

# Design as a top-level surface

## What changed for anyone using the cockpit

**The strip has seven modes, with Design second** — `overview · design · features · tasks · issues · review · library`. Nothing was retired to make room; a stored preference for any existing mode still resolves. Design is the only mode that is both a list and a page: the left pane carries the design system and the proposals, the main pane frames whichever is open, and reselecting the mode keeps the artifact you had open.

**The design surface opens with the project's identity**, read from `LLM_BRIEF.md` — what this is and what it is for, above the design system. A brief that still carries template placeholders is reported as unfinished instead of being rendered.

**A design lists the ADRs it links**, with each decision in the ADR author's own words, and nothing else. Governance ADRs stay in Library.

## What changed for anyone driving the API

- `GET /api/cockpit/brief` — new. Three states: `absent`, `unfilled`, `filled`. `state` describes the **identity** (a real name and purpose), not whether the file is finished; `placeholders` counts every remaining one, and the two are independent in both directions.
- `GET /api/cockpit/nav?mode=design` — new mode, two groups (`design-system`, `design-proposals`), items pointing at `~design/<id>`.
- `designs_payload` entries gain `rationale[]`.
- `GET /api/render?path=<file>` now serves the allowlisted top-level project files (`README.md`, `ROADMAP.md`, `SECURITY.md`, and the new `LLM_BRIEF.md`) from the project root. **This is a fix, not a widening**: the Library has emitted `/README.md` urls since FEAT-0010 and this endpoint had always refused them, so those rows were dead clicks. Exact filename match only; traversal and non-allowlisted root files are still refused, verified over HTTP.
- `SCHEMA_VERSION` is unchanged at 4 — every change here is additive.

## Validator

`validate_brief()` reports `BRIEF-PLACEHOLDER` as a **warning** with a count. A warning because 10 of 11 fleet repos would fail on the day it shipped, and a validator that fails everywhere gets ignored rather than obeyed.

## Worth knowing

Three defects in this feature were caught by independent review *after* the tasks were closed with evidence ([[ISS-0033]], [[ISS-0034]], [[ISS-0035]]) — a dead link, an untested route, and placeholder text leaking through a field nobody checked. Each DoD bullet had named its evidence, and that is precisely what let the review falsify them: it went to the named evidence and found it narrower than the claim.
