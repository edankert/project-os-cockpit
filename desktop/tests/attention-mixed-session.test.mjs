// The real Needs You entry builder must name current work while preserving
// a different session's waiting request in the same project card.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'renderer', 'renderer.js');

async function extractFunction(name) {
  const src = await fs.readFile(built, 'utf8');
  const start = src.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `${name} missing from built renderer`);
  let depth = 0;
  let end = src.indexOf('{', start);
  for (; end < src.length; end += 1) {
    if (src[end] === '{') depth += 1;
    if (src[end] === '}' && --depth === 0) break;
  }
  return src.slice(start, end + 1);
}

async function entriesFor(state, digest) {
  const label = await extractFunction('agentMessage');
  const line = await extractFunction('agentLine');
  const copy = await extractFunction('attentionAgentCopy');
  const entries = await extractFunction('attentionEntries');
  const deps = {
    agentStates: new Map([['ws', state]]),
    lastAgentSnap: null,
    activeId: 'ws',
    workspaces: [{ id: 'ws', name: 'project-os-cockpit' }],
    effectiveName: (ws) => ws.name,
    attentionIds: () => state.attention?.length ? ['ws'] : [],
    cacheTemperature: () => 'warm',
    fmtDuration: () => '1m',
    digests: digest ? new Map([['ws', digest]]) : new Map(),
    fleetHealth: new Map(),
    digestFor: () => digest,
    sinceLine: () => '',
    attentionFingerprint: () => 'fingerprint',
    alertKey: (ws, key) => `${ws}::${key}`,
    pruneDismissedAlerts: () => {},
    isAlertDismissed: () => false,
  };
  const names = Object.keys(deps);
  const run = new Function(...names, `${label}\n${line}\n${copy}\n${entries}\nreturn attentionEntries();`);
  return run(...Object.values(deps));
}

test('busy Codex is the headline while older Claude still needs review', async () => {
  const rows = await entriesFor({
    state: 'busy', agent: 'codex', ts: '2026-09-16T17:00:00Z', session_id: 'current',
    attention: [{
      state: 'waiting', agent: 'claude', ts: '2026-09-16T16:00:00Z',
      session_id: 'older', message: 'Claude is waiting for your input',
    }],
  });
  assert.equal(rows.length, 1);
  assert.equal(rows[0].message, 'Codex · working… · 1m');
  assert.equal(rows[0].pendingMessage, 'Claude is waiting for your input');
  assert.equal(rows[0].kind, 'waiting');
});

test('a current Codex approval stays the primary Needs You message', async () => {
  const rows = await entriesFor({
    state: 'needs-input', agent: 'codex', ts: '2026-09-16T17:01:00Z', session_id: 'current',
    attention: [
      { state: 'needs-input', agent: 'codex', ts: '2026-09-16T17:01:00Z', session_id: 'current', message: 'wants to use Bash' },
      { state: 'waiting', agent: 'claude', ts: '2026-09-16T16:00:00Z', session_id: 'older', message: 'Claude is waiting for your input' },
    ],
  });
  assert.equal(rows[0].message, 'Codex · wants to use Bash');
  assert.equal(rows[0].pendingMessage, undefined);
  assert.equal(rows[0].kind, 'needs-input');
});

test('a record card names Codex when no agent request is pending', async () => {
  const rows = await entriesFor({
    state: 'busy', agent: 'codex', ts: '2026-09-16T17:00:00Z', session_id: 'current',
    attention: [],
  }, { needsYou: 1, transitions: 2 });
  assert.equal(rows.length, 1);
  assert.equal(rows[0].kind, 'record');
  assert.equal(rows[0].message, 'Codex · working… · 1m');
});

test('elapsed working time does not undo dismissal, but a new request does', async () => {
  const source = await extractFunction('attentionFingerprint');
  const agentStates = new Map([['ws', { state: 'busy', ts: '2026-09-16T17:00:00Z' }]]);
  const fingerprint = new Function('agentStates', `${source}\nreturn attentionFingerprint;`)(agentStates);
  const card = {
    workspaceId: 'ws', kind: 'waiting', ts: '2026-09-16T16:00:00Z',
    message: 'Codex · working… · 1m', pendingMessage: 'Claude is waiting for your input',
  };
  assert.equal(
    fingerprint(card, undefined),
    fingerprint({ ...card, message: 'Codex · working… · 2m' }, undefined),
  );
  assert.notEqual(
    fingerprint(card, undefined),
    fingerprint({ ...card, ts: '2026-09-16T17:01:00Z' }, undefined),
  );
});
