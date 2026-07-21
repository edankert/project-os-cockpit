// Electron main process entry point.
//
// TASK-0058: bare BrowserWindow scaffold.
// TASK-0061: spawn Python sidecar per workspace, load its URL in-window.
// TASK-0063: native terminal pane (node-pty backed) lives in the renderer;
//            cleanup runs through this file's before-quit hook.
// TASK-0064: this file adds menu, single-instance lock, cockpit:// deep
//            links, and window-state persistence.

import { BrowserWindow, Menu, app, clipboard, dialog, ipcMain, shell } from 'electron';
import * as path from 'node:path';

import { registerWorkspaceIpc, getAllWorkspaces } from './ipc/workspaces';
import { registerSidecarIpc, shutdownAllSidecars } from './ipc/sidecar';
import {
  registerTerminalIpc,
  shutdownAllTerminals,
  hasPty,
  isTmuxBacked,
} from './ipc/terminal';
import { registerDispatchIpc } from './ipc/dispatch-queue';
import { registerAgentsFleetIpc } from './ipc/agents-fleet';
import { attachContextMenu } from './ipc/context-menu';
import { registerSettingsIpc } from './ipc/app-settings';
import {
  getLastAgentStates,
  startAgentStatePoller,
  stopAgentStatePoller,
} from './ipc/agent-state-poller';
import * as fsp from 'node:fs/promises';
import { ipcMain as _ipcMainForActiveWs } from 'electron';

// Renderer reports its currently-active workspace via IPC (TASK-0087
// suppression heuristic — don't notify about a workspace the user is
// already looking at). Kept here in main so it's accessible from
// modules other than the renderer.
let activeWorkspaceId: string | null = null;
_ipcMainForActiveWs.on('workspaces:active-changed', (_evt, id: string | null) => {
  activeWorkspaceId = typeof id === 'string' && id.length > 0 ? id : null;
});
import {
  attachWindowStatePersistence,
  loadWindowState,
} from './window-state';

// FEAT-0012 / TASK-0092 — multi-window model. `mainWindow` is always
// the most-recently-focused window (used for IPC popups, menu
// triggers, notifications). `allWindows` carries the full set so we
// can fan agent-state IPC + window-menu listings.
let mainWindow: BrowserWindow | null = null;
const allWindows: Set<BrowserWindow> = new Set();

// Pin userData to the historical path. Electron derives userData from
// app.name; calling app.setName() therefore moves the data dir, which
// in turn loses an existing `workspaces.json`. Lock the directory
// regardless of any name override below.
//
// macOS dev-mode caveat: the bold app name next to the Apple logo is
// sourced from `Electron.app/Contents/Info.plist`'s CFBundleName, not
// from `app.setName()`. It will keep saying "Electron" under
// `npm start` until the app is properly packaged.
app.setPath(
  'userData',
  path.join(app.getPath('appData'), 'project-os-cockpit-desktop'),
);

// Single-instance lock. A second launch (e.g. opening a `cockpit://`
// URL) hits the `second-instance` handler on the first instance
// instead of starting a new app.
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
}

app.on('second-instance', (_event, argv) => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.show();
    mainWindow.focus();
  }
  // Second-instance argv may contain a `cockpit://…` URL from Windows /
  // Linux protocol launches (macOS uses `open-url` below).
  const url = argv.find((a) => a.startsWith('cockpit://'));
  if (url) handleDeepLink(url);
});

// cockpit:// scheme registration. Lets agents / scripts run `open
// cockpit://<workspace-id>/<target>` and surface the desktop window.
if (!app.isDefaultProtocolClient('cockpit')) {
  app.setAsDefaultProtocolClient('cockpit');
}

app.on('open-url', (event, url) => {
  event.preventDefault();
  handleDeepLink(url);
});

function handleDeepLink(url: string): void {
  console.log(`[deeplink] received ${url}`);
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.show();
    mainWindow.focus();
    mainWindow.webContents.send('deeplink', url);
  }
}

