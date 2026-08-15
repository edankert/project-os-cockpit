---
type: "[[issue]]"
id: ISS-0170
aliases: ["ISS-0170"]
title: "TASK-0419's 'no new subprocess per repo' box was ticked with evidence saying the cold digest 'spawns nothing' — it spawns git, and the module's own docstring says so ten lines above the call"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-15
updated: "2026-08-15"
source: ["Independent review of [[FEAT-0100]] returning to `done`, 2026-08-15: checking each of the 27 close-out-ticked DoD boxes against the delivered system."]
severity: low
component: fleet
parent: ""
related: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[TASK-0419-Every-Card-Is-A-Full-Card]]", "[[PHASE-030-Obligations-Go-Home]]"]
tests: []
---

# A ticked box says the cold digest spawns nothing, and it spawns git

## The box

[[TASK-0419]], ticked at [[PHASE-030]]'s close-out on 2026-08-14:

> - [x] No new subprocess per repo: this rides the batch that already runs, and its added cost is bounded by the same timeout. — evidence: `_digest_counts` is called inside `summarise()`, in-process; it builds an index and calls `digest_payload` directly and **spawns nothing**

## What the code does

`_digest_counts` (`src/project_os_cockpit/fleet_validate.py:69`) calls `cockpit.digest_payload`, which calls `history_payload` (`src/project_os_cockpit/cockpit.py:5442`), which runs `subprocess.run(["git", …])` at `cockpit.py:5531` and again reads publication state through `git_state.read`, itself a git walk. So the cold pass spawns **several** git processes per repo, not none.

The function's own docstring says it, at `fleet_validate.py:80`:

> This rides the batch that already runs rather than adding a process per repo. **It costs one index build and one `git log` per repo per cold pass**, beside the validator subprocess already being spawned for each.

The docstring is right and the box is wrong about the same line of code, ten lines apart.

## Why file it rather than reword it

The box's **headline** — *"no new subprocess per repo"* — is defensible if read as the docstring reads it: no new *validator or sidecar* process, the added cost rides the existing batch. The **evidence sentence appended at close-out** is not defensible under any reading, and evidence is the part a later reader trusts, because it is what distinguishes a ticked box from an assumed one.

`QUALITY.md`'s rule is that a box is ticked only when the delivered system satisfies it, and this close-out's whole purpose was to resolve 27 boxes that had been left unticked on tasks already marked `done`. A false evidence line inside that repair is the repair repeating the original error in miniature.

The second clause — *"its added cost is bounded by the same timeout"* — is true at the process level (`COLD_TIMEOUT_MS` bounds the whole `fleet_validate` invocation, `desktop/src/ipc/fleet-health.ts:393`) and worth keeping as the wording.

## Suggested fix

Replace the evidence clause with what is actually true and checkable: `_digest_counts` adds no *process of its own* — no second validator, no sidecar — and its git cost is one `git log` per repo inside the batch already bounded by `COLD_TIMEOUT_MS`. Then the box says a thing a reader can verify against `fleet_validate.py:80`, which is where it will be checked.

## Fixed — 2026-08-15

[[TASK-0419]]'s evidence sentence corrected. It now reads that `_digest_counts` runs in-process inside `summarise()`, riding the validator subprocess already spawned per repo — **no new process per repo**, which is what the box actually claims — and records that the original wording ("and spawns nothing") was false, naming `cockpit.py:5531` and `fleet_validate.py:80` as the contradiction.

The box itself stays ticked, because the property it asserts is true. What was wrong was the evidence I wrote under it, and this is the second finding in two days of that same shape: a claim written from memory of the design rather than from the code, sitting under a box whose own wording was more careful than mine.
