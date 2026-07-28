---
type: "[[issue]]"
id: ISS-0042
aliases: ["ISS-0042"]
title: "The shell declares a parallel palette for roles base.css already names"
status: triage
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["found by the living style guide on its first render, 2026-07-28"]
related: ["[[ISS-0023-Status-Vocabulary-Drift]]", "[[DES-0002-Cockpit-Design-System]]", "[[TASK-0228-Living-Style-Guide]]", "[[TST-0019-Status-Vocabulary-Parity]]"]
fixed_by: []
---

# Two palettes for the same roles

Found by the style-guide page the moment it first rendered — which is the point of a page that reads the implementation instead of restating it.

## What it found

`renderer.css` redefines **10 tokens** over `base.css`, in two different ways.

**Overridden with a different value:**

```
--bg      base.css hsl(0 0% 99%)  →  renderer.css #f7f7f8
--border  base.css hsl(0 0% 86%)  →  renderer.css #e3e3e6
```

Neither pair is equal: `hsl(0 0% 99%)` is `#FCFCFC`, and `hsl(0 0% 86%)` is `#DBDBDB`.

**A parallel vocabulary for roles that already have names:**

| base.css | renderer.css | Same role? |
|---|---|---|
| `--text` | `--fg` | yes |
| `--text-muted` | `--fg-muted` | yes |
| `--text-faint` | `--fg-faint` | yes |
| `--accent-link` | `--accent` | yes |
| — | `--bg-elevated`, `--accent-soft`, `--row-hover`, `--row-active` | shell-only |

## Why it matters

**[[DES-0002]]'s palette table documents `base.css`.** The desktop app draws with `renderer.css`. So the design system, as written, describes the browser cockpit and not the application Edwin actually looks at — and the two disagree on the page ground and every hairline border.

This is [[ISS-0023]] one level up. That issue was one vocabulary restated in six places, drifting; this is two vocabularies for one set of semantic roles, already drifted, with nothing checking either. [[TST-0019]] guards the *status* palette and has nothing to say about the semantic one.

## What it is not

Not a bug in the style guide, and not necessarily a bug in the shell. A desktop app wanting a slightly different ground from a browser page is defensible. What is not defensible is that it is **undocumented and unchecked** — the divergence was invisible until a page read both files side by side.

## Options

1. **The shell consumes `base.css`'s names** and deletes its own aliases; keep only genuinely shell-specific tokens (`--row-hover`, `--row-active`). Single vocabulary; largest edit.
2. **Declare the aliasing explicitly** — `--fg: var(--text)` — so the mapping exists in one place and cannot drift, keeping shell-only tokens as they are.
3. **Document the shell palette as a deliberate second layer** in DES-0002, and extend the parity check to cover it. Cheapest; leaves two vocabularies.

Not chosen here. Recording it with the measurement is the finding; picking the fix is Edwin's.
