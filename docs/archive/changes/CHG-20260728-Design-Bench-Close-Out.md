---
type: "[[change]]"
id: CHG-20260728-Design-Bench-Close-Out
aliases: ["CHG-20260728-Design-Bench-Close-Out"]
title: "The design bench closes: a shell-stylesheet route, a living style guide, one palette vocabulary"
status: merged
date: 2026-07-28
owner: user:edwin
source: ["[[FEAT-0042-Design-Bench]]"]
related: ["[[PHASE-009-Design-Surfaces]]", "[[REQ-0023-Design-Artifacts-In-Repo]]", "[[ISS-0042-Two-Palettes-For-The-Same-Roles]]", "[[ISS-0049-Token-Parity-Check-Has-No-Caller]]", "[[CHG-20260728-Design-Top-Level-Surface]]"]
---

# Design bench close-out

## For anyone using the cockpit

**The design system is now a page you can look at.** `DES-0002` has an artifact that reads every value from the real stylesheets *as it renders* — 98 swatches, both schemes, the status bands beside the severity ramp, live widgets, and the two gaps the note records (no type scale, no spacing scale) stated beside their real measurements. Nothing on it is typed, so nothing on it can drift.

**A design with no artifact is readable.** The empty stage offers the note, and the id chip in every design header links to it.

**Documents render as documents.** A design that declares no `viewport:` gets the full pane, its own scrolling and no viewport chooser. Only a design that declares one is framed — and a declared frame is scaled to fit rather than making the stage a second scroller.

**Artifacts follow the app's theme**, passed in the asset URL. An artifact may honour or ignore it.

## For anyone driving the API

- `GET /_shell/<file>` — new. Serves the desktop shell's built stylesheet so an artifact can show real widgets. **Allow-list of exactly one filename**; absent in mode-1, where it 404s cleanly.
- `/_static/*.css` and `/_shell/*.css` send `Access-Control-Allow-Origin: *`. The design frame is sandboxed with an **opaque origin**, so it cannot read `cssRules` from stylesheets it links; it fetches the text and re-injects it instead. CSS only — `cockpit.js` is unchanged and a test asserts it.
- `GET /design-asset/...` now sends `charset=utf-8` on text types, matching the historical route. Previously the same bytes decoded two ways, so revision-compare showed an encoding difference as a design difference.
- `SCHEMA_VERSION` unchanged at 4.

## For anyone reading the stylesheets

**One vocabulary.** The desktop shell no longer declares `--fg`/`--fg-muted`/`--fg-faint`/`--accent` for roles `base.css` already names, nor overrides `--bg`/`--border` with different values — 152 usages rewritten. **The app's neutrals de-tint as a result**: the shell's were blue-tinted hex, `base.css`'s are true greys. Four shell-only tokens remain because `base.css` has no such role.

A test asserts the two declaration sets are **disjoint**, so any future redeclaration fails — not just the four aliases that existed.

## Withdrawn

**The design bench does not check token parity**, by decision ([[ISS-0049]] option 1). The claim that it did was refuted by mutation in independent review and has been removed from the feature, the phase and [[DES-0002]] rather than quietly dropped. `design_tokens.py` stays as a working module with no caller.

## Worth knowing

Fourteen defects were found on this surface **after** its tasks were closed with evidence, almost all by Edwin using the app rather than by the 126 tests. The pattern in most of them: verification ran in a context the app never uses — non-sandboxed, same-origin, no re-injection. `tools/dev/cdp.py` exists because of that, and the rule is written beside it: **the design frame is sandboxed, opaque-origin and cross-process, so an artifact checked outside it is a different artifact.**
