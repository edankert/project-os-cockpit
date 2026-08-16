---
type: "[[task]]"
id: TASK-0451
aliases: ["TASK-0451"]
title: "A published artifact is checkable — two of your-trainer's seven store XMLs do not parse"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0109-A-Shipped-Release-Reports-What-It-Kept]]", "Measured against ../your-trainer/docs/releases on 2026-08-16"]
parent: "[[FEAT-0109-A-Shipped-Release-Reports-What-It-Kept]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# A published artifact is checkable

## Why

`publication.artifacts_for()` lists the `REL-####-…` files beside a release note as rows you can open. The store listings are XML with hard constraints stated in their own header comments — *"500-char ceiling per locale"*, *"Char counts asserted < 500"* — and checked by nobody.

Parsed on 2026-08-16:

```
REL-0007 v2.0.0  play-store-descriptions   ** does not parse **
REL-0007 v2.0.0  play-store-listing        10 locales  max 492
REL-0008 v2.0.2  play-store-listing        10 locales  max 481
REL-0009 v2.0.4  play-store-listing        ** does not parse **
REL-0010 v2.0.5  play-store-listing        10 locales  max 362
REL-0011 v2.1.0  play-store-listing        10 locales  max 484
REL-0012 v2.1.6  play-store-listing        10 locales  max 414
```

Both failures have the same signature — leaked tool-call closing tags after the root element:

```xml
</release-notes>
</content>
</invoke>
```

A class of corruption from the authoring path, in the declared source of truth for store copy in ten locales. Four lines of stdlib parsing turns a file-open into a verdict.

## What

For each artifact: does it parse; and for a store listing, how many locales and the longest entry against the ceiling.

```
REL-0012-v2.1.6-play-store-listing.xml   10 locales · max 414 chars       ✓
REL-0009-v2.0.4-play-store-listing.xml   does not parse (line 115)        ✗
```

## Constraints

- **stdlib only** — `xml.etree.ElementTree`. No new dependency for four lines.
- **Never blocking.** A shipped release is history. This produces no obligation, no badge, no gate entry.
- **An unknown artifact kind is listed without a verdict**, not flagged. The checker knows about store listings; it must not imply judgement over a file it does not understand.
- A malformed file **names its line** and does not stop the rest of the page rendering.

## Done when

- [x] parse verdict per artifact, with line number on failure
- [x] locale count and longest entry for store listings, and the 500 ceiling reported when exceeded
- [x] unknown kinds listed with no verdict
- [x] one malformed artifact does not prevent the others rendering — the mutation that must fail
- [x] asserted live: both corrupt files reported, the five good ones not
