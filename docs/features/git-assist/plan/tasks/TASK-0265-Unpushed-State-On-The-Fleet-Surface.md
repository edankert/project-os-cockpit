---
type: "[[task]]"
id: TASK-0265
aliases: ["TASK-0265"]
title: "Unpushed commits and the remote's kind, on the surface that already reports repo health"
status: done
phase: "[[PHASE-021-Git-Is-Not-The-Users-Job]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0055-Git-Assist]]"]
parent: "[[FEAT-0055-Git-Assist]]"
effort: M
depends: []
blocks: ["[[TASK-0266-A-Deliberate-Push-Action]]"]
related: ["[[FEAT-0028-Fleet-Health-Surface]]"]
tests: []
---

# Unpushed state on the fleet surface

## Definition of Done
- [x] The fleet health row carries `ahead` (commits not on the remote) and `remote_kind` (`backup` / `deploy` / `none`)
- [x] `remote_kind` is derived from the remote **URL**, never from configuration
- [x] The rail tooltip says how far behind a repo is
- [x] The roll-up lists repos that are behind, separately from repos that are failing — they are different problems
- [x] A repo with no remote says so rather than reading as up to date
- [x] Costs nothing when up to date

## Steps
- [x] Extend the cold pass: `git rev-list --count @{u}..HEAD` and `git remote get-url`
- [x] Classify: an `https?://`/`git@` host with a known forge → `backup`; anything resolving to a server path or a remote named `production`/`deploy` → `deploy`; none → `none`
- [x] Render in the tooltip and the roll-up
- [x] Test: classification over real remote shapes, and that "no remote" ≠ "up to date"

## Notes

**Not a new surface.** [[FEAT-0028]]'s badge and roll-up already answer "what is the state of this repo"; unpushed commits are the same question and belong beside validator errors, not in a second panel.

**"No remote" must not read as fine.** Three fleet repos have none. Rendering that as up-to-date is the [[ISS-0065]] failure — absence presented as health.

## Done 2026-07-30

`fleet_validate.git_standing()` and `remote_kind()`, carried through the cold pass into the rail tooltip and a **separate** roll-up group — being behind is a different problem from failing, and a repo can be perfectly clean and six days unpushed.

Live, after pushing everything else earlier today:

```
Not pushed — 31 commits across 1 repo
  31   your-applications.com          [deploy remote]
1 with no remote: articles
```

**No remote is listed apart, not as up to date** — the ISS-0065 failure would be rendering absence as health.

**Classification is derived, never configured**, and an unrecognised remote is `deploy`: the safe default for "I do not know what this is" is "do not publish to it".

### The bug only one test could see

Appending `git_standing` to the end of the module put it **after** `if __name__ == "__main__": raise SystemExit(main())`. Importing the module binds every definition, so twelve tests passed; `python -m` stops at that line, so every repo reported `unavailable: NameError`. Exactly one test — the subprocess entrypoint — caught it. Now guarded: nothing may follow the entrypoint block.
