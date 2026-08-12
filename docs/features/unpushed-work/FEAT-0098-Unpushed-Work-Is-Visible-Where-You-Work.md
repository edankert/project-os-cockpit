---
type: "[[feature]]"
id: FEAT-0098
aliases: ["FEAT-0098"]
title: "Unpushed work is visible where you work — the overview carries this workspace's unpushed count and its push, instead of hiding both on the fleet screen"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
source: ["Edwin 2026-08-12, accepting ADR-0022 option 3: 'if not pushed automatically then this should clearly be identified in the tool and should be automated for the human to do this by possibly creating some kind of button'"]
goal: "The overview says when this workspace has commits nobody has published, and offers the push — the same action, with the same deploy-remote refusal, on the surface a person lands on."
requirements: []
tasks:
  - "[[TASK-0404-Unpushed-On-The-Overview]]"
related: ["[[ADR-0022]]", "[[FEAT-0055]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
tests: []
---

# Unpushed work is visible where you work

## Goal

**Both halves of Edwin's request already exist, in the wrong place.** [[FEAT-0055]] built a `Not pushed — N commits across M repos` section with a `Push N` per repo and a disabled `deploy remote` chip — on the `~agents` fleet screen. The only other mention is a line inside a **rail-square tooltip**.

So: nothing on the surface a person lands on, nothing on the note they are reading, nothing while they work.

That was survivable while a human made every commit. **[[ADR-0022]] changed it on 2026-08-12** — the delegate may now push to non-deploy remotes, and where it does not, the human must be told. Edwin's own words in the acceptance: *"if not pushed automatically then this should clearly be identified in the tool."*

This is [[ADR-0020]]'s rule applied to a case it did not cover: **unpushed work is an obligation, and it had no home.**

## Out of scope

- **Pushing automatically.** [[ADR-0022]] permits a delegate to; whether this project's worker does is [[PHASE-031]]'s, and publishing on someone's behalf without being asked is exactly what the supervised week exists to watch.
- **A second deploy-refusal.** The rule that a deploy remote is never offered lives in one function and stays there — a second copy is how one of them comes to disagree.
- **The fleet view.** It keeps its section; this adds the local one.

## Acceptance

- [x] The overview says when this workspace has commits nobody has pushed, and is **absent** when it has none.
- [x] It offers the push, and pushing from there does what pushing from the fleet screen does — **the same row builder**, so the deploy-remote refusal cannot drift between two surfaces.
- [x] A deploy remote refuses here too, with its reason, rather than being hidden.
- [x] A workspace with **no remote at all** says so — nothing is backed up is a different fact from nothing is unpushed.


## Evidence — 2026-08-12

Measured before building: unpushed state appeared in exactly two places — a **rail-square tooltip** and the `~agents` screen. Nothing on the overview, the note pane or the footer.

The band renders the fleet screen's own `buildBehindRow`, so `'deploy remote'` appears **once** in the renderer and the refusal cannot drift between two surfaces — asserted, because this is the one click in the app that publishes a live website.
