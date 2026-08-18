---
type: "[[task]]"
id: TASK-0477
aliases: ["TASK-0477"]
title: "The merge migration script — note to note, parity asserted through the reader"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0119-The-Merge-Migration]]"]
parent: "[[FEAT-0119-The-Merge-Migration]]"
effort: M
depends: ["[[TASK-0476-The-Validator-Learns-The-Merged-Type]]"]
blocks: []
related: []
tests: []
---

# The merge migration script

`tools/scripts/merge-checks-into-tests.py`, modelled on `migrate-acceptance-checks.py` which did the document→note move. Per note: `type` becomes `[[test]]`, `level: acceptance` and `kind: manual` are set, `status: active` is set, and every check field is carried through unchanged. `migrated_from:` is preserved verbatim; `merged_from:` records the `CHK-*` id and the pre-merge sha.

**Parity is asserted through the loaded suite, never by counting files** ([[REQ-0038-Nothing-Is-Lost-In-The-Merge]]): note count, the full distribution of `mark:` values, the set of `covers:` targets and the gate's blocking figure, each compared before and after, per repo. A file-count match proves the script wrote as many notes as it read and nothing else — which is the lesson [[ISS-0175]] left.

Runs `--dry-run` by default and refuses to write without `--write`.

Done when: the script round-trips this repo's 34 in a scratch clone with every parity assertion green, and refuses on any mismatch rather than reporting it.

## Done

`tools/scripts/merge-checks-into-tests.py`. Per note: `type` → `[[test]]`, `level: acceptance`, `kind: manual`, `status: active`, every acceptance field carried through untouched, `migrated_from:` preserved verbatim and `merged_from:` added with the `CHK-*` id and the pre-merge sha.

**Parity is a fingerprint, not a count.** Note count, the full distribution of `mark:` values, the distribution of `tier:`, the complete set of `covers:` targets, the gate's blocking figure, and the sorted set of titles — compared before and after **through `acceptance.load`**, which is the reader every surface uses. `--write` prints `REFUSING to report success` and exits non-zero on any mismatch rather than reporting one.

`--dry-run` is the default; it refuses to write without `--write`.


## Corrected after independent review (2026-08-18)

The script had **zero test coverage** while being a line-regex frontmatter editor that unlinks its inputs — the review's sharpest finding about this task, and correct. Five defects, all fixed and all now guarded in `tests/test_merge_migration.py`:

- **The refusal fired after every file was written and every `CHK-*` unlinked** — a report, not a refusal. Preconditions now run before the first write.
- **A frontmatter-less note was destroyed while parity stayed green**, because a note the reader can never see is missing from both sides of the comparison. Refused.
- **Block-style `aliases:`** would have been rewritten into invalid YAML. Refused.
- **A dirty tree** would have stamped `merged_from:` with a sha that does not contain the notes — the exact defect TASK-0463 fixed in the previous migration. Refused.
- **The fingerprint guarded 6 of ~22 fields.** Now 13, including `area`, `burden`, `evidence`, `automation` and the verdict triple — a migration that silently dropped any of them used to pass.

And `_set` used `value` as an `re.sub` **replacement**, so a backslash in a check title would have been interpreted rather than written.