// A walker must not have to know the repo keeps a ledger (ISS-0272).
//
// `verdictPlatform()` returns '' when the nav platform picker reads `All`, and
// once a repo keeps a ledger the server refuses a mark carrying no platform —
// correctly, because a scalar on the note would be a second answer to a
// question the ledger owns. The reader met that refusal mid-walk, in a message
// written for whoever is calling the API.
//
// This runs the REAL function out of the built bundle against controlled state.
// A source-text assertion would pass on the presence of the fallback without
// proving it returns anything, which is exactly the class of guard an
// independent review found surviving five mutants in this same change set.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const builtRenderer = path.join(here, '..', 'dist', 'renderer', 'renderer.js');

async function extractFunction(name) {
  const src = await fs.readFile(builtRenderer, 'utf8');
  const start = src.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `${name} not found in the built renderer`);
  let depth = 0;
  let i = src.indexOf('{', start);
  for (; i < src.length; i += 1) {
    if (src[i] === '{') depth += 1;
    else if (src[i] === '}') { depth -= 1; if (depth === 0) break; }
  }
  return src.slice(start, i + 1);
}

/** Run the real verdictPlatform with a controlled picker and ledger set. */
async function run({ picker, ledgers }) {
  const body = await extractFunction('verdictPlatform');
  // eslint-disable-next-line no-new-func
  const fn = new Function(
    'loadStoredPlatform', 'ledgerPlatforms',
    `${body}; return verdictPlatform;`,
  )(() => picker, ledgers);
  return fn();
}

test('the picker still wins when the reader has set one', async () => {
  assert.equal(await run({ picker: 'ios', ledgers: ['android'] }), 'ios');
});

test('on All, a single-ledger repo supplies its own platform', async () => {
  // The reported bug: this returned '' and the mark came back 409.
  assert.equal(await run({ picker: 'all', ledgers: ['android'] }), 'android');
  assert.equal(await run({ picker: '', ledgers: ['android'] }), 'android');
  assert.equal(await run({ picker: null, ledgers: ['android'] }), 'android');
});

test('a repo with no ledger is unchanged', async () => {
  // Nine of twelve fleet repos. The scalar write path is legal there and must
  // stay reachable; inventing a platform would route them somewhere new.
  assert.equal(await run({ picker: 'all', ledgers: [] }), '');
});

test('several ledgers stay ambiguous and are refused', async () => {
  // Guessing here puts a verdict on a platform nobody walked, which is worse
  // than the 409. The refusal is the correct answer to a real question.
  assert.equal(await run({ picker: 'all', ledgers: ['android', 'ios'] }), '');
});
