---
type: "[[issue]]"
id: ISS-0301
aliases: ["ISS-0301"]
title: "A framed page can POST to the sidecar's loopback-guarded write endpoints, because the guard asks where the request came from and the body parser never asks what content type it claims"
status: triage
phase: ""
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Independent review of FEAT-0147/FEAT-0148, 2026-09-12, finding 9: 'the sandbox denies reads, not writes ... a framed page has allow-scripts, knows its sidecar URL from location, and originates on the machine, so _require_loopback passes; it cannot read the reply and does not need to'"]
severity: medium
component: sidecar
parent: ""
related: ["[[ADR-0042-What-May-Be-Framed]]", "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]", "[[FEAT-0148-One-HTML-Viewer]]"]
tests: []
---

# A framed page can post to the write endpoints

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
