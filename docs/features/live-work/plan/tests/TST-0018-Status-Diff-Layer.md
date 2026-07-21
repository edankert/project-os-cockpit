---
type: "[[test]]"
id: TST-0018
aliases: ["TST-0018"]
title: "Status-diff layer — transitions emit once, non-changes and cold seed are silent"
status: passing
kind: automated
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
validates: ["[[TASK-0162]]"]
related: []
---

# TST-0018 — status-diff layer

`tests/test_status_diff.py` (4 tests): a real frontmatter-status change emits exactly one `cockpit:status-change` (with from/to/type) and logs it; an identical-status save is silent; a note first appearing after the cold seed is silent (but its next real change emits); deleted/unreadable events are ignored.
