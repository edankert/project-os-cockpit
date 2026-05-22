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
    item_ids = {
        i["id"]
        for g in payload["groups"]
        for i in g["items"]
        if g["key"] != "unattached-reqs"
    }
    assert "FEAT-0000" not in item_ids


def test_nav_payload_features_attaches_requirements_as_children(
    index: Index,
) -> None:
    """Each feature carries its requirements as `children` for the
    nested-collapsed render under the feature card (TASK-0030).

    Fixture: REQ-0001 has `specifies: ["[[FEAT-0001]]"]`, so it should
    surface under FEAT-0001's children.
    """
    payload = nav_payload(index, mode="features")
    feat1 = next(
        i for g in payload["groups"]
        for i in g["items"] if i["id"] == "FEAT-0001"
    )
    assert "children" in feat1, "FEAT-0001 should carry its requirements as children"
    child_ids = {c["id"] for c in feat1["children"]}
    assert "REQ-0001" in child_ids
    sample = next(c for c in feat1["children"] if c["id"] == "REQ-0001")
    assert sample["type"] == "requirement"
    assert sample["status"]  # populated from frontmatter


def test_nav_payload_features_orphan_requirements_group(
    index: Index, docs_root: Path
) -> None:
    """Requirements with no resolvable feature link surface in a final
    "Unattached requirements" group at the bottom of Features mode."""
    # Synthesise a requirement that doesn't link to any feature.
    (docs_root / "REQ-0099-Orphan.md").write_text(
        '---\ntype: "[[requirement]]"\nid: REQ-0099\ntitle: "Orphan req"\n'
        'status: approved\n---\n# Orphan\n',
        encoding="utf-8",
    )
    fresh = Index.build(docs_root)
    payload = nav_payload(fresh, mode="features")
    orphans = next(
        (g for g in payload["groups"] if g["key"] == "unattached-reqs"), None
    )
    assert orphans is not None, "orphan group should appear when any req has no specifies/scope"
    ids = {i["id"] for i in orphans["items"]}
    assert "REQ-0099" in ids
    assert "REQ-0001" not in ids  # REQ-0001 specifies FEAT-0001, not an orphan


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


def test_nav_payload_tasks_item_subtitle_is_body_description(
    index: Index,
) -> None:
    """Tasks subtitle is the first paragraph of body text, with wikilinks
    stripped (TASK-0029). The fixture's TASK-0001 body says
    "Implements [[FEAT-0001]]." — wikilinks resolve to "FEAT-0001"."""
    payload = nav_payload(index, mode="tasks")
    t1 = next(
        i for g in payload["groups"]
        for i in g["items"] if i["id"] == "TASK-0001"
    )
    assert t1["subtitle"]
    assert "FEAT-0001" in t1["subtitle"]
    assert "[[" not in t1["subtitle"]  # wikilink markup stripped


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


def test_nav_payload_issues_item_subtitle_is_body_description(
    index: Index,
) -> None:
    """Issues subtitle is the first paragraph of body text (TASK-0029).
    The fixture's ISS-0001 body has only an H1, so the subtitle is empty
    — the contract is "non-trivial body text or empty"."""
    payload = nav_payload(index, mode="issues")
    iss1 = next(
        i for g in payload["groups"]
        for i in g["items"] if i["id"] == "ISS-0001"
    )
    assert iss1["subtitle"] == ""


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


def test_nav_payload_library_no_legacy_handles_or_support_groups(
    index: Index,
) -> None:
    """The legacy ``handles`` and ``project-support`` groups are gone.

    Top-level project files are merged into the ``docs-tree`` group root
    (TASK-0021); subdir-handle groups are no longer surfaced as siblings.
    """
    payload = nav_payload(index, mode="library")
    keys = [g["key"] for g in payload["groups"]]
    assert "handles" not in keys
    assert "project-support" not in keys
    assert not any(k.startswith("handles-dir:") for k in keys)


