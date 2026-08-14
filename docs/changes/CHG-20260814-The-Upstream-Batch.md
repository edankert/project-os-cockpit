---
type: "[[change]]"
id: CHG-20260814-The-Upstream-Batch
title: "The upstream batch, the palette's blind spot, and 54 citations that pointed nowhere"
status: merged
owner: user:edwin
created: 2026-08-14
updated: 2026-08-14
source: ["Edwin 2026-08-14: 'one upstream visit to ~/Dev/repos/project-os/ batching all four, rewrite iss-0124 as suggested. Fix ISS-0142 as suggested. ISS-0127 let's close it but do not record a decision. ISS-0162 fix fully as suggested do the full sweep.'"]
commit: ""
pr: ""
impacts: ["two new validator warnings, fleet-wide", "releases are findable by name", "every upstream citation resolves", "the template stops shipping three workflow stubs"]
issues: ["[[ISS-0155]]", "[[ISS-0163]]", "[[ISS-0124-Four-Note-Types-Have-No-Status-Table]]", "[[ISS-0147]]", "[[ISS-0142-The-Release-Note-Cannot-Be-Found-By-Name]]", "[[ISS-0162-The-Bare-Upstream-Citations-Still-Resolve-To-Nothing]]", "[[ISS-0164-Phases-Are-The-Second-Type-The-Palette-Cannot-Find]]"]
features: []
reviewed_by: model:claude-opus-5
review_date: 2026-08-14
review_verdict: changes-requested
related: ["[[ADR-0024]]", "[[project-os-dev#ADR-0011]]", "[[PHASE-026-The-Returning-Human]]"]
---

# The upstream batch, the palette's blind spot, and 54 citations that pointed nowhere

## Summary

Seven issues closed, one filed, across two repos. Four could only be fixed upstream; three were this repo's.

## Upstream — `project-os` `0a44cdd`

`tools/scripts/validate-docs.py` is template-owned and `test_bundled_validator_matches_the_canonical_one` asserts the bundled copy is verbatim, so **half this repo's open backlog was unfixable here by construction.** One visit closed all four. Full reasoning in that repo's `CHG-20260814-Four-Gaps-The-Record-Could-Not-See`.

- **[[ISS-0155]]** — a `ready` manual test no longer needs a verification date. A **restoration**: added upstream 2026-08-01 (`5a487ad`), removed **three days later** on 2026-08-04 (`59bd47c`) by a whole-file overwrite, exactly as that commit's message predicted it would be.
- **[[ISS-0163]]** — `TEST-ENTRYPOINT`, new. **43 findings across five repos**; this one reads 0 because [[ISS-0130]] fixed its 22 notes the day before.
- **[[ISS-0124]]** — `STATUS-TYPE`, new, after being rewritten to what was actually left (two types, not four — two of the original four had resolved themselves).
- **[[ISS-0147]]** — the template stops shipping `WF-0001..0003`.

**The sync down was a patch, not a copy.** A file copy would have destroyed this repo's own gates — `PARENT-BACKLINK`, `SNAPSHOT-MEMBERSHIP`, `DESIGN-GATE` and `ACCEPT-STALE`, 149 lines of them. That is the same whole-file overwrite that lost ISS-0155's fix in the first place, and it was one command away from happening again in the opposite direction.

## Here

- **[[ISS-0142]]** — releases are findable. One entry in the `intent` view's group loop, because the quick corpus is built *from* nav modes: navigable and findable in one line, inheriting the filters a third `buildQuickCorpus` patch would have restated.
- **[[ISS-0162]]** — **53 citations rewritten across 41 files**, prose and frontmatter, plus the `CONTEXT.md` sentence naming the namespace. Scope was well over twice what the note claimed: five upstream ids, not two.
- **[[ISS-0127]]** — declined. No non-goals note.

## What the work found that nobody asked for

**[[ISS-0164]]**, filed: **phases are a second type the palette cannot find** — 34 notes (independently re-measured as exact), and ISS-0142's title had called releases *"the one note type"* it had never carried. That claim was measured by hand, one type at a time, which is how the bug was found in the first place. The per-type guard now measures all types in one pass and requires any zero to be **named with a reason**; a third instance cannot arrive quietly.

