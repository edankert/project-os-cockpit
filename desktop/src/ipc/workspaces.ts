// Workspace discovery + persistence (TASK-0060).
//
// A "workspace" is any directory containing a SNAPSHOT.yaml at its root.
// We scan a small list of configured roots (default ~/Dev/repos/),
// depth 2, skip the usual build / vendor directories, and remember the
// resulting list in app.getPath('userData')/workspaces.json so the
// switcher renders instantly on subsequent launches.

import { app, dialog, ipcMain, BrowserWindow } from 'electron';
import * as crypto from 'node:crypto';
import * as fs from 'node:fs/promises';
import type { Dirent } from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import * as yaml from 'js-yaml';

import type { Workspace } from '../types';

const DEFAULT_ROOTS = [path.join(os.homedir(), 'Dev', 'repos')];

console.log(`[workspaces] module init: HOME=${os.homedir()}, default roots=${JSON.stringify(DEFAULT_ROOTS)}`);
const SCAN_DEPTH = 2;
const SKIP_DIRS = new Set([
  'node_modules', '.git', 'target', 'dist', 'build',
  '__pycache__', '.venv', 'venv', '.next', '.cache',
]);

// In-memory cache, populated lazily on first IPC call. The store on
// disk is authoritative; this just avoids re-reading it on every list.
let workspaces: Workspace[] = [];

function storePath(): string {
  return path.join(app.getPath('userData'), 'workspaces.json');
}

interface StoredState {
  workspaces: Workspace[];
  roots?: string[];
}

async function readStore(): Promise<StoredState> {
  try {
    const raw = await fs.readFile(storePath(), 'utf-8');
    const data = JSON.parse(raw) as StoredState;
    return { workspaces: data.workspaces ?? [], roots: data.roots };
  } catch {
    return { workspaces: [] };
  }
}

async function writeStore(state: StoredState): Promise<void> {
  await fs.mkdir(path.dirname(storePath()), { recursive: true });
  await fs.writeFile(storePath(), JSON.stringify(state, null, 2), 'utf-8');
}

function idFor(repoRoot: string): string {
  // 16-char hex prefix is short enough to display and collision-safe
  // for the realistic workspace count on one machine.
  return crypto
    .createHash('sha1')
    .update(path.resolve(repoRoot))
    .digest('hex')
    .slice(0, 16);
}

// Probe a workspace root for a project icon. Tries the common
// conventions: explicit `icon.*` / `logo.*` at the root, a project-os
// `.cockpit/icon.*`, then web `favicon` locations. Returns a data URI
// suitable for `<img src="…">` (or null if none found / too large).
const ICON_PROBES: ReadonlyArray<readonly [string, string]> = [
  ['icon.svg',  'image/svg+xml'],
  ['icon.png',  'image/png'],
  ['logo.svg',  'image/svg+xml'],
  ['logo.png',  'image/png'],
  ['.cockpit/icon.svg', 'image/svg+xml'],
  ['.cockpit/icon.png', 'image/png'],
  ['public/favicon.svg', 'image/svg+xml'],
  ['public/favicon.png', 'image/png'],
  ['public/favicon.ico', 'image/x-icon'],
  ['static/favicon.svg', 'image/svg+xml'],
  ['static/favicon.png', 'image/png'],
  ['static/favicon.ico', 'image/x-icon'],
  ['apple-touch-icon.png', 'image/png'],
  ['favicon.svg', 'image/svg+xml'],
  ['favicon.png', 'image/png'],
  ['favicon.ico', 'image/x-icon'],
];
const ICON_MAX_BYTES = 200 * 1024;  // 200 KB sanity cap

async function findWorkspaceIcon(repoRoot: string): Promise<string | undefined> {
  for (const [rel, mime] of ICON_PROBES) {
    const abs = path.join(repoRoot, rel);
    try {
      const stat = await fs.stat(abs);
      if (!stat.isFile() || stat.size > ICON_MAX_BYTES) continue;
      const buf = await fs.readFile(abs);
      return `data:${mime};base64,${buf.toString('base64')}`;
    } catch {
      // missing / unreadable — try next candidate
    }
  }
  return undefined;
}

async function readSnapshotName(repoRoot: string): Promise<string | null> {
  try {
    const raw = await fs.readFile(
      path.join(repoRoot, 'SNAPSHOT.yaml'), 'utf-8',
    );
    const data = yaml.load(raw) as
      | { project?: { name?: string } } | null;
    return data?.project?.name ?? null;
  } catch {
    return null;
  }
}

async function readEntries(dir: string): Promise<Dirent[]> {
  try {
    return await fs.readdir(dir, { withFileTypes: true });
  } catch {
    return [];
  }
}

