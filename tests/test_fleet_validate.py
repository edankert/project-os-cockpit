"""Cold-workspace validation (FEAT-0028 / TASK-0249).

This is the half of the fleet health surface with a blast radius: it
runs a validator inside repositories the user never asked this app to
touch. Two things therefore have to be *asserted*, not intended:

1. **It does not write.** The validator's one write path (``fix_metrics``,
   which rewrites ``SNAPSHOT.yaml``) is behind ``--fix-metrics``. Nothing
   here passes it, and a fixture repo is compared byte-for-byte before
   and after a run.
2. **It never reports a false green.** A repo with no snapshot, no
   validator, or an unreadable one must come back ``unavailable`` with a
   reason — the same distinction FEAT-0018 drew for the browsed repo,
   for the same reason: grey is honest, green is a lie.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from project_os_cockpit import fleet_validate
from project_os_cockpit.validation import validate_repo

REPO_ROOT = Path(__file__).resolve().parents[1]


def _fingerprint(root: Path) -> dict[str, tuple[float, str]]:
    """Every file's mtime and content hash, recursively."""
    out: dict[str, tuple[float, str]] = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            p = Path(dirpath) / name
            try:
                out[str(p.relative_to(root))] = (
                    p.stat().st_mtime,
                    hashlib.sha256(p.read_bytes()).hexdigest(),
                )
            except OSError:
                continue
    return out


def _clone_repo(tmp_path: Path) -> Path:
    """A working copy of this repo's docs corpus — a real, valid one."""
    dst = tmp_path / "clone"
    dst.mkdir()
    shutil.copy2(REPO_ROOT / "SNAPSHOT.yaml", dst / "SNAPSHOT.yaml")
    shutil.copytree(REPO_ROOT / "docs", dst / "docs")
    shutil.copytree(REPO_ROOT / "tools", dst / "tools")
    return dst


