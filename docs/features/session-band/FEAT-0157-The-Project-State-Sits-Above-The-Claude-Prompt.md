---
type: "[[feature]]"
id: FEAT-0157
aliases: ["FEAT-0157"]
title: "The cockpit's facts join the project line above the Claude Code prompt, and cockpit commands answer there without spending tokens"
status: doing
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-08
updated: 2026-10-21
source:
  - "Edwin 2026-10-08: 'Plan the implementation in a new phase.'"
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]], 'Advisory hooks would stop paying context rent'"
  - "Edwin 2026-10-14, in project-os-dev, on which mod uses belong in project-os and which in the cockpit: 'yes, file them and update FEAT-0157'"
  - "Edwin 2026-10-14: 'Can we first implement the rest of the features in this phase and then test!', and his answers that day: 'Build FEAT-0041 too' (project-os's mod and its line upstream first, then this feature, then test) and 'Only when non-zero' for the other projects' count"
goal: "A person working in a cockpit Claude session sees, on the project line above the prompt, what the cockpit knows and the repo cannot: what needs them in this project and in the others, with a button that opens it in the cockpit. Commands typed at the prompt ask the cockpit a question without the model reading the answer."
requirements: []
tasks:
  - "[[TASK-0671-The-Shell-Keeps-A-File-Saying-What-Needs-You-In-The-Other-Projects]]"
  - "[[TASK-0672-The-Sidecar-Answers-What-The-Line-Needs-In-One-Request]]"
  - "[[TASK-0673-The-Cockpits-Facts-Join-The-End-Of-The-Project-Line]]"
  - "[[TASK-0674-Open-In-Cockpit-Brings-The-Cockpit-Forward-On-The-Focus-Item]]"
  - "[[TASK-0675-Cockpit-Needs-And-Cockpit-Release-Answer-In-A-Pane-Without-A-Turn]]"
  - "[[TASK-0676-The-Lines-Promises-Are-Proved-And-The-Register-Updated]]"
  - "[[TASK-0679-FEAT-0157-Review-Round-1-Fixes]]"
release: ""
acceptance_exception: ""
acceptance: "[[TST-0097-The-Cockpits-Counts-And-Open-Button-Sit-On-The-Project-Line]]"
design: ""
related:
  - "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
  - "[[project-os-dev#FEAT-0041-Project-Os-Mod]]"
  - "[[project-os-dev#REFERENCE-PROJECT-LINE-CONTRACT]]"
  - "[[project-os-dev#ISS-0106-Project-Os-As-A-Plugin]]"
  - "[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"
  - "[[DES-0015-The-Cockpit-In-Layers]]"
  - "[[PHASE-045-The-Cockpit-In-Layers]]"
  - "[[ISS-0277-Nothing-Detects-A-Stale-Or-Broken-Vendored-Cockpit]]"
  - "[[RISK-0004-Hook-Injection-Surface]]"
reviewed_by: ["model:claude-opus-5-5 (independent-reviewer, round 1, A)", "model:claude-opus-5-5 (independent-reviewer, round 1, B)"]
review_date: 2026-10-21
review_verdict: changes-requested
review_round: 1
---

# The cockpit's facts join the project line above the Claude prompt

