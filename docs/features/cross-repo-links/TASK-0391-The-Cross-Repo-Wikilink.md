---
type: "[[task]]"
id: TASK-0391
aliases: ["TASK-0391"]
title: "The cross-repo wikilink — parsing and rendering"
status: done
parent: "[[FEAT-0093]]"
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
---

# The cross-repo wikilink — parsing and rendering

WIKILINK_RE gains the project#ID form for both consumers (body and frontmatter strip). The sidecar emits the parts as data attributes rather than a URL it cannot resolve.
