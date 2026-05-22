"""Unit tests for :mod:`project_os_cockpit.terminal_proxy`.

Covers the pure pieces (WS accept math, HTML injection) without
spinning up an actual ttyd or WebSocket session.
"""

from __future__ import annotations

from project_os_cockpit import terminal_proxy


def test_ws_accept_rfc6455_example() -> None:
    """Matches the example from RFC 6455 §1.3 — key
    'dGhlIHNhbXBsZSBub25jZQ==' must accept to
    's3pPLMBiTxaQ9kYGzzhZRbK+xOo='."""
    assert (
        terminal_proxy.ws_accept("dGhlIHNhbXBsZSBub25jZQ==")
        == "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="
    )


def test_inject_html_extras_inserts_before_head_close() -> None:
    body = b"<!doctype html><html><head><title>x</title></head><body></body></html>"
    out = terminal_proxy.inject_html_extras(body)
    assert b"</head>" in out
    style_idx = out.find(b"<style>")
    head_close_idx = out.find(b"</head>")
    assert 0 <= style_idx < head_close_idx, "style block must precede </head>"
    assert b"xterm-viewport" in out
    assert b"scrollbar" in out


def test_inject_html_extras_passes_through_non_html() -> None:
    body = b"var foo = 1;"  # JS bundle, no </head>
    out = terminal_proxy.inject_html_extras(body)
    assert out == body


def test_inject_html_extras_case_insensitive_head() -> None:
    body = b"<HTML><HEAD></HEAD></HTML>"
    out = terminal_proxy.inject_html_extras(body)
    # match is case-insensitive on the search side; result preserves
    # original case + injects the style block.
    assert b"<style>" in out
    assert out.endswith(b"</HEAD></HTML>")


def test_inject_html_extras_idempotent_safety() -> None:
    """Running injection twice is harmless — extras stack, no crash."""
    body = b"<html><head></head></html>"
    once = terminal_proxy.inject_html_extras(body)
    twice = terminal_proxy.inject_html_extras(once)
    assert twice.count(b"xterm-viewport") >= once.count(b"xterm-viewport")
