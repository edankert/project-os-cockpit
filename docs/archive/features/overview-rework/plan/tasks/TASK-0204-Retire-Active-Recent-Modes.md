---
type: "[[task]]"
id: TASK-0204
aliases: ["TASK-0204"]
title: "Retire the Active and Recent nav modes (UI-only) — mode strip slims to six; phase-less default falls back to Overview; server modes stay"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0040-Overview-Rework]]"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[FEAT-0036-Live-Work-Views]]", "[[FEAT-0008-Cockpit-API-Hardening]]", "[[TASK-0164]]", "[[TASK-0165]]"]
tests: []
---

# Retire the Active and Recent nav modes (UI-only)

## Definition of Done

- [x] The Active and Recent mode buttons are removed from the mode strip; the strip carries six modes (Review takes the vacated slot — button shipped by FEAT-0041's TASK-0206; until that lands the strip simply has one fewer button).
- [x] Phase-less projects' default nav mode falls back from Active to Overview, whose Now board (TASK-0165) renders the same in-flight data full-width.
- [x] `nav?mode=active` and `nav?mode=recent` remain served unchanged (FEAT-0008 API stability rule) — the Now board and the strip work tab (TASK-0163) keep consuming `mode=active`; a wire test asserts both endpoints still respond.
- [x] A persisted left-mode value of `active`/`recent` in localStorage migrates gracefully (falls back to the default mode, no error).
- [x] FEAT-0036's note records the partial UI supersession (done at preflight; verify it still reads true at close-out).

## Steps

- [x] Remove the two buttons + their routing from the mode strip; adjust the default-mode fallback for phase-less projects.
- [x] Handle stale persisted mode values.
- [x] Add/keep server-side tests for `mode=active` / `mode=recent` payload stability.

## Notes

Rationale (dossier §Retiring the Active and Recent modes): Active was a whole mode for a state the audit found empty most of the time — its glanceable job moved to the focus band and phase meta, its live job to the progress rail (FEAT-0038) and strip; Recent's what-changed job is superseded by the git-anchored commits panel, with ⌘P + history covering jump-back. This is a button retirement, not an API one.
