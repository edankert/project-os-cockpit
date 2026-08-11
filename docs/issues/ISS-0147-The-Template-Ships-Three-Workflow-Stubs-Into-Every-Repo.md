---
type: "[[issue]]"
id: ISS-0147
aliases: ["ISS-0147"]
title: "The template ships three workflow notes into docs/ that only restate what lives in tools/ — 24 stubs across 8 repos, draft and untouched since 2026-01-29"
status: open
severity: low
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
phase: "[[PHASE-999-Future]]"
features: []
tasks: []
related: ["[[ISS-0123]]", "[[FEAT-0091-The-Standing-Documents]]"]
tags: [issue, template, upstream]
---

# The template ships three workflow stubs into every repo

## What was asked

Edwin, 2026-08-11: *"Review the workflows in docs area in all projects, I think they are there by accident and they should only exist in the tools area."*

## What the fleet says

Measured across the twelve repos the cockpit renders. **The category splits in two, and only one half is boilerplate.**

**Template-shipped, never adapted — 24 notes across 8 repos:**

`WF-0001-Existing-Project-Init`, `WF-0002-Template-Sync`, `WF-0003-Recovery-Resume`. Every one `status: draft`, every one `updated: 2026-01-29`, byte-identical to the template's in `project-os`, `project-os-bench` and here. **Six and a half months, eight repos, not one edit.**

They describe project-os's *own* machinery — initialise a project, sync the template, recover a session — and each names its real home in its own frontmatter: `tools/skills/project-derive/SKILL.md`, `tools/scripts/sync-project-os.sh`, `tools/instructions/HANDOFF.md`. **Edwin is right about these.** They are an index of the tools area, filed in the record, in a directory the validator walks and the cockpit renders as though the project had authored them.

**Project-authored, and genuinely documentation — 8 notes across 3 repos:**

| repo | notes | status |
|---|---|---|
| `obsidian-supernote-sync` | Daily Notes, Research Notes, World Building, Development, API Server | `active`, 2026-01-31 |
| `your-applications.com` | Update Marketing Assets, App Release Checklist | `active`, 2026-02-15 |
| `your-trainer` | Build And Run | `active`, 2026-01-27 |

**These are not tools-area material and have nowhere else to live.** *"How you build and run this app"* is a fact about the project; `tools/` is template-owned and `sync-project-os.sh` overwrites it, so a project workflow filed there would be destroyed by the next sync.

## So the hypothesis is half right, and the half matters

*"They should only exist in the tools area"* is correct for the three the template ships and wrong for the eight somebody wrote — acting on it wholesale would delete real documentation in three repos, two of which are live sites.

## Resolution

1. **Upstream: stop shipping the three.** They belong in `tools/` alongside the skills they point at, or nowhere. This is a template change and must be proposed in `~/Dev/repos/project-os/`, not fixed downstream.
2. **Here: remove this repo's three copies.** Byte-identical, `draft`, never referenced by any note in this corpus. `docs/workflows/README.md` stays, so the category still has a home for anything this project actually authors.
3. **The other seven repos keep theirs until the template stops shipping them** — a downstream repo is not the place to fix a template defect one copy at a time, which is the rule `CLAUDE.md` already states for `tools/`.

Filed rather than swept: eight repos is a fleet change, and the fleet is not this session's to edit.
