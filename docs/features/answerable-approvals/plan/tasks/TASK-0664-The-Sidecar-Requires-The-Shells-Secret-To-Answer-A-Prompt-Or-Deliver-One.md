---
type: "[[task]]"
id: TASK-0664
aliases: ["TASK-0664"]
title: "The sidecar requires the shell's secret to answer a permission prompt or to hand a prompt to a Claude session, and gets it on standard input at spawn"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]], candidate task 1", "plan/PLAN.md, 'The secret'", "Edwin 2026-10-14: the secret on the answer route and the dispatch route, not every write route"]
parent: "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"
effort: "M"
due: ""
depends: []
blocks: ["[[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]", "[[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]"]
related: ["[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]", "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]", "[[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]", "[[RISK-0005-The-Write-Surface]]", "[[REQ-0027-Every-Write-Guarded]]"]
tests: []
---

# The sidecar requires the shell's secret on two routes

After this task, `POST /api/cockpit/approve` and `POST /api/cockpit/deliveries` refuse any request that does not carry the secret the desktop shell made when it spawned that sidecar. Dispatching a prompt to a Claude session from the cockpit window, or with `cockpit dispatch`, works exactly as before, because the shell's main process sends the secret. Every other route is unchanged.

## Definition of Done

- [x] `spawnSidecar` in `desktop/src/ipc/sidecar.ts` makes a new secret per spawn (32 bytes from `crypto.randomBytes`, hex), keeps it on the sidecar's record in memory, spawns Python with `--secret-stdin` and `stdin: 'pipe'`, writes one JSON line `{"secret": ..., "approval_wait_ms": ...}`, and closes standard input.
- [x] `approval_wait_ms` comes from `approvalWaitMs` on the workspace's record in `workspaces.json`: absent means 5000, clamped to 0 to 30000. The `Workspace` type gains the optional field.
- [x] `__main__.py` reads exactly one line from standard input when, and only when, `--secret-stdin` is given, before the server binds. A missing or malformed line stops the sidecar with a clear error on stderr that does not print the line. Without the flag, startup is unchanged and the server has no secret.
- [x] `make_server` takes the secret and the wait. `_serve_approve` and `_serve_delivery_add` check, in this order: loopback, JSON content type, then the `X-Cockpit-Secret` header against the secret with `hmac.compare_digest`. Missing, wrong, or no secret configured: 403 with one message that does not say which.
- [x] `handToSidecar` in `dispatch-queue.ts` sends the header. A main-process helper returns the secret for a workspace's sidecar; nothing exports it to the renderer.
- [x] The secret is not in the sidecar's argv or environment, under `.cockpit/`, in the `hook-env` file or the instrument directory, in any terminal's environment, in stderr, or in any response body, including `/api/cockpit/state`.
- [x] `approvals.answer` is unchanged: `agent:principal` is still accepted, any other `agent:` actor is refused (Edwin, 2026-10-14).
- [x] pytest cases that fail when: an answer without the header is accepted; an answer with a wrong secret is accepted; a server started without a secret accepts an answer that names any secret, including an empty one; a delivery without the secret is added; `POST /api/cockpit/dispatch` with `enqueue` stops working without a secret (it must keep working); the plugin's `claim`, `started` and `dropped` start requiring it (they must not).
- [x] A node test that the spawn writes the line and closes stdin, and that `handToSidecar` sends the header.
- [x] `tests/test_remote_peer_refusal.py` and `tests/test_write_content_type.py` still pass; any count they keep is updated with a dated reason.

## Steps

- [x] `--secret-stdin` in `__main__.py`, the values through `make_server`.
- [x] The check on the two routes.
- [x] The shell: make, send, keep; the header in `handToSidecar`; `approvalWaitMs`.
- [x] Tests.

## Notes

- The plan's table says which routes are left without the secret and why. `cancel` is one of them; the main process could send the header at no cost, but Edwin scoped the secret to two routes.
- `pythonExecutable` is exported for FEAT-0028's cold-workspace pass, which spawns its own Python. Check whether that process serves the guarded routes. If it does not, it needs no secret; record which in this note when the task is built.
- Live harnesses that start a sidecar by hand (the acceptance-walk venue) will get 403 on the two routes. That is correct; a harness that needs them passes `--secret-stdin` itself.

## Built, 2026-10-14

**What a person notices:** nothing yet. Dispatching to a Claude session from the cockpit works as before. A request to answer a permission prompt, or to hand a prompt to a Claude session, that does not come from the shell's main process now gets 403.

- **Where the secret lives.** `spawnSidecar` makes it with `randomBytes(32)`, keeps it on the sidecar's record, and writes `{"secret", "approval_wait_ms"}` as one line to the child's stdin, then closes it (`desktop/src/ipc/sidecar.ts`). `sidecarSecretFor(workspaceId)` is the only reader, and `handToSidecar` in `dispatch-queue.ts` is its only caller so far. `__main__.py` reads the line only under `--secret-stdin` (`read_shell_line`), and a bad line stops the sidecar with exit code 2 and a message that does not repeat it.
- **The guard.** `_require_shell_secret` in `server.py`, called after `_require_loopback` and `_require_json_content_type` on `/api/cockpit/approve` and `/api/cockpit/deliveries`. A server started without the flag refuses every request on both.
- **A defect the node test found, fixed here.** The guard answers before reading the body. The handler speaks HTTP/1.1 keep-alive, so the unread body was parsed as the next request on that connection: a second refused answer got 501, then a hung-up socket. The guard now sets `close_connection`, and `_respond_json` sends `Connection: close` whenever the handler is about to close, which also corrects the existing payload-too-large refusal on `/api/agent-hook`. `test_a_refusal_closes_a_kept_alive_connection_cleanly` guards it. The content-type and loopback refusals have the same defect and are fixed under their own task.
- **FEAT-0028's Python runs need no secret.** `fleet-health.ts` runs `pythonExecutable()` twice, for `project_os_cockpit.fleet_validate` and `fleet_git`. Neither starts a server, so neither serves the guarded routes.
- **Tests that changed.** `test_remote_peer_refusal.py::test_a_loopback_peer_is_not_refused` now starts its server with a secret and sends it, because otherwise the two routes answer 403 for a reason that test is not about. `test_deliveries.py` sends it on its three delivery posts. The three node tests that stub `./sidecar` gained `sidecarSecretFor`; `submitted-dispatch.test.mjs` now asserts every delivery carries the header.
- **Mutation check.** With `_require_shell_secret` returning `True` first, six cases in `test_shell_secret.py` fail; restored, all pass.
