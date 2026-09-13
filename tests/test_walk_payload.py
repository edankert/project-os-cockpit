"""`acceptance.walk_payload` — the owed checks as a procedure ([[TASK-0618]]).

Constructed fixtures throughout, plus one comparison against `your-trainer`'s
live corpus when that repo is checked out beside this one. The live test is the
only one that can catch a rule the fixtures happen to satisfy; the fixtures are
the only ones that can be read as a specification, so both are here.

The property every other assertion hangs off is the first one: **the rows are
`ledger.owed` and nothing else.** A walk that showed a different set from the
gate would be a second answer to *what does this release owe*, which is the
thing the ledger exists to prevent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, ledger
from project_os_cockpit.index import Index


# --------------------------------------------------------------- fixtures

def _check(docs: Path, tid: str, *, area: str, body: str = "",
           after: str = "", covers: str = "", command: str = "",
           title: str = "") -> None:
    (docs / "tests" / "acceptance").mkdir(parents=True, exist_ok=True)
    extra = ""
    if after:
        extra += f"after: [{after}]\n"
    if covers:
        extra += f"covers: [{covers}]\n"
    if command:
        extra += f'command: "{command}"\n'
    (docs / "tests" / "acceptance" / f"{tid}.md").write_text(
        f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "{title or tid}"\n'
        f'level: acceptance\nstatus: active\narea: "{area}"\nmark: todo\n'
        f"{extra}---\n\n# {title or tid}\n\n{body}\n", encoding="utf-8")


def _ledger(docs: Path, platform: str, entries: list[dict],
            *, sealed: str = "", release: str = "") -> None:
    name = f"{release or 'WORKING'}-{platform}.json"
    path = docs / "releases" / "ledgers" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    body: dict = {"platform": platform, "entries": entries}
    if sealed:
        body["sealed"] = sealed
        body["release"] = release
    path.write_text(json.dumps(body, indent=2), encoding="utf-8")


def _walk_order(docs: Path, text: str) -> None:
    (docs / "tests" / "acceptance").mkdir(parents=True, exist_ok=True)
    (docs / "tests" / "acceptance" / "WALK.md").write_text(text, encoding="utf-8")


def _payload(docs: Path, *, platform: str = "android", release: str = "") -> dict:
    return acceptance.walk_payload(docs, Index.build(docs),
                                   platform=platform, release=release)


def _rows(payload: dict) -> list[dict]:
    out = [r for s in payload["sittings"] for r in s["rows"]]
    out.extend(payload["unplaced"])
    return out


def _ids(payload: dict) -> list[str]:
    return [r["id"] for r in _rows(payload)]


_ORDER_ONE_SITTING = """# Walk order

### A fresh install

```yaml
state: "the app installed and never opened"
surfaces: ["Profile"]
bench: ["a wiped phone", "a trainer paired"]
```
"""


# ------------------------------------------------- the row set IS the owed set

def test_the_rows_are_exactly_what_the_ledger_says_is_owed(tmp_path: Path) -> None:
    """The feature's whole claim, asserted by computing both sides.

    `TST-0002` has a surviving `pass`, so the gate does not ask for it and
    neither does the walk. `TST-0003` carries a `command:`, so no person owes
    it at all ([[ADR-0039]]).
    """
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _check(docs, "TST-0002", area="Profile")
    _check(docs, "TST-0003", area="Profile", command="pytest -k thing")
    _check(docs, "TST-0004", area="Workouts")
    _ledger(docs, "android", [
        {"check": "TST-0002", "date": "2026-09-01", "mark": "pass",
         "by": "user:edwin", "method": "manual"},
    ])

    payload = _payload(docs)
    suite = acceptance.load(docs, Index.build(docs), platform="android")
    manual = [i.note_id for i in suite.items
              if acceptance.section_of(i) in acceptance.MANUAL_SECTIONS]
    owed = ledger.owed(docs, "android", manual)

    assert sorted(_ids(payload)) == sorted(owed) == ["TST-0001", "TST-0004"]
    assert payload["counts"]["owed"] == 2


def test_a_blocking_verdict_is_still_owed(tmp_path: Path) -> None:
    """`fail` does not clear. Somebody walked it and it is still on the list —
    the distinction the character vocabulary could not carry."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _ledger(docs, "android", [
        {"check": "TST-0001", "date": "2026-09-01", "mark": "fail",
         "reason": "the screen is blank", "by": "user:edwin", "method": "manual"},
    ])
    assert _ids(_payload(docs)) == ["TST-0001"]


