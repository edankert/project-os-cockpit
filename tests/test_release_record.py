"""A release shows the record it kept (TST-0034 / FEAT-0107).

The finding this feature turned on: **Edwin's model was already implemented,
in his files, and nothing read it.** `tests_verified:`, the known-issues
section and the platform artifacts have been maintained by hand across twelve
releases and were invisible in the cockpit.

So most of these assert *reading*, not behaviour.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import cockpit, note_writes, publication
from project_os_cockpit.index import Index

YT = Path.home() / "Dev" / "repos" / "your-trainer" / "docs"


def _docs(tmp_path: Path) -> Path:
    d = tmp_path / "docs"
    (d / "releases").mkdir(parents=True)
    (d / "tests").mkdir(parents=True)
    (d / "tests" / "ACCEPTANCE_TESTS.md").write_text(
        "# Tier 1 — Feature Tests\n\n## 1.1 Area (FEAT-0001)\n- [ ] **A:** do it.\n",
        encoding="utf-8",
    )
    return d


def _rel(docs: Path, rid: str, status: str, version: str, *,
         verified: str = "[]", body: str = "") -> None:
    (docs / "releases" / f"{rid}-R.md").write_text(
        f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
        f'status: {status}\nversion: "{version}"\nfeatures: []\n'
        f"tests_verified: {verified}\n---\n\n# R\n{body}\n", encoding="utf-8",
    )


# ---- what it verified ----------------------------------------------------


def test_a_shipped_release_shows_what_it_verified(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0",
         verified='["[[ACCEPTANCE_TESTS_v1.0.0]]", "[[TST-0011-Thing]]"]')
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert [v["id"] for v in d["tests_verified"]] == [
        "ACCEPTANCE_TESTS_v1.0.0", "TST-0011-Thing",
    ]


def test_a_release_that_recorded_nothing_says_so(tmp_path: Path) -> None:
    """Five of your-trainer's twelve are empty. Saying *not recorded* is the
    honest answer; showing today's suite would claim the release was measured
    against a document written after it shipped."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert d["tests_verified"] == []


def test_a_shipped_release_shows_no_live_gate(tmp_path: Path) -> None:
    """Review finding P5. It shipped in July; recomputing the live suite for
    it answers a question nobody asked."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert d["gate"] == {}


def test_an_unshipped_release_still_shows_the_live_gate(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    d = publication.release_payload(docs.parent, Index.build(docs), "next")
    assert d["gate"]["exists"] is True


# ---- what it shipped with ------------------------------------------------


def test_the_known_issues_section_is_surfaced(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0",
         body="\n## Known issues (shipping with)\n\nISS-0347 unfixed.\n\n## Next\n\nnot this.")
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert "ISS-0347 unfixed." in d["known_issues"]
    assert "not this" not in d["known_issues"]


def test_a_release_with_no_such_section_reports_nothing(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0", body="\n## Scope\n\nstuff.")
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert d["known_issues"] == ""


# ---- what it published ---------------------------------------------------


def test_artifacts_are_found_by_the_convention(tmp_path: Path) -> None:
    """ADR-0028's amendment: a file in docs/releases/ named for the release is
    that release's artifact. The note is the record, not an artifact of it."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0007", "released", "2.0.0")
    (docs / "releases" / "REL-0007-v2.0.0-play-store-listing.xml").write_text("<x/>")
    (docs / "releases" / "REL-0008-v2.0.2-play-store-listing.xml").write_text("<x/>")
    found = publication.artifacts_for(docs, "REL-0007")
    assert [a["name"] for a in found] == ["REL-0007-v2.0.0-play-store-listing.xml"]
    assert found[0]["kind"] == "play store listing"


