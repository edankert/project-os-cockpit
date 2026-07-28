---
type: "[[task]]"
id: TASK-0223
aliases: ["TASK-0223"]
title: "Brief payload and the identity band"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0043-Design-Top-Level-Surface]]"]
parent: "[[FEAT-0043-Design-Top-Level-Surface]]"
effort: "M"
depends: ["[[TASK-0222]]"]
blocks: ["[[TASK-0224]]"]
related: []
tests: []
---

# Brief payload and identity band

## Definition of Done

- [x] A sidecar payload reads `LLM_BRIEF.md` — identity (name, purpose), high-value paths, invariants — evidence: `brief_payload()`; `GET /api/cockpit/brief`
- [x] The payload flags a brief that is **absent**, **unfilled**, or **filled**, as three distinct states — evidence: `test_three_states_not_two`
- [x] The surface renders the identity band first: what this is, who for, its shape — evidence: `buildIdentityBand` prepended before the design register
- [x] An unfilled brief renders a prompt to fill it, **never the placeholder text** — evidence: `test_placeholder_text_is_never_returned` (payload blanks it) and `test_the_band_never_renders_the_placeholder` (the unfilled branch returns before touching name/purpose)
- [x] An absent brief degrades to the design system alone rather than an error — evidence: `test_an_absent_brief_degrades_silently`
- [x] The band links to the file so editing is one click, and the file remains the source — evidence: 'Read the full brief' / 'Open LLM_BRIEF.md' navigate to the note

## Steps

- [x] Parse the brief's known sections tolerantly — a hand-edited brief must not break the surface
- [x] Three-state detection with tests for each
- [x] Build the band
- [x] Verify against this repo's real brief

## Result

Three states, and the middle one is why. A half-filled brief keeps what is real and blanks what is not — `Name: the thing` survives while `Purpose: REPLACE ME` becomes empty — because half-done is the normal state of a file being written, and a payload that discarded the whole thing would punish progress.

Tolerant parsing verified against a deliberately awkward file: unknown heading first, sections reordered, `Purpose` before `Name`. All parse; nothing breaks. The brief is prose a human edits, and failing closed on a hand-written file would be the wrong instinct entirely.

The unfilled branch returns **before touching `name` or `purpose`** — asserted by reading the branch, not just the output, so the placeholder cannot leak through a later edit.

## Notes

Parsing must be **tolerant**. The brief is prose a human edits, not a data file: a missing section, a reordered one, or an added heading are all normal and none may break the surface. Read what is recognised, ignore the rest, and never fail closed on a file whose whole purpose is being hand-written.

Three states, not two, because "no brief" and "brief that says REPLACE ME" call for different things — one is a project that has not adopted the convention, the other is a project that adopted it and stopped.
