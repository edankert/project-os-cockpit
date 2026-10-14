---
type: "[[issue]]"
id: ISS-0318
aliases: ["ISS-0318"]
title: "A Claude Code older than 2.1.287 ignores the cockpit plugin, and the session goes unreported without any warning"
status: open
phase: []
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]], open question 2"]
reported_by: agent
question: ""
severity: low
component: desktop
parent: ""
related: ["[[RISK-0004-Hook-Injection-Surface]]", "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"]
tests: []
---

# An older Claude Code leaves a cockpit session unreported without a word

## Problem

Since [[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]], a Claude session in a cockpit terminal reports to the cockpit only through a plugin. Claude Code loads plugins of this kind from version 2.1.287. An older Claude Code ignores `CLAUDE_CODE_PLUGIN_DIRS`, so the session runs normally but the rail dot, the agent row and the cost figures never appear. Nothing tells the person why.

The feature chose no fallback to the old shell scripts, because keeping both paths alive is what the phase removes. It recommended a visible warning instead. That warning is not built.

## Why it is not built now

On 2026-10-14 the installed Claude Code is 2.1.299, and CI tests the plugin on that version. Nothing on this machine reaches this case today.

## What a fix needs

- A way to learn the installed version without slowing every shell start: for example, the main process runs `claude --version` once per application start, with the login shell's PATH.
- A place to say it: a line in the cockpit terminal at start, as `deathHint` does in `ipc/terminal.ts`, or a mark on the rail.