def test_the_release_note_is_not_its_own_artifact(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0007", "released", "2.0.0")
    assert publication.artifacts_for(docs, "REL-0007") == []


# ---- capture at ship -----------------------------------------------------


def test_recording_writes_only_what_it_was_given(tmp_path: Path) -> None:
    """It does not snapshot, copy or guess. Ten of twelve releases shipped
    with the field empty because nobody was ever asked — asking is the whole
    mechanism."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    index = Index.build(docs)
    before = sorted(p.name for p in (docs / "releases").iterdir())
    note_writes.record_verification(
        index, "REL-0001", verified=["ACCEPTANCE_TESTS_v1.0.0", "TST-0011"],
    )
    after = sorted(p.name for p in (docs / "releases").iterdir())
    assert before == after, "no file may be created by recording"
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert [v["id"] for v in d["tests_verified"]] == [
        "ACCEPTANCE_TESTS_v1.0.0", "TST-0011",
    ]


def test_recording_nothing_leaves_it_not_recorded(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    note_writes.record_verification(Index.build(docs), "REL-0001", verified=[])
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert d["tests_verified"] == []


def test_the_record_route_is_loopback_guarded() -> None:
    src = (
        Path(__file__).resolve().parents[1]
        / "src" / "project_os_cockpit" / "server.py"
    ).read_text(encoding="utf-8")
    body = src.split("def _serve_release_verified(")[1].split("\n        def ")[0]
    assert "_require_loopback" in body


# ---- against the repo that has kept this record by hand ------------------


@pytest.mark.skipif(not YT.is_dir(), reason="your-trainer not present")
def test_the_record_your_trainer_already_kept_is_readable() -> None:
    """The claim this feature turned on, checked against the real corpus."""
    index = Index.build(YT)
    d = publication.release_payload(YT.parent, index, "REL-0012")
    assert [v["id"] for v in d["tests_verified"]] == [
        "ACCEPTANCE_CHECKLIST_v2.1.1",
        "TST-0011-AndroidBleHardeningAcceptance",
        "TST-0014-EdgeToEdgeInsetAcceptance",
    ]
    assert [a["kind"] for a in d["artifacts"]] == ["play store listing"]
    assert "ISS-0347" in d["known_issues"]
    assert d["gate"] == {}, "a release shipped in July shows no live gate"


# ---- ISS-0175: the checkbox correspondence -------------------------------


def test_a_task_list_after_a_paragraph_renders_no_checkboxes() -> None:
    """The cause, which was unknown when ISS-0175 was filed and is not a
    parser bug at all.

    Markdown lazy continuation: a task list opening immediately after a
    paragraph line, with no blank line between, is absorbed into the
    paragraph. It renders **zero** checkboxes while `_criterion_text` — being
    line-based — counts every one. That is the whole 579-against-542 gap.
    """
    import re as _re

    from project_os_cockpit.renderer import _markdown_to_html

    def boxes(text: str) -> int:
        html = _markdown_to_html(
            text, resolver=lambda t: None,
            asset_resolver=lambda t, s=None: None, source_path=Path("x.md"),
        )
        return len(_re.findall(r'type="checkbox"', html))

    assert boxes("## H\n\nSee the note.\n\n- [x] **A:** one.\n") == 1
    assert boxes("## H\n\nSee the note.\n- [x] **A:** one.\n") == 0


def test_a_count_mismatch_labels_nothing_rather_than_mislabelling() -> None:
    """`resolve_criterion` matches the source exactly BECAUSE ambiguity there
    is meant to be a refusal rather than a guess. Feeding it a confidently
    wrong value defeats that, and 285 of 542 rows in `your-trainer`'s suite
    were carrying another row's text."""
    import re as _re

    from project_os_cockpit.renderer import _markdown_to_html

    swallowed = "## H\n\nSee the note.\n- [x] **A:** one.\n\n- [x] **B:** two.\n"
    html = _markdown_to_html(
        swallowed, resolver=lambda t: None,
        asset_resolver=lambda t, s=None: None, source_path=Path("x.md"),
    )
    assert 'type="checkbox"' in html, "the fixture must still render a box"
    assert "data-raw=" not in html, (
        "a document whose counts disagree must carry NO data-raw at all — "
        "the alignment is unknowable, not merely short"
    )


def test_a_well_formed_document_still_gets_its_labels() -> None:
    """The refusal must be narrow: it degrades only the documents it cannot
    align, not every document."""
    import re as _re

    from project_os_cockpit.renderer import _markdown_to_html

    html = _markdown_to_html(
        "## H\n\n- [x] **A:** one.\n- [ ] **B:** two.\n",
        resolver=lambda t: None,
        asset_resolver=lambda t, s=None: None, source_path=Path("x.md"),
    )
    assert html.count("data-raw=") == 2
