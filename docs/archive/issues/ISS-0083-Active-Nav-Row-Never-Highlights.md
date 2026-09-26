---
type: "[[issue]]"
id: ISS-0083
aliases: ["ISS-0083"]
title: "The navigator never highlights the open note, because refreshActiveNavRow selects li.nav-item while the class sits on the inner div"
status: fixed
severity: medium
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Found 2026-08-02 while building [[TASK-0273]], which needs the active row in order to open the group containing it"]
component: desktop-renderer
related: ["[[TASK-0273-Finished-Groups-Roll-Up]]"]
fixed_by: ["[[TASK-0273-Finished-Groups-Roll-Up]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The active row never highlights

## What

`refreshActiveNavRow` does:

```ts
wsNavContent.querySelectorAll<HTMLLIElement>('li.nav-item').forEach((li) => {
  li.classList.toggle('is-active', !!rel && li.dataset.rel === rel);
});
```

`navItem` builds `<li data-rel=…>` with **no class**, and puts `nav-item` on the `<div>` inside it. So the selector matches no navigable row, and the function is a no-op.

## Evidence

Measured against the tree at `f5e6637`, before any of [[FEAT-0057]]'s changes — features mode, then `navigateTo` the first row in the list:

```
rowsWithRel:       112
liNavItemMatches:    1     <- the `… N more` fold row, the only li that sets the class
isActiveAnywhere:    0     <- after navigating to a row that IS in the list
```

The CSS agrees with the markup, not with the selector: `.ws-nav-content .nav-item.is-active` styles the div. Only the selector is wrong.

## Why nobody noticed

The highlight is a quiet affordance — you generally know what you just clicked. It only becomes load-bearing when the row is somewhere you did **not** click from: an agent's `cockpit:focus` event switching modes underneath you, or a note reached from History or the context pane.

It surfaced now because [[TASK-0273]] puts finished groups behind a roll-up and has to *open* the group containing the active row. That made a decorative no-op into a functional one.

## Fix

Select `li[data-rel]`, and toggle `is-active` on the inner `.nav-item` — matching what the stylesheet already targets. The `li` stays the handle for walking up to the enclosing `<details>`.

## Evidence it is fixed

Navigating to a row puts `is-active` on exactly one element, and it is the one whose `data-rel` matches.