async function hasSnapshot(dir: string): Promise<boolean> {
  try {
    const stat = await fs.stat(path.join(dir, 'SNAPSHOT.yaml'));
    return stat.isFile();
  } catch {
    return false;
  }
}

async function* walk(root: string, depth: number): AsyncGenerator<string> {
  if (depth < 0) return;
  for (const entry of await readEntries(root)) {
    if (!entry.isDirectory()) continue;
    if (SKIP_DIRS.has(entry.name)) continue;
    if (entry.name.startsWith('.')) continue;
    const full = path.join(root, entry.name);
    if (await hasSnapshot(full)) {
      yield full;
      // Don't descend into a discovered workspace — nested project-os
      // repos are vanishingly rare and would just create noise.
      continue;
    }
    yield* walk(full, depth - 1);
  }
}

async function discoverWorkspaces(roots: string[]): Promise<Workspace[]> {
  const found = new Map<string, Workspace>();
  for (const root of roots) {
    console.log(`[workspaces] scanning root: ${root}`);
    let count = 0;
    for await (const repoRoot of walk(root, SCAN_DEPTH)) {
      const id = idFor(repoRoot);
      const name = (await readSnapshotName(repoRoot)) ?? path.basename(repoRoot);
      const icon = await findWorkspaceIcon(repoRoot);
      console.log(`[workspaces]   found ${name} at ${repoRoot}${icon ? ' (icon)' : ''}`);
      found.set(id, {
        id,
        root: repoRoot,
        name,
        lastOpened: null,
        pinned: false,
        icon,
      });
      count += 1;
    }
    console.log(`[workspaces] root ${root} → ${count} workspace(s)`);
  }
  return Array.from(found.values()).sort((a, b) =>
    a.name.localeCompare(b.name),
  );
}

async function loadStored(): Promise<Workspace[]> {
  // FEAT-0016: auto-discovery on first launch removed. The user adds
  // workspaces manually via the rail `+` button. Stored entries are
  // verified to still point at real SNAPSHOT.yaml files; stale ones
  // are dropped silently. Icons are backfilled for entries missing
  // them (probe ran after the file was originally written).
  const stored = await readStore();
  const alive: Workspace[] = [];
  for (const ws of stored.workspaces) {
    if (!(await hasSnapshot(ws.root))) continue;
    if (!ws.icon) {
      const icon = await findWorkspaceIcon(ws.root);
      if (icon) ws.icon = icon;
    }
    alive.push(ws);
  }
  return alive;
}

async function persist(): Promise<void> {
  const stored = await readStore();
  await writeStore({ workspaces, roots: stored.roots });
}

async function buildWorkspace(repoRoot: string): Promise<Workspace> {
  const id = idFor(repoRoot);
  const name = (await readSnapshotName(repoRoot)) ?? path.basename(repoRoot);
  const icon = await findWorkspaceIcon(repoRoot);
  return { id, root: repoRoot, name, lastOpened: null, pinned: false, icon };
}

export function getWorkspace(id: string): Workspace | null {
  return workspaces.find((w) => w.id === id) ?? null;
}

export function getAllWorkspaces(): Workspace[] {
  // Returns a snapshot — callers (e.g. the agent-state poller) should
  // not retain references.
  return workspaces.slice();
}

export async function markOpened(id: string): Promise<void> {
  const ws = getWorkspace(id);
  if (!ws) return;
  ws.lastOpened = new Date().toISOString();
  const stored = await readStore();
  await writeStore({ workspaces, roots: stored.roots });
}

