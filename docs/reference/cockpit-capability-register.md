---
type: "[[reference]]"
id: REFERENCE-CAPABILITY-REGISTER
aliases: ["REFERENCE-CAPABILITY-REGISTER"]
title: "Capability register: what the cockpit can do today, keyed so a sibling application can track what it has and has not adopted"
status: active
owner: user:edwin
created: 2026-09-06
updated: 2026-09-06
scope: "project"
source:
  - "Edwin 2026-09-06: 'make sure to mark the current cockpit functionality so if any new cockpit functionality arrives which it will that we can adapt the other repo accordingly'"
  - "desktop/src/renderer/index.html, renderer.ts, main.ts; src/project_os_cockpit/server.py (the route table), cockpit.py (NAV_MODES); docs/reference/des-0014-glass-cockpit-review-2026-09-05.md Part 2"
related:
  - "[[project-os-deck#REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]"
  - "[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"
  - "[[FEAT-0093-A-Cross-Repo-Link-Carries-Its-Parts]]"
tags: [reference, register, capability, downstream]
---

# Capability register

## Purpose

A second application is being started in its own repository, beside this one, to build the views described in [[project-os-deck#REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]. It shares this repository's sidecar. This cockpit stays the primary place where new functionality is built, so capability will keep arriving here, and Edwin's requirement is that the other repository can see it and support it going forward.

This note is the mechanism. It lists every capability the cockpit has today under a stable key, records the commit it was measured at, and states the rule that keeps it current. The other repository keeps an adoption table against the same keys (adopted, not yet, not applicable, replaced by). A capability added here after the baseline is a new row here and an open row there.

**Baseline:** commit `570da22`, 2026-09-06, this repository at `main`.

## The rule

1. **A change note that adds or changes capability updates this register in the same commit.** "Capability" means anything a person or an agent can do or see through the shell, the sidecar's own HTML, the sidecar API or the `cockpit` CLI. A fix that changes no behaviour does not touch the register.
2. **A new capability is a new row with a new key and the date.** A changed one keeps its key and gains a dated line. A retired one keeps its key, marked retired, so the other repository can see what to drop.
3. **The other repository reads this note, not the code.** Its adoption table cites keys from here. When it needs a capability this register does not describe well enough to adopt, that is an issue in this repository against this note.
4. **Detecting drift without trust:** anything under `docs/changes/` dated after the baseline, or any commit touching `desktop/src/` or `src/project_os_cockpit/server.py` since the baseline, is a candidate that must either have a row here or a stated reason in its change note. The command is in Maintenance.

## Surfaces (ADR-0010)

| key | surface | what it is |
| --- | --- | --- |
| `surface.shell` | mode 3 | the Electron shell: one window per copy, one sidecar per workspace, Mac-local, reads and writes |
| `surface.sidecar-html` | mode 1 | the sidecar's own three-pane HTML, served on the LAN for a tablet; reads only; views Project, Features, Tasks, Issues, Recent |
| `surface.cli` | terminal | the `cockpit` command: `focus`, `state`, `history`, `signal`, `dispatch` |

## Shell capabilities

Measured from `index.html`, `renderer.ts` and `main.ts` at the baseline.

| key | capability | where |
| --- | --- | --- |
| `shell.workspaces.rail` | workspace rail with health marks per repo (validator, agent, git); rescan or add; remove from list; project settings (name, icon, colour) | `#ws-rail`, `ipc/workspaces.ts`, `ipc/fleet-health.ts` |
| `shell.workspaces.discovery` | a workspace is any directory under `~/Dev/repos/` with `SNAPSHOT.yaml` at its root | `ipc/workspaces.ts` |
| `shell.fleet.rollup` | fleet roll-up across every workspace, with the push action that refuses deploy remotes | `~agents`, `ipc/agents-fleet.ts`, `ipc/git.ts` |
| `shell.nav.modes` | navigator with buttons for overview, intent, features, issues, tests, publication, library; the server also serves tasks, active, recent; retired modes keep answering | `cockpit.py` `NAV_MODES`, `RETIRED_NAV_MODES` |
| `shell.nav.needs-you` | the owed group first in six views, per ADR-0025; a badge on every view button with what it owes | `obligations.py`, nav payload |
| `shell.nav.platform` | platform picker filtering the navigator | `#platform-bar` |
| `shell.nav.hide-completed` | collapse completed work | `#hide-completed-toggle` |
| `shell.nav.pins` | pinned notes per workspace | `pinnedStorageKey` |
| `shell.nav.library` | file tree of the docs root with by-type groups auto-discovered from `type:` | `cockpit.py` library payload |
| `shell.stage.tabs` | centre tabs for open notes; back and forward; scroll restore | `#center-tabs`, `menu:back`, `menu:forward` |
| `shell.stage.find` | find in page (⌘F) | `#find-bar` |
| `shell.stage.quick-switch` | quick switch to any note (⌘P) | `#quick-switch` |
| `shell.stage.capture` | file an issue at triage from anywhere | capture action |
| `shell.reader.render` | a note rendered by the sidecar: frontmatter strip, wikilinks, cross-repo links (`project#ID`), image embeds, callouts, project-os IDs linked | `/api/render`, `renderer.py`, `wikilinks.py`, `callouts.py` |
| `shell.reader.actuators` | actuator row on a note: transition, tick a criterion with evidence, release gate, run a test, decide an ADR, mark or retire a check | `/api/notes/*` |
| `shell.reader.design` | design pages: regions, comments, revisions, capture, offer for review, verdict | `/api/design/*`, `/api/cockpit/design-*` |
| `shell.context.pane` | right pane: linked notes and backlinks grouped by type | `/api/cockpit/context` |
| `shell.pages.overview` | overview: digest since "Caught up", unpushed commits, phase squares, validator report, contribution grid; per-phase page | `~overview`, `~overview/<PHASE>` |
| `shell.pages.history` | what changed state and when | `~history` |
| `shell.pages.checks` | acceptance checks with tier and area filters in the address; each row shows the comment behind its verdict, and the count of every comment the check carries; the page and its filters are remembered per workspace, so returning to a project resumes the walk (2026-09-06, [[ISS-0280]], [[ISS-0281]]) | `~checks`, `~checks/tier/<n>`, `~checks/area/<area>`, `cockpit:checks-place:<workspaceId>` |
| `shell.checks.mark-dialog` | the mark dialog shows the check's body — rendered through `/api/render`, so lists and headings read as lists and headings — and every comment on it, newest first, above the seven verdict buttons; the card is bounded so Save stays on screen whatever the body's length (2026-09-06, [[ISS-0281]], [[ISS-0282]]) | `askForMark`, `fillCheckProse`, `buildCheckComments` |
| `shell.pages.release` | release page and per-item pages; prepare, verify, mark released | `~release/<id>` |
| `shell.pages.accept` | acceptance runner for a feature, stepwise | `~accept/<FEAT>` |
| `shell.pages.test-run` | test runner for a test note | `~tests/<TST>/run` |
| `shell.pages.session` | an agent session's page: work and files | `~session/<id>` |
| `shell.pages.agents` | all sessions across the fleet | `~agents` |
| `shell.pages.inbox` | the inbox tray and page: store, discard, triage | `~inbox`, `/api/inbox/*` |
| `shell.agents.strip` | agent strip: state dot, cost, context used, conversation weight, cache temperature, touched notes, dispatch queue button, expand | `#agent-strip` |
| `shell.agents.attention` | agents needing attention, above the navigator | `#ws-attention` |
| `shell.agents.approvals` | approvals and dispatch requests; approve; dispatch a verb to an agent | `/api/cockpit/approvals`, `/api/cockpit/dispatch` |
| `shell.agents.follow` | follow agent navigation per workspace (Following toggle); `cockpit focus` lands here | `#follow-toggle`, `/api/cockpit/focus` |
| `shell.terminal` | one PTY per workspace inside tmux, rendered with xterm; toggle (⌘`), restart, height persisted | `ipc/terminal.ts`, `#terminal-pane` |
| `shell.live` | live reload over SSE; staleness is stated, never silently reloaded (ISS-0140) | `/_events`, `sse-reload.js` |
| `shell.validation` | validator report in the shell, failing notes marked | `/api/cockpit/validation` |
| `shell.theme` | light and dark themes from the design system (DES-0002) | `cockpit:theme` |
| `shell.settings` | settings popover (external hook) | `#settings-popover` |
| `shell.windows` | New Window (a full second copy), window bounds persisted app-wide, deep links, context menus per surface, context-aware copy and paste | `main.ts`, `window-state.ts`, `ipc/context-menu.ts`, `ipc/clipboard.ts` |
| `shell.state.local` | nav mode, pane widths, theme, hide-completed, pins, follow, terminal open and height, design side, scope-completed, platform, left pane collapsed are kept in `localStorage`, read once at start | `renderer.ts` |

## Sidecar API

Grouped from the route table in `server.py` at the baseline. A row is a group, not an endpoint; the other repository adopts groups.

| key | group | routes |
| --- | --- | --- |
| `api.read.nav` | navigation payloads | `/api/cockpit/nav`, `/api/cockpit/landing`, `/api/cockpit/locate`, `/api/cockpit/brief`, `/api/cockpit/stats` |
| `api.read.note` | a note and its neighbourhood | `/api/render`, `/api/cockpit/context`, `/docs/`, `/index` |
| `api.read.record` | the record's derived views | `/api/cockpit/decisions`, `/api/cockpit/designs`, `/api/cockpit/design-revisions/`, `/api/cockpit/design-comments/`, `/api/cockpit/history`, `/api/cockpit/changes`, `/api/cockpit/commits`, `/api/cockpit/unreleased`, `/api/cockpit/release`, `/api/cockpit/release-item`, `/api/cockpit/digest`, `/api/cockpit/watermark`, `/api/cockpit/activity` |
| `api.read.obligations` | what needs a person | `/api/cockpit/obligations`, `/api/cockpit/review-queue`, `/api/cockpit/acceptance`, `/api/cockpit/acceptance-debt`, `/api/cockpit/scope-tests`, `/api/cockpit/transitions`, `/api/cockpit/actions` |
| `api.read.check-history` | every verdict ever recorded against each check — mark, date, platform, author, method and the comment — newest first, in the acceptance payload's `view.history`. Empty in a repo with no ledger (2026-09-06, [[ISS-0281]]) Each row also carries `verdict_method`, so a surface can tell a walker's sentence from the migration backfill's. | `/api/cockpit/acceptance`, `ledger.events_by_check` |
| `api.read.agents` | sessions and their instruments | `/api/cockpit/sessions`, `/api/cockpit/agents`, `/api/cockpit/agent-state`, `/api/cockpit/session-cache`, `/api/cockpit/approvals`, `/api/cockpit/dispatch-requests`, `/api/cockpit/runtime`, `/api/cockpit/identity` |
| `api.read.validation` | the validator's report | `/api/cockpit/validation` |
| `api.read.state` | the user's view, for the CLI and following | `/api/cockpit/state`, `/api/cockpit/focus`, `/api/cockpit/tab-state` |
| `api.write.notes` | guarded writes to frontmatter, never body text | `/api/notes/transition`, `tick`, `tick-owed`, `check-toggle`, `mark-check`, `retire-check`, `create`, `attach`, `decide`, `shape`, `review`, `test-run`, `acceptance-run`, `acceptance`, `release-prepare`, `release-verified`, `release-mark-released`, `release-contents`, `seal-ledger`, `choose-variant`, `actions` |
| `api.write.design` | design page writes | `/api/design/capture`, `comment`, `offer-review`, `verdict` |
| `api.write.agents` | approve, dispatch, review requests, caught-up | `/api/cockpit/approve`, `dispatch`, `review-request`, `review-resolve`, `reviewed`, `review/`, `caught-up` |
| `api.write.inbox` | inbox store and discard | `/api/inbox`, `/api/inbox/store`, `/api/inbox/discard` |
| `api.infra` | events, static, project files, shell files, terminal, hooks, health | `/_events`, `/_static/`, `/_project/`, `/_shell/`, `/_inbox/`, `/api/terminal`, `/api/agent-hook`, `/healthz`, `/design-asset/`, `/design-asset-at/` |
| `api.guards` | writes are loopback-only (REQ-0027); human-only verbs refuse an agent (REQ-0026); verbs come from the registry (ISS-0153) | `approvals.py`, `note_writes.py`, `agent_actions.py` |

## What the other repository owes

- An adoption table keyed by the rows above, with one of: adopted, not yet, not applicable, replaced by (and what by).
- A dated line in that table each time it reads a new row here.
- An issue here, against this note, when a row is not described well enough to adopt.

## Maintenance

Update this note in the same commit as any change note that adds, changes or retires a capability (rule 1). To find candidates since the baseline:

```
git log --since=2026-09-06 --name-only --format='%h %ad %s' --date=short -- docs/changes desktop/src src/project_os_cockpit/server.py src/project_os_cockpit/cockpit.py
```

Every commit that list returns must correspond to a row here, or its change note must say why it adds no capability.

- 2026-09-06 — written at baseline `570da22`.
- 2026-09-06 — `shell.pages.checks` gains the comment on the row and the remembered place; `shell.checks.mark-dialog` and `api.read.check-history` are new ([[CHG-20260906-Acceptance-Checks-Keep-Their-Place-And-Their-Comments]]). Two further changes the same day add no capability key, because `shell.pages.checks` already promised both and neither was working: a verdict that does not clear is no longer dropped from the view ([[ISS-0281]]), and the tier chips now select a value the row predicate can match ([[ISS-0284]]).
