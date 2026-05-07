"""Unit tests for :mod:`docs_server.cockpit`.

Validates TASK-0012's DoD against the same fixture used by test_index.py:
- ``nav_payload`` groups every non-template feature by phase, carries the
  required columns + phase metadata.
- ``context_payload`` returns outbound + inbound-only sets for an active
  note, grouped by type, with ``id``/``title``/``status``/``priority``.
- Unknown / missing ``this`` returns an empty payload (no exception).
- Templates are excluded from both endpoints' lists.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from docs_server.cockpit import SCHEMA_VERSION, context_payload, nav_payload
from docs_server.index import Index


FIXTURE = Path(__file__).parent / "fixtures" / "index_basic"


@pytest.fixture()
def docs_root(tmp_path: Path) -> Path:
    target = tmp_path / "docs"
    shutil.copytree(FIXTURE, target)
    return target


@pytest.fixture()
def index(docs_root: Path) -> Index:
    return Index.build(docs_root)


# ---- nav payload -------------------------------------------------------


def test_nav_payload_schema_versioned(index: Index) -> None:
    payload = nav_payload(index)
    assert payload["schema_version"] == SCHEMA_VERSION
    assert "groups" in payload


def test_nav_payload_groups_features_by_phase(index: Index) -> None:
    payload = nav_payload(index)
    assert len(payload["groups"]) == 1  # all features share the same phase
    g = payload["groups"][0]
    assert g["phase_id"] == "PHASE-001"
    assert g["phase_title"] == "Foundation"
    assert g["phase_url"] == "/docs/PHASE-001-Foundation.md"
    item_ids = {item["id"] for item in g["items"]}
    assert item_ids == {"FEAT-0001", "FEAT-0002"}


def test_nav_payload_item_shape(index: Index) -> None:
    payload = nav_payload(index)
    feat1 = next(
        i for g in payload["groups"]
        for i in g["items"] if i["id"] == "FEAT-0001"
    )
    assert feat1["title"] == "Alpha feature"
    assert feat1["status"] == "active"
    assert feat1["goal"] == "Demonstrate the alpha"
    assert feat1["url"] == "/docs/FEAT-0001-Alpha.md"


def test_nav_payload_excludes_template_features(index: Index) -> None:
    payload = nav_payload(index)
    item_ids = {i["id"] for g in payload["groups"] for i in g["items"]}
    assert "FEAT-0000" not in item_ids


# ---- context payload ---------------------------------------------------


def test_context_payload_unknown_note_is_empty(index: Index) -> None:
    payload = context_payload(index, "DoesNotExist")
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["active"] is None
    assert payload["linked"] == []
    assert payload["backlinks"] == []


def test_context_payload_missing_this_is_empty(index: Index) -> None:
    payload = context_payload(index, None)
    assert payload["active"] is None
    assert payload["linked"] == []
    assert payload["backlinks"] == []


def test_context_payload_resolves_by_id(index: Index) -> None:
    payload = context_payload(index, "FEAT-0001")
    assert payload["active"] is not None
    assert payload["active"]["id"] == "FEAT-0001"
    assert payload["active"]["url"] == "/docs/FEAT-0001-Alpha.md"


def test_context_payload_linked_grouped_by_type(index: Index) -> None:
    """FEAT-0001's outbound includes FEAT-0002 (feature) + REQ-0001 (requirement)
    + the feature template (excluded from cockpit listings)."""
    payload = context_payload(index, "FEAT-0001")
    types = {g["type"] for g in payload["linked"]}
    assert "feature" in types  # FEAT-0002
    assert "requirement" in types  # REQ-0001


def test_context_payload_excludes_templates_from_linked(index: Index) -> None:
    payload = context_payload(index, "FEAT-0001")
    ids = {i["id"] for g in payload["linked"] for i in g["items"]}
    # FEAT-0000 is the placeholder in the template; should NOT appear.
    assert "FEAT-0000" not in ids


def test_context_payload_backlinks_excludes_already_linked(
    index: Index,
) -> None:
    """The 'backlinks' (inbound-only) set never contains a note already in 'linked'.

    FEAT-0001 ↔ FEAT-0002 link bidirectionally — FEAT-0002 should appear
    in `linked`, NOT in `backlinks` (it's already in outbound).
    """
    payload = context_payload(index, "FEAT-0001")
    linked_ids = {i["id"] for g in payload["linked"] for i in g["items"]}
    backlink_ids = {i["id"] for g in payload["backlinks"] for i in g["items"]}
    assert "FEAT-0002" in linked_ids
    assert "FEAT-0002" not in backlink_ids
    assert linked_ids.isdisjoint(backlink_ids)


def test_context_payload_inbound_only_change_appears(index: Index) -> None:
    """CHG-20260508-Inbound only references FEAT-0001 (not the other way around).

    It MUST appear in `backlinks`, NOT in `linked`.
    """
    payload = context_payload(index, "FEAT-0001")
    linked_ids = {i["id"] for g in payload["linked"] for i in g["items"]}
    backlink_ids = {i["id"] for g in payload["backlinks"] for i in g["items"]}
    assert "CHG-20260508-Inbound" not in linked_ids
    assert "CHG-20260508-Inbound" in backlink_ids


def test_context_payload_item_columns(index: Index) -> None:
    payload = context_payload(index, "FEAT-0001")
    # REQ-0001 should be in linked (FEAT-0001 body links to it).
    req = next(
        i for g in payload["linked"]
        for i in g["items"] if i["id"] == "REQ-0001"
    )
    assert req["title"] == "Some requirement"
    assert req["status"] == "approved"
    # priority is unset in the fixture's REQ-0001 — should be None, not "".
    assert req["priority"] is None
    assert req["url"] == "/docs/REQ-0001-Some-Req.md"


def test_context_payload_resolves_by_path(index: Index, docs_root: Path) -> None:
    """The JS client may pass a docs-root-relative path or a /docs/-prefixed URL."""
    payload = context_payload(index, "FEAT-0001-Alpha.md")
    assert payload["active"] is not None
    assert payload["active"]["id"] == "FEAT-0001"

    payload = context_payload(index, "/docs/FEAT-0001-Alpha.md")
    assert payload["active"] is not None
    assert payload["active"]["id"] == "FEAT-0001"
