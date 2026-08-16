---
type: "[[issue]]"
id: ISS-0183
aliases: ["ISS-0183"]
title: "SNAPSHOT.yaml is declared the canonical machine-readable context and did not parse as YAML — four invalid escapes, and nothing in the toolchain would ever have noticed"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: ["Found 2026-08-16 while registering FEAT-0108..0111, by parsing SNAPSHOT.yaml to check the edit rather than trusting it"]
severity: medium
component: tooling
parent: ""
related: ["[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
tests: []
---

# The canonical machine-readable file did not parse

## Problem

`LIFECYCLE.md` opens with:

> `SNAPSHOT.yaml` is the **canonical, machine-readable active context** for agents/LLMs.

It was not machine-readable. `yaml.safe_load` on it raised:

```
yaml.scanner.ScannerError: while scanning a double-quoted scalar
  in "SNAPSHOT.yaml", line 74, column 9
found unknown escape character "'"
```

Four occurrences of `\'` inside a double-quoted scalar — `a ticked box\'s evidence`, `that issue\'s real line`, `this close-out\'s own arithmetic`, `under ISS-0121\'s discriminator`. YAML's double-quoted style permits a fixed escape set and `\'` is not in it; the apostrophe needs no escape there at all. They were introduced by hand-writing shell-escaped prose into a `note:` field.

Confirmed present at `HEAD` before this session's edits, so it had been committed and had survived pre-commit and CI.

## Why nothing caught it

**Nothing in the toolchain parses this file as YAML.**

- `tools/scripts/sync-snapshot.py` edits it **line-by-line** — which is deliberate and correct, because it must preserve comments and ordering that a round-trip through a YAML emitter would destroy.
- `cockpit.py:180` and `cockpit.py:199` read `project.id` and `verification.staleness_days` with `re.search` over the raw text.
- `validate-docs.sh` reported **OK** on it.

So the file's one declared property — being readable by a machine — was the only property no machine checked. The app never broke because the app never parses it either.

## Impact

Latent rather than live, and worth stating precisely so it is not over- or under-sold. Nothing in this repo failed. **Any agent that follows `LIFECYCLE.md`'s instruction and loads the snapshot with a YAML parser gets a `ScannerError` and no context at all** — which is the exact audience the sentence names.

## Fixed 2026-08-16

Four `\'` replaced with `'`. The file now parses, and `focus`, `items.features` and `items.phases` were read back through `yaml.safe_load` to confirm the round trip.

## What is not fixed

**There is still no check that the snapshot parses.** This one was found by parsing the file to verify an unrelated edit — luck, not process. A one-line `yaml.safe_load` in `validate-docs.sh` would make it structural, and the reason to hesitate is real: the validator would then hard-fail on a file the rest of the toolchain is content to read line-by-line, and that is a change to what the gate means rather than an obvious win. Left as a question rather than answered quietly.

The same class of defect can recur through any hand-authored `note:`, which is where all four of these came from and which is the field this project writes most heavily.
