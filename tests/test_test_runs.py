"""The latest test run and CI runs on the Tests page (FEAT-0161 / TASK-0681).

The two files are project-os's (`tools/instructions/TEST-RUNS.md`,
project-os-dev FEAT-0042): `run-tests.py` rewrites
`.project-os/runs/latest.json` as it goes, and `ci-status.py` writes
`.project-os/ci/latest.json`. These cases cover the cockpit's reading of them:

- each file read when present, absent, not JSON, of another format, of an
  unknown version, and when it is missing optional keys (an older writer);
- a `running` run from this machine whose runner is gone reads as stopped,
  and one from another machine is shown as written;
- the log route serves a log the run file names and refuses every other path,
  including one the run file names that leads outside `.project-os/runs/`;
- both routes are loopback-only, over a real socket;
- the watcher publishes `cockpit:test-run` when a writer renames a new
  `latest.json` into place, including into a folder that did not exist when
  the watcher started.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pytest

from project_os_cockpit import test_runs
from project_os_cockpit.events import ControlEvent, EventBus
from project_os_cockpit.index import Index
from project_os_cockpit.server import (
    CockpitState,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)

NOW = datetime(2026, 10, 22, 11, 25, 3, tzinfo=timezone.utc)
HOST = "edwins-mac"
RUN_ID = "20261022T101500Z-48213"


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "your-trainer"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "README.md").write_text("# Docs\n", encoding="utf-8")
    return root


def _log(n: int) -> str:
    return f".project-os/runs/{RUN_ID}/logs/{n:03d}.log"


def _command(n: int, state: str, **extra) -> dict:
    entry = {
        "index": n, "tests": [f"TST-{n:04d}"], "command": f"./check {n}",
        "state": state, "started": None, "seconds": None, "exit": None,
        "reason": "", "log": None, "progress": None,
    }
    entry.update(extra)
    return entry


def _run(**extra) -> dict:
    run = {
        "format": "project-os/test-run", "version": 1, "id": RUN_ID,
        "repo": "your-trainer", "source": "pre-push",
        "commit": "8bf1562c0d1234", "branch": "main",
        "host": HOST, "pid": 48213,
        "started": "2026-10-22T10:15:00Z", "updated": "2026-10-22T11:25:03Z",
        "finished": None, "state": "running",
        "commands": [
            _command(1, "passing", started="2026-10-22T10:15:01Z", seconds=12.0,
                     exit=0, log=_log(1)),
            _command(2, "failing", tests=["TST-0022", "TST-0023"],
                     started="2026-10-22T10:15:13Z", seconds=212.4, exit=1,
                     reason="iOS app killed before the test runner connected\nmore",
                     log=_log(2)),
            _command(3, "timed_out", started="2026-10-22T10:18:46Z", seconds=600.0,
                     reason="timed out after 600 s", log=_log(3)),
            _command(4, "running", started="2026-10-22T11:17:03Z", log=_log(4),
                     progress={"done": 12, "total": 60, "now": "AddRiderFlowTest"}),
            _command(5, "waiting"),
        ],
    }
    run.update(extra)
    return run


def _write(path: Path, data) -> None:
    """Written as the writers do: a temporary file renamed over the old one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
    os.replace(tmp, path)


def _write_run(root: Path, run: dict, *, logs: bool = True) -> None:
    if logs:
        for c in run["commands"]:
            if c.get("log"):
                p = root / c["log"]
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(f"output of command {c['index']}\n", encoding="utf-8")
    _write(root / ".project-os" / "runs" / "latest.json", run)


def _payload(root: Path, *, alive=lambda pid: True, host: str = HOST) -> dict:
    return test_runs.run_payload(root, now=NOW, host=host, alive=alive)


# ---- the run file -----------------------------------------------------------


def test_no_run_file_says_how_to_make_one(tmp_path: Path) -> None:
    out = _payload(_repo(tmp_path))
    assert out["state"] == "absent"
    assert out["message"] == (
        "No test run yet. `python3 tools/scripts/run-tests.py` writes one.")
    assert "run" not in out


