---
type: "[[task]]"
id: TASK-0419
aliases: ["TASK-0419"]
title: "Every card is a full card — the cold pass carries the digest, so a project you have not opened says as much as one you have"
status: backlog
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["Edwin 2026-08-13: 'Why do you think it is necessary to show these initial cards for the projects instead of simply only showing the cards for the projects which have been selected, or otherwise show the full card all the time there is no need to have this intermediate state.' → 'Full card always.'"]
parent: "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
effort: M
depends: []
blocks: []
related: ["[[FEAT-0071]]", "[[FEAT-0028]]", "[[DES-0008-The-Returning-Human]]"]
tests: []
---

# Every card is a full card

## The cause, which is not a design

The attention panel's cards were drawing on two sources with two different reaches, and the difference showed:

- **Publication** — from the **shell**, which probes `git` for every discovered workspace on its own clock. Fleet-wide, always there.
- **The since-line** — from that project's **digest**, served by that project's **sidecar**. A sidecar exists only for a workspace opened this session: measured 2026-08-13 with ten workspaces discovered and `digests known: 1`.

So an unopened project got a card with a headline and no since-line — an intermediate state nobody chose, which is exactly how Edwin read it.

## Why not the cheaper option

The obvious alternative — card only the projects you have opened — was rejected: it resolves the inconsistency by deleting the signal. `your-applications.com` was sitting at **34 commits on a deploy remote**, unopened, and would have shown nothing until someone thought to look. That is [[FEAT-0055]]'s original failure restated (*312 commits across eight repos, nothing mentioning it*), which is the whole reason publication is on this panel.

## Definition of Done

- [ ] The cold pass (`fleet_validate.summarise`) carries each repo's digest numbers — watermark, transitions since it, owed count — beside the validator state and git standing it already reports.
- [ ] The shell feeds `digests` from that for any workspace without a live sidecar, and a live sidecar still wins where there is one: it is the fresher answer, and it is the one that updates between cold passes.
- [ ] **Every card carries the same lines**, whether or not its project has been opened. Asserted on the payload rather than eyeballed.
- [ ] No new subprocess per repo: this rides the batch that already runs, and its added cost is bounded by the same timeout.
- [ ] A repo with no `docs/`, no git, or an unreadable watermark degrades to *no digest* rather than to a wrong one, and does not take the batch down with it.

## Steps

- [ ] `summarise()` builds the index and calls `digest_payload` with the repo's own `Watermark`, guarded per repo.
- [ ] `fleet-health.ts` parses the block and exposes it on the row.
- [ ] The renderer prefers a live digest and falls back to the cold one.
- [ ] Assert the fallback, and assert that a live sidecar still overrides.
