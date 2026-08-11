---
type: "[[change]]"
id: CHG-20260811-P023
title: "PHASE-023 closes — the keystone phase, with FEAT-0062 cancelled rather than built and its exit criterion reconciled rather than ticked"
status: merged
date: 2026-08-11
owner: user:edwin
related: ["[[PHASE-023-Levers-For-The-Human]]", "[[FEAT-0062-Desk-Resolution-Flows]]", "[[ISS-0126]]", "[[RISK-0005]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[REL-0001-The-Human-Has-Levers]]"]
tags: [change]
---

# PHASE-023 closes

The keystone — six phases depended on it — and the second of [[REL-0001]]'s five to reach `done`. Three of its four features shipped on 2026-08-10; what remained was one feature nobody could build honestly, and the decision about it.

## The decision

Edwin cancelled [[FEAT-0062]] on 2026-08-11, via [[ISS-0126]]. Both verbs it would have built address states that do not occur, on a surface that no longer exists. Re-measured that day:

| | |
|---|---|
| `changes-requested` notes | 10 |
| …whose subject is **not** terminal — the only genuine obligation | **0** |
| review-ledger entries | 8 |
| …of kind `question` | **0** |

`FEAT-0062` and its two tasks are `cancelled`, not deleted: the argument for not building something is the durable part.

**What is not lost.** The dispatch machinery it would have used already exists. The inverse case — a `changes-requested` note whose subject is *not* terminal — is preserved by [[ISS-0121]]'s fix and surfaces in the view owning that note's type, which is where [[ADR-0020]] puts it.

## `declined` → `fixed`, and why the difference matters

ISS-0126 was first set to `declined`, then corrected. `declined` means *deliberate no-action, keep the note* — right if the feature had been left standing. But action was taken: three notes moved to `cancelled`. An issue whose report caused a correction is `fixed`, whatever shape the correction took.

## One criterion reconciled, not ticked

> `- [~]` The changes-requested register can reach zero through the desk alone

The desk was retired by [[ADR-0020]] and removed by [[FEAT-0090]]; the flow that would have satisfied this was cancelled. The register is *already* at zero, and the criterion asks for a route to zero through a surface that no longer exists — so it is reconciled with that reason rather than ticked on a technicality or left blocking a phase whose work is done.

`STATUSES.md` provides `- [~]` for exactly this, and PHASE-BOXES accepts it. Ticking it would have claimed a flow that was never built.

## [[RISK-0005]] closed

Its own condition was *"the hardening suite exists and exercises every refusal by attempting the forbidden thing… so a new endpoint added without the guard fails the suite by existing."* That suite parses the POST dispatch table — **21 routes** today — and [[REL-0001]]'s pass drove 10 of 10 mutation endpoints over the LAN interface `192.168.68.123:8791` for 403s, which is the check the automated test explicitly disclosed it could not make.

It was re-verified today against a new write endpoint (`/api/notes/acceptance-run`, TASK-0289): the enumeration found it and required its guard.

## Exit criteria

Four ticked with evidence, one reconciled. The four name the tests that hold them — the actuator row's vocabulary guard, the agent-owned refusal, quick capture, and the loopback/mtime pair — rather than pointing at prose.
