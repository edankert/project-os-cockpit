// The draft home window (FEAT-0160).
//
// A second window beside the present one, on the same sidecars. It shows
// three things and nothing else: what is owed across every project, where a
// phase stands, and what each project's agent is doing. It performs no act
// itself: choosing a row opens the present window at that note, through the
// same `cockpit://` link a deep link uses.
//
// This module runs in main because the per-workspace sidecar URLs live here
// (the same reason agents-fleet.ts does). It only reads: every request below
// is a GET against a sidecar this shell already talks to.

import { BrowserWindow, ipcMain } from 'electron';
import * as path from 'node:path';

import { getAllWorkspaces } from './workspaces';
import { fleetHealth, liveSidecarUrl } from './fleet-health';
import { HomePhase, HomeRelease, trimCriteria, trimPhases, trimRelease } from './home-payload';
import { coldCount, liveCount } from './needs-count';

export interface HomeProject {
  workspaceId: string;
  project: string;
  projectId: string;
  /** False when no sidecar answers for this project. Then `owed` is empty
   *  and `owedCount` carries the number from the last cold pass, if any.
   *  When live, `owedCount` is the sidecar's obligations total. */
  live: boolean;
  /** Why this project could not be read, or null when it was. A project
   *  that was not read is named as such; it is never shown as owing nothing. */
  notRead: string | null;
  /** The sidecar's own landing groups, unchanged: kind, verb, label, items. */
  owed: unknown[];
  owedCount: number | null;
  owedAt: string | null;
  /** Active and planned phases only, with their features trimmed. */
  phases: HomePhase[];
  release: HomeRelease | null;
}

export interface HomePayload { projects: HomeProject[]; generatedAt: number; }

export interface HomeWindowDeps {
  /** Hand a `cockpit://` link to the present window, creating one if none
   *  is open. main.ts owns that window, so it owns this. */
  openInMain: (url: string) => void;
}

const FETCH_MS = 2500;
const CACHE_MS = 3000;
let cache: { at: number; payload: HomePayload } | null = null;
let homeWindow: BrowserWindow | null = null;

