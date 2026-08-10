---
type: "[[feature]]"
id: FEAT-0091
aliases: ["FEAT-0091"]
title: "The standing documents get a manifest, a freshness signal and a home — the eight one-per-project notes stop being invisible and stop pretending to have a lifecycle"
status: planned
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ISS-0125-The-Singleton-Documents-Have-No-Lifecycle-And-No-Home]]", "[[REQ-0033-Every-Project-Can-Say-What-It-Is]]"]
goal: "Declare the one-per-project standing documents as extensible data, drop the lifecycle status they never had, report presence/singularity/placeholders/freshness, and land them on the Intent view so the documents describing the project are the first thing its view shows."
requirements: ["[[REQ-0033-Every-Project-Can-Say-What-It-Is]]"]
tasks:
  - "[[TASK-0380-The-Manifest-As-Data]]"
  - "[[TASK-0381-Statuses-Out-Checks-In]]"
  - "[[TASK-0382-Standing-Documents-Land-On-Intent]]"
  - "[[TASK-0383-The-Housekeeping]]"
  - "[[TASK-0384-Propose-The-Manifest-Upstream]]"
release: ""
related: ["[[ISS-0124-Four-Note-Types-Have-No-Status-Table]]", "[[ISS-0122-Active-Modes-Doing-Column-Counts-Notes-Nobody-Is-Working]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]"]
tests: []
---

# The standing documents

## Goal

Eight documents answer *what is this project*: `README`, `INDEX`, `ARCHITECTURE`, `GLOSSARY`, `OWNERSHIP`, `DESIGN`, `STYLEGUIDE`, `PHASES`. Measured across the fleet on 2026-08-10: **90 present of 96 possible, and 85 of those 90 stale or undated — 94%.** `DESIGN.md` and `STYLEGUIDE.md` here have not been touched since the day they were created, six and a half months ago.

They are carried under three different type values, two of them ad-hoc. They hold a `status:` in the **work-in-flight band**, so 18 references and the glossary are counted as work somebody is doing ([[ISS-0122]]). And [[REQ-0025]] already records that they *reach no surface at all*.

Nothing names the set, nothing checks it, nothing shows it. This does all three.

## Why it belongs in PHASE-030

The phase's goal is that every judgment the record owes surfaces where its subject lives. **"Confirm this is still true" is such a judgment**, and a six-month-old style guide is it going unasked. So staleness joins [[FEAT-0089]]'s obligation registry as a kind, owned by the Intent view and badged like every other — which is what makes this part of the phase rather than bolted onto it.

## Scope

**In:**

- The manifest: base set template-owned, project extensions in `SNAPSHOT.yaml`'s `docs_system` block
- Singularity enforced — one entry resolves to exactly one file
- `status:` removed from these documents; `updated:` becomes the field that carries meaning
- Checks: missing required entry, still-a-template-stub, stale — each reported distinctly, staleness as a warning
- The Intent view's landing renders the set with each document's age
- The upstream proposal, since 82 of the 90 documents are in other repos

**Out:**

- **A new note type.** [[REQ-0033]] records why: a type is for an open population, and there will never be a second glossary.
- **Rewriting the documents.** This makes their staleness visible; it does not make them true. Twelve are still recognisable template stubs and that is a finding to surface, not a backlog to clear here.
- **Blocking anything.** No build fails because a glossary is old.
- **`docs/references/COCKPIT-API.md`** and the nine container `README.md` signposts. They are `reference`-typed and stay that way; only the singleton set is in scope.

## Acceptance

- [ ] The set is declared once as data; no script or renderer carries its own list of names
- [ ] A project adds an entry without editing a template-owned file, and `sync-project-os.sh` does not destroy it
- [ ] An entry resolving to two files is an error
- [ ] None of the eight carries a lifecycle status, and none appears in an in-flight count
- [ ] Missing / stub / stale are reported distinctly; stale warns and never errors
- [ ] The Intent view opens on the set, each entry showing when it was last confirmed
- [ ] `REQ-0025`'s guard still passes — no note type loses its only surface
- [ ] The fleet number is re-measured after landing, so the 94% has an after

## Links

- Requirement: [[REQ-0033-Every-Project-Can-Say-What-It-Is]]
- Origin: [[ISS-0125-The-Singleton-Documents-Have-No-Lifecycle-And-No-Home]]
- Home: [[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]] builds the Intent view this lands on