Also found: eight occurrences across [[ISS-0148]], [[FEAT-0093]], [[CHG-20260812]], `CONTEXT.md` and [[ISS-0162]] itself **quote** the bare citation form to explain what it means or why the slash lost. `FEAT-0093`'s acceptance criterion is literally *"`[[ADR-0011]]` with no prefix keeps its current meaning exactly"* — a naive sweep would have made it assert the opposite of what it verifies.

## Behaviour that changed

- Two new validator **warnings** fleet-wide, both dated to promote on 2026-11-12.
- **One repo's verdict changes, and it improves.** `your-health` goes **FAIL (2 errors) → OK**: two `ready` manual tests with no `last_verified` that the restored exemption clears. The original claim here read "no repo's verdict changes", checked only for repos that *started* failing, and so could not see one that stopped.
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

## Independent review — 2026-08-14, `changes-requested`

Fresh context, separate session, never saw the authoring reasoning; same model family as the author (`model:claude-opus-5`, recorded in `reviewed_by` per [[project-os-dev#ADR-0013]]). **The code is right and nothing here asks for a revert.** Every Evidence row reproduces, both new checks were re-measured independently and hit their stated figures exactly, and all three local guards fail under mutation. What is requested are corrections to the record — which is what this note is.

**Finding 1 — *"No repo's verdict changes"* is false, and the check behind it only looked one way.** Ran all twelve fleet repos against `0a44cdd` and against `HEAD~1` of the same file. `your-health` goes **FAIL (2 errors) → OK**: `TST-0012` and `TST-0013` are `status: ready`, `kind: manual`, `last_verified: ""`, and the restored exemption clears both. The evidence offered — *"`your-trainer`'s single error is `DEFER-RETENTION`, identical with the unmodified validator"* — is true and confirms only that no repo *started* failing. It cannot see a repo that stopped, and one did. The change is a repair, and the note gives it away by claiming nothing happened.

**Finding 2 — the list of gates the patch protected is wrong on two of four, and omits the two that were actually at risk.** `DECISION-RULE` has **never existed in this repo** — 0 occurrences at `HEAD` and at `HEAD~1`, in both `tools/scripts/validate-docs.py` and the bundled copy. It is upstream-only (`validate_decision_rule`, called at upstream `validate-docs.py:1616`), so a file copy would have **added** it, not destroyed it. `DECISION-OPTIONS` is byte-identical upstream, so a copy would have preserved it. The genuinely local checks a copy would have destroyed are `PARENT-BACKLINK`, `SNAPSHOT-MEMBERSHIP` and — unnamed here — **`DESIGN-GATE`** ([[FEAT-0070]]) and **`ACCEPT-STALE`** ([[FEAT-0064]]). Measured local-only content: **149 lines** in two blocks, not 146. The paragraph's conclusion holds; its evidence does not. Corollary worth its own line: because the sync is a patch, this repo's validator is **148 lines behind upstream** — the 147-line `validate_decision_rule` block and its call site — and carries no `DECISION-RULE`. No live impact (no `## Rule` ADR here), but the note asserts the opposite of the actual state.

**Finding 3 — both new checks are undated warnings, which is the one thing [[project-os-dev#ADR-0011]] forbids.** That ADR's decision reads: *"`warn` survives only as a dated migration state: a warning must name the cutover date at which it becomes an error, that date must be encoded in the code … A check with no cutover is promoted or deleted."* `TEST-ENTRYPOINT` and `STATUS-TYPE` both call `report.warn` directly, neither appears in `PROMOTIONS` (`validate-docs.py:620`, which carries only `REVIEW` and `PLAN-STATE`), and neither message carries a date. The comment above the emit says *"A warning with a promotion date, per ADR-0011"* (`tools/scripts/validate-docs.py:1700`, and identically in the bundled copy) — it asserts the missing property in so many words. [[ISS-0163]] closes on the same claim: *"of the ADR-0011 shape — a warning with a date"*. Either wire a cutover ≤90 days out into `PROMOTIONS`, or stop citing the ADR.

**Finding 4 — *"three weeks later"* is three days.** `5a487ad` is 2026-08-01; `59bd47c` is 2026-08-04. Confirmed with `git log -S` — those two and `0a44cdd` are the only commits that ever touched the exemption. Everything else about the restoration verifies exactly: mutation-checked, a `ready` manual test with no `last_verified` errors under the previous validator and does not under this one, and a `passing` one with no `last_verified` still errors under both. The error is repeated in this repo's commit message, in the upstream commit message, and in the restored code comment.

**Finding 5 — the counts in the sweep are not reproducible as stated.** Measured across `docs/**` + root `*.md`, templates excluded: **59** bare `[[ADR-00nn]]` occurrences of the five upstream ids across **43** files before, **53 rewritten across 41 files** (39 files lost all of theirs; `ISS-0148` and `CHG-20260812` were partially reduced), not *"54 across 38"*. *"Six upstream ids"* is five — [[ISS-0162]]'s own table names `ADR-0011/0012/0013/0014/0019` under a heading of 6 and then reports 5 swept; the sixth appears to be `ADR-9999`, which is a deliberately dangling id rather than an upstream one, so the *"three times what the note claimed"* framing rests on it. This matters more than the arithmetic because that note already carries a **Correction** section for exactly this failure.

**Finding 6 — *"four occurrences deliberately left bare"* names a file that has none and misses two that do.** [[ADR-0024]] contains **zero** bare `[[ADR-00nn]]` wikilinks: it quotes `[[NOTE-ID]]` generically and writes `ADR-0011` unbracketed. The bare occurrences that survive are `ISS-0148` (2), `FEAT-0093` (1), `CHG-20260812` (1), plus `CONTEXT.md` (1) and `ISS-0162` (3) — eight, every one inside inline code, every one equally deliberate. **The substantive claim is true and was the thing worth checking**: no bare upstream citation remains outside inline code anywhere in `docs/` or the root, and all four notes that explain the syntax read correctly. `FEAT-0093`'s criterion is intact and was never at risk — the file is not in the commit at all.

**Finding 7 — this note's own `status: draft` is outside its type's vocabulary, and it is the defect class [[ISS-0124]] just closed, one step over.** `STATUSES.md` allows `merged` and `reverted` for `[[change]]`; `validate-docs.py:93` encodes the same set. Nothing checks it: `CHG` is not in `ID_PREFIXES` (`validate-docs.py:60`), so change notes never enter `note_index`. `STATUS-TYPE` does not catch it either — it reports a type with *no* table, and `change` has one. Four change notes now read `draft` against 135 `merged`. This has teeth: stamping an honest `changes-requested` on a `draft` change note makes `_verdict_is_owed` true forever, and `tests/test_tests_view.py:1383` asserts the live corpus contains **zero** owed re-reviews. At committed `90a74cb` that holds (107 register rows, 0 owed) — the suite failure seen today is two concurrent review sessions' uncommitted stamps, not this commit. But the third stamp is this one, and the guard punishes the honest verdict rather than the condition.

**Not defects, recorded so the next reader does not re-derive them.** `TEST-ENTRYPOINT` **43 across five repos** and `STATUS-TYPE` **4 across three** both reproduce exactly, per-repo, against [[ISS-0163]]'s table. The bundled copy is byte-identical to the canonical one (`md5 220698184273849baac17f3b531d723e`) and the two new checks were transplanted verbatim. `REL-0001` is reachable in the `intent` payload in its own **Releases** group, and the per-type sweep independently confirms **phase 34/0** — [[ISS-0164]]'s headline figure is exact. All three local guards fail under mutation. `validate-docs.sh` is `OK`. One caveat on the new palette guard: it triggers only on a whole type reading zero, so a *partial* gap stays quiet — 13 `reference` ids are unreachable today (the `docs/*/README.md` signposts and `STYLEGUIDE`), which is harmless but means *"a third instance cannot arrive quietly"* holds for whole types only. Finally, the follow-up saying this change *"still owe[s] the independent review pass `QUALITY.md` asks for"* is at odds with this repo's own [[ADR-0023]], which retired that obligation for `CHG-*` notes and says reviewing one *"remains possible and is never wrong; it stops being owed"*.
