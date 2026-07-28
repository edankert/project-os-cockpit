#!/usr/bin/env python3
"""Minimal Chrome DevTools Protocol client — enough to evaluate JS in the
Electron renderer and read the answer. No dependencies: the handshake is a
plain HTTP upgrade and we only need one masked text frame out, one frame in.
"""
import base64, json, os, socket, struct, sys, urllib.request


def targets(port=9222):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as r:
        return json.load(r)


def _recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed")
        buf += chunk
    return buf


def _read_frame(sock):
    b1, b2 = _recv_exact(sock, 2)
    length = b2 & 0x7F
    if length == 126:
        length = struct.unpack(">H", _recv_exact(sock, 2))[0]
    elif length == 127:
        length = struct.unpack(">Q", _recv_exact(sock, 8))[0]
    return _recv_exact(sock, length)   # server frames are never masked


def _send_frame(sock, payload: bytes):
    header = bytearray([0x81])         # FIN + text
    mask = os.urandom(4)
    n = len(payload)
    if n < 126:
        header.append(0x80 | n)
    elif n < 1 << 16:
        header.append(0x80 | 126); header += struct.pack(">H", n)
    else:
        header.append(0x80 | 127); header += struct.pack(">Q", n)
    header += mask
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    sock.sendall(bytes(header) + masked)


def evaluate(expression, port=9222, url_contains="renderer"):
    target = next(t for t in targets(port)
                  if url_contains in t["url"])
    ws = target["webSocketDebuggerUrl"]
    path = ws.split("127.0.0.1:%d" % port, 1)[1]
    sock = socket.create_connection(("127.0.0.1", port), timeout=15)
    key = base64.b64encode(os.urandom(16)).decode()
    sock.sendall((
        f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
        f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
    ).encode())
    # drain the handshake response
    data = b""
    while b"\r\n\r\n" not in data:
        data += sock.recv(4096)

    _send_frame(sock, json.dumps({
        "id": 1, "method": "Runtime.evaluate",
        "params": {"expression": expression, "awaitPromise": True,
                   "returnByValue": True},
    }).encode())
    while True:
        msg = json.loads(_read_frame(sock))
        if msg.get("id") == 1:
            sock.close()
            result = msg.get("result", {})
            if "exceptionDetails" in result:
                return {"__error": result["exceptionDetails"].get("text"),
                        "detail": str(result["exceptionDetails"])[:400]}
            return result.get("result", {}).get("value")


if __name__ == "__main__":
    expr = sys.stdin.read()
    print(json.dumps(evaluate(expr), indent=2, default=str))
