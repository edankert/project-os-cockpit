"""`tools/scripts/merge-checks-into-tests.py` — the ADR-0031 migration.

Written after independent review found the script had **zero** coverage while
being a line-regex frontmatter editor that unlinks its inputs. Every case here
is one the reviewer named: the refusals must fire before the first write, and a
fingerprint that guards six of twenty-two fields is a fingerprint that passes
while data is lost.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "tools" / "scripts" / "merge-checks-into-tests.py"


def _repo(tmp_path: Path, notes: dict[str, str]) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "tests" / "acceptance").mkdir(parents=True)
    (root / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
    for name, text in notes.items():
        (root / "docs" / "tests" / "acceptance" / name).write_text(text, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "seed"], cwd=root, check=True)
    return root


def _run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(root), *args],
        capture_output=True, text=True, timeout=120,
        cwd=str(REPO_ROOT), env={"PATH": "/usr/bin:/bin", "HOME": str(root)})


def _check(cid: str, extra: str = "") -> str:
    return (f'---\ntype: "[[check]]"\nid: {cid}\naliases: ["{cid}"]\n'
            f'title: "A check"\nstatus: active\ntier: 1\narea: "Area"\n'
            f'section: "1.1"\nordinal: 10\nmark: "x"\n{extra}---\n\nwalk it\n')


def test_a_frontmatterless_note_is_refused_before_anything_is_written(tmp_path) -> None:
    """The worst case the reviewer found: it would be destroyed silently.

    A line-regex editor writes `type: ...` into a file with no frontmatter and
    produces something the reader cannot parse — and the fingerprint stays green,
    because a note the reader could never see is missing from both sides of it.
    """
    root = _repo(tmp_path, {
        "CHK-0001-Good.md": _check("CHK-0001"),
        "CHK-0002-Bad.md": "no frontmatter here at all\n",
    })
    proc = _run(root, "--write")
    assert proc.returncode == 1, proc.stdout
    assert "REFUSED" in proc.stdout and "no frontmatter" in proc.stdout
    # And nothing moved: the refusal is a precondition, not a report.
    names = {p.name for p in (root / "docs" / "tests" / "acceptance").iterdir()}
    assert names == {"CHK-0001-Good.md", "CHK-0002-Bad.md"}


def test_block_style_aliases_are_refused(tmp_path) -> None:
    """`aliases:` on its own line with entries beneath it.

    The editor rewrites the `aliases:` LINE, which for a block-style list means
    the entries below it are orphaned and the YAML stops parsing.
    """
    root = _repo(tmp_path, {
        "CHK-0001-Block.md": _check("CHK-0001").replace(
            'aliases: ["CHK-0001"]', 'aliases:\n  - "CHK-0001"'),
    })
    proc = _run(root, "--write")
    assert proc.returncode == 1
    assert "block-style aliases" in proc.stdout


def test_uncommitted_acceptance_notes_are_refused(tmp_path) -> None:
    """`merged_from:` records a sha, and if the notes are uncommitted it is a lie.

    The previous migration hit this and fixed it by stamping "(uncommitted at
    migration)"; this one refuses instead, because a migration is a moment
    somebody can choose.
    """
    root = _repo(tmp_path, {"CHK-0001-Good.md": _check("CHK-0001")})
    (root / "docs" / "tests" / "acceptance" / "CHK-0002-New.md").write_text(
        _check("CHK-0002"), encoding="utf-8")
    proc = _run(root, "--write")
    assert proc.returncode == 1
    assert "acceptance notes are uncommitted" in proc.stdout


def test_unrelated_dirt_does_not_block_the_migration(tmp_path) -> None:
    """Scoped to the notes, deliberately.

    `your-trainer` carries ~100 uncommitted files of unrelated work at any
    moment. A whole-tree refusal there is an automation people disable, and a
    whole-tree *stage* is the thing CLAUDE.md forbids by name. What
    `merged_from:` claims is that its sha contains THESE checks; a dirty Kotlin
    file says nothing about that.
    """
    root = _repo(tmp_path, {"CHK-0001-Good.md": _check("CHK-0001")})
    (root / "unrelated.kt").write_text("fun main() {}\n", encoding="utf-8")
    proc = _run(root, "--write")
    assert proc.returncode == 0, proc.stdout
    assert "parity holds" in proc.stdout


def test_a_clean_migration_renames_and_keeps_the_old_id_reachable(tmp_path) -> None:
    """The happy path, asserted on what a reader can still find."""
    root = _repo(tmp_path, {
        "CHK-0001-Serve.md": _check("CHK-0001"),
        "CHK-0002-Reload.md": _check("CHK-0002").replace('section: "1.1"', 'section: "1.2"'),
    })
    proc = _run(root, "--write")
    assert proc.returncode == 0, proc.stdout
    acc = root / "docs" / "tests" / "acceptance"
    assert not list(acc.glob("CHK-*.md"))
    migrated = sorted(p.name for p in acc.glob("TST-*.md"))
    assert migrated == ["TST-0001-Serve.md", "TST-0002-Reload.md"]
    first = (acc / "TST-0001-Serve.md").read_text(encoding="utf-8")
    assert 'type: "[[test]]"' in first
    assert "level: acceptance" in first
    assert '"CHK-0001"' in first, "the old id must stay reachable as an alias"
    assert "merged_from:" in first
    assert "parity holds" in proc.stdout


def test_the_fingerprint_guards_more_than_the_gate_fields(tmp_path) -> None:
    """A fingerprint of six fields passes while eleven others are dropped.

    Asserted on the fingerprint itself rather than by breaking the script,
    because the property is *what it would notice*, and the cheapest way to
    lose a field is to add one the comparison never learned about.
    """
    sys.path.insert(0, str(SCRIPT.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("merge_checks", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    root = _repo(tmp_path, {"CHK-0001-Serve.md": _check("CHK-0001")})
    suite = module.read_suite(root / "docs")
    keys = set(module.fingerprint(suite))
    for field in ("areas", "sections", "verdicts", "automation", "burden",
                  "evidence", "invalidated"):
        assert field in keys, f"the fingerprint would not notice {field} being lost"
