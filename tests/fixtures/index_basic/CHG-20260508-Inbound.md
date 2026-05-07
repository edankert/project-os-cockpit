---
type: "[[change]]"
id: CHG-20260508-Inbound
aliases: ["CHG-20260508-Inbound"]
title: "Test change linking only inbound to FEAT-0001"
status: merged
features: ["[[FEAT-0001]]"]
---

# Test change

This change references FEAT-0001 in its frontmatter (`features` field) but
FEAT-0001 doesn't reference back. Used by `tests/test_cockpit.py` to verify
the right-pane "inbound-only" grouping.