def test_nav_payload_library_docs_tree_merges_project_root_files(
    index: Index, tmp_path: Path
) -> None:
    """README.md / ROADMAP.md / SECURITY.md at the project root render as
    files at the root of the ``docs-tree`` group — not as a separate
    "Top-level docs" group (TASK-0021)."""
    project_root = tmp_path / "fake-project"
    project_root.mkdir()
    (project_root / "README.md").write_text("# stub\n", encoding="utf-8")
    (project_root / "ROADMAP.md").write_text("# stub\n", encoding="utf-8")

    payload = nav_payload(index, mode="library", project_root=project_root)
    docs_tree = next((g for g in payload["groups"] if g["key"] == "docs-tree"), None)
    assert docs_tree is not None, (
        "Docs tree should appear when project_root has at least one allowed root file"
    )
    assert docs_tree["item_layout"] == "compact"
    titles = [i["title"] for i in docs_tree["items"]]
    assert "README.md" in titles
    assert "ROADMAP.md" in titles
    # SECURITY.md was not created → must not surface even though it's allowed.
    assert "SECURITY.md" not in titles
    # README.md sorts to the top of the items list.
    assert titles[0] == "README.md"


def test_nav_payload_library_includes_changes_group(index: Index) -> None:
    """The Project section surfaces a Changes group as a rare-type
    (TASK-0038). Items use the standard id+title shape."""
    payload = nav_payload(index, mode="library")
    changes = next((g for g in payload["groups"] if g["key"] == "rare:change"), None)
    assert changes is not None, "fixture has at least one change note"
    assert changes["label"] == "Changes"
    assert changes["item_layout"] == "stacked"
    for item in changes["items"]:
        assert item["id"].startswith("CHG-")
        assert item["type"] == "change"


def test_nav_payload_library_no_rare_reference_group(index: Index) -> None:
    """Reference-typed notes no longer have their own rare-type group
    (TASK-0036) — they're inlined into the Docs tree."""
    payload = nav_payload(index, mode="library")
    keys = [g["key"] for g in payload["groups"]]
    assert "rare:reference" not in keys


def test_nav_payload_library_docs_tree_includes_root_references(
    index: Index,
) -> None:
    """Reference-typed notes at the docs root show in the Docs tree with
    ``type: "reference"`` so the JS picks the book-open icon (TASK-0036).
    Filename is the title; no status, no id."""
    payload = nav_payload(index, mode="library")
    docs_tree = next((g for g in payload["groups"] if g["key"] == "docs-tree"), None)
    assert docs_tree is not None
    titles_root = {i["title"] for i in docs_tree["items"]}
    assert "README.md" in titles_root
    readme = next(i for i in docs_tree["items"] if i["title"] == "README.md")
    assert readme["type"] == "reference"
    assert readme["id"] == ""
    assert readme["status"] is None
    assert readme["subtitle"] == ""


def test_nav_payload_library_docs_tree_excludes_canonical_container_dirs(
    index: Index,
) -> None:
    """All canonical project-os container dirs (changes/, decisions/,
    tests/, ...) are hidden from the Docs tree, even for inline-type
    notes living inside them (TASK-0037). __templates__/ also stays
    excluded by the prefix filter."""
    payload = nav_payload(index, mode="library")
    docs_tree = next((g for g in payload["groups"] if g["key"] == "docs-tree"), None)
    assert docs_tree is not None
    subgroup_labels = {sg["label"] for sg in docs_tree.get("subgroups", [])}
    for canonical in (
        "changes/", "decisions/", "features/", "issues/", "phases/",
        "plans/", "releases/", "requirements/", "risks/", "tasks/",
        "tests/", "workflows/", "__templates__/",
    ):
        assert canonical not in subgroup_labels, (
            f"{canonical} should not appear as a Docs tree subgroup"
        )


