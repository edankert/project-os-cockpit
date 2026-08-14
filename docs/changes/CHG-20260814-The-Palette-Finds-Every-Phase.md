---
type: "[[change]]"
id: CHG-20260814-The-Palette-Finds-Every-Phase
title: "The quick palette finds every phase — a group head is a note too, and the six with no head come from the overview"
status: merged
owner: user:edwin
created: 2026-08-14
updated: 2026-08-14
source: ["Edwin 2026-08-14: 'Fix ISS-0164 … reproduce the problem if possible, then follow the project-os lifecycle'"]
commit: ""
pr: ""
impacts: ["typing a PHASE-#### id in the quick switcher opens the phase note", "nav group payloads carry `type` when the head names a note", "buildQuickCorpus fetches /api/cockpit/stats", "the palette corpus grows by 34 rows"]
issues: ["[[ISS-0164-Phases-Are-The-Second-Type-The-Palette-Cannot-Find]]"]
features: ["[[FEAT-0072]]"]
related: ["[[ISS-0142-The-Release-Note-Cannot-Be-Found-By-Name]]", "[[ISS-0132]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]", "[[CHG-20260814-Views-Stop-Reparsing-The-Snapshot]]"]
---

# The palette finds every phase

## Reproduced first

Against the live sidecar, rebuilding the corpus exactly as `buildQuickCorpus` does:

| typed | before | after |
|---|---|---|
| `PHASE-030` | **No matches** | `PHASE-030`, exact id |
| `PHASE-011` | **`ISS-0071`** — `issues/ISS-0071-Review-Findings-PHASE-011-012.md`, matched on its filename | `PHASE-011` first, `ISS-0071` second |
| `PHASE-017` *(superseded)* | No matches | `PHASE-017` |
| `PHASE-031` *(planned)* | No matches | `PHASE-031` |

The second row was not known when [[ISS-0164]] was filed and is the worse failure: typing a phase id did not always return nothing, it sometimes returned **a note about the phase instead of the phase**, scoring on `rel.includes(q)` so it arrived looking like an answer.

## The cause was one unread field

[[ISS-0164]] was filed saying *"no nav mode carries phases"*. That was wrong, and Edwin caught it by asking whether phases were selectable on the Features page — they are. `_features_groups` groups features under their phase and emits `key` = `PHASE-011`, `url` = the note, and [[ISS-0132]] made that head navigate.

`flattenNavItems` — the corpus builder — walked `group.items` and `group.subgroups` and **never the head**. So the phases sat in a payload the palette already fetched, in the one field it did not read.

## Both halves, because the head harvest alone is a partial

Harvesting heads makes **28 of 34** findable. `_features_groups` emits a group only for a phase with work grouped under it, so PHASE-012/015/017/018/019/031 — two done, three superseded, one planned — have no head at all. **Those are the six nobody can browse to either**, which makes typing the id the only route to them.

So:

1. **`flattenNavItems` harvests a group head that names a note.** Conditioned on the url, not on the key's shape, so a mode added later inherits this rather than becoming the next [[ISS-0142]]. The head's type comes from the payload — `_features_groups` now sends `type` — rather than being inferred from a `PHASE-` prefix, because a second place deciding what that prefix means is a parallel rule.
2. **`buildQuickCorpus` fetches `/api/cockpit/stats` for the tail.** 1.8 ms, and the overview payload already carries all 34 with their rel. This is a fetch *beside* a nav home, for what the home cannot hold — not the *instead of* the issue's superseded option 1 proposed.

The existing dedupe by rel collapses the 28 that arrive both ways. The corpus goes 851 → 885 unique rows: exactly the 34.

## Guards, and the hole one of them had

Three, each mutation-tested by reintroducing the defect:

- **the harvest is asserted in the renderer source.** This exists because the coverage guard *models* the harvest in Python — so deleting it from the renderer left that guard green, measuring a corpus the code no longer built. Deleting it now fails here.
- **the `cockpit/stats` fetch is asserted**, beside `review-queue` and `cockpit/changes`.
- **phases are asserted complete, not non-zero.** Mutated by dropping `rel` from the overview's phases, it reports *"28 of 34 reach the palette"* — the partial `found > 0` would have called fixed.

`KNOWN_ABSENT` gained a reverse check: an exemption must still *be* one. That file carried the wrong reason for phases for a day, inside the exemption for phases.

## Restart to see it

The corpus is built in the renderer, so a running shell keeps the old bundle until it restarts.
