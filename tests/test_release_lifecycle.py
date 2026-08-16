"""The release accumulates, then asks (TST-0032 / FEAT-0105).

```
open        accumulating — gate silent
  ↓         a person says "I intend to ship this"
preparing   the gate asks
  ↓
released    shipped — the next one opens
```

The middle state is the whole design. If a release is always open and the gate
asked whenever one existed, the gate would ask **forever** — the self-re-arming
badge ADR-0027 excludes staleness for, and the failure PHASE-034 exists to
avoid producing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import cockpit, note_writes, obligations, publication
from project_os_cockpit.index import Index

SUITE = (
    "# Tier 1 — Feature Tests\n\n## 1.1 Area (FEAT-0001)\n"
    "- [ ] **A:** do it.\n"
)


def _docs(tmp_path: Path) -> Path:
    d = tmp_path / "docs"
    (d / "tests").mkdir(parents=True)
    (d / "tests" / "ACCEPTANCE_TESTS.md").write_text(SUITE, encoding="utf-8")
    return d


def _rel(docs: Path, rid: str, status: str, version: str,
         preparing: str = "") -> None:
    d = docs / "releases"
    d.mkdir(parents=True, exist_ok=True)
    body = (
        f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
        f'status: {status}\nversion: "{version}"\n'
    )
    if preparing:
        body += f'preparing: "{preparing}"\n'
    (d / f"{rid}-R.md").write_text(body + "---\n", encoding="utf-8")


def _gate_obligations(docs: Path) -> list[dict]:
    rows = obligations.owed_items(Index.build(docs))["publication"]
    return [r for r in rows if r["type"] == obligations.GATE_OBLIGATION_KIND]


# ---- the three states ----------------------------------------------------


def test_an_open_release_asks_nothing(tmp_path: Path) -> None:
    """A draft with no `preparing:` is accumulating. The suite has an
    unchecked gating check and the gate stays silent."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    _rel(docs, "REL-0002", "draft", "1.1.0")
    index = Index.build(docs)
    assert [r["id"] for r in publication.open_releases(index)] == ["REL-0002"]
    assert publication.preparing(index) is None
    assert _gate_obligations(docs) == []


def test_preparing_is_what_makes_the_gate_ask(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "draft", "1.1.0", preparing="2026-08-16")
    assert publication.preparing(Index.build(docs))["id"] == "REL-0001"
    assert len(_gate_obligations(docs)) == 1


def test_a_released_release_leaves_nothing_open(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    index = Index.build(docs)
    assert publication.open_releases(index) == []
    assert publication.preparing(index) is None


def test_a_draft_a_shipped_version_overtook_is_neither(tmp_path: Path) -> None:
    """It is stale, not open and not preparing — even with the flag set."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0008", "draft", "2.0.2", preparing="2026-08-16")
    _rel(docs, "REL-0012", "released", "2.1.6")
    index = Index.build(docs)
    assert publication.open_releases(index) == []
    assert publication.preparing(index) is None
    assert [d["id"] for d in publication.stale_drafts(index)] == ["REL-0008"]


# ---- the derived next release --------------------------------------------


def test_the_next_release_is_shown_without_a_note(tmp_path: Path) -> None:
    """Edwin wanted *"there is always a release"*. It is DERIVED — no note is
    auto-written, because `unreleased_payload` already computes the set and a
    note appearing unasked is what CLAUDE.md warns against."""
    docs = _docs(tmp_path)
    (docs / "features" / "f").mkdir(parents=True)
    (docs / "features" / "f" / "FEAT-0001-F.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "F"\n'
        "status: done\n---\n", encoding="utf-8",
    )
    groups = {
        g["key"]: g for g in cockpit.nav_payload(
            Index.build(docs), "publication", project_root=docs.parent,
        )["groups"]
    }
    nxt = groups["release-next"]
    assert nxt["label"].startswith("Next release")
    # FEAT-0107: the GROUP navigates to the page. The row-level Prepare verb
    # is gone with the rungs — a release is opened from its own page, which is
    # where every other view in this app puts the acting.
    assert nxt["url"] == "~release/next"
    assert not list((docs / "releases").glob("*.md")) if (
        docs / "releases").is_dir() else True


def test_declaring_sets_the_flag_and_the_version(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    result = note_writes.create_release(
        Index.build(docs), docs, title="v1.1.0", version="1.1.0",
    )
    fresh = Index.build(docs)
    prep = publication.preparing(fresh)
    assert prep is not None and prep["id"] == result["id"]
    assert prep["preparing"] is True


def test_a_second_open_release_is_refused(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "draft", "1.1.0")
    with pytest.raises(note_writes.WriteError) as err:
        note_writes.create_release(
            Index.build(docs), docs, title="v1.2.0", version="1.2.0",
        )
    assert "already open" in str(err.value)
