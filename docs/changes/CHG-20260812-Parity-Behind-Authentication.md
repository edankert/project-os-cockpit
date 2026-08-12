---
type: "[[change]]"
id: CHG-20260812-Parity-Auth
title: "ADR-0010 decides option 4 — parity across surfaces, gated on an authenticated write path — and the notes that inherit it say so"
status: merged
date: 2026-08-12
owner: user:edwin
related: ["[[ADR-0010]]", "[[REQ-0034]]", "[[REQ-0027]]", "[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]", "[[RISK-0005-The-Write-Surface]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[ADR-0022]]", "[[FEAT-0098]]"]
tags: [change, security]
---

# Parity behind authentication

## What was decided

[[ADR-0010]] sat `proposed` since 2026-08-09 proposing **option 3** — *mode 1 is the reading surface, permanently*. Edwin accepted it as **option 2**, full parity, on 2026-08-12: *"we want to be able to support the same functionality across multiple surfaces… not sure how much of a concern the security issues raised are when used within very clear boundaries. But open for push back."*

The pushback, and his agreement with it, produced a fourth option.

**Option 4: parity is the goal, authentication is its precondition.**

## Why option 2 could not be taken as written

**The loopback check is not a safety feature on top of an authorisation model — it is the authorisation model.** There is no authentication anywhere in this tool. [[REL-0001]] drove every mutation endpoint over the real LAN interface: ten of ten returned 403 while reads returned 200. Remove that check and *"who may write here"* has no answer at all.

Three specifics sharpened it:

- **A LAN is a boundary a router advertises**; loopback is one the OS enforces. A guest phone, an IoT device or one compromised laptop is inside "clear boundaries".
- **One of these repos publishes a website.** `your-applications.com`'s only remote is a deploy target.
- **[[ADR-0022]] was accepted the same hour**, letting the delegate push to non-deploy remotes. Hold both at once and an unauthenticated LAN write can reach a remote. **Neither ADR sees that alone** — it exists only in the pair, which is the argument for deciding them against each other rather than in sequence.

And the reason not to simply keep option 3: it made the difference **permanent and principled**, which quietly converted *"we have not built authentication"* into *"the browser must never write"*. Those are different claims and only the first is true.

## What changed in the record

| note | change |
|---|---|
| [[ADR-0010]] | Option 4 added; Decision, Consequences and Status rewritten for it; `decided_option: "4"`; both accepts kept in the decision record, including the one that was reconsidered |
| **[[REQ-0034]]** | **New.** A non-loopback write proves who is asking. Absence of proof is refusal; the terminal stays out of scope; the mechanism is deliberately undecided |
| [[REQ-0027]] | States it is **unweakened** — the note a person opens to ask whether the rule still applies |
| [[REQ-0032]] | Gains a clause: a difference is on the record **and names what would end it** |
| [[RISK-0005]] | Records that it **re-opens before REQ-0034 lands**, and must re-close on new evidence rather than inherit the old closure |
| [[PHASE-029]] | Unblocked and reshaped; REQ-0034 joins it as a precondition; the reading half can start now |
| `SECURITY.md` | **Written.** It was still the template's `REPLACE ME` — on the one project whose live question is a security boundary |

## The trap this avoids

Starting the parity work, meeting the loopback check halfway through, and deleting it because it is in the way. The precondition is a phase member now, so it is scheduled rather than discovered — and [[REQ-0027]] and [[RISK-0005]] both say, in their own notes, that nothing has been relaxed yet.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: new ([[REQ-0034]]) · updated ([[REQ-0027]], [[REQ-0032]])
- tasks: not-applicable
- issues: not-applicable
- tests: not-applicable — no behaviour changed; the guards that exist are unchanged and still pass
- workflows: not-applicable
- decisions: updated ([[ADR-0010]] rewritten for option 4)
- risks: updated ([[RISK-0005]] — re-open condition recorded)
- changes: new (this note)
- snapshot: updated (counters, focus)
