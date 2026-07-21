---
type: "[[feature]]"
id: FEAT-0037
aliases: ["FEAT-0037"]
title: "Context menus & clipboard — cut/copy/paste and standard right-click everywhere, including the terminal"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
goal: "Right-click works everywhere: a single main-process context-menu handler provides role-based Cut/Copy/Paste/Select All wherever there is a selection or editable field (plus macOS Look Up and spellcheck for free), deferring to the existing custom nav/link/rail menus; the terminal gets its own menu (Copy when selected, bracketed Paste, Select All, Clear) plus ⌘C/⌘V wiring and an opt-in copy-on-select setting; the doc pane gains Copy ID / Copy path unification and 'Dispatch selection as prompt…' glue into the verb system."
requirements: []
tests: []
tasks: ["[[TASK-0166]]", "[[TASK-0167]]", "[[TASK-0168]]"]
related: ["[[FEAT-0012-Native-Nav-Right-Pane]]", "[[FEAT-0024-Agent-Verbs]]"]
---

# Context menus & clipboard

## Why

Electron provides no native text context menu — right-click is dead outside the custom menus, and the terminal has no menu at all (user feedback 2026-07-19; spec: round-2 artifact §5). Decision taken: terminal right-click with a selection opens the menu (Mac convention); copy-on-select ships as a setting for the PuTTY-inclined.

## Scope

- **TASK-0166:** generic handler on `webContents "context-menu"` — role-based items when `params.isEditable` or `params.selectionText`; custom menus keep priority (they preventDefault first); covers doc text, palette input, settings fields.
- **TASK-0167:** terminal menu — Copy (`term.hasSelection()`), Paste (clipboard → PTY, bracketed-paste for multi-line), Select All, Clear; ⌘C copies selection / ⌘V pastes; `copyOnSelect` app setting.
- **TASK-0168:** doc-pane extras — unify Copy ID / Copy path across menus; selection menu adds Copy, "Copy as Markdown quote", and "Dispatch selection as prompt…" (selected text → dispatch prompt, reusing the FEAT-0025 runtime).
