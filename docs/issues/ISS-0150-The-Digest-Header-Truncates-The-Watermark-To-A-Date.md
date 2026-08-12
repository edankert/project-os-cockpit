---
type: "[[issue]]"
id: ISS-0150
aliases: ["ISS-0150"]
title: "Since you looked reports the time since midnight — the header truncates the watermark instant to a date, so catching up at 08:52 reads 8 hours ago"
status: fixed
severity: medium
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
phase: "[[PHASE-030-Obligations-Go-Home]]"
features: ["[[FEAT-0071-Since-You-Looked]]"]
tasks: []
related: ["[[ISS-0145]]"]
tags: [issue, renderer, time]
---

# The digest header truncates the watermark to a date

## What was found

Edwin, 2026-08-12: *"this section shows the right content but shows the time as being 8hrs at the moment, this is not correct, I have selected the caught up option a couple of minutes ago."*

The header builds its relative time like this:

```ts
const seen = d.seen_at && !d.seen_at.startsWith('1970') ? d.seen_at.slice(0, 10) : '';
head.textContent = `Since you looked — ${relativeTime(seen)}`;
```

**`.slice(0, 10)` cuts `2026-08-12T08:49:31Z` down to `2026-08-12`**, so `relativeTime` measures from **midnight**. Catching up at 08:52 reports *8 hours ago*, and would report *2 minutes ago* only if you caught up at 00:02. The number is a clock reading, not an elapsed time.

## Why the payload was never the problem

`digest_payload` carries the full instant, and `test_a_commit_carries_its_instant_not_only_its_day` in `tests/test_digest_watermark.py` asserts it does — deliberately, because a date-only watermark was a known failure mode there. The server got it right and the header threw the precision away one line before using it.

That is the shape worth naming: **the test guarded the producer, and the defect was in the consumer**, which is why a payload assertion could pass forever while the screen said something false.

## The fix

Use the instant. `relativeTime` already handles a full ISO timestamp — every other caller passes one.

## What the tests hold

`test_the_header_measures_from_the_instant_not_the_day` reads the built bundle and fails on any truncation of `seen_at` before it reaches `relativeTime`. Asserted against the *bundle* rather than the source because this is a behaviour of the shipped renderer, and the bundle is what was on screen when the 8 hours appeared.
