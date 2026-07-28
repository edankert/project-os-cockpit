# Development probes

## `cdp.py` — talk to the running Electron app

Dependency-free DevTools Protocol client. It exists because three separate bugs
([[ISS-0043]], [[ISS-0046]], [[ISS-0047]]) hid in the gap between "the artifact
opened in a browser tab" and "the artifact in the design frame" — the frame is
sandboxed, opaque-origin and cross-process, so **any check conducted outside it
is checking a different thing.**

```bash
cd desktop && npx electron . --remote-debugging-port=9222 &
curl -s http://127.0.0.1:9222/json | python3 -c "import sys,json;[print(t['type'],t['url'][:90]) for t in json.load(sys.stdin)]"
```

The design frame appears as its own `iframe` target, so it can be measured
directly:

```python
from cdp import evaluate
evaluate("getComputedStyle(document.body).overflow", url_contains="design-asset")
```

`url_contains` picks the target: `renderer/index.html` for the app shell,
`design-asset` for the artifact inside the frame.

Not part of the test suite — it needs a running app with a debug port. It is
the tool to reach for when a surface behaves differently in the app than
anywhere it has been tested, which is the situation it was written for.
