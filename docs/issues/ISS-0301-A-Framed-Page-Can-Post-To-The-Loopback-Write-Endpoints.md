---
type: "[[issue]]"
id: ISS-0301
aliases: ["ISS-0301"]
title: "A web page shown in the cockpit's viewer can change your notes through the sidecar, because the sidecar accepts any request that comes from this machine"
status: open
phase: ""
owner: user:edwin
created: 2026-09-12
updated: "2026-09-20"
reported_by: review
source: ["Independent review of FEAT-0147/FEAT-0148, 2026-09-12, finding 9: 'the sandbox denies reads, not writes ... a framed page has allow-scripts, knows its sidecar URL from location, and originates on the machine, so _require_loopback passes; it cannot read the reply and does not need to'"]
severity: medium
component: sidecar
parent: ""
related: ["[[ADR-0042-What-May-Be-Framed]]", "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]", "[[FEAT-0148-One-HTML-Viewer]]"]
tests: []
---

# A page shown in the viewer can change your notes through the sidecar

A script inside an HTML file that the cockpit's viewer shows can send requests that change notes, the review queue or the inbox, and the sidecar carries them out. The script cannot read the reply, but it does not need to: the change happens anyway.

## Problem

The sidecar's write endpoints are guarded by `_require_loopback`, which asks **where the request came from**. A page framed by the viewer runs on the same machine, so it passes.

The sandbox does not stop it. `sandbox="allow-scripts"` without the same-origin flag means the frame cannot **read** a reply — it has an opaque origin — but nothing stops it **sending**. And `_read_json_body` (`server.py:1714`) ignores `Content-Type`, so a request a browser will send cross-origin without a preflight — `text/plain` — is parsed as JSON all the same.

Demonstrated by the reviewer against a real sidecar:

```
curl -X POST -H 'Content-Type: text/plain' -d '{"kind":"bogus"}' …/api/cockpit/review-request
→ unknown kind: bogus      (the body was parsed)
```

A framed page knows its own sidecar's URL from `location`, so it can address every one of those endpoints.

## Why this is filed rather than fixed here

**It predates the viewer.** The same was true of the design bench, which framed pages with `allow-scripts` from the same origin-less sandbox, and of any note body that renders raw HTML. [[ADR-0042-What-May-Be-Framed]] widened *which files* may be framed, not what a framed file may do.

What the ADR and [[RISK-0008-The-Sandbox-Is-The-Only-Boundary]] got wrong is the **wording**: both say the sandbox is the boundary, which is true for reads and false for writes. RISK-0008 is corrected to say so.

## What would fix it

Two candidates, neither started:

- **Refuse a body whose `Content-Type` is not `application/json`.** Cheap, and it removes the no-preflight path. It does not stop a page that sets the header, but such a request is preflighted and the sidecar can refuse the preflight.
- **A token the shell knows and a framed page does not.** The real fix, and a bigger one: every write endpoint requires it, the shell sends it, and `_require_loopback` stops being the only gate.

The threat is bounded — a framed page is a file already inside `docs/`, so an attacker who can write one can usually write the others — but "the attacker already won" is not why a guard should hold.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** Nothing, until an HTML file under `docs/` carries a hostile script. Opening that file in the viewer would then let it make changes to the project, such as moving a note's status or queueing a review, without the person clicking anything.

Evidence (the class of flaw is a cross-site request that needs no preflight; no exploit was written): the only gate on the sidecar's write routes is `_require_loopback` at `src/project_os_cockpit/server.py:1917`, which checks the client address alone (30 call sites, `grep -c "_require_loopback(" server.py`). `_read_json_body` at `server.py:1889` reads `Content-Length` and parses the body as JSON without looking at `Content-Type`, so a `text/plain` body, which a browser sends cross-origin without asking permission first, is accepted. `grep -n "Origin\|Sec-Fetch-Site\|Referer" server.py` finds no check of where the request came from, only two `Access-Control-Allow-Origin: *` headers on read responses (lines 3943, 4233). The viewer frames pages with `sandbox="allow-scripts"` (`desktop/src/renderer/renderer.ts:6389`), which stops reading replies but not sending requests, and the framed file is served with no Content-Security-Policy (`server.py:3176-3181`). No commit since 2026-09-12 changed either function.

