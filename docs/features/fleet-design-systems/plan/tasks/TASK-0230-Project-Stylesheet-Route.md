---
type: "[[task]]"
id: TASK-0230
aliases: ["TASK-0230"]
title: "Serve a project's own stylesheets to its design artifacts"
status: done
phase: "[[PHASE-999-Unscheduled]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0044-Fleet-Design-Systems]]"]
parent: "[[FEAT-0044-Fleet-Design-Systems]]"
effort: "M"
depends: []
blocks: ["[[TASK-0231-Fleet-Design-System-Rollout]]"]
related: ["[[TASK-0227-Expose-Shell-Stylesheet]]", "[[ISS-0043-Sandboxed-Artifact-Cannot-Read-CSS]]", "[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]"]
tests: []
---

# Serve a project's own stylesheets

## Why

[[TASK-0227]] exposed the *cockpit's* shell stylesheet so its own style guide could show real widgets. Every other project in the fleet has the same need and none of them can meet it: `public/css/style.css` and `obsidian-plugin/styles.css` sit above the docs root, and the design-asset route reaches nothing there.

Without this, a downstream design system can only be a hand-typed table — the exact artifact [[DES-0002]] stopped claiming was checked.

## The shape

**The allow-list is derived from the corpus, not configured.** A design note declares what it reads:

```yaml
stylesheets:
  - public/css/style.css
```

and the sidecar serves exactly those paths and nothing else. A hardcoded list would drift from the notes; a directory share would publish the project.

## Definition of Done

- [x] A design note may declare `stylesheets:`, and those paths are served under a dedicated route — evidence: `_design_stylesheets`; `GET /_project/<rel>`; `test_a_declared_stylesheet_is_served`
- [x] The allow-list is **computed from the design notes**, so adding a path to a note is the only way to widen it — evidence: `project_stylesheet_allowlist` walks `notes_by_type("design")`; `test_the_allowlist_is_the_corpus_not_a_constant`
- [x] Anything not declared is refused, including a real stylesheet elsewhere in the project — evidence: same test — `private.css` is a real stylesheet in the project and 404s; `test_declaring_nothing_serves_nothing` closes the empty case
- [x] Traversal, escape and symlinks-out-of-tree are refused, reusing the existing guards rather than re-deriving them — evidence: `test_the_route_reads_css_and_nothing_else` and `test_a_symlink_out_of_the_tree_is_refused`, which resolves through the link and refuses with 403
- [x] CSS only — the route must not become a way to read the project — evidence: extension check plus the declaration filter; `test_the_route_guards_hold_even_if_the_declaration_filter_does_not` exercises the route's own check with a hostile allow-list
- [x] `Access-Control-Allow-Origin` is set so a **sandboxed, opaque-origin** frame can fetch and re-inject, as [[ISS-0043]] established — evidence: asserted in `test_a_declared_stylesheet_is_served`; without it a sandboxed opaque-origin frame cannot fetch and re-inject ([[ISS-0043]])
- [x] A declared path that does not exist 404s cleanly; the page says so rather than rendering unstyled — evidence: `test_a_declared_but_missing_stylesheet_404s`, which also asserts the rest of the server is unaffected
- [x] Every guard test **fails when its guard is removed from the endpoint**, asserts the guarded effect did not happen, and asserts the refusal pre-empts the other branches ([[ISS-0056]]'s three-clause rule) — evidence: four mutations run. Allow-list and containment each killed a test. **Two did not**, and that is recorded rather than hidden — see Result

## Steps

- [x] `stylesheets:` in the design payload
- [x] The route, with the corpus-derived allow-list
- [x] Tests over real HTTP, including the three-clause guard shape
- [ ] Release to `project-os` and re-vendor the fleet — **outstanding**, carried by [[TASK-0231]]

## Result

**Mutation testing found two guards that could not fire.** Removing the route's `.css` check and its `..` check each left every test green — because `_design_stylesheets` drops those declarations before they ever reach the allow-list. The tests were exercising the *filter*, not the route.

Two layers deserve two tests. `test_the_route_guards_hold_even_if_the_declaration_filter_does_not` hands the route a hostile allow-list directly — what would happen if the filter were relaxed — and the `.css` mutation now dies against it.

The `..` check still cannot be made to fire: containment (`relative_to`) refuses the same inputs, with the same status. So it is kept as a fast path and **its comment says exactly that**, rather than implying it protects something. A check that cannot fire under a comment claiming it guards is the defect this codebase has found three times today ([[ISS-0024]], [[ISS-0049]], [[ISS-0056]]); leaving one behind while fixing its siblings would have been the fourth.

## Notes

**Read-only, and CSS only.** The render server binds `0.0.0.0`; these are stylesheets an app already ships to anyone who loads it. The narrowing exists so the route cannot become a general file read, which is the thing that would make binding wide a mistake.

The three-clause guard rule is not optional here. Four versions of one loopback test in [[ISS-0056]] each missed the mutation that motivated them; this route ships with the rule already learned.
