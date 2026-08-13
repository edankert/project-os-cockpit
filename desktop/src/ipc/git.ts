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

/** What a repo has that its remote does not, and what kind of remote
 *  that is (TASK-0415 / ISS-0156).
 *
 *  `ahead` is null when there is no upstream to be ahead **of**, which
 *  is not the same as being up to date and must never render as such.
 *
 *  Lives here, beside the push, on purpose: this module already owns
 *  the backup/deploy classification because it is the process that runs
 *  `git push` and will not trust a classification that arrived over
 *  IPC. The count and the classification are the same question asked of
 *  the same repo, so they are answered in one place.
 */
export async function probeGitState(root: string): Promise<{
  ahead: number | null;
  remote: string | null;
  remoteKind: 'backup' | 'deploy' | 'none';
}> {
  // 5s, not the push's 60s: this runs for every workspace on a timer,
  // and a hung git on one repo must not stall the fleet.
  const remote = await run(root, ['remote', 'get-url', 'origin'], 5_000);
  let url = remote.ok ? remote.out.trim() : '';
  if (!url) {
    // No `origin`, but there may be another remote — and if it is a
    // deploy target, that is precisely what the caller needs to know.
    const all = await run(root, ['remote'], 5_000);
    const first = (all.ok ? all.out : '').split('\n').map((s) => s.trim()).filter(Boolean)[0];
    if (first) {
      const other = await run(root, ['remote', 'get-url', first], 5_000);
      url = other.ok ? other.out.trim() : '';
    }
  }
  const kind = remoteKind(url);
  if (kind === 'none') return { ahead: null, remote: null, remoteKind: 'none' };

  const counted = await run(root, ['rev-list', '--count', '@{u}..HEAD'], 5_000);
  const parsed = counted.ok ? Number.parseInt(counted.out.trim(), 10) : Number.NaN;
  return {
    // A branch with no upstream fails the count. Null, not zero: "I
    // cannot tell" and "nothing to publish" are different answers and
    // only one of them is reassuring.
    ahead: Number.isFinite(parsed) ? parsed : null,
    remote: url || null,
    remoteKind: kind,
  };
}

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
