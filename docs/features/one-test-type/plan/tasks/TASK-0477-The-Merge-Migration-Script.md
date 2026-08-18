---
type: "[[task]]"
id: TASK-0477
aliases: ["TASK-0477"]
title: "The merge migration script — note to note, parity asserted through the reader"
status: backlog
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
