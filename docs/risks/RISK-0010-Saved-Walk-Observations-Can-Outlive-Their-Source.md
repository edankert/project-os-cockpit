---
type: "[[risk]]"
id: RISK-0010
title: "Saved release test observations can outlive the action they judged"
status: open
owner: user:edwin
created: 2026-09-16
updated: 2026-09-27
source: ["Your Trainer FEAT-0122, 2026-09-16"]
likelihood: medium
impact: high
mitigation: ["Key saved progress by workspace, release and platform", "Associate marks and evidence with the action and expectation content", "Show changed work for review before an old observation contributes to a verdict", "Test failed storage and ledger writes"]
related: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]", "[[TASK-0630-Record-And-Resume-Walk-Observations]]"]
---

# Saved release test observations can outlive the action they judged

## Description

The page can retain a local step mark after the procedure action, expectation, candidate build or platform changes. Reusing that mark could make a new check appear observed when nobody performed its current instruction.

## Mitigation

- Scope saved position and observations to the workspace, release and platform.
- Tie each observation and attachment to the content it judged, then flag changed content for review.
- Preserve ledger history when a person corrects a verdict.
- Exercise failed local storage and ledger writes without advancing or duplicating results.

## Implemented storage boundary

The cockpit owns the browser records under `cockpit:walk-focus:<workspace>`, `cockpit:walk-steps:<workspace>`, `cockpit:walk-completed:<workspace>`, `cockpit:walk-evidence:<workspace>`, `cockpit:walk-ready:<workspace>`, `cockpit:walk-observation-history:<workspace>` and `cockpit:walk-timer:<workspace>:<step>`. Each observation key includes release, platform, section and the full authored action, required state, capture metadata and expectation content. The completed-check index names checks this browser recorded under a release and platform; it does not hold verdicts. A saved note also records its user-entered build, platform, release, required state and recording time. The browser retains these records until the user clears site data; no cross-computer transfer is promised.

When the procedure changes, an old observation is retained for review and cannot mark the new action. When a candidate invalidation appears in the ledger history, the old mark is archived before the action can be recorded again. Marks for completed checks stay available in the correction section. After a changed step is rerun, its older mark is archived. A failed archive pauses step recording rather than reusing an invalid mark. The ledger remains the only store for completed check verdicts.

An authored capture prompt asks for the app build identifier before saving a note or filing a PNG. The optional PNG is stored under the affected check through the existing note attachment endpoint; the browser keeps its returned record path, not the image bytes. The later comparison shows the originating build, state, platform and image. Saving evidence refreshes an open comparison immediately. A verdict posted after attachment includes the PNG path in its ledger evidence references. The build is entered by the walker and is not verified automatically against the running app.

Clearing browser site data removes local notes and unfinished step marks, so the page must report missing evidence rather than imply it survived. A PNG already filed under `docs/attachments` remains in the workspace, but a cleared browser no longer knows which source observation to show it beside. Attaching a PNG after posting a verdict does not change that historical verdict event; the next recorded verdict can carry the attachment reference.

The correction path asks the server for the current authored procedure for browser-indexed completed checks. A saved step signature restores its mark only when its current action and expectation content still match. The local index selects which completed checks to display; it never changes what the ledger says is owed or cleared. An invalid procedure displays its check instructions and repair reason without offering a step verdict.

## Triggers

- A new action displays an old mark after a procedure edit.
- A different platform or release displays another release test's evidence.
- A failed write advances the page as though its verdict were recorded.
