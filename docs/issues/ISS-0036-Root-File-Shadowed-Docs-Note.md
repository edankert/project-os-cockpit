---
type: "[[issue]]"
id: ISS-0036
aliases: ["ISS-0036"]
title: "The root-file render branch shadowed docs/README.md"
status: fixed
severity: high
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review round 2, 2026-07-28 (FEAT-0043)"]
related: ["[[ISS-0033-Identity-Band-Link-Is-Dead]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
fixed_by: []
---

# The fix for ISS-0033 shadowed a real note

## What happened

The root-file branch added to `_serve_render` did two things wrong together: it tested the allowlist **after** the `docs/` prefix had been stripped, and it resolved the root allowlist **before** `docs_root`. So `docs/README.md` — a real note in this repo, `id: DOCS-README` — was answered with the project-root README.

```
path=README.md       -> project-root README
path=docs/README.md  -> project-root README      <- explicit, unambiguous, wrong
```

The second line is the damning one. A caller who spelled out exactly which file they wanted got a different one.

## Why the new test did not catch it

`test_the_brief_link_resolves_over_http` creates `docs/README.md` but no root `README.md`, so the shadowing branch is never taken. The test exercised the path it was written for and no other — the same narrowness that let ISS-0033 through, one layer down.

## Fix

Keep the disambiguator and reverse the order: `docs_root` is resolved **first**, and the root allowlist is consulted only when docs has no such file *and* the caller did not say `docs/`. Reordering alone would have mirrored the bug (the root README becoming unreachable whenever `docs/README.md` exists) — it takes both halves, and the test now asserts both.

The root file is therefore reachable exactly when docs has no file by that name, which is the true state of affairs for `LLM_BRIEF.md` and is what makes the branch safe rather than merely narrow.

Security was never the issue and is unchanged: exact filename membership, `..` rejected before the branch, `CLAUDE.md` and `SECRETS.md` still refused — re-verified over HTTP.
