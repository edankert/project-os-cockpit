"""A release can be finished (FEAT-0116 / TASK-0469, TASK-0470, TASK-0471).

The view could begin a release and walk its gate; it could not finish one.
`HUMAN_TRANSITIONS` has no `release` key — measured, and the reason nothing
anywhere could take a release from `draft` to `released` ([[ISS-0181]] item 4).
The consequence was already on disk: `../your-trainer`'s REL-0013 was prepared
by the cockpit with `features: []`, so the moment its status flipped its page
would read *"What shipped — 0 feature(s)"*.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import note_writes, publication, sweep
from project_os_cockpit.index import Index
from project_os_cockpit.note_writes import WriteError

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"

FEATURE = """---
type: "[[feature]]"
id: FEAT-9001
aliases: ["FEAT-9001"]
title: "A shipped thing"
status: done
owner: user:edwin
created: 2026-08-01
updated: 2026-08-01
{impact}---

# A feature
"""

RELEASE = """---
type: "[[release]]"
id: REL-9001
aliases: ["REL-9001"]
title: "The first one"
status: draft
version: "1.2.0"
preparing: "2026-08-01"
tag: ""
date: ""
owner: user:edwin
created: 2026-08-01
updated: 2026-08-01
features: ["[[FEAT-9001]]"]
changes: []
tests_verified: []
previous_release: ""
related: []
tags: [release]
---

# The first one

## Scope

