---
type: "[[issue]]"
id: ISS-0078
aliases: ["ISS-0078"]
title: "PHASE-003's downstream pilot was overtaken by workspace discovery and never built, while CLAUDE.md still tells every session the shim exists"
status: fixed
severity: medium
phase: "[[PHASE-015-Phase-Hygiene]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30: 'can you review PHASE-003 and suggest if this still needed, I think it can be closed without implementation'"]
component: docs-system
related: ["[[PHASE-003-Downstream-Pilot]]", "[[FEAT-0005-Downstream-Pilot]]", "[[PHASE-005-Desktop-Shell]]"]
fixed_by: ["[[PHASE-015-Phase-Hygiene]]"]
tests: []
---

# The pilot was overtaken, and the instructions still claim it shipped

## What PHASE-003 was for

Two things in one phase: **validate the cross-repo invocation pattern** by building a thin shim in `your-applications.com/tools/project-os-cockpit/`, and **read the docs on a tablet** over Wi-Fi.

## The pattern was validated by something better

[[FEAT-0007]] / [[PHASE-005]] gave the desktop shell workspace discovery: it finds every `SNAPSHOT.yaml`-bearing repo — **12 on this machine** — and spawns a sidecar per workspace. [[FEAT-0028]] validated all twelve in one pass on 2026-07-30.

So the pattern is not "proven by one pilot"; it is in daily use across the fleet, by a mechanism that did not exist when this phase was written.

And the shim is now near-worthless. Its whole job is `python -m project_os_cockpit docs`, one command — run by hand against three repos while closing [[TASK-0231]] the same day.

## Three things that confirm it was never live

- **The shim exists in no fleet repo.** Never built.
- **`ADR-0003`, which the phase says must be authored before it ships, was never written — and its number was taken** by "Visual style direction". The decision this phase gates on cannot now be filed under that ID.
- **[[FEAT-0005]] has no outstanding work of its own.** Its only task ([[TASK-0020]]) is `done` and its only requirement ([[REQ-0017]]) is `implemented`, and **both belong to [[PHASE-002]]**. TASK-0020's real subject is the upstream *release* mechanism, not the downstream shim.

## The falsehood in the instructions

`CLAUDE.md` line 10:

> The first downstream pilot is `~/Dev/repos/your-applications.com/` — that repo's `tools/project-os-cockpit/` is the integration point used to validate this tool against real project-os content.

That directory has never existed. This is the project's primary instruction file, read at the start of every session, and it has been pointing agents at an integration point that is not there.

## The tablet question — settled

The phase's other half was tablet reading, and it is **not** served by the app: desktop-spawned sidecars bind `127.0.0.1`, and only standalone mode 1 binds `0.0.0.0`.

**Edwin, 2026-07-30: no tablet.** Settled rather than dropped, so closing the phase loses nothing.

## Expected

The phase and its feature carry statuses that say what happened — overtaken, not delivered — and `CLAUDE.md` describes something that exists.

## Next Actions

- [x] `PHASE-003` → `superseded` by [[PHASE-005]], the mechanism that replaced it
- [x] `FEAT-0005` → `cancelled`, not `done` — it never shipped
- [x] Correct `CLAUDE.md`'s downstream-pilot paragraph


## Fixed 2026-07-30

- **[[PHASE-003]] → `superseded`**, `superseded_by: [[PHASE-005]]`. Not `done`: nothing was built. Each exit criterion is answered in the note — the shim (never needed), the tablet (settled: no), and the adoption criterion (met by a different route, since a repo is adopted by *existing*).
- **[[FEAT-0005]] → `cancelled`**, with why it read as pending for three months while having nothing to do: its only task and only requirement are finished and belong to [[PHASE-002]], and [[TASK-0020]]'s real subject is the upstream *release* mechanism rather than the downstream shim.

### The falsehood was in five files, not one

`CLAUDE.md` was where Edwin saw it, and a sweep found the same claim in four more:

| file | said |
|---|---|
| `CLAUDE.md` | the pilot integration point is `your-applications.com/tools/project-os-cockpit/` |
| `LLM_BRIEF.md` | downstream repos "consume through a thin shim under their own `tools/project-os-cockpit/`" |
| `docs/ARCHITECTURE.md` | the deployment shape *is* a per-repo shim |
| `docs/GLOSSARY.md` | a downstream consumer runs the cockpit "via a shim under its `tools/project-os-cockpit/`" |
| `docs/PHASES.md` | PHASE-003 `planned`, deploy under that path |

All five now describe **discovery**: the shell finds every `SNAPSHOT.yaml`-bearing repo and hosts a server per workspace, and nothing is installed into a consumed repo. `CLAUDE.md` and the three prose files carry a dated correction rather than a silent edit, so a reader can see the claim changed.

**Left alone deliberately:** [[PHASE-003]] and [[FEAT-0005]] themselves, and `CHG-20260507-Rename-To-Project-Os-Cockpit`. Those are the record of what was planned; rewriting them would be the fabrication the supersede exists to avoid.

### Worth carrying

Two of these files — `CLAUDE.md` and `LLM_BRIEF.md` — exist **specifically to tell an agent what this project is**, and both had been describing an integration that never existed. Neither the validator nor any guard can catch that: prose about a directory is not a link, and `BRIEF-PLACEHOLDER` only checks for unfilled template text.

The plan changed in [[PHASE-005]] and the documents describing the plan were never revisited. That is the same shape as [[ISS-0074]] (a phase field nobody re-asked at close-out) and [[ISS-0077]] (a granularity nobody counted) — a value that was true when written and that nothing ever re-checks.


### My own guard caught a case it had modelled wrong

Superseding PHASE-003 failed `test_no_terminal_phase_names_a_superseded_phase`, written hours earlier for the PHASE-016 merge. It banned **every** terminal note from naming a superseded phase.

That is right for a **merge** and wrong for an **abandonment**. PHASE-016 absorbed three phases, so their delivered work had a new home. PHASE-003 was *overtaken*, and [[FEAT-0005]] was cancelled alongside it — re-homing that feature to [[PHASE-005]] would assert the desktop shell delivered the downstream pilot, which nothing did.

The property is narrower than the first version claimed: **delivered work must name the phase that delivered it.** Work abandoned with its phase stays there, because that is where it was abandoned.

Split into two guards, both mutation-verified — one that a `done`-band note may not name a superseded phase, and one that FEAT-0005 stays where it is, so the rule cannot quietly widen back.

A test-code bug surfaced on the way: a walrus in a dict-comprehension **key** is bound after the value expression evaluates, so the first cut raised `UnboundLocalError`. The corpus was right throughout.