def test_nav_payload_library_typed_rare_keeps_id_and_title(
    index: Index, tmp_path: Path
) -> None:
    """Typed-structured rare-type groups (decisions/releases/risks/tests/
    workflows/plans) keep the original ``id + human title`` shape — these
    notes have meaningful frontmatter titles and IDs (TASK-0025)."""
    # Synthesise an ADR fixture so the assertion has something to bind to.
    adr_dir = docs_root_for(index) / "decisions"
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / "ADR-0099-Sample.md").write_text(
        '---\ntype: "[[adr]]"\nid: ADR-0099\ntitle: "Sample ADR"\nstatus: accepted\n---\n# Sample\n',
        encoding="utf-8",
    )
    fresh = Index.build(docs_root_for(index))
    payload = nav_payload(fresh, mode="library")
    adrs = next((g for g in payload["groups"] if g["key"] == "rare:adr"), None)
    assert adrs is not None, "synthetic ADR should produce the rare:adr group"
    for item in adrs["items"]:
        # Id is a project-os ID, NOT a filename.
        assert item["id"].startswith("ADR-")
        assert not item["id"].endswith(".md")
        # Title is the frontmatter human title.
        assert not item["title"].endswith(".md"), (
            f"typed-rare title should be the human title, got {item['title']!r}"
        )
        assert item["subtitle"] == ""
        assert item["type"] == "adr"


def docs_root_for(index: Index) -> Path:
    return index.docs_root


def test_nav_payload_items_carry_type_for_icons(index: Index) -> None:
    """Every item across modes carries a ``type`` field so the JS can
    render a per-type icon (TASK-0023). Untyped tree items may use ``""``."""
    for mode in ("features", "tasks", "issues", "recent", "library"):
        payload = nav_payload(index, mode=mode)
        for g in payload["groups"]:
            for item in g["items"]:
                assert "type" in item, f"mode={mode} item missing 'type': {item}"


def test_context_payload_items_carry_type_for_icons(index: Index) -> None:
    """Right-pane (linked + backlinks) items also carry ``type``."""
    payload = context_payload(index, "FEAT-0001")
    for bucket in ("linked", "backlinks"):
        for g in payload[bucket]:
            for item in g["items"]:
                assert "type" in item, f"{bucket} item missing 'type': {item}"


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
    # Non-issue items have no severity field populated.
    assert req["severity"] is None
    assert req["url"] == "/docs/REQ-0001-Some-Req.md"


def test_context_payload_issue_carries_severity_with_default(
    index: Index,
) -> None:
    """Issue right-pane items show ``severity`` (default 'low' when
    frontmatter lacks one) and suppress ``priority`` — TASK-0035."""
    payload = context_payload(index, "FEAT-0001")
    issue_items = [
        i for g in payload["backlinks"]
        for i in g["items"] if i["id"] == "ISS-0001"
    ]
    assert issue_items, "ISS-0001 should appear in FEAT-0001 backlinks"
    item = issue_items[0]
    # Fixture has severity: high explicitly set.
    assert item["severity"] == "high"
    assert item["priority"] is None


def test_context_payload_issue_default_severity_low(
    index: Index, docs_root: Path
) -> None:
    """An issue without a frontmatter severity defaults to 'low'."""
    (docs_root / "ISS-0099-Mystery.md").write_text(
        '---\ntype: "[[issue]]"\nid: ISS-0099\ntitle: "Mystery"\n'
        'status: open\naffects: ["[[FEAT-0001]]"]\n---\n# Mystery\n',
        encoding="utf-8",
    )
    fresh = Index.build(docs_root)
    payload = context_payload(fresh, "FEAT-0001")
    iss = next(
        i for g in payload["backlinks"]
        for i in g["items"] if i["id"] == "ISS-0099"
    )
    assert iss["severity"] == "low"
    assert iss["priority"] is None


def test_context_payload_resolves_by_path(index: Index, docs_root: Path) -> None:
    """The JS client may pass a docs-root-relative path or a /docs/-prefixed URL."""
    payload = context_payload(index, "FEAT-0001-Alpha.md")
    assert payload["active"] is not None
    assert payload["active"]["id"] == "FEAT-0001"

    payload = context_payload(index, "/docs/FEAT-0001-Alpha.md")
    assert payload["active"] is not None
    assert payload["active"]["id"] == "FEAT-0001"
