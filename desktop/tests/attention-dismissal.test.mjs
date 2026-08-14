// A dismissal survives a restart (TASK-0420, ISS-0165).
//
// TASK-0420's Definition of Done asked for this to be "asserted rather than
// assumed", and the box was never ticked. Independent review on 2026-08-14
// found out why it mattered: the store was restored from localStorage and
// wiped on the same tick, so a ✕ never survived a relaunch — the one property
// the feature was asked for.
//
// The mechanism: `refreshAttention()` is called at module load to paint the
// last-known state immediately, and at that moment `workspaces` is still `[]`
// because discovery is async. Every restored key failed `workspaces.some(...)`
// inside `pruneDismissedAlerts`, so all of them were deleted and `{}` written
// back before the fleet was ever known.
//
// This runs the REAL function, extracted from the built renderer, against the
// module's own initial state — the same way the review demonstrated it. A
// source-text assertion would have been satisfied by the guard's presence
// without proving it does anything, and the defect here was never about the
// text being absent: `pruneDismissedAlerts` read correctly and behaved wrongly
// only because of *when* it ran.

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
  const open = i;
  for (; i < src.length; i += 1) {
    if (src[i] === '{') depth += 1;
    else if (src[i] === '}') {
      depth -= 1;
      if (depth === 0) break;
    }
  }
  return src.slice(start, i + 1);
}

/** Run pruneDismissedAlerts with a controlled `workspaces` and store. */
async function runPrune({ workspaces, dismissed, liveKeys }) {
  const body = await extractFunction('pruneDismissedAlerts');
  const store = { ...dismissed };
  const written = [];
  const localStorage = {
    setItem: (_k, v) => { written.push(v); },
    getItem: () => null,
  };
  // eslint-disable-next-line no-new-func
  const fn = new Function(
    'workspaces', 'dismissedAlerts', 'localStorage', 'ATTENTION_DISMISS_KEY',
    `${body}; return pruneDismissedAlerts;`,
  )(workspaces, store, localStorage, 'cockpit.attention.dismissed');
  fn(new Set(liveKeys));
  return { store, written };
}

const KEY = 'ws-abc::fingerprint-1';

test('a dismissal is not wiped before the fleet is discovered', async () => {
  // Exactly the module-load state: workspaces still empty, refreshAttention
  // called, the store just restored from localStorage.
  const { store, written } = await runPrune({
    workspaces: [],
    dismissed: { [KEY]: 1 },
    liveKeys: [],
  });
  assert.deepEqual(store, { [KEY]: 1 }, 'the restored dismissal was deleted in memory');
  assert.deepEqual(written, [], 'an empty store was persisted over the real one');
});

test('a vanished workspace is still pruned once the fleet IS known', async () => {
  // The guard must not disable pruning outright — that would leak keys forever.
  const { store, written } = await runPrune({
    workspaces: [{ id: 'ws-other' }],
    dismissed: { [KEY]: 1 },
    liveKeys: [KEY],
  });
  assert.deepEqual(store, {}, 'a key for a workspace that no longer exists was kept');
  assert.equal(written.length, 1, 'the prune was not persisted');
});

test('a superseded fingerprint is pruned while its workspace lives', async () => {
  const { store } = await runPrune({
    workspaces: [{ id: 'ws-abc' }],
    dismissed: { [KEY]: 1 },
    liveKeys: ['ws-abc::fingerprint-2'],
  });
  assert.deepEqual(store, {}, 'a stale fingerprint survived a newer one replacing it');
});

test('a live dismissal on a live workspace is kept', async () => {
  const { store, written } = await runPrune({
    workspaces: [{ id: 'ws-abc' }],
    dismissed: { [KEY]: 1 },
    liveKeys: [KEY],
  });
  assert.deepEqual(store, { [KEY]: 1 }, 'a current dismissal was dropped');
  assert.deepEqual(written, [], 'nothing changed, so nothing should have been written');
});
