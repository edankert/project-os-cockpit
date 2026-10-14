---
type: "[[plan]]"
title: "Delivery plan: the cockpit's facts on the project line above the Claude prompt, and two commands that answer in a pane"
status: active
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]", "Edwin 2026-10-14: 'Build FEAT-0041 too'; 'Only when non-zero'; 'Can we first implement the rest of the features in this phase and then test!'"]
implements: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"]
related: ["[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]", "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]", "[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]", "[[project-os-dev#FEAT-0041-Project-Os-Mod]]", "[[project-os-dev#REFERENCE-PROJECT-LINE-CONTRACT]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[REQ-0027-Every-Write-Guarded]]", "[[REQ-0019-Agent-Fleet-Visibility]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:`; see docs/__templates__/plan.md. -->
# Delivery plan: the cockpit's facts on the project line

In a cockpit terminal, the line project-os draws above the Claude prompt will end with the cockpit's facts: how many things need the person in this project, how many in the other projects when that is above zero, and an "Open in cockpit" button. Two commands, `/cockpit-needs` and `/cockpit-release`, will answer from the sidecar in a pane without starting a Claude turn. The shell gains one small file per project, the sidecar one read-only route, and the cockpit plugin a drawing hook, a button and two commands. The work is six tasks.

## What exists today

- **The plugin** (`desktop/plugin/claude-code/hooks/register.ts`) reports the session to the sidecar, submits dispatched prompts, and offers permission prompts to the cockpit. It finds the sidecar through `sidecarUrl`, which reads `$COCKPIT_INSTRUMENT_DIR/hook-env` on every call. It draws nothing.
- **This project's count**: `GET /api/cockpit/obligations` returns `{views, breakdown, verbs, nouns, total, kinds}` for one workspace (`server.py`, `obligations.badges_payload`). `total` is the number the badges show (ADR-0020 decision 3).
- **The other projects' counts**: no sidecar has them. The draft home window's `buildProject` (`desktop/src/ipc/home-window.ts`) reads each live sidecar's obligations, and for a project with no sidecar uses the cold digest's `needsYou` and `computedAt` from `fleetHealth()`.
- **The instrument folder**: the shell makes one per workspace (`agent-instrument.ts`, `instrumentDirFor`) and keeps `hook-env` in it current (`setSidecarUrl`).
- **Deep links**: `cockpit://<project>/<target>` brings the window forward and opens the target; the project may be the workspace ID, the target a note ID (`main.ts`, `handleDeepLink`; `renderer/deep-link.ts`).

## The contract with the sidecar

The plugin asks the sidecar one question for the line, and the shell's file answers the other.

### `GET /api/cockpit/line` (new, TASK-0672)

Loopback only, like the routes the plugin already calls. Read-only. Answers in one request what the line and the button need for this project:

```json
{
  "schema_version": 1,
  "needs_you": {
    "total": 3,
    "kinds": [
      { "kind": "feature", "count": 2, "verb": "review", "noun": "feature" },
      { "kind": "requirement", "count": 1, "verb": "approve", "noun": "requirement" }
    ]
  },
  "open_target": "FEAT-0157"
}
```

- `needs_you.total` is the same number `GET /api/cockpit/obligations` returns as `total`, computed by the same function, so the line and the badges never disagree. `kinds` is that payload's breakdown flattened across views, with the verb and the singular or plural noun already chosen.
- `open_target` is the focus item the button opens: the snapshot's `focus.task`, else `focus.issue`, else `focus.feature`, else `focus.phase`, else `null`. With `null` the button opens the project's home.
- Any failure to compute returns 500, never a zero. The plugin then leaves this project's count off the line.

### `needs-elsewhere.json` in the instrument folder (new, TASK-0671)

Written by the shell's main process into `$COCKPIT_INSTRUMENT_DIR/needs-elsewhere.json`, beside `hook-env`, for every workspace that has an instrument folder:

```json
{
  "schema_version": 1,
  "written_at": "2026-10-14T21:30:05Z",
  "workspace_id": "ws-7f3a",
  "projects": [
    { "project": "your-health", "workspace_id": "ws-11c2", "count": 4, "as_of": "2026-10-14T21:30:04Z", "source": "live" },
    { "project": "your-trainer", "workspace_id": "ws-90ab", "count": 1, "as_of": "2026-10-14T19:02:00Z", "source": "cold" },
    { "project": "project-os-deck", "workspace_id": "ws-5d01", "count": null, "as_of": null, "source": "unknown" }
  ]
}
```

- `workspace_id` at the top is this folder's own workspace. The plugin uses it to build the button's link. `projects` lists every other workspace and never this one.
- Each count comes from the same function the home window uses, moved out of `home-window.ts` so both call it.
- The shell rewrites the file every 30 seconds while the app runs, and at once when a workspace opens or closes. It writes a temporary file and renames it, so the plugin never reads half a file. With `COCKPIT_NO_INSTRUMENT` set, no file is written.

### What the line shows, and when it leaves a number out

- **This project**: `3 need you` when `needs_you.total` is above zero. Nothing when it is zero, or when the route failed or the sidecar is down.
- **The other projects**: the sum of every project whose `count` is known and whose `as_of` is under 24 hours old, as `5 in other projects`. Left out when the sum is zero, when the file is missing, or when `written_at` is more than 2 minutes old (the shell has stopped, or this terminal outlived it). When one or more projects are `unknown` or too old, the number gets a plus, `5+ in other projects`, and `/cockpit-needs` names which ones.
- **The button**: drawn whenever the sidecar answered the line route. It is the sign that the cockpit was read, which matters because both counts can be absent.

The plugin re-reads both sources every 10 seconds and after each `turn.complete`, and redraws only when the text changes.

## Delivery sequence

Across both repositories, in order:

1. **project-os-dev [[project-os-dev#TASK-0198-Two-Plugins-Share-The-Line-Above-The-Prompt-Checked-Live|TASK-0198]]**: the live check that two plugins can share the band above the prompt as the contract describes. If it fails, Edwin decides the fallback before step 4 here.
2. **Here, at any time, in any order**, because none of them touches the line:
   - [[TASK-0671-The-Shell-Keeps-A-File-Saying-What-Needs-You-In-The-Other-Projects|TASK-0671]]: the shell's `needs-elsewhere.json`.
   - [[TASK-0672-The-Sidecar-Answers-What-The-Line-Needs-In-One-Request|TASK-0672]]: `GET /api/cockpit/line`.
   - [[TASK-0675-Cockpit-Needs-And-Cockpit-Release-Answer-In-A-Pane-Without-A-Turn|TASK-0675]]: the two commands in a pane. Needs TASK-0671 and TASK-0672 for `/cockpit-needs`.
3. **project-os-dev TASK-0199 to TASK-0203**: the mod, its line, and the sync into this repository.
4. **Here**: [[TASK-0673-The-Cockpits-Facts-Join-The-End-Of-The-Project-Line|TASK-0673]] (the segment on the line) after TASK-0198, then [[TASK-0674-Open-In-Cockpit-Brings-The-Cockpit-Forward-On-The-Focus-Item|TASK-0674]] (the button's action). Both can be built and unit-tested against a fake `project-os:line` before step 3 finishes; the live look needs it.
5. **Here**: [[TASK-0676-The-Lines-Promises-Are-Proved-And-The-Register-Updated|TASK-0676]]: the guarantee tests, the register rows, the change note, TST-0097 made ready.
6. **Edwin walks** TST-0096 step 9 (FEAT-0159), project-os-dev TST-0047, and [[TST-0097-The-Cockpits-Counts-And-Open-Button-Sit-On-The-Project-Line|TST-0097]]. Then the independent reviews.

## Capability register

Each change note in this feature updates `docs/reference/cockpit-capability-register.md` in the same commit (CLAUDE.md, "A sibling application tracks this cockpit's capability"). Expected rows:

| key | new or changed | what it records | task |
| --- | --- | --- | --- |
| `shell.agents.claude-plugin` | changed | The plugin also draws the cockpit's segment on the project line and reads `needs-elsewhere.json`. | TASK-0673 |
| `shell.agents.project-line` | new | In a cockpit Claude terminal, this project's and the other projects' needs-you counts at the end of the project-os line, with the honesty rules above. | TASK-0673 |
| `shell.agents.open-in-cockpit` | new | The line's Open in cockpit button and the `cockpit://<workspace>/<focus>` link it opens. | TASK-0674 |
| `shell.agents.prompt-commands` | new | `/cockpit-needs` and `/cockpit-release`, answered in a pane with no Claude turn. | TASK-0675 |
| `shell.fleet.needs-elsewhere` | new | The shell's per-workspace file of the other projects' counts, refreshed every 30 s. | TASK-0671 |
| `api.read.line` | new | `GET /api/cockpit/line`, loopback only. | TASK-0672 |

Deck (`project-os-deck`) would see the line only through Claude Code, so most rows are "not applicable" there; the route and the file are what it could adopt.

## Dependencies

- **Hard:** [[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]] (done): the plugin and its sidecar address.
- **Hard, across repositories:** [[project-os-dev#FEAT-0041-Project-Os-Mod]]: TASK-0198 before TASK-0673; TASK-0203's sync before TST-0097 can be walked.
- **Hard:** Claude Code 2.1.300, the version the contract was read against.
- **No later phase.** FEAT-0041 is in no phase in project-os-dev and is being built now, by Edwin's decision. [[PHASE-045-The-Cockpit-In-Layers]] is not needed: the line uses today's obligations count.

## Impact analysis (2026-10-14)

Checked against the features, requirements and decisions sharing these areas. **No conflict.**

- [[REQ-0027-Every-Write-Guarded]]: no new write route. `GET /api/cockpit/line` reads; the shell's file is written by the main process into its own instrument folder.
- [[REQ-0019-Agent-Fleet-Visibility]] and ADR-0020 decision 3 (the badge total covers every kind): the line uses `total` from the same function, so it cannot leave a kind out.
- [[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]] (doing): TASK-0671 moves the home window's counting into a shared function. The window's behaviour must not change; its tests run unchanged.
- [[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]] (doing, waiting on TST-0096): it also edits `register.ts`. The new hooks are separate registrations; none changes `tool.check`.
- [[DES-0015-The-Cockpit-In-Layers]] is not accepted; nothing here depends on it.
- **Phase:** FEAT-0157 depends on another repository's unphased feature, not on a later phase here. The PHASE-046 note's Out of Scope said FEAT-0041 was out; it now says what changed and why.

## Risk scan (2026-10-14)

Triggers checked (LIFECYCLE, "Risk scan triggers"):

- **A directory layout or artifact path change: applies.** A new file in each instrument folder. It is under the app's own data folder, nothing is written under `~/.claude`, and the file holds counts and project names only. [[RISK-0004-Hook-Injection-Surface]] gains one line naming it (TASK-0676), as it names `hook-env`.
- **A security exposure: considered, small.** The plugin runs `open cockpit://<workspace>/<id>` through `$.process.run`, with an argument list and no shell. The workspace ID comes from the shell's file and the target from the sidecar; both are checked against a strict pattern before use (TASK-0674). The other projects' names appear in this project's terminal; that is the trade Edwin accepted with "only when non-zero".
- **A new dependency or version constraint: covered upstream.** The drawing contract with the project-os mod is the shared dependency; [[project-os-dev#RISK-0006-The-Project-Os-Mod-Runs-Unsandboxed-In-Every-Session-On-A-New-Interface]] records it. If a key changes, the cockpit's segment draws alone, which is visible.
- **A runtime increase: small.** One loopback GET and one file read every 10 seconds per Claude session; one file write per workspace every 30 seconds.
- **A new env var or configuration surface: none.**

No new `RISK-*` note.

## What the implementation must not do

- Show a number it could not read, or a count of zero for the other projects.
- Put a cockpit name, route or variable into anything under project-os's control.
- Draw its own line when the project-os line is there; it adds a segment.
- Run a shell command string; `open` gets an argument list.
- Start a Claude turn from `/cockpit-needs` or `/cockpit-release`.
- Change any `tool.check` verdict, or anything FEAT-0158 and FEAT-0159 built.
