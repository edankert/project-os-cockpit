---
type: "[[task]]"
id: TASK-0558
aliases: ["TASK-0558"]
title: "Add and remove a feature on a preparing release, from the release page"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
parent: "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# The write path that does not exist

A release note has carried `features: [...]` since [[REL-0001]] and **nothing has ever written it**. Composing a release means editing frontmatter by hand.

## Definition of Done

- [x] `POST /api/notes/release-contents` — `{release, action: add|remove, id}` — editing `features:` line by line with `_set_block_list`, which is already hardened for this shape.
- [x] **Refused on a release that has shipped.** [[ADR-0035]]: a release page reports and does not record, and changing what a shipped release contained rewrites what it was measured against.
- [x] **Refused when the id does not resolve**, and when the feature is already in another **open release on the same platform** — see below, because the obvious version of that rule is wrong.
- [ ] *(client half — [[TASK-0511]])* The release page offers add/remove **and a candidate list**: done-but-unshipped features not claimed by an open release on this platform. Without the candidate list the control is a text box, and a text box for an id is how [[ISS-0142]] happened.
- [ ] *(client half — [[TASK-0511]])* Both front doors ([[ISS-0230]]'s lesson), or the difference is decided and recorded.

## The rule that is easy to get wrong

**A feature in two open releases on the SAME PLATFORM is an error. Across platforms it is the normal case.**

An earlier draft of this said *any* two open releases, which would have been wrong the first time a feature shipped to both — and Edwin's question is what caught it: *"a feature can be (is more than likely) delivered to multiple platforms."* Measured in `your-trainer`: 45 android features, 9 ios, 25 cross-platform, and the iOS ones are the *porting work* rather than twins. See [[ISS-0236]] for why `platform:` on the feature is the wrong place to answer this from.

## Done 2026-08-20 — the server half

`note_writes.release_contents(index, release, action=, feature_id=)` behind `POST /api/notes/release-contents`, loopback-only like every other write path. Eight tests on constructed fixtures — **no repo composes a release yet, so the corpus cannot exercise any of it** — and three mutants run, one per refusal.

**The client half is [[TASK-0511]]**: the picker, the candidate list, and the both-front-doors question. Splitting them here rather than half-building the UI is deliberate; the two DoD lines that belong to it are marked.

### `_set_field(quote=False)`, not `_set_block_list`

The task names `_set_block_list`, *"already hardened for this shape"*. It is not: it writes a YAML **list of maps**, and `features:` is a flat inline list of wikilinks. The helper that is hardened for this shape is `_set_field(..., quote=False)` — quoting an inline list turns it into one string that parses back as a single value, which is [[FEAT-0107]]/[[TASK-0445]]'s defect where a release reported nothing it had verified. Asserted directly: the written line must be `features: ["[[FEAT-0001-Thing]]"]`.

Second task in a row whose named helper or rule was wrong — [[TASK-0512]] pointed at `blocking_for`, the reading [[ADR-0040]] rejected. Both were written before the thing they point at settled.

### The rule that is easy to get wrong, and the mutant that proves it

**A feature in two open releases on the same platform is refused. Across platforms it is the normal case.** Dropping the `platform` comparison — the *any two open releases* rule an earlier draft carried — fails `test_across_platforms_it_is_the_normal_case`. That would have been wrong the first time a feature shipped to both, and Edwin's question is what caught it in the note: *"a feature can be (is more than likely) delivered to multiple platforms."*

Platform is read from the **release**, never the feature — [[ISS-0236]] is why: `platform:` on a feature is a scalar for a three-tuple and cannot answer this.

### The id is the member; the slug is display

`[[FEAT-0001-Thing]]` and a bare `FEAT-0001` name one feature, so membership compares on the id. A remove that matched the full wikilink would silently no-op against `[[FEAT-0001]]`, which is what eleven historical releases actually contain.

## Independent review — third pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`, reviewing `6cc7f72..HEAD`. Verdict: **approved**. Every claim below was re-measured or re-executed.

All three refusals are genuinely guarded. Five mutants executed, every one caught by a named test:

| mutation | caught by |
|---|---|
| a shipped release becomes mutable | `test_a_shipped_release_is_immutable` |
| the platform comparison dropped from the clash check | `test_across_platforms_it_is_the_normal_case` |
| a phase naming nothing that resolves is accepted | `test_a_phase_naming_nothing_that_resolves_is_refused` |
| the same-platform clash check neutered | `test_the_same_feature_in_two_open_releases_on_one_platform_is_refused`, `test_a_phase_clash_names_the_feature_not_the_phase` |
| a phase stored instead of contributing its features | three tests |

The third refusal is the one the note flags as easy to get wrong, and the per-contributed-feature check — refusing on the member that clashes rather than on the phase id — is asserted rather than described. Overriding `_set_block_list` in favour of the wikilink-list helper is right: quoting the list turns it into one string, which is the `FEAT-0107`/`TASK-0445` defect the note cites.
