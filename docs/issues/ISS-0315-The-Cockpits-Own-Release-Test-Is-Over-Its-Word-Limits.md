---
type: "[[issue]]"
id: ISS-0315
aliases: ["ISS-0315"]
title: "The cockpit's own macOS release test is over its word limits, because its three owed checks have no procedure and no Expect lines"
status: open
phase: []
owner: unassigned
created: 2026-09-27
updated: 2026-09-27
source: ["The template's length check became an error on 2026-09-27 (project-os-dev TASK-0196), and this repository's release test was the one consumer that failed it"]
reported_by: agent
question: ""
severity: low
component: "tests"
parent: ""
related: ["[[TST-0083-A-Release-Is-Prepared-Without-An-Editor]]", "[[TST-0086-A-Note-Shows-The-Pictures-Beside-It]]", "[[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]", "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"]
tests: ["[[TST-0083]]", "[[TST-0086]]", "[[TST-0087]]"]
---

# The cockpit's own release test is over its word limits

## Problem

When the cockpit's next macOS release is tested, two of its sections print far more text than the release test allows. "The server, in a browser" prints 809 words against a budget of 380, and "Across the fleet" prints 487 against 340. TST-0087's title, which prints as its action, is 23 words.

The cause is the checks' older format. TST-0083, TST-0086 and TST-0087 have a `## Procedure` of prose with the expected results in bold, and no `## Steps` or `## Expect`. With no procedure for the section, each check prints in full.

Until this is fixed, `docs/tests/acceptance/RELEASE-TEST.md` sets `length_limits: {error: false}`, so the length check warns here instead of failing validation. The template's default is an error.

## Expected

Each of the three checks has numbered `## Steps` and one short `## Expect` line per step. The two sections have a procedure in the shape of your-trainer's (`tools/skills/release-test-procedure/SKILL.md`). The `length_limits` override is removed.

## When

At the cockpit's next release preparation. `tools/skills/release-test-prep/SKILL.md` does exactly this. The checks are rewritten when they are next tested ("Existing checks are rewritten on contact, never swept", `tools/instructions/TESTING.md`).
