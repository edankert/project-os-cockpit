#!/usr/bin/env python3
"""Move a fleet repo onto the upstream project-os validator (TASK-0580, FEAT-0143).

Every `SNAPSHOT.yaml`-bearing repo under `~/Dev/repos` carries its own copy of
`tools/scripts/validate-docs.py`. Four of them are ~780 lines behind upstream and
so run **none** of the acceptance rules -- `_acceptance_is_settled` occurs zero
times in all four (ISS-0209). `sync-project-os.sh` will not fix that on its own:
it classifies the file as DIVERGED (both sides moved since the recorded baseline)
and skips it, which is how routine syncs kept reporting success while the fleet
fell further behind.

The census (TASK-0579) established that the reconciliation those newer rules
demand is **two rules and 1086 findings across four repos, with nothing else at
all**:

    PARENT-BACKLINK        1044   a child names `parent: FEAT-X`, and FEAT-X's
                                  `tasks:` / `issues:` does not name it back
    SNAPSHOT-MEMBERSHIP      42   the snapshot's copy of that same list disagrees
                                  with the note's

Those are one relationship seen from its two ends, so this script performs one
operation: **read the children, write the parents, then make the snapshot agree
with the notes.** ADR-0009 settles the direction -- the note is the authored
source, so the snapshot is what gets corrected.

Stdlib only, like every other script under tools/scripts/.

Usage:
    migrate-fleet-validator.py <repo> [--upstream PATH] [--dry-run]
                               [--no-sync] [--no-snapshot]
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_UPSTREAM = Path.home() / "Dev" / "repos" / "project-os"

#: Back-reference fields, keyed by the child's note type. The SET matches
#: PARENT-BACKLINK's `back_fields`; the ORDER deliberately does not. Upstream
#: writes `("fixes", "issues")` and reads them as a union, so order is
#: immaterial there -- here the first entry is the field this script WRITES, and
#: `issues:` is the one every note in this fleet actually uses. The rest are
#: read as already-satisfying.
BACK_FIELDS = {"task": ("tasks",), "issue": ("issues", "fixes")}


# ---------------------------------------------------------------- validator

def load_validator(upstream_root: Path):
    """Import upstream's validate-docs.py as a module.

    Deliberate: this script and the rule it repairs then share one
    `build_note_index`, one `extract_ids` and one `note_type`. A second
    implementation here would be a second opinion about which notes exist, and
    the failure mode of that is a migration that reports success against rules
    it read differently from the validator that will judge it.
    """
    path = upstream_root / "tools" / "scripts" / "validate-docs.py"
    if not path.is_file():
        raise SystemExit("migrate-fleet-validator: no validator at %s" % path)
    spec = importlib.util.spec_from_file_location("_upstream_validate_docs", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_upstream_validate_docs"] = module
    spec.loader.exec_module(module)
    return module


def prefix_of(v, the_id):
    """The ID family of `the_id`, or "".

    A local copy because upstream's is nested inside `validate_traceability` and
    so cannot be imported. The body is three lines and is driven off the
    validator's own `ID_RE`, so the two cannot disagree about what an id is.
    """
    m = v.ID_RE.match(the_id)
    return m.group(1) if m else ""


# ------------------------------------------------------------ frontmatter io

FM_DELIM = "---"


def split_frontmatter(text: str):
    """(before, body_of_frontmatter, after) or None when there is no frontmatter.

    `before` is the opening delimiter line, `after` starts at the closing one.
    """
    body = text.lstrip("\ufeff")
    lead = len(text) - len(body)
    # CRLF and a BOM are both present in the fleet (`articles`, and one PLAN.md
    # in `your-sudoku`). Refusing them here raised `ValueError` out of
    # `apply_plan`, which writes note by note -- so the crash landed AFTER the
    # forced validator copy and left a half-migrated corpus.
    if not (body.startswith(FM_DELIM + "\n") or body.startswith(FM_DELIM + "\r\n")):
        return None
    end = body.find("\n" + FM_DELIM, len(FM_DELIM))
    if end == -1:
        return None
    head_len = body.index("\n", len(FM_DELIM)) + 1
    return text[:lead + head_len], body[head_len:end + 1], body[end + 1:]


def _key_extent(lines, key):
    """(start, stop) of a top-level `key:` and its indented continuation, or None."""
    pattern = re.compile(r"^%s\s*:" % re.escape(key))
    for i, line in enumerate(lines):
        if not pattern.match(line):
            continue
        j = i + 1
        # A multi-line flow list closes at whatever column its author chose, and
        # three notes in `your-trainer` close it at column 0. Consuming only the
        # INDENTED continuation left the `]` behind as an orphan line, turning a
        # rewrite into frontmatter that does not parse -- ISS-0260's defect,
        # reintroduced by the tool that found it. Balance the brackets first.
        depth = lines[i].count("[") - lines[i].count("]")
        while depth > 0 and j < len(lines):
            depth += lines[j].count("[") - lines[j].count("]")
            j += 1
        while j < len(lines) and (lines[j].startswith((" ", "\t")) or not lines[j].strip()):
            # A blank line only continues the block if something indented follows.
            if not lines[j].strip():
                k = j
                while k < len(lines) and not lines[k].strip():
                    k += 1
                if k >= len(lines) or not lines[k].startswith((" ", "\t")):
                    break
            j += 1
        return i, j
    return None


def render_list(key: str, links) -> str:
    """A block sequence, always.

    Block rather than flow because `your-trainer` has a feature owning 100+
    tasks and a flow list of those is a single unreadable line; and because the
    fleet's own notes already use block sequences for `source:` and `related:`.
    Both YAML readers in the validator (PyYAML and its `parse_yaml_subset`
    fallback) accept it.
    """
    if not links:
        return "%s: []\n" % key
    return "%s:\n%s" % (key, "".join('  - "[[%s]]"\n' % l for l in links))


def set_frontmatter_list(text: str, key: str, links, id_re) -> str:
    """Set a top-level frontmatter list, returning the text unchanged when the
    ID set already matches.

    The unchanged-return is the point, not an optimisation. This runs over 3993
    hand-written notes; a rewrite that reorders keys or reflows a string would
    be a silent whole-corpus diff wearing a one-line change's clothes. So the
    comparison is on IDs, and only a genuine difference is allowed to touch
    bytes (TST-0080).
    """
    parts = split_frontmatter(text)
    if parts is None:
        raise ValueError("no frontmatter")
    head, fm, tail = parts
    lines = fm.splitlines(keepends=True)
    extent = _key_extent(lines, key)
    wanted_ids = [_id_of(l, id_re) for l in links]
    if extent is not None:
        current = "".join(lines[extent[0]:extent[1]])
        have = set(id_re.findall(current.split(":", 1)[1]))
        have = set("%s-%s" % m for m in have)
        if have == set(wanted_ids):
            return text
        lines[extent[0]:extent[1]] = [render_list(key, links)]
    else:
        if not wanted_ids:
            return text
        lines.append(render_list(key, links))
    return head + "".join(lines) + tail


def _id_of(link: str, id_re) -> str:
    m = id_re.search(link)
    return "%s-%s" % (m.group(1), m.group(2)) if m else link


# ------------------------------------------------------------- reconcile plan

class Plan:
    def __init__(self):
        self.additions = {}     # (feature_id, field) -> [link stems]
        self.unclaimed = []     # (feature_id, field, id) already listed, nothing claims it
        self.dangling = []      # (child_id, parent_id) parent note does not exist


def plan_backlinks(v, note_index) -> Plan:
    """What each feature note must name, computed from the children that declare it.

    Add-only by construction. An entry already in a feature's list that no child
    claims is REPORTED and kept: PARENT-BACKLINK only ever fires on a missing
    back-reference, so removing is a judgement this script has no basis for and
    is the direction that loses information.
    """
    plan = Plan()
    claims = {}                 # (parent_id, field) -> {child_id: stem}
    for child_id, entry in sorted(note_index.items()):
        c_path, c_fm = entry
        fields = BACK_FIELDS.get(v.note_type(c_fm))
        if not fields:
            continue
        for parent_id in v.extract_ids((c_fm or {}).get("parent")):
            if prefix_of(v, parent_id) != "FEAT":
                continue
            if parent_id not in note_index:
                plan.dangling.append((child_id, parent_id))
                continue
            claims.setdefault((parent_id, fields[0]), {})[child_id] = c_path.stem

    for (parent_id, field), children in sorted(claims.items()):
        p_fm = note_index[parent_id][1] or {}
        # Satisfaction is judged across EVERY field the rule accepts -- an issue
        # already named in `fixes:` satisfies PARENT-BACKLINK and must not be
        # copied into `issues:` as well.
        named_anywhere = set()
        for f in BACK_FIELDS[_child_type_for(field)]:
            named_anywhere.update(v.extract_ids(p_fm.get(f)))
        if set(children) <= named_anywhere:
            continue
        # What gets WRITTEN is the target field's own contents plus the
        # claimants it is missing. Ordered by id, so a second run produces the
        # same bytes as the first.
        stems = dict(children)
        for existing in sorted(v.extract_ids(p_fm.get(field))):
            if existing in stems:
                continue
            note = note_index.get(existing)
            stems[existing] = note[0].stem if note else existing
        plan.additions[(parent_id, field)] = [stems[i] for i in sorted(stems)]

    # Anything named on a feature that no child claims.
    for feat_id, (_p, p_fm) in sorted(note_index.items()):
        if v.note_type(p_fm) != "feature":
            continue
        for field, ctype in (("tasks", "task"), ("issues", "issue"), ("fixes", "issue")):
            for named_id in v.extract_ids((p_fm or {}).get(field)):
                if prefix_of(v, named_id) != {"task": "TASK", "issue": "ISS"}[ctype]:
                    continue
                child = note_index.get(named_id)
                if child is None:
                    continue        # DANGLING-LINK owns the missing-note case
                if feat_id not in v.extract_ids((child[1] or {}).get("parent")):
                    plan.unclaimed.append((feat_id, field, named_id))
    return plan


def _child_type_for(field):
    return "task" if field == "tasks" else "issue"


def apply_plan(v, note_index, plan: Plan, dry_run: bool):
    """Returns (written, unhandled). A note the writer cannot read is REPORTED
    and skipped rather than raised: this loop writes file by file, after
    `run_sync --force` has already replaced the validator, so an exception
    halfway through leaves a corpus that is half migrated and a repo that
    cannot commit."""
    written, unhandled = [], []
    for (feat_id, field), links in sorted(plan.additions.items()):
        path = note_index[feat_id][0]
        text = path.read_text(encoding="utf-8")
        try:
            new = set_frontmatter_list(text, field, links, v.ID_RE)
        except ValueError as exc:
            unhandled.append((feat_id, field, path, str(exc)))
            continue
        if new == text:
            continue
        written.append((feat_id, field, len(links), path))
        if not dry_run:
            path.write_text(new, encoding="utf-8")
    return written, unhandled


# --------------------------------------------------------------- snapshot io

def planned_tasks(v, plan: Plan):
    """feature id -> the TASK ids its note will hold once the plan is applied."""
    out = {}
    for (feat_id, field), links in plan.additions.items():
        if field != "tasks":
            continue
        out[feat_id] = sorted({i for i in (_id_of(l, v.ID_RE) for l in links)
                               if prefix_of(v, i) == "TASK"})
    return out


def reconcile_snapshot(v, repo_root: Path, note_index, dry_run: bool, planned=None):
    """Make `items.features.*.tasks` equal the note's TASK ids.

    Textual and per-entry, not a YAML round-trip: `SNAPSHOT.yaml` in these repos
    carries comments that are load-bearing prose (`# Pruned: FEAT-0001 through
    FEAT-0021`), and a dump would drop every one of them.

    `planned` is what a `--dry-run` reads instead of the notes. Without it the
    dry run reconciles against notes the dry run did not write, and reports zero
    snapshot changes where the real run makes several -- a preview that is
    silent about half the work is the reports-success-because-it-could-not-look
    failure this whole phase is about.
    """
    snap_path = repo_root / "SNAPSHOT.yaml"
    if not snap_path.is_file():
        return []
    text = snap_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    try:
        start = next(i for i, l in enumerate(lines) if l.rstrip("\n") == "  features:")
    except StopIteration:
        return []
    changes = []
    i = start + 1
    while i < len(lines):
        line = lines[i]
        if line.strip() and not line.startswith("    "):
            break                                   # left the features block
        flow = re.match(r"^    ([A-Z]+-\d+):\s*\{(.*)\}\s*$", line)
        if flow:
            # `your-trainer` writes every feature as a one-line flow mapping:
            #     FEAT-0020: { file: "...", title: "...", status: backlog }
            # The block form below never matched it, so the first run of this
            # tool reported "0 snapshot entries" and left 33 SNAPSHOT-MEMBERSHIP
            # errors standing in the largest repo in the fleet.
            feat_id = flow.group(1)
            note = note_index.get(feat_id)
            if note is None:
                i += 1
                continue
            want = (planned or {}).get(feat_id)
            if want is None:
                want = sorted({t for t in v.extract_ids((note[1] or {}).get("tasks"))
                               if prefix_of(v, t) == "TASK"})
            inner = flow.group(2)
            existing = re.search(r"tasks\s*:\s*\[[^\]]*\]", inner)
            have = sorted({t for t in v.extract_ids(existing.group(0) if existing else "")
                           if prefix_of(v, t) == "TASK"})
            if have == want:
                i += 1
                continue
            rendered = "tasks: [%s]" % ", ".join('"%s"' % t for t in want)
            if existing:
                inner = inner[:existing.start()] + rendered + inner[existing.end():]
            else:
                inner = "%s, %s " % (inner.rstrip().rstrip(","), rendered)
            lines[i] = "    %s: {%s}\n" % (feat_id, inner)
            changes.append((feat_id, len(have), len(want)))
            i += 1
            continue
        m = re.match(r"^    ([A-Z]+-\d+):\s*$", line)
        if not m:
            i += 1
            continue
        feat_id = m.group(1)
        j = i + 1
        while j < len(lines) and (lines[j].startswith("      ") or not lines[j].strip()):
            j += 1
        note = note_index.get(feat_id)
        if note is None:
            i = j
            continue
        want = (planned or {}).get(feat_id)
        if want is None:
            want = sorted({t for t in v.extract_ids((note[1] or {}).get("tasks"))
                           if prefix_of(v, t) == "TASK"})
        k = next((n for n in range(i + 1, j)
                  if re.match(r"^      tasks\s*:", lines[n])), None)
        # Read the whole value, not just its first line: a block sequence spans
        # several, and reading only line k would report an empty list and
        # rewrite a correct entry on every run.
        k_end = k
        if k is not None:
            k_end = k + 1
            while k_end < j and lines[k_end].startswith("        "):
                k_end += 1
        have = (sorted({t for t in v.extract_ids("".join(lines[k:k_end]))
                        if prefix_of(v, t) == "TASK"}) if k is not None else [])
        if have == want:
            i = j
            continue
        rendered = "      tasks: [%s]\n" % ", ".join('"%s"' % t for t in want)
        if k is not None:
            lines[k:k_end] = [rendered]
            j -= (k_end - k) - 1
        elif want:
            lines.insert(i + 1, rendered)
            j += 1
        changes.append((feat_id, len(have), len(want)))
        i = j
    if changes and not dry_run:
        snap_path.write_text("".join(lines), encoding="utf-8")
    return changes


# ------------------------------------------------------------------- syncing

def superset_report(repo_root: Path, upstream_root: Path):
    """Lines a repo added to a template-owned file since its baseline that are
    NOT in upstream today -- i.e. what `--force` would discard.

    Reported rather than enforced. The census found 32 such lines in `your-sudoku`
    and `your-trainer` and every one is ADR-0030's `CHK`/`checks` collection,
    which ADR-0031 deliberately retired. "Absent from upstream" and "lost" are
    not the same thing, and only a person can tell them apart -- so this prints
    and does not decide.
    """
    state = repo_root / ".project-os-sync"
    baseline = None
    if state.is_file():
        m = re.search(r'baseline_sha:\s*"([0-9a-f]+)"', state.read_text(encoding="utf-8"))
        baseline = m.group(1) if m else None
    rel = "tools/scripts/validate-docs.py"
    current = repo_root / rel
    if not current.is_file():
        return baseline, None
    up = (upstream_root / rel).read_text(encoding="utf-8")
    up_lines = {l.strip() for l in up.splitlines() if l.strip()}
    if not baseline:
        return baseline, None
    proc = subprocess.run(["git", "-C", str(upstream_root), "show", "%s:%s" % (baseline, rel)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return baseline, None
    base_lines = {l.strip() for l in proc.stdout.splitlines() if l.strip()}
    added = [l.strip() for l in current.read_text(encoding="utf-8").splitlines()
             if l.strip() and l.strip() not in base_lines]
    return baseline, sorted({l for l in added if l not in up_lines})


#: Path fragments the sync must never carry downstream. `sync-project-os.py`
#: walks upstream's FILESYSTEM rather than its index, so anything sitting in a
#: template-owned directory is copied -- including `tools/scripts/__pycache__/`,
#: which is gitignored upstream and therefore invisible to every reviewer of the
#: sync. Filed as ISS-0257; pruned here so the migration does not deposit one
#: byte of upstream's build output in four repos on the way past.
ARTEFACT_FRAGMENTS = ("__pycache__", ".pytest_cache", ".egg-info")


def prune_artefacts(repo_root: Path, synced_paths, dry_run: bool):
    removed = []
    for rel in synced_paths:
        if not any(frag in rel for frag in ARTEFACT_FRAGMENTS):
            continue
        target = repo_root / rel
        if not target.exists():
            continue
        removed.append(rel)
        if not dry_run:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
    return removed


def parse_synced_paths(output: str):
    """Relative paths the sync said it wrote."""
    out = []
    for line in output.splitlines():
        line = line.replace("[dry-run]", "").strip()
        if not line.startswith("synced "):
            continue
        rest = line[len("synced "):].strip()
        out.append(rest.split(" (")[0].strip())
    return out


def run_sync(repo_root: Path, upstream_root: Path, dry_run: bool):
    # UPSTREAM's sync script, not the downstream copy. The downstream one is
    # itself a template-owned file this migration is here to replace, and a repo
    # whose sync script predates the manifest cannot read the manifest that says
    # what it owns.
    cmd = ["python3", str(upstream_root / "tools" / "scripts" / "sync-project-os.py"),
           str(upstream_root), "--repo-root", str(repo_root), "--force"]
    if dry_run:
        cmd.append("--dry-run")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr)


# ---------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="Fleet repo to migrate")
    ap.add_argument("--upstream", default=str(DEFAULT_UPSTREAM))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-sync", action="store_true", help="Reconcile only; do not copy template files")
    ap.add_argument("--no-snapshot", action="store_true", help="Leave SNAPSHOT.yaml alone")
    args = ap.parse_args(argv)

    repo_root = Path(args.repo).expanduser().resolve()
    upstream_root = Path(args.upstream).expanduser().resolve()
    if not (repo_root / "SNAPSHOT.yaml").is_file():
        raise SystemExit("migrate-fleet-validator: %s has no SNAPSHOT.yaml" % repo_root)

    v = load_validator(upstream_root)
    tag = "[dry-run] " if args.dry_run else ""
    print("%smigrate-fleet-validator: %s <- %s" % (tag, repo_root.name, upstream_root))

    baseline, orphans = superset_report(repo_root, upstream_root)
    print("%s  baseline %s; validator lines added downstream and absent from upstream: %s"
          % (tag, baseline or "none", "unknown" if orphans is None else len(orphans)))
    for line in (orphans or [])[:40]:
        print("%s    ABSENT-UPSTREAM  %s" % (tag, line[:140]))

    if not args.no_sync:
        rc, out = run_sync(repo_root, upstream_root, args.dry_run)
        for line in out.splitlines():
            print("%s  %s" % (tag, line))
        if rc != 0:
            raise SystemExit("migrate-fleet-validator: sync failed (rc=%d)" % rc)
        for rel in prune_artefacts(repo_root, parse_synced_paths(out), args.dry_run):
            print("%s  PRUNED    %s (build artefact the sync carried over; ISS-0257)" % (tag, rel))

    note_index, _claimants = v.build_note_index(repo_root / "docs")
    plan = plan_backlinks(v, note_index)
    written, unhandled = apply_plan(v, note_index, plan, args.dry_run)
    for feat_id, field, path, why in unhandled:
        print("%s  UNREADABLE %s `%s:` needs an entry and its frontmatter could not be "
              "read (%s: %s) -- skipped, fix by hand"
              % (tag, feat_id, field, path.relative_to(repo_root), why))
    for feat_id, field, n, path in written:
        print("%s  BACKLINK  %s `%s:` -> %d entr%s (%s)"
              % (tag, feat_id, field, n, "y" if n == 1 else "ies", path.relative_to(repo_root)))
    for child_id, parent_id in plan.dangling:
        print("%s  DANGLING  %s declares parent: %s and no such note exists -- left alone"
              % (tag, child_id, parent_id))
    for feat_id, field, named_id in plan.unclaimed:
        print("%s  UNCLAIMED %s `%s:` names %s, which does not declare it as parent -- kept"
              % (tag, feat_id, field, named_id))

    snap_changes = []
    if not args.no_snapshot:
        # Re-read: the notes just changed, and the snapshot must follow THEM.
        note_index, _ = v.build_note_index(repo_root / "docs")
        snap_changes = reconcile_snapshot(v, repo_root, note_index, args.dry_run,
                                          planned_tasks(v, plan) if args.dry_run else None)
        for feat_id, before, after in snap_changes:
            print("%s  SNAPSHOT  %s tasks: %d -> %d" % (tag, feat_id, before, after))

    print("%smigrate-fleet-validator: %d note(s) rewritten, %d snapshot entr%s, "
          "%d dangling, %d unclaimed, %d unreadable"
          % (tag, len(written), len(snap_changes),
             "y" if len(snap_changes) == 1 else "ies",
             len(plan.dangling), len(plan.unclaimed), len(unhandled)))
    return 1 if unhandled else 0


if __name__ == "__main__":
    sys.exit(main())
