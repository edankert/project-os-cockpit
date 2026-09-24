import { test } from 'node:test';
import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);

test('queued Codex work pastes then submits, and an interruption holds the next item', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'codex-dispatch-'));
  const writes = [];
  const delivered = [];
  const module = { exports: {} };
  const fakeHttp = {
    get(_url, _options, callback) {
      const req = new EventEmitter();
      queueMicrotask(() => {
        const res = new EventEmitter(); callback(res);
        res.emit('data', JSON.stringify({ session: { live: true, agent: 'codex' } }));
        res.emit('end');
      });
      return req;
    },
    request() { const req = new EventEmitter(); req.end = () => {}; return req; },
  };
  try {
    const built = new URL('../dist/ipc/dispatch-queue.js', import.meta.url);
    vm.runInNewContext(fs.readFileSync(built, 'utf8'), {
      exports: module.exports, module, console, Buffer, URL, setTimeout, clearTimeout,
      require(name) {
        if (name === 'electron') return {
          app: { getPath: () => dir }, ipcMain: {},
          BrowserWindow: { getAllWindows: () => [{ isDestroyed: () => false,
            webContents: { send: (event, data) => {
              if (event === 'dispatch:delivered') delivered.push(data);
            } } }] },
        };
        if (name === './terminal') return { hasPty: () => true,
          writeToPty: (ws, text) => { writes.push({ ws, text }); return true; } };
        if (name === './sidecar') return { sidecarUrlFor: () => 'http://127.0.0.1:1234' };
        if (name === 'node:http') return fakeHttp;
        return require(name);
      },
    });
    const { executeDispatch, onAgentStateChanged, queueDepthFor } = module.exports;
    const item = { id: 'TASK-1', rel: 'task.md', agent: 'codex', prompt: 'Run this\nand report', ts: '' };
    onAgentStateChanged('background-workspace', 'busy');
    assert.equal((await executeDispatch('background-workspace', item)).queued, true);
    onAgentStateChanged('background-workspace', 'waiting');
    await new Promise((resolve) => setTimeout(resolve, 50));
    assert.deepEqual(writes, [{ ws: 'background-workspace', text: '\x1b[200~Run this\nand report\x1b[201~' }]);
    assert.equal(delivered.length, 0);
    await new Promise((resolve) => setTimeout(resolve, 250));
    assert.equal(writes[1].text, '\r');
    assert.equal(delivered[0].mode, 'repl');
    onAgentStateChanged('background-workspace', 'needs-input');
    assert.equal((await executeDispatch('background-workspace', item)).queued, true);
    assert.equal(queueDepthFor('background-workspace'), 1);
    assert.equal(writes.length, 2, 'interrupted state must not release queued work');
    await new Promise((resolve) => setTimeout(resolve, 300));
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});
