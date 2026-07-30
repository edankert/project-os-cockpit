---
type: "[[issue]]"
id: ISS-0037
aliases: ["ISS-0037"]
title: "Library rows for top-level project files are dead clicks"
status: triage
severity: low
phase: "[[PHASE-012-Attention-In-The-Strip]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["found while fixing [[ISS-0033]], 2026-07-28"]
related: ["[[ISS-0033-Identity-Band-Link-Is-Dead]]", "[[ISS-0036-Root-File-Shadowed-Docs-Note]]"]
fixed_by: []
---

# The Library's root-file rows do nothing

## What

`_project_support_items` emits `url: "/README.md"` for the top-level project files, and has since FEAT-0010. `extractRel` returns `null` for that shape, so the row gets no `data-rel` and the delegated click handler — which keys entirely off `data-rel` — ignores it. Clicking README, ROADMAP or SECURITY in the Library does nothing, and has never done anything.

Pre-existing and out of scope for FEAT-0043; recorded rather than fixed.

## Why the obvious fix is wrong

Routing `/X.md` by stripping the slash was tried while closing [[ISS-0033]] and reverted. `/docs/README.md` and `/README.md` both reduce to the rel `README.md`, so two distinct Library rows — a real note and a project file — collapse onto one fetch, and whichever file the server prefers wins. That is [[ISS-0036]] relocated into the client.

## What it actually needs

The rel must carry the disambiguator the url already has. Options, in rough order of preference:

1. A `~root/<file>` virtual-page prefix, matching the mechanism `~design` and `~review` already use, routed explicitly by `navigateToInner`.
2. Keep the leading `/` through `navigateToInner` as an explicit "project root" marker, and stop the API from stripping it. Cheaper but relies on a distinction the API has historically treated as noise ("accepts both forms").

Not urgent: the files are reachable in the editor, and nothing in the cockpit sends a user to them except the identity band, which navigates directly and is unaffected.
