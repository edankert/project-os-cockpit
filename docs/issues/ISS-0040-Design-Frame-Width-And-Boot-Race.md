---
type: "[[issue]]"
id: ISS-0040
aliases: ["ISS-0040"]
title: "The design frame is narrower than the artifact; and a virtual-landing mode loses its page on boot"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28 while reviewing the design surface"]
related: ["[[ISS-0039-Nested-Scrollbars-On-The-Design-Surface]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
fixed_by: []
---

# Three findings from one report

Edwin: *"I don't think you provide the correct sizes to the underlying frame."* Plus two sidebar layout complaints.

## 1. The frame is narrower than the design it shows

Measured against the **real** renderer: a 1356px pane leaves the frame **1036px**, because the 260px sidebar and gaps come out of it. DES-0001's dossier is authored at **1240px**. So the design scrolled sideways inside its own frame — scrollbars inside scrollbars again, in the other axis, one layer further in than the fix for [[ISS-0039]] reached.

**Fix:** the details sidebar collapses, and the choice persists. Collapsed, the frame reaches **1312px** — wider than the artifact, so the horizontal scroll disappears. The toggle lives in the *head*, not the sidebar: a control that vanishes with the thing it controls cannot bring it back.

Not attempted: scaling the artifact to fit. It would need the content width, and the sandbox denies `contentDocument` by design.

## 2. A virtual-landing mode loses its page on boot

The sidecar-ready handler reads:

```js
void loadWsNav();
if (currentNavMode !== 'overview') void navigateTo('README.md');
```

`loadWsNav()` navigates Design to `~design`; the line below then races it to README and wins. Select Design, restart the app, and you land on README with the Design button still lit. The guard named only `overview` because it was written when overview was the only such mode — **Review inherited the bug on the day it was added, and Design on the day it was added.** Now a named set, so the next such mode cannot inherit it silently.

## 3. Two sidebar layouts sized for a page, not a column

Both were written when these components sat full-width under the frame, and neither was re-checked when they moved into a 260px sidebar:

- **Revision rail** — `justify-content: space-between` put the reason and the date+hash in two columns; the date column took a third of the width and squashed the reason to a few words. The reason is the part you read when picking a revision. Now stacked.
- **Rationale** — a three-column grid (id · decision · Open) pushed the decision into a ~150px gutter. The id is an eyebrow above the text now, and the decision gets the whole column.

## The verification failure worth recording

The harness written for [[ISS-0039]] measured a DOM I wrote **by hand**. It passed every check while the surface was still wrong on screen, because a mock cannot reproduce the real height chain (`.stage > .stage-main > .doc-view`), the real stylesheet order (`base.css`, `cockpit.css`, then `renderer.css`), or what `paint()` actually builds.

It is deleted. `desktop/harness/design-harness.html` loads the **shipped bundle** against a stubbed sidecar and drives it to a real design. A test now asserts that it loads `dist/renderer/renderer.js` — the property that matters is not "a harness exists" but "the harness runs what ships". A harness that can pass while the app is broken is worse than no harness.

Two things the real harness caught immediately that the mock could not: one missing bridge namespace (`app.onMenuDispatch`) throws at module scope and stops the whole bundle, and the ready handler drops its event unless the workspace is already active.
