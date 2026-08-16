---
type: "[[issue]]"
id: ISS-0173
aliases: ["ISS-0173"]
title: "The acceptance suite names its features and issues in bare form and the parser reads only wikilinks, so 72 of 82 sections resolve to nothing and every Tier 2 item reports as violating a rule it satisfies"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-16
review_verdict: approved
source: ["Found on 2026-08-16 while checking whether an acceptance row could be scoped to the feature it verifies"]
severity: medium
component: cockpit-server
parent: ""
related: ["[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[FEAT-0102-Publication-Becomes-A-View]]", "[[ISS-0141]]", "[[ISS-0162]]"]
tests: []
---

# The suite's own ids are written in a form nothing reads

## Problem

`acceptance.py:81` extracts the ids a section heading names:

```python
_ID_RE = re.compile(r"\[\[([A-Z]+-[0-9A-Za-z-]+?)(?:\|[^\]]*)?\]\]")
```

Wikilink form only. `../your-trainer`'s suite writes them bare, which is the ordinary way a heading names something:

```
## 1.1 Profile Management (FEAT-0002)
## 1.2 Hardware Connectivity (FEAT-0001, FEAT-0007)
## 1.6 Monetization & Licensing (FEAT-0011, FEAT-0104)
```

Measured: **72 of 82 section headings name at least one id. The parser finds 0.** Not one heading in the file uses wikilink form.

## Two consequences

**A check that is 100% false-positive.** `Suite.missing_issue_refs()` enforces `TESTING.md`'s rule that a Tier 2 regression test *"references the `ISS-*` that created it"*. It reports **158 of 158** Tier 2 items as violating it. Nothing consumes that method today, which is exactly why nobody noticed — a rule nobody reads cannot be wrong loudly.

**The link that would scope the gate is unreadable.** [[ADR-0028]] routes an obligation by the state of its subject. For an acceptance row, the subject is the feature or issue its section names — and that is written in the document already. All 60 currently-blocking rows resolve to zero refs, so the row → feature link the gate needs does not exist as far as any code can tell.

This is the same shape as [[ISS-0162]], where 48 bare `[[ADR-0011]]`-style citations resolved to nothing: the record said the right thing, in a form the reader did not accept.

## Expected

`_ID_RE` accepts a bare `FEAT-0104` / `ISS-0373` alongside the wikilink form, so a section heading naming its subjects in the ordinary way is read.

Two things to get right rather than assume:

1. **Bare-id matching must not harvest prose.** A section titled *"Handles TASK-0132-style imports"* should not become a ref to a task. Anchor to the id shape and prefer ids appearing in the heading's trailing parenthetical, which is where all 72 of these sit.
2. **`missing_issue_refs` will start reporting a real number, and it may not be zero.** That is the check working. Whatever it reports on first honest run gets recorded rather than treated as a regression introduced here.

## Notes

Landable independently of the rest of [[PHASE-034]], and worth doing before [[FEAT-0102]] — the gate can be built either way, but built first it would be built against a corpus where every row is unattributable, which is the wrong shape to design against.

The upstream question — whether `TESTING.md` should require wikilink form and every suite be rewritten — is deliberately not asked here. Twelve repos write it bare; the reader is what should change.

## Fixed 2026-08-16

`heading_refs()` accepts a bare id **in the trailing parenthetical only**, alongside wikilink form anywhere. The anchor is not a guess: measured across every suite in the fleet, **114 of 114 id-bearing headings put all of theirs there**, and `area` already strips exactly that span for the same reason. So the rule covers everything with no prose-harvesting risk — *"Handles TASK-0132-style imports"* acquires no subject.

**The honest number, as the issue asked.** `missing_issue_refs()` on `your-trainer` goes from **158 of 158 to 73 of 158**: 85 Tier 2 items do reference the issue that created them, and 73 genuinely do not. That is recorded rather than treated as a regression introduced here — it is the check working for the first time. This repo's own suite goes 7 to 0.

**And the property [[FEAT-0102]] needed:** all 60 of `your-trainer`'s blocking rows now name a subject, where 0 did before.

Guards in `tests/test_tests_view.py`, three mutations, each defeated: bare ids unread, the parenthetical anchor removed, and the dedupe removed.
