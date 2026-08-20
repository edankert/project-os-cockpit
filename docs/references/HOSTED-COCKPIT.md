---
type: "[[reference]]"
id: HOSTED-COCKPIT
title: "Hosting the cockpit — the app on a server, the repos on people's own machines"
status: active
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
tags: [architecture, hosting, security, discussion]
related: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]", "[[REQ-0034-A-Non-Loopback-Write-Is-Authenticated]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[PHASE-033-The-Workspace-Is-Not-Always-Local]]", "[[RISK-0001-Render-Server-Exposure]]", "[[PHASE-040-The-Agent-Session-Is-Not-A-Terminal]]"]

---

# Hosting the cockpit

**This is a record of a discussion, not a decision.** Nothing here is agreed, scheduled or scoped. It exists so the next person to raise the idea starts from what was already worked out rather than from scratch.

Discussed 2026-08-20 (Edwin + agent).

## The idea

Host **the cockpit application** on a VPS. **Do not host the repos.** A repository lives on its owner's own machine, and the hosted web frontend links to — or connects through to — that machine.

This is deliberately *not* "put the repos on a server". The first analysis assumed that and was corrected: the point is a hosted **app** over locally-held **data**.

## The structural finding

**There is no separable app to host.**

The browser cockpit is **server-rendered HTML**. `navigateTo()` fetches a URL, parses the response and swaps `#cockpit-centre`'s `innerHTML`; the page is built by `templates.py` on the machine holding the repos. The client-side surface is tiny and entirely same-origin — measured 2026-08-20, `cockpit.js` reaches exactly five endpoints plus an SSE stream, all relative paths:

```
EventSource("/_events")          fetch("/api/cockpit/tab-state")
fetch("/api/terminal")           fetchJson("/api/cockpit/validation")
fetchJson("/api/cockpit/nav")    fetchJson("/api/cockpit/context")
```

There is no CORS support beyond one deliberately narrowed `.css` header, whose own comment reads *"narrowing to `.css` is so this does not quietly become blanket CORS."*

So the work is **not hosting**. It is **building a client that does not exist yet** — an SPA talking to an API across an origin boundary. That is [[PHASE-029]]'s eleven views plus [[FEAT-0084]]'s shared view vocabulary, retargeted: rather than porting server-rendered pages into `cockpit.js`, the API contract gets defined once and rendering moves entirely client-side. It makes FEAT-0084 load-bearing rather than housekeeping.

## Three transport problems

All solvable, none free:

- **NAT** — the owner's machine is not addressable from the internet, so it must dial *out* and something must relay.
- **Mixed content** — an HTTPS page cannot fetch `http://192.168.x.x`; browsers block it outright. A relay terminating TLS sidesteps this; a direct connection does not.
- **Authentication** — [[REQ-0034]]. Unavoidable here: nothing is on loopback any more, and [[ADR-0010]] is explicit that *"the loopback check is not a safety feature on top of an authorisation model. It **is** the authorisation model."*

### Transport options

**Edwin's answer: design for both, decide later** — keep the transport a seam rather than a commitment.

| | Tailscale | Relay on the VPS |
|---|---|---|
| Reaches through NAT | yes | yes |
| VPS sees your data | **no** — serves the client only | **yes** — relays it |
| Client software needed | Tailscale on every device | none, any browser |
| Who builds the transport | nobody | you |
| Identity | tailnet does it | REQ-0034, for real |

T3 Code has built the relay version and is a working reference: a relay with **separate credentials, issuers and trust boundaries** from the environment server, and DPoP-bound proof-of-possession tokens so a leaked credential cannot be replayed.

## The audience answer changes the size of this

Asked who it is for, Edwin answered **public / anyone**.

That converts REQ-0034 from *"authenticate a write"* into accounts, tenancy, per-user isolation, abuse handling and support. **That is a product, not a phase**, and it should be said plainly before anyone scopes it.

It also means the thing being described — a hosted control plane for other people's machines — is close to what T3 Code already is. Worth being explicit about the difference: **T3 runs agents; the cockpit is the project-os record** — phases, obligations, the release gate, the review desk. Complementary rather than competing, but the overlap in *transport and auth* is near-total, which is the strongest argument for solving them once (see [[PHASE-040]]).

## Neighbouring work already on the record

[[PHASE-033]] — *"The workspace is not always local"* — is `planned` and unstarted, and its title is nearly this question. But its shape is **different**: SSH out to a remote workspace, keeping the trust boundary on your Mac. Hosting moves the boundary to the VPS. Those are not the same architecture and the record has not yet chosen between them.

It carries FEAT-0099, REQ-0035/0036, ADR-0026 (remote transport), RISK-0007 (remote trust boundary) and TST-0024.

## Should the cockpit move to Node?

Asked and answered **no**, for a reason that is not about line count:

`tools/scripts/*.py` is **template-owned**, synced from upstream `project-os`, used by all twelve repos. The cockpit does not own it. Converting to Node does not convert those — you would either keep shelling out to Python, or fork the fleet's tooling for one repo. And `validate_docs_bundled.py` must stay **byte-identical** to `tools/scripts/validate-docs.py`, enforced by `diff -q` in the suite — a guarantee that exists precisely *because* they are one language.

Could T3's implementation be rebuilt in Python? The **plumbing** yes, and cheaply — PTYs, a WebSocket server, an event log. The **adapters** are the real cost: parsing Claude Code's and Codex's stream formats and keeping up as those CLIs change, against a moving target, permanently. Rebuilding would mean owning the hard part to avoid borrowing the easy one.

## What would have to be true

Not a plan — the preconditions any plan would inherit:

1. A real client exists (PHASE-029 / FEAT-0084, retargeted to cross-origin)
2. REQ-0034 is implemented, at whatever scale the audience answer demands
3. A transport is chosen, or the seam is genuinely built for both
4. The relationship to PHASE-033 is decided rather than left as two overlapping plans
5. Someone has said out loud whether "public" is the goal or the horizon

## Corrections made during this discussion

Kept because each was stated confidently and was wrong:

- **"Host the app, not the repos" was misread** as "put the repos on a VPS", and the first analysis answered the wrong question entirely.
- **"T3 has native iOS and Android apps"** — it does not. Web app in a mobile browser. Taken from marketing copy and repeated unchecked.
- **"A Node service in a Python + Electron fleet"** framed Node as foreign. Electron *is* Node; `desktop/src` is 24,240 lines of TypeScript against 33,509 of Python. The repo has been bilingual all along.
