// Electron main process entry point.
//
// TASK-0058: bare BrowserWindow scaffold.
// TASK-0061: spawn Python sidecar per workspace, load its URL in-window.
// TASK-0063: native terminal pane (node-pty backed) lives in the renderer;
//            cleanup runs through this file's before-quit hook.
// TASK-0064: this file adds menu, single-instance lock, cockpit:// deep
//            links, and window-state persistence.

import { BrowserWindow, Menu, app, clipboard, desktopCapturer, dialog, ipcMain, shell, systemPreferences } from 'electron';
import { spawn } from 'node:child_process';
import * as fs from 'node:fs/promises';
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
import { registerFleetHealthIpc, stopFleetHealth } from './ipc/fleet-health';
import { registerClipboardIpc } from './ipc/clipboard';
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
        // Preserve whatever the renderer says is current, even if this build
        // does not recognise it: coercing to 'claude' ticked the wrong radio
        // and made a third agent unselectable (ISS-0032).
        const currentAgent = typeof payload.currentAgent === 'string'
          ? payload.currentAgent : '';
        const menuAgents = Array.isArray(payload.agents) && payload.agents.length
          ? payload.agents as Array<{ id: string; label: string }>
          : [{ id: 'claude', label: 'Claude Code' }, { id: 'codex', label: 'Codex' }];
        const submenu: Electron.MenuItemConstructorOptions[] = verbs.map((v) => ({
          label: String(v.label),
          click: () => sendDispatch('agent-dispatch', { id, rel, verb: v.key, workspaceId }),
        }));
        submenu.push({ type: 'separator' });
        // Built from the registry, not two literals (ISS-0032): adding an agent
        // is one entry in agents.py, not an edit here as well.
        for (const a of menuAgents) {
          submenu.push({
            label: a.label, type: 'radio', checked: currentAgent === a.id,
            click: () => sendDispatch('agent-set', { agent: a.id }),
          });
        }
        items.push({ type: 'separator' });
        items.push({ label: 'Agent', submenu });
      }
      return items;
    }
    // TASK-0234. Triage is first and Discard is last and separated: the
    // convention's goal is that the inbox empties by being *filed*, and
    // discarding is the irreversible one.
    case 'inbox-item': {
      const name = typeof payload.name === 'string' ? payload.name : '';
      if (!name) return [];
      const abs = root ? path.join(root, 'inbox', name) : '';
      return [
        {
          label: 'Triage this item',
          click: () => sendDispatch('inbox-triage', { name, workspaceId }),
        },
        {
          label: 'Open',
          click: () => sendDispatch('inbox-open', { name }),
        },
        { type: 'separator' },
        {
          label: 'Reveal in Finder',
          enabled: !!abs,
          click: () => { if (abs) shell.showItemInFolder(abs); },
        },
        {
          label: 'Copy name',
          click: () => clipboard.writeText(name),
        },
        { type: 'separator' },
        {
          label: 'Discard',
          click: () => sendDispatch('inbox-discard', { name }),
        },
      ];
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
    // Edit — Cut/Undo/Select-All keep their roles, but Copy and Paste
    // are CONTEXT-AWARE (FEAT-0054 / TASK-0263).
    //
    // `role: 'copy'` runs `webContents.copy()`, which can only see a DOM
    // selection. xterm's selection is not one, so the role could never
    // serve the console — and on macOS a menu accelerator fires BEFORE
    // the page's keydown, so the renderer's own ⌘C/⌘V handling was
    // racing something it could not win, and ⌘V could fire twice.
    //
    // These ask the renderer instead. It knows which pane has focus and
    // routes to the terminal or the document accordingly, so there is
    // one path and the accelerators still appear in the menu.
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        {
          label: 'Copy',
          accelerator: 'CmdOrCtrl+C',
          click: () => {
            if (mainWindow && !mainWindow.isDestroyed()) {
              mainWindow.webContents.send('menu:edit', { action: 'copy' });
            }
          },
        },
        {
          label: 'Paste',
          accelerator: 'CmdOrCtrl+V',
          click: () => {
            if (mainWindow && !mainWindow.isDestroyed()) {
              mainWindow.webContents.send('menu:edit', { action: 'paste' });
            }
          },
        },
        { type: 'separator' },
        { role: 'selectAll' },
      ],
    },
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
          // Rehomed from the console's context menu, which ISS-0080
          // deleted. It was the only action there with no other route.
          label: 'Restart Console',
          click: () => {
            mainWindow?.webContents.send('menu:restart-terminal');
          },
        },
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
  // Per-workspace validator state across the fleet (FEAT-0028 / TASK-0248).
  registerFleetHealthIpc({ getAllWindows: () => Array.from(allWindows) });
  registerSettingsIpc();
  // One clipboard path for the whole app (FEAT-0054 / TASK-0261).
  registerClipboardIpc();

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

  // Take a screenshot straight into the active project's inbox (FEAT-0045).
  //
  // `screencapture -i` is the same interactive selection ⌘⇧4 gives, so the
  // muscle memory is unchanged — but the file lands in the project instead of
  // on the Desktop, which is the whole point: the step this removes is not the
  // capture, it is the filing afterwards.
  //
  // Writing straight to the destination rather than via the clipboard means
  // there is no intermediate state to lose, and no dependency on the user
  // remembering which of the four capture shortcuts copies rather than saves.
  ipcMain.handle('app:capture-screenshot', async (_evt, ...args: unknown[]) => {
    const ws = getAllWorkspaces().find((w) => w.id === (args[0] as string));
    if (!ws) return { ok: false, error: 'no active workspace' };
    const dir = path.join(ws.root, 'inbox');
    const stamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const target = path.join(dir, `${stamp}-screenshot.png`);
    try {
      await fs.mkdir(dir, { recursive: true });
    } catch (err) {
      return { ok: false, error: String(err) };
    }
    // macOS attributes screen capture to the app that SPAWNS `screencapture`,
    // not to the CLI. In dev that is Electron itself, under node_modules —
    // which is not the name anyone looks for in the settings list, so the
    // message below names it explicitly.
    const capturedBy = app.isPackaged ? app.getName() : 'Electron';
    const screenAccess = (): string => (process.platform === 'darwin'
      ? systemPreferences.getMediaAccessStatus('screen')
      : 'granted');

    // ASK, rather than only reporting. Until something requests screen
    // capture macOS has no TCC entry for this app, and System Settings shows
    // no row to enable — Edwin hit exactly that: the message told him to
    // enable "Electron" in a list that did not contain it. `screencapture`
    // cannot register us, because it is an Apple-signed system binary and the
    // permission attaches to it, not to its caller. `desktopCapturer` is the
    // one API here that makes the request in the cockpit's own name.
    if (process.platform === 'darwin' && screenAccess() !== 'granted') {
      try {
        // 1x1 thumbnails: the request is the point, the pixels are not.
        await desktopCapturer.getSources({
          types: ['screen'], thumbnailSize: { width: 1, height: 1 },
        });
      } catch { /* the prompt is the outcome we wanted; sources are not */ }
    }
    const access = screenAccess();
    const permissionHint = access === 'granted'
      // Granted since this process started: TCC is per-process at launch, so
      // the running app still cannot capture until it is restarted. Saying
      // "grant the permission" here would be advice already taken.
      ? `Screen recording is now granted to ${capturedBy}, but this window `
        + `started before that. Restart the cockpit and try again.`
      : `macOS has not granted screen recording to ${capturedBy}. Look for `
        + `\u201c${capturedBy}\u201d in System Settings \u203a Privacy & `
        + `Security \u203a Screen Recording \u2014 if it is not listed, add `
        + `it with \u201c+\u201d from ${process.execPath.replace(/\/Contents\/MacOS\/.*$/, '')} `
        + `\u2014 then restart the cockpit.`;

    return await new Promise((resolve) => {
      // -i interactive, -o no window shadow. No -c: straight to the file, so
      // there is no intermediate clipboard state to lose.
      //
      // Deliberately still spawned when `access` is not 'granted': on
      // 'not-determined' this is what makes macOS show the permission prompt
      // in the first place. Short-circuiting would mean the prompt never
      // appears and the feature can never start working.
      const child = spawn('screencapture', ['-i', '-o', target]);
      let stderr = '';
      child.stderr?.on('data', (d) => { stderr += String(d); });
      child.on('error', (err) => resolve({ ok: false, error: String(err) }));
      child.on('close', async (code) => {
        // THREE outcomes, not two. A first cut checked only whether the file
        // existed and reported everything else as `cancelled` — so a macOS
        // Screen Recording denial, which is the first thing anyone hits on a
        // new machine, would have told the user they cancelled something they
        // never started. `screencapture` exits 0 and writes nothing when the
        // user presses Escape, and exits non-zero with a message when it
        // genuinely fails.
        let exists = false;
        try { await fs.access(target); exists = true; } catch { /* absent */ }
        if (exists) {
          resolve({ ok: true, name: path.basename(target) });
          return;
        }
        if (code === 0 && !stderr.trim()) {
          resolve({ ok: false, cancelled: true });
          return;
        }
        // "could not create image from rect" is what macOS actually says when
        // the permission is missing. Reported raw it reads like a geometry bug
        // and sends you looking at the selection rectangle — Edwin hit exactly
        // this. The hint was already written but sat in the `||` fallback, so
        // it could only appear when stderr was EMPTY, which is the one case
        // where this is not the cause.
        const raw = stderr.trim();
        const isPermission = access !== 'granted'
          || /could not create image|not authori[sz]ed|permission/i.test(raw);
        resolve({
          ok: false,
          error: isPermission
            ? permissionHint
            : (raw || `screencapture exited ${code}`),
        });
      });
    });
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
  stopFleetHealth();
});
