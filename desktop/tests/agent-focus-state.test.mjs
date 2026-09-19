// A real SSE sidecar can deliver an approval and its resolution between
// state-file polls. Both transitions must reach the Electron renderer.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as http from 'node:http';
import * as path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const { subscribeAgentFocus, unsubscribeAgentFocus } = await import(
  pathToFileURL(path.join(here, '..', 'dist', 'ipc', 'agent-focus.js')).href
);

test('forwards each live approval transition for the open workspace', async () => {
  let client;
  const server = http.createServer((req, res) => {
    assert.equal(req.url, '/_events');
    res.writeHead(200, { 'Content-Type': 'text/event-stream' });
    res.write(': connected\n\n');
    client = res;
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const received = [];
  const window = {
    id: 91,
    isDestroyed: () => false,
    webContents: { send: (channel, payload) => received.push({ channel, payload }) },
  };
  try {
    subscribeAgentFocus(window, `http://127.0.0.1:${server.address().port}`, 'project-os-cockpit');
    await until(() => client);
    const approval = { state: 'needs-input', agent: 'codex', ts: '2026-09-16T16:40:52Z', message: 'wants to use Bash' };
    const resumed = { state: 'busy', agent: 'codex', ts: '2026-09-16T16:40:53Z' };
    client.write(`event: cockpit:agent-state\ndata: ${JSON.stringify(approval)}\n\n`);
    client.write(`event: cockpit:agent-state\ndata: ${JSON.stringify(resumed)}\n\n`);
    await until(() => received.length === 2);
    assert.deepEqual(received, [
      { channel: 'workspaces:agent-state', payload: { workspaceId: 'project-os-cockpit', payload: approval } },
      { channel: 'workspaces:agent-state', payload: { workspaceId: 'project-os-cockpit', payload: resumed } },
    ]);
  } finally {
    unsubscribeAgentFocus(window);
    client?.end();
    await new Promise((resolve) => server.close(resolve));
  }
});

async function until(predicate) {
  const deadline = Date.now() + 2000;
  while (!predicate()) {
    if (Date.now() > deadline) throw new Error('Timed out waiting for SSE delivery');
    await new Promise((resolve) => setTimeout(resolve, 5));
  }
}
