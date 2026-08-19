---
type: "[[test]]"
id: TST-0045
aliases: ["TST-0045", "CHK-0002"]
title: "Live reload"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Render server and the browser front door"
covers: ["[[FEAT-0001]]", "[[FEAT-0002]]", "[[FEAT-0006]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.1.2 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0002 @ 4c02731"
---

# Live reload

edit a note on disk while the page is open. Expect: the centre pane updates without a manual refresh. — 2026-08-10: appended a comment to `docs/README.md` with `/_events` open; `event: file-changed / data: README.md` arrived within 3s, followed by a `cockpit:validation` re-run. Probe reverted.
