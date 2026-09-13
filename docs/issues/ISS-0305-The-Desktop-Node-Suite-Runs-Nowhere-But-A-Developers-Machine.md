---
type: "[[issue]]"
id: ISS-0305
aliases: ["ISS-0305"]
title: "The desktop's node suite runs nowhere but a developer's machine: it needs a build CI never makes, so it skips instead of failing"
status: triage
severity: medium
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
source: ["Independent review of PHASE-043, 2026-09-13, finding 6"]
area: "Verification health and the fleet"
component: "tests/test_desktop_node_suite.py"
severity_note: ""
affects: ["[[FEAT-0149-The-Walk-Page]]"]
related: ["[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]"]
tags: [issue, testing, ci]
---

# The desktop's node suite runs nowhere but a developer's machine

## What happens

`desktop/tests/*.test.mjs` is the only place in this repo where renderer behaviour is executed rather than read as source text. Seven files now, twenty-three of the tests added by [[FEAT-0149-The-Walk-Page]] among them.

They run from `tests/test_desktop_node_suite.py`, which **skips** when `desktop/dist/ipc/fleet-health.js` is absent — and `desktop/dist/` is gitignored and no workflow builds it. So on CI the wrapper skips, and the twenty-three tests that hold the walk page's behaviour report as six skipped tests rather than as anything at all.

## Why it matters

It is the difference between a guard and a habit. The suite passes here because the author ran `npm run build` before `pytest`; nobody else's run of the same commit executes a line of it. A renderer change that breaks the walk page, made by a session that does not build the desktop, is green all the way to `--as-committed`.

It is not new and it is not this feature's — it has been true since the node suite was written ([[FEAT-0028]] / TASK-0248) and every desktop guard added since inherits it. It is filed now because [[FEAT-0149-The-Walk-Page]] put its strongest assertions there, so the gap stopped being theoretical.

## Where it is

```
grep -n "BUILT\|pytest.skip" tests/test_desktop_node_suite.py
cat .github/workflows/*.yml | grep -n "npm\|node"
```

## What a fix looks like

The CI step set builds the desktop (`npm --prefix desktop ci && npm --prefix desktop run build`) before the Python suite, and the wrapper stops skipping when the build is absent — a missing build on CI is then a failure rather than a silent pass. The cost is a node install in the workflow, which is the real decision here: it is not free, and this repo's CI has been Python-only on purpose.

The cheaper half, worth doing either way: the wrapper should say how many test files it skipped, so a run that executed none of them does not look like a run that had none to execute.

## Owner

Edwin decides whether CI grows a node build. Until it does, a renderer change is verified by the session that makes it, and the node suite is a local gate.
