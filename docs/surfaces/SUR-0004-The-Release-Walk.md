---
type: "[[surface]]"
id: SUR-0004
aliases: ["SUR-0004"]
title: "The release test"
status: active
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
kind: screen
platforms: []
parent: ""
gallery: []
related: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
tags: [surface]
---

# The release test

One platform's release test, in the Tests view ([[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]). It was the walk page until 2026-09-27; `~walk` and `~walk/<platform>` still open it.

- **In the Tests pane**, "Release test · <version>" sits after Needs you, with one row per platform and its sections under it. Each row carries a done/total count and a thin bar, and each section a dot: empty, half, full, or red when a result there needs the owner.
- **The platform overview**, `~release-test/<platform>`: "Test <version> on <platform>", a bar split by result, Continue where you stopped, Needs you (Fail, Question, Blocked and Partial results, and declared readiness problems), the sections with their bench lines, and the changed screens no section tests.
- **A section**, `~release-test/<platform>/<section>`: what changed on its screens with before and after pictures, Setup folded into On the bench, Before you start and Later, then its checks in groups, numbered from 1, each one action and one expected line with its tag. Pass and Fail are one tap; More offers Partial, Question, Blocked, N/A and Excused; every result but Pass needs a reason.

The page decides nothing about what is owed or how a section is laid out: that is upstream's generator, bundled as `release_test_bundled.py`, served by `/api/cockpit/release-test`. A result is kept in the browser per printed check; when every printed check of one test note has a result, one ledger event is written for that note through `postCheckVerdict`, the most serious result winning.
