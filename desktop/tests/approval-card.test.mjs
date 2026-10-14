// A permission prompt answered from the Needs you panel (FEAT-0159 / TASK-0666).
//
// Two halves. The card's words come from `approvalCardText`, extracted from
// the built renderer. The answer and the live updates come from the built
// main-process module `approvals.js`, run against a stand-in sidecar that
// records what it is sent. The renderer must never post the answer itself:
// only the main process holds the secret and names the person.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as http from 'node:http';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const builtRenderer = path.join(here, '..', 'dist', 'renderer', 'renderer.js');
const builtApprovals = path.join(here, '..', 'dist', 'ipc', 'approvals.js');
const css = path.join(here, '..', 'src', 'renderer', 'renderer.css');

function extractFunction(name) {
  const src = fs.readFileSync(builtRenderer, 'utf8');
  const start = src.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `${name} not found in the built renderer`);
  let depth = 0;
  let i = src.indexOf('{', start);
  for (; i < src.length; i += 1) {
    if (src[i] === '{') depth += 1;
    else if (src[i] === '}') { depth -= 1; if (depth === 0) break; }
  }
  return new Function(`return (${src.slice(start, i + 1)});`)();
}

const open = { approval_id: 'a-1', session_id: '9baeb548-0e32', tool: 'Bash', prompt: 'rm -rf build', status: 'open', wait_ms: 5000 };

test('an open prompt offers an answer and shows the command whole', () => {
  const text = extractFunction('approvalCardText');
  const card = text(open);
  assert.equal(card.actionable, true);
  assert.equal(card.title, 'Claude asks to run a command');
  assert.equal(card.command, 'rm -rf build');
  assert.equal(card.session, 'session 9baeb548');
  assert.equal(card.note, '');
});

test('a long command is not cut', () => {
  const text = extractFunction('approvalCardText');
  const long = `${'x'.repeat(15000)} && echo end`;
  assert.equal(text({ ...open, prompt: long }).command, long);
  // Nor by the stylesheet: the block wraps and scrolls.
  const rule = fs.readFileSync(css, 'utf8').match(/\.ws-approval-cmd \{[^}]*\}/)?.[0] ?? '';
  assert.match(rule, /white-space: pre-wrap/);
  assert.match(rule, /overflow: auto/);
  assert.doesNotMatch(rule, /ellipsis|nowrap/);
});

test('a prompt is a plain row with its answer as two words, not a bordered box with buttons', () => {
  // TASK-0670: Edwin did not want the box or the full-width buttons.
  const sheet = fs.readFileSync(css, 'utf8');
  const row = sheet.match(/\.ws-approval-row \{[^}]*\}/)?.[0] ?? '';
  assert.notEqual(row, '');
  assert.doesNotMatch(row, /border:|background:/);
  const buttons = sheet.match(/\.ws-approval-actions button \{[^}]*\}/)?.[0] ?? '';
  assert.match(buttons, /border: none/);
  assert.doesNotMatch(buttons, /flex: 1/);
  const build = extractFunction('buildApprovalRow');
  assert.match(build.toString(), /meta\.appendChild\(actions\)/,
    'Approve and Deny sit on the session line');
});

test('a prompt handed to the terminal offers no answer, and says why in its own number', () => {
  const text = extractFunction('approvalCardText');
  const card = text({ ...open, status: 'handed-to-terminal' });
  assert.equal(card.actionable, false);
  assert.equal(card.note, "Answer in the terminal: the cockpit's 5 s wait ran out");
  assert.equal(text({ ...open, status: 'handed-to-terminal', wait_ms: 2500 }).note,
    "Answer in the terminal: the cockpit's 2.5 s wait ran out");
  assert.equal(text({ ...open, tool: 'Write', agent_id: 'agent-12345678' }).title, 'A Claude subagent asks to use Write');
});

test('the renderer never posts an answer itself', () => {
  const src = fs.readFileSync(builtRenderer, 'utf8');
  assert.equal(src.includes('/api/cockpit/approve'), false,
    'the renderer names the answer route; only the main process may, with the secret');
  assert.equal(src.includes('X-Cockpit-Secret'), false);
});

