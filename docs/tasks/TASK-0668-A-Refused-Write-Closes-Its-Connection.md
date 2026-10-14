---
type: "[[task]]"
id: TASK-0668
aliases: ["TASK-0668"]
title: "A write the sidecar refuses before reading its body closes the connection, so the next request on it is not misread"
status: done
phase: ""
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["Found while building [[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]]: desktop/tests/shell-secret.test.mjs sent two refused answers to a real sidecar and the second got 501, not 403"]
parent: "[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]"
effort: "S"
due: ""
depends: []
blocks: []
related: ["[[TASK-0632]]", "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"]
tests: []
---

# A refused write closes its connection

A client that sends a write the sidecar refuses, and then a second request on the same kept-alive connection, gets a wrong answer to the second one. The sidecar refuses a write with the wrong `Content-Type` (415) or from another machine (403) before it reads the body. It speaks HTTP/1.1 and keeps the connection open, so the unread body is still on the socket and is parsed as the next request line. Node's HTTP client keeps connections alive by default since Node 19, so the shell's own main process is such a client.

**How it was found.** TASK-0664's node test sent two answers without the secret to a real sidecar. The first got 403 and the second got 501. The secret guard was fixed in TASK-0664 (`close_connection`, and `_respond_json` now sends `Connection: close` when the handler is about to close). The two older guards, `_require_json_content_type` (TASK-0632, ISS-0301) and `_require_loopback`, have the same defect and are fixed here.

## Definition of Done

- [x] `_require_json_content_type` and `_require_loopback` set `close_connection` before they answer a refusal, so the response carries `Connection: close`.
- [x] A test sends two refused writes down one `http.client` connection and expects 415 for both; it fails without the fix.
- [x] TASK-0664's keep-alive test is changed to reuse one connection the same way.

## Steps

- [x] The two guards.
- [x] The tests, run with and without the fix.

## Built, 2026-10-14

`_require_json_content_type` and `_require_loopback` in `server.py` set `close_connection` before answering a refusal, and `_respond_json` (changed in TASK-0664) then sends `Connection: close`. `tests/test_write_content_type.py::test_two_refused_writes_on_one_connection_are_both_refused` sends two `text/plain` writes down one `http.client` connection: before the fix the second got a wrong status, after it both get 415. TASK-0664's test in `tests/test_shell_secret.py` now reuses one connection the same way.
