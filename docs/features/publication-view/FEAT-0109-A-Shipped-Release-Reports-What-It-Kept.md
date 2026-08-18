---
type: "[[feature]]"
id: FEAT-0109
aliases: ["FEAT-0109"]
title: "A shipped release reports what it kept, not what it claims — the evidence behind tests_verified is graded and the published artifacts are checked"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Independent functionality review of PHASE-034, 2026-08-16", "Measured against ../your-trainer on 2026-08-16"]
goal: "Stop the shipped-release page asserting things that are not true. A link rendered under the heading 'Acceptance tests as executed' should report what was actually executed, and an artifact listed as published should be known to parse."
requirements: []
tasks: ["[[TASK-0450-Grade-The-Evidence-Behind-Tests-Verified]]", "[[TASK-0451-A-Published-Artifact-Is-Checkable]]"]
design: ""
release: ""
depends: []
related: ["[[FEAT-0107-Publication-Is-A-List-Of-Releases]]", "[[FEAT-0106-The-Release-Page]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]

---

# A shipped release reports what it kept

## The heading is currently a claim the page does not check

[[FEAT-0107]] taught the shipped-release page to read `tests_verified:` and render it under **Acceptance tests as executed**. Follow one link:

- `REL-0012` (v2.1.6, shipped) names `[[TST-0011-AndroidBleHardeningAcceptance]]`.
- `TST-0011` has **18 checkboxes, all unticked**, and **18 `- Evidence: ___` slots, all blank**, while carrying `status: ready` and `last_verified: 2026-06-26`.
- Its own text reads: *"Until every Tier-A row here passes, the branch stays unmerged (RISK-0008)."*

Nothing in it was executed. The page renders it under a heading that says it was.

And the field is worse than stale — it is **inert**. Measured across `../your-trainer`: `last_verified` equals `created` in **15 of the 16** TST notes that carry it. The single exception is TST-0011, which differs by one day and has zero of eighteen rows walked. **The field has never recorded a verification, anywhere.** It is written at authoring time by a template and never touched again.

That is a stronger and simpler statement than the one this project has been carrying — *"11 of 21 TST notes were verified before their features last moved"* — and it retires it. Staleness was never the problem; the field does not mean what its name says.

## What the page says instead

```
Acceptance tests as executed
  TST-0011  Android BLE hardening    0/18 walked · 0 evidence · never verified   ⚠
  TST-0014  Edge-to-edge insets      12/14 walked · 12 witnessed                 ✓
```

Twenty lines of rendering. It converts a link that *implies* evidence into a row that *reports* it, and it is the only thing that makes `tests_verified` worth writing at all.

The grade is a read of the linked note: ticked over total, how many rows carry a filled evidence slot or a dated witness, and whether `last_verified` differs from `created`. Nothing new is stored.

## The artifacts are structured data nobody parses

The page lists `REL-0012-v2.1.6-play-store-listing.xml` as a row you can open. It is XML with hard constraints stated in its own header comment — *"500-char ceiling per locale"*, *"Char counts asserted < 500"* — and verified by nobody.

Parsed on 2026-08-16, all seven of them:

```
REL-0007 v2.0.0  play-store-descriptions   ** does not parse **
REL-0007 v2.0.0  play-store-listing        10 locales  max 492   ← 8 chars of headroom
REL-0008 v2.0.2  play-store-listing        10 locales  max 481
REL-0009 v2.0.4  play-store-listing        ** does not parse **
REL-0010 v2.0.5  play-store-listing        10 locales  max 362
REL-0011 v2.1.0  play-store-listing        10 locales  max 484
REL-0012 v2.1.6  play-store-listing        10 locales  max 414
```

**Two of the seven are corrupt**, with an identical signature — leaked tool-call closing tags appended after the root element:

```xml
</release-notes>
</content>
</invoke>
```

That is not a typo, it is a class of corruption from the authoring path, and it is sitting in the declared source of truth for store copy in ten locales — one of them the file the public 2.0 announcement was cut from. This is the whole argument for the check: it is four lines of stdlib XML parsing, and the corpus it would run against is already broken twice over.

```
Published artifacts
  REL-0012-v2.1.6-play-store-listing.xml   10 locales · max 414 chars   ✓
  REL-0009-v2.0.4-play-store-listing.xml   does not parse (line 115)    ✗
```

It turns a file-open into a verdict, and it is the only **external** artifact this whole system touches.

## Acceptance criteria

- [x] Each `tests_verified` entry renders **walked / total** and an **evidence count**, not just a link.
- [x] A note whose `last_verified` equals its `created` is reported as **never verified**, in those words.
- [x] A `tests_verified` entry that resolves to **no note** says so rather than rendering a dead link.
- [x] An empty `tests_verified` — **5 of 12** of `../your-trainer`'s release notes — renders as a stated absence, not an empty section.
- [x] Each artifact reports **parses / does not parse**, and for a store listing, the **locale count** and the **longest entry**.
- [x] A malformed artifact names its **line number** and does not prevent the rest of the page rendering.
- [x] An artifact kind the checker does not know is listed **without a verdict**, rather than being flagged.
- [x] Nothing here writes. A failing artifact produces no obligation and no badge — it is a fact on the page of the release that shipped it.

## How this is verified

A `TST-*` asserting the grade against a fixture whose numbers are known exactly, plus a live assertion against `../your-trainer` that both corrupt files are reported and the five good ones are not. Mutations to defeat: grade a blank evidence slot as filled; treat `last_verified == created` as verified; swallow the parse error and report `✓`; report only the first artifact.

## What this deliberately does not do

**It does not fix the two corrupt files.** They belong to `../your-trainer` and repairing another repo's committed artifacts is that repo's work, not this one's — see the phase note's *found in the fleet* section.

**It does not gate on any of this.** A shipped release is history. Nothing here can make a past release blocking, and no badge counts it.
