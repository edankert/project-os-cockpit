---
type: "[[task]]"
id: TASK-0168
aliases: ["TASK-0168"]
title: "Doc-pane menu extras — Copy ID/path unification, Copy as quote, Dispatch selection as prompt"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0037"
effort: ""
due: ""
depends: ["[[TASK-0166]]"]
blocks: []
related: ["[[FEAT-0024-Agent-Verbs]]", "[[FEAT-0025-Dispatch-Runtime]]"]
tests: []
---

# TASK-0168 — doc-pane menu extras

Unify Copy ID / Copy path across every menu that shows notes (nav rows, cards, doc links, doc header — today the wording and availability differ). Selection menu in the doc pane adds **Copy as Markdown quote** (`> …` with a `[[id]]` attribution line) and **Dispatch selection as prompt…** — the selected text becomes the dispatch prompt for the current agent via the FEAT-0025 runtime (confirm dialog showing the target agent, same delivery rules as verbs). Verification: each menu shows the same Copy ID/path pair; dispatching a selection lands it in the terminal REPL/shell exactly like a verb dispatch.
