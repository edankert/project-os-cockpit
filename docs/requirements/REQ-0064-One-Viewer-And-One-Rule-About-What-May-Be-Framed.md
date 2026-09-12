---
type: "[[requirement]]"
id: REQ-0064
aliases: ["REQ-0064"]
title: "Any HTML page in the record opens in one viewer that knows nothing about designs, and the only limit on what it may frame is the workspace's own `docs/`"
status: draft
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'can we introduce a html viewer instead of this design bench?'", "Edwin, 2026-09-12: 'I don't think the current bench provides much ... so I would remove it and instead have a generic html viewer'"]
priority: high
scope: "The surface that frames an HTML page, the limit on what it may frame, and the removal of the design bench and its endpoints. Not: what a design note contains."
acceptance:
  - "[ ] An HTML page any note references opens in a viewer, whatever the note's type — evidence: <TST-0087 step>"
  - "[ ] No route, view mode or display decision in the sidecar or the renderer is named after, or gated on, `design` — evidence: <grep command output>"
  - "[ ] `/api/design/capture`, `/api/design/comment`, `/api/design/offer-review`, `/api/design/verdict`, `/api/cockpit/design-revisions/`, `/api/cockpit/design-comments/`, `/design-asset/` and `/design-asset-at/` are gone, and each is either re-homed with its new home named or retired with the reason written down — evidence: <the capability table in FEAT-0148, plus routes grep>"
  - "[ ] A design's Accept and Decline still work from the note, through `/api/notes/transition`; `design_revision` is no longer written and the three notes that already carry one are unchanged — evidence: <walk step, note_writes.py>"
  - "[ ] A design note carrying a `## Revisions` log and `## Review` comments still shows them, because they are Markdown in the note and the note renderer already shows Markdown — evidence: <TST-0087 step>"
  - "[ ] A link that names a design's ID opens the design's **note**, like every other ID, with no special case left in link resolution; [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] is `superseded` with this requirement named in its `superseded_by:` — evidence: <REQ-0062 frontmatter, deep-link.ts>"
  - "[ ] The Intent landing still leads a reader to every design, and what its design rows now open is stated — evidence: <TST-0087 step>"
  - "[ ] `docs/reference/cockpit-capability-register.md` has no row naming a removed route, and Deck's adoption table has been told which rows changed — evidence: <register path, deck path>"
implements: "[[FEAT-0148-One-HTML-Viewer]]"
verifies: []
related:
  - "[[ADR-0042-What-May-Be-Framed]]"
  - "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]"
  - "[[FEAT-0042-Design-Bench]]"
  - "[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"
  - "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]"
  - "[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]"
tests: ["[[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]"]
tags: [requirement, render, design]
---

# One viewer, and one rule about what may be framed

## Approval

**Criterion 5 is answered.** Edwin, 2026-09-12: a design's ID opens **the note**, like every other ID. The rule is deleted rather than re-pointed, `designBenchTarget` goes with it, and [[TASK-0614-Links-Stop-Asking-For-The-Bench]] carries it out.

*(The first version of this section put two readings to him — (a) the rule disappears, (b) it re-points at the viewer — and recommended (a). He chose (a). The alternative is recorded here rather than deleted, because the next reader will want to know that re-pointing was considered and why the note won: once a design is Markdown with pictures, the note **is** the design, so resolving an ID to it is the right answer rather than a fallback.)*

**Criterion 2's framing limit is also answered, and in the other direction from the first draft.** There is no allowlist and no reachability test: the viewer frames any file inside the workspace's `docs/`, cross-repo included ([[ADR-0042-What-May-Be-Framed]]). Edwin asked *"what is the issue if this isn't limited?"* and the answer, once checked, was none — `/docs/<rel>` has served every file under `docs/` with no gate for months, on a socket bound to `0.0.0.0`. The boundary that remains is the iframe sandbox, which is what [[RISK-0008-The-Sandbox-Is-The-Only-Boundary]] now tracks.

**Criterion 3 is answered too, and the first draft of the table was wrong in two places.** Edwin corrected the design-verdict row on 2026-09-12: *"The only thing about design verdict buttons, why can we not have these, we currently allow for the other items to be triaged and providing review info?"* Accept and Decline for a design were never bench-hosted — they sit on the note, from the actuator table every type shares — so nothing was being removed there. What is retired is the verdict's **binding to an artifact commit**, which he accepted with *"Drop the binding for now!"*, and which re-opens a real hazard: [[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]. The second error was in the region-comments row, which claimed the feature had never been used; 12 region-anchored comments exist. Both corrections are visible in the feature note rather than absorbed.

**Nothing in this requirement is now waiting on Edwin** except the two things the whole phase waits on: accepting [[ADR-0042-What-May-Be-Framed]], and settling [[ADR-0043-How-A-Note-Marks-HTML-To-Render]].

## Statement

The cockpit **shall** frame an HTML page through one viewer that is not specific to designs, **shall** frame any file inside the workspace's `docs/` and nothing outside it ([[ADR-0042-What-May-Be-Framed]]), and **shall not** retain a surface, route or view mode whose identity is "design".

## Rationale

Edwin, 2026-09-12: *"I don't think the current bench provides much ... so I would remove it and instead have a generic html viewer."* The corpus agrees with him more than the code does. Measured across 47 design notes in 12 repos on 2026-09-12:

- 33 declare an `asset:`, so two-thirds of the bench's reason to exist is present.
- 24 artifacts declare `data-design-region`, the anchor for region comments — and **12 region-anchored comments exist in the whole fleet**, all of them on one note (`project-os-deck` DES-0002), all written by one reviewer in one pass on 2026-09-05. Four more comments are document-level. So the annotation machinery has been used once, seriously, by a reviewer who could equally have typed the same list into the note.
- 6 notes carry a real `## Revisions` entry (deck DES-0002 has 10, your-health DES-0002 has 9, this repo's DES-0004 has 4). That is the one bench feature with genuine recurring use — and it survives the bench's removal for free, because a revision log is Markdown in the note.
- 1 note uses `## Variant`, and `chosen_variant:` is set on **none**. Choose-a-variant and the ADR it offers have never been exercised on a real design.

The removal is therefore small in what it loses and large in what it simplifies: `tests/test_design_bench.py` alone holds 170 tests across 3,174 lines, plus `test_design_gate.py` (7), `test_design_variants.py` (11) and `test_design_tokens.py` (10).

Removing a feature means removing its tests. It does **not** mean removing its notes: [[FEAT-0042-Design-Bench]] and its tasks stay as the record of what was built and why, at `superseded`.

## Acceptance Criteria

- [ ] An HTML page any note references opens in a viewer, whatever the note's type — evidence: <path>
- [ ] Nothing in the sidecar or renderer decides display by the word `design` — evidence: <path>
- [ ] The eight endpoints are gone, each re-homed or retired with the reason recorded — evidence: <path>
- [ ] Accept and Decline still work from a design's note, and `design_revision` is no longer written — evidence: <path>
- [ ] A design's `## Revisions` and `## Review` sections still read as Markdown in the note — evidence: <path>
- [ ] A design's ID opens its note, with no special case left in link resolution, and REQ-0062 carries `superseded_by:` — evidence: <path>
- [ ] The Intent landing still reaches every design — evidence: <path>
- [ ] The capability register carries no removed route, and Deck has been told — evidence: <path>

## Traceability

- Implements: [[FEAT-0148-One-HTML-Viewer]]
- Verified by: [[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]
