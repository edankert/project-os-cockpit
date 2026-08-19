---
type: "[[test]]"
id: TST-0046
aliases: ["TST-0046"]
title: "A tablet can read it"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Render server and the browser front door"
covers: ["[[FEAT-0001]]", "[[FEAT-0002]]", "[[FEAT-0006]]"]
related: []
level: acceptance
---

# A tablet can read it

open the same URL from another device on the Wi-Fi. Expect: the page renders; every write control is either absent or refuses (the render port binds `0.0.0.0`, writes are loopback-only). — 2026-08-10, over the real LAN interface `192.168.68.123:8791`: reads **200**; and **all ten** mutation endpoints — `notes/transition`, `notes/check-toggle`, `notes/test-run`, `notes/tick`, `notes/create`, `notes/review`, `design/verdict`, `cockpit/caught-up`, `cockpit/review-request`, `cockpit/review-resolve` — returned **403**, while the same endpoint over loopback returned 400 (reached, bad body). *A second device was not used; a non-loopback peer was, which is the property. This is the check `test_mutation_endpoints_reject_non_loopback_callers` disclosed it could not make — "an honest static check, since http.server cannot spoof a peer address".*
