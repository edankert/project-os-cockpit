// The shell makes a secret for each sidecar it spawns and hands it over on
// standard input, never in argv or the environment (FEAT-0159 / TASK-0664).
//
// Runs the built sidecar.js with stand-ins for Electron and the other main
// modules, but a REAL spawn of the real Python sidecar (COCKPIT_DESKTOP_PYTHON,
// set by tests/test_desktop_node_suite.py). So "the sidecar got the secret" is
// read from the sidecar's own answers: an answer without the header is
// refused, and the same answer with it gets past the guard.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as childProcess from 'node:child_process';
import * as crypto from 'node:crypto';
import * as fs from 'node:fs';
import * as http from 'node:http';
import { createRequire } from 'node:module';
import * as os from 'node:os';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'ipc', 'sidecar.js');
const requireFromDesktop = createRequire(path.join(here, '..', 'package.json'));

function workspaceDir() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'shell-secret-'));
  fs.mkdirSync(path.join(root, 'docs'));
  fs.writeFileSync(path.join(root, 'docs', 'README.md'), '# Hi\n');
  fs.writeFileSync(path.join(root, 'SNAPSHOT.yaml'), 'version: 1\n');
  return root;
}

function load(workspace) {
  const spawned = [];
  const events = [];
  const handlers = {};
  const window = { id: 1, isDestroyed: () => false, webContents: { send: (_ch, ev) => events.push(ev) } };
  const module = { exports: {} };
  vm.runInNewContext(fs.readFileSync(built, 'utf-8'), {
    module, exports: module.exports, console, process, setTimeout, clearTimeout, Buffer, URL,
    __dirname: path.dirname(built),
    require: (name) => {
      if (name === 'electron') return {
        app: { isPackaged: false, getPath: () => os.tmpdir(), getAppPath: () => path.join(here, '..') },
        BrowserWindow: { fromId: () => window },
        ipcMain: { handle: (channel, fn) => { handlers[channel] = fn; } },
      };
      if (name === 'node:child_process') return {
        ...childProcess,
        spawn: (cmd, args, options) => {
          const child = childProcess.spawn(cmd, args, options);
          spawned.push({ cmd, args, options, child });
          return child;
        },
      };
      if (name === 'node:crypto') return crypto;
      if (name === 'node:fs') return fs;
      if (name === 'node:http') return http;
      if (name === 'node:path') return path;
      if (name === 'portfinder') return requireFromDesktop('portfinder');
      if (name === './workspaces') return { getWorkspace: () => workspace, markOpened: async () => {} };
      if (name === './agent-focus') return { subscribeAgentFocus() {}, unsubscribeAgentFocus() {} };
      if (name === './agent-instrument') return { setSidecarUrl() {} };
      if (name === './approvals') return { watchApprovals() {}, unwatchApprovals() {} };
      throw new Error(`unexpected import ${name}`);
    },
  }, { filename: built });
  module.exports.registerSidecarIpc({ getActiveWindow: () => window });
  return { ...module.exports, spawned, events, open: () => handlers['workspaces:open'](null, workspace.id) };
}

async function until(predicate, ms = 15000) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    const v = predicate();
    if (v) return v;
    await new Promise((r) => setTimeout(r, 50));
  }
  throw new Error('timed out');
}

function post(url, body, secret) {
  const data = Buffer.from(JSON.stringify(body));
  const headers = { 'Content-Type': 'application/json', 'Content-Length': data.length };
  if (secret) headers['X-Cockpit-Secret'] = secret;
  return new Promise((resolve, reject) => {
    const req = http.request(url, { method: 'POST', headers }, (res) => {
      let text = '';
      res.on('data', (c) => { text += c; });
      res.on('end', () => resolve({ status: res.statusCode, text }));
    });
    req.on('error', reject);
    req.end(data);
  });
}

test('a spawned sidecar gets its secret on stdin and requires it', { timeout: 30000 }, async () => {
  const workspace = { id: 'ws-secret', root: workspaceDir(), name: 'x', projectId: 'x', lastOpened: null, pinned: false };
  const s = load(workspace);
  try {
    await s.open();
    const ready = await until(() => s.events.find((e) => e.kind === 'ready' || e.kind === 'failed'));
    assert.equal(ready.kind, 'ready', JSON.stringify(ready.payload));

    const secret = s.sidecarSecretFor(workspace.id);
    assert.match(secret, /^[0-9a-f]{64}$/);

    const [{ args, options }] = s.spawned;
    assert.ok(args.includes('--secret-stdin'));
    assert.equal(options.stdio[0], 'pipe');
    assert.ok(!args.join(' ').includes(secret), 'the secret is not in argv');
    assert.ok(!Object.values(options.env).some((v) => String(v).includes(secret)), 'nor in the environment');

    const url = `${ready.payload.url}/api/cockpit/approve`;
    const answer = { approval_id: 'none', decision: 'granted', actor: 'user:edwin' };
    assert.equal((await post(url, answer)).status, 403, 'refused without the secret');
    assert.equal((await post(url, answer, 'f'.repeat(64))).status, 403, 'refused with a wrong one');
    const withIt = await post(url, answer, secret);
    assert.equal(withIt.status, 404, `past the guard, to "no such approval": ${withIt.text}`);
    assert.ok(!withIt.text.includes(secret));
  } finally {
    s.shutdownAllSidecars();
  }
});

test('the line on stdin carries the wait, defaulted and clamped', () => {
  const s = load({ id: 'unused', root: os.tmpdir() });
  const read = (wait) => JSON.parse(s.shellLine('k', wait));
  assert.deepEqual(read(undefined), { secret: 'k', approval_wait_ms: 5000 });
  assert.equal(read(1200).approval_wait_ms, 1200);
  assert.equal(read(0).approval_wait_ms, 0);
  assert.equal(read(-1).approval_wait_ms, 0);
  assert.equal(read(120000).approval_wait_ms, 30000);
  assert.equal(read('5000').approval_wait_ms, 5000);
  assert.ok(s.shellLine('k', 1).endsWith('\n'));
});
