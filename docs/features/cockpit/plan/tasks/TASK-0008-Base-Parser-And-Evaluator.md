---
type: "[[task]]"
id: TASK-0008
aliases: ["TASK-0008"]
title: ".base parser + DSL evaluator"
status: backlog
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: M
due: ""
depends: ["[[TASK-0007]]"]
blocks: ["[[TASK-0009]]"]
related: []
tests: []
---

# .base parser + DSL evaluator

> **Deferred (2026-05-08).** [[ADR-0004]] moved the cockpit to a code-driven JSON layer; this task is no longer required for FEAT-0006. Kept in-tree at `status: backlog` because if a future "render any `.base` as a standalone HTML page" feature is scaffolded, ~70 % of the planned work below is still applicable. Re-activate by setting `status: next` and updating `implements` to point at the new feature.

## Definition of Done
- [ ] `docs_server.bases` module with: `parse(path) -> BaseDocument`, `evaluate(base, index, *, this=None) -> EvaluatedBase`.
- [ ] `BaseDocument` carries: `filters` (AST), `formulas` (dict of name → AST), `properties` (dict of key → display config), `views` (list of view configs).
- [ ] `EvaluatedBase` carries: `views` (each with its filtered+sorted+grouped row set) and `rows` (list of row dicts keyed by property name; values include resolved formula outputs).
- [ ] Filter evaluator handles every primitive used in the existing 12 `.base` files:
  - Boolean: `and`, `or`, `not` (YAML mapping form *and* the `'!expr'` string-prefix form).
  - Comparison: `==`, `!=`.
  - Type-link literal: `link("X")` and `"[[X]]"` — both resolve to the same value (a typed-link sentinel). `type == link("feature")` matches notes whose `type` frontmatter is `[[feature]]`.
  - File predicates: `file.ext`, `file.inFolder("path/")`, `file.hasLink(this.file)`.
  - Frontmatter predicates: `<field>.containsAny("a", "b", ...)`, `<field>.isEmpty()`.
- [ ] `containsAny` semantics: scalar field value → "value is in the given set"; list field value → set intersection non-empty. Documented in module docstring and tested both ways.
- [ ] `this.file` substitution: when `this` is provided to `evaluate(...)`, expressions referencing `this.file` resolve to that note's path. When `this` is absent, expressions referencing `this.file` evaluate to None and predicates depending on it short-circuit to False.
- [ ] Formula evaluator handles `if(cond, a, b)` and `file.asLink(<expr>)`.
- [ ] Per-view post-processing: `groupBy.property` + `groupBy.direction`, `sort` (list of `{property, direction}`), `order` (column order projection), `columnSize`, `rowHeight` carried through into `EvaluatedBase` for the renderer to consume.
- [ ] Unrecognised primitives log a warning naming the offending file + token, then evaluate to False (rows excluded) rather than crashing.
- [ ] Unit tests cover: every primitive in isolation, `this.file` binding, the `'!status.containsAny(...)'` string-prefix negation form, scalar-vs-list `containsAny`, and a full pass of NAV.base + CONTEXT.base against a fixture index.

## Steps
- [ ] YAML-load `.base` (the file format is plain YAML — `pyyaml` already a dep).
- [ ] Parse the filter tree into a small AST (Boolean nodes, Compare nodes, Call nodes for `file.X(...)` / `<field>.containsAny(...)`).
- [ ] Implement the evaluator as a recursive walker; `this` and the `Index` flow through as evaluator state.
- [ ] Implement formulas similarly — one walker, separate entry point.
- [ ] Implement view post-processing (group/sort/order projection).
- [ ] Build a fixture docs tree under `tests/fixtures/cockpit/` with a handful of notes covering each predicate.
- [ ] Write the test suite.

## Notes
**Pin during implementation:**
- The `'!status.containsAny(...)'` form (with the leading `!`) appears as a quoted string in YAML because `!` is a YAML reserved character. Detect it as a string-prefix negation and parse the remainder normally.
- `link("X")` and `"[[X]]"` are interchangeable surface syntax for the same typed-link value.
- When `groupBy.direction` and a `sort` rule on the same property both apply, group-by direction wins for group ordering and the sort rule applies within each group.

Do **not** speculatively implement primitives that no current `.base` file uses. Add them when a real base needs them.
