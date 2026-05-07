"""Unit tests for :mod:`project_os_cockpit.cockpit`.

Validates the cockpit v2 schema against the shared fixture:
- ``nav_payload`` returns a generalised ``{schema_version, mode, groups}``
  envelope across four modes (features / tasks / issues / recent).
- ``context_payload`` returns outbound + inbound-only sets for an active
  note, grouped by type, with ``id``/``title``/``status``/``priority``.
- Unknown / missing ``this`` returns an empty payload (no exception).
- Templates are excluded from both endpoints' lists.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from project_os_cockpit.cockpit import SCHEMA_VERSION, context_payload, nav_payload
from project_os_cockpit.index import Index


FIXTURE = Path(__file__).parent / "fixtures" / "index_basic"


@pytest.fixture()
def docs_root(tmp_path: Path) -> Path:
    target = tmp_path / "docs"
    shutil.copytree(FIXTURE, target)
    return target


@pytest.fixture()
def index(docs_root: Path) -> Index:
    return Index.build(docs_root)


# ---- nav payload (mode = features, default) ----------------------------


def test_nav_payload_schema_versioned(index: Index) -> None:
    payload = nav_payload(index)
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["mode"] == "features"
    assert "groups" in payload


def test_nav_payload_unknown_mode_falls_back_to_features(index: Index) -> None:
    payload = nav_payload(index, mode="bogus")
    assert payload["mode"] == "features"


def test_nav_payload_features_groups_by_phase(index: Index) -> None:
    payload = nav_payload(index, mode="features")
    assert len(payload["groups"]) == 1  # all features share the same phase
    g = payload["groups"][0]
    assert g["key"] == "PHASE-001"
    assert g["label"] == "PHASE-001 · Foundation"
    assert g["url"] == "/docs/PHASE-001-Foundation.md"
    assert g["status"] == "active"
    item_ids = {item["id"] for item in g["items"]}
    assert item_ids == {"FEAT-0001", "FEAT-0002"}


def test_nav_payload_features_item_shape(index: Index) -> None:
    payload = nav_payload(index, mode="features")
    feat1 = next(
        i for g in payload["groups"]
        for i in g["items"] if i["id"] == "FEAT-0001"
    )
    assert feat1["title"] == "Alpha feature"
    assert feat1["status"] == "active"
    assert feat1["subtitle"] == "Demonstrate the alpha"
    assert feat1["url"] == "/docs/FEAT-0001-Alpha.md"


def test_nav_payload_features_excludes_template_features(index: Index) -> None:
    payload = nav_payload(index, mode="features")
    item_ids = {i["id"] for g in payload["groups"] for i in g["items"]}
    assert "FEAT-0000" not in item_ids


# ---- nav payload (mode = tasks) ----------------------------------------


def test_nav_payload_tasks_groups_by_status(index: Index) -> None:
    payload = nav_payload(index, mode="tasks")
    assert payload["mode"] == "tasks"
    keys = [g["key"] for g in payload["groups"]]
    # Doing comes before Backlog per TASK_STATUS_ORDER.
    assert keys.index("doing") < keys.index("backlog")
    doing = next(g for g in payload["groups"] if g["key"] == "doing")
    assert doing["status"] == "doing"
    assert doing["label"] == "Doing"
    item_ids = {i["id"] for i in doing["items"]}
    assert "TASK-0001" in item_ids


def test_nav_payload_tasks_item_subtitle_carries_parent(index: Index) -> None:
    payload = nav_payload(index, mode="tasks")
    t1 = next(
        i for g in payload["groups"]
        for i in g["items"] if i["id"] == "TASK-0001"
    )
    # Parent feature + effort, joined by " · ".
    assert "FEAT-0001" in t1["subtitle"]
    assert "M" in t1["subtitle"]


# ---- nav payload (mode = issues) ---------------------------------------


def test_nav_payload_issues_groups_by_severity(index: Index) -> None:
    payload = nav_payload(index, mode="issues")
    assert payload["mode"] == "issues"
    keys = [g["key"] for g in payload["groups"]]
    # high before low per SEVERITY_ORDER.
    assert keys.index("high") < keys.index("low")
    high = next(g for g in payload["groups"] if g["key"] == "high")
    assert high["label"] == "High"
    assert {i["id"] for i in high["items"]} == {"ISS-0001"}


def test_nav_payload_issues_item_subtitle_has_affects_and_component(
    index: Index,
) -> None:
    payload = nav_payload(index, mode="issues")
    iss1 = next(
        i for g in payload["groups"]
        for i in g["items"] if i["id"] == "ISS-0001"
    )
    assert "FEAT-0001" in iss1["subtitle"]
    assert "alpha" in iss1["subtitle"]


# ---- nav payload (mode = recent) ---------------------------------------


def test_nav_payload_recent_returns_items_in_buckets(index: Index) -> None:
    payload = nav_payload(index, mode="recent")
    assert payload["mode"] == "recent"
    # At least one bucket should exist (fixture notes have updated dates).
    assert payload["groups"], "recent mode should surface at least one group"
    bucket_keys = {g["key"] for g in payload["groups"]}
    assert bucket_keys.issubset({"today", "yesterday", "week", "month", "earlier"})
    # Items carry a subtitle of "<type> · <iso-date>" — at least the type.
    sample = payload["groups"][0]["items"][0]
    assert sample["subtitle"], "recent items must have a subtitle"


def test_nav_payload_recent_excludes_templates(index: Index) -> None:
    payload = nav_payload(index, mode="recent")
    ids = {i["id"] for g in payload["groups"] for i in g["items"]}
    # __templates__/feature.md has id FEAT-0000 — must not surface.
    assert "FEAT-0000" not in ids


# ---- platform filter ---------------------------------------------------


def test_nav_payload_surfaces_available_platforms(index: Index) -> None:
    """Server lists distinct non-empty platform values it found in the corpus.

    Fixture has TASK-0001 (ios), TASK-0002 (android), ISS-0001 (ios).
    """
    payload = nav_payload(index)
    assert payload["available_platforms"] == ["android", "ios"]
    assert payload["platform"] == "all"


def test_nav_payload_platform_ios_filters_tasks(index: Index) -> None:
    """Picking iOS keeps iOS + shared + platform-agnostic items, drops Android."""
    payload = nav_payload(index, mode="tasks", platform="ios")
    assert payload["platform"] == "ios"
    ids = {i["id"] for g in payload["groups"] for i in g["items"]}
    assert "TASK-0001" in ids       # platform: ios
    assert "TASK-0002" not in ids   # platform: android — dropped


def test_nav_payload_platform_unknown_falls_back_to_all(index: Index) -> None:
    """Picking a platform that isn't in the corpus drops every platform-tagged item.

    Items with empty/missing platform (cross-platform) still pass through.
    """
    payload = nav_payload(index, mode="tasks", platform="web")
    ids = {i["id"] for g in payload["groups"] for i in g["items"]}
    assert "TASK-0001" not in ids
    assert "TASK-0002" not in ids


def test_context_payload_platform_filters_relationships(index: Index) -> None:
    """Right-pane filtering uses the same predicate as the left pane."""
    payload = context_payload(index, "FEAT-0001", platform="ios")
    # FEAT-0001 has no platform set → still resolved as active.
    assert payload["active"] is not None
    assert payload["platform"] == "ios"
    # Inbound-only TASK-0001 is iOS → kept; android items would be dropped.
    backlink_ids = {i["id"] for g in payload["backlinks"] for i in g["items"]}
    assert "TASK-0001" in backlink_ids


def test_context_payload_platform_drops_other_platform(index: Index) -> None:
    payload = context_payload(index, "FEAT-0002", platform="ios")
    # TASK-0002 (android) targets FEAT-0002 — should NOT appear under iOS.
    backlink_ids = {i["id"] for g in payload["backlinks"] for i in g["items"]}
    assert "TASK-0002" not in backlink_ids


# ---- nav payload (mode = library) --------------------------------------


def test_nav_payload_library_top_level_handles_group(index: Index) -> None:
    """Top-level non-ID *.md files appear in the 'handles' group with filename
    as title and the compact layout flag."""
    payload = nav_payload(index, mode="library")
    assert payload["mode"] == "library"
    handles = next((g for g in payload["groups"] if g["key"] == "handles"), None)
    assert handles is not None, "fixture has README.md, expected handles group"
    assert handles["item_layout"] == "compact"
    titles = {i["title"] for i in handles["items"]}
    assert "README.md" in titles
    # Subdir handles are NOT in this group — they get their own group below.
    assert "ACCEPTANCE_TESTS.md" not in titles
    sample = next(i for i in handles["items"] if i["title"] == "README.md")
    assert sample["id"] == ""
    assert sample["status"] is None
    assert sample["subtitle"] == ""


def test_nav_payload_library_subdir_handles_nest_under_handles_parent(
    index: Index,
) -> None:
    """Subdir handle groups are nested as ``subgroups`` inside the parent
    "Project handles" group — NOT siblings of the rare-types groups.

    This way the user sees subdirs as children of the project-handles
    section both visually (indented) and structurally (collapse the
    parent → subdirs collapse with it).
    """
    payload = nav_payload(index, mode="library")
    # Subdirs should NOT be top-level groups any more.
    top_level_keys = [g["key"] for g in payload["groups"]]
    assert not any(k.startswith("handles-dir:") for k in top_level_keys)
    # They should live under the handles parent's `subgroups`.
    handles = next(g for g in payload["groups"] if g["key"] == "handles")
    sub_keys = [sg["key"] for sg in handles.get("subgroups", [])]
    assert "handles-dir:tests" in sub_keys
    tests_sub = next(sg for sg in handles["subgroups"] if sg["key"] == "handles-dir:tests")
    assert tests_sub["label"] == "tests/"
    assert tests_sub["item_layout"] == "compact"
    assert "ACCEPTANCE_TESTS.md" in [i["title"] for i in tests_sub["items"]]


def test_nav_payload_library_rare_types_drop_subtitle(index: Index) -> None:
    """Rare-types items use the stacked layout and carry no type label."""
    # Add an ADR fixture-style note via direct frontmatter inspection: the
    # base fixture doesn't include one, so this test just guards the schema.
    payload = nav_payload(index, mode="library")
    rare_groups = [g for g in payload["groups"] if g["key"].startswith("rare:")]
    for g in rare_groups:
        assert g["item_layout"] == "stacked"
        for item in g["items"]:
            assert item["subtitle"] == "", (
                "rare-type items must drop the type label — group header carries it"
            )


def test_nav_payload_library_excludes_id_prefixed_files_from_handles(
    index: Index,
) -> None:
    """FEAT-0001-Alpha.md is ID-prefixed → must NOT appear in handles."""
    payload = nav_payload(index, mode="library")
    handles = next((g for g in payload["groups"] if g["key"] == "handles"), None)
    assert handles is not None
    ids = {i["id"] for i in handles["items"]}
    assert "FEAT-0001" not in ids
    assert "TASK-0001" not in ids
    assert "REQ-0001" not in ids


def test_nav_payload_library_pinned_section_resolves_paths(
    index: Index, docs_root: Path
) -> None:
    """A pinned path that resolves to a real note appears in the Pinned group."""
    payload = nav_payload(
        index, mode="library", pinned=["FEAT-0001-Alpha.md"]
    )
    pinned_groups = [g for g in payload["groups"] if g["key"] == "pinned"]
    assert pinned_groups, "Pinned group should be present when pinned items resolve"
    items = pinned_groups[0]["items"]
    assert any(i["id"] == "FEAT-0001" for i in items)


def test_nav_payload_library_pinned_drops_stale_paths(index: Index) -> None:
    """A pinned path that no longer resolves is silently dropped."""
    payload = nav_payload(
        index, mode="library", pinned=["does/not/exist.md", "FEAT-0001-Alpha.md"]
    )
    pinned_groups = [g for g in payload["groups"] if g["key"] == "pinned"]
    assert pinned_groups
    assert len(pinned_groups[0]["items"]) == 1   # only the resolvable one


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
