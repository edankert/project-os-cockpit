---
type: "[[design]]"
id: DES-0007
aliases: ["DES-0007"]
title: "The bench closes the loop — variants rendered and chosen, surfaces measured side by side, annotations that become requests"
role: proposal
status: draft
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Review 2026-08-03: a design is prose read once; PHASE-022's twelve rounds each began with hand-driven CDP measurement because the tool cannot compare its own surfaces"]
asset: ""
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[FEAT-0067-Designs-Render-Their-Artefacts]]", "[[FEAT-0068-The-Measure-View]]", "[[FEAT-0069-Annotate-To-Request]]", "[[FEAT-0070-Design-Gating-And-Scaffolding]]", "[[DES-0002-Cockpit-Design-System]]"]
---

# The bench closes the loop

## What exists, and where it stops

The bench renders a DES note's markdown and tracks **revisions** — `design_revisions_payload` walks real git history, and `design_revision` on an acceptance records *which* revision was accepted so a v3 approval cannot launder v6. `DES-0004` shipped with an HTML asset (`asset:` frontmatter) that renders as a static page. The loop stops there: options live in prose, comparison happens in the reader's head, comments happen in chat, and nothing downstream is held to the outcome.

## 1 — Variants (FEAT-0067)

Convention over machinery: a DES note section `## Variant <name>` whose body contains a fenced `html` block is a variant. The bench renders every variant's fragment in a **sandboxed iframe** (`sandbox` without `allow-scripts` unless the note's frontmatter opts in), side by side, with the design-system stylesheet injected so mockups inherit the real tokens.

**Choosing**: a `Choose` action per variant → through the actuator path ([[DES-0005]]) it (a) records `chosen_variant: <name>` on the DES note, (b) offers to scaffold the ADR — template-filled with the variants as *options considered*, `status: proposed`, for the human to Accept through the same actuator row. The decision record falls out of the act of deciding; nothing is auto-accepted.

## 2 — The measure view (FEAT-0068)

The tool PHASE-022 lacked. Two panes, each holding either a bench artefact/variant or **one of the cockpit's own surfaces**, plus a probe:

- **Artefacts**: same-origin iframes — the probe walks `getComputedStyle` directly.
- **Own surfaces**: the desktop shell injects the probe into its own webContents (the machinery my CDP sessions used by hand, made a feature). Pick an element in each pane; the table shows both sides' box metrics, font, colour — differences highlighted.

Output is copyable as the measurement tables this session's ISS notes carried — because that is the artefact a design correction starts from. Explicitly v1-scoped to self and artefacts; external apps are a later risk scan.

## 3 — Annotate to request (FEAT-0069)

Click a rendered artefact (or select text in any DES note) → a pin plus comment box → `POST /api/cockpit/review-request` with a new kind `annotation`, `subject:` the DES id, and an `anchor` (variant + CSS path + offset for pins; text quote for selections). The queue renders annotations under the design's entry; resolving goes through the existing `review-resolve`. The pin's anchor degrades honestly: if the artefact changed and the anchor no longer resolves, the annotation shows "anchor lost at revision <sha>" rather than floating to the wrong spot — same honesty rule as `subject_missing`.

## 4 — Gating and scaffolding (FEAT-0070)

- A feature gains optional `design: "[[DES-…]]"`. Local validator rule `DESIGN-GATE`: a feature whose design is not `accepted` cannot leave the pending band. Warning for one release, then error — ADR-0011's pattern. Upstream proposal filed alongside, same route as the close-out rule.
- On an accepted design: a `Derive requirements` action **dispatches** the impact-analysis/feature-scaffold skills with the design as source. An agent drafts REQs citing the design's decisions; they arrive `draft`; the human approves through the actuator row. The human-agent split is preserved at every step — text never appears without someone having asked.

## Rejected alternatives

- **A visual design editor.** The bench renders and compares; authoring stays in files, where agents and humans already share it.
- **Screenshot-diff comparison.** Pixels diff noisily and explain nothing; computed-style tables name the difference. (Screenshots remain *evidence* — FEAT-0066 — just not the comparator.)
- **Auto-generating REQs on accept.** FEAT-0051's rule: things appearing without anyone asking is the worse failure. Dispatch, draft, approve.
