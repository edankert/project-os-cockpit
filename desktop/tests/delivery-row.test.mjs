// What a queued prompt's row says (FEAT-0158; TASK-0659).
//
// After the person stops a Claude turn with Esc, Claude Code takes no prompt
// from a plugin until they send it something, so the plugin holds the prompt.
// In TST-0095's second run the row still said "Waiting for Claude to finish
// its turn", and the prompt was read as stalled. This runs the real
// `deliveryRowText`, extracted from the built renderer.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const builtRenderer = path.join(here, '..', 'dist', 'renderer', 'renderer.js');

/** Pull one top-level `function NAME(...) { ... }` out of the built bundle. */
async function extractFunction(name) {
  const src = await fs.readFile(builtRenderer, 'utf8');
  const start = src.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `${name} not found in the built renderer`);
  let depth = 0;
  let i = src.indexOf('{', start);
  for (; i < src.length; i += 1) {
    if (src[i] === '{') depth += 1;
    else if (src[i] === '}') {
      depth -= 1;
      if (depth === 0) break;
    }
  }
  return new Function(`return (${src.slice(start, i + 1)});`)();
}

test('a prompt held after Esc says it is waiting for the person', async () => {
  const rowText = await extractFunction('deliveryRowText');
  assert.equal(rowText({ state: 'waiting' }), 'Waiting for Claude to finish its turn');
  assert.equal(
    rowText({ state: 'waiting', waiting_for: 'you' }),
    'Waiting for you: Claude was stopped, so this follows your next message to it',
  );
  assert.equal(rowText({ state: 'held', reason: 'the session ended' }), 'Not delivered: the session ended');
});

test('a removed prompt is not called cancelled before it reached the session', async () => {
  // TASK-0662: a prompt whose session ended while it was being submitted may
  // have run, so removing it is recorded as removed, with the reason.
  const text = await extractFunction('dispatchProvenanceText');
  assert.equal(
    text({ verb: 'implement', agent: 'claude', removed: true, reason: 'the session ended before Claude confirmed its turn, so it may have run' }, '17:00', ''),
    'dispatched implement · claude · not delivered (the session ended before Claude confirmed its turn, so it may have run), removed 17:00',
  );
  assert.equal(text({ verb: 'implement', agent: 'claude', cancelled: true }, '17:00', ''),
    'dispatched implement · claude · cancelled 17:00, before it reached the session');
  assert.equal(text({ verb: 'implement', agent: 'codex' }, '17:00', 'session 01a13b3a'),
    'dispatched implement · codex · 17:00 → session 01a13b3a');
});
