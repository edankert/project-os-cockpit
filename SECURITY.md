---
type: reference
id: SECURITY
owner: user:edwin
created: 2026-01-26
updated: 2026-08-12
tags: [security]
---

# Security

This tool reads and writes a developer's project records on their own machine, and serves them read-only to their own network. That is the whole of what it does, and it decides everything below.

## The threat model, stated

**What is being protected:** the record — twelve repositories of notes, plans and decisions — and the machine they sit on. One of those repos (`your-applications.com`) has a deploy target as its only remote, so a write there can publish a live website.

**Who is trusted:** the person at the Mac. Nobody else, including other devices on the same Wi-Fi. A home network is a boundary a router advertises; loopback is one the operating system enforces, and only the second is a security control.

**What is not defended against:** an attacker with local user access. If someone can run code as this user they already have the record, the SSH keys and the credentials; nothing here would help.

## The current model

**Reads are open on the LAN. Writes are loopback-only. There is no authentication.**

- The render server binds `0.0.0.0` deliberately, so a tablet on the same Wi-Fi can *read* the record ([[REQ-0013]]).
- Every mutation endpoint refuses a non-loopback peer ([[REQ-0027]]). This is not a safety net over an authorisation model — **it is the authorisation model**.
- The guard is enumerated rather than remembered: `test_every_note_mutating_endpoint_requires_loopback` parses the POST dispatch table out of `server.py`, so an endpoint added without the check **fails the suite by existing** ([[RISK-0005]]).
- It has been exercised for real, not only asserted: [[REL-0001]]'s verification drove every mutation endpoint over the LAN interface `192.168.68.123:8791` — **ten of ten returned 403 while reads returned 200**.
- The embedded terminal is off by default, loopback-bound when on, and refuses a non-loopback bind without an explicit escape hatch ([[RISK-0001]]). Shell access is a different hazard and keeps its own rule.

## The decided direction

[[ADR-0010]] option 4, 2026-08-12: **parity across surfaces is the goal, and authentication is its precondition.**

The browser cockpit will eventually do everything the shell does. It does not do so yet, and the reason is stated rather than dressed as a principle: nothing in this tool can currently answer *"who is asking"*. [[REQ-0034]] is that work. When it lands, the loopback check is **replaced** by proof of identity rather than removed, and every write verb crosses at once.

**Until then the current model holds in full.** An accepted direction is not a licence to drop a guard early, and [[REQ-0027]] says so at its own foot.

## Rules that do not change

- **No secrets in the record.** No credentials, tokens or proprietary binaries in notes or frontmatter.
- **Publishing is a person's act.** The tool commits; it never pushes on its own initiative, and a deploy remote is refused everywhere ([[FEAT-0055]]). [[ADR-0022]] permits a delegate to push to non-deploy remotes — the deploy refusal is untouched by it and is not negotiable.
- **Absence of proof is refusal**, never a fallback to "probably fine on a LAN".
- **A new mutation endpoint is guarded or it fails the build.** The check is structural on purpose: vigilance does not survive a refactor.

## Reporting

This is a personal tool with one user. If that changes, this section becomes a real one.