function createWindow(): BrowserWindow {
  const state = loadWindowState();
  const win = new BrowserWindow({
    x: state.x,
    y: state.y,
    width: state.width,
    height: state.height,
    minWidth: 900,
    minHeight: 600,
    title: 'project-os-cockpit',
    show: false,
    // hiddenInset (macOS) — traffic lights stay visible but the
    // chrome strip becomes transparent so the app extends to the
    // very edge of the window (FEAT-0009 / TASK-0093).
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  allWindows.add(win);
  mainWindow = win;

  attachWindowStatePersistence(win);
  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  win.once('ready-to-show', () => { win.show(); });

  win.on('focus', () => { mainWindow = win; });

  attachContextMenu(win);

  win.webContents.on('console-message', (_e, level, message, line, sourceId) => {
    const sigil = ['v', 'i', 'w', 'e'][level] ?? '?';
    console.log(`[renderer ${sigil}] ${message}  (${sourceId}:${line})`);
  });

  win.webContents.on('did-fail-load', (_e, code, desc, url) => {
    console.error(`[renderer] did-fail-load: code=${code} desc=${desc} url=${url}`);
  });

  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://127.0.0.1') || url.startsWith('http://localhost')) {
      return { action: 'allow' };
    }
    void shell.openExternal(url);
    return { action: 'deny' };
  });

  win.on('closed', () => {
    allWindows.delete(win);
    if (mainWindow === win) {
      mainWindow = allWindows.size > 0 ? Array.from(allWindows)[allWindows.size - 1] : null;
    }
  });

  return win;
}

// FEAT-0012 / TASK-0090 — context menu templates per surface.
function buildContextTemplate(
  type: string,
  payload: Record<string, unknown>,
): Electron.MenuItemConstructorOptions[] {
  const id = typeof payload.id === 'string' ? payload.id : '';
  const rel = typeof payload.rel === 'string' ? payload.rel : '';
  const root = typeof payload.root === 'string' ? payload.root : '';
  const url = typeof payload.url === 'string' ? payload.url : '';
  const workspaceId = typeof payload.workspaceId === 'string' ? payload.workspaceId : '';

  const sendDispatch = (action: string, data: Record<string, unknown>): void => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('menu:dispatch', { action, ...data });
    }
  };

  switch (type) {
    case 'nav-row':
    case 'doc-link': {
      const items: Electron.MenuItemConstructorOptions[] = [];
      if (rel) {
        items.push({
          label: 'Open', click: () => sendDispatch('navigate', { rel }),
        });
      }
      if (id) {
        items.push({
          label: 'Copy ID', click: () => clipboard.writeText(id),
        });
      }
      if (rel) {
        items.push({
          label: 'Copy path', click: () => clipboard.writeText(rel),
        });
        items.push({ type: 'separator' });
        items.push({
          label: 'Reveal in Finder', click: () => {
            if (workspaceId) {
              // Renderer passes workspace root via `root` so we can
              // resolve the absolute path here.
              if (root) {
                const abs = path.join(root, rel);
                shell.showItemInFolder(abs);
              }
            }
          },
        });
      }
      if (type === 'doc-link' && url) {
        items.push({
          label: 'Copy link', click: () => clipboard.writeText(url),
        });
      }
      // Agent verbs (FEAT-0024 / TASK-0132): the renderer passes the
      // note type's verb list from the registry; the submenu ends with
      // the Claude/Codex preference radios.
      const verbs = Array.isArray(payload.verbs)
        ? (payload.verbs as Array<{ key?: unknown; label?: unknown }>)
            .filter((v) => typeof v?.key === 'string' && typeof v?.label === 'string')
        : [];
      if (verbs.length > 0) {
        const currentAgent = payload.currentAgent === 'codex' ? 'codex' : 'claude';
        const submenu: Electron.MenuItemConstructorOptions[] = verbs.map((v) => ({
          label: String(v.label),
          click: () => sendDispatch('agent-dispatch', { id, rel, verb: v.key, workspaceId }),
        }));
        submenu.push({ type: 'separator' });
        submenu.push({
          label: 'Claude Code', type: 'radio', checked: currentAgent === 'claude',
          click: () => sendDispatch('agent-set', { agent: 'claude' }),
        });
        submenu.push({
          label: 'Codex', type: 'radio', checked: currentAgent === 'codex',
          click: () => sendDispatch('agent-set', { agent: 'codex' }),
        });
        items.push({ type: 'separator' });
        items.push({ label: 'Agent', submenu });
      }
      return items;
    }
    case 'rail': {
      return [
        {
          label: 'Open',
          click: () => sendDispatch('switch-workspace', { workspaceId }),
        },
        {
          label: 'Reveal repo in Finder',
          enabled: !!root,
          click: () => { if (root) shell.openPath(root); },
        },
        {
          label: 'Copy path',
          enabled: !!root,
          click: () => { if (root) clipboard.writeText(root); },
        },
      ];
    }
    default:
      return [];
  }
}