**Started 2026-10-14.** The project line itself is built first, upstream, by [[project-os-dev#FEAT-0041-Project-Os-Mod]]; Edwin chose that order ("Build FEAT-0041 too"). The delivery plan is `plan/PLAN.md`; the acceptance check is [[TST-0097-The-Cockpits-Counts-And-Open-Button-Sit-On-The-Project-Line|TST-0097]].

## Acceptance Criteria

Written 2026-10-21, after round 1 of the review found the note had none. Each restates a Scope item or a promise the change note makes, as something a walk or a test can show.

1. In a Claude session in a cockpit terminal, the project line ends with "N needs you" (one) or "N need you" (more) when this project owes something. N is the sidecar's needs-you total, the same number as the cockpit's badges.
2. It shows "M in other projects" only when M is above zero. M sums the other projects' counts that are under a day old, from a file the shell rewrote within the last 2 minutes. It reads "M+" when any project's count is missing or older. It never reads 0.
3. When this project's sidecar does not answer, this project's count and the button are left out; nothing is shown as 0.
4. `[ Open in cockpit ]` opens `cockpit://<workspace>/<focus item>`, or `cockpit://<workspace>` when nothing is in focus, and the cockpit window comes forward there. The button needs only the sidecar's answer, not the other projects' file.
5. `/cockpit-needs` and `/cockpit-release` open a pane with the answer and start no Claude turn. `/cockpit-release`'s blocked count is the release gate's own count.
6. In a narrow terminal the cockpit's part is cut before project-os's facts.
7. In a terminal the cockpit did not open, or with `COCKPIT_NO_INSTRUMENT` set, neither the cockpit's part nor the two commands appear.
8. `GET /api/cockpit/line` refuses a request from another machine, and answers 500, never a zero, when it cannot read.

## Review

**Round 1, 2026-10-21: changes-requested.** Two `independent-reviewer` sessions (A and B) worked from the same packet in clean contexts. Both are the same model as the author (`claude-opus-5-5`); independence here is the clean context (ADR-0013).

| # | Claim | Combined verdict | Evidence |
|---|---|---|---|
| 0 | The feature's acceptance criteria | refuted: none existed | Both. Written above, 2026-10-21. |
| 1 | This project's count is the badges' total | holds | Both: `line_payload` returns `badges["total"]`. Removing the route's `_require_loopback` failed `test_another_machine_is_refused` and the guard-count test. |
| 2 | The other projects' count: written by the shell, shown only above zero and fresh | holds | Both: `sum > 0` → `sum >= 0` failed one plugin test; removing the 2-minute check failed one; removing the self-row filter and making a missing answer 0 each failed `needs-elsewhere.test.mjs`. |
| 3 | The home window and the file give one project the same number | holds | A: removing `row.owedCount = owed.total` failed the comparison test. A noted one case where they still differ (see below). |
| 4 | Open in cockpit opens the focus item | holds up to the link; the window is TST-0097 step 5 | Both. Both noted the button appears only once the shell's other-projects file exists, because the workspace ID came from it. |
| 5 | The two commands answer in a pane with no turn | holds | Both: `immediate: true`, the handler returns `{}`, plugin test "each command opens its pane and starts no turn". |
| 6 | TST-0097 guards the behaviour | not checked: never walked | Both. Step 2 expects M to equal the home window's sum, which a day-old count makes untrue. |

**The packet was incomplete.** It left out `a204091`, which holds the plugin's segment, button and commands (about 300 lines of `register.ts`). Its subject names only TASK-0673 to TASK-0676. The packet script read the feature's `tasks:` field only when written on one line, and this note writes it as a block list. Both reviewers followed `line.test.ts` into `register.ts` for claims 2, 4 and 5. Fixed in the template: project-os-dev TASK-0210.

**Other observations, and what was done:**

- The button waits for the other-projects file (both): **fixed**, the workspace ID now comes from the instrument folder's name ([[TASK-0679-FEAT-0157-Review-Round-1-Fixes|TASK-0679]]).
- "1 need you" (B): **fixed**, "1 needs you".
- `/cockpit-release` said "Blocked: N" with N the checks owed for this release's own features, not the gate's count (A raised it unchecked): **fixed**. Checked live first: the gate blocked on 6, the pane would have said 3.
- TST-0097 step 2's wording (both): **fixed**, it now compares fresh counts and expects "+" for a stale one.
- When the line route fails, the line keeps old facts (A): **does not hold**. `sidecarCall` returns `undefined` on any failure and never throws, so `readLine` sets `line.answer` to undefined and redraws without the count and the button. Only a failing clock would reach the catch that keeps old facts.
- The home window marks a project "not read" when `/landing` or `/stats` fails, while the file uses the live total (A): **comment corrected** in `home-window.ts`; the number, when both show one, is the same.
- The refresh calls in `sidecar.ts` and `main.ts` have no test (A): recorded; TST-0097 steps 2 to 4 are where they are seen.
- CLAUDE.md's "all 69 were current" (A): **updated** to the current count.
- The note's `updated:` date (both): **updated**.

## Goal

One line above the Claude Code prompt shows where the project stands. Its project half belongs to project-os, because it can be read from the repo and should appear in every session, in every repo, inside the cockpit or not. That half is the focus item with its status and phase, the validator's error count, the routing hint, and the wrong-model warning. This feature adds the cockpit's half to the same line: how many things need the person in this project, how many in the other projects, and an "Open in cockpit" button. It also adds commands that ask the cockpit a question at the prompt and answer in a pane, without starting a turn. Nothing on the line costs tokens, because the model never reads it.

## Scope

**In this feature (the cockpit's half):**

- The needs-you count for this project, from the sidecar's obligations total.
- The count for the other projects, shown only when it is above zero and fresh. A sidecar knows only its own project, so the shell, which sees every project, writes this number to a file the plugin reads.
- An "Open in cockpit" button that brings the cockpit forward on this project's focus item.
- Two commands that answer from the sidecar, drawn in a pane: what is owed across projects (`/cockpit-needs`), and where a release stands (`/cockpit-release`). These are the two questions the `cockpit` CLI cannot answer today, per the 2026-10-13 sort note in project-os-dev.

**In project-os ([[project-os-dev#FEAT-0041-Project-Os-Mod]]):**

- The line itself, the focus item, its status and phase, and the validator's error and REVIEW-STALE counts.
- The `session.start` check that the session's model matches the pin.
- The routing hint (HC-008) on the line.
- Commands that only run a repo's own scripts (`/pos-q <ID>`, `/pos-validate`, `/pos-where`), later.

## Findings

- **One line, drawn once, joined in the drawing.** The project-os mod draws the line. The cockpit plugin adds its segment to the end of it through Claude Code's drawing chain: each `ui.render` hook gets the tree drawn beneath it from `next(e)` and can add to it. Whichever plugin's hook is outer joins the two, so their order does not matter. project-os never names the cockpit, its service or its variables. The rules are [[project-os-dev#REFERENCE-PROJECT-LINE-CONTRACT]].
- **Why not have the mod call the sidecar.** The cockpit plugin reads the sidecar's address from `$COCKPIT_INSTRUMENT_DIR/hook-env` on every call, because the sidecar can restart on a new port; it refuses any address not on this machine, and honours `COCKPIT_NO_INSTRUMENT` (`desktop/plugin/claude-code/hooks/register.ts`, `sidecarUrl`). The mod would have had to repeat all of that in another repository.
- **Where the numbers come from.** This project's count is the sidecar's obligations `total` (`GET /api/cockpit/obligations`, `obligations.badges_payload`), the same number the cockpit's badges show. No sidecar route covers the fleet. The only code that gathers every project's count is the shell's draft home window (`desktop/src/ipc/home-window.ts`, `buildProject`): live sidecars first, then the cold digest's `needsYou` with its `computedAt` from `fleetHealth()`. The line's number for the other projects must come from the same code, so the window and the line agree.
- **How the shell hands the number over.** The shell already writes `hook-env` into each workspace's instrument folder, and the plugin reads it with `$.fs.read` (`desktop/src/ipc/agent-instrument.ts`, `setSidecarUrl`). A second small file beside it carries the other projects' counts.
- **Commands.** `$.command.register` with `immediate: true` runs a command with no Claude turn. Built-in names such as `/focus` are reserved, so the names carry a prefix. A command that returns `{}` and draws in a `Pane` keeps its output away from the model. A command's answer is computed by code, not by the AI, so its counts can be trusted.
- **The button.** The shell already handles `cockpit://<project>/<target>` links, where the project may be the shell's workspace ID and the target a note ID (`desktop/src/main.ts`, `handleDeepLink`; `desktop/src/renderer/deep-link.ts`). On macOS `open cockpit://...` brings the running app forward. The plugin can run it with `$.process.run`.
- **This is DES-0015's first layer inside Claude Code.** [[DES-0015-The-Cockpit-In-Layers]] calls it L0, the glance. That design is not accepted ([[PHASE-045-The-Cockpit-In-Layers]]), so the line uses today's obligations count.
- **The vendored cockpit.** [[ISS-0277-Nothing-Detects-A-Stale-Or-Broken-Vendored-Cockpit]] has no check today. This feature does not build one.
- **Drawing appears only in the terminal and the Desktop app's Code tab.** Other front ends see nothing. That is acceptable, because the cockpit's windows show every fact on the line.

## Decisions

1. **The cockpit commands live in the cockpit's own plugin** (`desktop/plugin/claude-code/`), which loads only in cockpit terminals. project-os never names a cockpit command. Settled 2026-10-14 by the coordinating session, on this note's recommendation.
2. **"Open in cockpit" uses a `cockpit://` link**, which the shell already handles (`desktop/src/main.ts`, TASK-0064, ISS-0293). Settled 2026-10-14 by the coordinating session; no new sidecar call is needed.
3. **The other projects' count is on the line only when it is above zero** (Edwin, 2026-10-14: "Only when non-zero"). It is also left out when the shell's file is missing or old. It is never shown as 0.
4. **The cockpit joins the line through the drawing, not through a call from the project-os mod** (coordinating session, 2026-10-14), so project-os stays free of cockpit knowledge, for the same reason as decision 1.

## Verification

Full run on 2026-10-21, project-os-cockpit 541bba6, after the push and with every later commit from other sessions included:

- `.venv/bin/python -m pytest -q` (Python 3.13): 2254 passed, 10 skipped.
- `node --test tests/*.test.mjs` in `desktop/` after `npm run build`: 229 tests, 229 pass.
- `claude plugin test .` in `desktop/plugin/claude-code` (Claude Code 2.1.303): 62 pass, 0 fail.
- CI on 65c6de9: validate-docs (Python 3.12, Linux) and observed-coverage (Python 3.11, macOS, Claude Code 2.1.300) both green, after TASK-0677 fixed one test that failed before Python 3.13.

## Links

- Phase: [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]
- The project half: [[project-os-dev#FEAT-0041-Project-Os-Mod]]
- The contract: [[project-os-dev#REFERENCE-PROJECT-LINE-CONTRACT]]
- Code: `desktop/plugin/claude-code/hooks/register.ts`, `desktop/src/ipc/agent-instrument.ts`, `desktop/src/ipc/home-window.ts`, `src/project_os_cockpit/obligations.py`, `src/project_os_cockpit/server.py`
