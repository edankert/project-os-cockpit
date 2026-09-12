---
type: "[[plan]]"
title: "A link that names a design opens the design bench — delivery sequence"
status: done
owner: user:edwin
created: 2026-09-11
updated: "2026-09-12"
source: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
implements: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
related: ["[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]", "[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]"]
---

# A link that names a design opens the design bench

Two tasks. The first writes the rule as a pure function with its own tests. The second makes the one function that resolves a link by ID ask that rule first.

## Delivery sequence

0. **Ask Edwin to approve [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]**, which is `draft`. Ask the open question in [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] at the same time: should an in-repo `[[DES-####]]` wikilink open the bench too? Nothing below depends on the answer. A yes adds a third task after these two.
1. **[[TASK-0606-The-Design-Register-Decides-Where-An-ID-Opens]]**: `designBenchTarget(noteId, designs)` in `desktop/src/renderer/deep-link.ts`, and its cases in `desktop/tests/deep-link.test.mjs`.
2. **[[TASK-0607-Links-Resolved-By-ID-Open-A-Design-In-The-Bench]]**: `locateAndOpen` in `desktop/src/renderer/renderer.ts` fetches the design register and asks `designBenchTarget` before it asks `/api/cockpit/locate`. A source guard in `tests/test_design_links.py`, the two capability register rows, and the walk in [[TST-0085-A-Link-To-A-Design-Shows-The-Design]].
3. **Close-out**: a change note, REQ-0062's criteria ticked with evidence, PHASE-005's added exit criterion ticked and the phase closed again, and `bash tools/scripts/close-out-commit.sh` naming the paths. Moving the feature to `done` is a review gate in `tools/instructions/QUALITY.md`, so run the independent review there.

## The shape of the change

The rule, as TASK-0606 should write it:

```ts
function designBenchTarget(
  noteId: string,
  designs: ReadonlyArray<{ id: string; asset?: string; variants?: ReadonlyArray<unknown> }>,
): string | null
```

It returns `~design/<id as the register spells it>` when `noteId` matches a register entry case-insensitively and that entry has a non-empty `asset` or at least one variant. It returns `null` otherwise, and `null` means "open the note as today".

The call, as TASK-0607 should write it, at the top of `locateAndOpen`:

```ts
const bench = designBenchTarget(noteId, await designsForLink());
if (bench) { void navigateTo(bench); return; }
// the existing /api/cockpit/locate lookup follows, unchanged
```

`designsForLink` stands for "fetch `/api/cockpit/designs` from `sidecarBaseUrl` now, and return an empty list on any failure". The name is the implementer's choice.

## Dependencies

- **Hard: this builds on uncommitted work.** `deep-link.ts`, `openCockpitLink`, the path-carrying `pendingCrossRepoJump` and `desktop/scripts/open-link.sh` came from [[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]] on 2026-09-10 and were not committed when this was planned. Read them from the working tree. Never check out over them.
- **Hard: TASK-0606 before TASK-0607.** The call site needs the function.
- **Build:** run `npm run build` in `desktop/` after every TypeScript change. The node tests read `desktop/dist/`, and `tests/test_status_vocabulary.py::test_desktop_build_is_not_stale` fails when `dist/` was not built from the current source: it compares a digest of `desktop/src/**/*.ts` with the one the build wrote.

## Things that will go wrong if nobody says them

- **Do not reuse the cached register.** `fetchDesignRegister()` keeps the last good list when a fetch fails. After a project switch, that list belongs to the project the reader just left. A failed fetch would then send `DES-0002` to the wrong project's bench, which says "No design DES-0002". The link must fall back to the note instead.
- **Do not put the rule in `navigateTo`.** The bench header's ID chip, the `Read <ID> as a note` button and an owed design's landing row all open the note with `navigateTo(d.rel)`. A rule in `navigateTo` would send each of them straight back to the bench, and the reader could never reach the note.
- **Keep `deep-link.ts` free of browser globals.** Its node test runs it with an empty global scope, no `URL` included, because the renderer's Chromium 128 reads no host from a `cockpit://` URL ([[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]). The new function needs nothing but its two arguments.
- **The parked jump already reads the right sidecar.** When a link switches project, `locateAndOpen` runs from the sidecar-ready handler, after `sidecarBaseUrl` points at the arriving project. No extra wait is needed.
- **Run the full suite in the foreground and read its output:** `.venv/bin/python -m pytest -q -p no:cacheprovider`. A background run once reported green from the wrapper's exit code while pytest had written nothing. One failure is known and unrelated: `tests/test_release_evidence.py::test_both_corrupt_store_artifacts_are_reported_and_the_others_are_not`.
- **Restart the cockpit by its pid only.** Deck also runs as `Electron .`, and a pattern kill has already taken down the wrong app once. Check `ps -p <pid>` shows the command you expect before stopping it.
