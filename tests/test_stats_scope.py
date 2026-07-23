"""Scoped stats payload + cache (FEAT-0023 / TASK-0128, TST-0012).

Fixture tree: two phases, features/tasks split across them, a test
linked to a scoped feature via `features:`, and exit criteria in the
phase note body.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

from project_os_cockpit import cockpit
from project_os_cockpit.index import Index
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _note(path: Path, fm: dict, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f"{k}: {json.dumps(v)}")
        else:
            lines.append(f'{k}: "{v}"' if isinstance(v, str) and not v.startswith("[[") else f'{k}: {json.dumps(v)}')
    lines.append("---")
    path.write_text("\n".join(lines) + "\n\n" + body, encoding="utf-8")


def _make_tree(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    _note(docs / "phases" / "PHASE-001-Alpha.md", {
        "type": "[[phase]]", "id": "PHASE-001", "title": "Alpha",
        "status": "done", "order": 1,
    })
    _note(docs / "phases" / "PHASE-002-Beta.md", {
        "type": "[[phase]]", "id": "PHASE-002", "title": "Beta",
        "status": "active", "order": 2,
    }, body=(
        "# Beta\n\n## Exit Criteria\n"
        "- [x] first criterion met\n"
        "- [ ] second criterion pending\n"
        "## Notes\n- [ ] not an exit criterion\n"
    ))
    _note(docs / "features" / "a" / "FEAT-0001-A.md", {
        "type": "[[feature]]", "id": "FEAT-0001", "title": "Feat A",
        "status": "done", "phase": "[[PHASE-001]]",
    })
    _note(docs / "features" / "b" / "FEAT-0002-B.md", {
        "type": "[[feature]]", "id": "FEAT-0002", "title": "Feat B",
        "status": "in-progress", "phase": "[[PHASE-002]]",
    })
    # Task inherits phase from parent feature (no direct phase).
    _note(docs / "features" / "b" / "plan" / "tasks" / "TASK-0001-B1.md", {
        "type": "[[task]]", "id": "TASK-0001", "title": "B task",
        "status": "done", "parent": "[[FEAT-0002]]",
    })
    _note(docs / "features" / "a" / "plan" / "tasks" / "TASK-0002-A1.md", {
        "type": "[[task]]", "id": "TASK-0002", "title": "A task",
        "status": "done", "parent": "[[FEAT-0001]]",
    })
    # Test linked to the Beta feature only via `features:`.
    _note(docs / "tests" / "TST-0001-B.md", {
        "type": "[[test]]", "id": "TST-0001", "title": "B test",
        "status": "passing", "features": ["[[FEAT-0002]]"],
    })
    return docs


def test_scoped_payload_filters_and_enriches(tmp_path: Path):
    docs = _make_tree(tmp_path)
    index = Index.build(docs)

    full = cockpit.stats_payload(index)
    assert full["scope"] is None
    assert full["hero"]["tasks"]["total"] == 2
    assert len(full["phases"]) == 2

    scoped = cockpit.stats_payload(index, scope="PHASE-002")
    assert scoped is not None
    assert scoped["scope"]["id"] == "PHASE-002"
    assert scoped["scope"]["title"] == "Beta"
    # Only Beta's feature/task/test survive the filter.
    assert scoped["hero"]["features"]["total"] == 1
    assert scoped["hero"]["tasks"]["total"] == 1
    assert scoped["hero"]["tests"] == {"total": 1, "passing": 1}
    assert len(scoped["phases"]) == 1
    assert scoped["phases"][0]["key"] == "PHASE-002"
    assert scoped["phases"][0]["features"][0]["id"] == "FEAT-0002"
    # Exit criteria parsed from the note body, Notes section excluded.
    assert scoped["exit_criteria"] == [
        {"text": "first criterion met", "done": True},
        {"text": "second criterion pending", "done": False},
    ]
    # Scoped recent feed only contains Beta items.
    ids = {r["id"] for r in scoped["activity"]["recent"]}
    assert "TASK-0002" not in ids
    assert "FEAT-0001" not in ids


def test_unknown_scope_returns_none(tmp_path: Path):
    docs = _make_tree(tmp_path)
    index = Index.build(docs)
    assert cockpit.stats_payload(index, scope="PHASE-099") is None


def _spin_up(docs: Path):
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
            agent_tracker=server.agent_tracker,
        ),
    )
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return server, httpd, port


def _get(port: int, path: str):
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}{path}", timeout=3,
        ) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_endpoint_scope_and_cache(tmp_path: Path):
    docs = _make_tree(tmp_path)
    server, httpd, port = _spin_up(docs)
    try:
        status, body = _get(port, "/api/cockpit/stats?scope=PHASE-002")
        assert status == 200
        assert body["scope"]["id"] == "PHASE-002"

        status, _ = _get(port, "/api/cockpit/stats?scope=PHASE-042")
        assert status == 404

        # Cache validity: same generation → identical payload identity
        # can't be observed over HTTP, so prove behaviour instead —
        # a stale cache would miss the new task after invalidation.
        new_task = docs / "features" / "b" / "plan" / "tasks" / "TASK-0003-B2.md"
        _note(new_task, {
            "type": "[[task]]", "id": "TASK-0003", "title": "B task 2",
            "status": "backlog", "parent": "[[FEAT-0002]]",
        })
        _, before = _get(port, "/api/cockpit/stats?scope=PHASE-002")
        assert before["hero"]["tasks"]["total"] == 1  # cache still serving
        server.index.invalidate(new_task)             # watcher-equivalent
        _, after = _get(port, "/api/cockpit/stats?scope=PHASE-002")
        assert after["hero"]["tasks"]["total"] == 2   # generation bumped
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_generation_increments_on_invalidate(tmp_path: Path):
    docs = _make_tree(tmp_path)
    index = Index.build(docs)
    g0 = index.generation
    target = docs / "features" / "a" / "FEAT-0001-A.md"
    index.invalidate(target)
    assert index.generation == g0 + 1


def test_retired_and_superseded_count_as_done(tmp_path: Path) -> None:
    """TASK-0176: terminal-resolved items complete the progress bar — a
    superseded feature, a retired requirement, and a cancelled task are
    done (not backlog), and the hero tiles agree with the phase bar (no
    hero-vs-bar disagreement), so a phase of only-resolved items is 100%."""
    docs = tmp_path / "docs"
    _note(docs / "phases" / "PHASE-001-Alpha.md", {
        "type": "[[phase]]", "id": "PHASE-001", "title": "Alpha",
        "status": "active", "order": 1,
    })
    _note(docs / "features" / "s" / "FEAT-0001-Sup.md", {
        "type": "[[feature]]", "id": "FEAT-0001", "title": "Sup",
        "status": "superseded", "phase": "[[PHASE-001]]",
    })
    _note(docs / "requirements" / "REQ-0001-Ret.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "Ret",
        "status": "retired", "phase": "[[PHASE-001]]",
    })
    # A cancelled task under the superseded feature — must count done in
    # BOTH the hero tile and the phase bar (the review's harmonisation).
    _note(docs / "features" / "s" / "plan" / "tasks" / "TASK-0001-C.md", {
        "type": "[[task]]", "id": "TASK-0001", "title": "Cancelled",
        "status": "cancelled", "parent": "[[FEAT-0001]]",
    })
    idx = Index.build(docs)
    pay = cockpit.stats_payload(idx, scope="PHASE-001")
    hero = pay["hero"]
    assert hero["features"] == {"total": 1, "done": 1}
    assert hero["requirements"] == {"total": 1, "done": 1}
    assert hero["tasks"] == {"total": 1, "done": 1}  # cancelled counts done
    # Phase progress bucket: the superseded feature counts done, no backlog.
    phase = next((p for p in pay["phases"] if p.get("key") == "PHASE-001"), None)
    assert phase is not None
    assert phase["tasks"]["backlog"] == 0
    assert phase["tasks"]["done"] >= 1
    # Drill-down: the feature + the (loose) requirement both bucket done.
    buckets = {c["id"]: c["bucket"]
               for f in phase["features"]
               for c in ([f] + f.get("children", []))}
    buckets.update({c["id"]: c["bucket"] for c in phase.get("loose", [])})
    assert buckets["FEAT-0001"] == "done"
    assert buckets["REQ-0001"] == "done"


def test_boxes_agree_with_hero_per_type(tmp_path: Path) -> None:
    """TASK-0181: the phase boxes and the hero counts consult ONE per-type
    done set, so a status that's terminal for one type but not another can't
    render a filled box while the count disagrees. `accepted` is done for a
    requirement but NOT for a task — the old type-agnostic union bucketed
    BOTH done, diverging from the per-type hero. Now both agree per type."""
    docs = tmp_path / "docs"
    _note(docs / "phases" / "PHASE-001-Alpha.md", {
        "type": "[[phase]]", "id": "PHASE-001", "title": "Alpha",
        "status": "active", "order": 1,
    })
    _note(docs / "features" / "x" / "FEAT-0001-X.md", {
        "type": "[[feature]]", "id": "FEAT-0001", "title": "X",
        "status": "in-progress", "phase": "[[PHASE-001]]",
    })
    # `accepted` requirement → done for a requirement (DONE_REQ).
    _note(docs / "requirements" / "REQ-0001-Acc.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "Acc",
        "status": "accepted", "phase": "[[PHASE-001]]",
    })
    # `accepted` task → NOT done for a task (not in DONE_TASK). Under the old
    # union this rendered a filled box while the hero task count said 0/1.
    _note(docs / "features" / "x" / "plan" / "tasks" / "TASK-0001-A.md", {
        "type": "[[task]]", "id": "TASK-0001", "title": "Acc task",
        "status": "accepted", "parent": "[[FEAT-0001]]",
    })
    idx = Index.build(docs)
    pay = cockpit.stats_payload(idx, scope="PHASE-001")
    hero = pay["hero"]
    # Hero: the requirement counts done, the task does NOT.
    assert hero["requirements"] == {"total": 1, "done": 1}
    assert hero["tasks"] == {"total": 1, "done": 0}
    # Boxes agree with the hero, per type.
    phase = next(p for p in pay["phases"] if p.get("key") == "PHASE-001")
    buckets = {c["id"]: c["bucket"]
               for f in phase["features"]
               for c in ([f] + f.get("children", []))}
    buckets.update({c["id"]: c["bucket"] for c in phase.get("loose", [])})
    assert buckets["REQ-0001"] == "done"      # accepted requirement → filled
    assert buckets["TASK-0001"] == "backlog"  # accepted task → NOT filled
    # And the phase task bar counts the accepted task as backlog, not done.
    assert phase["tasks"]["done"] == 0
    assert phase["tasks"]["backlog"] == 1


def test_child_phase_placement_agrees_across_views(tmp_path: Path) -> None:
    """TASK-0182: a task whose own `phase:` differs from its parent feature's
    phase (a deferred task parked in a future phase) must appear in the SAME
    place on the project overview and on every scoped phase page — under its
    OWN phase (loose), never under its parent's phase section. A normal child
    that inherits its parent's phase still nests under the parent."""
    docs = tmp_path / "docs"
    _note(docs / "phases" / "PHASE-001-Alpha.md", {
        "type": "[[phase]]", "id": "PHASE-001", "title": "Alpha",
        "status": "active", "order": 1,
    })
    _note(docs / "phases" / "PHASE-002-Future.md", {
        "type": "[[phase]]", "id": "PHASE-002", "title": "Future",
        "status": "planned", "order": 2,
    })
    _note(docs / "features" / "f" / "FEAT-0001-F.md", {
        "type": "[[feature]]", "id": "FEAT-0001", "title": "F",
        "status": "done", "phase": "[[PHASE-001]]",
    })
    # Parked task: parent is in PHASE-001 but the task itself is in PHASE-002.
    _note(docs / "features" / "f" / "plan" / "tasks" / "TASK-0001-Parked.md", {
        "type": "[[task]]", "id": "TASK-0001", "title": "Parked",
        "status": "deferred", "parent": "[[FEAT-0001]]",
        "phase": "[[PHASE-002]]",
    })
    # Normal task: no own phase → inherits PHASE-001 from the parent.
    _note(docs / "features" / "f" / "plan" / "tasks" / "TASK-0002-Normal.md", {
        "type": "[[task]]", "id": "TASK-0002", "title": "Normal",
        "status": "done", "parent": "[[FEAT-0001]]",
    })
    idx = Index.build(docs)

    def _feat_children(pay, phase_key, feat_id):
        ph = next(p for p in pay["phases"] if p.get("key") == phase_key)
        feat = next(f for f in ph["features"] if f["id"] == feat_id)
        return {c["id"] for c in feat.get("children", [])}

    def _loose_ids(pay, phase_key):
        ph = next((p for p in pay["phases"] if p.get("key") == phase_key), None)
        return {c["id"] for c in (ph or {}).get("loose", [])}

    # --- project overview (unscoped) ---
    full = cockpit.stats_payload(idx)
    # FEAT-0001 (PHASE-001) nests only the phase-inheriting child, NOT the
    # parked one — the parked task surfaces loose under its own PHASE-002.
    assert _feat_children(full, "PHASE-001", "FEAT-0001") == {"TASK-0002"}
    assert "TASK-0001" in _loose_ids(full, "PHASE-002")
    assert "TASK-0001" not in _loose_ids(full, "PHASE-001")

    # --- scoped parent-phase page (PHASE-001) agrees: no parked task ---
    p1 = cockpit.stats_payload(idx, scope="PHASE-001")
    assert _feat_children(p1, "PHASE-001", "FEAT-0001") == {"TASK-0002"}
    assert "TASK-0001" not in _loose_ids(p1, "PHASE-001")

    # --- scoped own-phase page (PHASE-002) shows the parked task loose ---
    p2 = cockpit.stats_payload(idx, scope="PHASE-002")
    assert "TASK-0001" in _loose_ids(p2, "PHASE-002")


