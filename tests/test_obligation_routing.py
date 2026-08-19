"""Obligation routing is per-item and complete (TST-0025 / FEAT-0101).

Guards [[ADR-0028]] against the two ways it fails silently: a kind that routes
nowhere and is therefore counted nowhere, and an in-flight rule that quiets
more than it was asked to.

Constructed fixtures, deliberately — the fleet measurement is TST-0026's job.
These are the cases that must hold whatever any repo happens to contain.

**The two most dangerous cases are the ones that produce a smaller number
without failing anything**: an obligation naming no subject, and one naming a
subject whose status nobody declared. Both are tested, both ask, and both are
mutation-tested against the implementation that would quietly drop them.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import cockpit, obligations
from project_os_cockpit.index import Index

REPO_DOCS = Path(__file__).resolve().parents[1] / "docs"


def _note(path: Path, fm: dict[str, object], body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for key, value in fm.items():
        lines.append(f"{key}: {value!r}" if isinstance(value, str) else f"{key}: {value}")
    lines.append("---")
    path.write_text("\n".join(lines) + "\n" + body, encoding="utf-8")


@pytest.fixture()
def docs(tmp_path: Path) -> Path:
    """A corpus with one feature per status and obligations pointed at them."""
    d = tmp_path / "docs"
    for fid, status in (
        ("FEAT-0001", "doing"), ("FEAT-0002", "backlog"), ("FEAT-0003", "done"),
        ("FEAT-0004", "planned"), ("FEAT-0005", "cancelled"),
        ("FEAT-0006", "hibernating"),          # declared by nobody
    ):
        _note(d / "features" / fid.lower() / f"{fid}-F.md", {
            "type": "[[feature]]", "id": fid, "title": f"Feature {fid}",
            "status": status,
            # Every fixture feature declares its acceptance impact discharged.
            # These tests are about the IN-FLIGHT rule — which subject's status
            # makes a requirement or a test owed — and a feature at `doing`
            # legitimately owes an acceptance sweep of its own since TASK-0468.
            # Leaving the field absent would make every count in this module
            # about two rules at once, and the first of them to change would
            # break tests that have no opinion about it.
            "acceptance_impact": "none — fixture, nothing to sweep",
        })
    return d


def _index(docs: Path) -> Index:
    return Index.build(docs)


# ---- 1-2: the shape holds ------------------------------------------------


def test_every_kind_routes_somewhere() -> None:
    """A type or note-less source with no routing rule fails here.

    The completeness burden `obligations.py` already carries for undeclared
    types, extended to the axis ADR-0028 adds. Per-item routing must not become
    the place a kind goes missing quietly.
    """
    index = Index.build(REPO_DOCS)
    for note_type, ob in obligations.OBLIGATIONS.items():
        if not ob.owed:
            continue
        assert ob.view or ob.route, f"{note_type} routes nowhere"
        if ob.route is None:
            assert ob.view in obligations.VIEWS, note_type
    for kind, source in obligations.note_less_sources().items():
        assert source.view in obligations.VIEWS, kind
    # And every view a route can produce is a real view.
    for path in index.paths():
        record = index.get(path)
        if record is None or not record.note_type:
            continue
        ob = obligations.for_type(record.note_type)
        if ob is None or not ob.owed:
            continue
        view = obligations.view_for(record, ob)
        assert view in obligations.VIEWS or view == "", record.note_id


def test_the_page_and_the_badge_are_one_walk() -> None:
    """`counts_by_kind` is DERIVED from `owed_items` (TASK-0423), so the two
    cannot drift. It used to be a second pass asserted equal — a property that
    has to be maintained rather than one that holds by construction."""
    index = Index.build(REPO_DOCS)
    rows = obligations.owed_items(index)
    counts = obligations.counts_by_kind(index)
    for view in obligations.VIEWS:
        assert sum(counts[view].values()) == len(rows[view]), view


# ---- 3-7: requirements ---------------------------------------------------


@pytest.mark.parametrize(
    ("feature", "owed"),
    [
        ("FEAT-0001", True),    # doing
        ("FEAT-0004", True),    # planned — scheduled is live work
        ("FEAT-0002", False),   # backlog
        ("FEAT-0003", False),   # done
        ("FEAT-0005", False),   # cancelled
    ],
)
def test_a_requirement_asks_while_its_feature_is_in_flight(
    docs: Path, feature: str, owed: bool,
) -> None:
    _note(docs / "requirements" / "REQ-0001-R.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "R",
        "status": "draft", "implements": f'["[[{feature}]]"]',
    })
    ids = [r["id"] for r in obligations.owed_items(_index(docs))["features"]]
    assert ("REQ-0001" in ids) is owed


def test_any_subject_in_flight_is_enough(docs: Path) -> None:
    """A requirement naming several features asks if ANY is live."""
    _note(docs / "requirements" / "REQ-0001-R.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "R",
        "status": "draft", "implements": '["[[FEAT-0002]]", "[[FEAT-0001]]"]',
    })
    ids = [r["id"] for r in obligations.owed_items(_index(docs))["features"]]
    assert "REQ-0001" in ids


def test_deferred_beats_the_rule_even_when_the_feature_is_doing(
    docs: Path,
) -> None:
    """The derived rule is a DEFAULT; `deferred` is a DECISION (ADR-0028
    decision 6). The case that separates them is exactly this one — a deferred
    requirement whose feature comes alive must stay quiet."""
    _note(docs / "requirements" / "REQ-0001-R.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "R",
        "status": "deferred", "implements": '["[[FEAT-0001]]"]',
    })
    index = _index(docs)
    assert [r["id"] for r in obligations.owed_items(index)["features"]] == []
    # …and it is not in the QUIET group either: it never entered the rule,
    # because `deferred` is not an owed status for its type.
    assert [r["id"] for r in obligations.suppressed_items(index)["features"]] == []


# ---- 8-11: tests, and the two dangerous cases ---------------------------


def test_a_manual_test_asks_while_a_feature_it_verifies_is_in_flight(
    docs: Path,
) -> None:
    _note(docs / "tests" / "TST-0001-T.md", {
        "type": "[[test]]", "id": "TST-0001", "title": "T", "status": "ready",
        "kind": "manual", "last_verified": "2026-01-01",
        "features": '["[[FEAT-0001]]"]',
    }, "## Steps\n1. Do it.\n")
    ids = [r["id"] for r in obligations.owed_items(_index(docs))["tests"]]
    assert ids == ["TST-0001"]


def test_a_manual_test_rests_when_every_subject_is_terminal(docs: Path) -> None:
    _note(docs / "tests" / "TST-0001-T.md", {
        "type": "[[test]]", "id": "TST-0001", "title": "T", "status": "ready",
        "kind": "manual", "last_verified": "2026-01-01",
        "features": '["[[FEAT-0003]]", "[[FEAT-0005]]"]',
    }, "## Steps\n1. Do it.\n")
    index = _index(docs)
    assert obligations.owed_items(index)["tests"] == []
    quiet = obligations.suppressed_items(index)["tests"]
    assert [r["id"] for r in quiet] == ["TST-0001"]
    # The row carries the REASON — the subject and its status.
    assert quiet[0]["subjects"] == [
        {"id": "FEAT-0003", "status": "done"},
        {"id": "FEAT-0005", "status": "cancelled"},
    ]


def test_an_obligation_naming_no_subject_still_asks(docs: Path) -> None:
    """THE clause most likely to be got wrong.

    `your-trainer`'s TST-0001 and TST-0002 are `scope: system` with no
    features. Under a naive reading they become never-owed, which LOSES two
    tests rather than quieting them — and it shows up only as a smaller number,
    never as a failure. Nothing can prove a subject-less obligation is resting,
    so it asks.
    """
    _note(docs / "tests" / "TST-0001-T.md", {
        "type": "[[test]]", "id": "TST-0001", "title": "T", "status": "ready",
        "kind": "manual", "last_verified": "2026-01-01", "features": "[]",
    }, "## Steps\n1. Do it.\n")
    index = _index(docs)
    assert [r["id"] for r in obligations.owed_items(index)["tests"]] == ["TST-0001"]
    assert obligations.suppressed_items(index)["tests"] == []


def test_an_undeclared_subject_status_still_asks(docs: Path) -> None:
    """A status in neither set is not evidence of rest.

    Silently quieting on one would make every future status value a way to
    disappear from the badge — and `RESTING_STATES` is derived from
    `statuses.COMPLETED_STATUSES` precisely so a new terminal value arrives
    resting rather than becoming a permanent question.
    """
    _note(docs / "tests" / "TST-0001-T.md", {
        "type": "[[test]]", "id": "TST-0001", "title": "T", "status": "ready",
        "kind": "manual", "last_verified": "2026-01-01",
        "features": '["[[FEAT-0006]]"]',          # status: hibernating
    }, "## Steps\n1. Do it.\n")
    ids = [r["id"] for r in obligations.owed_items(_index(docs))["tests"]]
    assert ids == ["TST-0001"]


def test_a_subject_the_corpus_does_not_carry_still_asks(docs: Path) -> None:
    """A dangling `implements:` cannot be shown to be resting either."""
    _note(docs / "requirements" / "REQ-0001-R.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "R",
        "status": "draft", "implements": '["[[FEAT-9999]]"]',
    })
    ids = [r["id"] for r in obligations.owed_items(_index(docs))["features"]]
    assert ids == ["REQ-0001"]


def test_the_terminal_statuses_of_every_subject_type_rest() -> None:
    """The first draft hand-listed feature statuses and missed `implemented`,
    `retired` and `fixed` — a test's subject can be a requirement or an issue.
    Measured on `your-trainer`: 8 owed tests where the rule should leave 5, and
    all three extras were that one gap."""
    for status in ("implemented", "retired", "fixed", "done", "cancelled",
                   "superseded", "backlog", "deferred"):
        assert status in obligations.RESTING_STATES, status
    for status in ("doing", "review", "planned"):
        assert status not in obligations.RESTING_STATES, status


# ---- 12: triage is untouched --------------------------------------------


def test_triage_is_owed_in_every_phase(docs: Path) -> None:
    """Its subject is the ISSUE — nobody has read it yet — not the thing the
    issue is about. That is why it is the one obligation the rule does not
    shrink, and it follows from the model rather than being carved out."""
    _note(docs / "issues" / "ISS-0001-I.md", {
        "type": "[[issue]]", "id": "ISS-0001", "title": "I", "status": "triage",
    })
    index = _index(docs)
    assert [r["id"] for r in obligations.owed_items(index)["issues"]] == ["ISS-0001"]
    assert obligations.suppressed_items(index)["issues"] == []
    assert "issue" not in obligations.SUBJECT_FIELDS


# ---- 13-15: the quiet is on screen --------------------------------------


def test_a_suppressed_row_is_counted_nowhere(docs: Path) -> None:
    """Not the badge, not the digest, not the fleet card."""
    _note(docs / "requirements" / "REQ-0001-R.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "R",
        "status": "draft", "implements": '["[[FEAT-0002]]"]',
    })
    index = _index(docs)
    # Scoped to the view under test: an empty fixture tree owes 8 standing
    # documents it has never written, which is correct and is not this rule's
    # business.
    assert obligations.counts(index)["features"] == 0
    assert "requirement" not in obligations.badges_payload(index)["breakdown"].get(
        "features", {},
    )
    digest = cockpit.digest_payload(docs.parent, index, "")
    assert all(i["id"] != "REQ-0001" for i in digest["needs_you"])
    # …and it is on screen.
    group = cockpit.suppressed_group(index, "features")
    assert len(group) == 1
    assert [i["id"] for i in group[0]["items"]] == ["REQ-0001"]


def test_the_lines_count_equals_the_rows_it_expands_to(docs: Path) -> None:
    for n in range(1, 4):
        _note(docs / "requirements" / f"REQ-000{n}-R.md", {
            "type": "[[requirement]]", "id": f"REQ-000{n}", "title": "R",
            "status": "draft", "implements": '["[[FEAT-0002]]"]',
        })
    group = cockpit.suppressed_group(_index(docs), "features")[0]
    assert "3" in group["label"]
    assert len(group["items"]) == 3
    assert group["suppressed"] is True
    assert not group.get("needs_human"), \
        "the quiet group must not claim to need a person"


def test_the_line_is_absent_when_nothing_is_suppressed(docs: Path) -> None:
    """Absent at zero — this project's standing rule, and a permanent
    `0 more` is the shape a reader learns to stop seeing."""
    _note(docs / "requirements" / "REQ-0001-R.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "R",
        "status": "draft", "implements": '["[[FEAT-0001]]"]',
    })
    assert cockpit.suppressed_group(_index(docs), "features") == []


def test_a_repo_with_no_phases_routes_and_labels_without_inventing_one(
    docs: Path,
) -> None:
    """Three of the twelve repos have no `PHASE-*` notes at all. Phase is the
    grouping LABEL; the rule reads feature status, so nothing here may require
    a phase to exist."""
    _note(docs / "requirements" / "REQ-0001-R.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "R",
        "status": "draft", "implements": '["[[FEAT-0002]]"]',
    })
    group = cockpit.suppressed_group(_index(docs), "features")[0]
    assert "no phase" in group["label"]
    assert "PHASE" not in group["label"]


# ---- 16: routing moves the row, never the note --------------------------


def test_routing_moves_the_row_and_never_the_note() -> None:
    """ADR-0025's shortcut, not a relocation. A `TST-*` stays listed in the
    Tests navigator whichever phase currently owes it — a note that vanished
    from its own view at the moment a reader needed it would make the tree
    wrong exactly when it matters."""
    index = Index.build(REPO_DOCS)
    # Tier groups included since ADR-0031: an acceptance test is a `test` note
    # and the navigator lists it under its tier. Skipping them here was free
    # while a check was a different type; now it would assert that 34 notes have
    # vanished from a view they are plainly in.
    listed = set()
    for group in cockpit.nav_payload(index, "tests")["groups"]:
        listed.update(str(i["id"]) for i in group["items"])
    #: **Acceptance checks are represented by their SURFACE** (ISS-0222), so
    #: they are not individually listed and must not be: `your-trainer` put
    #: 579 of them in this pane. Nothing is lost — REQ-0047 criterion 3 — the
    #: surface row expands to its checks on the page that can walk them, and
    #: says how many. What this guards is that every EXECUTABLE test still has
    #: its own row, which is the population ADR-0025's shortcut is about.
    corpus = {
        r.note_id for r in index.notes_by_type("test")
        if r.note_id and not r.rel_path.startswith("__templates__/")
        and str(r.frontmatter.get("level", "") or "").strip().lower()
        != "acceptance"
    }
    assert corpus <= listed, corpus - listed

    #: And every acceptance check is accounted for by exactly one surface row.
    from project_os_cockpit import acceptance as _acc

    suite = _acc.load(index.docs_root, index)
    if suite.exists:
        areas = {str(i.area or "").strip() or "—" for i in suite.items}
        assert areas <= listed, areas - listed


def test_a_tests_subject_fields_track_the_link_rename() -> None:
    """ADR-0032 renamed the field `subject_ids` reads, and the rename was missed.

    `SUBJECT_FIELDS["test"]` named `verifies`/`features`/`requirements`, all
    three of which ADR-0032 deleted from every test in this repo — so
    `subject_ids` resolved nothing for 77 of 77 notes and
    `subject_is_in_flight` treats a subject-less note as LIVE by design. The
    in-flight quieting switched off for the whole test population and the badge
    moved 1 → 3, silently. Found by independent review.

    Asserted as *the field a test declares must be one this reads*, so the next
    rename fails here instead of moving a number nobody is watching.
    """
    from project_os_cockpit import obligations

    assert "covers" in obligations.SUBJECT_FIELDS["test"], (
        "SUBJECT_FIELDS lost the field ADR-0032 made canonical; the in-flight "
        "rule silently stops applying to every test"
    )
    index = Index.build(REPO_DOCS)
    resolving = [
        r.note_id for r in index.notes_by_type("test")
        if r.frontmatter.get("covers") and obligations.subject_ids(r)
    ]
    declaring = [
        r.note_id for r in index.notes_by_type("test") if r.frontmatter.get("covers")
    ]
    assert len(resolving) == len(declaring), (
        f"{len(declaring) - len(resolving)} test(s) declare a subject that "
        "subject_ids cannot see"
    )


def test_a_draft_requirement_does_not_outvote_its_own_backlog_feature() -> None:
    """ISS-0202: a feature and its requirements are not peers.

    `ids_in_flight` is *"in flight if ANY subject is"*, written for peers — *"a
    section naming several features is walkable while one of them is live"*. A
    `draft` requirement of a `backlog` feature is the same fact counted twice,
    in the direction that asks: TST-0024 was owed because REQ-0035/0036 sit at
    `draft` while FEAT-0099 has not been started and its phase is `planned`.

    Deliberately narrow. The broader *"all subjects must be live"* rule was
    measured across twelve repos and silences four tests whose subjects include
    a feature at `doing` — `your-trainer`'s iOS parity walk among them — so it
    trades this noise for a real silence.
    """
    index = Index.build(REPO_DOCS)
    owed = {r["id"] for r in obligations.owed_items(index).get("tests", [])}
    assert "TST-0024" not in owed, (
        "TST-0024 is owed again: a draft requirement is outvoting the backlog "
        "feature it implements"
    )
    # And the rule must not have quieted everything — a test whose feature is
    # genuinely live still asks.
    record = index.get(index.by_id("TST-0024"))
    assert record is not None and record.status == "ready", (
        "TST-0024 is no longer `ready`, so this guard has lost its subject"
    )