def test_a_running_run_reads_as_the_terminal_view_does(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _write_run(root, _run())
    out = _payload(root)
    assert out["state"] == "ok"
    run = out["run"]
    # 1h10m since it started; three of five commands have finished.
    assert run["header"] == "your-trainer · pre-push · 1h10m · 3 of 5 commands"
    assert run["state"] == "running" and run["live"] is True
    assert run["commit"] == "8bf1562"
    assert [c["symbol"] for c in run["commands"]] == ["■", "✗", "⧗", "▶", "□"]
    assert [c["index"] for c in run["commands"]] == [1, 2, 3, 4, 5]
    # Rows: failing, timed out and running. Passing and waiting are told by
    # their blocks alone.
    listed = [c["index"] for c in run["commands"] if c["listed"]]
    assert listed == [2, 3, 4]
    failing = run["commands"][1]
    assert failing["tests"] == ["TST-0022", "TST-0023"]
    assert failing["took"] == "3m32s"
    assert failing["reason"] == "iOS app killed before the test runner connected"
    running = run["commands"][3]
    assert running["progress"] == "12/60 AddRiderFlowTest"
    assert running["took"] == "8m"            # now - its start
    assert running["log_url"] == (
        "/api/cockpit/test-run/log?path="
        ".project-os%2Fruns%2F20261022T101500Z-48213%2Flogs%2F004.log")
    # A waiting command has no log yet, and so no link.
    assert run["commands"][4]["log_url"] == ""


def test_a_finished_run_counts_every_command_and_stops_ticking(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    run = _run(state="failing", finished="2026-10-22T11:40:00Z")
    run["commands"] = run["commands"][:3]
    _write_run(root, run)
    out = _payload(root)["run"]
    assert out["header"] == "your-trainer · pre-push · 1h25m · 3 of 3 commands"
    assert out["live"] is False
    assert out["state_line"] == "finished with failures"


@pytest.mark.parametrize("content, says", [
    ("{\"format\": \"project-os/test-run\", \"version\": 1, ", "is not valid JSON"),
    ("[1, 2]", "is not a JSON object"),
    (json.dumps({"format": "something-else", "version": 1}), "is not a project-os/test-run file"),
    (json.dumps({"format": "project-os/test-run", "version": 2, "commands": []}),
     "is format version 2, which this cockpit does not read"),
    (json.dumps({"format": "project-os/test-run", "commands": []}),
     "is format version None, which this cockpit does not read"),
])
def test_a_run_file_that_cannot_be_read_says_so_in_one_line(
    tmp_path: Path, content: str, says: str,
) -> None:
    root = _repo(tmp_path)
    _write(root / ".project-os" / "runs" / "latest.json", content)
    out = _payload(root)
    assert out["state"] == "unreadable"
    assert out["message"] == f".project-os/runs/latest.json {says}."
    assert "run" not in out


def test_a_run_file_missing_optional_keys_still_reads(tmp_path: Path) -> None:
    """An older or smaller writer: no host, pid, index, log, progress or times.

    TEST-RUNS.md: a reader ignores keys it does not know, and every key it
    knows may be empty. Unknown keys at both levels are ignored too.
    """
    root = _repo(tmp_path)
    _write_run(root, {
        "format": "project-os/test-run", "version": 1, "state": "running",
        "brand_new_key": {"nested": True},
        "commands": [
            {"tests": ["TST-0001"], "state": "passing", "also_new": 1},
            {"tests": ["TST-0002"]},
            {"command": "./gradlew test", "state": "a-state-from-the-future"},
            "not a command",
        ],
    }, logs=False)
    out = _payload(root)
    assert out["state"] == "ok"
    run = out["run"]
    assert [c["index"] for c in run["commands"]] == [1, 2, 3]
    assert [c["state"] for c in run["commands"]] == [
        "passing", "waiting", "a-state-from-the-future"]
    # An unknown state still gets a block and a row, in its own words.
    future = run["commands"][2]
    assert future["symbol"] == test_runs.UNKNOWN_SYMBOL
    assert future["listed"] is True
    assert future["label"] == "a-state-from-the-future"
    # The header falls back to the folder's name when the run names no repo.
    assert run["header"] == "your-trainer · 1 of 3 commands"
    assert all(c["log_url"] == "" for c in run["commands"])


def test_a_dead_runner_on_this_machine_reads_as_stopped(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _write_run(root, _run())
    asked: list[int] = []

    def gone(pid: int) -> bool:
        asked.append(pid)
        return False

    run = _payload(root, alive=gone)["run"]
    assert asked == [48213]
    assert run["state"] == "stopped" and run["live"] is False
    assert run["state_line"].startswith("stopped: runner 48213 is no longer running")
    # The command it was running is shown as interrupted, with its own symbol.
    cmd = run["commands"][3]
    assert (cmd["state"], cmd["symbol"], cmd["listed"]) == ("interrupted", "‖", True)
    # Elapsed stops at the last write, not at now.
    assert "1h10m" in run["header"]


def test_the_host_matches_with_or_without_its_local_suffix(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _write_run(root, _run(host="Edwins-Mac.local"))
    assert _payload(root, alive=lambda pid: False)["run"]["state"] == "stopped"


@pytest.mark.parametrize("change", [
    {"host": "ci-runner-7"},     # another machine: its pid means nothing here
    {"pid": None},               # no pid to ask about
    {"state": "failing"},        # finished: nothing to check
])
def test_a_run_that_cannot_be_judged_stopped_is_shown_as_written(
    tmp_path: Path, change: dict,
) -> None:
    root = _repo(tmp_path)
    _write_run(root, _run(**change))
    run = _payload(root, alive=lambda pid: False)["run"]
    assert run["state"] == change.get("state", "running")


def test_pid_alive_tells_a_live_process_from_a_finished_one() -> None:
    assert test_runs.pid_alive(os.getpid()) is True
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    assert test_runs.pid_alive(child.pid) is False
    assert test_runs.pid_alive(0) is False


def test_durations_and_ages_read_at_the_runs_grain() -> None:
    f = test_runs.format_duration
    assert [f(None), f(4.4), f(59), f(60), f(212.4), f(3600), f(4200), f(90000)] == [
        "", "4s", "59s", "1m", "3m32s", "1h", "1h10m", "1d1h"]
    a = test_runs.format_ago
    assert [a(None), a(30), a(720), a(3 * 3600), a(2 * 86400)] == [
        "", "just now", "12m ago", "3h ago", "2d ago"]


# ---- the log a run names ----------------------------------------------------


def test_a_named_log_is_served_and_nothing_else(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    run = _run()
    # A wrong run file that names a path outside `.project-os/runs/`.
    run["commands"].append(_command(6, "failing", log="docs/README.md"))
    run["commands"].append(_command(7, "failing", log="../outside.log"))
    run["commands"].append(_command(8, "failing", log=str(root / "docs" / "README.md")))
    _write_run(root, run, logs=False)
    for c in run["commands"][:4]:
        p = root / c["log"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x\n", encoding="utf-8")
    (tmp_path / "outside.log").write_text("secret\n", encoding="utf-8")

    assert test_runs.log_file(root, _log(2)) == (root / _log(2)).resolve()
    refused = [
        "docs/README.md",                       # named, but not under runs/
        "../outside.log",                       # named, and outside the repo
        str(root / "docs" / "README.md"),       # named, and absolute
        f".project-os/runs/{RUN_ID}/logs/099.log",   # under runs/, not named
        f".project-os/runs/{RUN_ID}/logs/../../latest.json",
        "", "\x00",
    ]
    for rel in refused:
        assert test_runs.log_file(root, rel) is None, rel


def test_a_named_log_that_is_a_link_out_of_runs_is_refused(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    run = _run()
    _write_run(root, run)
    secret = tmp_path / "secret.txt"
    secret.write_text("token\n", encoding="utf-8")
    link = root / _log(1)
    link.unlink()
    link.symlink_to(secret)
    assert test_runs.log_file(root, _log(1)) is None


def test_a_long_log_is_sent_from_its_end(tmp_path: Path) -> None:
    log = tmp_path / "big.log"
    log.write_text("".join(f"line {i}\n" for i in range(1000)), encoding="utf-8")
    out = test_runs.read_log(log, limit=200).decode("utf-8")
    assert out.startswith("[the first ")
    assert out.rstrip().endswith("line 999")
    body = out.split("\n\n", 1)[1]
    assert body.startswith("line ")           # a whole line, not half of one


# ---- the CI file ------------------------------------------------------------


def _ci(**extra) -> dict:
    failed = {
        "id": 18734412, "url": "https://github.com/edankert/your-trainer/actions/runs/18734412",
        "commit": "8bf1562c0d1234", "event": "push", "status": "completed",
        "conclusion": "failure", "created": "2026-10-22T10:40:00Z",
        "updated": "2026-10-22T11:02:00Z", "failing_tests": ["TST-0022"],
        "failing_jobs": ["android"], "details": "artifact",
    }
    running = dict(failed, id=18734999, commit="aaaa111bbbb", status="in_progress",
                   conclusion=None, updated="2026-10-22T11:20:00Z",
                   failing_tests=[], failing_jobs=[])
    passed = dict(failed, conclusion="success", failing_tests=[], failing_jobs=[],
                  url="https://github.com/edankert/your-trainer/actions/runs/1")
    jobs_only = dict(failed, failing_tests=[], failing_jobs=["lint", "unit"],
                     details="jobs", updated="2026-10-20T11:00:00Z")
    data = {
        "format": "project-os/ci-status", "version": 1, "repo": "your-trainer",
        "branch": "main", "fetched": "2026-10-22T11:22:03Z", "error": "",
        "workflows": [
            {"name": "android-tests", "latest": failed, "last_finished": failed},
            {"name": "validate-docs", "latest": running, "last_finished": failed},
            {"name": "ios-tests", "latest": passed, "last_finished": passed},
            {"name": "lint", "latest": jobs_only, "last_finished": jobs_only},
        ],
    }
    data.update(extra)
    return data


def test_no_ci_file_says_so_in_one_line(tmp_path: Path) -> None:
    out = test_runs.ci_payload(_repo(tmp_path), now=NOW)
    assert out["state"] == "absent"
    assert out["message"] == (
        "No CI result yet. `python3 tools/scripts/ci-status.py` fetches one.")


def test_each_workflow_reads_as_its_latest_run(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _write(root / ".project-os" / "ci" / "latest.json", _ci())
    out = test_runs.ci_payload(root, now=NOW)
    assert out["state"] == "ok"
    assert out["fetched_ago"] == "3m ago" and out["error"] == ""
    wf = {w["name"]: w for w in out["workflows"]}
    android = wf["android-tests"]
    assert (android["state"], android["symbol"], android["commit"]) == ("failed", "✗", "8bf1562")
    assert android["ago"] == "23m ago"
    assert android["failing_tests"] == ["TST-0022"]
    assert android["url"].endswith("/actions/runs/18734412")
    assert android["red"] is True and android["previous"] is None
    # Still running after a failure: the failure travels with it.
    docs = wf["validate-docs"]
    assert docs["state"] == "running" and docs["red"] is True
    assert docs["previous"]["failing_tests"] == ["TST-0022"]
    assert wf["ios-tests"]["state"] == "passing" and wf["ios-tests"]["red"] is False
    # No run file uploaded: the failed jobs are named instead.
    assert wf["lint"]["failing_jobs"] == ["lint", "unit"]
    assert wf["lint"]["ago"] == "2d ago"


def test_a_fetch_error_is_one_line_beside_the_previous_runs(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _write(root / ".project-os" / "ci" / "latest.json",
           _ci(error="gh is not logged in.\nRun gh auth login."))
    out = test_runs.ci_payload(root, now=NOW)
    assert out["error"] == "gh is not logged in."
    assert len(out["workflows"]) == 4


def test_a_ci_link_that_is_not_http_is_not_offered(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    data = _ci()
    data["workflows"][0]["latest"]["url"] = "file:///etc/passwd"
    _write(root / ".project-os" / "ci" / "latest.json", data)
    wf = test_runs.ci_payload(root, now=NOW)["workflows"][0]
    assert wf["url"] == ""


def test_a_ci_file_of_an_unknown_version_is_unreadable(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _write(root / ".project-os" / "ci" / "latest.json", _ci(version=3))
    out = test_runs.ci_payload(root, now=NOW)
    assert out["state"] == "unreadable"
    assert out["message"] == (
        ".project-os/ci/latest.json is format version 3, which this cockpit does not read.")


# ---- the routes -------------------------------------------------------------


def _serve(root: Path, client: str | None = None):
    docs = (root / "docs").resolve()
    bus = EventBus()
    index = Index.build(docs)
    base = _make_handler(docs, index, bus, cockpit_state=CockpitState())
    if client is not None:
        class Remote(base):  # type: ignore[misc,valid-type]
            @property
            def client_address(self):
                return (client, 54321)

            @client_address.setter
            def client_address(self, _value):
                pass
        handler = Remote
    else:
        handler = base
    httpd = _NoDNSThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def _get(url: str) -> tuple[int, str, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.status, resp.headers.get("Content-Type", ""), resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Content-Type", ""), exc.read()


def test_the_route_returns_both_readings_and_serves_a_named_log(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _write_run(root, _run())
    httpd, base = _serve(root)
    try:
        status, _ctype, body = _get(f"{base}/api/cockpit/test-run")
        assert status == 200
        data = json.loads(body)
        assert data["run"]["state"] == "ok" and data["ci"]["state"] == "absent"
        url = data["run"]["run"]["commands"][1]["log_url"]

        status, ctype, body = _get(base + url)
        assert status == 200 and ctype.startswith("text/plain")
        assert body == b"output of command 2\n"

        for rel in ["docs/README.md", "../SNAPSHOT.yaml", "/etc/passwd",
                    f".project-os/runs/{RUN_ID}/logs/099.log"]:
            status, _ctype, body = _get(
                f"{base}/api/cockpit/test-run/log?path={urllib.parse.quote(rel, safe='')}")
            assert status == 404, rel
            assert json.loads(body)["error"] == "not a log the latest test run names"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_both_routes_refuse_a_peer_on_the_network(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _write_run(root, _run())
    httpd, base = _serve(root, client="203.0.113.7")
    try:
        for path in ["/api/cockpit/test-run",
                     "/api/cockpit/test-run/log?path=" + urllib.parse.quote(_log(1), safe="")]:
            status, _ctype, body = _get(base + path)
            assert status == 403, path
            assert json.loads(body)["error"] == "test run reads are loopback-only"
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- the watcher ------------------------------------------------------------


def _wait_for(events: list, n: int, seconds: float = 8.0) -> None:
    deadline = time.time() + seconds
    while time.time() < deadline and len(events) < n:
        time.sleep(0.05)


def test_a_new_latest_file_publishes_one_event_per_burst(tmp_path: Path) -> None:
    """Driven through the real observer, with no `.project-os/` at start.

    The first run's folder appears after the sidecar started, so the watcher
    must find it and announce the file already in it; later rewrites arrive
    as renames of a temporary file, which is the move the writers make.
    """
    root = _repo(tmp_path)
    bus = EventBus()
    seen: list[dict] = []
    bus.subscribe(lambda ev: seen.append(ev.data)
                  if isinstance(ev, ControlEvent) and ev.event_type == "cockpit:test-run"
                  else None)
    watcher = test_runs.TestRunWatcher(root, bus, debounce_seconds=0.1, rearm_seconds=0.2)
    watcher.start()
    try:
        time.sleep(0.5)
        assert seen == []                     # nothing exists; nothing to say
        _write_run(root, _run())
        _wait_for(seen, 1)
        assert seen and seen[0] == {"what": ["run"]}

        time.sleep(1.0)                       # let FSEvents attach to runs/
        seen.clear()
        for state in ("failing", "passing", "failing"):   # one burst of rewrites
            _write_run(root, _run(state=state))
        _wait_for(seen, 1)
        time.sleep(0.5)
        assert seen and all(e == {"what": ["run"]} for e in seen)
        assert len(seen) <= 2, seen           # coalesced, not one per write

        seen.clear()
        # A log line is not news: the logs live a folder down, unwatched.
        (root / _log(1)).write_text("more output\n", encoding="utf-8")
        time.sleep(0.8)
        assert seen == []

        _write(root / ".project-os" / "ci" / "latest.json", _ci())
        _wait_for(seen, 1)
        assert seen and seen[0] == {"what": ["ci"]}
    finally:
        watcher.stop()
