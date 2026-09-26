---
type: "[[issue]]"
id: ISS-0043
aliases: ["ISS-0043"]
title: "A sandboxed artifact cannot read the stylesheets it links, so the style guide rendered empty"
status: fixed
severity: high
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28: 'I do not see any of the artefacts ... DES-0002'"]
related: ["[[TASK-0228-Living-Style-Guide]]", "[[TASK-0215-Design-Render-Surface]]", "[[DES-0002-Cockpit-Design-System]]"]
fixed_by: []
---

# The page worked everywhere except where it runs

Edwin: *"I am unable to scroll the page and I do not see any of the artefacts."*

## Cause

The design frame is `sandbox="allow-scripts"` and deliberately **not** `allow-same-origin` — a frame granted both can remove its own sandbox, and `test_frame_allows_scripts_but_nothing_else` asserts it stays that way.

The cost, which [[TASK-0228]] did not anticipate: a sandboxed frame has an **opaque origin**. Every stylesheet it loads *from the very server that served it* is then a cross-origin resource, so `sheet.cssRules` throws `SecurityError`. The style guide enumerates design tokens through exactly that call. It found nothing, rendered its prose and empty swatch panels, and — being short — had nothing to scroll.

Proven side by side: the same URL in two frames, one sandboxed and one not. Prose and applied CSS identical; swatches present in one, absent in the other. Applying a stylesheet never needed an origin; *reading its rules* always did.

## Why the verification missed it

Every check ran against a **directly-opened page**, which has a real origin — the one context the design bench never uses. The harness had grown careful about the real bundle, the real stylesheet chain and the real height chain, and still tested the artifact outside the sandbox that defines its runtime.

## Fix

Keep the sandbox. Fetch the stylesheet **text** and inject it as an inline `<style>`; inline sheets belong to the frame's own document and carry no origin question, so the CSSOM opens up and nothing downstream changes.

That fetch is itself cross-origin from an opaque origin (`Origin: null`), so `/_static/*.css` and `/_shell/*.css` now send `Access-Control-Allow-Origin: *`. **CSS only** — narrowed deliberately so this does not become blanket CORS on every static file the package ships; `cockpit.js` is unchanged and a test asserts it. These are the app's own stylesheets, already readable by anything that can reach the render port, and no user data passes through them.

The page also stops failing blank: an unexpected error now renders what happened. A blank page is the worst failure mode for a page whose job is to show things — and blank was exactly what Edwin got.