One feature.
"""


def _repo(tmp_path: Path, *, impact: str = "", suite: bool = False) -> Index:
    docs = tmp_path / "docs"
    (docs / "features" / "x").mkdir(parents=True)
    (docs / "releases").mkdir(parents=True)
    (docs / "features" / "x" / "FEAT-9001-A.md").write_text(
        FEATURE.format(impact=impact), encoding="utf-8")
    (docs / "releases" / "REL-9001-v1.2.0.md").write_text(
        RELEASE, encoding="utf-8")
    if suite:
        checks = docs / "tests" / "acceptance"
        checks.mkdir(parents=True)
        (checks / "CHK-0001-Unwalked.md").write_text(
            "---\n"
            'type: "[[check]]"\nid: CHK-0001\naliases: ["CHK-0001"]\n'
            'title: "Nobody has walked this"\nstatus: active\n'
            "owner: user:edwin\ncreated: 2026-08-01\nupdated: 2026-08-01\n"
            'tier: 1\narea: "The thing"\nsection: "1.1"\nordinal: 10\n'
            'mark: "todo"\nverdict_date: ""\nverdict_reason: ""\n'
            "invalidated_by: {}\nautomation: manual\ncovered_by: []\n"
            'covers: ["[[FEAT-9001]]"]\nburden: []\nevidence: []\n'
            'migrated_from: ""\nrelated: []\n---\n\n# Nobody has walked this\n\n'
            "Do the thing.\n", encoding="utf-8")
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'version: 1\nupdated: "2026-08-01T00:00Z"\n'
        'focus:\n  task: ""\n  issue: ""\ncounters:\n  CHK: 1\nitems: {}\n',
        encoding="utf-8")
    return Index.build(docs)


SWEPT = 'acceptance_impact: "none — nothing user-visible"\n'


# --------------------------------------------------------- the two refusals

def test_it_refuses_while_a_frozen_feature_has_not_been_considered(
    tmp_path: Path,
) -> None:
    """Edwin: *"whether all acceptance tests have been considered … when
    somebody presses that release start button or maybe even before this."*

    Before it, always — the sweep is continuous. **Mark released is where
    considered-ness is ENFORCED**, because it is the one moment that is both
    cheap and final: nothing has shipped yet, and after this nothing can be
    added to what did.
    """
    index = _repo(tmp_path)
    with pytest.raises(WriteError) as caught:
        note_writes.mark_released(index, "REL-9001")
    # Naming the subject is the point. "Something is not ready" is a refusal
    # nobody can act on.
    assert "FEAT-9001" in caught.value.message
    assert "acceptance_impact" in caught.value.message


def test_it_refuses_on_a_blocked_gate_without_recorded_exceptions(
    tmp_path: Path,
) -> None:
    """TESTING.md has always allowed shipping over an unwalked check —
    *"exceptions must be documented in the release note with justification"* —
    and nothing ever implemented either half. This is the first half; the
    documented exception is the escape it points at."""
    index = _repo(tmp_path, impact=SWEPT, suite=True)
    with pytest.raises(WriteError) as caught:
        note_writes.mark_released(index, "REL-9001")
    assert "Nobody has walked this" in caught.value.message
    assert "exception" in caught.value.message.lower()


def test_a_documented_exception_clears_the_gate_refusal(tmp_path: Path) -> None:
    """The escape is a sentence in the note, and a low bar on purpose.

    The judgement is the person's; this only asks whether they wrote it down. A
    stricter parser would refuse a legitimate exception phrased slightly
    differently — and a refusal nobody can satisfy gets worked around by
    editing the status by hand, which is worse than the state it protected.
    """
    index = _repo(tmp_path, impact=SWEPT, suite=True)
    path = index.by_id("REL-9001")
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n## Exceptions\n\n- **Release exception:** the rig is in a box.\n",
        encoding="utf-8")
    index = Index.build(index.docs_root)
    result = note_writes.mark_released(index, "REL-9001")
    assert result["status"] == "released"


def test_a_release_with_no_version_is_refused(tmp_path: Path) -> None:
    """The tag it would print names nothing."""
    index = _repo(tmp_path, impact=SWEPT)
    path = index.by_id("REL-9001")
    path.write_text(path.read_text(encoding="utf-8").replace(
        'version: "1.2.0"', 'version: ""'), encoding="utf-8")
    index = Index.build(index.docs_root)
    with pytest.raises(WriteError) as caught:
        note_writes.mark_released(index, "REL-9001")
    assert "no version" in caught.value.message


# ------------------------------------------------------------- the write

def test_it_writes_status_date_tag_and_freezes_the_list(tmp_path: Path) -> None:
    """REL-0013's *"What shipped — 0 feature(s)"* future, made unrepresentable.

    The list was always derived and never written down, so the moment a status
    flips there is nothing left to derive it from. Freezing it is the whole
    difference between a record and a computation that has expired.
    """
    index = _repo(tmp_path, impact=SWEPT)
    result = note_writes.mark_released(index, "REL-9001")
    assert result["status"] == "released" and result["tag"] == "v1.2.0"
    assert result["features"] == ["FEAT-9001"]
    text = index.by_id("REL-9001").read_text(encoding="utf-8")
    assert re.search(r'^status: "?released"?$', text, re.M)
    assert re.search(r'^tag: "v1\.2\.0"$', text, re.M)
    assert re.search(r'^date: "\d{4}-\d{2}-\d{2}"$', text, re.M)
    assert re.search(r'^features: \["\[\[FEAT-9001\]\]"\]$', text, re.M)


def test_an_empty_features_list_is_frozen_from_the_derived_set(
    tmp_path: Path,
) -> None:
    """**REL-0013's exact state**, which is on disk in `../your-trainer` today.

    It was prepared by the cockpit with `features: []` — the derived list was
    never written down — so the moment its status flips its page reads *"What
    shipped — 0 feature(s)"*. The version with `features:` already populated
    passes whether or not the freeze works, which is why that test could not
    catch a mutation removing it, and this one does.
    """
    index = _repo(tmp_path, impact=SWEPT)
    path = index.by_id("REL-9001")
    path.write_text(path.read_text(encoding="utf-8").replace(
        'features: ["[[FEAT-9001]]"]', "features: []"), encoding="utf-8")
    index = Index.build(index.docs_root)
    result = note_writes.mark_released(index, "REL-9001")
    assert result["features"] == ["FEAT-9001"], (
        "the derived list was not frozen — this release will report shipping "
        "nothing"
    )
    assert 'features: ["[[FEAT-9001]]"]' in path.read_text(encoding="utf-8")


def test_it_prints_the_git_commands_and_runs_neither(tmp_path: Path) -> None:
    """Publishing stays a person's act.

    A commit is local and reversible; once a forge has a tag, deleting it does
    not unpublish it. The commands come back as text.
    """
    index = _repo(tmp_path, impact=SWEPT)
    result = note_writes.mark_released(index, "REL-9001")
    assert any(c.startswith("git tag -a v1.2.0") for c in result["commands"])
    assert any(c == "git push origin v1.2.0" for c in result["commands"])
    # Nothing ran: the repo is not even a git repo, and the write succeeded.
    assert not (tmp_path / ".git").exists()


def test_a_released_release_cannot_be_released_again(tmp_path: Path) -> None:
    index = _repo(tmp_path, impact=SWEPT)
    note_writes.mark_released(index, "REL-9001")
    fresh = Index.build(index.docs_root)
    with pytest.raises(WriteError) as caught:
        note_writes.mark_released(fresh, "REL-9001")
    assert "already released" in caught.value.message


# --------------------------------------------------- name the version

def test_the_scaffold_is_template_shaped(tmp_path: Path) -> None:
    """FEAT-0110 reads a heading the tool's own writer never produced.

    `create_release` ignored `docs/__templates__/release.md` and wrote an
    inline literal with no Known-issues section and no Post-Release-Actions
    section — so the reader and the writer disagreed about the note's shape,
    and the reader was right.
    """
    docs = tmp_path / "docs"
    (docs / "releases").mkdir(parents=True)
    (docs / "__templates__").mkdir(parents=True)
    (docs / "__templates__" / "release.md").write_text(
        (REPO_ROOT / "docs" / "__templates__" / "release.md").read_text(
            encoding="utf-8"), encoding="utf-8")
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'version: 1\nupdated: "x"\nfocus:\n  task: ""\ncounters: {}\nitems: {}\n',
        encoding="utf-8")
    index = Index.build(docs)
    result = note_writes.create_release(
        index, docs, title="The next one", version="2.0.0",
        features=["FEAT-9001"], actor="user:edwin")
    text = (docs / result["rel"]).read_text(encoding="utf-8")
    assert "### Known Issues (shipping with)" in text
    assert "### Post-Release Actions" in text
    # …and named the way the corpus names them: `REL-0012-v2.1.6.md`, not
    # `REL-0013-V2-1-7.md`.
    assert result["rel"].endswith("-v2.0.0.md"), result["rel"]
    assert re.search(r'^version: "2\.0\.0"$', text, re.M)
    assert re.search(r'^status: "?draft"?$', text, re.M)


def test_the_control_names_the_version_rather_than_starting_a_process() -> None:
    """Edwin: *"not sure if the start button should even exist ever."*

    It survives — `preparing:` is what stops the gate obligation asking outside
    a release window — but it shrinks to one job. Under the continuous model
    the process has been running all along.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "go.textContent = 'Name the version';" in src
    assert "'Start ▸'" not in src


