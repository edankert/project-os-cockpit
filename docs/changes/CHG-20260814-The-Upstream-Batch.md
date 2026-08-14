---
type: "[[change]]"
id: CHG-20260814-The-Upstream-Batch
title: "The upstream batch, the palette's blind spot, and 54 citations that pointed nowhere"
status: draft
owner: user:edwin
created: 2026-08-14
updated: 2026-08-14
source: ["Edwin 2026-08-14: 'one upstream visit to ~/Dev/repos/project-os/ batching all four, rewrite iss-0124 as suggested. Fix ISS-0142 as suggested. ISS-0127 let's close it but do not record a decision. ISS-0162 fix fully as suggested do the full sweep.'"]
commit: ""
pr: ""
impacts: ["two new validator warnings, fleet-wide", "releases are findable by name", "every upstream citation resolves", "the template stops shipping three workflow stubs"]
issues: ["[[ISS-0155]]", "[[ISS-0163]]", "[[ISS-0124-Four-Note-Types-Have-No-Status-Table]]", "[[ISS-0147]]", "[[ISS-0142-The-Release-Note-Cannot-Be-Found-By-Name]]", "[[ISS-0162-The-Bare-Upstream-Citations-Still-Resolve-To-Nothing]]", "[[ISS-0164-Phases-Are-The-Second-Type-The-Palette-Cannot-Find]]"]
features: []
related: ["[[ADR-0024]]", "[[project-os-dev#ADR-0011]]", "[[PHASE-026-The-Returning-Human]]"]
---

# The upstream batch, the palette's blind spot, and 54 citations that pointed nowhere

## Summary

Seven issues closed, one filed, across two repos. Four could only be fixed upstream; three were this repo's.

## Upstream — `project-os` `0a44cdd`

`tools/scripts/validate-docs.py` is template-owned and `test_bundled_validator_matches_the_canonical_one` asserts the bundled copy is verbatim, so **half this repo's open backlog was unfixable here by construction.** One visit closed all four. Full reasoning in that repo's `CHG-20260814-Four-Gaps-The-Record-Could-Not-See`.

- **[[ISS-0155]]** — a `ready` manual test no longer needs a verification date. A **restoration**: added upstream 2026-08-01, removed three weeks later by a whole-file overwrite, exactly as that commit's message predicted it would be.
- **[[ISS-0163]]** — `TEST-ENTRYPOINT`, new. **43 findings across five repos**; this one reads 0 because [[ISS-0130]] fixed its 22 notes the day before.
- **[[ISS-0124]]** — `STATUS-TYPE`, new, after being rewritten to what was actually left (two types, not four — two of the original four had resolved themselves).
- **[[ISS-0147]]** — the template stops shipping `WF-0001..0003`.

**The sync down was a patch, not a copy.** A file copy would have destroyed this repo's own gates — `PARENT-BACKLINK`, `SNAPSHOT-MEMBERSHIP`, `DECISION-OPTIONS`, `DECISION-RULE`, 146 lines of them. That is the same whole-file overwrite that lost ISS-0155's fix in the first place, and it was one command away from happening again in the opposite direction.

## Here

- **[[ISS-0142]]** — releases are findable. One entry in the `intent` view's group loop, because the quick corpus is built *from* nav modes: navigable and findable in one line, inheriting the filters a third `buildQuickCorpus` patch would have restated.
- **[[ISS-0162]]** — **54 citations rewritten across 38 files**, prose and frontmatter, plus the `CONTEXT.md` sentence naming the namespace. Scope was **three times** what the note claimed: six upstream ids, not two.
- **[[ISS-0127]]** — declined. No non-goals note.

## What the work found that nobody asked for

**[[ISS-0164]]**, filed: **phases are a second type the palette cannot find** — 34 notes, and ISS-0142's title had called releases *"the one note type"* it had never carried. That claim was measured by hand, one type at a time, which is how the bug was found in the first place. The per-type guard now measures all types in one pass and requires any zero to be **named with a reason**; a third instance cannot arrive quietly.

Also found: four occurrences in [[ADR-0024]], [[ISS-0148]], [[FEAT-0093]] and [[CHG-20260812]] **quote** the bare citation form to explain what it means or why the slash lost. `FEAT-0093`'s acceptance criterion is literally *"`[[ADR-0011]]` with no prefix keeps its current meaning exactly"* — a naive sweep would have made it assert the opposite of what it verifies.

## Behaviour that changed

- Two new validator **warnings** fleet-wide. No repo's verdict changes: `your-trainer`'s single error is `DEFER-RETENTION`, identical with the unmodified validator.
- `REL-0001` is findable by name and appears under **Releases** on the Intent view.
- Every upstream ADR citation resolves and is clickable across the fleet.
- Nothing about what may write, what may push, or what is refused.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: not-applicable
- issues: 7 fixed/declined, 1 new ([[ISS-0164]])
- tests: not-applicable
- workflows: not-applicable
- decisions: not-applicable — [[ADR-0024]] and [[project-os-dev#ADR-0011]] already decided the shapes used
- risks: not-applicable
- changes: new
- snapshot: updated

## Evidence

| guard | mutation | result |
|---|---|---|
| `test_every_id_bearing_type_is_findable_in_the_palette` | the `releases` group is removed again | fails |
| `test_no_bare_citation_names_an_upstream_decision` | any ADR id with no local note, written bare | fails |
| `test_a_standing_document_names_the_upstream_namespace` | CONTEXT.md loses the sentence | fails |
| upstream `ready` exemption | note flipped to `passing` | errors, as before |
| upstream `TEST-ENTRYPOINT` | `passing` + `kind: automated` + no `command:` | fires |
| upstream `STATUS-TYPE` | an unknown type; a status-free type gaining a status | fires both |

## Follow-ups

- [ ] [[ISS-0164]] — phases in the palette, if 34 rows are worth their space.
- [ ] The 43 `TEST-ENTRYPOINT` findings are each repo's to answer.
- [ ] [[FEAT-0100]] and this change still owe the independent review pass `QUALITY.md` asks for.