async function getJson(url: string): Promise<Record<string, unknown> | null> {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), FETCH_MS);
  try {
    const resp = await fetch(url, { signal: ctl.signal });
    if (!resp.ok) return null;
    return (await resp.json()) as Record<string, unknown>;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

async function owedGroups(base: string): Promise<{ groups: unknown[]; total: number | null } | null> {
  const ob = await getJson(`${base}/api/cockpit/obligations`);
  if (!ob) return null;
  const views = (ob?.views ?? {}) as Record<string, unknown>;
  const owing = Object.keys(views).filter((v) => Number(views[v]) > 0);
  const landings = await Promise.all(
    owing.map((v) => getJson(`${base}/api/cockpit/landing?view=${encodeURIComponent(v)}`)));
  const groups: unknown[] = [];
  for (const landing of landings) {
    // A view that says it owes something and then does not list it means
    // the list is incomplete, so the whole project counts as not read.
    if (!landing || !Array.isArray(landing.groups)) return null;
    groups.push(...(landing.groups as unknown[]));
  }
  // The same count the project line's file carries for this project
  // (needs-count.ts), so the two never disagree (FEAT-0157).
  return { groups, total: liveCount(ob, Date.now()).count };
}

async function buildProject(
  ws: { id: string; root: string; name: string; projectId: string },
): Promise<HomeProject> {
  const row: HomeProject = {
    workspaceId: ws.id, project: ws.name, projectId: ws.projectId,
    live: false, notRead: null, owed: [], owedCount: null, owedAt: null, phases: [], release: null,
  };
  const base = await liveSidecarUrl(ws);
  if (!base) {
    // No sidecar: say what the last cold pass counted, and when. A number
    // with its date is honest; a list this shell cannot fetch would not be.
    const cold = coldCount(fleetHealth().rows.find((r) => r.workspaceId === ws.id)?.digest);
    if (cold.source === 'cold') { row.owedCount = cold.count; row.owedAt = cold.asOf; }
    row.notRead = 'it is not open in the cockpit';
    return row;
  }
  const [owed, stats, release] = await Promise.all([
    owedGroups(base),
    getJson(`${base}/api/cockpit/stats`),
    getJson(`${base}/api/cockpit/release`),
  ]);
  if (owed === null || stats === null) {
    // A sidecar that is up and does not answer is also "not read". An empty
    // list here would say nothing is owed, which nobody checked.
    row.notRead = 'its sidecar did not answer';
    return row;
  }
  row.live = true;
  row.owed = owed.groups;
  row.owedCount = owed.total;
  row.phases = trimPhases(stats);
  row.release = trimRelease(release);
  // What still stands between an active phase and finished is its unticked
  // exit criteria, which the sidecar serves one phase at a time.
  await Promise.all(row.phases.filter((p) => p.status === 'active').map(async (p) => {
    p.exit = trimCriteria(
      await getJson(`${base}/api/cockpit/stats?scope=${encodeURIComponent(p.key)}`), p.key);
  }));
  return row;
}

async function buildPayload(): Promise<HomePayload> {
  const now = Date.now();
  if (cache && now - cache.at < CACHE_MS) return cache.payload;
  const projects = await Promise.all(getAllWorkspaces().map(buildProject));
  const payload: HomePayload = { projects, generatedAt: now };
  cache = { at: now, payload };
  return payload;
}

/** Open the draft home window, or bring the open one forward. One is enough:
 *  it shows every project, so a second copy would show the same thing. */
export function openHomeWindow(): void {
  if (homeWindow && !homeWindow.isDestroyed()) {
    if (homeWindow.isMinimized()) homeWindow.restore();
    homeWindow.show();
    homeWindow.focus();
    return;
  }
  const win = new BrowserWindow({
    // A navigation window: small, and it stays in front of the present
    // window it steers. Edwin, 2026-10-13: "if we want this as separate
    // navigation window then the window should stay on top."
    width: 560,
    height: 660,
    minWidth: 340,
    minHeight: 240,
    title: 'Cockpit home (draft)',
    alwaysOnTop: true,
    fullscreenable: false,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload-home.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });
  homeWindow = win;
  // 'floating' keeps it above ordinary windows without covering the Dock,
  // the menu bar or a system dialog.
  win.setAlwaysOnTop(true, 'floating');
  win.loadFile(path.join(__dirname, '..', 'renderer', 'home.html'));
  win.once('ready-to-show', () => { win.show(); });
  // The page links nowhere. Anything that tries to open a window is refused.
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  win.on('closed', () => { if (homeWindow === win) homeWindow = null; });
}

/** True for the draft home window. The Edit menu asks, because its Copy
 *  is routed to the present window's own handler and would otherwise copy
 *  from the wrong window. */
export function isHomeWindow(win: BrowserWindow | null | undefined): boolean {
  return !!win && win === homeWindow;
}

export function registerHomeWindowIpc(deps: HomeWindowDeps): void {
  ipcMain.handle('home:data', () => buildPayload());

  ipcMain.handle('home:open', (_evt, req: { projectId?: unknown; target?: unknown }): boolean => {
    const projectId = String(req?.projectId ?? '');
    const target = String(req?.target ?? '');
    // Only a project this shell knows, and only a note ID or a path that
    // stays inside the repository. The page is ours, and it is still checked.
    if (!getAllWorkspaces().some((w) => w.projectId === projectId)) return false;
    if (target.split('/').some((seg) => seg === '..' || seg === '.')) return false;
    deps.openInMain(target
      ? `cockpit://${projectId}/${target.split('/').map(encodeURIComponent).join('/')}`
      : `cockpit://${projectId}`);
    return true;
  });
}
