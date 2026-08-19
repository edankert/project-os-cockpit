---
type: "[[test]]"
id: TST-0018
aliases: ["TST-0018"]
title: "Status-diff layer — transitions emit once, non-changes and cold seed are silent"
status: active
covers: ["[[TASK-0162-Status-Diff-Layer]]", "[[FEAT-0036-Live-Work-Views]]"]
command: ".venv/bin/pytest tests/test_status_diff.py -q"
owner: user:edwin
created: 2026-07-19
updated: 2026-08-13
related: []
last_verified: 2026-07-19

---

# TST-0018 — status-diff layer

`tests/test_status_diff.py` (4 tests): a real frontmatter-status change emits exactly one `cockpit:status-change` (with from/to/type) and logs it; an identical-status save is silent; a note first appearing after the cold seed is silent (but its next real change emits); deleted/unreadable events are ignored.
