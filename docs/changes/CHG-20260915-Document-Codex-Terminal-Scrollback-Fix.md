---
type: "[[change]]"
id: CHG-20260915-Document-Codex-Terminal-Scrollback-Fix
title: "Document Codex Terminal Scrollback Fix"
status: merged
owner: user:edwin
created: 2026-09-15
updated: 2026-09-15
source: ["[[ISS-0310]]"]
commit: ""
pr: ""
impacts: ["desktop/src/ipc/agent-instrument.ts", "desktop/src/renderer/renderer.ts", "desktop/src/ipc/terminal.ts"]
issues: ["[[ISS-0310]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[FEAT-0003]]", "[[ISS-0016]]", "[[ISS-0154]]", "[[ISS-0161]]", "[[ISS-0255]]"]
---

# Document the Codex terminal scrollback fix

## Summary
The cockpit's Codex launch path was documented as the source of the missing terminal history. Codex provides `--no-alt-screen` as an inline mode that preserves terminal scrollback. The earlier decision to omit that flag was superseded by [[CHG-20260915-Launch-Codex-in-inline-terminal-mode-for-scrollback]].

## Impact

- No screen changed: this is a documentation-only diagnosis; the Electron wrapper still needs the proposed implementation.


## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: not-applicable — FEAT-0003 is unchanged; the issue links it as the affected terminal feature
- requirements: not-applicable — no requirement changed
- tasks: not-applicable — implementation was not requested; a future task will own the code change
- issues: new — [[ISS-0310]] records the Codex-specific scrollback defect and proposed fix
- tests: not-applicable — no code change or new test note; live verification is a follow-up
- workflows: not-applicable — no workflow changed
- decisions: not-applicable — the note records a CLI launch option, not a new architecture decision
- risks: not-applicable — no dependency, environment variable, credential, or path contract changed
- changes: new — this note
- snapshot: updated — ISS-0310, this change note, and the counters were added

## Follow-ups
- [x] Record the initial decision not to apply `--no-alt-screen`; that decision was later superseded.
- [x] Add the wrapper regression check.
- [ ] Verify the live Electron terminal and decide separately whether the 256 KB PTY replay cap needs its own issue.
