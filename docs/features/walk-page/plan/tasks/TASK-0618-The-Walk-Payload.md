---
type: "[[task]]"
id: TASK-0618
aliases: ["TASK-0618"]
title: "The walk payload: the owed checks grouped into the consumer's sittings, from the template's bundled module"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
source: ["[[FEAT-0149-The-Walk-Page]]"]
parent: "[[FEAT-0149-The-Walk-Page]]"
effort: L
due: ""
depends: []
blocks: ["[[TASK-0619-The-Walk-Page]]", "[[TASK-0620-The-Survey]]"]
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]]"]
tests: ["[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]"]
tags: [task, acceptance, publication]
---

# The walk payload

## Why

Everything the walk page shows is a question the data already answers, and nothing asks it. `ledger.owed(docs_root, platform, checks)` returns the run list. `acceptance.load` knows each check's `area:` and section. The consumer's `docs/tests/acceptance/WALK.md` names the sittings and their order. This task joins the three into one payload, and it does so by bundling the template's implementation rather than writing a second one, because the rules are stated once upstream (project-os-dev TESTING.md, "The walk") and two implementations of one predicate is how a badge and a gate come to disagree about the same corpus.

## Definition of Done

- [x] `acceptance.walk_payload(docs_root, index, *, platform: str, release: str = "") -> dict` exists and returns `{"platform", "release", "survey": [...], "sittings": [...], "unplaced": [...], "counts": {"owed", "placed", "unplaced"}, "order_source": "walk.md" | "fallback"}`.
- [x] The union of every row in `sittings[*].rows` and `unplaced` is exactly `ledger.owed(docs_root, platform, [manual check ids])`, where manual means `section_of(item) in MANUAL_SECTIONS`. A test computes both over a constructed fixture and over `your-trainer`'s live docs when present, and asserts set equality and no duplicates.
- [x] A sitting is `{"name", "state", "bench": [...], "surfaces": [...], "checks": [...], "rows": [...]}` and sittings appear in WALK.md's file order. A sitting with no owed rows is omitted from `sittings` and counted nowhere.
- [x] A check joins the first sitting whose `surfaces` names its `area:` or whose `checks` names its id; a check matched by no sitting goes to `unplaced`. Tested with a check named by two sittings and one named by none.
- [x] Inside a sitting, rows are ordered by `after:` first, then id. A cycle in `after:` raises a payload error naming the checks in the cycle; the payload still returns with that sitting in id order and an `errors` list. Tested with a two-check cycle.
- [x] A row is the `~checks` row shape (`_row(item)`) plus `setup`, `steps`, `expect` (the text under those headings in the note, or `None`) and `after: [...]`.
- [x] With no WALK.md, `order_source` is `"fallback"` and `sittings` holds one sitting per `area:` in id order, named after the area, with `state` and `bench` empty.
- [x] The payload contains no key named `minutes`, `duration` or `estimate` at any depth. A test walks the payload and asserts it.
- [x] `GET /api/cockpit/walk?platform=<p>&release=<id>` serves the payload beside the existing `/api/cockpit/acceptance` route, with the same platform defaulting rule that route uses (absent means the open release's platform; `all` is refused with a 400, because a walk is on one platform).
- [x] The ordering and survey logic lives in a bundled copy of the template module, `src/project_os_cockpit/walk_sheet_bundled.py`, verified identical to upstream by the same mechanism that verifies `validate_docs_bundled.py`. Until upstream ships, the file carries a header saying it is the prototype and the sync step is listed here as unticked.

## Steps

- [x] Read `view_payload` (`src/project_os_cockpit/acceptance.py`, from the `def view_payload` line) and `_row`, and reuse `_row` for the row shape. Do not fork it.
- [x] Read `ledger.owed` and `ledger.events_by_check` (`src/project_os_cockpit/ledger.py`, near the end of the file). The row set is `owed`; the survey in [[TASK-0620-The-Survey]] is `events_by_check`.
- [x] Add a WALK.md reader to the bundled module: frontmatter `gallery:` (optional) and a body of sittings. Follow the template's WALK.md shape exactly as project-os-dev FEAT-0029 defines it; if the template has not landed, write the reader to the shape in that feature's plan and mark the sync step unticked.
- [x] Add the `after:` reader: a list of `TST-*` ids on the check note's frontmatter, absent meaning empty. Do not read ordering from prose.
- [x] Add `walk_payload` in `acceptance.py` as a thin call into the bundled module, passing `Suite` items and the owed set.
- [x] Add the route in `src/project_os_cockpit/server.py` beside `/api/cockpit/acceptance` (the `if path == "/api/cockpit/acceptance":` branch), reusing its platform resolution.
- [x] Tests in `tests/test_walk_payload.py`, constructed fixtures in the style of `tests/test_gate_subtraction.py`, plus one live-corpus test guarded by the presence of `../your-trainer/docs`.
- [x] Add `walk_sheet_bundled.py` to the sync manifest and to the verification test that covers `validate_docs_bundled.py`.

## Notes

**What this must not do.** Infer a sitting from the procedure text, from bracket tags, or from the check's title. [[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]] tried that and a scanner got six false positives out of six. The only inputs are `area:`, `after:`, WALK.md, and the ledger.

**Why `all` is refused.** `/api/cockpit/acceptance` accepts `all` as the union across platforms because a gate on two ledgers must fail closed. A walk is a person on one bench with one build; a union walk would ask them to tick a check for a platform they are not holding.

**Why the sitting carries `state` and `bench` as text.** They are the two things the hand-written run plan's pre-flight section carried and no note could: the product state the sitting starts from and what must be on the bench. They are rendered, never parsed.

## Done 2026-09-13

`acceptance.walk_payload(docs_root, index, *, platform, release="")` returns the survey, the sittings, the unplaced rows, the counts and `order_source`. Served at `GET /api/cockpit/walk`.

**The rows are `ledger.owed` and nothing else**, asserted by computing both sides over a fixture and over `your-trainer`'s live corpus (`tests/test_walk_payload.py`). 39 rows on its open Android release; 4 on this repo at the time of writing.

**The rules are upstream's.** `tools/scripts/walk-sheet.py` is bundled verbatim as `src/project_os_cockpit/walk_sheet_bundled.py` and `tests/test_walk_bundle.py` asserts the two files are byte-identical. The one adaptation the sidecar needs — upstream's `_validator()` looks for `validate-docs.py` beside itself, and beside the bundled copy the file is `validate_docs_bundled.py` — is done by seeding the module's global in `acceptance._walk_module`, precisely so the identity assertion can stay exact.

**What the cockpit supplies, and it is lookups rather than rules:** its own check scoping (`acceptance.load`, so the walk and `~checks` see one suite), its ledger reader (`ledger.load`, so one parser validates every ledger this app reads), and the note index that turns an id into a title and finds the `SUR-*` note for a surface.

### Decisions taken here

- **Bundle, never import from the browsed repo.** The proposal in the plan, taken as written. A repo's own copy of the script is for a person generating Markdown; reading it would make the page's behaviour depend on how recently that repo synced.
- **The scoping is the cockpit's, and the difference is reported rather than chosen.** Upstream reads every `level: acceptance` note anywhere under `docs/`; `acceptance.load` reads the ones the suite holds. The payload takes the cockpit's owed set, and any row the bundled module then drops is reported in `errors` rather than silently missing. Running the two side by side on this repo immediately produced a real difference, filed as [[ISS-0303-The-Walk-Sheet-Lists-Retired-Checks]].
- **`gallery` is one field on the payload, not one per survey entry.** The task's wording put it on the entry; it is a property of the repo, and repeating it under every surface would print one fact many times.
- **`all` is refused at the route, not answered.** So is a platform name no ledger carries: it reads no verdicts and reports every check in the repo as owed.