def test_no_row_appears_twice(tmp_path: Path) -> None:
    """A check claimed by two sittings is walked once, in the first.

    The alternative is a walker recording two verdicts for one check in one
    sitting, which the ledger would accept and nobody could read back.
    """
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _ledger(docs, "android", [])
    _walk_order(docs, """---
gallery: ""
---

# Walk order

### First

```yaml
surfaces: ["Profile"]
```

### Second

```yaml
surfaces: ["Profile"]
```
""")
    payload = _payload(docs)
    assert _ids(payload) == ["TST-0001"]
    assert [s["name"] for s in payload["sittings"]] == ["First"]


def test_a_check_no_sitting_claims_is_unplaced(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _check(docs, "TST-0002", area="Nobody names this")
    _ledger(docs, "android", [])
    _walk_order(docs, _ORDER_ONE_SITTING)
    payload = _payload(docs)
    assert [r["id"] for r in payload["sittings"][0]["rows"]] == ["TST-0001"]
    assert [r["id"] for r in payload["unplaced"]] == ["TST-0002"]
    assert payload["counts"] == {"owed": 2, "placed": 1, "unplaced": 1}


def test_a_sitting_names_a_check_by_id(tmp_path: Path) -> None:
    """`checks:` claims one check whatever its area says — the escape hatch for
    the check that has to be walked in a state its surface does not imply."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _check(docs, "TST-0002", area="Workouts")
    _ledger(docs, "android", [])
    _walk_order(docs, """# Walk order

### By id

```yaml
checks: ["TST-0002"]
```

### By surface

```yaml
surfaces: ["Profile"]
```
""")
    payload = _payload(docs)
    assert [[r["id"] for r in s["rows"]] for s in payload["sittings"]] == [
        ["TST-0002"], ["TST-0001"]]


def test_a_sitting_with_no_owed_row_is_not_rendered(tmp_path: Path) -> None:
    """An empty sitting is a heading a walker reads and cannot act on."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _ledger(docs, "android", [])
    _walk_order(docs, _ORDER_ONE_SITTING + """
### Never claimed

```yaml
surfaces: ["Workouts"]
```
""")
    payload = _payload(docs)
    assert [s["name"] for s in payload["sittings"]] == ["A fresh install"]


def test_the_sitting_carries_its_state_and_bench(tmp_path: Path) -> None:
    """The two facts the hand-written run plan's pre-flight held and no note
    could: what state the sitting starts from, and what must be on the bench."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _ledger(docs, "android", [])
    _walk_order(docs, _ORDER_ONE_SITTING)
    sitting = _payload(docs)["sittings"][0]
    assert sitting["state"] == "the app installed and never opened"
    assert sitting["bench"] == ["a wiped phone", "a trainer paired"]
    assert sitting["surfaces"] == ["Profile"]


# ------------------------------------------------------------------ ordering

def test_after_orders_rows_inside_a_sitting(tmp_path: Path) -> None:
    """`after:` beats id order, and only inside the sitting that holds both."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile", after='"TST-0002"')
    _check(docs, "TST-0002", area="Profile")
    _ledger(docs, "android", [])
    _walk_order(docs, _ORDER_ONE_SITTING)
    payload = _payload(docs)
    assert [r["id"] for r in payload["sittings"][0]["rows"]] == [
        "TST-0002", "TST-0001"]


def test_after_reads_the_wikilink_form_too(tmp_path: Path) -> None:
    """The corpus writes both forms; reading one of them is [[ISS-0173]]."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile", after='"[[TST-0002]]"')
    _check(docs, "TST-0002", area="Profile")
    _ledger(docs, "android", [])
    payload = _payload(docs)
    assert [r["id"] for r in _rows(payload)] == ["TST-0002", "TST-0001"]
    assert _rows(payload)[1]["after"] == ["TST-0002"]


def test_a_cycle_is_reported_and_the_walk_still_happens(tmp_path: Path) -> None:
    """Nothing gates on `after:`, so failing the sheet over a cycle would cost
    the walker their afternoon to save an ordering. It is an error on the
    payload and the rows fall back to id order."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile", after='"TST-0002"')
    _check(docs, "TST-0002", area="Profile", after='"TST-0001"')
    _ledger(docs, "android", [])
    payload = _payload(docs)
    assert [r["id"] for r in _rows(payload)] == ["TST-0001", "TST-0002"]
    assert payload["errors"], "a cycle was swallowed"
    assert "TST-0001" in payload["errors"][0]
    assert "TST-0002" in payload["errors"][0]