def test_work_items_enrichment(tmp_path: Path) -> None:
    """TASK-0191: work_notes enrich into items with real title/status/type,
    per-type `done`, and `current_prompt` gated on the prompt boundary."""
    docs = tmp_path / "docs"
    _note(docs / "requirements" / "REQ-0001-A.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "Req A",
        "status": "accepted",  # accepted requirement → done
    })
    _note(docs / "features" / "f" / "plan" / "tasks" / "TASK-0001-B.md", {
        "type": "[[task]]", "id": "TASK-0001", "title": "Task B",
        "status": "accepted",  # accepted task → NOT done (per-type)
    })
    _note(docs / "issues" / "ISS-0001-C.md", {
        "type": "[[issue]]", "id": "ISS-0001", "title": "Iss C", "status": "open",
    })
    idx = Index.build(docs)
    sess = {
        "work_notes": [
            "requirements/REQ-0001-A.md",
            "features/f/plan/tasks/TASK-0001-B.md",
            "issues/ISS-0001-C.md",
        ],
        "work_ts": {
            "requirements/REQ-0001-A.md": "2026-07-22T10:00:00+00:00",   # after prompt
            "features/f/plan/tasks/TASK-0001-B.md": "2026-07-22T09:00:00+00:00",  # before
            # ISS has no touch timestamp at all
        },
        "prompt_started": "2026-07-22T09:30:00+00:00",
    }
    items = cockpit.work_items_for_session(idx, sess)
    by_id = {i["id"]: i for i in items}

    assert by_id["REQ-0001"]["title"] == "Req A"
    assert by_id["REQ-0001"]["type"] == "requirement"
    assert by_id["REQ-0001"]["done"] is True            # accepted req = done
    assert by_id["TASK-0001"]["done"] is False           # accepted task ≠ done
    assert by_id["ISS-0001"]["status"] == "open"

    # current_prompt: touched at/after the prompt boundary only.
    assert by_id["REQ-0001"]["current_prompt"] is True    # 10:00 ≥ 09:30
    assert by_id["TASK-0001"]["current_prompt"] is False   # 09:00 < 09:30
    assert by_id["ISS-0001"]["current_prompt"] is False    # no touch ts