/** A stand-in sidecar: its approvals, an event stream, and what it was sent. */
async function sidecar() {
  const received = [];
  let stream = null;
  const approvals = [{ ...open }];
  const server = http.createServer((req, res) => {
    let body = '';
    req.on('data', (c) => { body += c; });
    req.on('end', () => {
      received.push({ method: req.method, path: req.url, headers: req.headers, body: body ? JSON.parse(body) : null });
      if (req.url === '/_events') {
        res.writeHead(200, { 'Content-Type': 'text/event-stream' });
        res.flushHeaders();
        stream = res;
        return;
      }
      res.setHeader('Content-Type', 'application/json');
      if (req.url === '/api/cockpit/approvals') {
        res.end(JSON.stringify({ approvals }));
      } else if (req.url === '/api/cockpit/approve') {
        const a = approvals.find((x) => x.approval_id === JSON.parse(body).approval_id);
        res.end(JSON.stringify({ ok: true, result: { ...a, status: 'granted' } }));
      } else {
        res.end('{"ok":true}');
      }
    });
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  return {
    url: `http://127.0.0.1:${server.address().port}`,
    received,
    emit: (record) => stream?.write(`event: cockpit:approval\ndata: ${JSON.stringify(record)}\n\n`),
    close: () => { stream?.end(); server.closeAllConnections?.(); server.close(); },
  };
}

function load(url) {
  const handlers = {};
  const sent = [];
  const window = { isDestroyed: () => false, webContents: { send: (channel, ev) => sent.push({ channel, ev }) } };
  const module = { exports: {} };
  vm.runInNewContext(fs.readFileSync(builtApprovals, 'utf-8'), {
    module, exports: module.exports, console, setTimeout, clearTimeout, Buffer, URL,
    require: (name) => {
      if (name === 'electron') return {
        BrowserWindow: { getAllWindows: () => [window] },
        ipcMain: { handle: (channel, fn) => { handlers[channel] = fn; } },
      };
      if (name === 'node:http') return http;
      if (name === 'node:os') return { userInfo: () => ({ username: 'edwin' }) };
      if (name === './sidecar') return { sidecarUrlFor: () => url, sidecarSecretFor: () => 'shell-secret' };
      throw new Error(`unexpected import ${name}`);
    },
  }, { filename: builtApprovals });
  module.exports.registerApprovalIpc();
  return { ...module.exports, handlers, sent };
}

async function until(predicate, ms = 3000) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    if (predicate()) return;
    await new Promise((r) => setTimeout(r, 20));
  }
  throw new Error('timed out');
}

test('the main process answers with the secret and the person, whatever the renderer sends', async () => {
  const s = await sidecar();
  try {
    const m = load(s.url);
    const answer = m.handlers['approval:answer'];
    // A fourth argument, as a renderer trying to choose the actor would pass.
    const result = await answer(null, 'ws', 'a-1', 'granted', 'agent:anyone');
    assert.equal(result.ok, true);
    const [post] = s.received.filter((r) => r.path === '/api/cockpit/approve');
    assert.equal(post.headers['x-cockpit-secret'], 'shell-secret');
    assert.deepEqual(post.body, { approval_id: 'a-1', decision: 'granted', actor: 'user:edwin' });

    const refused = await answer(null, 'ws', 'a-1', 'yes');
    assert.equal(refused.ok, false);
    assert.equal(s.received.filter((r) => r.path === '/api/cockpit/approve').length, 1, 'a bad decision is not posted');
  } finally { s.close(); }
});

test('a sidecar\'s approvals reach the windows as they change', async () => {
  const s = await sidecar();
  try {
    var m = load(s.url);
    m.watchApprovals('ws', s.url);
    const changes = () => m.sent.filter((x) => x.channel === 'approval:changed');
    await until(() => changes().some((c) => c.ev.approvals.length === 1));
    assert.equal(changes().at(-1).ev.workspaceId, 'ws');

    s.emit({ ...open, status: 'handed-to-terminal' });
    await until(() => changes().at(-1).ev.approvals[0]?.status === 'handed-to-terminal');

    s.emit({ ...open, status: 'closed' });
    await until(() => changes().at(-1).ev.approvals.length === 0);
    assert.deepEqual(Object.keys(m.liveApprovals()), []);
  } finally { m?.unwatchApprovals('ws'); s.close(); }
});