def test_the_cycle_phrase_is_the_one_the_payload_keys_on() -> None:
    """`_CYCLE_PHRASE` is upstream's wording, and the payload sorts errors from
    warnings by it. Pinned here so a reword upstream fails a test rather than
    silently demoting a cycle to something to tidy in WALK.md."""
    from project_os_cockpit import walk_sheet_bundled as walk
    warnings: list[str] = []
    walk.order_rows(
        [walk.Check(id="TST-0001", title="a", path="a.md", after=["TST-0002"]),
         walk.Check(id="TST-0002", title="b", path="b.md", after=["TST-0001"])],
        warnings, "Somewhere")
    assert warnings and acceptance._CYCLE_PHRASE in warnings[0]


# ---------------------------------------------------------------- the row

def test_a_row_carries_the_procedure_and_the_checks_row_shape(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile", title="Sign in", body=(
        "## Setup\n\nA signed-out app.\n\n"
        "## Steps\n\n1. Tap Sign in.\n\n"
        "## Expect\n\nThe profile screen.\n"))
    _ledger(docs, "android", [])
    row = _rows(_payload(docs))[0]
    assert row["setup"] == "A signed-out app."
    assert row["steps"] == "1. Tap Sign in."
    assert row["expect"] == "The profile screen."
    #: The `~checks` row shape, unforked — the page reuses `buildCheckRow`.
    assert row["id"] == "TST-0001"
    assert row["name"] == "Sign in"
    assert row["mark"] == "todo"
    assert row["rel"].endswith("TST-0001.md")


def test_a_note_with_no_headings_says_so_and_keeps_its_prose(tmp_path: Path) -> None:
    """53 of `your-trainer`'s 61 owed rows are in this shape. A row that
    printed nothing for them would be a sheet nobody can walk."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile",
           body="Open the app and confirm the splash screen appears.")
    _ledger(docs, "android", [])
    row = _rows(_payload(docs))[0]
    assert row["setup"] is None
    assert row["steps"] is None
    assert row["lead"] == "Open the app and confirm the splash screen appears."


def test_the_older_headings_are_read_as_fallbacks(tmp_path: Path) -> None:
    """`Procedure` and `Expected results` are the pre-ADR-0027 shape. Setup has
    no fallback, and that absence is what "not stated" means."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile", body=(
        "## Procedure\n\nTap it.\n\n## Expected results\n\nIt opens.\n"))
    _ledger(docs, "android", [])
    row = _rows(_payload(docs))[0]
    assert row["steps"] == "Tap it."
    assert row["expect"] == "It opens."
    assert row["setup"] is None


# ---------------------------------------------------------------- the order