export function registerWorkspaceIpc(): void {
  ipcMain.handle('workspaces:list', async (): Promise<Workspace[]> => {
    console.log(`[workspaces] list called (cached: ${workspaces.length})`);
    if (workspaces.length === 0) {
      try {
        workspaces = await loadStored();
      } catch (err) {
        console.error('[workspaces] loadStored threw:', err);
        return [];
      }
    }
    console.log(`[workspaces] returning ${workspaces.length} workspace(s)`);
    return workspaces;
  });

  // Rescan is no longer auto-discovery (FEAT-0016). It just refreshes
  // the alive-list (drop stale entries, backfill icons). Manual adds
  // are explicit via workspaces:pickAndAdd.
  ipcMain.handle('workspaces:rescan', async (): Promise<Workspace[]> => {
    workspaces = await loadStored();
    await persist();
    return workspaces;
  });

  // ----- FEAT-0016: manual CRUD --------------------------------------

  // Native directory picker → either a single project (if it has
  // SNAPSHOT.yaml) or recursive scan of its descendants. Returns the
  // updated list + a small summary describing what happened so the
  // renderer can surface it.
  ipcMain.handle('workspaces:pickAndAdd', async (evt): Promise<{
    workspaces: Workspace[];
    added: number;
    skipped: number;
    cancelled: boolean;
    error?: string;
  }> => {
    const window = BrowserWindow.fromWebContents(evt.sender);
    const res = await dialog.showOpenDialog(window ?? undefined!, {
      title: 'Add project',
      message: 'Pick a project root (folder with SNAPSHOT.yaml) or a parent folder to scan.',
      properties: ['openDirectory', 'createDirectory'],
    });
    if (res.canceled || res.filePaths.length === 0) {
      return { workspaces, added: 0, skipped: 0, cancelled: true };
    }
    const picked = res.filePaths[0];
    const found: string[] = [];
    if (await hasSnapshot(picked)) {
      found.push(picked);
    } else {
      for await (const repoRoot of walk(picked, SCAN_DEPTH)) {
        found.push(repoRoot);
      }
    }
    if (found.length === 0) {
      return { workspaces, added: 0, skipped: 0, cancelled: false,
        error: 'No SNAPSHOT.yaml found in the selected folder or its descendants.' };
    }
    const existingIds = new Set(workspaces.map((w) => w.id));
    let added = 0;
    let skipped = 0;
    for (const repoRoot of found) {
      const id = idFor(repoRoot);
      if (existingIds.has(id)) { skipped += 1; continue; }
      workspaces.push(await buildWorkspace(repoRoot));
      added += 1;
    }
    workspaces.sort((a, b) => a.name.localeCompare(b.name));
    await persist();
    return { workspaces, added, skipped, cancelled: false };
  });

  // Patch user overrides (rename / userIcon). Identity fields stay
  // immutable here — caller can't move a workspace's root via update.
  ipcMain.handle('workspaces:update', async (
    _evt,
    patch: {
      id: string;
      userName?: string | null;
      userIcon?: string | null;
      userEmoji?: string | null;
      userColor?: string | null;
    },
  ): Promise<{ ok: boolean }> => {
    const ws = workspaces.find((w) => w.id === patch.id);
    if (!ws) return { ok: false };
    const applyStr = (key: 'userName' | 'userIcon' | 'userEmoji' | 'userColor',
                     val: string | null | undefined): void => {
      if (val === undefined) return;
      if (val === null || val === '') delete ws[key];
      else ws[key] = val;
    };
    applyStr('userName',  patch.userName);
    applyStr('userIcon',  patch.userIcon);
    applyStr('userEmoji', patch.userEmoji);
    applyStr('userColor', patch.userColor);
    await persist();
    return { ok: true };
  });

  ipcMain.handle('workspaces:remove', async (_evt, id: string): Promise<{ ok: boolean }> => {
    const idx = workspaces.findIndex((w) => w.id === id);
    if (idx < 0) return { ok: false };
    workspaces.splice(idx, 1);
    await persist();
    return { ok: true };
  });

  // Image file picker for the userIcon. Returns a data URI capped at
  // ICON_MAX_BYTES. The caller chains this with workspaces:update.
  // When given a workspaceId, the picker starts in that workspace's
  // root so the user can grab an icon out of the project itself.
  ipcMain.handle('workspaces:pickIcon', async (evt, opts?: { workspaceId?: string }): Promise<{
    ok: boolean; dataUri?: string; error?: string;
  }> => {
    const window = BrowserWindow.fromWebContents(evt.sender);
    const ws = opts?.workspaceId ? workspaces.find((w) => w.id === opts.workspaceId) : null;
    const res = await dialog.showOpenDialog(window ?? undefined!, {
      title: 'Choose project icon',
      properties: ['openFile'],
      filters: [{ name: 'Images', extensions: ['png', 'svg', 'jpg', 'jpeg', 'ico', 'webp'] }],
      defaultPath: ws?.root,
    });
    if (res.canceled || res.filePaths.length === 0) return { ok: false, error: 'cancelled' };
    const file = res.filePaths[0];
    try {
      const stat = await fs.stat(file);
      if (stat.size > ICON_MAX_BYTES) {
        return { ok: false, error: `image too large (max ${ICON_MAX_BYTES / 1024} KB)` };
      }
      const buf = await fs.readFile(file);
      const ext = path.extname(file).toLowerCase().slice(1);
      const mimeMap: Record<string, string> = {
        png: 'image/png', svg: 'image/svg+xml', jpg: 'image/jpeg',
        jpeg: 'image/jpeg', ico: 'image/x-icon', webp: 'image/webp',
      };
      const mime = mimeMap[ext] ?? 'application/octet-stream';
      return { ok: true, dataUri: `data:${mime};base64,${buf.toString('base64')}` };
    } catch (err) {
      return { ok: false, error: String(err) };
    }
  });
}
