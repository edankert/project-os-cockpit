---
type: "[[risk]]"
id: RISK-0011
title: "Renaming the walk to the release test can break links to the old address and drop results a tester saved in the browser mid-release"
status: open
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]", "Edwin, 2026-09-27, decision D1"]
likelihood: medium
impact: high
mitigation: ["Keep ~walk and ~walk/<platform> opening the new overview", "Move values from the five old browser storage keys to the new keys once, then remove the old keys", "Leave the ledger's stored values and file format unchanged", "Rename the bundled generator only together with project-os-dev's rename, so the byte-identity test never fails between the two"]
related: ["[[TASK-0639-Rename-The-Walk-To-The-Release-Test]]", "[[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]]", "[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]"]
---

# Renaming the walk drops links and saved progress

## Description

The rename changes an address, an API path and five browser storage keys (`cockpit:walk-focus`, `walk-completed`, `walk-place`, `walk-steps`, `walk-evidence`). Three things can go wrong:

- Links to `~walk/<platform>` stop working. Your Trainer's release note `REL-0017-v2.2.0.md` links there, and every fleet repository's copy of the cockpit under `tools/cockpit/` links there until the next cockpit release reaches it.
- A tester halfway through a release loses the results and evidence saved in the browser, because the page reads new keys and the old ones are ignored.
- The bundled generator's byte-identity test fails if this repository renames the file before project-os-dev does, or the other way round.

## Mitigation

- `~walk` and `~walk/<platform>` open the new overview (TASK-0639, TASK-0644).
- On first load, a value under an old key is moved to its new key and the old key is removed; a renderer test proves an old saved result still shows.
- The ledger format and values do not change.
- The bundled file is renamed in the same change that syncs project-os-dev's renamed generator.

## Risk scan, 2026-09-27

Triggers checked for FEAT-0155: an artifact path change applies (route, API, bundled file and storage keys), which is this risk. No new external dependency, environment variable, long-running step, or credential or licence exposure.
