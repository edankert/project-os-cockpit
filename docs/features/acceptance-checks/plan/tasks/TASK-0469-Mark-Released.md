---
type: "[[task]]"
id: TASK-0469
aliases: ["TASK-0469"]
title: "Mark released — the missing end of the process, behind two refusals, printing the git commands it will not run"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0116-A-Release-Can-Be-Finished]]"]
parent: "[[FEAT-0116-A-Release-Can-Be-Finished]]"
effort: M
depends: ["[[TASK-0468-The-Considered-Obligation]]"]
blocks: []
related: ["[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]]"]
tests: []
---

# Mark released

`HUMAN_TRANSITIONS` gains its `release` key — the review measured that it has none, which is why nothing anywhere can take a release from `draft` to `released` ([[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]] item 4). One control beside the gate summary writes `status: released`, `date:`, `tag: v<version>`, and **freezes the derived feature list into `features:`** — without which REL-0013 ships reading "What shipped — 0 feature(s)".

Two refusals, both naming their subjects: the gate is blocked and the note records no exceptions; or a feature being frozen lacks `acceptance_impact` — the refusal lists the features. This is where Edwin's *"whether all acceptance tests have been considered"* is enforced, at the one moment it is both cheap and final.

It prints `git tag -a v<version> …` and `git push origin v<version>` and runs neither — publishing stays a person's act.

## Done when

- [ ] A release can travel Name-the-version → walked → Mark released entirely in the cockpit, and the note afterwards carries status, date, tag and the frozen list.
- [ ] Both refusals fire with their subjects named; neither can be clicked through.
- [ ] Nothing runs git; the commands are shown.
