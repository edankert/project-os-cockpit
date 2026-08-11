"""Done is not shipped (FEAT-0072 / TASK-0315).

The cockpit has always known one of these two facts. `status: done` is the
other one's twin and was standing in for it, which is how a project ships
nothing for six months while every surface reads green.

The interesting case is the one that cannot be observed in this repo today:
**no release has ever been `released`**, so the branch that subtracts shipped
features never runs here. A test that only exercised the live corpus would
pass while that branch was broken — which it briefly was, calling an
`extract_ids` this module does not import. So the shipped case is built
explicitly.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from project_os_cockpit import cockpit
from project_os_cockpit.index import Index


FIXTURE = Path(__file__).parent / "fixtures" / "index_basic"
REPO_DOCS = Path(__file__).resolve().parent.parent / "docs"


@pytest.fixture()
def docs(tmp_path: Path) -> Path:
    target = tmp_path / "docs"
    shutil.copytree(FIXTURE, target)
    return target


def _write(docs: Path, name: str, body: str) -> None:
    (docs / "releases").mkdir(parents=True, exist_ok=True)
    (docs / "releases" / name).write_text(body, encoding="utf-8")


def _feature(docs: Path, fid: str, status: str) -> None:
    d = docs / "features" / fid.lower()
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{fid}-Thing.md").write_text(
        f'---\ntype: "[[feature]]"\nid: {fid}\naliases: ["{fid}"]\n'
        f'title: "A thing"\nstatus: {status}\n---\n\n# A thing\n',
        encoding="utf-8",
    )


def test_a_draft_release_ships_nothing(docs: Path) -> None:
    """`draft` is *"prepared and verified, not yet live"* — so drafting a note
    must not empty the card.

    This is the whole reason the filter is on `released` and not on existence.
    A count that fell to zero the moment somebody wrote a plan would be the
    surface asserting that the release had happened.
    """
    _feature(docs, "FEAT-9001", "done")
    _write(docs, "REL-0001-Draft.md",
           '---\ntype: "[[release]]"\nid: REL-0001\naliases: ["REL-0001"]\n'
           'title: "Drafted"\nstatus: draft\ndate: "2026-08-11"\n'
           'features: ["[[FEAT-9001]]"]\n---\n\n# Drafted\n')

    payload = cockpit.unreleased_payload(Index.build(docs))
    assert "FEAT-9001" in [r["id"] for r in payload["items"]], (
        "a drafted release emptied the card; drafting is not shipping"
    )
    assert payload["since"] is None


def test_a_released_release_ships_what_it_names(docs: Path) -> None:
    """The branch this repo cannot exercise, built on purpose.

    No release here has ever been `released`, so this path never runs against
    the live corpus — and it was broken when first written (a `NameError` on
    an unimported helper) without any test noticing.
    """
    _feature(docs, "FEAT-9001", "done")
    _feature(docs, "FEAT-9002", "done")
    _feature(docs, "FEAT-9003", "planned")
    _write(docs, "REL-0001-Shipped.md",
           '---\ntype: "[[release]]"\nid: REL-0001\naliases: ["REL-0001"]\n'
           'title: "Shipped"\nstatus: released\ndate: "2026-08-01"\n'
           'features: ["[[FEAT-9001]]", "[[FEAT-9003]]"]\n---\n\n# Shipped\n')

    payload = cockpit.unreleased_payload(Index.build(docs))
    ids = [r["id"] for r in payload["items"]]
    assert "FEAT-9001" not in ids, "a shipped feature is still counted unreleased"
    assert "FEAT-9002" in ids, "a done feature no release names went missing"
    assert "FEAT-9003" not in ids, "a planned feature is not 'done but unshipped'"
    assert payload["since"] is not None
    assert payload["since"]["id"] == "REL-0001"
    assert payload["since"]["date"] == "2026-08-01"


def test_the_newest_shipped_release_is_the_one_reported(docs: Path) -> None:
    """`since` names the latest, so the card's sentence is about the right one."""
    _feature(docs, "FEAT-9001", "done")
    _write(docs, "REL-0001-Old.md",
           '---\ntype: "[[release]]"\nid: REL-0001\naliases: ["REL-0001"]\n'
           'title: "Old"\nstatus: released\ndate: "2026-01-01"\n'
           'features: []\n---\n\n# Old\n')
    _write(docs, "REL-0002-New.md",
           '---\ntype: "[[release]]"\nid: REL-0002\naliases: ["REL-0002"]\n'
           'title: "New"\nstatus: released\ndate: "2026-06-01"\n'
           'features: []\n---\n\n# New\n')

    since = cockpit.unreleased_payload(Index.build(docs))["since"]
    assert since is not None and since["id"] == "REL-0002", since


def test_the_count_matches_the_rows_and_the_rows_can_navigate(docs: Path) -> None:
    """The card navigates, so every row needs a rel the renderer accepts."""
    _feature(docs, "FEAT-9001", "done")
    payload = cockpit.unreleased_payload(Index.build(docs))
    assert payload["count"] == len(payload["items"])
    for row in payload["items"]:
        assert row.get("rel"), f"{row.get('id')} has no rel; the row is a dead click"
        assert not str(row["rel"]).startswith("/"), (
            "rows carry a docs-relative rel, like every other record row"
        )


