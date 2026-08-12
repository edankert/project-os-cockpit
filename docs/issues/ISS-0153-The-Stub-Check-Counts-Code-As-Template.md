---
type: "[[issue]]"
id: ISS-0153
aliases: ["ISS-0153"]
title: "The stub check reads inline code as template placeholders — two written documents are reported as unfilled, with a verb that has no action behind it"
status: fixed
severity: medium
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
phase: "[[PHASE-030-Obligations-Go-Home]]"
features: ["[[FEAT-0091-The-Standing-Documents]]", "[[FEAT-0094]]"]
tasks: []
related: ["[[ISS-0152]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
tags: [issue, obligations, false-positive]
---

# The stub check counts code as template

## What was found

Edwin, 2026-08-12: *"The tool provides Needs you options for the Architecture and Ownership.md files but it does not allow me to select anything, how do I review this?"*

He cannot select anything because **there is nothing to do**. Both documents are written; the obligation is wrong.

`standing.check` marks a document a `stub` when it holds three or more placeholders, and `_PLACEHOLDER_RE` is `<[A-Za-z][^>\n]{2,40}>|TODO|FIXME|replace_me|YYYY-MM-DD`. Every hit in these two is **inline code**:

| document | "placeholders" | what they actually are |
|---|---|---|
| `ARCHITECTURE.md` | `<type>`, `<path>`, `<repo>`, `<iframe src=…>` | `` `GET /index/<type>` ``, `` `data: <path>` ``, `` `python -m project_os_cockpit <repo>/docs` ``, and an HTML tag in an example |
| `OWNERSHIP.md` | `<handle>`, `<name>`, `<name>` | `` `user:<handle>` ``, `` `group:<name>` ``, `` `system:<name>` `` — the owner format, which is what an ownership document is *for* |

`ARCHITECTURE.md` carries a full ASCII architecture diagram and a Components section. It is manifestly not a stub. **A document is being told to write itself because it explains a path convention.**

A real template placeholder looks nothing like these — `<What is wrong?>`, `<Change Title>`, `<affected areas/flows/workflows>` — prose in angle brackets, and **never inside backticks**.

## The second half: a verb with nothing behind it

Even for a genuine stub the row said `Confirm`, and clicking offered nothing — `/api/notes/actions?id=ARCHITECTURE` answers `actions: []`, correctly, because a standing document has no status and no human transition.

**`Confirm` is the wrong verb for every owed kind.** You cannot confirm a document nobody has written. The three owed kinds want three different things — create it, write it, decide which file is the one — and the one kind `Confirm` fits (`stale`: *"still true?"*) is deliberately **not** owed.

## The fix

**Strip code before scanning.** Fenced blocks and inline spans are removed first, so notation is notation. That takes this corpus from two false stubs to zero and leaves every genuine placeholder intact.

**A verb per kind**, read from the finding rather than one constant: `missing` → **Create**, `stub` → **Write**, `ambiguous` → **Resolve**. The row opens the document, which is the action — not every obligation is a button, and a surface that says `Write` and opens the file has told the truth twice.

## What the tests hold

- The exact strings from both documents parse as **not** stubs, named individually, so a future tightening of the regex cannot quietly re-break them.
- A document that really does hold its template is still a stub — the vacuity guard, without which the fix is indistinguishable from deleting the check.
- Each owed kind reports its own verb.
