---
type: "[[change]]"
id: CHG-20260814-One-Walk-For-Publication
title: "Publication is walked once, the unknown count reaches every surface, and Tier 3 retires"
status: merged
owner: user:edwin
created: 2026-08-14
updated: 2026-08-14
source: ["Edwin 2026-08-14: 'Review the 3 open issues and suggest how to resolve them' → then 'Fix the others as suggested'"]
commit: ""
pr: ""
impacts: ["the fleet's unpushed counts now come from a Python subprocess the shell spawns, not from git.ts", "a repo with a remote and no upstream is reported as unknown on the attention card and the fleet roll-up instead of vanishing", "desktop tests need an interpreter that can import the package (COCKPIT_DESKTOP_PYTHON)", "the acceptance suite's Tier 3 block is empty; the suite is 34 items, all gating"]
issues: ["[[ISS-0165-The-Attention-Card-Reads-A-Second-Git-Walk]]", "[[ISS-0143-The-Tier-3-Block-Is-Owed-A-Retirement]]"]
features: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[FEAT-0086-Tests-Becomes-A-View]]"]
related: ["[[CHG-20260814-The-Review-Findings]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]", "[[TASK-0421-An-Unknown-Count-Is-Unknown-On-Every-Surface]]", "[[TASK-0422-One-Walk-For-Publication]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# One walk for publication

## Summary

Two of the three open issues, closed. [[ISS-0165]] said the attention card reads a second git walk; it was reading the second of **three**, and the divergence it called latent was already live. [[ISS-0143]] said Tier 3's retirement was owed and tracked nowhere; the trigger had fired three days earlier.

## ISS-0165 — what was actually there

The issue named two implementations of *"how many commits are unpublished"*. There were three:

| where | read by |
|---|---|
| `git_state.read()` | the badge (`obligations._publication_rows`) and History |
| `probeGitState` (`desktop/src/ipc/git.ts`) | the rail's attention card and the fleet roll-up |
| `fleet_validate.git_standing` | **nobody** — the shell computes it and discards it ([[ISS-0156]]) |

**Measured on the real fleet, 2026-08-14**, running the new pass over all 18 repos under `~/Dev/repos/`: **`edankert.com` has a deploy remote and no upstream**, so `ahead` is `null`. Before this change the badge counted one publication obligation for it while the attention card dropped its row and the roll-up placed it in neither *behind* (needs a number) nor *no remote* (needs no remote) — it was absent from both surfaces. Two repos with no remote at all (`articles`, `project-os-bench`) are `null` for the different, correctly-stated reason.

**And they had already diverged.** The 2026-08-14 repair for [[ADR-0027]]'s fourth admission test — an unknown count may not render as nothing owed — landed in Python only. On the two TypeScript surfaces a null `ahead` was coerced to `0` and then dropped for being `<= 0`, so a repo with a real remote and no upstream counted **one** obligation on the badge and appeared **nowhere** on the card or the roll-up. The issue's *"nothing is visibly wrong today"* was the one claim in it that did not survive reading the code.

## What changed

**The unknown survives to the sentence.** `AttentionEntry.publish.ahead` is `number | null`; `publicationText` gained the unknown branch and says what History already said — *"No upstream set — nothing can say what is unpublished"*. The fleet roll-up gained a third line beside *behind* and *no remote*, because a repo with a remote and no count fell between those two filters and rendered as nothing at all. The dismissal fingerprint distinguishes an unknown from a card with no publication line, so the ✕ still means *until something changes*.

**The walk is Python's, for every workspace.** New module `project_os_cockpit.fleet_git` prints one JSON line per repo from `git_state.read_fresh()`; `fleet-health.ts` spawns it for the whole fleet on the 60-second clock it already had. `probeGitState` is gone. `git.ts` keeps `remoteKind` alone — that classification decides whether `git push` may run, and this is the process that runs it.

**`dirty` came along**, because it was the same defect one number to the left: `_uncommitted_notes` (History's band) and `probeGitState` each walked `git status --porcelain -- docs/ SNAPSHOT.yaml` with their own copy of the rename handling. `git_state.dirty_paths()` is that walk now, History decorates its rows from it, and `GitState.dirty` is what the shell reads.

**`fleet_validate` stopped being the third copy.** `git_standing` delegates and `remote_kind` is an alias. Its wire format is unchanged for anyone running it standalone.

### The resolution the issue proposed, and why it is not the one taken

It asked for `fleetHealth` to read the sidecar's publication payload. **A sidecar exists only for a workspace someone has opened**, so that answers for one repo and leaves eleven blank — [[ISS-0156]] with the sign flipped, on the surface whose whole point is being cross-workspace. The property to keep was *one clock for the whole fleet*; the property to gain was *one implementation*. A batch on the existing clock gives both.

## ISS-0143 — Tier 3 retires

The tier contract says a verification check is promoted or removed after a verified release. [[REL-0001]] shipped on 2026-08-11 and both items stayed, deliberately: removing them the same evening would have edited the record a shipped release cites. Three days on, that cost is gone. **3.1** is removed rather than promoted because `tests/test_tests_view.py` already asserts what it looked at; **3.2** is removed because promoting it would install a permanent check whose precondition no session can produce. Both items' evidence is preserved verbatim under the Tier 3 heading, and [[REL-0001]] gained one line saying so — its figures are unchanged, because they record what the gate read that day.

**The tracker the issue asked for is still not built, and the check it proposed would not have worked.** *"A `released` release newer than the suite's `updated:`"* — REL-0001's date and the suite's `updated:` were both 2026-08-11, so it would not have fired here, and `updated:` moves on any edit, so it would go quiet permanently after the first unrelated change. A working check needs its own field (when Tier 3 was last reconciled) against the newest `released` release, and its home is `acceptance.py`. Recorded in the suite with the flaw named, rather than built wrong.

## Guards

- `desktop/tests/git-state.test.mjs` — a real repo with a remote and no upstream reports `ahead: null`; the shell's row is compared against what `python -m project_os_cockpit.fleet_git` says for the same repo, rather than against a number that happens to match; and `git.ts` is asserted to contain no `rev-list` and no `--porcelain`. That last one is the guard [[ISS-0165]] asked for: the existing `counts_by_kind` assertion covers the two Python surfaces and is structurally blind to the third.
- `tests/test_fleet_git.py` — the wire format, the unknown, the record scope, read-only argv, and that no module walks git for publication state on its own. Plus a renderer source guard that the zero-coercion is gone.

**Both structural guards were written wrong first, in the same way, an hour apart:** each searched source text that included its own explanatory comment naming the very command it forbids. The TypeScript guard *failed* on the fix it was written for; the Python guard did too. Both now strip comments — the JS one line-wise, the Python one through `ast` — because a guard a comment can satisfy or break is measuring prose. Each was then mutation-tested by reintroducing the defect in code.

## Migration

**The desktop shell now needs a Python interpreter that can import this package in order to report publication state at all.** It already needed one for the cold validator pass, and resolution is unchanged (`COCKPIT_DESKTOP_PYTHON`, then the bundled runtime, then system `python3`) — but the exposure is wider: if none can import the package, the fleet's unpushed counts stay empty instead of only the cold validator's rows. Nothing renders as *pushed*; a missing answer keeps the last one and absence reads as no claim. `tests/test_desktop_node_suite.py` hands the node suite its own interpreter.