def test_the_real_repo_reports_its_actual_state() -> None:
    """The number this project should be showing today.

    Written while REL-0001 was `draft`, asserting `since is None` — nothing had
    shipped, so every done feature was unreleased — with the failure message
    saying what to do on the day that stopped being true: *"if that is real,
    this project's first release has happened and this assertion should record
    it."* **2026-08-11: it happened.** REL-0001 is `released` at `1.0.0`, so the
    card now measures against it instead of against nothing.

    The floor stays a floor rather than an exact count, which would fail every
    time a feature closes.
    """
    payload = cockpit.unreleased_payload(Index.build(REPO_DOCS))
    since = payload["since"]
    assert since is not None, "the first release has un-shipped itself"
    assert since["id"] == "REL-0001" and since["date"] == "2026-08-11"
    # The 27 features REL-0001 names are shipped; what remains is everything
    # done before it that the release did not claim.
    assert payload["count"] >= 50, payload["count"]
    # **The whole named set**, not a sample of it. Independent review pointed
    # out that four names cannot catch a membership bug in the other 23, and
    # that a floor of 40 against a live 59 is looser than the state it guards.
    # The release note's `features:` list is the set membership is computed
    # from, so read it rather than restating it here.
    note = (REPO_DOCS / "releases" / "REL-0001-The-Human-Has-Levers.md").read_text(
        encoding="utf-8",
    )
    named = set(re.findall(r"\[\[(FEAT-\d+)", note.split("features:", 1)[1].split("\n", 1)[0]))
    assert len(named) == 27, sorted(named)
    assert not named & {row["id"] for row in payload["items"]}, (
        "a feature this release names is still counted as unreleased"
    )


# ---------------------------------------------------------------------------
# TASK-0316 — drafting a release, which publishes nothing
# ---------------------------------------------------------------------------


def test_drafting_writes_one_file_and_ships_nothing(docs: Path) -> None:
    """The whole risk surface of this feature, asserted.

    Drafting allocates an id and writes a note. It must not set `released`,
    must not stamp a `date` (that records when it SHIPPED), and must not touch
    anything else in the corpus — pushing and deploying stay a person's
    deliberate act (FEAT-0055's line).
    """
    from project_os_cockpit import note_writes

    _feature(docs, "FEAT-9001", "done")
    _feature(docs, "FEAT-9002", "done")
    index = Index.build(docs)
    before = {p: p.read_text(encoding="utf-8") for p in docs.rglob("*.md")}

    result = note_writes.create_release(
        index, docs, title="First light", features=["FEAT-9001", "FEAT-9002"],
    )

    assert result["status"] == "draft"
    note = (docs / result["rel"]).read_text(encoding="utf-8")
    assert "status: draft" in note
    assert 'date: ""' in note, "a drafted release stamped a ship date it has not earned"
    assert "[[FEAT-9001]]" in note and "[[FEAT-9002]]" in note

    # Nothing else moved.
    for path, text in before.items():
        assert path.read_text(encoding="utf-8") == text, f"drafting modified {path.name}"


def test_the_drafted_note_lists_what_the_card_showed(docs: Path) -> None:
    """One computation, two consumers.

    The card's count and the note's `features:` must be the same set, or the
    human confirms one number and the record keeps another.
    """
    from project_os_cockpit import note_writes

    _feature(docs, "FEAT-9001", "done")
    _feature(docs, "FEAT-9002", "done")
    _feature(docs, "FEAT-9003", "planned")
    index = Index.build(docs)

    payload = cockpit.unreleased_payload(index)
    shown = [r["id"] for r in payload["items"]]
    result = note_writes.create_release(index, docs, title="Second", features=shown)

    assert result["features"] == shown
    assert "FEAT-9003" not in result["features"], "a planned feature reached the note"


def test_the_id_increments_and_a_collision_is_refused(docs: Path) -> None:
    """`counters.REL` read 0 for six months; this is the first path that raises it."""
    from project_os_cockpit import note_writes

    assert note_writes.next_release_id(Index.build(docs)) == "REL-0001"
    note_writes.create_release(Index.build(docs), docs, title="One", features=[])
    assert note_writes.next_release_id(Index.build(docs)) == "REL-0002"

    # A stale index computes an id that already exists — refused, not overwritten.
    stale = Index.build(docs)
    note_writes.create_release(stale, docs, title="Two", features=[])
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.create_release(stale, docs, title="Two again", features=[])
    assert exc.value.status == 409


def test_a_release_needs_a_title(docs: Path) -> None:
    from project_os_cockpit import note_writes

    with pytest.raises(note_writes.WriteError):
        note_writes.create_release(Index.build(docs), docs, title="   ", features=[])


def test_release_is_creatable_and_the_door_stayed_narrow() -> None:
    """Widening the allow-list is the thing to notice, so it is asserted."""
    from project_os_cockpit import note_writes

    assert note_writes.CREATABLE_TYPES == {"issue", "release"}, (
        "the creatable set changed; each type earns its own review of what "
        "'next id' and 'which template' mean (FEAT-0059's Out of Scope)"
    )