def test_validating_a_repo_does_not_modify_it(tmp_path: Path) -> None:
    """Read-only, asserted over a corpus the write path WOULD change.

    The first version of this cloned a *clean* corpus, where `fix_metrics`
    would rewrite nothing even if `--fix-metrics` were passed — so the
    byte-for-byte comparison could not fail and the argv guard was doing
    all the work (PHASE-013 review, F5). The fixture now carries a real
    metrics mismatch, which is exactly what the write path exists to
    correct, so passing the flag makes this test go red.
    """
    repo = _clone_repo(tmp_path)
    _induce_metrics_drift(repo)
    before = _fingerprint(repo)
    assert before, "fixture is empty — the assertion below would be vacuous"

    report = validate_repo(repo)
    assert report["state"] == "failing", (
        "the fixture must be one the write path would change, or this "
        "assertion is vacuous"
    )

    after = _fingerprint(repo)
    changed = {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
    assert not changed, (
        "validating a repo modified it — fleet health runs this in repos "
        f"this app does not own: {sorted(changed)}"
    )


def test_the_cold_pass_command_never_carries_fix_metrics(
    tmp_path: Path, monkeypatch
) -> None:
    """`--fix-metrics` is the validator's only write path.

    Asserted against the argv the code actually builds, captured at the
    `subprocess.run` boundary. The first cut of this grepped the source
    for the flag and failed on the *docstring* explaining that the flag
    is not passed — the string-shaped-guard failure this repo keeps
    relearning, arriving this time as a false positive rather than a
    false green.
    """
    import project_os_cockpit.validation as validation

    seen: list[list[str]] = []
    real_run = validation.subprocess.run

    def spy(cmd, *args, **kwargs):  # type: ignore[no-untyped-def]
        seen.append(list(cmd))
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(validation.subprocess, "run", spy)
    validate_repo(_clone_repo(tmp_path))

    assert seen, "the validator was never invoked — this assertion would be vacuous"
    for cmd in seen:
        assert "--fix-metrics" not in cmd, (
            f"the cold pass would rewrite another repo's SNAPSHOT.yaml: {cmd}"
        )
        assert "--repo-root" in cmd, "the validator must be aimed explicitly, not by cwd"


def test_a_repo_without_a_snapshot_is_unavailable_not_ok(tmp_path: Path) -> None:
    """No snapshot → grey with a reason, never green."""
    empty = tmp_path / "not-a-project"
    (empty / "docs").mkdir(parents=True)
    line = fleet_validate.summarise(empty)
    assert line["state"] == "unavailable"
    assert line["state"] != "ok", "a repo with nothing to validate must not read as passing"
    assert line.get("detail"), "unavailable without a reason is indistinguishable from a bug"


def _induce_metrics_drift(repo: Path) -> None:
    """A real METRICS error — the one `fix_metrics` exists to rewrite."""
    snap = repo / "SNAPSHOT.yaml"
    text = snap.read_text(encoding="utf-8")
    marker = "  counts:\n"
    assert marker in text
    head, _, tail = text.partition(marker)
    lines = tail.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip().startswith("tasks_total:"):
            indent = ln[: len(ln) - len(ln.lstrip())]
            lines[i] = f"{indent}tasks_total: 99999"
            break
    else:
        raise AssertionError("no tasks_total in metrics.counts")
    snap.write_text(head + marker + "\n".join(lines), encoding="utf-8")


def test_the_fixture_is_one_the_write_path_would_change(tmp_path: Path) -> None:
    """Guards the guard above: prove `--fix-metrics` rewrites THIS fixture.

    Without this, `test_validating_a_repo_does_not_modify_it` could go
    quietly vacuous again — a future fixture change that stops producing a
    metrics mismatch would leave it passing for the wrong reason.
    """
    import subprocess
    import sys

    repo = _clone_repo(tmp_path)
    _induce_metrics_drift(repo)
    before = _fingerprint(repo)
    subprocess.run(
        [sys.executable, str(repo / "tools" / "scripts" / "validate-docs.py"),
         "--repo-root", str(repo), "--fix-metrics"],
        capture_output=True, text=True, timeout=120, cwd=str(repo),
    )
    assert _fingerprint(repo) != before, (
        "--fix-metrics changed nothing, so the read-only test above proves "
        "nothing about the flag"
    )


def test_a_drifting_repo_reports_its_own_error_count(tmp_path: Path) -> None:
    """Counts are per-repo, and a real defect moves them."""
    repo = _clone_repo(tmp_path)
    clean = fleet_validate.summarise(repo)
    assert clean["state"] == "ok", clean

    _induce_metrics_drift(repo)
    drifted = fleet_validate.summarise(repo)
    assert drifted["state"] == "failing"
    assert drifted["errors"] >= 1
    assert drifted["errors"] > clean["errors"]


def test_the_module_entrypoint_emits_one_json_line_per_repo(
    tmp_path: Path, capsys
) -> None:
    """The wire format the desktop shell parses."""
    repo = _clone_repo(tmp_path)
    missing = tmp_path / "nope"
    rc = fleet_validate.main([str(repo), str(missing)])
    assert rc == 0, "one unreadable repo must not kill the batch"
    lines = [json.loads(l) for l in capsys.readouterr().out.splitlines() if l.strip()]
    assert len(lines) == 2
    assert lines[0]["root"] == str(repo)
    assert lines[0]["state"] == "ok"
    assert lines[1]["state"] == "unavailable"
    for line in lines:
        # Counts, not lists: ten repos' full violation lists across a
        # pipe is a lot of bytes for a badge that shows a number.
        assert isinstance(line["errors"], int)
        assert isinstance(line["warnings"], int)


def test_the_entrypoint_runs_as_a_subprocess(tmp_path: Path) -> None:
    """`python -m project_os_cockpit.fleet_validate` is how main spawns it."""
    repo = _clone_repo(tmp_path)
    proc = subprocess.run(
        [sys.executable, "-m", "project_os_cockpit.fleet_validate", str(repo)],
        capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout.strip().splitlines()[0])
    assert payload["state"] == "ok"


def test_the_repos_own_validator_is_preferred_over_the_bundled_copy(
    tmp_path: Path,
) -> None:
    """The decision TASK-0249 owns, pinned.

    FEAT-0028's brief plan says "the repo's validate-docs.py";
    `validate-fleet.sh` says it uses THIS repo's "for uniform
    semantics". They give different badges for the same repo. The
    resolution is per-repo, matching `ValidationRunner`'s locate order
    and its stated reason — a repo's own copy honours its own
    STATUSES.md, so a red badge its own CI would not raise is a false
    positive.
    """
    from project_os_cockpit.validation import BUNDLED_VALIDATOR, ValidationRunner

    repo = _clone_repo(tmp_path)
    own = repo / "tools" / "scripts" / "validate-docs.py"
    assert own.is_file(), "fixture should carry its own validator"
    assert ValidationRunner(repo).locate_validator() == own

    own.unlink()
    assert ValidationRunner(repo).locate_validator() == BUNDLED_VALIDATOR, (
        "a repo predating the validator must still get a signal, not nothing"
    )


def test_the_summary_says_which_validator_produced_it(tmp_path: Path) -> None:
    """PHASE-013 review, F4.

    TASK-0249's recommendation was per-repo "with the repo's validator
    version surfaced so uniformity is visible rather than assumed", and
    the implementation dropped that clause. The per-repo choice is only
    defensible if a reader can see it was made — otherwise a fleet of
    mixed template versions looks uniform, which is the assumption
    ISS-0026 was filed for.
    """
    repo = _clone_repo(tmp_path)
    assert fleet_validate.summarise(repo)["validator"] == "repo"

    (repo / "tools" / "scripts" / "validate-docs.py").unlink()
    assert fleet_validate.summarise(repo)["validator"] == "bundled", (
        "a repo falling back to the cockpit's bundled validator must say so"
    )
