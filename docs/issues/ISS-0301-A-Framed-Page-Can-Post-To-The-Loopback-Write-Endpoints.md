---
type: "[[issue]]"
id: ISS-0301
aliases: ["ISS-0301"]
title: "A web page shown in the cockpit's viewer can change your notes through the sidecar, because the sidecar accepts any request that comes from this machine"
status: open
phase: ""
owner: user:edwin
created: 2026-09-12
updated: "2026-09-19"
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
