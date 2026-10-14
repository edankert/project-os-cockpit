// The fleet view's queue depth counts prompts the sidecar holds for a Claude
// session as well as the shell's own queue (FEAT-0158 criterion 9). The
// review found no test for the shell's half (TASK-0662).

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'ipc', 'agents-fleet.js');

function load(state) {
  const module = { exports: {} };
  vm.runInNewContext(fs.readFileSync(built, 'utf-8'), {
    module, exports: module.exports, console, setTimeout, clearTimeout, AbortController,
    fetch: async () => ({ ok: true, json: async () => state }),
    require: (name) => {
      if (name === 'electron') return { ipcMain: { handle() {} } };
      if (name === 'node:fs') return fs;
      if (name === 'node:path') return path;
      if (name === './workspaces') return { getAllWorkspaces: () => [] };
      if (name === './agent-state-poller') return { getLastAgentPayloads: () => new Map() };
      if (name === './sidecar') return { sidecarUrlFor: () => 'http://127.0.0.1:9', sidecarSecretFor: () => null };
      if (name === './dispatch-queue') return { queueDepthFor: () => 1 };
      if (name === './codex-usage') return { getCodexUsage: () => null };
      throw new Error(`unexpected import ${name}`);
    },
  }, { filename: built });
  return module.exports;
}

test('the queue depth adds the prompts the sidecar holds to the shell queue', async () => {
  const row = await load({ deliveries_open: 2, session: null }).buildRow({ id: 'ws', name: 'ws', root: '/tmp/ws' });
  assert.equal(row.queueDepth, 3);
});

test('a sidecar that does not report deliveries leaves the shell queue as it is', async () => {
  const row = await load({ session: null }).buildRow({ id: 'ws', name: 'ws', root: '/tmp/ws' });
  assert.equal(row.queueDepth, 1);
});