def test_with_no_walk_order_the_payload_says_so(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Workouts")
    _check(docs, "TST-0002", area="Profile")
    _ledger(docs, "android", [])
    payload = _payload(docs)
    assert payload["order_source"] == "fallback"
    #: One sitting per area, in area order, id order inside.
    assert [s["name"] for s in payload["sittings"]] == ["Profile", "Workouts"]
    assert not payload["unplaced"]


def test_the_authored_order_is_the_file_order(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _check(docs, "TST-0002", area="Workouts")
    _ledger(docs, "android", [])
    _walk_order(docs, """# Walk order

### Workouts first

```yaml
surfaces: ["Workouts"]
```

### Profile second

```yaml
surfaces: ["Profile"]
```
""")
    payload = _payload(docs)
    assert payload["order_source"] == "walk.md"
    assert [s["name"] for s in payload["sittings"]] == [
        "Workouts first", "Profile second"]


def test_a_sitting_that_claims_nothing_is_a_warning_not_an_error(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _ledger(docs, "android", [])
    _walk_order(docs, """# Walk order

### Claims nothing

```yaml
state: "anything"
```
""")
    payload = _payload(docs)
    assert payload["warnings"], "a sitting claiming nothing went unreported"
    assert not payload["errors"]


def test_the_gallery_command_is_read_verbatim(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _ledger(docs, "android", [])
    _walk_order(docs, """---
gallery: "./gradlew recordScreenshots"
---

# Walk order

### A sitting

```yaml
surfaces: ["Profile"]
```
""")
    assert _payload(docs)["gallery"] == "./gradlew recordScreenshots"


# -------------------------------------------------------------- the guard rail

def test_the_payload_carries_no_time_estimate(tmp_path: Path) -> None:
    """[[TASK-0449]]'s guard rail, which this feature keeps: order, never a
    schedule. Counts of rows are the only numbers."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile", body="## Setup\n\nTakes 5 minutes.\n")
    _ledger(docs, "android", [])
    payload = _payload(docs)

    banned = {"minutes", "minute", "duration", "estimate", "eta"}
    seen: list[str] = []

    def walk_keys(node, where: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if str(key).lower() in banned:
                    seen.append(f"{where}.{key}")
                walk_keys(value, f"{where}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk_keys(value, f"{where}[{i}]")

    walk_keys(payload, "payload")
    assert not seen, f"the walk payload carries a time estimate: {seen}"
    #: …and the note's own prose is untouched. The rule is about what the
    #: payload computes, never about censoring what a check says.
    assert "5 minutes" in (_rows(payload)[0]["setup"] or "")


def test_a_mistyped_platform_reads_no_ledger_at_all(tmp_path: Path) -> None:
    """Why the route refuses an unknown platform name instead of answering.

    A walk asked for by a name no ledger carries reads no verdicts, so every
    check in the repo comes back owed — 545 rows on `your-trainer`, with no
    warning. `/api/cockpit/walk` checks the name against `ledger.platforms`
    first (`tests/test_walk_route.py`); this records why it has to.
    """
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _ledger(docs, "android", [
        {"check": "TST-0001", "date": "2026-09-01", "mark": "pass",
         "by": "user:edwin", "method": "manual"},
    ])
    assert _ids(_payload(docs, platform="android")) == []
    assert _ids(_payload(docs, platform="andriod")) == ["TST-0001"]
    assert ledger.platforms(docs) == ["android"]


def test_the_bundled_module_and_the_ledger_agree_on_a_sealed_excuse(
        tmp_path: Path) -> None:
    """The one resolution rule the two implementations could differ on.

    An `excused` expires when its ledger seals and a `pass` beneath it does
    not. If the module and `ledger.owed` read that differently the payload
    reports it as an error rather than quietly showing the smaller set — so a
    clean run here is the assertion that they agree.
    """
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _check(docs, "TST-0002", area="Profile")
    _ledger(docs, "android", [
        {"check": "TST-0001", "date": "2026-08-01", "mark": "pass",
         "by": "user:edwin", "method": "manual"},
        {"check": "TST-0001", "date": "2026-08-02", "mark": "excused",
         "reason": "not this cycle", "by": "user:edwin", "method": "manual"},
        {"check": "TST-0002", "date": "2026-08-02", "mark": "excused",
         "reason": "not this cycle", "by": "user:edwin", "method": "manual"},
    ], sealed="2026-08-03", release="REL-0001")
    _ledger(docs, "android", [])
    payload = _payload(docs)
    #: TST-0001 keeps the `pass` under the expired excuse; TST-0002 had nothing
    #: underneath and is owed again.
    assert _ids(payload) == ["TST-0002"]
    assert not payload["errors"], payload["errors"]


# ------------------------------------------------------------- the live corpus

YOUR_TRAINER = Path(__file__).resolve().parents[2] / "your-trainer" / "docs"


@pytest.mark.skipif(not YOUR_TRAINER.is_dir(),
                    reason="your-trainer is not checked out beside this repo")
def test_the_live_corpus_row_set_equals_ledger_owed() -> None:
    """The exit criterion, computed both ways over the corpus the page is for.

    A fixture cannot catch a rule that only fires at 600 notes; this is the
    only test that reads the suite the walk page was built to render.
    """
    index = Index.build(YOUR_TRAINER)
    platform = (ledger.platforms(YOUR_TRAINER) or ["android"])[0]
    payload = acceptance.walk_payload(YOUR_TRAINER, index, platform=platform)

    suite = acceptance.load(YOUR_TRAINER, index, platform=platform)
    manual = [i.note_id for i in suite.items
              if i.note_id and acceptance.section_of(i) in acceptance.MANUAL_SECTIONS]
    owed = ledger.owed(YOUR_TRAINER, platform, manual)

    got = _ids(payload)
    assert len(got) == len(set(got)), "a check appears on the walk twice"
    assert sorted(got) == sorted(owed)
    assert payload["counts"]["owed"] == len(owed)
    assert not payload["errors"], payload["errors"]
