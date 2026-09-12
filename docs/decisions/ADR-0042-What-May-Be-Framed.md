---
type: "[[adr]]"
id: ADR-0042
aliases: ["ADR-0042"]
title: "Any file under a repo's `docs/` may be framed, in any workspace the shell holds — because serving it was never the boundary, and the sandbox is"
status: "accepted"
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: "2026-09-12"
source: ["Edwin, 2026-09-12: 'I don't think we need that rule, what is the issue if this isn't limited? yes cross repo is allowed. Rewrite ADR-0042'", "src/project_os_cockpit/server.py:3375", "src/project_os_cockpit/server.py:4233"]
decision: "The viewer may frame any file that resolves inside a workspace's docs/ directory, in any workspace the shell has open. No allowlist, no reachability test, no same-repo restriction. The boundary that remains is the sandbox with no allow-same-origin, plus path containment in docs_root."
context: "The design bench frames only files a design note claims in asset:, and the rule's stated purpose was to stop the render surface becoming a file browser. Measured: /docs/<rel> already serves every file under docs/ to anyone who can reach the sidecar, so the render surface was already a file browser and the allowlist was protecting nothing."
alternatives:
  - "Reference reachability — a note must point at the file (the first version of this ADR, dropped by Edwin)"
  - "Keep a renamed allowlist field"
  - "Serve anything under docs/ (decided)"
consequences:
  - "An HTML page may reference anything beside it, at any depth, which fixes ISS-0299 with no bookkeeping"
  - "Cross-repo framing works because the shell holds one sidecar URL per workspace; each sidecar still bounds its own docs/"
  - "The sandbox is now the only thing between a framed document and the cockpit, so any change to the frame's sandbox attribute is a security change and must be reviewed as one"
supersedes: ""
superseded: ""
related:
  - "[[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]"
  - "[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"
  - "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]"
  - "[[FEAT-0148-One-HTML-Viewer]]"
tags: [adr, security, render]
decided_option: "3"
---

# What may be framed

## Context

The cockpit frames authored HTML in a sandboxed iframe. Today one route does it and it accepts one thing: a file named by some design note's `asset:` (`src/project_os_cockpit/server.py:3375`). The docstring gives the reason — *"Serving any file under docs/ by path would turn a render surface into a file browser."*

That sentence has been false for months, and checking it is what settled this decision.

`/docs/<rel>` (`server.py:4233`) serves **any file under `docs/`** by path. It has no allowlist, no authentication and no gate beyond rejecting `..` and checking containment in `docs_root`. And the render server binds `0.0.0.0` by design so a tablet on the same Wi-Fi can read the notes (`src/project_os_cockpit/cockpit.py:2108`). So every file under `docs/` is already readable by anything on the network that can reach the sidecar. The design allowlist was not protecting those files from being read. It was deciding which of them the cockpit would *present* — a curation rule wearing a security rule's clothes.

Two things now push on it anyway. An HTML page cannot show an image sitting beside it, because the image is claimed by nothing ([[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]]) — which is why a 4.6 MB page exists with 51 pictures pasted in as base64. And the bench is being replaced by a viewer any note may use, so "claimed by a *design* note" stops being expressible.

## Options

1. **Reference reachability** — a file may be framed when some note points at it, plus one level deep from an already-reachable page. Preserves the curation property. Costs a derived set that has to be rebuilt on every index reload, a 404 whose real meaning is "nobody linked this", and a stated depth limit that will surprise the first person who writes a page that loads a stylesheet that loads a font.
2. **A renamed allowlist field** — `asset:` on any note type. Cheapest to build, and it is the friction that produced the base64 in the first place: 27 images in a folder means 27 frontmatter lines.
3. **Any file under `docs/`, any workspace.** No list, no derivation, no depth limit.

## Decision

**Option 3.** The viewer frames any file that resolves inside a workspace's `docs/` directory, in any workspace the shell has open.

Edwin, 2026-09-12: *"I don't think we need that rule, what is the issue if this isn't limited? yes cross repo is allowed."*

The answer to his question is that there is no issue, and the measurement above is why: framing widens no read access, because `/docs/<rel>` already grants all of it to anyone who can reach the sidecar. What the allowlist bought was tidiness, and it was charged for in base64.

**Cross-repo works through the shell, not through a route.** Each sidecar serves exactly one workspace and still refuses anything outside its own `docs_root`. The shell holds one sidecar URL per open workspace, so framing a page from another repo means addressing that repo's sidecar. No sidecar gains reach into a directory it did not already own.

**What remains the boundary, and is load-bearing:**

- The frame is sandboxed **without** `allow-same-origin`, so a framed document gets an opaque origin. It cannot read the sidecar API, the cockpit's DOM, `localStorage`, or the parent window. This is the whole containment story now, and it is the same one it always was.
- `..` traversal is rejected and the resolved path must lie inside `docs_root`.
- The response is GET-only, carries no cookies, and sets `X-Content-Type-Options: nosniff`.
- `allow-scripts` stays as it is today — on for a standalone page, which needs it (the style guide carries a theme toggle); off by default for HTML inside a note unless the note opts in.

Because the allowlist is gone, **the sandbox attribute is now the only thing between a framed document and the cockpit.** Any change to it is a security change and is reviewed as one. That is the sentence to keep.

## Alternatives

- **Option 1, dropped by Edwin.** It was this ADR's first proposal, written before `/docs/<rel>` was checked. Its argument rested on the belief that the allowlist limited what could be read; once that turned out to be false, the option was paying a derived-set rebuild, a depth limit and a confusing 404 for a curation property nobody had asked for. The first version's full reasoning is in git history; the amendment note below records what changed and why.
- **Option 2, rejected.** Preserves the property at a measured cost: zero design artifacts in the fleet reference a relative image file, and 51 images in one document were base64-encoded instead. When declaring a file is expensive, people stop using files.

## Consequences

- [[ISS-0299-An-HTML-Page-Cannot-Show-An-Image-Beside-It]] is fixed with no bookkeeping: a page references anything beside it, at any depth, exactly as it would on disk.
- `/design-asset` and `/design-asset-at` can be deleted rather than generalised. What replaces them is a route that resolves a path inside `docs_root` and serves it with the artifact headers — which is nearly `/docs/<rel>` with a different header set, and whether it should just *be* `/docs/<rel>` is [[TASK-0613-A-Generic-HTML-Viewer]]'s to decide.
- **A file under `docs/` that nobody meant to publish is now presentable.** That is the residual position, and it is the same position `/docs/<rel>` has held all along. [[RISK-0008-The-Sandbox-Is-The-Only-Boundary]] states what is actually left.
- Nothing here loosens `/docs/<rel>`, and nothing here changes who can reach the sidecar. The `0.0.0.0` bind and what it implies is [[RISK-0001-Terminal-Exposure]]'s and [[RISK-0007-Remote-Workspace-Trust-Boundary]]' territory, untouched.

## Amendment history

**First version, 2026-09-12 (morning), `proposed`:** decided Option 1, reference reachability, on the belief that the design allowlist was the thing keeping the cockpit from serving arbitrary files.

**Rewritten the same day** after Edwin asked *"what is the issue if this isn't limited?"* and the question was checked rather than answered from memory. `/docs/<rel>` already serves every file under `docs/` with no gate, on a socket bound to `0.0.0.0`. The premise of the first version was wrong, so the option it chose was solving a problem that did not exist. The open question the first version raised — whether the set should span repos — is answered by Edwin in the same message: yes.
