---
type: "[[plan]]"
title: "The review desk as record — delivery plan"
status: done
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
implements: ["[[FEAT-0049-Review-Desk-As-Record]]"]
related: ["[[FEAT-0041-Review-Desk]]"]
---

# The review desk as record — delivery plan

## Delivery sequence

1. **[[TASK-0241]]** — `review_queue_payload` gains a `registers` block carrying every test note (id, title, status, `last_verified`, manual/automated, staleness). Renderer draws it beneath the queue in the left pane. Tests stat tile gains `navMode` → `~review`.
2. **[[TASK-0242]]** — reviewed register from note frontmatter: scan the index for `review_verdict`, emit id/title/type/verdict/reviewer/date, most recent first. Rendered under the queue beside the tests register; the store's outcome tally stays untouched.

## Why the notes and not the store

The store retains resolved requests (`status: "resolved"` + `resolved_at`, `review.py:234-236`) so rendering them would be cheap — but `_MAX_REQUESTS = 200` trims oldest-first on every save, so the register would quietly lose its tail. Note frontmatter has no such ceiling and is the authored record by [[ADR-0009]]. The store keeps the outcome counts, which the notes cannot answer.
