// A dispatch to a live Claude session is handed to the sidecar, never typed
// (FEAT-0158 / TASK-0656).
//
// Runs the built dispatch-queue.js with stand-ins for Electron and the
// terminal, against a real HTTP server that answers as the sidecar does. Every
// write to the terminal is recorded, so "nothing is typed" is a fact the test
// reads, not one it assumes.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as http from 'node:http';
import * as os from 'node:os';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'ipc', 'dispatch-queue.js');

/** A stand-in sidecar: its live session, and what it was sent. */
async function sidecar(session) {
  const received = [];
  const server = http.createServer((req, res) => {
    let body = '';
    req.on('data', (c) => { body += c; });
    req.on('end', () => {
      const json = body ? JSON.parse(body) : null;
      received.push({ method: req.method, path: req.url, body: json });
      res.setHeader('Content-Type', 'application/json');
      if (req.url === '/api/cockpit/state') {
        res.end(JSON.stringify({ session }));
      } else if (req.url === '/api/cockpit/deliveries') {
        const claimed = session?.plugin_claimed === true;
        res.end(JSON.stringify({ ok: true, delivery: {
          did: 'd-1', id: json.id, verb: json.verb, prompt: json.prompt, session_id: json.session_id,
          state: claimed ? 'waiting' : 'held',
          ...(claimed ? {} : { reason: 'this Claude session has no cockpit plugin' }),
        } }));
      } else {
        res.end('{"ok":true}');
      }
    });
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  return { url: `http://127.0.0.1:${server.address().port}`, received, close: () => server.close() };
}

/** `foreground` is what tmux would name the terminal's foreground program. */
function load(sidecarUrl, foreground = 'zsh') {
  const writes = [];
  const module = { exports: {} };
  vm.runInNewContext(fs.readFileSync(built, 'utf-8'), {
    module, exports: module.exports, console, setTimeout, clearTimeout, Buffer, URL,
    require: (name) => {
      if (name === 'electron') return {
        app: { getPath: () => fs.mkdtempSync(path.join(os.tmpdir(), 'dispatch-')) },
        BrowserWindow: { getAllWindows: () => [] },
        ipcMain: { handle() {}, on() {} },
      };
      if (name === 'node:fs') return fs;
      if (name === 'node:http') return http;
      if (name === 'node:path') return path;
      if (name === './terminal') return {
        hasPty: () => true,
        writeToPty: (_ws, data) => { writes.push(data); return true; },
        foregroundCommand: async () => foreground,
      };
      if (name === './sidecar') return { sidecarUrlFor: () => sidecarUrl };
      throw new Error(`unexpected import ${name}`);
    },
  }, { filename: built });
  return { ...module.exports, writes };
}

const item = (agent = 'claude') => ({
  id: 'TASK-0001', rel: 'tasks/TASK-0001.md', verb: 'implement', agent,
  prompt: 'implement TASK-0001', ts: '2026-10-14T14:00:00Z',
});

test('a live Claude session gets a delivery, busy or not, and nothing is typed', async () => {
  const s = await sidecar({ live: true, agent: 'claude', session_id: 's-1', plugin_claimed: true });
  try {
    for (const state of ['waiting', 'busy', 'needs-input']) {
      const q = load(s.url, '2.1.299');
      q.onAgentStateChanged('ws', state, { deliver: false });
      const res = await q.executeDispatch('ws', item());
      assert.equal(res.delivered, 'submit', state);
      assert.equal(res.delivery.state, 'waiting');
      assert.deepEqual(q.writes, [], `nothing typed while ${state}`);
    }
    const posted = s.received.filter((r) => r.path === '/api/cockpit/deliveries');
    assert.equal(posted.length, 3);
    assert.equal(posted[0].body.session_id, 's-1');
    assert.equal(posted[0].body.prompt, 'implement TASK-0001');
    assert.equal(s.received.some((r) => r.path === '/api/cockpit/dispatch'), false,
      'a submitted prompt is stamped by the sidecar at its turn, not here');
  } finally { s.close(); }
});

test('a Claude session no plugin claims is held, and nothing is typed', async () => {
  const s = await sidecar({ live: true, agent: 'claude', session_id: 's-2', plugin_claimed: false });
  try {
    const q = load(s.url, '2.1.299');
    q.onAgentStateChanged('ws', 'waiting', { deliver: false });
    const res = await q.executeDispatch('ws', item());
    assert.equal(res.delivery.state, 'held');
    assert.match(res.warning, /not delivered: this Claude session has no cockpit plugin/);
    assert.deepEqual(q.writes, []);
  } finally { s.close(); }
});

test('a live Codex session is still typed, and its ledger entry says so', async () => {
  const s = await sidecar({ live: true, agent: 'codex', session_id: 'c-1' });
  try {
    const q = load(s.url, 'codex');
    q.onAgentStateChanged('ws', 'waiting', { deliver: false });
    const res = await q.executeDispatch('ws', item('codex'));
    assert.equal(res.delivered, 'repl');
    assert.deepEqual(q.writes, ['\x1b[200~implement TASK-0001\x1b[201~', '\r']);
    await new Promise((r) => setTimeout(r, 50));
    const ledger = s.received.find((r) => r.path === '/api/cockpit/dispatch');
    assert.equal(ledger.body.delivered_by, 'typed');
    assert.equal(s.received.some((r) => r.path === '/api/cockpit/deliveries'), false);
  } finally { s.close(); }
});

test('with no live session, the shell runs the agent as a command', async () => {
  const s = await sidecar(null);
  try {
    const q = load(s.url);
    q.onAgentStateChanged('ws', 'idle', { deliver: false });
    const res = await q.executeDispatch('ws', item());
    assert.equal(res.delivered, 'shell');
    assert.deepEqual(q.writes, ["claude 'implement TASK-0001'\r"]);
  } finally { s.close(); }
});

test('a sidecar that refuses the delivery keeps the dispatch queued, never typed', async () => {
  const s = await sidecar({ live: true, agent: 'claude', session_id: 's-3', plugin_claimed: true });
  const refusing = http.createServer((req, res) => {
    if (req.url === '/api/cockpit/state') {
      res.end(JSON.stringify({ session: { live: true, agent: 'claude', session_id: 's-3' } }));
    } else {
      res.statusCode = 400;
      res.end(JSON.stringify({ ok: false, error: '30 prompts are already waiting in this workspace' }));
    }
  });
  await new Promise((r) => refusing.listen(0, '127.0.0.1', r));
  try {
    const q = load(`http://127.0.0.1:${refusing.address().port}`, '2.1.299');
    q.onAgentStateChanged('ws', 'waiting', { deliver: false });
    const res = await q.executeDispatch('ws', item());
    assert.equal(res.queued, true);
    assert.match(res.warning, /30 prompts are already waiting/);
    assert.deepEqual(q.writes, []);
    assert.equal(q.queueDepthFor('ws'), 1);
  } finally { s.close(); refusing.close(); }
});

test('a Codex nobody has prompted yet gets the prompt pasted, never a codex command', async () => {
  // Codex runs its first hook when its first turn starts, so the cockpit has
  // no session for it yet (TST-0095 step 10, ISS-0322).
  const s = await sidecar(null);
  try {
    const q = load(s.url, 'codex');
    q.onAgentStateChanged('ws', 'idle', { deliver: false });
    const res = await q.executeDispatch('ws', item('claude'));
    assert.equal(res.delivered, 'repl');
    assert.deepEqual(q.writes, ['\x1b[200~implement TASK-0001\x1b[201~', '\r']);
    assert.equal(q.writes.some((w) => w.startsWith('codex ') || w.startsWith('claude ')), false);
    await new Promise((r) => setTimeout(r, 50));
    const ledger = s.received.find((r) => r.path === '/api/cockpit/dispatch');
    assert.equal(ledger.body.agent, 'codex', 'the ledger names the agent that got it, not the menu choice');
  } finally { s.close(); }
});

test('a Claude the cockpit cannot reach is held, and nothing is typed', async () => {
  // The kill switch: no plugin, no hook, so no session (TST-0095 step 9).
  const s = await sidecar(null);
  try {
    const q = load(s.url, '2.1.299');
    q.onAgentStateChanged('ws', 'idle', { deliver: false });
    const res = await q.executeDispatch('ws', item());
    assert.equal(res.queued, true);
    assert.match(res.warning, /Claude is running in this terminal but the cockpit cannot reach it/);
    assert.deepEqual(q.writes, []);
    assert.equal(q.queueDepthFor('ws'), 1);
  } finally { s.close(); }
});

test('any other program, or a terminal that cannot be read, holds the dispatch', async () => {
  const s = await sidecar(null);
  try {
    for (const [foreground, why] of [['vim', /vim is running in this terminal/], [null, /could not tell what is running/]]) {
      const q = load(s.url, foreground);
      q.onAgentStateChanged('ws', 'idle', { deliver: false });
      const res = await q.executeDispatch('ws', item());
      assert.equal(res.queued, true, String(foreground));
      assert.match(res.warning, why);
      assert.deepEqual(q.writes, []);
    }
  } finally { s.close(); }
});

test('a shell in the foreground wins over a Codex session the sidecar still lists', async () => {
  const s = await sidecar({ live: true, agent: 'codex', session_id: 'c-gone' });
  try {
    const q = load(s.url, 'zsh');
    q.onAgentStateChanged('ws', 'waiting', { deliver: false });
    const res = await q.executeDispatch('ws', item('codex'));
    assert.equal(res.delivered, 'shell');
    assert.deepEqual(q.writes, ["codex 'implement TASK-0001'\r"]);
  } finally { s.close(); }
});

test('the foreground program is classified by name', () => {
  const q = load('http://127.0.0.1:9');
  for (const shell of ['zsh', '-zsh', 'bash', '/bin/sh', 'fish']) assert.equal(q.classifyForeground(shell), 'shell', shell);
  assert.equal(q.classifyForeground('codex'), 'codex');
  assert.equal(q.classifyForeground('2.1.299'), 'claude');
  assert.equal(q.classifyForeground('claude'), 'claude');
  assert.equal(q.classifyForeground('vim'), 'other');
  assert.equal(q.classifyForeground(null), 'unknown');
  assert.equal(q.classifyForeground(''), 'unknown');
});

test('the routing table', () => {
  const q = load('http://127.0.0.1:9');
  const claude = { live: true, agent: 'claude', sessionId: 's' };
  const codex = { live: true, agent: 'codex', sessionId: 'c' };
  const none = { live: false, agent: null, sessionId: null };
  assert.equal(q.routeFor(claude, 'waiting', 'claude'), 'submit');
  assert.equal(q.routeFor(claude, 'busy', 'claude'), 'submit');
  assert.equal(q.routeFor({ ...claude, sessionId: null }, 'waiting', 'claude'), 'hold');
  assert.equal(q.routeFor(codex, 'busy', 'codex'), 'queue');
  assert.equal(q.routeFor(codex, 'waiting', 'codex'), 'repl');
  assert.equal(q.routeFor(none, 'idle', 'codex'), 'repl');
  assert.equal(q.routeFor(none, 'idle', 'claude'), 'hold');
  assert.equal(q.routeFor(none, 'idle', 'other'), 'hold');
  assert.equal(q.routeFor(none, 'idle', 'unknown'), 'hold');
  assert.equal(q.routeFor(none, 'idle', 'shell'), 'shell');
  assert.equal(q.routeFor(codex, 'waiting', 'shell'), 'shell');
});
