---
type: "[[issue]]"
id: ISS-0146
aliases: ["ISS-0146"]
title: "Intent lists every standing document twice — once from the manifest and once as a reference, under two different ids for the same file, which is why no duplicate check caught it"
status: fixed
severity: medium
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
phase: "[[PHASE-030-Obligations-Go-Home]]"
features: ["[[FEAT-0091-The-Standing-Documents]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"]
tasks: []
related: ["[[ISS-0068-Waiting-On-You-Is-A-Workaround]]"]
tags: [issue, navigation, duplication]
---

# Intent lists every standing document twice

## What was found

Edwin, 2026-08-11: *"The intent reference section seems to repeat some of the docs defined in the top section."*

Not some — **all eight.** Measured from the live payload:

| standing (`What this project is · 8`) | reference (`Reference · 11`) | file |
|---|---|---|
| `README` | `DOCS-README` | `/docs/README.md` |
| `ARCHITECTURE` | `ARCH` | `/docs/ARCHITECTURE.md` |
| `STYLEGUIDE` | `STYLE` | `/docs/STYLEGUIDE.md` |
| `INDEX`, `GLOSSARY`, `OWNERSHIP`, `DESIGN`, `PHASES` | same ids | same files |

`Reference` holds 11 rows, and **8 of them are the 8 above**. Only `ACCEPTANCE-TESTS`, `REF-COCKPIT-API` and the snapshot-migration note are its own.

## Why no check caught it

[[ISS-0068]]'s rule is *one item, one home*, and the guard that enforces it compares **ids**. The manifest ([[FEAT-0091]]) synthesises an id from the document's role — `ARCHITECTURE` — while the reference group uses the note's own frontmatter `id:` — `ARCH`. Same file, same URL, two ids, so a set intersection finds nothing.

**A duplicate that renames itself is invisible to a check that trusts names.** The rel path is the identity that cannot be forged, and nothing was comparing it.

## The fix

The standing manifest owns the eight. `Reference` excludes any document the manifest claims, matched on **rel path** rather than id, so a future renaming cannot reintroduce the pair. Reference keeps what is genuinely its own.

The dedupe guard for this view now compares rel paths too — the assertion that would have failed on the day this shipped.
