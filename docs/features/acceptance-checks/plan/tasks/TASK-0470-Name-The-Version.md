---
type: "[[task]]"
id: TASK-0470
aliases: ["TASK-0470"]
title: "Name the version — Start shrinks to one job and scaffolds from the repo's own template"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0116-A-Release-Can-Be-Finished]]"]
parent: "[[FEAT-0116-A-Release-Can-Be-Finished]]"
effort: S
depends: []
blocks: []
related: ["[[FEAT-0105-There-Is-Always-A-Release]]"]
tests: []
---

# Name the version

Start survives — `preparing:` is what stops the gate obligation asking forever outside a release window, and the draft note is the hook `tests_verified`, known issues and artifacts hang off — but it shrinks to exactly one job and stops implying the process begins there. Under the continuous model the process has been running all along; this button names the version.

The scaffold reads `docs/__templates__/release.md` instead of an inline literal: `previous_release:` set, the Known-issues and Post-Release-Actions sections present (FEAT-0110 reads a heading the tool's own writer never produced), `platform:`/`tags:` matching the corpus, filename matching the `REL-0012-v2.1.6.md` convention rather than `REL-0013-V2-1-7.md`.

## Done when

- [ ] The control is labelled *Name the version* and the note it writes is template-shaped — sections, fields, filename.
- [ ] A note prepared by the cockpit and one prepared by hand from the template are indistinguishable in structure.
