---
type: "[[issue]]"
id: ISS-0042
aliases: ["ISS-0042"]
title: "The shell declares a parallel palette for roles base.css already names"
status: fixed
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

**Chosen 2026-07-28: option 1.** The shell consumes `base.css`'s names.

- `--fg` → `--text`, `--fg-muted` → `--text-muted`, `--fg-faint` → `--text-faint`, `--accent` → `--accent-link`: **152 usages rewritten**, all four declarations deleted from both schemes.
- The `--bg` and `--border` overrides are deleted too. They were the same name carrying a different value, which is the drift itself rather than a shell need. The desktop now draws `base.css`'s ground: `--bg` `#f7f7f8` → `hsl(0 0% 99%)`, `--border` `#e3e3e6` → `hsl(0 0% 86%)`, and the equivalents in dark. Slightly lighter ground, slightly lighter hairlines — say if that reads wrong and the shell can declare a *different token* rather than redefining a shared one.
- Four tokens stay in the shell because `base.css` has no equivalent role: `--bg-elevated`, `--accent-soft`, `--row-hover`, `--row-active`. A comment above them says why, and says not to reintroduce an alias.

Guarded by `test_the_shell_declares_no_alias_for_a_base_css_role`, which asserts the two declaration sets are **disjoint** — so any future redeclaration of a base.css role fails, not just the four aliases that existed today.

**Verified**, not assumed: every role resolves in both schemes with nothing unresolved, checked in a browser against the built stylesheets.

**Found while doing it, unrelated and pre-existing — and initially overstated.** A first pass reported four tokens "referenced but never declared". Independent review checked them and **only one is a real problem**:

- `--surface-1` (`cockpit.css:487`) — `var(--surface-1)` with **no fallback**, declared nowhere. Invalid at computed-value time, so the property silently renders inherited. Genuine.
- `--tree-indent` — always written `var(--tree-indent, 0px)`. Has a fallback; never invalid.
- `--bg-hover` — always written `var(--bg-hover, rgba(125, 166, 255, 0.08))`. Same.
- `--token` — appears only inside a `base.css` **comment** ("rules use var(--token) only"). A regex false positive, not a reference at all.

The overstatement is the finding worth keeping: a grep for `var\((--[a-z-]+)` counts comments as code and treats a fallback as if it were absent, and the sentence built on it normalised three non-problems next to one real one. The guard now ignores comments and flags only `var()` **without** a fallback, which reduces the pinned set to `--surface-1` alone.