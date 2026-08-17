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

from project_os_cockpit import cockpit, note_writes, publication, statuses
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
    assert "ISS-0347 unfixed." in d["known_issues_html"]
    assert "not this" not in d["known_issues_html"]


def test_a_release_with_no_such_section_reports_nothing(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0", body="\n## Scope\n\nstuff.")
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert d["known_issues_html"] == ""


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
    assert "ISS-0347" in d["known_issues_html"]
    assert "<table" in d["known_issues_html"], "the table is RENDERED, not printed"
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


# ---- ISS-0179: six from reading the view ---------------------------------


def test_the_next_release_does_not_read_as_settled(tmp_path: Path) -> None:
    """The inversion Edwin found. A next release is by definition full of
    `done` features, so carrying each feature's own status made the whole
    group read as finished — it went to the Completed band while shipped
    releases, whose rows had no status at all, sorted to the top as open.

    **Asserted as the property, not as a proxy for it** (ISS-0191). This read
    `all(status == "ready")`, which is one way to keep the group unsettled and
    was mistaken for the rule itself — so when the acceptance row started
    reporting the gate (`blocked`/`passing`, which IS its state in this
    release) the guard went red over a change it had no opinion about, while
    still not covering the state that would actually break it: nothing
    unshipped and a settled gate, where the only row left is terminal.

    Both halves are pinned now. Rows that stand for a NOTE still carry
    `ready`; the group as a whole must always hold something unfinished.
    """
    docs = _docs(tmp_path)
    (docs / "features" / "f").mkdir(parents=True)
    (docs / "features" / "f" / "FEAT-0001-F.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "F"\n'
        "status: done\n---\n", encoding="utf-8",
    )
    groups = cockpit.nav_payload(
        Index.build(docs), "publication", project_root=docs.parent,
    )["groups"]
    nxt = groups[0]
    assert nxt["key"] == "release-next", "the next release comes first"
    rows = [i for sg in nxt["subgroups"] for i in sg["items"]] + nxt["items"]
    named = [i for i in rows if i["id"]]
    assert named, "no row names a note, so the rule below asserts nothing"
    assert all(i["status"] == "ready" for i in named), \
        "a row's status is its state IN THIS RELEASE, not the note's own"
    _assert_not_all_terminal(rows)


def _assert_not_all_terminal(rows: list) -> None:
    """The property `groupIsSettled` reads: a group every one of whose rows is
    terminal sinks into the Completed band."""
    open_rows = [
        r for r in rows
        if str(r.get("status") or "").lower() not in statuses.COMPLETED_STATUSES
    ]
    assert open_rows, (
        "every row in the next release is terminal, so the navigator files "
        "it under COMPLETED — the ISS-0179 inversion, reached again"
    )


def test_a_settled_gate_and_nothing_unshipped_still_reads_as_open(
    tmp_path: Path,
) -> None:
    """The state the old proxy could not see (ISS-0191).

    Nothing waiting on a release, every Tier 1/2 check settled: the features
    subgroup is absent, so the only row left is the acceptance one — and it is
    `passing`, which is terminal. `Next release` would file itself under
    Completed, which is what Edwin has now reported twice.
    """
    docs = _docs(tmp_path)          # `_docs` writes a suite with one unticked row
    (docs / "tests" / "ACCEPTANCE_TESTS.md").write_text(
        "# Tier 1 — Feature Tests\n\n## 1.1 Area (FEAT-0001)\n"
        "- [x] **A:** walked.\n", encoding="utf-8",
    )
    groups = cockpit.nav_payload(
        Index.build(docs), "publication", project_root=docs.parent,
    )["groups"]
    nxt = groups[0]
    assert nxt["key"] == "release-next"
    rows = [i for sg in nxt["subgroups"] for i in sg["items"]] + nxt["items"]
    assert any("Nothing unshipped" in str(r["title"]) for r in rows), (
        "the placeholder that says the release is empty is unreachable — it "
        "was keyed on the subgroups being empty, and the acceptance subgroup "
        "is almost always there"
    )
    _assert_not_all_terminal(rows)


def test_a_shipped_release_reads_as_settled(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    groups = {
        g["key"]: g for g in cockpit.nav_payload(
            Index.build(docs), "publication", project_root=docs.parent,
        )["groups"]
    }
    shipped = groups["release-REL-0001"]
    rows = [i for sg in shipped["subgroups"] for i in sg["items"]]
    assert all(i["status"] == "released" for i in rows)
    assert shipped["default_open"] is False


def test_a_release_carries_its_date(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    (docs / "releases" / "REL-0001-R.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\nstatus: released\n'
        'version: "1.0.0"\ndate: "2026-07-05"\nfeatures: []\n---\n',
        encoding="utf-8",
    )
    groups = cockpit.nav_payload(
        Index.build(docs), "publication", project_root=docs.parent,
    )["groups"]
    label = next(g["label"] for g in groups if g["key"] == "release-REL-0001")
    assert "2026-07-05" in label, label


def test_a_release_carries_its_tests_and_artifacts_in_the_navigator(
    tmp_path: Path,
) -> None:
    """*"The acceptance tests are not available in the left hand"* and *"the
    other release files are also not available there"*. A release's content is
    not only its features."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0",
         verified='["[[ACCEPTANCE_TESTS_v1.0.0]]"]')
    (docs / "releases" / "REL-0001-v1.0.0-play-store-listing.xml").write_text("<x/>")
    groups = {
        g["key"]: g for g in cockpit.nav_payload(
            Index.build(docs), "publication", project_root=docs.parent,
        )["groups"]
    }
    # Grouped by type now (ISS-0180): Features / Issues / Acceptance tests /
    # Documents, rather than one flat list where a play-store XML sat between
    # a feature and a test.
    subs = {sg["label"].split(" ·")[0]: sg
            for sg in groups["release-REL-0001"]["subgroups"]}
    assert "Acceptance tests" in subs and "Documents" in subs, sorted(subs)
    assert any("ACCEPTANCE" in i["title"] for i in subs["Acceptance tests"]["items"])
    assert any(i["title"].endswith(".xml") for i in subs["Documents"]["items"])
    # And exactly ONE way to the release itself: its own group header. A
    # `Release note` row underneath was a second route to the same subject,
    # and a confusing one — the header opens the PAGE, the row opened the raw
    # note.
    rows = [i for sg in groups["release-REL-0001"]["subgroups"] for i in sg["items"]]
    assert all(i["title"] != "Release note" for i in rows)
    assert groups["release-REL-0001"]["url"] == "~release/REL-0001"


def test_the_next_release_carries_all_the_acceptance_tests(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    groups = cockpit.nav_payload(
        Index.build(docs), "publication", project_root=docs.parent,
    )["groups"]
    rows = [i for sg in groups[0]["subgroups"] for i in sg["items"]]
    assert any(r["url"] == "/docs/tests/ACCEPTANCE_TESTS.md" for r in rows)


def test_a_wikilink_whose_slug_drifted_still_resolves(tmp_path: Path) -> None:
    """`REL-0012` cites `[[FEAT-0085-BleHardening]]`; the note is
    `FEAT-0085-BleReliabilityLayer`. The id is the identity and the slug is
    decoration."""
    docs = tmp_path / "docs"
    (docs / "features" / "f").mkdir(parents=True)
    (docs / "features" / "f" / "FEAT-0085-BleReliabilityLayer.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0085\ntitle: "BLE"\n'
        "status: done\n---\n", encoding="utf-8",
    )
    index = Index.build(docs)
    assert index.resolve("FEAT-0085-BleHardening") is not None
    assert index.resolve("FEAT-0085") is not None


def test_an_exact_filename_still_beats_the_id_fallback(tmp_path: Path) -> None:
    """The fallback is tried LAST. A note whose filename is the cited string
    must win, or the fallback would silently redirect real links."""
    docs = tmp_path / "docs"
    (docs / "features" / "f").mkdir(parents=True)
    for slug, nid in (("FEAT-0085-BleHardening", "FEAT-0090"),
                      ("FEAT-0085-Other", "FEAT-0085")):
        (docs / "features" / "f" / f"{slug}.md").write_text(
            f'---\ntype: "[[feature]]"\nid: {nid}\ntitle: "{slug}"\n'
            "status: done\n---\n", encoding="utf-8",
        )
    index = Index.build(docs)
    resolved = index.resolve("FEAT-0085-BleHardening")
    assert resolved is not None and "BleHardening" in resolved


def test_the_publication_badge_counts_only_what_the_view_shows(
    tmp_path: Path,
) -> None:
    """Edwin: *"if you remove it then it should no longer be included in the
    badge in the view icon."* A count on a button that opens a view not
    containing what it counts sends the reader somewhere the work is not."""
    from project_os_cockpit import obligations

    assert obligations.NOTE_LESS["unpushed commit"].view == "overview"
    assert obligations.NOTE_LESS["undeployed commit"].view == "overview"
    assert obligations.NOTE_LESS["release gate"].view == "publication"


def test_a_group_whose_content_is_nested_is_judged_on_that_content() -> None:
    """`groupIsSettled([])` is TRUE by design — an empty list has no unsettled
    member. Harmless while every group carried its rows directly; wrong the
    moment a release's content moved into subgroups, because `items` went
    empty and `Preparing · 2.1.7` filed itself under Completed.

    Edwin asked *"why is preparing in the completed section?"* twice: first
    because a row carried its feature's own status, then because there were no
    rows to read at all. Both are one mistake — asking the question of the
    wrong list.
    """
    src = (
        Path(__file__).resolve().parents[1]
        / "desktop" / "src" / "renderer" / "renderer.ts"
    ).read_text(encoding="utf-8")
    assert "function allGroupItems(" in src
    # Neither caller may go back to reading `items` alone.
    assert "groupIsSettled(group.items" not in src, (
        "a settled check that reads only `items` is blind to nested content"
    )
    assert src.count("groupIsSettled(allGroupItems(group))") == 2