Small fix: yes for the first half. Refusing a body whose `Content-Type` is not `application/json` is one place in `_read_json_body` and a test can fail without it. The cockpit's own hook forwarders already send that header (`desktop/src/ipc/agent-instrument.ts:90,110,138`); other clients, such as Deck and `cockpit signal`, must be checked before the refusal lands. Checking the `Origin` or `Sec-Fetch-Site` header on writes is a second cheap layer. A secret token that only the shell knows is the full fix and is bigger.

**Belongs to:** no feature (related to FEAT-0148 and RISK-0008). **Next:** refuse non-JSON bodies on write routes with a test, then decide on the token separately.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).

## The fix is made and is waiting for Edwin to see it (2026-09-20, TASK-0632)

**This issue stays `open` on purpose.** [[ISS-0313]] marks it *"Security: show Edwin before closing"*, and a security change that closes itself has had one reviewer. The code is committed; the status is the thing being held.

### What to look at

`src/project_os_cockpit/server.py`, the new `_require_json_content_type`. A write whose `Content-Type` is not `application/json` is refused with **415 Unsupported Media Type**, before the body is read.

```
$ curl -X POST -H 'Content-Type: text/plain' -d '{"kind":"bogus"}' .../api/cockpit/review-request
{"ok": false, "error": "a write must say Content-Type: application/json; this one said 'text/plain'"}
```

Before: `unknown kind: bogus`, which is the route reporting that it read and understood the body.

### Why this specific header closes anything

A browser sends a cross-origin POST **without asking permission first** only while the `Content-Type` is one of three "simple" values: `text/plain`, `application/x-www-form-urlencoded`, `multipart/form-data`. Requiring `application/json` forces a preflight, and the sidecar answers no preflight. All four are refused by the tests, and so is an absent header — every client this repo knows sends one, and "absent" is what a hand-rolled `fetch` from a framed page produces.

### Checked before it landed, as the ticket asked

**Every client already sends the header.** No client change was needed and nothing was broken.

| client | where | sends it |
| --- | --- | --- |
| Electron renderer | `desktop/src/renderer/renderer.ts` — six POST sites | yes |
| sidecar's own page | `src/project_os_cockpit/static/cockpit.js:154` | yes |
| `cockpit` CLI, including `cockpit signal` | `src/project_os_cockpit/cli.py:84` | yes |
| agent hook, statusline and Codex notify forwarders | `desktop/src/ipc/agent-instrument.ts` — `curl -H 'Content-Type: application/json'` in all three emitted scripts | yes |
| dispatch queue | `desktop/src/ipc/dispatch-queue.ts:147` | yes |
| **project-os-deck** | `desktop/src/shared/write-client.ts:223-225` — its single `post()`, which every sidecar write goes through | yes |

Deck's `/deck/sidecar/` proxy forwards **reads only** (`desktop/src/main/host.ts`, `READ_METHODS`), so it is not a second path in.

### It covers more routes than the report described

The report named `_read_json_body`. Five write handlers had their own copy of that body reader and would have kept the hole: `/api/cockpit/agent-state`, `/api/cockpit/dispatch`, `/api/notes/check-toggle`, `/api/cockpit/focus` and `/api/cockpit/tab-state`. All five now call the shared reader, which also gives them the size cap their copies never had. `/api/agent-hook` keeps its own reader — it refuses an empty body and drops the connection on an oversized one — and calls the guard directly.

### Which test guards it

`tests/test_write_content_type.py`, nine cases. The reviewer's curl run as itself; the same request with the right header still reaching the route; all four no-preflight content types plus the absent one; `application/json; charset=utf-8` accepted, because refusing it is how a guard becomes the thing someone disables; and a sweep over **every** guarded POST route in the dispatch table, so a route that grows its own body reader fails here instead of falling out silently.

**Run both ways.** With the guard: `9 passed`. With `server.py` reverted: `7 failed, 2 passed`. The ten write-path suites around it pass 159.

### What this does NOT fix

- **A page that sets the header.** It is then preflighted, and the sidecar refuses no preflight because it answers none. The day something answers one, this guard stops mattering.
- **The `Origin` / `Sec-Fetch-Site` check**, the cheap second layer the report suggests. Not made.
- **A secret the shell knows and a framed page does not.** That is the real fix, and it is a bigger change: every write endpoint requires it, the shell sends it, and `_require_loopback` stops being the only gate. Not started.
- **No Content-Security-Policy** on a framed file (`server.py`, the `/framed/` response).

[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]] should be re-read against this, and is not amended here.

### To close this

Edwin reads the above, runs the curl if he wants to, and says so. Then the status goes to `fixed`.
