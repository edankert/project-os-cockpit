---
type: "[[task]]"
id: TASK-0558
aliases: ["TASK-0558"]
title: "Add and remove a feature on a preparing release, from the release page"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# The write path that does not exist

A release note has carried `features: [...]` since [[REL-0001]] and **nothing has ever written it**. Composing a release means editing frontmatter by hand.

## Definition of Done

- [ ] `POST /api/notes/release-contents` — `{release, action: add|remove, id}` — editing `features:` line by line with `_set_block_list`, which is already hardened for this shape.
- [ ] **Refused on a release that has shipped.** [[ADR-0035]]: a release page reports and does not record, and changing what a shipped release contained rewrites what it was measured against.
- [ ] **Refused when the id does not resolve**, and when the feature is already in another **open release on the same platform** — see below, because the obvious version of that rule is wrong.
- [ ] The release page offers add/remove **and a candidate list**: done-but-unshipped features not claimed by an open release on this platform. Without the candidate list the control is a text box, and a text box for an id is how [[ISS-0142]] happened.
- [ ] Both front doors ([[ISS-0230]]'s lesson), or the difference is decided and recorded.

## The rule that is easy to get wrong

**A feature in two open releases on the SAME PLATFORM is an error. Across platforms it is the normal case.**

An earlier draft of this said *any* two open releases, which would have been wrong the first time a feature shipped to both — and Edwin's question is what caught it: *"a feature can be (is more than likely) delivered to multiple platforms."* Measured in `your-trainer`: 45 android features, 9 ios, 25 cross-platform, and the iOS ones are the *porting work* rather than twins. See [[ISS-0236]] for why `platform:` on the feature is the wrong place to answer this from.