def test_work_items_seeded_session_without_prompt(tmp_path: Path) -> None:
    """A seeded session (sidecar reloaded, no prompt boundary yet) counts any
    timestamped touch as current, so the in-flight set survives a reload."""
    docs = tmp_path / "docs"
    _note(docs / "issues" / "ISS-0002-D.md", {
        "type": "[[issue]]", "id": "ISS-0002", "title": "D", "status": "fixed",
    })
    idx = Index.build(docs)
    sess = {
        "work_notes": ["issues/ISS-0002-D.md"],
        "work_ts": {"issues/ISS-0002-D.md": "2026-07-22T08:00:00+00:00"},
        "prompt_started": None,
    }
    items = cockpit.work_items_for_session(idx, sess)
    assert items[0]["current_prompt"] is True
    assert items[0]["done"] is True   # fixed issue = done


def test_work_items_include_snapshot_focus(tmp_path: Path) -> None:
    """TASK-0193: the in-flight set includes the SNAPSHOT `focus` items even
    when no note was touched this prompt, unioned + deduped with touched."""
    docs = tmp_path / "docs"
    _note(docs / "features" / "f" / "plan" / "tasks" / "TASK-0116-Rebrand.md", {
        "type": "[[task]]", "id": "TASK-0116", "title": "Rebrand", "status": "doing",
    })
    _note(docs / "issues" / "ISS-0022-Trends.md", {
        "type": "[[issue]]", "id": "ISS-0022", "title": "Trends review", "status": "fixed",
    })
    _note(docs / "phases" / "PHASE-0007-V2.md", {
        "type": "[[phase]]", "id": "PHASE-0007", "title": "Trends V2", "status": "active",
    })
    # SNAPSHOT.yaml lives at docs_root.parent.
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'counters:\n  TASK: 116\n'
        'focus:\n'
        '  task: "TASK-0116"\n'
        '  issue: "ISS-0022"\n'
        '  feature: ""\n'
        '  phase: "[[PHASE-0007-V2]]"\n'
        '  note: "some free text mentioning TASK-9999 which must be ignored"\n'
        'items:\n  features: {}\n',
        encoding="utf-8",
    )
    idx = Index.build(docs)

    # Session touched NOTHING this prompt (agent edited code, not notes).
    sess = {"work_notes": [], "work_ts": {}, "prompt_started": "2026-07-23T17:14:00+00:00"}
    items = cockpit.work_items_for_session(idx, sess)
    by_id = {i["id"]: i for i in items}

    # Focus items surface as current-prompt, enriched from the index.
    assert by_id["TASK-0116"]["current_prompt"] is True
    assert by_id["TASK-0116"]["title"] == "Rebrand"
    assert by_id["TASK-0116"]["done"] is False          # doing task
    assert by_id["ISS-0022"]["done"] is True             # fixed issue
    assert by_id["PHASE-0007"]["title"] == "Trends V2"   # wikilink id resolved
    # The `note` free-text id is NOT pulled in.
    assert "TASK-9999" not in by_id
    # Empty focus field contributes nothing.
    assert all(i["id"] for i in items)