function buildMenu(): void {
  const isMac = process.platform === 'darwin';
  const template: Electron.MenuItemConstructorOptions[] = [
    ...(isMac
      ? [{
          label: app.name,
          submenu: [
            { role: 'about' as const },
            { type: 'separator' as const },
            { role: 'services' as const },
            { type: 'separator' as const },
            { role: 'hide' as const },
            { role: 'hideOthers' as const },
            { role: 'unhide' as const },
            { type: 'separator' as const },
            { role: 'quit' as const },
          ],
        }]
      : []),
    {
      label: 'File',
      submenu: [
        {
          label: 'New Window',
          accelerator: isMac ? 'Cmd+N' : 'Ctrl+N',
          click: () => { createWindow(); },
        },
        { type: 'separator' },
        {
          label: 'Rescan workspaces',
          accelerator: isMac ? 'Cmd+Shift+R' : 'Ctrl+Shift+R',
          click: () => {
            mainWindow?.webContents.send('menu:rescan');
          },
        },
        { type: 'separator' },
        isMac ? { role: 'close' } : { role: 'quit' },
      ],
    },
    { role: 'editMenu' },
    {
      label: 'View',
      submenu: [
        {
          label: 'Back',
          accelerator: isMac ? 'Cmd+[' : 'Alt+Left',
          click: () => { mainWindow?.webContents.send('menu:back'); },
        },
        {
          label: 'Forward',
          accelerator: isMac ? 'Cmd+]' : 'Alt+Right',
          click: () => { mainWindow?.webContents.send('menu:forward'); },
        },
        { type: 'separator' },
        {
          label: 'Toggle Terminal',
          accelerator: isMac ? 'Cmd+`' : 'Ctrl+`',
          click: () => {
            mainWindow?.webContents.send('menu:toggle-terminal');
          },
        },
        { type: 'separator' },
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    { role: 'windowMenu' },
    {
      role: 'help',
      submenu: [
        {
          label: 'About project-os-cockpit',
          click: () => {
            void dialog.showMessageBox({
              type: 'info',
              title: 'project-os-cockpit',
              message: `${app.name} ${app.getVersion()}`,
              detail: 'Electron shell for the project-os cockpit. Renders project-os Markdown notes as a 3-pane viewer; spawns the Python sidecar per workspace.',
              buttons: ['OK'],
            });
          },
        },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

app.whenReady().then(() => {
  buildMenu();
  registerWorkspaceIpc();
  registerSidecarIpc({ getActiveWindow: () => mainWindow });
  registerTerminalIpc({ getActiveWindow: () => mainWindow });
  registerDispatchIpc();
  registerAgentsFleetIpc();
  registerSettingsIpc();

  // Agent-state poller — reads each workspace's
  // .cockpit/agent-state.json every 5 s and fans diffs to the
  // renderer so the rail dots stay live (FEAT-0010 / TASK-0082).
  startAgentStatePoller({
    getWorkspaces: () => getAllWorkspaces(),
    getWindow: () => mainWindow,
    getAllWindows: () => Array.from(allWindows),
    getActiveWorkspaceId: () => activeWorkspaceId,
  });

  // Stale-url janitor (ISS-0007 / TASK-0146): after an unclean exit,
  // `.cockpit/url` files survive pointing at ports another workspace's
  // sidecar may claim next launch — misrouting external hooks and the
  // cockpit CLI. Probe each discovered workspace's url against the
  // sidecar identity endpoint and unlink dead or wrong-root files.
  // A live standalone sidecar answers with its matching root and is
  // left alone. Delayed so the renderer's first workspace listing has
  // populated discovery.
  setTimeout(() => { void janitorStaleUrls(); }, 3000);

  // Renderer asks main to open external URLs in the system browser
  // (FEAT-0011 / TASK-0071). Filter to http(s) only so we don't get
  // tricked into opening file:// or other schemes.
  ipcMain.handle('app:openExternal', async (_evt, url: string) => {
    if (typeof url !== 'string') return { ok: false, error: 'url must be a string' };
    if (!/^https?:\/\//i.test(url)) return { ok: false, error: 'only http(s) URLs allowed' };
    await shell.openExternal(url);
    return { ok: true };
  });

  // FEAT-0016: reveal a directory or file in Finder. Direct handler so
  // the renderer's project-settings popover doesn't need to round-trip
  // through the context-menu IPC just to open a folder.
  ipcMain.handle('app:revealInFinder', async (_evt, abs: string) => {
    if (typeof abs !== 'string' || !abs) return { ok: false, error: 'path required' };
    shell.showItemInFolder(abs);
    return { ok: true };
  });

  // Drag-and-drop file resolver (FEAT-0012 / TASK-0091). Renderer
  // hands us an absolute path; we figure out whether it belongs to
  // an existing workspace and reply with an action.
  ipcMain.handle('app:resolve-dropped-file', async (_evt, absPath: string) => {
    if (typeof absPath !== 'string' || !absPath) {
      return { action: 'ignored', reason: 'no path' };
    }
    if (!absPath.toLowerCase().endsWith('.md')) {
      return { action: 'ignored', reason: 'not a markdown file' };
    }
    const workspaces = getAllWorkspaces();
    for (const ws of workspaces) {
      const docsRoot = path.join(ws.root, 'docs');
      const norm = path.resolve(absPath);
      const docsNorm = path.resolve(docsRoot);
      if (norm === docsNorm || norm.startsWith(docsNorm + path.sep)) {
        return {
          action: 'navigate',
          workspaceId: ws.id,
          rel: path.relative(docsNorm, norm),
        };
      }
    }
    // Walk up looking for a SNAPSHOT.yaml (offer to add the repo).
    let cursor = path.dirname(absPath);
    for (let i = 0; i < 8; i++) {
      try {
        const stat = await (await import('node:fs/promises')).stat(
          path.join(cursor, 'SNAPSHOT.yaml'),
        );
        if (stat.isFile()) {
          return { action: 'offer-add-workspace', root: cursor };
        }
      } catch { /* keep walking */ }
      const parent = path.dirname(cursor);
      if (parent === cursor) break;
      cursor = parent;
    }
    return { action: 'ignored', reason: 'not a project-os note' };
  });

  // Native context menus (FEAT-0012 / TASK-0090).
  // Renderer fires `menu:show-context` with a type + payload; main
  // builds the native menu template, popups it on the active window,
  // and inlines any main-side action (clipboard / Finder). For
  // renderer-side actions (navigate, switch workspace, etc.) we
  // send back an IPC the renderer subscribes to.
  ipcMain.handle('menu:show-context', (_evt, type: string, payload: Record<string, unknown>) => {
    if (!mainWindow) return;
    const template = buildContextTemplate(type, payload);
    if (template.length === 0) return;
    Menu.buildFromTemplate(template).popup({ window: mainWindow });
  });

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

async function janitorStaleUrls(): Promise<void> {
  for (const ws of getAllWorkspaces()) {
    const urlFile = path.join(ws.root, '.cockpit', 'url');
    let url: string;
    try {
      url = (await fsp.readFile(urlFile, 'utf-8')).trim();
    } catch {
      continue; // no url file — nothing to clean
    }
    if (!/^https?:\/\/(127\.0\.0\.1|localhost)[:/]/.test(url)) continue;
    const probe = async (): Promise<'ok' | 'wrong-root' | 'down'> => {
      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 800);
        const resp = await fetch(`${url}/api/cockpit/identity`, { signal: controller.signal });
        clearTimeout(timer);
        if (!resp.ok) return 'down';
        const identity = (await resp.json()) as { root?: string };
        const answeredRoot = (identity.root ?? '').toLowerCase();
        let wsRoot = ws.root;
        try { wsRoot = await fsp.realpath(ws.root); } catch { /* keep raw */ }
        return answeredRoot === wsRoot.toLowerCase() ? 'ok' : 'wrong-root';
      } catch {
        return 'down'; // unreachable (dead port) — classic post-kill leftover
      }
    };
    let verdict = await probe();
    if (verdict === 'down') {
      // One retry: a sidecar spawning right now writes its url a beat
      // before its socket listens — don't unlink a live server's fresh
      // file over that sliver. A wrong-root answer is definitive.
      await new Promise((resolve) => setTimeout(resolve, 1500));
      verdict = await probe();
    }
    if (verdict !== 'ok') {
      try {
        await fsp.unlink(urlFile);
        console.log(`[janitor] removed stale .cockpit/url for ${ws.name}`);
      } catch { /* already gone */ }
    }
  }
}

app.on('window-all-closed', () => {
  // macOS keeps apps alive without windows; other platforms quit.
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', (event) => {
  // Quit guard (ISS-0008 / TASK-0145): fallback (non-tmux) terminals
  // die with us, so a graceful quit while an agent is mid-flight in
  // one deserves a deliberate confirmation. tmux-backed agents keep
  // running headless and reattach next launch — no dialog for them.
  const risky: string[] = [];
  for (const ws of getAllWorkspaces()) {
    const state = getLastAgentStates().get(ws.id);
    if (state !== 'busy' && state !== 'needs-input') continue;
    if (hasPty(ws.id) && !isTmuxBacked(ws.id)) risky.push(ws.name);
  }
  if (risky.length > 0) {
    const choice = dialog.showMessageBoxSync({
      type: 'warning',
      buttons: ['Quit Anyway', 'Cancel'],
      defaultId: 1,
      cancelId: 1,
      message: `Agents are still working in: ${risky.join(', ')}`,
      detail: 'These terminals run directly under the app — quitting kills the agent sessions inside them.',
    });
    if (choice === 1) {
      event.preventDefault();
      return;
    }
  }
  shutdownAllSidecars();
  shutdownAllTerminals();
  stopAgentStatePoller();
});
