---
type: "[[phase]]"
id: PHASE-032
aliases: ["PHASE-032"]
title: "The reasoning is recorded — a judgment on the record can carry why, not only what"
status: done
order: 32
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
features: ["[[FEAT-0095]]", "[[FEAT-0096]]"]
issues: ["[[ISS-0152]]"]
related: ["[[ADR-0010]]", "[[DES-0005-The-Actuator-Grammar]]", "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
tags: [phase]
---

# The reasoning is recorded

## Goal

**A judgment a person makes on the record carries the reasoning behind it — in the note where the decision lives, in a form both the cockpit and Obsidian render.**

Today the tool can record *that* a human decided and never *why*. Measured across six write paths ([[ISS-0152]]): exactly one carries the person's own words, and it can only attach them to a checkbox line.

## Why a phase and not a task

Both tests in `CLAUDE.md` hold. The goal above is one sentence with no list in it. And the exit criteria below are properties of the record rather than a restatement of the work — the last of them cannot be satisfied in this repo at all.

It spans three repos, which is the honest reason: the cockpit's write path and renderer, the record's conventions in the template, and the decision itself in `project-os-dev`. A feature cannot straddle that; a task certainly cannot.

## Scope

- **[[FEAT-0095]]** — a human verb carries a note, appended to the decided note as a dated, attributed Obsidian callout that the cockpit renders.
- **[[FEAT-0096]]** — a decision's open questions become acceptance criteria, so they are answered one at a time with evidence rather than stamped in one click.

Out: the `Comment` verb that changes no status ([[ISS-0152]] option 2, rejected — it creates a state nothing reads). `Request changes` on the ADR vocabulary is deferred, not refused: it is the same shape as FEAT-0095 and can join it if the first pass proves the pattern.

## Exit criteria

- [x] No human-owned verb in the cockpit can record a verdict without the option of carrying prose — asserted over `HUMAN_TRANSITIONS`, not over the two verbs that prompted this.
- [x] The prose lands in the note being decided, dated and attributed, and renders as a callout in the cockpit **and** in Obsidian — one syntax, two readers, neither one's invention.
- [x] [[ADR-0010]] is decidable question by question: its open threads are criteria, and each can be answered with evidence today.
- [x] Both conventions are **captured upstream** — the callout form and the criteria-on-a-decision form — in `project-os`'s instructions, with the decision recorded in `project-os-dev`. *This one cannot be met inside this repo, which is the point of stating it here.*
- [x] [[ISS-0152]] closes, and closes because the gap it measured is gone rather than because the two verbs that exposed it were special-cased.


## Closed — 2026-08-12

All five criteria met, including the one that could not be met in this repo: [[ADR-0020]] in `project-os-dev` (`d8b4742`) records the decision, and `DECISIONS.md` + `OBSIDIAN.md` in the template (`e4f3a44`) carry both conventions.

**Two of the four tasks needed no code.** The criteria machinery was already ungated by note type, and the owed mark was already on the row. The phase's real content turned out to be one write path, one renderer, and two conventions written down where the next project will find them.
