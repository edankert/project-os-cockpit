---
type: "[[risk]]"
id: RISK-0008
aliases: ["RISK-0008"]
title: "With the framing allowlist gone, the iframe sandbox is the only thing between a framed document and the cockpit — and nothing marks that attribute as load-bearing"
status: closed
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[ADR-0042-What-May-Be-Framed]]", "desktop/src/renderer/renderer.ts:5708"]
likelihood: low
impact: high
mitigation:
  - "A test asserts the frame's sandbox attribute and that it does NOT contain allow-same-origin, failing loudly if anyone adds it"
  - "A comment at the sandbox line states that it is the only boundary, naming ADR-0042"
  - "Any change to the frame's sandbox attribute is treated as a security change and reviewed as one"
related:
  - "[[ADR-0042-What-May-Be-Framed]]"
  - "[[FEAT-0148-One-HTML-Viewer]]"
  - "[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"
tags: [risk, security, render]
---

# The sandbox is the only boundary

## Description

[[ADR-0042-What-May-Be-Framed]] removes the allowlist that decided which files the cockpit would frame. That is defensible — `/docs/<rel>` already serves every file under `docs/` to anyone who can reach the sidecar, and the sidecar binds `0.0.0.0` by design — so the allowlist was never what kept those files private. But it means the **only** thing now separating a framed document from the cockpit is one HTML attribute: the iframe is sandboxed without `allow-same-origin`, which gives the document an opaque origin and denies it the sidecar API, the parent DOM and `localStorage`.

One attribute, in one line, with `allow-scripts` already present beside it. Adding seven characters to that attribute would hand every framed page the run of the cockpit's origin, and nothing in the code says so. The comment at `desktop/src/renderer/renderer.ts:5708` explains why `allow-scripts` is *on*; it does not say that `allow-same-origin` being *off* is the entire security model.

The likelihood is low — nobody adds `allow-same-origin` casually — and the impact is high, which is the shape of a hazard that needs a guard rather than vigilance.

## What this risk is *not*

It is not "framing becomes a file browser". That was the first version of this note, written before `/docs/<rel>` was read. Serving every file under `docs/` by path is what the cockpit has done for months, on an interface bound to the LAN, and framing adds nothing to it. Whether the sidecar should be reachable from the network at all is a separate, older question, and it belongs to [[RISK-0001-Terminal-Exposure]] and [[RISK-0007-Remote-Workspace-Trust-Boundary]].

The only genuinely new exposure is presentational: a file nobody meant to publish can now be *shown* by the cockpit as though it were part of the record. That is a tidiness cost Edwin accepted explicitly, not a confidentiality one.

## Mitigation

- A test that reads the frame's `sandbox` attribute and fails if `allow-same-origin` appears in it. This is the whole mitigation; the rest is documentation.
- One sentence at the sandbox line saying it is the only boundary and naming this ADR, so the next person to widen it has to do so deliberately.

## Triggers

- `allow-same-origin` appearing in any `sandbox` attribute in the renderer.
- A framed document being given a channel to the parent — `postMessage` handling, a shared `localStorage` shim, a query parameter carrying a token.
- The viewer being reached from anything other than an iframe.

## Closing condition

Closes when the sandbox assertion exists as a test. Not when [[ADR-0042-What-May-Be-Framed]] is accepted — an accepted decision with no enforcement is the state this note exists to flag.

## Amendment history

**First version, 2026-09-12 (morning):** titled *"Framing becomes a file browser"*, on the assumption that the design allowlist was what kept the cockpit from serving arbitrary files. **Rewritten the same day** when that was checked and found false. The hazard the first version named does not exist; the hazard that does exist is the one the first version treated as already handled.

## Closed 2026-09-12

On the mitigation this risk named, not on the danger going away. The danger is unchanged: after [[ADR-0042-What-May-Be-Framed]] the absence of the same-origin flag is the only thing between a framed document and the cockpit.

What closes it is that the absence is now **asserted and explained**. `tests/test_framing.py` reads every `sandbox` value the renderer sets and fails if the flag appears in any of them, and a second test requires the reason to be written at the attribute rather than only in a note — a boundary nobody names is one a refactor removes. `tests/test_design_bench.py` used to refuse the literal anywhere in `renderer.ts`; that file went with the bench, and the refusal moved into `test_framing.py` with it.

Both tests were run against a deliberately broken renderer — the flag added to the viewer's frame — and both failed, which is the only evidence that matters for a guard.
