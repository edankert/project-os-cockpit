---
type: "[[task]]"
id: TASK-0606
aliases: ["TASK-0606"]
title: "One pure function decides whether a note ID opens the design bench, reading the project's design register rather than the ID's prefix"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-09-11
updated: 2026-09-11
source: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
parent: "FEAT-0146"
effort: "S"
due: ""
depends: []
blocks: ["[[TASK-0607-Links-Resolved-By-ID-Open-A-Design-In-The-Bench]]"]
related: ["[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]", "[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]"]
tests: ["[[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]"]
---

# The design register decides where an ID opens

This task writes the rule of [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] as a function nothing calls yet. Given a note ID and a project's design register, it says whether a link naming that ID should open the design bench. [[TASK-0607-Links-Resolved-By-ID-Open-A-Design-In-The-Bench]] wires it in.

## Definition of Done

- [x] `desktop/src/renderer/deep-link.ts` defines `designBenchTarget(noteId, designs)`. Like `parseCockpitLink` beside it, it is a plain global with no imports, no exports and no browser globals.
- [x] It returns `~design/<id>` when `noteId` matches a register entry's `id`, ignoring case, and that entry has a non-empty `asset` or at least one entry in `variants`. The returned ID is spelled as the register spells it. In every other case it returns `null`, which means "open the note as today".
- [x] The file's header comment says the file now also decides where a link that names an ID lands, and that the design register decides it, not the prefix.
- [x] `desktop/tests/deep-link.test.mjs` gains these cases, run in the same context with no `URL` in scope:
  - [x] A design with an asset gives `~design/DES-0002`.
  - [x] The ID written in lower case still matches, and the result uses the register's spelling.
  - [x] A design with variants and no asset gives the bench.
  - [x] A design whose `asset` names a file that does not exist (`asset` set, `has_asset: false`) gives the bench, because the bench reports the missing file.
  - [x] A design with no asset and no variants gives `null`.
  - [x] `DES-0099`, absent from the register, gives `null`. The prefix does not decide.
  - [x] A design whose ID has no `DES-` prefix, such as `UX-0001`, gives the bench. The register decides.
  - [x] A feature ID gives `null`, and so does any ID against an empty register.
- [x] Each of three broken versions of the function turns at least one case red, and the result is recorded in [[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]'s `adequacy:`. The three: one that ignores `asset` and `variants` and sends every design to the bench; one that matches on the `DES-` prefix instead of the register; one that compares IDs case-sensitively. A fourth was tried too, one that reads `has_asset` instead of `asset`; it turned the missing-file case red.
- [x] `npm run build` in `desktop/` has run, and `tests/test_desktop_node_suite.py` passes. `deep-link.test.mjs` runs 20 cases, 9 of them new.

## Steps

- [x] Add the function and its structural type to `deep-link.ts`. The renderer's `DesignRecord` interface lives in `renderer.ts` and is not visible to a plain script, so declare only the three fields the rule reads: `id`, `asset`, `variants`.
- [x] Add the cases to `deep-link.test.mjs`. Extend the `before` hook to expose `designBenchTarget` the way it exposes `parseCockpitLink`.
- [x] Build, run the node suite, try the three broken versions, and restore the real one.

## Notes

- **Why `asset` and not `has_asset`.** The register sets `has_asset` only when the file exists. A declared but missing asset should still open the bench, whose "Artifact not found: <path>" message is how the tool reports a broken path today. So the rule reads whether an asset is declared (`asset` is not empty), not whether the file is there.
- **Why this file.** `deep-link.ts` already holds the one other pure decision about links, and it is already loaded before `renderer.js` and tested without a window. A second file would need its own `<script>` tag in `index.html` and its own test harness for one function.
- **Why the register and not the prefix.** [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]], "Decisions this requirement records", gives the reasons. The register reads the note's type, and it is the only source that also says whether the bench has anything to show.

## Outcome (2026-09-11)

`designBenchTarget(noteId, designs)` is in `desktop/src/renderer/deep-link.ts`, below `parseCockpitLink`. It declares its own three-field `DesignBenchEntry` type. It also returns `null`, rather than throwing, when the register is not a list: a ninth case in the test file checks `null`, `undefined`, an object and a string.
