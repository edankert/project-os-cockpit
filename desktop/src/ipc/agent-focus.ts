// Agent-focus bridge (TASK-0064).
//
// The Python cockpit publishes a `cockpit:focus` SSE event on
// `<sidecar>/_events` whenever an external `cockpit focus <id>` call
// resolves a target. In browser mode the cockpit's own JS handles
// navigation; in the Electron shell the iframe's embedded cockpit JS
// still does that — but we ALSO want the desktop window to come
// forward when an agent calls focus while the app is hidden.
//
// So the main process subscribes to each active sidecar's SSE stream
// and, on a `cockpit:focus` event, calls `window.show()` + `focus()`.
// We keep one subscription per window and tear it down when the
// sidecar exits or the window closes.

import { BrowserWindow } from 'electron';
import * as http from 'node:http';

interface Subscription {
  windowId: number;
  request: http.ClientRequest;
}

const subs = new Map<number, Subscription>();

export function subscribeAgentFocus(
  window: BrowserWindow,
  sidecarUrl: string,
): void {
  unsubscribeAgentFocus(window);

  const parsed = new URL(sidecarUrl);
  const req = http.get({
    host: parsed.hostname,
    port: parsed.port ? Number(parsed.port) : 80,
    path: '/_events',
    headers: { 'Accept': 'text/event-stream' },
  }, (res) => {
    if (res.statusCode !== 200) {
      res.resume();
      return;
    }
    res.setEncoding('utf-8');
    let buffer = '';
    let currentEvent = '';
    let currentData = '';

    const handleEvent = (): void => {
      if (currentEvent === 'cockpit:focus') {
        // Surface the focus to the user: bring the window forward.
        if (!window.isDestroyed()) {
          if (window.isMinimized()) window.restore();
          window.show();
          window.focus();
          window.webContents.send('agent:focus', tryParseJson(currentData));
        }
      }
      currentEvent = '';
      currentData = '';
    };

    res.on('data', (chunk: string) => {
      buffer += chunk;
      let nl: number;
      while ((nl = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, nl);
        buffer = buffer.slice(nl + 1);
        if (line === '') {
          handleEvent();
          continue;
        }
        if (line.startsWith(':')) continue; // SSE comment / heartbeat
        if (line.startsWith('event: ')) {
          currentEvent = line.slice('event: '.length).trim();
        } else if (line.startsWith('data: ')) {
          // Multiline data accumulates; v1 cockpit events are single-line.
          currentData = currentData
            ? `${currentData}\n${line.slice('data: '.length)}`
            : line.slice('data: '.length);
        }
      }
    });

    res.on('end', () => { subs.delete(window.id); });
    res.on('error', () => { subs.delete(window.id); });
  });
  req.on('error', () => { subs.delete(window.id); });

  subs.set(window.id, { windowId: window.id, request: req });
}

export function unsubscribeAgentFocus(window: BrowserWindow): void {
  const sub = subs.get(window.id);
  if (!sub) return;
  subs.delete(window.id);
  try { sub.request.destroy(); } catch { /* ignore */ }
}

function tryParseJson(raw: string): unknown {
  try { return JSON.parse(raw); } catch { return raw; }
}