# ------------------------------------------- the page reports its record

def test_the_note_is_reachable_from_the_page_about_it() -> None:
    """The authored record was unreachable from the only view about it."""
    src = RENDERER.read_text(encoding="utf-8")
    body = src[src.index("function buildReleasePage("):]
    body = body[:body.index("\nfunction ")]
    assert "note · docs/${d.rel}" in body


def test_still_owed_carries_the_split_with_open_first(tmp_path: Path) -> None:
    """REL-0010's heading said 11; the truth is 1 open + 2 done + 8 unknowable.

    One number over three populations is a number nobody can act on — and the
    eight unknowable ones are why it stayed at 11: nothing outside the repo can
    tell whether a store listing was updated.
    """
    split = publication._owed_split([
        {"verdict": "open"}, {"verdict": "done"}, {"verdict": "done"},
        {"verdict": "unknowable"},
    ])
    assert split == {"open": 1, "done": 2, "unknowable": 1}
    src = RENDERER.read_text(encoding="utf-8")
    assert "${split.open} open" in src
    assert src.index("${split.open} open") < src.index("${split.done} done")


def test_a_prose_entry_renders_as_a_claim_not_a_broken_link(
    tmp_path: Path,
) -> None:
    """11 of the corpus's 15 `tests_verified` entries are recorded sentences.

    Every one rendered as *"not in this corpus"* — which reads as a defect in
    the record rather than as the record doing its job. Asserted on the PAYLOAD
    as well as the renderer: a guard on the client branch alone survived a
    mutation that made the flag always false, because the branch was still
    there and simply never taken.
    """
    index = _repo(tmp_path, impact=SWEPT)
    path = index.by_id("REL-9001")
    path.write_text(path.read_text(encoding="utf-8").replace(
        "tests_verified: []",
        'tests_verified: ["Unit tests: 614 tests, all passing", "TST-9999"]'),
        encoding="utf-8")
    index = Index.build(index.docs_root)
    data = publication.release_payload(tmp_path, index, "REL-9001")
    rows = {r["id"]: r for r in data["tests_verified"]}
    assert rows["Unit tests: 614 tests, all passing"]["claim"] is True
    # …and an id-shaped entry that resolves to nothing is still a broken link,
    # which is a different fact and must keep saying so.
    assert rows["TST-9999"]["claim"] is False

    src = RENDERER.read_text(encoding="utf-8")
    assert "v.claim ? v.id" in src


