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


# ---- git standing (FEAT-0055 / TASK-0265) ----------------------------

def test_remote_kind_is_derived_from_the_url_not_configured() -> None:
    """This decides whether anything may push, so it must not be a setting.

    `your-applications.com`'s only remote is a server path; classifying
    it wrong deploys a live website.
    """
    from project_os_cockpit.fleet_validate import remote_kind

    assert remote_kind("https://github.com/edankert/x.git") == "backup"
    assert remote_kind("git@github.com:edankert/x.git") == "backup"
    assert remote_kind("https://gitlab.com/e/x.git") == "backup"
    assert remote_kind("root@76.13.51.7:/home/edankert/repos/x.git") == "deploy"
    assert remote_kind("/srv/git/x.git") == "deploy"
    assert remote_kind("") == "none"


def test_an_unrecognised_remote_is_deploy_not_backup() -> None:
    """The safe default for "I do not know what this is" is "do not
    publish to it". Getting this backwards publishes to something."""
    from project_os_cockpit.fleet_validate import remote_kind

    for weird in ("ssh://unknown.example/x.git", "file:///tmp/x.git",
                  "https://git.internal.example/x.git"):
        assert remote_kind(weird) == "deploy", weird


def test_no_upstream_is_not_up_to_date(tmp_path: Path) -> None:
    """`ahead: None` must be distinguishable from `ahead: 0`.

    Three fleet repos have no remote. Rendering that as up-to-date is
    the ISS-0065 failure — absence presented as health.
    """
    from project_os_cockpit.fleet_validate import git_standing

    repo = tmp_path / "r"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    standing = git_standing(repo)
    assert standing["ahead"] is None
    assert standing["remote_kind"] == "none"


def test_ahead_counts_unpushed_commits(tmp_path: Path) -> None:
    from project_os_cockpit.fleet_validate import git_standing

    bare = tmp_path / "b.git"
    repo = tmp_path / "r"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for k, v in (("user.email", "t@e.st"), ("user.name", "T")):
        subprocess.run(["git", "-C", str(repo), "config", k, v], check=True)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "one"], check=True)
    branch = subprocess.run(["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", str(bare)], check=True)
    subprocess.run(["git", "-C", str(repo), "push", "-q", "-u", "origin", branch], check=True)
    assert git_standing(repo)["ahead"] == 0

    (repo / "b.txt").write_text("b\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "two"], check=True)
    assert git_standing(repo)["ahead"] == 1


def test_the_entrypoint_block_stays_at_the_end_of_the_module() -> None:
    """`raise SystemExit(main())` mid-module stops execution there.

    Appending `git_standing` after that block bound nothing: `main()`
    ran before the definition was reached, and every repo reported
    `unavailable: NameError`. Importing the module hides it entirely —
    only the subprocess entrypoint sees it, which is why exactly one
    test caught it.
    """
    src = (REPO_ROOT / "src" / "project_os_cockpit" / "fleet_validate.py").read_text()
    after = src.split('if __name__ == "__main__":', 1)[1]
    leftover = [l for l in after.splitlines()
                if l.strip() and not l.strip().startswith(("raise SystemExit", "#"))]
    assert not leftover, (
        "code follows the entrypoint block and will never be reached by "
        f"`python -m`: {leftover}"
    )


def test_the_cold_pass_carries_a_digest_and_degrades_to_none(tmp_path: Path) -> None:
    """TASK-0419's payload half, asserted rather than eyeballed.

    Written at close-out: the task reached `done` with every Definition-of-Done
    box unticked and no test, and two of those boxes ask for exactly this —
    *"Asserted on the payload rather than eyeballed"* and *"a repo with no
    `docs/`, no git, or an unreadable watermark degrades to no digest rather
    than to a wrong one, and does not take the batch down with it."*

    The second clause is the one worth having. `_digest_counts` swallows every
    exception on purpose, so a regression there is silent by construction —
    it does not crash, it just quietly stops answering, and every card loses
    its since-line for a reason nobody can see.
    """
    from project_os_cockpit.fleet_validate import _digest_counts

    # No `docs/` at all — the cheapest degradation, and the one the batch hits
    # for any directory that is not a project.
    bare = tmp_path / "not-a-project"
    bare.mkdir()
    assert _digest_counts(bare) is None

    # `docs/` but no git: an index builds, the history does not.
    nogit = tmp_path / "nogit"
    (nogit / "docs").mkdir(parents=True)
    (nogit / "docs" / "a.md").write_text(
        '---\ntype: "[[task]]"\nid: TASK-0001\nstatus: done\n---\n\n# A\n')
    assert _digest_counts(nogit) is None

    # A real repo answers, with every field the card reads.
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "SNAPSHOT.yaml").write_text("project:\n  name: probe\n")
    (repo / "docs" / "a.md").write_text(
        '---\ntype: "[[task]]"\nid: TASK-0001\nstatus: done\n---\n\n# A\n')
    for args in (
        ("init", "-q", "--initial-branch=main", "."),
        ("config", "user.email", "t@example.com"),
        ("config", "user.name", "T"),
        ("add", "-A"),
        ("commit", "-qm", "TASK-0001: base"),
    ):
        subprocess.run(["git", "-C", str(repo), *args], check=False,
                       capture_output=True)

    digest = _digest_counts(repo)
    assert digest is not None, "a real repo with docs/ and git must answer"
    assert set(digest) == {"seen_at", "transitions", "needs_you", "computed_at"}, digest
    assert isinstance(digest["transitions"], int)
    assert isinstance(digest["needs_you"], int)


def test_one_bad_repo_does_not_take_the_cold_batch_down(
    tmp_path: Path, monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """The other half of TASK-0419's degradation box, pinned separately.

    Split out because the first test does not reach it: `Watermark._load`
    already swallows `OSError`, and a missing `docs/` returns before anything
    can raise — so narrowing `_digest_counts`'s `except Exception` to
    `except ValueError` left that test green. The clause being protected is
    *"does not take the batch down with it"*, and the only honest way to
    assert it is to make the call actually raise.
    """
    from project_os_cockpit import cockpit as _cockpit
    from project_os_cockpit.fleet_validate import _digest_counts

    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "a.md").write_text(
        '---\ntype: "[[task]]"\nid: TASK-0001\nstatus: done\n---\n\n# A\n')

    def boom(*a: object, **k: object) -> dict[str, object]:
        raise RuntimeError("this repo is having a bad day")

    monkeypatch.setattr(_cockpit, "digest_payload", boom)
    # No exception escapes, and the answer is *nothing* rather than a wrong
    # number — the whole reason this returns `None` instead of zeroes.
    assert _digest_counts(repo) is None
