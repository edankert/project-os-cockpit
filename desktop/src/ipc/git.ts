// The push, and only ever from a person (FEAT-0055 / TASK-0266).
//
// Nothing in this app pushes on a timer, on close-out, or on any event.
// A commit is local and reversible; a push is publishing, and once a
// forge has cached and indexed it, deleting does not unpublish.
//
// The refusal is the feature. `your-applications.com`'s only remote is
// `root@…:/home/…/your-applications.com.git` — a server path, so
// pushing it DEPLOYS A LIVE WEBSITE. On 2026-07-30 that was one
// ambiguous instruction away from happening.
//
// Remote kind is derived from the URL here as well as in the Python
// payload, deliberately: this is the process that actually runs `git
// push`, and it must not trust a classification that arrived over IPC.

import { ipcMain } from 'electron';
import { execFile } from 'node:child_process';

import { getAllWorkspaces } from './workspaces';

const FORGE_HOSTS = ['github.com', 'gitlab.com', 'bitbucket.org', 'codeberg.org'];

/** `backup` may be pushed to. Anything unrecognised is `deploy` —
 *  the safe default for "I do not know what this is" is "do not
 *  publish to it". */
export function remoteKind(url: string): 'backup' | 'deploy' | 'none' {
  const u = (url || '').trim().toLowerCase();
  if (!u) return 'none';
  for (const host of FORGE_HOSTS) {
    if (u.includes(`//${host}/`) || u.includes(`@${host}:`)) return 'backup';
  }
  return 'deploy';
}

function run(cwd: string, args: string[], timeout = 60_000): Promise<{
  ok: boolean; out: string; err: string;
}> {
  return new Promise((resolve) => {
    execFile('git', ['-C', cwd, ...args], { timeout }, (err, stdout, stderr) => {
      resolve({ ok: !err, out: stdout ?? '', err: stderr || String(err ?? '') });
    });
  });
}

// `probeGitState` lived here from TASK-0415 until TASK-0422, and counted
// `rev-list @{u}..HEAD` plus a scoped `status --porcelain` for every workspace
// on the fleet clock. It was a second implementation of a question
// `git_state.py` already answered for the badge and for History — so
// FEAT-0100's claim, *one walk, so two surfaces cannot disagree*, was true of
// the notes and false of the code (ISS-0165).
//
// They agreed right up until one of them changed, and then one did: the
// unknown-count repair of 2026-08-14 was made in Python, and this side went on
// turning "there is no upstream, so no count exists" into a zero.
//
// The counting now comes from `project_os_cockpit.fleet_git`, which
// `fleet-health.ts` spawns on the same 60-second clock for every workspace —
// so ISS-0156's one-clock property survives and there is one implementation.
// What stays here is the classification below, which decides whether `git
// push` may run at all: this is the process that runs it, and it does not take
// that answer over IPC.

export function registerGitIpc(): void {
  ipcMain.handle('git:push', async (_evt, workspaceId: unknown) => {
    const ws = getAllWorkspaces().find((w) => w.id === workspaceId);
    if (!ws) return { ok: false, error: 'unknown workspace' };

    const remote = await run(ws.root, ['remote', 'get-url', 'origin']);
    const url = remote.ok ? remote.out.trim() : '';
    const kind = remoteKind(url);

    if (kind === 'none') {
      return { ok: false, error: 'this repo has no remote' };
    }
    if (kind === 'deploy') {
      // Re-checked here rather than trusting the renderer's disabled
      // button: a UI state is not a guard.
      return {
        ok: false,
        error: `refused — ${url} is a deployment target, not a backup. `
          + 'Pushing it would publish a running site.',
      };
    }

    const res = await run(ws.root, ['push']);
    if (!res.ok) {
      // git's own message, not a summary of it.
      return { ok: false, error: (res.err || 'push failed').trim().slice(0, 400) };
    }
    return { ok: true };
  });
}