def test_work_items_focus_union_dedupes_touched(tmp_path: Path) -> None:
    """A focus item that was ALSO touched this prompt appears once, carrying
    the touch timestamp (TASK-0193)."""
    docs = tmp_path / "docs"
    _note(docs / "issues" / "ISS-0022-Trends.md", {
        "type": "[[issue]]", "id": "ISS-0022", "title": "T", "status": "doing",
    })
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'focus:\n  issue: "ISS-0022"\n', encoding="utf-8")
    idx = Index.build(docs)
    sess = {
        "work_notes": ["issues/ISS-0022-Trends.md"],
        "work_ts": {"issues/ISS-0022-Trends.md": "2026-07-23T18:00:00+00:00"},
        "prompt_started": "2026-07-23T17:00:00+00:00",
    }
    items = cockpit.work_items_for_session(idx, sess)
    assert [i["id"] for i in items] == ["ISS-0022"]      # appears exactly once
    assert items[0]["current_prompt"] is True
    assert items[0]["ts"] == "2026-07-23T18:00:00+00:00"  # adopted the touch ts


def test_work_items_include_session_status_changes(tmp_path: Path) -> None:
    """TASK-0194: a note whose status changed this session surfaces as a
    current work item even if it was never a `work_note` touch (e.g. edited
    by a shell tool), while a created-but-unchanged note stays out."""
    docs = tmp_path / "docs"
    _note(docs / "features" / "f" / "plan" / "tasks" / "TASK-0200-Done.md", {
        "type": "[[task]]", "id": "TASK-0200", "title": "Shipped", "status": "done",
    })
    _note(docs / "requirements" / "REQ-0100-Backlog.md", {
        "type": "[[requirement]]", "id": "REQ-0100", "title": "Backlog", "status": "draft",
    })
    idx = Index.build(docs)
    sess = {
        "work_notes": [],          # nothing touched via an edit tool
        "work_ts": {},
        "prompt_started": "2026-07-23T17:00:00+00:00",
        # TASK-0200 changed status this session (via the watcher); REQ-0100
        # was only created (no transition) so it must NOT appear.
        "status_touched": {
            "features/f/plan/tasks/TASK-0200-Done.md": {
                "id": "TASK-0200", "status": "done",
                "ts": "2026-07-23T16:30:00+00:00", "title": "Shipped",
            },
        },
    }
    items = cockpit.work_items_for_session(idx, sess)
    by_id = {i["id"]: i for i in items}
    assert by_id["TASK-0200"]["current_prompt"] is True   # shown despite no touch
    assert by_id["TASK-0200"]["done"] is True
    assert by_id["TASK-0200"]["title"] == "Shipped"       # enriched from index
    assert "REQ-0100" not in by_id                         # created ≠ worked


def test_record_status_change_stamps_live_session(tmp_path: Path) -> None:
    """TASK-0194: record_status_change stamps the live session and rides the
    slim `status_touched`; no live session → no-op."""
    from project_os_cockpit.agent_hooks import AgentSessionTracker
    tr = AgentSessionTracker(docs_root=tmp_path / "docs")
    payload = {"id": "ISS-0050", "rel": "issues/ISS-0050-X.md",
               "to": "fixed", "ts": "2026-07-23T18:00:00+00:00", "title": "X"}
    # No live session yet → no-op.
    tr.record_status_change(payload)
    tr.ingest({"hook_event_name": "SessionStart", "session_id": "S1", "agent": "claude"})
    tr.record_status_change(payload)
    sess = tr.snapshot()["session"]
    st = sess["status_touched"]
    assert "issues/ISS-0050-X.md" in st
    assert st["issues/ISS-0050-X.md"]["status"] == "fixed"