def test_confidence_is_a_check_property_rolled_up(tmp_path: Path) -> None:
    """Edwin asked *"is this a feature stat"* — it is not.

    It is `automation:` on the checks touching what shipped, summed. Authoring
    it on the feature would be the same fact written twice, and the two copies
    would disagree the first time a check changed.
    """
    index = _repo(tmp_path, impact=SWEPT, suite=True)
    conf = publication._confidence(index, [{"id": "FEAT-9001"}])
    assert conf == {"total": 1, "full": 0, "partial": 0, "manual": 1,
                    "scoped": True}
    # A release naming nothing reports honestly rather than inventing a scope.
    assert publication._confidence(index, [])["scoped"] is False


# ------------------------------------------------------- one view per item

def test_a_feature_row_inside_a_release_opens_the_item_view() -> None:
    """Edwin: *"you would like to have one view per item."*

    The thing selected and the thing received were mismatched — a row inside a
    release opened the plain note with no release context at all.
    """
    from project_os_cockpit import cockpit

    index = Index.build(REPO_ROOT / "docs")
    urls = []
    for group in cockpit.nav_payload(index, mode="publication")["groups"]:
        for sub in group.get("subgroups") or []:
            for row in sub.get("items") or []:
                if row.get("type") in ("feature", "issue") and row.get("id"):
                    urls.append(row["url"])
    assert urls, "no feature or issue rows inside any release group"
    for url in urls:
        assert re.match(r"^~release/[\w-]+/(FEAT|ISS)-\d+$", url), url


def test_the_item_page_answers_with_release_context(tmp_path: Path) -> None:
    index = _repo(tmp_path, impact=SWEPT, suite=True)
    data = publication.release_item_payload(index, "REL-9001", "FEAT-9001")
    assert data["exists"] and data["release"] == "REL-9001"
    assert data["release_version"] == "1.2.0"
    assert [r["id"] for r in data["originated"]] == ["CHK-0001"]
    assert data["impact_state"] == "none"


def test_a_feature_with_no_checks_reads_as_considered_or_owed() -> None:
    """The empty state is the point, not a failure.

    *"Acceptance impact considered — none"* and *"not yet swept"* are opposite
    sentences, and until this phase the surface could only render both as an
    empty list.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = src[src.index("function buildReleaseItemPage("):]
    body = body[:body.index("\n// ") if "\n// " in body else len(body)]
    assert "Acceptance impact not yet swept." in body
    assert "Acceptance impact — ${d.acceptance_impact}" in body
    # …and the bare note is one row away, never the destination.
    assert "note · docs/${d.rel}" in body


def test_marking_a_check_from_the_item_page_uses_the_one_control() -> None:
    """A third mark control would be a third vocabulary for one record."""
    src = RENDERER.read_text(encoding="utf-8")
    body = src[src.index("function buildReleaseItemPage("):]
    body = body[:body.index("\nfunction buildReleasePage(")]
    assert "buildCheckRow(item)" in body


def test_the_sweep_page_writes_nothing_until_save() -> None:
    """Cancelling is closing the page — there is no draft state to clean up."""
    src = RENDERER.read_text(encoding="utf-8")
    body = src[src.index("function buildSweepPage("):]
    body = body[:body.index("\n// ") if "\n// " in body else len(body)]
    assert body.count("postJson(") == 1
    assert "'/api/notes/acceptance-sweep'" in body
