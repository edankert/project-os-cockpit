"""A shipped release reports what it kept (TST-0036 / FEAT-0109, FEAT-0110).

Two headings on the release page assert things nobody checks. *"Acceptance
tests as executed"* links `REL-0012` to a note with **18 unticked boxes and 18
blank evidence slots**; *"Published artifacts"* lists two XML files that **do
not parse**. And `## Post-Release Actions` — 37 unticked boxes across eight
notes — is read by nothing at all.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import publication
from project_os_cockpit.index import Index

TRAINER = Path.home() / "Dev" / "repos" / "your-trainer"
needs_trainer = pytest.mark.skipif(
    not (TRAINER / "docs").is_dir(), reason="../your-trainer is not present",
)


class _Rec:
    def __init__(self, body: str = "", **front: object) -> None:
        self.body = body
        self.frontmatter = front
        self.status = str(front.get("status") or "")
        self.note_type = str(front.get("note_type") or "test")
        self.title = ""
        self.rel_path = ""


# ----- grading the evidence (TASK-0450) -------------------------------------


def test_a_blank_evidence_slot_does_not_count_as_evidence() -> None:
    """The mutation that must fail.

    `TST-0011` has eighteen `- Evidence: ___` lines and zero observations. A
    grader that counted the slot rather than its contents would report it 18/18
    evidenced, which is precisely the false claim this exists to remove.
    """
    rec = _Rec(
        "- [ ] **A:** do the thing.\n"
        "  - Evidence: ___\n"
        "- [ ] **B:** do the other.\n"
        "  - Evidence: ___\n",
    )
    grade = publication._grade(rec)
    assert grade["total"] == 2
    assert grade["walked"] == 0
    assert grade["evidence"] == 0


def test_a_filled_slot_a_witness_and_a_dated_verdict_all_count() -> None:
    """Three forms, all measured in the corpus rather than invented."""
    rec = _Rec(
        "- [x] **A:** did it.\n"
        "  - Evidence: saw 69 bpm on the tile\n"
        "- [x] **B:** did it. ✅ (Claude, tablet: address rotated)\n"
        "- [~] **C:** partly. **Partial pass 2026-06-06**: German locale.\n",
    )
    grade = publication._grade(rec)
    assert grade["total"] == 3
    assert grade["walked"] == 2
    assert grade["evidence"] == 3


def test_last_verified_equal_to_created_reads_as_never_verified() -> None:
    """15 of the 16 `TST-*` notes carrying the field are in this state: it is
    stamped by the template at authoring time and has never once recorded a
    verification. "Never" is the honest word, not "stale"."""
    same = _Rec("", created="2026-06-25", last_verified="2026-06-25")
    moved = _Rec("", created="2026-06-25", last_verified="2026-07-02")
    absent = _Rec("", created="2026-06-25")
    assert publication._grade(same)["never_verified"] is True
    assert publication._grade(moved)["never_verified"] is False
    assert publication._grade(absent)["never_verified"] is False


# ----- checking the artifacts (TASK-0451) -----------------------------------


def test_a_malformed_artifact_reports_its_line(tmp_path: Path) -> None:
    bad = tmp_path / "REL-0001-v1.0.0-play-store-listing.xml"
    bad.write_text(
        '<?xml version="1.0"?>\n<release-notes version="1.0.0">\n'
        "  <en-GB>hello</en-GB>\n</release-notes>\n</invoke>\n",
        encoding="utf-8",
    )
    got = publication._check_artifact(bad)
    assert got["checked"] is True and got["ok"] is False
    assert "does not parse" in got["problem"]
    assert "line 5" in got["problem"]


def test_a_store_listing_reports_its_locales_and_longest_entry(
    tmp_path: Path,
) -> None:
    good = tmp_path / "REL-0001-v1.0.0-play-store-listing.xml"
    good.write_text(
        '<?xml version="1.0"?>\n<release-notes version="1.0.0">\n'
        "  <en-GB>short</en-GB>\n  <de-DE>a somewhat longer one</de-DE>\n"
        "</release-notes>\n",
        encoding="utf-8",
    )
    got = publication._check_artifact(good)
    assert got["ok"] is True
    assert got["locales"] == 2
    assert got["longest"] == len("a somewhat longer one")


def test_an_entry_over_the_ceiling_is_a_problem(tmp_path: Path) -> None:
    over = tmp_path / "REL-0001-v1.0.0-play-store-listing.xml"
    over.write_text(
        '<?xml version="1.0"?>\n<release-notes version="1.0.0">\n'
        f"  <en-GB>{'x' * 501}</en-GB>\n</release-notes>\n",
        encoding="utf-8",
    )
    got = publication._check_artifact(over)
    assert got["ok"] is False and "501" in got["problem"]


def test_a_kind_the_checker_does_not_know_gets_no_verdict(
    tmp_path: Path,
) -> None:
    """Implying judgement over a file it does not understand would be the same
    overreach as a gate counting what it cannot read."""
    other = tmp_path / "REL-0001-v1.0.0-screenshot.png"
    other.write_bytes(b"\x89PNG\r\n")
    got = publication._check_artifact(other)
    assert got == {"checked": False}


def test_one_malformed_artifact_does_not_hide_the_others(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "releases"
    folder.mkdir()
    (folder / "REL-0001-v1.0.0-a-listing.xml").write_text(
        "<r>\n</r>\n</invoke>\n", encoding="utf-8")
    (folder / "REL-0001-v1.0.0-b-listing.xml").write_text(
        '<release-notes><en-GB>ok</en-GB></release-notes>\n', encoding="utf-8")
    got = publication.artifacts_for(tmp_path, "REL-0001")
    assert len(got) == 2
    assert [a["ok"] for a in got] == [False, True]


# ----- the post-release checklist (TASK-0452) -------------------------------


def test_a_checklist_under_a_h3_is_found() -> None:
    """**Five of the eight** use `###`. A reader anchored on `##` finds 12
    boxes where the corpus holds 37 — measured, not assumed."""
    body = (
        "## Summary\n\nsome prose\n\n"
        "### Post-Release Actions\n\n"
        "- [x] Already done\n- [ ] Still owed\n- [ ] Also owed\n"
    )
    got = publication.post_release_actions(body)
    assert [b["text"] for b in got] == ["Still owed", "Also owed"]


def test_a_subsection_inside_the_checklist_stays_part_of_it() -> None:
    """The section ends at a heading at or ABOVE its own level — the ISS-0172
    rule, which this project has had to learn once already on a different
    parser."""
    body = (
        "### Post-Release Actions\n\n- [ ] Top level\n\n"
        "#### Later that week\n\n- [ ] Nested\n\n"
        "## A new top-level section\n\n- [ ] Not ours\n"
    )
    got = publication.post_release_actions(body)
    assert [b["text"] for b in got] == ["Top level", "Nested"]


def test_a_note_with_no_such_section_yields_nothing() -> None:
    assert publication.post_release_actions("## Summary\n\n- [ ] a box\n") == []


def test_a_retrospective_heading_is_not_a_checklist() -> None:
    """`## Post-Release Review — PHASE-010 findings` is a retrospective.
    Sweeping it in would offer to tick prose."""
    body = "## Post-Release Review — findings\n\n- [ ] we should have tested X\n"
    assert publication.post_release_actions(body) == []


# ----- the three verdicts (TASK-0453) ---------------------------------------


class _Idx:
    def __init__(self, notes: dict[str, _Rec]) -> None:
        self._n = notes

    def by_id(self, note_id: str):          # noqa: ANN201
        return note_id if note_id in self._n else None

    def get(self, path):                    # noqa: ANN001, ANN201
        return self._n.get(path)


def test_a_tag_that_exists_is_done_and_one_that_does_not_is_open() -> None:
    index = _Idx({})
    done = publication.verdict_for("Tag repo: `git tag v2.0.5`", index,
                                   {"v2.0.5"})
    missing = publication.verdict_for("Tag repo: `git tag v2.0.2`", index,
                                      {"v2.0.5"})
    assert done["verdict"] == publication.DONE
    assert missing["verdict"] == publication.OPEN


def test_pushing_a_tag_is_unknowable_not_done() -> None:
    """A local tag existing says nothing about whether it was pushed, and the
    box asks about pushing."""
    got = publication.verdict_for(
        "Push tag: `git push origin v2.0.5 && git push`", _Idx({}), {"v2.0.5"},
    )
    assert got["verdict"] == publication.UNKNOWABLE


def test_a_status_box_is_done_only_when_every_note_reached_it() -> None:
    index = _Idx({
        "ISS-0268": _Rec(status="fixed", note_type="issue"),
        "ISS-0269": _Rec(status="fixed", note_type="issue"),
        "ISS-0270": _Rec(status="open", note_type="issue"),
    })
    both = publication.verdict_for(
        "Set `status: fixed` on ISS-0268 + ISS-0269", index, set())
    one = publication.verdict_for(
        "Set `status: fixed` on ISS-0268 + ISS-0270", index, set())
    assert both["verdict"] == publication.DONE
    assert one["verdict"] == publication.OPEN


def test_a_failed_lookup_is_never_done() -> None:
    """The direction that fails safe. A wrong `done` offers a tick that
    destroys the only record the obligation existed."""
    got = publication.verdict_for(
        "Set `status: fixed` on ISS-9999", _Idx({}), set())
    assert got["verdict"] == publication.UNKNOWABLE
    got_no_tags = publication.verdict_for(
        "Tag repo: `git tag v1.0.0`", _Idx({}), None)
    assert got_no_tags["verdict"] == publication.UNKNOWABLE


def test_an_impossible_status_splits_on_whether_anything_happened() -> None:
    """`published` is not a release status and `passing` is not a requirement
    status — four release notes instruct the first. But the two cases differ:
    REL-0010 is already `released` (stale phrasing for something terminal),
    while REQ-0183 is still `draft` and has not moved in 85 days. Collapsing
    both to `unknowable` would bury a live obligation behind a wording
    complaint.
    """
    index = _Idx({
        "REL-0010": _Rec(status="released", note_type="release"),
        "REQ-0183": _Rec(status="draft", note_type="requirement"),
    })
    stale = publication.verdict_for(
        "Update REL-0010 status to `published`", index, set())
    live = publication.verdict_for(
        "Set `status: passing` on REQ-0183 after the window", index, set())
    assert stale["verdict"] == publication.UNKNOWABLE
    assert live["verdict"] == publication.OPEN
    # Both still say the instruction cannot be followed as written.
    assert "not a valid release status" in stale["evidence"]
    assert "not a valid requirement status" in live["evidence"]


def test_a_box_naming_nothing_the_record_holds_is_unknowable() -> None:
    for text in [
        "Upload AAB to Play Console",
        "Watch Play Console Vitals for 30 days; zero entries is the bar",
        "flip reported_issues.investigation_status in compatibility.json",
    ]:
        got = publication.verdict_for(text, _Idx({}), set())
        assert got["verdict"] == publication.UNKNOWABLE, text


# ----- against the real corpus ----------------------------------------------


@needs_trainer
def test_both_corrupt_store_artifacts_are_reported_and_the_others_are_not(
) -> None:
    """Two of seven, both ending with leaked tool-call closing tags after the
    root element — in the declared source of truth for store copy in ten
    locales."""
    bad, good = [], []
    for number in range(1, 14):
        for art in publication.artifacts_for(TRAINER / "docs", f"REL-{number:04d}"):
            (bad if art.get("checked") and not art["ok"] else good).append(
                art["name"])
    assert sorted(bad) == [
        "REL-0007-v2.0.0-play-store-descriptions.xml",
        "REL-0009-v2.0.4-play-store-listing.xml",
    ]
    assert len(good) == 5


@needs_trainer
def test_every_good_store_listing_carries_ten_locales() -> None:
    for number in range(7, 13):
        for art in publication.artifacts_for(TRAINER / "docs", f"REL-{number:04d}"):
            if art.get("ok") and art.get("locales"):
                assert art["locales"] == 10, art["name"]
                assert art["longest"] <= publication._STORE_CEILING


@needs_trainer
def test_rel_0012_names_a_test_note_where_nothing_was_walked() -> None:
    """The heading says *"as executed"*. This is what it links to."""
    index = Index.build(TRAINER / "docs")
    payload = publication.release_payload(TRAINER, index, "REL-0012")
    row = next(v for v in payload["tests_verified"] if "TST-0011" in v["id"])
    assert row["grade"]["total"] == 18
    assert row["grade"]["walked"] == 0
    assert row["grade"]["evidence"] == 0


@needs_trainer
def test_the_corpus_holds_thirty_seven_unticked_post_release_boxes() -> None:
    index = Index.build(TRAINER / "docs")
    total, notes = 0, 0
    for number in range(1, 14):
        owed = publication.release_payload(
            TRAINER, index, f"REL-{number:04d}").get("still_owed") or []
        if owed:
            notes += 1
            total += len(owed)
    assert (notes, total) == (6, 37)


@needs_trainer
def test_the_boxes_the_record_can_decide_are_decided() -> None:
    index = Index.build(TRAINER / "docs")
    owed = publication.release_payload(TRAINER, index, "REL-0010")["still_owed"]

    def verdict(needle: str) -> str:
        hits = [b for b in owed if needle in b["text"]]
        assert len(hits) == 1, f"{needle!r} matched {len(hits)} boxes"
        return str(hits[0]["verdict"])

    assert verdict("git tag v2.0.5") == publication.DONE
    assert verdict("ISS-0268") == publication.DONE
    assert verdict("REQ-0183") == publication.OPEN
    # 85 days after the fix shipped, and nothing in the repo can prove it
    # either way — which is the honest answer, not a guess. The box names a
    # JSON field in a SIBLING workspace; inferring its value from prose is
    # exactly the guess `unknowable` exists to refuse.
    assert verdict("compatibility.json") == publication.UNKNOWABLE


# ----- lazy continuation, asked of the renderer (TASK-0452) -----------------


@pytest.mark.parametrize(("before", "expected"), [
    ("some prose\n\n", 1),          # blank line — a real list
    ("some prose\n", 0),            # ISS-0175: absorbed into the paragraph
    ("1. First thing\n", 1),        # a sibling list item, renders fine
    ("- First thing\n", 1),
    ("- [x] Already done\n", 1),
])
def test_a_box_is_read_only_when_it_renders_as_one(
    before: str, expected: int,
) -> None:
    """The first attempt used the obvious heuristic — *refuse unless the line
    above is itself a checkbox* — and it was wrong on the corpus: after a
    numbered item a `- [ ]` becomes a **sibling**, not a continuation. The rule
    is now asked of the same markdown pipeline the page renders with, because
    Markdown's behaviour here is not reconstructible by eye.
    """
    body = f"### Post-Release Actions\n\n{before}- [ ] Ship it\n"
    assert len(publication.post_release_actions(body)) == expected


# ----- the age (TASK-0453) --------------------------------------------------


def test_only_an_open_box_carries_an_age() -> None:
    """An age on a done box is noise; an age on an unknowable one implies the
    tool knows it is outstanding."""
    record = _Rec(
        "### Post-Release Actions\n\n"
        "- [ ] Tag repo: `git tag v1.0.0`\n"
        "- [ ] Tag repo: `git tag v9.9.9`\n"
        "- [ ] Upload the thing somewhere\n",
    )
    index = _Idx({})
    rows = publication.still_owed(
        record, index, Path("/nonexistent"), shipped_on="2026-01-01")
    by_verdict = {r["verdict"]: r["age_days"] for r in rows}
    # No tags are readable from a nonexistent root, so the first two are
    # unknowable; what matters is that only `open` ever carries a number.
    assert all(v == 0 for k, v in by_verdict.items()
               if k != publication.OPEN)


def test_an_unreadable_release_date_yields_no_age_rather_than_a_guess() -> None:
    assert publication._age_days("") == 0
    assert publication._age_days("not-a-date") == 0
    assert publication._age_days("2026-01-01") > 0


# ----- the three tests_verified shapes (TASK-0450) --------------------------


def test_an_entry_resolving_to_no_note_is_said_rather_than_linked(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    (docs / "releases").mkdir(parents=True)
    (docs / "releases" / "REL-0001-v1.0.0.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "v1"\n'
        'status: released\nversion: "1.0.0"\n'
        'tests_verified: ["[[TST-9999-Nope]]"]\n---\n\n# v1\n',
        encoding="utf-8")
    index = Index.build(docs)
    row = publication.release_payload(
        tmp_path, index, "REL-0001")["tests_verified"][0]
    assert row["resolved"] is False
    assert "grade" not in row


def test_a_note_with_no_checkboxes_grades_as_no_checks() -> None:
    grade = publication._grade(_Rec("Just prose, nothing to walk.\n"))
    assert grade["total"] == 0 and grade["walked"] == 0


def test_an_empty_tests_verified_is_a_stated_absence(tmp_path: Path) -> None:
    """Five of twelve release notes are in this state."""
    docs = tmp_path / "docs"
    (docs / "releases").mkdir(parents=True)
    (docs / "releases" / "REL-0001-v1.0.0.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "v1"\n'
        'status: released\nversion: "1.0.0"\n---\n\n# v1\n',
        encoding="utf-8")
    index = Index.build(docs)
    payload = publication.release_payload(tmp_path, index, "REL-0001")
    assert payload["tests_verified"] == []
    assert payload["status"] == "released"
