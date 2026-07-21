// Renderer entry — workspace switcher + cockpit mount (TASK-0060 + TASK-0061).
//
// NOTE: This file deliberately has NO `import` / `export` statements.
// tsc's `module: CommonJS` setting emits CommonJS module wrappers for
// any file with imports/exports, and `exports`/`require` are NOT
// defined in the renderer's plain `<script>` context. Keeping this
// file as a top-level script avoids needing a bundler or a separate
// tsconfig for the renderer. Types are inlined below.
//
// All Node / Electron access is routed through `window.cockpit`
// (defined in preload.ts). This script runs in the sandboxed renderer
// context.

interface Workspace {
  id: string;
  root: string;
  name: string;
  lastOpened: string | null;
  pinned: boolean;
  icon?: string;
  userName?: string;
  userIcon?: string;
  userEmoji?: string;
  userColor?: string;
}

function effectiveName(ws: Workspace): string {
  return ws.userName && ws.userName.length > 0 ? ws.userName : ws.name;
}

interface SidecarReadyPayload {
  workspaceId: string;
  port: number;
  url: string;
}

interface SidecarFailedPayload {
  workspaceId: string;
  reason: string;
  stderrTail?: string;
}

interface SidecarExitedPayload {
  workspaceId: string;
  code: number | null;
  signal: NodeJS.Signals | null;
}

interface AgentStatePayload {
  state: string;
  ts: string;
  target?: string;
  agent?: string;
  message?: string;
  decayed_from?: string;
}

interface QueuedDispatch {
  id: string; rel: string; verb?: string;
  agent: 'claude' | 'codex'; prompt: string; ts: string;
}

interface CockpitApi {
  workspaces: {
    list: () => Promise<Workspace[]>;
    rescan: () => Promise<Workspace[]>;
    open: (id: string) => Promise<{ ok: boolean; error?: string }>;
    onAgentState: (
      cb: (ev: { workspaceId: string; payload: AgentStatePayload | null }) => void,
    ) => () => void;
    onSwitchTo: (
      cb: (ev: { workspaceId: string }) => void,
    ) => () => void;
    notifyActiveChanged: (id: string | null) => void;
    pickAndAdd: () => Promise<{
      workspaces: Workspace[]; added: number; skipped: number;
      cancelled: boolean; error?: string;
    }>;
    update: (patch: {
      id: string;
      userName?: string | null;
      userIcon?: string | null;
      userEmoji?: string | null;
      userColor?: string | null;
    }) => Promise<{ ok: boolean }>;
    remove: (id: string) => Promise<{ ok: boolean }>;
    pickIcon: (workspaceId?: string) => Promise<{ ok: boolean; dataUri?: string; error?: string }>;
  };
  sidecar: {
    onEvent: (
      cb: (ev: { kind: string; payload?: unknown }) => void,
    ) => () => void;
  };
  menu: {
    onRescan: (cb: () => void) => () => void;
    onToggleTerminal: (cb: () => void) => () => void;
    onBack: (cb: () => void) => () => void;
    onForward: (cb: () => void) => () => void;
  };
  agent: {
    onFocus: (cb: (payload: unknown) => void) => () => void;
    onDispatchSelection: (cb: (text: string) => void) => () => void;
  };
  agents: {
    fleet: () => Promise<FleetPayload>;
    sessions: (workspaceId: string) => Promise<AgentSessionSlim[]>;
  };
  app: {
    openExternal: (url: string) => Promise<{ ok: boolean; error?: string }>;
    revealInFinder: (abs: string) => Promise<{ ok: boolean; error?: string }>;
    showContextMenu: (type: string, payload: Record<string, unknown>) => Promise<void>;
    onMenuDispatch: (
      cb: (ev: { action: string } & Record<string, unknown>) => void,
    ) => () => void;
    resolveDroppedFile: (absPath: string) => Promise<{
      action: 'navigate' | 'offer-add-workspace' | 'ignored';
      workspaceId?: string;
      rel?: string;
      root?: string;
      reason?: string;
    }>;
  };
  deeplink: {
    onUrl: (cb: (url: string) => void) => () => void;
  };
  settings: {
    get: () => Promise<{ externalHook: boolean }>;
    set: (patch: Record<string, unknown>) => Promise<{ ok: boolean; error?: string; settings: { externalHook: boolean } }>;
  };
  dispatch: {
    execute: (workspaceId: string, item: unknown) => Promise<{ queued: boolean; delivered?: string; warning?: string; error?: string }>;
    list: (workspaceId: string) => Promise<QueuedDispatch[]>;
    remove: (workspaceId: string, index: number) => Promise<QueuedDispatch[]>;
    clear: (workspaceId: string) => Promise<QueuedDispatch[]>;
    poke: (workspaceId: string, state: string) => void;
    onQueueChanged: (cb: (ev: { workspaceId: string; items: QueuedDispatch[] }) => void) => () => void;
    onDelivered: (cb: (ev: { workspaceId: string; item: QueuedDispatch; mode: string; warning?: string }) => void) => () => void;
  };
  terminal: {
    spawn: (opts: { workspaceId: string; cwd?: string; cols?: number; rows?: number }) => Promise<{ ok: boolean; error?: string }>;
    attach: (workspaceId: string) => Promise<{ ok: boolean; error?: string; backlog: string }>;
    write: (workspaceId: string, data: string) => void;
    resize: (workspaceId: string, cols: number, rows: number) => void;
    dispose: (workspaceId: string) => Promise<{ ok: boolean }>;
    onData: (cb: (ev: { workspaceId: string; data: string }) => void) => () => void;
    onExit: (cb: (info: { workspaceId: string; exitCode: number; signal?: number }) => void) => () => void;
  };
}

// Ambient declarations for the UMD-loaded xterm + addon-fit globals.
// (Renderer is a non-module script, so we can't `import` them — they're
// loaded via `<script>` tags in index.html.)
//
// xterm UMD assigns each named export directly to `window`, so the
// `Terminal` class is reachable as a global. addon-fit's UMD assigns
// the whole module object to `window.FitAddon`, so the class itself
// lives at `FitAddon.FitAddon`. Different shapes, hence the asymmetric
// declarations below.
declare const Terminal: new (options?: Record<string, unknown>) => XtermTerminal;
declare const FitAddon: { FitAddon: new () => XtermFitAddon };

interface XtermTerminal {
  open(elem: HTMLElement): void;
  write(data: string | Uint8Array): void;
  loadAddon(addon: unknown): void;
  onData(cb: (data: string) => void): void;
  onResize(cb: (size: { cols: number; rows: number }) => void): void;
  readonly cols: number;
  readonly rows: number;
  dispose(): void;
  focus(): void;
  reset(): void;
  clear(): void;
  getSelection(): string;
  hasSelection(): boolean;
  selectAll(): void;
  onSelectionChange(cb: () => void): void;
  /** xterm.js: mutating `options.theme` re-paints the visible buffer. */
  options: { theme?: Record<string, string> };
}

interface XtermFitAddon {
  fit(): void;
  proposeDimensions(): { cols: number; rows: number } | undefined;
}

// Pull the API off `window` via a single typed cast so the rest of the
// file is plain typed code.
const cockpitApi = (window as unknown as { cockpit: CockpitApi }).cockpit;

// Bridge: base.css uses `[data-theme="dark"]` to activate the dark
// palette (mode-1 cockpit.js toggles this from a UI control). Until
// FEAT-0009 wires a proper theme picker, mirror the OS preference
// straight onto <html> so the metadata-strip + body content match
// the native chrome.
// Theme picker (FEAT-0009 / TASK-0095). Override `prefers-color-scheme`
// when the user picks an explicit theme via the status-bar buttons.
type ThemePref = 'system' | 'light' | 'dark';

function loadStoredTheme(): ThemePref {
  try {
    const v = localStorage.getItem('cockpit:theme');
    if (v === 'light' || v === 'dark' || v === 'system') return v;
  } catch { /* localStorage unavailable */ }
  return 'system';
}

let themePref: ThemePref = loadStoredTheme();

function applyTheme(): void {
  const dark = themePref === 'dark'
    || (themePref === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  // Repaint the xterm if one's been spawned — its palette is JS-driven,
  // not CSS-driven (FEAT-0015 user feedback). Guarded against the
  // temporal-dead-zone: applyTheme() runs at module init before `term`
  // is declared, so reading it would throw a ReferenceError.
  try {
    if (term) term.options.theme = currentTerminalTheme();
  } catch { /* term not yet declared */ }
}

function setThemePref(pref: ThemePref): void {
  themePref = pref;
  try { localStorage.setItem('cockpit:theme', pref); } catch { /* ignore */ }
  applyTheme();
  // After DOM is ready (and DOM lookups have run) the theme buttons
  // exist — keep this guarded so the initial call doesn't crash if
  // it fires before the listeners are wired.
  refreshThemeButtons();
}

function refreshThemeButtons(): void {
  document.querySelectorAll<HTMLButtonElement>('.sf-theme-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.theme === themePref);
  });
}

applyTheme();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);

function $<T extends Element>(sel: string): T {
  const el = document.querySelector(sel);
  if (!el) throw new Error(`missing element: ${sel}`);
  return el as T;
}

const listEl       = $<HTMLUListElement>('#workspace-list');
const wsRailAdd    = $<HTMLButtonElement>('#ws-rail-add');
const leftPaneCollapseBtn = $<HTMLButtonElement>('#left-pane-collapse');
const hideCompletedBtn    = $<HTMLButtonElement>('#hide-completed-toggle');
const followBtn           = document.getElementById('follow-toggle') as HTMLButtonElement | null;
const platformBarEl       = $<HTMLDivElement>('#platform-bar');
const platformCombo       = $<HTMLDivElement>('#platform-combo');
const platformLabel       = $<HTMLSpanElement>('#platform-label');
const platformMenu        = $<HTMLUListElement>('#platform-menu');
const wsNavProject        = $<HTMLElement>('#ws-nav-project');
const wsNavProjectIcon    = $<HTMLSpanElement>('#ws-nav-project-icon');
const wsNavProjectName    = $<HTMLSpanElement>('#ws-nav-project-name');
const projectSettingsBtn  = $<HTMLButtonElement>('#project-settings-btn');
const projectSettingsMenu = $<HTMLDivElement>('#project-settings-menu');
const psmName             = $<HTMLInputElement>('#psm-name');
const psmPickIcon         = $<HTMLButtonElement>('#psm-pick-icon');
const psmEmoji            = $<HTMLInputElement>('#psm-emoji');
const psmSwatches         = $<HTMLDivElement>('#psm-swatches');
const psmResetIcon        = $<HTMLButtonElement>('#psm-reset-icon');
const psmReveal           = $<HTMLButtonElement>('#psm-reveal');
const psmRemove           = $<HTMLButtonElement>('#psm-remove');
const placeholder  = $<HTMLDivElement>('#placeholder');
const docView      = $<HTMLElement>('#doc-view');
const statusBar    = $<HTMLDivElement>('#status-bar');
const terminalBtn  = $<HTMLButtonElement>('#terminal-toggle');
const terminalPane = $<HTMLDivElement>('#terminal-pane');
const terminalMount = $<HTMLDivElement>('#terminal-mount');
const terminalDivider = $<HTMLDivElement>('#terminal-divider');
const wsNavPlaceholder = $<HTMLDivElement>('#ws-nav-placeholder');
const wsNavContent = $<HTMLDivElement>('#ws-nav-content');
const appEl = $<HTMLDivElement>('#app');
const rightPaneToggle = $<HTMLButtonElement>('#right-pane-toggle');
const rightPaneContent = $<HTMLDivElement>('#right-pane-content');
const quickSwitchEl = $<HTMLDivElement>('#quick-switch');
const quickSwitchInput = $<HTMLInputElement>('#quick-switch-input');
const quickSwitchResults = $<HTMLUListElement>('#quick-switch-results');
const findBar = $<HTMLDivElement>('#find-bar');
const findInput = $<HTMLInputElement>('#find-input');
const findCount = $<HTMLSpanElement>('#find-count');
const findPrevBtn = $<HTMLButtonElement>('#find-prev');
const findNextBtn = $<HTMLButtonElement>('#find-next');
const findCloseBtn = $<HTMLButtonElement>('#find-close');
const sfSidecar = $<HTMLSpanElement>('#sf-sidecar');
const sfPath = $<HTMLSpanElement>('#sf-path');

let workspaces: Workspace[] = [];
let activeId: string | null = null;
// Per-workspace agent-state (FEAT-0010 / TASK-0082). The poller in
// main fans diffs from `.cockpit/agent-state.json` files via the
// `workspaces:agent-state` IPC; we paint a colored dot per pill.
const agentStates = new Map<string, AgentStatePayload>();
// The Electron sidecar exposes a per-workspace HTTP endpoint at this
// URL once `sidecar:event` 'ready' fires. The centre pane fetches
// /api/render against this base; null between workspaces.
let sidecarBaseUrl: string | null = null;
// Current docs-rel path mounted in the centre pane. Null when the
// placeholder is showing.
let currentRel: string | null = null;

// One shared auto-hide timer so a newer toast always cancels an older
// toast's pending hide (TASK-0158 — overlapping toasts used to hide
// each other early). Callers use scheduleHide() rather than their own
// setTimeout(hideStatus, …).
let statusHideTimer: number | null = null;

function showStatus(text: string, kind: 'info' | 'error' = 'info'): void {
  if (statusHideTimer != null) { clearTimeout(statusHideTimer); statusHideTimer = null; }
  statusBar.replaceChildren(document.createTextNode(text));
  statusBar.classList.toggle('error', kind === 'error');
  statusBar.classList.remove('is-actionable');
  statusBar.onclick = null;
  statusBar.hidden = false;
}

function scheduleHide(ms: number): void {
  if (statusHideTimer != null) clearTimeout(statusHideTimer);
  statusHideTimer = window.setTimeout(hideStatus, ms);
}

// A status toast with a click action — used for suppressed agent-focus
// jumps (TASK-0158): "Agent focus → TARGET · open".
function showActionStatus(text: string, action: string, onClick: () => void): void {
  if (statusHideTimer != null) { clearTimeout(statusHideTimer); statusHideTimer = null; }
  statusBar.replaceChildren(document.createTextNode(`${text} · `));
  const link = document.createElement('button');
  link.type = 'button';
  link.className = 'status-bar-action';
  link.textContent = action;
  link.addEventListener('click', (e) => { e.stopPropagation(); hideStatus(); onClick(); });
  statusBar.appendChild(link);
  statusBar.classList.remove('error');
  statusBar.classList.add('is-actionable');
  statusBar.hidden = false;
}

function hideStatus(): void {
  if (statusHideTimer != null) { clearTimeout(statusHideTimer); statusHideTimer = null; }
  statusBar.hidden = true;
  statusBar.onclick = null;
  statusBar.classList.remove('is-actionable');
}

function renderWorkspaceRail(): void {
  // FEAT-0015 / TASK-0100: each workspace is a square. Renders the
  // project icon (data URI sourced from `findWorkspaceIcon` in main)
  // when available, otherwise a colored letter fallback.
  listEl.innerHTML = '';
  if (workspaces.length === 0) {
    const li = document.createElement('li');
    li.className = 'empty';
    li.textContent = '+ to add';
    listEl.appendChild(li);
    return;
  }
  for (const ws of workspaces) {
    const li = document.createElement('li');
    li.className = 'ws-square';
    li.dataset.id = ws.id;
    if (ws.id === activeId) li.classList.add('active');

    paintWorkspaceVisual(li, ws, 32);

    li.addEventListener('click', () => { void openWorkspace(ws.id); });
    li.addEventListener('mousedown', (e) => {
      // Middle-click closes the workspace (Chrome / VS Code convention).
      if (e.button === 1) {
        e.preventDefault();
        closeWorkspace(ws.id);
      }
    });
    applyAgentStateToSquare(li, ws);
    listEl.appendChild(li);
  }
}

function colorFromName(name: string): string {
  // Deterministic hue (0-360) from the workspace name. Saturation +
  // lightness picked so all variants read on both light and dark bg.
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) | 0;
  }
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue} 55% 45%)`;
}

function applyAgentStateToSquare(li: HTMLLIElement, ws: Workspace): void {
  const state = agentStates.get(ws.id);
  const stateLine = state
    ? `\nagent: ${state.state}${state.message ? ` — ${state.message}` : ''}`
    : '';
  li.title = `${effectiveName(ws)}\n${ws.root}${stateLine}`;
  for (const cls of ['state-busy', 'state-waiting', 'state-needs-input', 'state-done', 'state-idle', 'state-error']) {
    li.classList.remove(cls);
  }
  const existingDot = li.querySelector('.ws-dot');
  if (existingDot) existingDot.remove();
  if (!state) return;
  const key = state.decayed_from ? 'idle' : state.state;
  li.classList.add(`state-${key}`);
  // Acknowledged alerts go static (pulse off, colour kept) — TASK-0157.
  li.classList.toggle('acked', isAlertAcked(ws.id, state.ts || ''));
  const dot = document.createElement('span');
  dot.className = 'ws-dot';
  dot.setAttribute('aria-hidden', 'true');
  li.appendChild(dot);
}

function closeWorkspace(id: string): void {
  // Soft close: just drop from the active list in the UI. The real
  // sidecar lifecycle is owned by main; the user re-opens via the +.
  const idx = workspaces.findIndex((w) => w.id === id);
  if (idx < 0) return;
  workspaces.splice(idx, 1);
  agentStates.delete(id);
  if (activeId === id) {
    // Pick the next-best tab to land on; fall back to placeholder.
    activeId = null;
    if (workspaces.length > 0) {
      const fallback = workspaces[Math.min(idx, workspaces.length - 1)];
      void openWorkspace(fallback.id);
    } else {
      placeholder.hidden = false;
      docView.hidden = true;
    }
  }
  renderWorkspaceRail();
}

async function loadWorkspaces(): Promise<void> {
  try {
    console.log('[renderer] requesting workspace list…');
    workspaces = await cockpitApi.workspaces.list();
    console.log(`[renderer] got ${workspaces.length} workspaces`);
    renderWorkspaceRail();
  } catch (err) {
    console.error('[renderer] workspaces.list failed:', err);
    showStatus(`Failed to load workspaces: ${String(err)}`, 'error');
  }
}

async function rescanWorkspaces(): Promise<void> {
  wsRailAdd.disabled = true;
  showStatus('Scanning for workspaces…');
  try {
    workspaces = await cockpitApi.workspaces.rescan();
    renderWorkspaceRail();
    showStatus(`Found ${workspaces.length} workspace${workspaces.length === 1 ? '' : 's'}.`);
    scheduleHide(1500);
  } catch (err) {
    showStatus(`Rescan failed: ${String(err)}`, 'error');
  } finally {
    wsRailAdd.disabled = false;
  }
}

function setProjectHeader(ws: Workspace | null): void {
  if (!ws) {
    wsNavProject.hidden = true;
    return;
  }
  wsNavProject.hidden = false;
  const displayName = effectiveName(ws);
  wsNavProjectName.textContent = displayName || '?';
  wsNavProjectName.title = `${displayName}\n${ws.root}`;
  paintWorkspaceVisual(wsNavProjectIcon, ws, 22);
}

// ----- Workspace visual painter --------------------------------------
// Priority (most specific wins):
//   1. userIcon  → uploaded image
//   2. userEmoji → emoji character
//   3. icon      → auto-probed favicon / logo in the project dir
//   4. identicon → 5×5 symmetric SVG derived from ws.id (with userColor
//                  or a hash-derived hue)

function paintWorkspaceVisual(target: HTMLElement, ws: Workspace, sizePx: number): void {
  target.replaceChildren();
  target.classList.remove('ws-has-emoji');
  target.style.backgroundColor = '';
  if (ws.userIcon) {
    const img = document.createElement('img');
    img.className = 'ws-icon';
    img.alt = '';
    img.src = ws.userIcon;
    target.appendChild(img);
    return;
  }
  if (ws.userEmoji) {
    target.classList.add('ws-has-emoji');
    target.textContent = ws.userEmoji;
    target.style.fontSize = `${Math.round(sizePx * 0.6)}px`;
    return;
  }
  if (ws.icon) {
    const img = document.createElement('img');
    img.className = 'ws-icon';
    img.alt = '';
    img.src = ws.icon;
    target.appendChild(img);
    return;
  }
  // Identicon fallback.
  target.appendChild(buildIdenticon(ws.id, ws.userColor));
  target.style.backgroundColor = ws.userColor
    ? withAlpha(ws.userColor, 0.12)
    : identiconTint(ws.id);
}

const IDENTICON_SVG_NS = 'http://www.w3.org/2000/svg';

function buildIdenticon(seed: string, colorOverride?: string): SVGElement {
  // 32-bit FNV-like hash from the workspace id; the first 15 bits drive
  // the cell pattern (3 cols × 5 rows, mirrored), the remaining bits
  // pick a hue.
  let hash = 2166136261 >>> 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (hash ^ seed.charCodeAt(i)) >>> 0;
    hash = Math.imul(hash, 16777619) >>> 0;
  }
  const fill = colorOverride ?? `hsl(${hash % 360} 55% 42%)`;
  const svg = document.createElementNS(IDENTICON_SVG_NS, 'svg');
  svg.setAttribute('class', 'ws-identicon');
  svg.setAttribute('viewBox', '0 0 30 30');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('fill', fill);
  const CELL = 6;
  for (let r = 0; r < 5; r++) {
    for (let c = 0; c < 3; c++) {
      const bit = (hash >>> (r * 3 + c)) & 1;
      if (!bit) continue;
      for (const col of c === 2 ? [2] : [c, 4 - c]) {
        const rect = document.createElementNS(IDENTICON_SVG_NS, 'rect');
        rect.setAttribute('x', String(col * CELL));
        rect.setAttribute('y', String(r * CELL));
        rect.setAttribute('width', String(CELL));
        rect.setAttribute('height', String(CELL));
        svg.appendChild(rect);
      }
    }
  }
  return svg;
}

function identiconTint(seed: string): string {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) | 0;
  return `hsl(${Math.abs(h) % 360} 50% 92%)`;
}

function withAlpha(color: string, alpha: number): string {
  // Best-effort tint for the square background. hsl() → keep, just
  // mix toward elevated bg via CSS opacity isn't possible here; instead
  // return an hsla approximation when input is hsl(...), or a fallback.
  const m = color.match(/^hsl\(\s*(-?\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%\s*\)$/);
  if (m) {
    return `hsl(${m[1]} ${m[2]}% 92%)`;
  }
  return color + Math.round(alpha * 255).toString(16).padStart(2, '0');
}

async function openWorkspace(id: string): Promise<void> {
  if (id === activeId) return;
  activeId = id;
  // Tell main which workspace is active so the agent-state poller
  // can suppress notifications about the one the user is on (TASK-0087).
  cockpitApi.workspaces.notifyActiveChanged(id);
  const ws = workspaces.find((w) => w.id === id);
  if (ws) setProjectHeader(ws);
  // If the terminal pane is open, swap the xterm to the new
  // workspace's PTY (FEAT-0015 / TASK-0104).
  if (!terminalPane.hidden) void attachTerminalTo(id);
  renderWorkspaceRail();
  refreshFollowButton();  // reflect the new workspace's follow mode
  scheduleAck();  // looking at this workspace may acknowledge its alert
  placeholder.hidden = true;
  docView.hidden = true;
  sidecarBaseUrl = null;
  // Drop the previous workspace's snapshot so a waiting row for the
  // newly-active workspace doesn't briefly show the old workspace's
  // cost before the new sidecar's /api/cockpit/state resolves (review
  // finding, FEAT-0030). Clear the agent strip too so it can't keep
  // rendering the previous workspace's session if the new sidecar
  // fails to spawn (review finding F3).
  lastAgentSnap = null;
  showAgentStrip(null, null);
  // `stripLastPrompt` and `workTransitions` are sticky *within* a
  // workspace (the strip keeps showing the last prompt / touched notes
  // between runs), but must not survive a switch — otherwise a project
  // whose current session has no prompt of its own renders the previous
  // workspace's prompt (ISS-0015). Clear them so the strip starts clean.
  stripLastPrompt = '';
  workTransitions.clear();
  // Centre tabs are per-workspace context — reset on switch (TASK-0159).
  agentsTabOpen = false;
  lastDocRel = null;
  docTabChanged = false;
  // Overview scope is per-project — a phase from the previous workspace
  // won't exist here (a phase-less project would 404 on ~overview/PHASE-…).
  // Reset so a new workspace starts at the unscoped project overview (TASK-0177).
  overviewScope = null;
  scopePhaseList = null;
  renderCenterTabs();
  currentRel = null;
  setSidecarStatus('spawning');
  refreshFooterPath();
  refreshFooterAgent();
  showStatus('Starting cockpit…');
  const res = await cockpitApi.workspaces.open(id);
  if (!res.ok) {
    showStatus(`Failed to open workspace: ${res.error ?? 'unknown error'}`, 'error');
    placeholder.hidden = false;
    activeId = null;
    renderWorkspaceRail();
  }
  // The sidecar:ready event handler below loads the URL into the iframe.
}

cockpitApi.sidecar.onEvent((ev) => {
  switch (ev.kind) {
    case 'ready': {
      const p = ev.payload as SidecarReadyPayload;
      if (p.workspaceId !== activeId) return;
      sidecarBaseUrl = p.url;
      setSidecarStatus('ready');
      hideStatus();
      // SSE soft-reload + heartbeat (TASK-0086) — subscribe to this
      // sidecar's event stream now that we know its URL.
      attachSidecarEventStream(p.url);
      startTabStateHeartbeat();
      // In-workspace nav populates as soon as the sidecar is up
      // (TASK-0083). Default landing for the centre pane: README.md
      // — UNLESS the user is in Overview mode, where loadWsNav() will
      // route to loadOverview() and mount the dashboard. Without this
      // guard a workspace switch would race the README fetch against
      // the stats fetch and overwrite the dashboard.
      void loadWsNav();
      if (currentNavMode !== 'overview') void navigateTo('README.md');
      void refreshAgentSnapshot();
      void loadAgentActions();
      void refreshQueueItems();
      void drainDispatchRequests();
      break;
    }
    case 'failed': {
      const p = ev.payload as SidecarFailedPayload;
      if (p.workspaceId !== activeId) return;
      const tail = p.stderrTail ? `\n${p.stderrTail}` : '';
      showStatus(`Sidecar failed: ${p.reason}${tail}`, 'error');
      setSidecarStatus('failed', `sidecar: failed (${p.reason})`);
      placeholder.hidden = false;
      docView.hidden = true;
      sidecarBaseUrl = null;
      currentRel = null;
      activeId = null;
      refreshFooterPath();
      refreshFooterAgent();
      renderWorkspaceRail();
      break;
    }
    case 'exited': {
      const p = ev.payload as SidecarExitedPayload;
      if (p.workspaceId !== activeId) return;
      const detail = p.code === 0 ? 'cleanly' : `code ${p.code ?? 'null'}, signal ${p.signal ?? 'null'}`;
      showStatus(`Sidecar exited ${detail}.`);
      setSidecarStatus('exited', `sidecar: exited (${detail})`);
      placeholder.hidden = false;
      docView.hidden = true;
      sidecarBaseUrl = null;
      currentRel = null;
      activeId = null;
      refreshFooterPath();
      refreshFooterAgent();
      renderWorkspaceRail();
      break;
    }
  }
});

// ----------------------------------------------------------------------
// Centre pane (TASK-0070) — fetch /api/render and mount the HTML.
// ----------------------------------------------------------------------

interface RenderResponse {
  schema_version: number;
  rel_path: string;
  title: string;
  frontmatter: Record<string, unknown>;
  metadata_html: string;
  html: string;
  linked: unknown[];
  backlinks: unknown[];
  produced_by?: {
    session_id: string;
    agent?: string | null;
    started?: string | null;
    total_cost_usd?: number;
  };
  dispatch_history?: Array<{
    id: string; verb?: string; agent?: string; ts: string;
    session_id: string | null; live: boolean; pending?: boolean;
    total_cost_usd?: number;
  }>;
}

// Provenance of the currently open note (FEAT-0025 / TASK-0135) —
// feeds the re-dispatch guard and the provenance line.
let currentDispatchHistory: RenderResponse['dispatch_history'] | null = null;
let currentNoteStatus: string | null = null;

// History stack for the centre pane (TASK-0072). Entries are normalised
// docs-rel paths (no leading "docs/", no query). Hash anchors are part
// of the entry — back/forward to the same path with a different anchor
// is intentional.
const HISTORY_LIMIT = 100;
const historyStack: string[] = [];
let historyCursor = -1;

// Per-note scroll preservation (TASK-0073). Keyed by rel-without-frag
// so #anchor jumps inside the same doc don't pollute the saved
// position. Updated on every nav-away.
const scrollPositions = new Map<string, number>();

function stripFragment(rel: string): string {
  const idx = rel.indexOf('#');
  return idx >= 0 ? rel.slice(0, idx) : rel;
}

function noteTypeFromFrontmatter(fm: Record<string, unknown>): string | null {
  const raw = fm.type;
  if (typeof raw !== 'string') return null;
  return raw.replace(/[[\]"]/g, '').trim().toLowerCase() || null;
}

function buildDocHeader(data: RenderResponse, rel: string): HTMLElement {
  const bar = document.createElement('div');
  bar.className = 'doc-header';

  // One row: type icon + ID + path on the left; verb buttons
  // right-aligned with the status chip at the very end.
  const row = document.createElement('div');
  row.className = 'doc-header-row';

  const identity = document.createElement('div');
  identity.className = 'doc-header-identity';
  const noteType = noteTypeFromFrontmatter(data.frontmatter || {});
  appendIf(identity, typeIcon(noteType || undefined, 15));
  const fmId = typeof data.frontmatter?.id === 'string'
    ? (data.frontmatter.id as string) : '';
  if (fmId) {
    const idEl = document.createElement('span');
    idEl.className = 'doc-header-id';
    idEl.textContent = fmId;
    identity.appendChild(idEl);
  }
  const pathEl = document.createElement('button');
  pathEl.type = 'button';
  pathEl.className = 'doc-header-path';
  pathEl.textContent = `docs/${rel}`;
  pathEl.title = 'Click to copy path';
  pathEl.addEventListener('click', () => {
    void navigator.clipboard?.writeText(`docs/${rel}`);
    const orig = pathEl.textContent;
    pathEl.textContent = 'copied';
    setTimeout(() => { pathEl.textContent = orig; }, 800);
  });
  identity.appendChild(pathEl);
  row.appendChild(identity);

  const right = document.createElement('div');
  right.className = 'doc-header-right';
  const dispatchId = fmId && isDispatchableId(fmId) ? fmId.toUpperCase() : null;
  if (dispatchId) {
    const verbs = verbsForId(dispatchId, {
      type: noteType, status: currentNoteStatus,
    });
    for (const verb of verbs) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'doc-header-verb' + (verb.default ? ' is-default' : '');
      btn.textContent = verb.default ? `▶ ${verb.label}` : verb.label;
      btn.title = `${verb.label} ${dispatchId} with the agent`;
      btn.addEventListener('click', () => {
        void dispatchToAgent(dispatchId, rel, undefined, verb.key);
      });
      right.appendChild(btn);
    }
  }
  appendIf(right, statusChip(currentNoteStatus || undefined));
  if (right.childElementCount > 0) row.appendChild(right);
  bar.appendChild(row);
  return bar;
}

async function navigateTo(
  rel: string,
  opts: { replace?: boolean; fromHistory?: boolean } = {},
): Promise<void> {
  await navigateToInner(rel, opts);
  renderCenterTabs();
}

async function navigateToInner(
  rel: string,
  opts: { replace?: boolean; fromHistory?: boolean } = {},
): Promise<void> {
  if (!sidecarBaseUrl) return;
  // Capture the current scroll position before we replace innerHTML;
  // back / forward restore from this map.
  if (currentRel) {
    scrollPositions.set(stripFragment(currentRel), docView.scrollTop);
  }
  // Strip any leading "/docs/" — the API accepts both forms but
  // keeping `currentRel` canonical simplifies history.
  let normalised = rel.replace(/^\/+/, '');
  if (normalised.startsWith('docs/')) normalised = normalised.slice('docs/'.length);
  normalised = normalised.split('?')[0];
  // Virtual pages (TASK-0127/0130): `~overview[/PHASE-…]` and
  // `~session/<id>` render synthesized pages instead of fetching
  // /api/render — with real history entries so back/forward work.
  if (normalised === '~overview' || normalised.startsWith('~overview/')) {
    const scopeId = normalised.startsWith('~overview/')
      ? normalised.slice('~overview/'.length).toUpperCase()
      : null;
    const target = scopeId ? `~overview/${scopeId}` : '~overview';
    const ok = await renderOverviewPage(scopeId);
    if (ok) {
      currentRel = target;
      currentDispatchHistory = null;
      currentNoteStatus = null;
      pushHistory(target, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  if (normalised.startsWith('~session/')) {
    const ok = await renderSessionDetailPage(normalised.slice('~session/'.length));
    if (ok) {
      currentRel = normalised;
      pushHistory(normalised, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  if (normalised === '~agents') {
    const ok = await renderAgentsPage();
    if (ok) {
      currentRel = '~agents';
      currentDispatchHistory = null;
      currentNoteStatus = null;
      agentsTabOpen = true;   // pin the fleet tab (TASK-0159)
      docTabChanged = false;  // switching to agents clears the doc dot
      pushHistory('~agents', opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  const fragmentIndex = normalised.indexOf('#');
  const pathOnly = fragmentIndex >= 0 ? normalised.slice(0, fragmentIndex) : normalised;
  const frag = fragmentIndex >= 0 ? normalised.slice(fragmentIndex + 1) : null;

  let resp: Response;
  try {
    resp = await fetch(
      `${sidecarBaseUrl}/api/render?path=${encodeURIComponent(pathOnly)}`,
    );
  } catch (err) {
    showStatus(`Render fetch failed: ${String(err)}`, 'error');
    return;
  }
  if (resp.status === 404) {
    mountPlaceholder(pathOnly);
    pushHistory(normalised, opts.replace ?? false);
    return;
  }
  if (!resp.ok) {
    showStatus(`Render failed: HTTP ${resp.status}`, 'error');
    return;
  }
  const data = (await resp.json()) as RenderResponse;
  // Server-side resolution: `metadata_html` is the pre-resolved
  // metadata strip (TASK-0075). `html` is the rendered body with
  // wikilinks already turned into `<a>` tags. The click handler on
  // #doc-view intercepts links in either section identically.
  docView.innerHTML = (data.metadata_html || '') + data.html;
  docView.classList.remove('overview-pane', 'agents-page');
  docView.hidden = false;
  placeholder.hidden = true;
  currentRel = normalised;
  lastDocRel = normalised;   // the doc tab points here (TASK-0159)

  currentDispatchHistory = data.dispatch_history ?? null;
  currentNoteStatus = typeof data.frontmatter?.status === 'string'
    ? (data.frontmatter.status as string) : null;
  // Doc header bar (FEAT-0026 / TASK-0140): identity + path + verbs.
  docView.prepend(buildDocHeader(data, pathOnly));
  // Dispatch provenance (FEAT-0025 / TASK-0135).
  if (data.dispatch_history && data.dispatch_history.length > 0) {
    const d = data.dispatch_history[0];
    const prov = document.createElement('div');
    prov.className = 'chg-provenance dispatch-provenance';
    const when = d.ts ? new Date(d.ts).toLocaleString() : '';
    const sess = d.pending
      ? 'pending delivery'
      : d.session_id
        ? `session ${d.session_id.slice(0, 8)}${d.live ? ' (live)' : ''}${typeof d.total_cost_usd === 'number' ? ` · $${d.total_cost_usd.toFixed(2)}` : ''}`
        : '';
    prov.textContent = `dispatched ${d.verb ?? 'default'} · ${d.agent ?? 'agent'}${when ? ` · ${when}` : ''}${sess ? ` → ${sess}` : ''}`;
    docView.prepend(prov);
  }
  // CHG provenance (FEAT-0022 / TASK-0126): cockpit-side enrichment,
  // the note file itself is untouched.
  if (data.produced_by) {
    const prov = document.createElement('div');
    prov.className = 'chg-provenance';
    const cost = typeof data.produced_by.total_cost_usd === 'number'
      ? ` · $${data.produced_by.total_cost_usd.toFixed(2)}` : '';
    prov.textContent = `produced by ${data.produced_by.agent || 'agent'} session ${data.produced_by.session_id.slice(0, 8)}${cost}`;
    docView.prepend(prov);
  }
  wireInteractiveCheckboxes();
  wireMetadataStripPersistence();
  applyScrollTarget(pathOnly, frag, opts.fromHistory ?? false);
  pushHistory(normalised, opts.replace ?? false);
  // Highlight the nav row matching the new doc (TASK-0083).
  refreshActiveNavRow();
  // Refresh the right pane against the new doc (TASK-0085).
  void loadRightPane(normalised);
  // Heartbeat the new URL so the cockpit's state snapshot stays
  // accurate (TASK-0086).
  void sendTabState();
  // Update the status footer (TASK-0094).
  refreshFooterPath();
  // Repaint the star — its filled state depends on currentRel.
  paintStar();
}

// ----------------------------------------------------------------------
// Interactive task-list checkboxes (TASK-0074)
// ----------------------------------------------------------------------

// Persist the frontmatter strip's open/collapsed state across navigation
// (FEAT-0015 user request). The server emits `<details class="metadata-strip" open>`
// every render; localStorage remembers the user's last choice so a
// collapse on one note stays collapsed when they navigate to the next.
const METADATA_STRIP_KEY = 'cockpit:metadata-strip-open';

function wireMetadataStripPersistence(): void {
  const det = docView.querySelector<HTMLDetailsElement>('details.metadata-strip');
  if (!det) return;
  let storedOpen = true;
  try {
    const v = localStorage.getItem(METADATA_STRIP_KEY);
    if (v === '0') storedOpen = false;
  } catch { /* ignore */ }
  det.open = storedOpen;
  det.addEventListener('toggle', () => {
    try { localStorage.setItem(METADATA_STRIP_KEY, det.open ? '1' : '0'); }
    catch { /* ignore */ }
  });
}

function wireInteractiveCheckboxes(): void {
  // pymdownx.tasklist with `clickable_checkbox: False` renders the
  // boxes as `disabled` — mode-1 browser view stays read-only. Mode 3
  // enables them by stripping the attribute; the change handler
  // delegates from #doc-view and writes back through the new endpoint.
  const boxes = docView.querySelectorAll<HTMLInputElement>('input[type=checkbox]');
  boxes.forEach((box) => box.removeAttribute('disabled'));
}

docView.addEventListener('change', async (e) => {
  const tgt = e.target;
  if (!(tgt instanceof HTMLInputElement)) return;
  if (tgt.type !== 'checkbox') return;
  if (!sidecarBaseUrl || !currentRel) return;

  const all = docView.querySelectorAll('input[type=checkbox]');
  const idx = Array.from(all).indexOf(tgt);
  if (idx < 0) return;

  const pathOnly = stripFragment(currentRel);
  const desired = tgt.checked;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/notes/check-toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: pathOnly, index: idx, checked: desired }),
    });
    if (!resp.ok) {
      tgt.checked = !desired; // revert optimistic update
      const reason = await resp.text();
      showStatus(`Checkbox toggle failed: ${reason}`, 'error');
      scheduleHide(2500);
    }
  } catch (err) {
    tgt.checked = !desired;
    showStatus(`Checkbox toggle failed: ${String(err)}`, 'error');
    scheduleHide(2500);
  }
});

function applyScrollTarget(
  pathOnly: string,
  frag: string | null,
  fromHistory: boolean,
): void {
  // The browser would scroll to the anchor synchronously after parsing,
  // but we just injected innerHTML — layout hasn't happened yet. Defer
  // to next frame so getBoundingClientRect / scrollIntoView see the
  // laid-out DOM.
  requestAnimationFrame(() => {
    if (frag) {
      try {
        const el = docView.querySelector(`#${CSS.escape(frag)}`);
        if (el) {
          (el as HTMLElement).scrollIntoView({ block: 'start' });
          return;
        }
      } catch {
        /* invalid id — fall through to top */
      }
    }
    if (fromHistory) {
      docView.scrollTop = scrollPositions.get(pathOnly) ?? 0;
    } else {
      docView.scrollTop = 0;
    }
  });
}

function pushHistory(entry: string, replace: boolean): void {
  try { queueMicrotask(refreshHistoryButtons); } catch { /* TDZ on early renders */ }
  if (replace && historyCursor >= 0) {
    historyStack[historyCursor] = entry;
    return;
  }
  // Drop any forward history that's now stale.
  if (historyCursor < historyStack.length - 1) {
    historyStack.length = historyCursor + 1;
  }
  // No-op if the user just clicked the same link.
  if (historyStack[historyCursor] === entry) return;
  historyStack.push(entry);
  // Trim oldest entries if we blow the cap.
  if (historyStack.length > HISTORY_LIMIT) {
    const drop = historyStack.length - HISTORY_LIMIT;
    historyStack.splice(0, drop);
  }
  historyCursor = historyStack.length - 1;
}

function back(): void {
  if (historyCursor <= 0) return;
  historyCursor -= 1;
  // Re-render without pushing onto history; restore scroll from the
  // per-note map.
  const entry = historyStack[historyCursor];
  void navigateTo(entry, { replace: true, fromHistory: true });
}

function forward(): void {
  if (historyCursor >= historyStack.length - 1) return;
  historyCursor += 1;
  const entry = historyStack[historyCursor];
  void navigateTo(entry, { replace: true, fromHistory: true });
}

// Top-bar back / forward / search button wiring + disabled-state sync.
// Imperative ids — these elements live in the window-wide top bar.
const topBarBack   = $<HTMLButtonElement>('#top-bar-back');
const topBarFwd    = $<HTMLButtonElement>('#top-bar-fwd');
const topBarSearch = $<HTMLButtonElement>('#top-bar-search');

function refreshHistoryButtons(): void {
  topBarBack.disabled = historyCursor <= 0;
  topBarFwd.disabled  = historyCursor >= historyStack.length - 1;
}

topBarBack.addEventListener('click',   () => back());
topBarFwd.addEventListener('click',    () => forward());
topBarSearch.addEventListener('click', () => {
  if (quickSwitchEl.hidden) openQuickSwitch();
  else closeQuickSwitch();
});

refreshHistoryButtons();

// ----- Pin / star the current doc (per-workspace localStorage) -------
// Browser cockpit mode 1 uses the same storage shape under
// `project-os-cockpit.cockpit.pinned-paths`; the native shell keys
// per workspace so pins don't leak across projects.

const topBarStar = $<HTMLButtonElement>('#top-bar-star');

function pinnedStorageKey(workspaceId: string): string {
  return `cockpit:pinned:${workspaceId}`;
}

function loadPinned(workspaceId: string): string[] {
  try {
    const raw = localStorage.getItem(pinnedStorageKey(workspaceId));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter((s) => typeof s === 'string') : [];
  } catch { return []; }
}

function savePinned(workspaceId: string, paths: string[]): void {
  try {
    localStorage.setItem(pinnedStorageKey(workspaceId), JSON.stringify(paths));
  } catch { /* ignore */ }
}

function isPinnedHere(rel: string): boolean {
  if (!activeId) return false;
  return loadPinned(activeId).indexOf(rel) >= 0;
}

function togglePinned(rel: string): boolean {
  if (!activeId) return false;
  const list = loadPinned(activeId);
  const idx = list.indexOf(rel);
  if (idx >= 0) list.splice(idx, 1);
  else list.push(rel);
  savePinned(activeId, list);
  return idx < 0;
}

const STAR_OUTLINE = '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>';

function paintStar(): void {
  const rel = currentRel ? stripFragment(currentRel) : null;
  topBarStar.disabled = !rel;
  if (!rel) {
    topBarStar.setAttribute('aria-pressed', 'false');
    topBarStar.title = 'Pin to Library';
    topBarStar.replaceChildren(makeSvg(STAR_OUTLINE, 14, {}));
    return;
  }
  const pinned = isPinnedHere(rel);
  topBarStar.setAttribute('aria-pressed', pinned ? 'true' : 'false');
  topBarStar.title = pinned ? 'Unpin from Library' : 'Pin to Library';
  topBarStar.replaceChildren(makeSvg(STAR_OUTLINE, 14, {}));
}

topBarStar.addEventListener('click', () => {
  const rel = currentRel ? stripFragment(currentRel) : null;
  if (!rel || !activeId) return;
  togglePinned(rel);
  paintStar();
  // Refresh Library nav if it's currently the active mode — the
  // server returns a Pinned group when we send ?pinned=…
  if (currentNavMode === 'library' && sidecarBaseUrl) void loadWsNav();
});

// Schedule the initial paint after PANEL_LEFT_* constants + makeSvg
// are declared further down the file.
queueMicrotask(paintStar);

// Mouse button 3 (back) / 4 (forward) — common on 5-button mice.
// `mousedown` is more reliable than `auxclick` for these buttons.
document.addEventListener('mousedown', (e) => {
  if (e.button === 3) {
    e.preventDefault();
    back();
  } else if (e.button === 4) {
    e.preventDefault();
    forward();
  }
});

cockpitApi.menu.onBack(() => back());
cockpitApi.menu.onForward(() => forward());

function mountPlaceholder(missing: string): void {
  docView.innerHTML =
    `<h1>No note here</h1>` +
    `<p class="meta">${escapeHtml(missing)} did not resolve to a Markdown file in this workspace.</p>` +
    `<p class="meta">Pick another note (left nav lands in <code>FEAT-0010</code>) or open one from a parent doc.</p>`;
  docView.hidden = false;
  placeholder.hidden = true;
  currentRel = null;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ----------------------------------------------------------------------
// Link interception (TASK-0071)
// ----------------------------------------------------------------------

type LinkClass =
  | { kind: 'docs'; rel: string }
  | { kind: 'fragment'; frag: string }
  | { kind: 'external'; url: string }
  | { kind: 'unknown' };

function classifyLink(href: string): LinkClass {
  if (!href) return { kind: 'unknown' };
  if (href.startsWith('#')) {
    return { kind: 'fragment', frag: href.slice(1) };
  }
  // Resolve relative URLs against the docs root of the active
  // sidecar; the cockpit's wikilink renderer emits anchors like
  // `<a href="/docs/features/foo.md">`.
  const base = sidecarBaseUrl ? sidecarBaseUrl + '/docs/' : 'http://placeholder/';
  let parsed: URL;
  try {
    parsed = new URL(href, base);
  } catch {
    return { kind: 'unknown' };
  }

  if (sidecarBaseUrl) {
    const sidecar = new URL(sidecarBaseUrl);
    if (parsed.host === sidecar.host) {
      // Same origin — only `/docs/*` paths are renderable.
      if (parsed.pathname.startsWith('/docs/')) {
        const rel = parsed.pathname.slice('/docs/'.length) + (parsed.hash || '');
        return { kind: 'docs', rel };
      }
      // Same-origin but a non-renderable route (e.g. /_static/) —
      // let it fall through to external so the user can decide.
    }
  }

  if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
    return { kind: 'external', url: parsed.href };
  }
  return { kind: 'unknown' };
}

docView.addEventListener('click', (e) => {
  const target = e.target as HTMLElement | null;
  if (!target) return;
  const anchor = target.closest('a') as HTMLAnchorElement | null;
  if (!anchor) return;
  const href = anchor.getAttribute('href');
  if (!href) return;

  const cls = classifyLink(href);

  // Cmd/Ctrl-click forces the system browser even for docs-internal
  // links (the "open in new tab" escape hatch).
  if ((e.metaKey || e.ctrlKey) && cls.kind === 'docs' && sidecarBaseUrl) {
    e.preventDefault();
    const absolute = `${sidecarBaseUrl}/docs/${cls.rel}`;
    void cockpitApi.app.openExternal(absolute);
    return;
  }

  switch (cls.kind) {
    case 'docs':
      e.preventDefault();
      void navigateTo(cls.rel);
      break;
    case 'external':
      e.preventDefault();
      void cockpitApi.app.openExternal(cls.url);
      break;
    case 'fragment': {
      e.preventDefault();
      try {
        const el = docView.querySelector(`#${CSS.escape(cls.frag)}`);
        if (el) (el as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'start' });
      } catch {
        /* CSS.escape unavailable / invalid id — best-effort skip */
      }
      break;
    }
    case 'unknown':
      e.preventDefault();
      break;
  }
});

// Rescan binding moved to the rail's + button (wsRailAdd). The menu
// item still triggers rescan via `cockpitApi.menu.onRescan` below.

cockpitApi.workspaces.onSwitchTo((ev) => {
  // Notification click (TASK-0087) — switch to the named workspace.
  void openWorkspace(ev.workspaceId);
});

cockpitApi.workspaces.onAgentState((ev) => {
  const prev = agentStates.get(ev.workspaceId)?.state;
  noteFinish(ev.workspaceId, prev, ev.payload);
  if (ev.payload) {
    agentStates.set(ev.workspaceId, ev.payload);
  } else {
    agentStates.delete(ev.workspaceId);
  }
  // Repaint only the affected tab so a state change on one
  // workspace doesn't disturb the rest of the strip.
  const li = listEl.querySelector<HTMLLIElement>(`li[data-id="${ev.workspaceId}"]`);
  if (li) {
    const ws = workspaces.find((w) => w.id === ev.workspaceId);
    if (ws) applyAgentStateToSquare(li, ws);
  }
  if (ev.workspaceId === activeId) {
    refreshFooterAgent();
    void refreshAgentSnapshot();
    scheduleAck();  // new alert on the workspace you're looking at
  }
  refreshAttention();
  if (currentRel === '~agents') void renderAgentsPage(true);
});

// ----------------------------------------------------------------------
// Terminal pane (TASK-0063)
// ----------------------------------------------------------------------

// Per-workspace terminal sessions (FEAT-0015 / TASK-0104):
// PTYs live in main, keyed by workspaceId. The xterm in the renderer
// is a single shared instance; switching workspaces re-attaches it
// to the new workspace's PTY (rewriting the buffer with the backlog).
// PTYs persist across switches — they only die on explicit dispose
// or app shutdown, so REPLs / dev servers survive when you flip tabs.

let term: XtermTerminal | null = null;
let fitAddon: XtermFitAddon | null = null;
let attachedTerminalId: string | null = null;
const liveTerminals = new Set<string>();
let terminalListenersWired = false;

const TERMINAL_THEME_DARK = {
  background: '#1b1d1f',
  foreground: '#d6d6d6',
  cursor: '#7da6ff',
  cursorAccent: '#1b1d1f',
  selectionBackground: '#33373b',
  black: '#1b1d1f',  red: '#cc6f6f', green: '#8ab886', yellow: '#d5b878',
  blue: '#7da6ff',  magenta: '#b48ead', cyan: '#86c1b9', white: '#c5c8c6',
  brightBlack: '#5c5f63', brightRed: '#d68a8a', brightGreen: '#a6c898',
  brightYellow: '#e0c895', brightBlue: '#9bb8ff', brightMagenta: '#c8a4c6',
  brightCyan: '#a5d3cc', brightWhite: '#f0f0f0',
};

const TERMINAL_THEME_LIGHT = {
  background: '#ffffff',
  foreground: '#1c1d1f',
  cursor: '#3b6ea8',
  cursorAccent: '#ffffff',
  selectionBackground: '#dfe6ee',
  black: '#1c1d1f',  red: '#b54a4a', green: '#3f7a44', yellow: '#a06c1a',
  blue: '#3b6ea8',  magenta: '#86458a', cyan: '#347a72', white: '#3a3d41',
  brightBlack: '#6b6e73', brightRed: '#c45656', brightGreen: '#4f9656',
  brightYellow: '#b97f2e', brightBlue: '#4d83c2', brightMagenta: '#9a5c9e',
  brightCyan: '#479287', brightWhite: '#1c1d1f',
};

function currentTerminalTheme(): Record<string, string> {
  return document.documentElement.dataset.theme === 'dark'
    ? TERMINAL_THEME_DARK
    : TERMINAL_THEME_LIGHT;
}

function activeWorkspaceCwd(): string | undefined {
  if (!activeId) return undefined;
  const ws = workspaces.find((w) => w.id === activeId);
  return ws?.root;
}

// Wire IPC listeners once. data/exit events come in tagged with
// workspaceId; we filter to the currently-attached one so other
// workspaces' bytes don't leak into the visible xterm.
function wireTerminalListenersOnce(): void {
  if (terminalListenersWired) return;
  terminalListenersWired = true;
  cockpitApi.terminal.onData((ev) => {
    if (!term) return;
    if (ev.workspaceId !== attachedTerminalId) return;
    term.write(ev.data);
  });
  cockpitApi.terminal.onExit((info) => {
    liveTerminals.delete(info.workspaceId);
    if (info.workspaceId !== attachedTerminalId || !term) return;
    term.write(`\r\n\x1b[90m[terminal exited code=${info.exitCode}${info.signal ? ` signal=${info.signal}` : ''}]\x1b[0m\r\n`);
  });
}

// Lazily build the xterm shell. Bytes typed in are routed to whichever
// PTY is currently attached.
function ensureXterm(): void {
  if (term) return;
  term = new Terminal({
    fontFamily: 'ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace',
    fontSize: 13,
    theme: currentTerminalTheme(),
    cursorBlink: true,
    scrollback: 5000,
    allowProposedApi: true,
  });
  fitAddon = new FitAddon.FitAddon();
  term.loadAddon(fitAddon);
  term.open(terminalMount);
  fitAddon.fit();

  // Keep xterm's geometry in sync with its container (ISS-0016). Toggling
  // the pane visible (hidden→shown on a view switch), a window/monitor
  // resize, or a divider drag all change the mount's size; without a
  // re-fit xterm keeps a stale row count (the prompt and lines below it
  // clip off-screen under the mount's overflow:hidden) and a stale scroll
  // viewport (mouse-wheel dead until a manual resize). A ResizeObserver
  // catches every case — including the hidden→visible transition, which
  // reports a 0→real size change. rAF-debounced; fit() only resizes xterm
  // *within* the mount, so it can't re-trigger the observer into a loop.
  let fitPending = false;
  const refit = (): void => {
    if (fitPending) return;
    fitPending = true;
    requestAnimationFrame(() => {
      fitPending = false;
      if (terminalPane.hidden) return;
      try { fitAddon?.fit(); } catch { /* xterm not ready yet */ }
    });
  };
  new ResizeObserver(refit).observe(terminalMount);

  term.onData((data) => {
    if (attachedTerminalId) cockpitApi.terminal.write(attachedTerminalId, data);
  });
  term.onResize(({ cols, rows }) => {
    if (attachedTerminalId) cockpitApi.terminal.resize(attachedTerminalId, cols, rows);
  });
  // Copy-on-select (TASK-0167, opt-in) — PuTTY convention for the
  // terminally-inclined.
  term.onSelectionChange(() => {
    if (!copyOnSelect || !term?.hasSelection()) return;
    const s = term.getSelection();
    if (s) void navigator.clipboard.writeText(s);
  });
  // Terminal context menu (TASK-0167) — xterm's selection isn't a DOM
  // selection, so the native menu can't see it; build our own.
  terminalMount.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    e.stopPropagation();
    showTerminalMenu(e.clientX, e.clientY);
  });
  wireTerminalListenersOnce();
}

// ----- Terminal context menu + clipboard (TASK-0167) -------------------
let copyOnSelect = false;
try { copyOnSelect = localStorage.getItem('cockpit:copy-on-select') === '1'; }
catch { /* ignore */ }
let termMenuEl: HTMLElement | null = null;

function closeTerminalMenu(): void {
  if (termMenuEl) { termMenuEl.remove(); termMenuEl = null; }
}

// Multi-line pastes are wrapped in bracketed-paste markers so a shell /
// REPL treats them as one block instead of running each line.
function bracketedPaste(text: string): string {
  return text.includes('\n') ? `\x1b[200~${text}\x1b[201~` : text;
}

async function pasteIntoTerminal(): Promise<void> {
  if (!attachedTerminalId) return;
  try {
    const text = await navigator.clipboard.readText();
    if (text) cockpitApi.terminal.write(attachedTerminalId, bracketedPaste(text));
  } catch { /* clipboard blocked — ignore */ }
}

function copyTerminalSelection(): void {
  const s = term?.hasSelection() ? term.getSelection() : '';
  if (s) void navigator.clipboard.writeText(s);
}

function showTerminalMenu(x: number, y: number): void {
  closeTerminalMenu();
  const menu = document.createElement('div');
  menu.className = 'term-menu';
  const hasSel = !!term?.hasSelection();
  const add = (label: string, enabled: boolean, fn: () => void): void => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'term-menu-item';
    b.textContent = label;
    b.disabled = !enabled;
    b.addEventListener('click', () => { closeTerminalMenu(); fn(); });
    menu.appendChild(b);
  };
  add('Copy', hasSel, copyTerminalSelection);
  add('Paste', true, () => { void pasteIntoTerminal(); });
  add('Select All', true, () => term?.selectAll());
  add('Clear', true, () => term?.clear());
  const sep = document.createElement('div');
  sep.className = 'term-menu-sep';
  menu.appendChild(sep);
  add(copyOnSelect ? '✓ Copy on select' : 'Copy on select', true, () => {
    copyOnSelect = !copyOnSelect;
    try { localStorage.setItem('cockpit:copy-on-select', copyOnSelect ? '1' : '0'); } catch { /* ignore */ }
  });
  menu.style.visibility = 'hidden';
  document.body.appendChild(menu);
  // Keep the menu on-screen.
  const r = menu.getBoundingClientRect();
  menu.style.left = `${Math.min(x, window.innerWidth - r.width - 4)}px`;
  menu.style.top = `${Math.min(y, window.innerHeight - r.height - 4)}px`;
  menu.style.visibility = 'visible';
  termMenuEl = menu;
  window.setTimeout(() => document.addEventListener('mousedown', closeTerminalMenu, { once: true }), 0);
}

// Attach the xterm to a workspace's PTY: spawn it if not yet alive,
// otherwise replay the backlog so the screen resumes in-place.
async function attachTerminalTo(workspaceId: string): Promise<void> {
  ensureXterm();
  if (!term) return;
  if (attachedTerminalId === workspaceId) return;
  attachedTerminalId = workspaceId;
  term.reset();
  const cwd = workspaces.find((w) => w.id === workspaceId)?.root;
  if (!liveTerminals.has(workspaceId)) {
    const res = await cockpitApi.terminal.spawn({
      workspaceId, cwd, cols: term.cols, rows: term.rows,
    });
    if (!res.ok) {
      term.write(`\x1b[31m[failed to spawn terminal: ${res.error ?? 'unknown'}]\x1b[0m\r\n`);
      return;
    }
    liveTerminals.add(workspaceId);
    return;
  }
  // PTY already running for this workspace — re-attach and replay
  // the captured backlog so the user sees the previous screen.
  const res = await cockpitApi.terminal.attach(workspaceId);
  if (res.ok && res.backlog) term.write(res.backlog);
  // Re-send our current geometry; main may have lost track if the
  // window resized while detached.
  cockpitApi.terminal.resize(workspaceId, term.cols, term.rows);
}

function showTerminal(): void {
  terminalPane.hidden = false;
  terminalBtn.classList.add('active');
  if (activeId) void attachTerminalTo(activeId);
  requestAnimationFrame(() => {
    try { fitAddon?.fit(); } catch { /* xterm not ready yet */ }
    term?.focus();
  });
  scheduleAck();  // terminal now visible — start the seen-timer (TASK-0157)
}

function hideTerminal(): void {
  terminalPane.hidden = true;
  terminalBtn.classList.remove('active');
}

function toggleTerminal(): void {
  if (terminalPane.hidden) showTerminal();
  else hideTerminal();
}

terminalBtn.addEventListener('click', toggleTerminal);
// Cmd+` triggers via the View → Toggle Terminal menu accelerator now;
// kept this listener as a fallback so Cmd+` works even when the
// renderer has focus on a child element that swallowed the accelerator.
document.addEventListener('keydown', (e) => {
  if (e.metaKey && e.key === '`') {
    e.preventDefault();
    toggleTerminal();
  }
  // Terminal clipboard keys (TASK-0167): ⌘C copies the xterm selection
  // when one exists (otherwise falls through to the shell's own binding);
  // ⌘V pastes into the PTY. Only while the terminal is focused.
  if (e.metaKey && !terminalPane.hidden && terminalMount.contains(document.activeElement)) {
    if (e.key === 'c' && term?.hasSelection()) {
      e.preventDefault();
      copyTerminalSelection();
    } else if (e.key === 'v') {
      e.preventDefault();
      void pasteIntoTerminal();
    }
  }
});

cockpitApi.menu.onRescan(() => { void rescanWorkspaces(); });
cockpitApi.menu.onToggleTerminal(() => { toggleTerminal(); });

cockpitApi.agent.onFocus((payload) => {
  if (!payload || typeof payload !== 'object') return;
  const p = payload as { url?: unknown; target?: unknown };
  const target = typeof p.target === 'string' ? p.target : '?';
  // The URL the server resolves is shaped like `/docs/features/…md`
  // (or `/README.md` for top-level support files); only the former
  // is renderable here.
  const url = typeof p.url === 'string' ? p.url : '';
  const rel = url.startsWith('/docs/') ? url.slice('/docs/'.length) : null;
  // Follow gate (TASK-0158 / REQ-0020): navigate only when this
  // workspace is in Following mode AND the user isn't parked on a
  // virtual page they opened deliberately. Otherwise the jump is
  // offered, never forced.
  // While the fleet is pinned and visible AND this workspace is
  // following, a follow updates the doc tab in the background rather
  // than evicting the fleet (TASK-0159). In Manual mode the focus is
  // ignored (falls through to the actionable toast) — the Manual
  // contract wins over the tab convenience.
  if (rel && isFollowing(activeId) && maybeBackgroundDocNav(rel)) {
    return;
  }
  const onVirtual = !!currentRel && currentRel.startsWith('~');
  const mayFollow = isFollowing(activeId) && !onVirtual;
  if (rel && mayFollow) {
    showStatus(`Agent focus → ${target}`);
    scheduleHide(1500);
    void navigateTo(rel);
  } else if (rel) {
    showActionStatus(`Agent focus → ${target}`, 'open', () => { void navigateTo(rel); });
    scheduleHide(6000);
  } else {
    showStatus(`Agent focus → ${target}`);
    scheduleHide(1500);
  }
});

// Dispatch a doc-pane text selection as an agent prompt (TASK-0168).
cockpitApi.agent.onDispatchSelection((text) => { void dispatchSelectionAsPrompt(text); });

async function dispatchSelectionAsPrompt(text: string): Promise<void> {
  const wsId = activeId;
  const trimmed = (text || '').trim();
  if (!wsId || !trimmed) return;
  const chosen = loadDispatchAgent();
  const preview = trimmed.length > 140 ? `${trimmed.slice(0, 140)}…` : trimmed;
  if (!window.confirm(`Dispatch the selected text to ${chosen}?\n\n${preview}`)) return;
  const item: QueuedDispatch = {
    id: currentFrontmatterId() || 'selection',
    rel: currentRel && !currentRel.startsWith('~') ? currentRel : '',
    agent: chosen,
    prompt: trimmed,
    ts: new Date().toISOString(),
  };
  const freshPty = !liveTerminals.has(wsId);
  showTerminal();
  await new Promise((r) => setTimeout(r, freshPty ? 600 : 150));
  const res = await cockpitApi.dispatch.execute(wsId, item);
  if ('error' in res && res.error) { showStatus(`Dispatch failed: ${res.error}`, 'error'); return; }
  showStatus(res.queued ? 'Queued selection' : `Dispatched selection (${res.delivered})`);
  scheduleHide(2000);
}

cockpitApi.deeplink.onUrl((url) => {
  // cockpit://<workspace-id>/<target>
  showStatus(`Deeplink received: ${url}`);
  scheduleHide(2000);
  try {
    const u = new URL(url);
    const wsId = u.host;
    if (wsId) void openWorkspace(wsId);
  } catch {
    /* malformed URL — already surfaced via showStatus */
  }
});

// Vertical resize via divider drag.
terminalDivider.addEventListener('mousedown', (downEv) => {
  downEv.preventDefault();
  const startY = downEv.clientY;
  const startHeight = terminalPane.getBoundingClientRect().height;
  const onMove = (moveEv: MouseEvent) => {
    const delta = startY - moveEv.clientY;
    const next = Math.min(window.innerHeight - 120, Math.max(80, startHeight + delta));
    terminalPane.style.height = `${next}px`;
  };
  const onUp = () => {
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onUp);
    try { fitAddon?.fit(); } catch { /* ignore */ }
  };
  document.addEventListener('mousemove', onMove);
  document.addEventListener('mouseup', onUp);
});

// Window resize → re-clamp a dragged-tall pane so it can't exceed a
// now-smaller window (moving to a smaller screen would otherwise push the
// prompt off the bottom — ISS-0016), then re-fit. The ResizeObserver also
// catches the fit, but the height clamp is a policy the observer can't do.
window.addEventListener('resize', () => {
  if (terminalPane.hidden) return;
  if (terminalPane.style.height) {
    const h = terminalPane.getBoundingClientRect().height;
    terminalPane.style.height =
      `${Math.min(window.innerHeight - 120, Math.max(80, h))}px`;
  }
  try { fitAddon?.fit(); } catch { /* ignore */ }
});

void loadWorkspaces();

// + button on the workspace rail rescans + adds (FEAT-0015 / TASK-0100).
// A full picker overlay is a future follow-up.
// FEAT-0016: rail `+` opens a native directory picker. If the picked
// dir is a project, add it; if it's a parent of projects, scan and
// add all SNAPSHOT-bearing descendants. Auto-discovery is gone.
wsRailAdd.addEventListener('click', () => { void addWorkspaceFlow(); });

// ---- Project settings popover (FEAT-0016 / TASK-0107) ----------------

function openProjectSettings(): void {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  psmName.value = effectiveName(ws);
  psmEmoji.value = ws.userEmoji ?? '';
  refreshSwatchSelection(ws.userColor ?? '');
  projectSettingsMenu.hidden = false;
  projectSettingsBtn.setAttribute('aria-expanded', 'true');
  // Defer focus so the click that opened the menu doesn't blur the
  // input via the document-level click-outside listener.
  setTimeout(() => psmName.focus(), 0);
}

function refreshSwatchSelection(currentColor: string): void {
  psmSwatches.querySelectorAll<HTMLButtonElement>('.psm-swatch').forEach((btn) => {
    btn.classList.toggle('is-active', (btn.dataset.color ?? '') === currentColor);
  });
}

function closeProjectSettings(): void {
  projectSettingsMenu.hidden = true;
  projectSettingsBtn.setAttribute('aria-expanded', 'false');
}

projectSettingsBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  if (projectSettingsMenu.hidden) openProjectSettings();
  else closeProjectSettings();
});

document.addEventListener('click', (e) => {
  if (projectSettingsMenu.hidden) return;
  const t = e.target as Node;
  if (!projectSettingsMenu.contains(t) && t !== projectSettingsBtn) {
    closeProjectSettings();
  }
});

document.addEventListener('keydown', (e) => {
  if (!projectSettingsMenu.hidden && e.key === 'Escape') {
    closeProjectSettings();
    projectSettingsBtn.focus();
  }
});

async function refreshActiveWorkspaceFromMain(): Promise<void> {
  workspaces = await cockpitApi.workspaces.list();
  renderWorkspaceRail();
  const ws = activeId ? workspaces.find((w) => w.id === activeId) : null;
  if (ws) setProjectHeader(ws);
}

// Save the rename on blur or Enter; revert on Escape.
async function commitRename(): Promise<void> {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  const next = psmName.value.trim();
  // If the user cleared the field or typed the auto-derived name back,
  // drop the override so future SNAPSHOT renames take effect again.
  const userName = (next === '' || next === ws.name) ? null : next;
  if ((ws.userName ?? null) === userName) return;
  await cockpitApi.workspaces.update({ id: activeId, userName });
  await refreshActiveWorkspaceFromMain();
}

psmName.addEventListener('blur', () => { void commitRename(); });
psmName.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); void commitRename().then(closeProjectSettings); }
  else if (e.key === 'Escape') {
    e.preventDefault();
    // Revert to current effective name + close.
    const ws = activeId ? workspaces.find((w) => w.id === activeId) : null;
    if (ws) psmName.value = effectiveName(ws);
    closeProjectSettings();
  }
});

psmPickIcon.addEventListener('click', async () => {
  if (!activeId) return;
  const pick = await cockpitApi.workspaces.pickIcon(activeId);
  if (!pick.ok) {
    if (pick.error && pick.error !== 'cancelled') {
      showStatus(`Icon: ${pick.error}`, 'error');
      scheduleHide(3000);
    }
    return;
  }
  await cockpitApi.workspaces.update({ id: activeId, userIcon: pick.dataUri ?? null });
  await refreshActiveWorkspaceFromMain();
  closeProjectSettings();
});

// Commit the emoji input on blur or Enter. Cleared = revert to icon
// chain. Apply on each input change so the user sees the rail update
// immediately as they type.
async function commitEmoji(): Promise<void> {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  const next = psmEmoji.value.trim();
  const userEmoji = next === '' ? null : next;
  if ((ws.userEmoji ?? null) === userEmoji) return;
  await cockpitApi.workspaces.update({ id: activeId, userEmoji });
  await refreshActiveWorkspaceFromMain();
}

psmEmoji.addEventListener('change', () => { void commitEmoji(); });
psmEmoji.addEventListener('blur',   () => { void commitEmoji(); });
psmEmoji.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); void commitEmoji(); }
});

// Color swatches.
psmSwatches.addEventListener('click', async (e) => {
  if (!activeId) return;
  const btn = (e.target as HTMLElement).closest<HTMLButtonElement>('.psm-swatch');
  if (!btn) return;
  const next = btn.dataset.color ?? '';
  await cockpitApi.workspaces.update({ id: activeId, userColor: next === '' ? null : next });
  await refreshActiveWorkspaceFromMain();
  refreshSwatchSelection(next);
});

// Reset clears all three overrides (uploaded icon, emoji, colour).
// Display reverts to: auto-probed favicon → identicon (hash colour).
psmResetIcon.addEventListener('click', async () => {
  if (!activeId) return;
  await cockpitApi.workspaces.update({
    id: activeId, userIcon: null, userEmoji: null, userColor: null,
  });
  await refreshActiveWorkspaceFromMain();
  closeProjectSettings();
});

psmReveal.addEventListener('click', () => {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  void cockpitApi.app.revealInFinder(ws.root);
  closeProjectSettings();
});

psmRemove.addEventListener('click', async () => {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  // eslint-disable-next-line no-alert
  const ok = window.confirm(
    `Remove "${effectiveName(ws)}" from the workspace list?\n\nThe project's files are not deleted.`,
  );
  if (!ok) return;
  const idToRemove = activeId;
  await cockpitApi.workspaces.remove(idToRemove);
  // Drop from local state + switch off if it was active.
  workspaces = workspaces.filter((w) => w.id !== idToRemove);
  closeProjectSettings();
  if (workspaces.length > 0) {
    activeId = null;
    void openWorkspace(workspaces[0].id);
  } else {
    activeId = null;
    placeholder.hidden = false;
    docView.hidden = true;
    setProjectHeader(null);
  }
  renderWorkspaceRail();
});

async function addWorkspaceFlow(): Promise<void> {
  wsRailAdd.disabled = true;
  showStatus('Choose a project folder…');
  try {
    const res = await cockpitApi.workspaces.pickAndAdd();
    if (res.cancelled) { hideStatus(); return; }
    if (res.error) {
      showStatus(res.error, 'error');
      scheduleHide(3000);
      return;
    }
    workspaces = res.workspaces;
    renderWorkspaceRail();
    const msg = res.skipped > 0
      ? `Added ${res.added}; skipped ${res.skipped} duplicate${res.skipped === 1 ? '' : 's'}.`
      : `Added ${res.added} project${res.added === 1 ? '' : 's'}.`;
    showStatus(msg);
    scheduleHide(2000);
  } catch (err) {
    showStatus(`Add failed: ${String(err)}`, 'error');
  } finally {
    wsRailAdd.disabled = false;
  }
}

// Tab keyboard shortcuts (FEAT-0014 / TASK-0097): Cmd/Ctrl+1..9 jumps
// to the Nth tab, Cmd+W closes the active tab.
document.addEventListener('keydown', (e) => {
  const meta = e.metaKey || e.ctrlKey;
  if (!meta) return;
  if (e.key >= '1' && e.key <= '9') {
    const idx = parseInt(e.key, 10) - 1;
    const ws = workspaces[idx];
    if (ws) {
      e.preventDefault();
      void openWorkspace(ws.id);
    }
    return;
  }
  if (e.key === 'w' || e.key === 'W') {
    if (activeId) {
      e.preventDefault();
      closeWorkspace(activeId);
    }
  }
});

// ----------------------------------------------------------------------
// In-workspace nav (FEAT-0010 / TASK-0083)
// ----------------------------------------------------------------------

interface NavItem {
  id?: string;
  title?: string;
  status?: string;
  url?: string;
  subtitle?: string;
  type?: string;
  children?: NavItem[];
}

interface NavGroupData {
  key?: string;
  label?: string;
  url?: string;
  status?: string;
  items?: NavItem[];
  item_layout?: string;          // 'stacked' | 'compact' | default
  subgroups?: NavGroupData[];
  default_open?: boolean;
}

interface NavPayload {
  schema_version: number;
  mode: string;
  platform: string;
  available_platforms?: string[];
  groups?: NavGroupData[];
}

const NAV_MODES = ['overview', 'features', 'tasks', 'issues', 'active', 'library', 'recent'] as const;
type NavMode = typeof NAV_MODES[number];

// Statuses that count as "completed" for the hide-completed filter.
// Mirror of cockpit.js COMPLETED_STATUSES so the desktop renderer
// matches the browser cockpit's idea of "done".
const COMPLETED_STATUSES = new Set([
  'done', 'merged', 'fixed', 'fulfilled', 'met', 'complete',
  'verified', 'passing', 'published', 'closed',
  'obsolete', 'retired', 'cancelled', 'superseded',
  'wont-fix', 'reverted', 'accepted',
]);

let hideCompleted = false;
try { hideCompleted = localStorage.getItem('cockpit:hide-completed') === '1'; }
catch { /* ignore */ }

// ----- Follow mode (FEAT-0034 / TASK-0158) -----------------------------
// Per-workspace: whether the centre pane follows agent `cockpit focus`
// events. Default following (matches mode-1). Even when following, a
// deliberately-opened virtual page (~agents/~overview/~session) is never
// evicted (REQ-0020) — the suppressed jump stays available via a
// clickable toast.
function followKey(wsId: string): string { return `cockpit:follow:${wsId}`; }
function isFollowing(wsId: string | null): boolean {
  if (!wsId) return true;
  try { return localStorage.getItem(followKey(wsId)) !== 'manual'; }
  catch { return true; }
}
function setFollowing(wsId: string, following: boolean): void {
  try { localStorage.setItem(followKey(wsId), following ? 'following' : 'manual'); }
  catch { /* storage unavailable — mode resets next launch */ }
}
function refreshFollowButton(): void {
  if (!followBtn) return;
  const following = isFollowing(activeId);
  followBtn.setAttribute('aria-pressed', following ? 'true' : 'false');
  followBtn.title = following
    ? 'Following agent navigation (click for Manual)'
    : 'Manual — ignoring agent navigation (click to Follow)';
}

// Ids of docs notes the active session is touching — drives the nav
// "agent" chip (TASK-0164). Derived from the session's docs_notes.
const sessionTouchedIds = new Set<string>();
// Numbered types stop at the numeric id (FEAT-0034, not the slug that
// follows); CHG ids are the full dated slug.
const ID_RE = /((?:TASK|ISS|FEAT|REQ|PHASE|RISK|TST|ADR)-\d+|CHG-[0-9A-Za-z-]+)/;
function refreshSessionTouched(): void {
  sessionTouchedIds.clear();
  const s = lastAgentSnap?.session ?? lastAgentSnap?.last_session;
  const notes = s?.work_notes ?? s?.docs_notes ?? [];
  for (const n of notes) {
    const m = String(n).match(ID_RE);
    if (m) sessionTouchedIds.add(m[1]);
  }
}

// Live-migrate the Active nav mode on a status transition (TASK-0164):
// reload the mode so the row moves to its new group, then flash it.
function handleStatusChange(c: { id?: string; to?: string }): void {
  if (currentNavMode === 'active' && sidecarBaseUrl) {
    void loadWsNav().then(() => { if (c.id) flashNavItem(c.id); });
  }
  // Phase-less Now board live-migration (TASK-0165).
  const board = docView.querySelector<HTMLElement>('.now-board');
  if (board && currentRel && currentRel.startsWith('~overview')) {
    void fillNowBoard(board).then(() => {
      if (!c.id) return;
      const card = board.querySelector<HTMLElement>(`.now-card-item[data-id="${CSS.escape(c.id)}"]`);
      if (card) {
        card.classList.add('now-card-flash');
        window.setTimeout(() => card.classList.remove('now-card-flash'), 1600);
      }
    });
  }
  noteWorkTransition(c);  // session "work" tab (TASK-0163)
}

function flashNavItem(id: string): void {
  const li = wsNavContent.querySelector<HTMLElement>(`li[data-id="${CSS.escape(id)}"]`);
  if (!li) return;
  li.classList.add('nav-status-flash');
  window.setTimeout(() => li.classList.remove('nav-status-flash'), 1600);
}

// ----- Centre tabs: doc + pinned Agents (FEAT-0034 / TASK-0159) --------
// A two-tab strip appears only while the Agents fleet is pinned open.
// The doc tab holds the last real note; follow/agent navigation updates
// it in the background (a dot) without leaving the fleet view.
const centerTabs = document.getElementById('center-tabs') as HTMLDivElement | null;
let agentsTabOpen = false;
let lastDocRel: string | null = null;
let docTabChanged = false;

function docTabLabel(): string {
  if (!lastDocRel) return 'Doc';
  const m = lastDocRel.match(/(?:^|\/)((?:TASK|ISS|FEAT|REQ|PHASE|RISK|CHG|ADR|TST)-[0-9A-Za-z-]+)/);
  if (m) return m[1].split('-').slice(0, 2).join('-');
  const base = lastDocRel.split('/').pop() || lastDocRel;
  return base.replace(/\.md$/, '');
}

function renderCenterTabs(): void {
  if (!centerTabs) return;
  if (!agentsTabOpen) { centerTabs.hidden = true; centerTabs.replaceChildren(); return; }
  centerTabs.hidden = false;
  centerTabs.replaceChildren();
  const onAgents = currentRel === '~agents';

  const docTab = document.createElement('button');
  docTab.type = 'button';
  docTab.className = 'center-tab' + (onAgents ? '' : ' on');
  docTab.setAttribute('role', 'tab');
  docTab.setAttribute('aria-selected', onAgents ? 'false' : 'true');
  docTab.textContent = docTabLabel();
  if (docTabChanged && onAgents) {
    const dot = document.createElement('span');
    dot.className = 'center-tab-dot';
    dot.title = 'updated in the background';
    docTab.appendChild(dot);
  }
  docTab.addEventListener('click', () => {
    docTabChanged = false;
    if (lastDocRel) void navigateTo(lastDocRel);
    else void navigateTo('~overview');
  });

  const agentsTab = document.createElement('button');
  agentsTab.type = 'button';
  agentsTab.className = 'center-tab' + (onAgents ? ' on' : '');
  agentsTab.setAttribute('role', 'tab');
  agentsTab.setAttribute('aria-selected', onAgents ? 'true' : 'false');
  const label = document.createElement('span');
  label.textContent = 'Agents';
  agentsTab.appendChild(label);
  const close = document.createElement('span');
  close.className = 'center-tab-close';
  close.textContent = '×';
  close.title = 'Close Agents tab';
  close.setAttribute('role', 'button');
  close.addEventListener('click', (e) => { e.stopPropagation(); closeAgentsTab(); });
  agentsTab.appendChild(close);
  agentsTab.addEventListener('click', () => { if (currentRel !== '~agents') void navigateTo('~agents'); });

  centerTabs.append(docTab, agentsTab);
}

function closeAgentsTab(): void {
  agentsTabOpen = false;
  renderCenterTabs();
  if (currentRel === '~agents') {
    if (lastDocRel) void navigateTo(lastDocRel);
    else void navigateTo('~overview');
  }
}

// Follow/agent navigation targeting a doc while the fleet is pinned and
// visible updates the doc tab in the background instead of evicting the
// fleet (TASK-0159). Returns true if it consumed the navigation.
function maybeBackgroundDocNav(rel: string): boolean {
  if (agentsTabOpen && currentRel === '~agents') {
    lastDocRel = rel;
    docTabChanged = true;
    renderCenterTabs();
    return true;
  }
  return false;
}

function isCompletedStatus(status: string | undefined): boolean {
  if (!status) return false;
  return COMPLETED_STATUSES.has(String(status).toLowerCase());
}

function isItemHidden(item: { status?: string }): boolean {
  return hideCompleted && isCompletedStatus(item.status);
}

function loadStoredNavMode(): NavMode {
  try {
    const v = localStorage.getItem('cockpit:nav-mode');
    if (v && (NAV_MODES as readonly string[]).includes(v)) return v as NavMode;
  } catch { /* localStorage unavailable */ }
  return 'features';
}

let currentNavMode: NavMode = loadStoredNavMode();

function setNavMode(mode: NavMode): void {
  currentNavMode = mode;
  try { localStorage.setItem('cockpit:nav-mode', mode); } catch { /* ignore */ }
  refreshNavModeButtons();
  if (sidecarBaseUrl) void loadWsNav();
}

function refreshNavModeButtons(): void {
  // Mode icons live in the window-wide top bar (FEAT-0015 it. 2).
  document.querySelectorAll<HTMLButtonElement>('.top-bar-btn[data-mode]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.mode === currentNavMode);
  });
}

// ----- Overview dashboard (FEAT-0017 / TASK-0110) --------------------

interface StatsHero {
  features: { total: number; done: number };
  tasks:    { total: number; done: number };
  issues:   { total: number; open: number };
  tests:    { total: number; passing: number };
  risks:    { total: number; open: number };
  requirements?: { total: number; done: number };
  last_change?: { id?: string; title: string; rel: string; date: string } | null;
}
interface PhaseItem {
  id?: string; title: string; rel?: string;
  status: string; bucket: 'done' | 'in_progress' | 'backlog';
  type: string;
}
interface PhaseFeature extends PhaseItem { children: PhaseItem[] }
interface StatsPhase {
  key: string; title: string; status: string | null; rel?: string | null;
  tasks: { done: number; in_progress: number; backlog: number };
  features: PhaseFeature[];
  loose: PhaseItem[];
}
interface StatsRecent { id?: string; title: string; rel: string; date: string; type?: string; features?: string[] }
interface StatsPayload {
  schema_version: number;
  scope?: { id: string; title: string; status: string; rel: string } | null;
  exit_criteria?: Array<{ text: string; done: boolean }> | null;
  hero: StatsHero;
  phases: StatsPhase[];
  status_mix: Record<string, Record<string, number>>;
  activity: {
    weekly: Array<{ week_iso: string; start_date: string; count: number }>;
    recent: StatsRecent[];
  };
}

// Current Overview scope (FEAT-0023): null = whole project, else a
// PHASE-#### id. The scope list for the left pane is cached from the
// last unscoped payload (server-side stats cache makes refetch cheap).
let overviewScope: string | null = null;
let scopePhaseList: StatsPhase[] | null = null;

async function renderOverviewPage(scope: string | null): Promise<boolean> {
  if (!sidecarBaseUrl) return false;
  const q = scope ? `?scope=${encodeURIComponent(scope)}` : '';
  let resp: Response;
  try {
    resp = await fetch(`${sidecarBaseUrl}/api/cockpit/stats${q}`);
  } catch (err) {
    showStatus(`Stats fetch failed: ${String(err)}`, 'error');
    return false;
  }
  if (resp.status === 404) {
    // The requested scope doesn't exist in this project (a remembered
    // phase from another workspace, a phase-less project, or a stale
    // deep link). Degrade to the unscoped project overview instead of
    // erroring (TASK-0177).
    if (scope !== null) {
      overviewScope = null;
      scopePhaseList = null;
      return renderOverviewPage(null);
    }
    showStatus(`Unknown phase: ${scope}`, 'error');
    return false;
  }
  if (!resp.ok) {
    showStatus(`Stats fetch failed: HTTP ${resp.status}`, 'error');
    return false;
  }
  const data = (await resp.json()) as StatsPayload;
  overviewScope = scope;
  if (!scope) {
    scopePhaseList = data.phases;
  } else if (!scopePhaseList) {
    // Entered a scope directly (deep link / history) — fetch the full
    // phase list for the scope pane; the server cache absorbs it.
    void (async () => {
      try {
        const r = await fetch(`${sidecarBaseUrl}/api/cockpit/stats`);
        if (r.ok) {
          scopePhaseList = ((await r.json()) as StatsPayload).phases;
          renderOverviewScopePane();
        }
      } catch { /* pane fills on next project-scope visit */ }
    })();
  }
  renderOverviewScopePane();
  if (scope && data.scope) renderScopedOverview(data);
  else renderProjectOverview(data);
  void renderOverviewRightPane(scope && data.scope ? data.scope.rel : null);
  return true;
}

function renderProjectOverview(data: StatsPayload): void {
  docView.classList.add('overview-pane');
  docView.classList.remove('agents-page');
  // Phase-less projects get a live Now board instead of an empty phase
  // grid (TASK-0165) — the same in-flight data as the Active nav mode.
  const middle = data.phases.length === 0
    ? buildNowBoard()
    : buildPhaseSection(data.phases);
  docView.replaceChildren(
    buildHero(data.hero),
    middle,
    buildBottomGrid(data),
    buildFeedsGrid(data),
  );
  docView.hidden = false;
  placeholder.hidden = true;
  refreshFooterPath();
}

// Now board (TASK-0165): Doing / Next / Done-today columns rendered
// from the Active-mode data, live-migrating on status transitions.
function buildNowBoard(): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-now-board';
  const h = document.createElement('h3');
  h.textContent = 'Now — work in flight';
  wrap.appendChild(h);
  const board = document.createElement('div');
  board.className = 'now-board';
  wrap.appendChild(board);
  void fillNowBoard(board);
  return wrap;
}

async function fillNowBoard(board: HTMLElement): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/nav?mode=active`);
    if (!resp.ok) return;
    const data = await resp.json() as { groups: NavGroupData[] };
    board.replaceChildren();
    if (data.groups.length === 0) {
      const empty = document.createElement('p');
      empty.className = 'meta';
      empty.textContent = 'Nothing in flight right now.';
      board.appendChild(empty);
      return;
    }
    for (const g of data.groups) {
      const items = g.items ?? [];
      const col = document.createElement('div');
      col.className = 'now-col';
      const head = document.createElement('div');
      head.className = 'now-col-head';
      head.textContent = `${g.label} · ${items.length}`;
      col.appendChild(head);
      for (const it of items) {
        const card = document.createElement('button');
        card.type = 'button';
        card.className = 'now-card-item';
        if (it.id) card.dataset.id = String(it.id);
        appendIf(card, typeIcon(it.type));
        const idl = document.createElement('span');
        idl.className = 'now-card-id mono';
        idl.textContent = it.id || '';
        card.appendChild(idl);
        if (it.id && sessionTouchedIds.has(it.id)) {
          const chip = document.createElement('span');
          chip.className = 'nav-agent-chip';
          chip.textContent = 'agent';
          card.appendChild(chip);
        }
        appendIf(card, statusChip(it.status));
        const rel = extractRel(it.url);
        if (rel) card.addEventListener('click', () => void navigateTo(rel));
        col.appendChild(card);
      }
      board.appendChild(col);
    }
  } catch { /* transient — ignore */ }
}

function buildHero(hero: StatsHero): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-hero';
  const fmt = (n: number, total: number): string => total ? `${n} / ${total}` : '—';
  const cell = (label: string, value: string, sub?: string): HTMLElement => {
    const el = document.createElement('div');
    el.className = 'ov-hero-cell';
    el.innerHTML = `<div class="ov-hero-value">${value}</div>`
      + `<div class="ov-hero-label">${label}</div>`
      + (sub ? `<div class="ov-hero-sub">${sub}</div>` : '');
    return el;
  };
  wrap.append(
    cell('Features', fmt(hero.features.done, hero.features.total)),
    cell('Tasks',    fmt(hero.tasks.done,    hero.tasks.total)),
    cell('Issues',   String(hero.issues.open), `${hero.issues.total} total`),
    cell('Tests',    `${hero.tests.passing} / ${hero.tests.total}`),
    cell('Risks',    String(hero.risks.open), `${hero.risks.total} total`),
  );
  if (hero.last_change) {
    const last = document.createElement('div');
    last.className = 'ov-hero-cell ov-hero-last';
    last.innerHTML = `<div class="ov-hero-value ov-hero-last-title">${escapeHtml(hero.last_change.title)}</div>`
      + `<div class="ov-hero-label">Last change</div>`
      + `<div class="ov-hero-sub">${escapeHtml(hero.last_change.date)}</div>`;
    last.style.cursor = 'pointer';
    last.title = hero.last_change.rel;
    last.addEventListener('click', () => {
      if (hero.last_change?.rel) void navigateTo(hero.last_change.rel);
    });
    wrap.appendChild(last);
  }
  return wrap;
}

function buildPhaseSection(phases: StatsPhase[]): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section';
  wrap.innerHTML = '<h3>Progress by phase</h3>';
  for (const p of phases) {
    const total = p.tasks.done + p.tasks.in_progress + p.tasks.backlog;
    const row = document.createElement('div');
    row.className = 'ov-phase';
    const titleHtml = p.rel
      ? `<a class="ov-phase-title" href="#" data-rel="${escapeHtml(p.rel)}">${escapeHtml(p.title)}</a>`
      : `<span class="ov-phase-title">${escapeHtml(p.title)}</span>`;
    const meta = document.createElement('div');
    meta.className = 'ov-phase-meta';
    meta.innerHTML = `${titleHtml}<span class="ov-phase-count">${p.tasks.done}/${total}</span>`;
    row.appendChild(meta);

    const bar = document.createElement('div');
    bar.className = 'ov-phase-bar';
    bar.title = `${p.tasks.done} done · ${p.tasks.in_progress} in progress · ${p.tasks.backlog} backlog`;
    // Per-feature group: feature square (slightly larger) followed by
    // its child squares (smaller). Loose items get their own trailing
    // group with a distinct dashed border.
    for (const feat of p.features) {
      bar.appendChild(buildPhaseFeatureGroup(feat));
    }
    if (p.loose.length > 0) {
      bar.appendChild(buildPhaseLooseGroup(p.loose));
    }
    if (p.features.length === 0 && p.loose.length === 0) {
      const empty = document.createElement('span');
      empty.className = 'ov-phase-empty';
      empty.textContent = '(no items)';
      bar.appendChild(empty);
    }
    row.appendChild(bar);

    // Selecting a phase drills into its scoped dashboard (FEAT-0023) —
    // the note itself is reachable from the scoped header's "open note".
    if (/^PHASE-/i.test(p.key)) {
      const link = meta.querySelector<HTMLAnchorElement>('a.ov-phase-title');
      (link ?? meta).addEventListener('click', (e) => {
        e.preventDefault();
        void navigateTo(`~overview/${p.key}`);
      });
      meta.style.cursor = 'pointer';
    }
    wrap.appendChild(row);
  }
  return wrap;
}

function makePhaseSquare(item: PhaseItem, isFeature: boolean): HTMLElement {
  const sq = document.createElement('span');
  sq.className = 'ov-phase-sq' + (isFeature ? ' is-feature' : '');
  sq.dataset.bucket = item.bucket;
  sq.dataset.type = item.type;
  sq.title = `${item.id ?? ''} ${item.title} (${item.status || '—'})`.trim();
  if (item.rel) {
    sq.style.cursor = 'pointer';
    sq.addEventListener('click', () => {
      setNavMode('features');
      void navigateTo(item.rel!);
    });
  }
  return sq;
}

function buildPhaseFeatureGroup(feat: PhaseFeature): HTMLElement {
  const g = document.createElement('span');
  g.className = 'ov-phase-group';
  g.title = `${feat.id ?? ''} ${feat.title}`.trim();
  g.appendChild(makePhaseSquare(feat, true));
  for (const c of feat.children) g.appendChild(makePhaseSquare(c, false));
  return g;
}

function buildPhaseLooseGroup(loose: PhaseItem[]): HTMLElement {
  const g = document.createElement('span');
  g.className = 'ov-phase-group ov-phase-group-loose';
  g.title = `${loose.length} item${loose.length === 1 ? '' : 's'} without a parent feature`;
  for (const c of loose) g.appendChild(makePhaseSquare(c, false));
  return g;
}

const STATUS_COLOR_BY_KEY: Record<string, string> = {
  // Done family
  done: 'var(--status-done)', merged: 'var(--status-done)', verified: 'var(--status-done)',
  closed: 'var(--status-done)', fixed: 'var(--status-done)', complete: 'var(--status-done)',
  passing: 'var(--status-done)', accepted: 'var(--status-done)',
  // Active family
  active: 'var(--status-active)', doing: 'var(--status-active)',
  'in-progress': 'var(--status-active)', in_progress: 'var(--status-active)',
  proposed: 'var(--status-active)', draft: 'var(--status-active)',
  // Blocked / negative
  blocked: 'var(--severity-high)', failed: 'var(--severity-critical)',
  cancelled: 'var(--text-faint)', superseded: 'var(--text-faint)',
  retired: 'var(--text-faint)', obsolete: 'var(--text-faint)',
  // Backlog / planned
  backlog: 'var(--text-faint)', planned: 'var(--text-faint)',
  triage: 'var(--severity-medium)', open: 'var(--severity-medium)',
};

function donutGradient(mix: Record<string, number>): string {
  const total = Object.values(mix).reduce((a, b) => a + b, 0);
  if (total === 0) return `var(--text-faint)`;
  // Sort entries so the donut has a stable arc order.
  const entries = Object.entries(mix).sort((a, b) => b[1] - a[1]);
  const parts: string[] = [];
  let acc = 0;
  for (const [status, count] of entries) {
    const start = (acc / total) * 100;
    acc += count;
    const end = (acc / total) * 100;
    const color = STATUS_COLOR_BY_KEY[status] || 'var(--text-muted)';
    parts.push(`${color} ${start}% ${end}%`);
  }
  return `conic-gradient(${parts.join(', ')})`;
}

function buildBottomGrid(data: StatsPayload): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-bottom';

  // Activity histogram on the left.
  const activity = document.createElement('div');
  activity.className = 'ov-tile ov-activity';
  const maxCount = Math.max(1, ...data.activity.weekly.map((w) => w.count));
  const bars = data.activity.weekly.map((w) => {
    const pct = (w.count / maxCount) * 100;
    return `<span class="ov-act-bar" title="${w.week_iso} · ${w.count} change${w.count === 1 ? '' : 's'}" style="height:${pct}%"></span>`;
  }).join('');
  activity.innerHTML = `
    <h3>Activity (last 13 weeks)</h3>
    <div class="ov-act-chart">${bars}</div>
    <div class="ov-act-axis"><span>13w</span><span>now</span></div>`;
  wrap.appendChild(activity);

  // Donuts on the right.
  const donuts = document.createElement('div');
  donuts.className = 'ov-tile ov-donuts';
  donuts.innerHTML = '<h3>Status mix</h3>';
  const grid = document.createElement('div');
  grid.className = 'ov-donut-grid';
  for (const key of ['features', 'tasks', 'issues', 'requirements']) {
    const mix = data.status_mix[key] || {};
    const total = Object.values(mix).reduce((a, b) => a + b, 0);
    const d = document.createElement('div');
    d.className = 'ov-donut-cell';
    d.innerHTML = `
      <div class="ov-donut" style="background: ${donutGradient(mix)}">
        <div class="ov-donut-hole">${total}</div>
      </div>
      <div class="ov-donut-label">${key}</div>`;
    grid.appendChild(d);
  }
  donuts.appendChild(grid);
  wrap.appendChild(donuts);
  return wrap;
}

function buildRecentFeed(recent: StatsRecent[]): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-feed';
  wrap.innerHTML = '<h3>Recent activity</h3>';
  if (recent.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No changes recorded yet.';
    wrap.appendChild(empty);
    return wrap;
  }
  const ul = document.createElement('ul');
  ul.className = 'ov-feed-list';
  for (const r of recent) {
    const li = document.createElement('li');
    const typeTag = r.type
      ? `<span class="ov-feed-type ov-feed-type-${escapeHtml(r.type)}">${escapeHtml(r.type)}</span>`
      : '';
    const idTag = r.id ? `<span class="ov-feed-id">${escapeHtml(r.id)}</span>` : '';
    const featTag = r.features && r.features.length
      ? `<span class="ov-feed-tag">${escapeHtml(r.features.join(', '))}</span>`
      : '';
    li.innerHTML = `
      <span class="ov-feed-date">${escapeHtml(r.date)}</span>
      ${typeTag}
      ${idTag}
      <span class="ov-feed-title">${escapeHtml(r.title)}</span>
      ${featTag}`;
    li.style.cursor = 'pointer';
    li.title = r.rel;
    li.addEventListener('click', () => {
      if (r.rel) {
        setNavMode('features');
        void navigateTo(r.rel);
      }
    });
    ul.appendChild(li);
  }
  wrap.appendChild(ul);
  return wrap;
}

// Wire the top-bar + rail-tools controls (FEAT-0015 iteration 2):
// mode icons + collapse buttons in the top bar; hide-completed +
// terminal + settings on the workspace rail. Runs once at startup
// after TYPE_ICONS / GROUP_ICONS are declared.
function initNavToolbar(): void {
  const modeIconMap: Record<string, string> = {
    // Lucide bar-chart: bars of varying heights — reads as "stats".
    overview: '<line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/>',
    features: TYPE_ICONS.feature,
    tasks:    TYPE_ICONS.task,
    issues:   TYPE_ICONS.issue,
    // Active: a "pulse/activity" line — work in motion.
    active:   '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    library:  TYPE_ICONS.reference,
    recent:   GROUP_ICONS.history,
  };
  document.querySelectorAll<HTMLButtonElement>('.top-bar-btn[data-mode]').forEach((btn) => {
    const mode = btn.dataset.mode as NavMode;
    const paths = modeIconMap[mode] || TYPE_ICONS._default;
    btn.replaceChildren(makeSvg(paths, 16, {}));
    btn.addEventListener('click', () => {
      if ((NAV_MODES as readonly string[]).includes(mode)) setNavMode(mode);
    });
  });

  // Hide-completed: eye-strikethrough icon. Flips the `hideCompleted`
  // module state and re-renders the nav so the filter actually drops
  // done/closed/verified/... items (mirrors the browser cockpit's
  // COMPLETED_STATUSES list).
  const eyeOff = '<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/>';
  hideCompletedBtn.replaceChildren(makeSvg(eyeOff, 16, {}));
  hideCompletedBtn.setAttribute('aria-pressed', hideCompleted ? 'true' : 'false');
  hideCompletedBtn.addEventListener('click', () => {
    hideCompleted = !hideCompleted;
    hideCompletedBtn.setAttribute('aria-pressed', hideCompleted ? 'true' : 'false');
    try { localStorage.setItem('cockpit:hide-completed', hideCompleted ? '1' : '0'); } catch { /* ignore */ }
    if (sidecarBaseUrl) void loadWsNav();
    // Also re-apply the filter to the right pane in place — no fetch
    // needed since the last payload is cached.
    if (lastContextPayload) renderRightPane(lastContextPayload);
  });

  // Terminal toggle (existing click handler registered later in the
  // file). Search opens the quick-switch palette; Pinned + Settings
  // are disabled placeholders. All SVGs injected here.
  terminalBtn.replaceChildren(makeSvg(GROUP_ICONS.terminal, 18, {}));
  const agentsBtn = document.getElementById('agents-toggle');
  if (agentsBtn) {
    agentsBtn.replaceChildren(makeSvg(GROUP_ICONS.agents, 18, {}));
    agentsBtn.addEventListener('click', () => {
      if (!sidecarBaseUrl) return;  // need a workspace open to host the page
      void navigateTo('~agents');
    });
  }
  if (followBtn) {
    followBtn.replaceChildren(makeSvg(GROUP_ICONS.follow, 18, {}));
    refreshFollowButton();
    followBtn.addEventListener('click', () => {
      if (!activeId) return;
      const next = !isFollowing(activeId);
      setFollowing(activeId, next);
      refreshFollowButton();
      showStatus(next ? 'Following agent navigation' : 'Manual — agent navigation ignored');
      scheduleHide(1500);
    });
  }
  const settingsBtn = document.getElementById('settings-toggle');
  if (settingsBtn) settingsBtn.replaceChildren(makeSvg(GROUP_ICONS.settings, 18, {}));
  const searchBtn = document.getElementById('search-toggle') as HTMLButtonElement | null;
  if (searchBtn) {
    searchBtn.replaceChildren(makeSvg(GROUP_ICONS.search, 18, {}));
    searchBtn.addEventListener('click', () => {
      if (quickSwitchEl.hidden) openQuickSwitch();
      else closeQuickSwitch();
    });
  }
  // Rail star removed — the per-doc pin now lives in the top bar
  // (right of the search field). Library mode shows the Pinned group.

  // Left-pane collapse — toggles .app.left-collapsed + syncs CSS
  // variables so the top-bar's left zone and the grid's nav column
  // both shrink to button-width.
  leftPaneCollapseBtn.addEventListener('click', () => {
    applyLeftPaneState(!appEl.classList.contains('left-collapsed'));
  });
  // Hydrate persisted state.
  let leftCollapsedInit = false;
  try {
    leftCollapsedInit = localStorage.getItem(LEFT_PANE_STORAGE_KEY) === '1';
  } catch { /* ignore */ }
  applyLeftPaneState(leftCollapsedInit);

  // Right-pane: paint icon now that PANEL_RIGHT_* paths exist.
  paintRightCollapse();

  refreshNavModeButtons();
}

// initModeRibbon() is invoked LATER — after TYPE_ICONS / GROUP_ICONS
// are declared (temporal-dead-zone). See the call near the bottom of
// the item-render port section.

// Platform filter (FEAT-0015 / TASK-0102). Persisted per-workspace
// because each project has its own platform vocabulary.

function platformStorageKey(): string {
  return `cockpit:platform:${activeId || '_'}`;
}

function loadStoredPlatform(): string {
  try {
    const v = localStorage.getItem(platformStorageKey());
    if (v) return v;
  } catch { /* ignore */ }
  return 'all';
}

function setPlatform(p: string): void {
  try { localStorage.setItem(platformStorageKey(), p); } catch { /* ignore */ }
  if (sidecarBaseUrl) void loadWsNav();
}

function renderPlatformBar(available: string[] | undefined): void {
  const list = available || [];
  if (list.length <= 1) {
    platformBarEl.hidden = true;
    return;
  }
  platformBarEl.hidden = false;
  const current = loadStoredPlatform();
  platformLabel.textContent = current;
  platformMenu.replaceChildren();
  for (const p of ['all', ...list]) {
    const li = document.createElement('li');
    li.textContent = p;
    li.dataset.value = p;
    li.setAttribute('role', 'option');
    if (p === current) li.classList.add('is-active');
    li.addEventListener('click', () => {
      closePlatformMenu();
      setPlatform(p);
    });
    platformMenu.appendChild(li);
  }
}

function openPlatformMenu(): void {
  platformMenu.hidden = false;
  platformCombo.setAttribute('aria-expanded', 'true');
}

function closePlatformMenu(): void {
  platformMenu.hidden = true;
  platformCombo.setAttribute('aria-expanded', 'false');
}

platformCombo.addEventListener('click', (e) => {
  e.stopPropagation();
  if (platformMenu.hidden) openPlatformMenu();
  else closePlatformMenu();
});

document.addEventListener('click', (e) => {
  if (platformMenu.hidden) return;
  const t = e.target as Node;
  if (!platformBarEl.contains(t)) closePlatformMenu();
});

document.addEventListener('keydown', (e) => {
  if (!platformMenu.hidden && e.key === 'Escape') closePlatformMenu();
});

async function loadWsNav(): Promise<void> {
  if (!sidecarBaseUrl) return;
  if (currentNavMode === 'overview') {
    // Overview is a virtual page (FEAT-0023 / TASK-0130): route through
    // navigateTo so it lands in history and back/forward can reach it.
    const target = overviewScope ? `~overview/${overviewScope}` : '~overview';
    void navigateTo(target, { replace: currentRel === target });
    return;
  }
  const platform = loadStoredPlatform();
  const platformQ = platform && platform !== 'all'
    ? `&platform=${encodeURIComponent(platform)}` : '';
  // The server's Library mode emits a "Pinned" group when we hand it
  // the list of pinned rel-paths. Mode-1 cockpit uses the same query.
  const pins = activeId ? loadPinned(activeId) : [];
  const pinnedQ = pins.length > 0
    ? `&pinned=${encodeURIComponent(pins.join(','))}` : '';
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/nav?mode=${encodeURIComponent(currentNavMode)}${platformQ}${pinnedQ}`,
    );
    if (!resp.ok) {
      showStatus(`Nav fetch failed: HTTP ${resp.status}`, 'error');
      return;
    }
    const data = (await resp.json()) as NavPayload;
    renderPlatformBar(data.available_platforms);
    renderWsNav(data);
  } catch (err) {
    showStatus(`Nav fetch failed: ${String(err)}`, 'error');
  }
}

function renderWsNav(data: NavPayload): void {
  wsNavPlaceholder.hidden = true;
  wsNavContent.hidden = false;
  wsNavContent.innerHTML = '';
  const groups = data.groups || [];
  if (groups.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.style.padding = '24px 16px';
    empty.textContent = `(no items for mode "${data.mode}")`;
    wsNavContent.appendChild(empty);
    return;
  }
  let any = false;
  for (const group of groups) {
    const node = renderNavGroup(group, currentNavMode);
    if (node) {
      wsNavContent.appendChild(node);
      any = true;
    }
  }
  if (!any) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.style.padding = '24px 16px';
    empty.textContent = hideCompleted
      ? 'Everything in this view is completed (toggle the eye icon to show).'
      : `(no items for mode "${data.mode}")`;
    wsNavContent.appendChild(empty);
  }
  refreshActiveNavRow();
}

// ----------------------------------------------------------------------
// Item renderers (FEAT-0014 / TASK-0099) — ported from cockpit.js so the
// native renderer emits the same DOM as the browser cockpit. cockpit.css
// styles every selector below; no new CSS needed.
// ----------------------------------------------------------------------

const SVG_NS = 'http://www.w3.org/2000/svg';

// Lucide-style monochrome paths keyed by note type. Stroke uses
// currentColor so the per-type CSS tokens (cockpit.css) drive the hue.
const TYPE_ICONS: Record<string, string> = {
  feature:     '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><path d="M4 22V15"/>',
  task:        '<path d="m9 11 3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
  issue:       '<polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
  requirement: '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>',
  phase:       '<path d="M3 9h18"/><path d="M3 15h18"/><path d="M5 4v16"/><path d="M19 4v16"/><path d="M9 9v6"/><path d="M15 9v6"/>',
  change:      '<line x1="3" x2="9" y1="12" y2="12"/><line x1="15" x2="21" y1="12" y2="12"/><circle cx="12" cy="12" r="3"/>',
  adr:         '<path d="m16 16 3-8 3 8c-2 1-4 1-6 0z"/><path d="m2 16 3-8 3 8c-2 1-4 1-6 0z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
  decision:    '<path d="m16 16 3-8 3 8c-2 1-4 1-6 0z"/><path d="m2 16 3-8 3 8c-2 1-4 1-6 0z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
  risk:        '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
  test:        '<path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7"/><path d="M7 16h10"/>',
  workflow:    '<rect width="8" height="8" x="3" y="3" rx="2"/><path d="M7 11v4a2 2 0 0 0 2 2h4"/><rect width="8" height="8" x="13" y="13" rx="2"/>',
  release:     '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="m7.5 4.27 9 5.15"/>',
  reference:   '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
  plan:        '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15"/><path d="M15 6v15"/>',
  _default:    '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
};

const GROUP_ICONS: Record<string, string> = {
  agents:        '<rect width="16" height="10" x="4" y="10" rx="2"/><path d="M12 6v4"/><circle cx="12" cy="4" r="1.5"/><path d="M9 14h.01"/><path d="M15 14h.01"/><path d="M2 14h2"/><path d="M20 14h2"/>',
  follow:        '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2.5"/><path d="M12 2v3"/><path d="M12 19v3"/><path d="M2 12h3"/><path d="M19 12h3"/>',
  star:          '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
  folder_tree:   '<path d="M20 10a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1h-2.5a1 1 0 0 1-.8-.4l-.9-1.2A1 1 0 0 0 15 3h-2a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1Z"/><path d="M20 21a1 1 0 0 0 1-1v-3a1 1 0 0 0-1-1h-2.9a1 1 0 0 1-.88-.55l-.42-.85a1 1 0 0 0-.92-.6H13a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1Z"/><path d="M3 5a2 2 0 0 0 2 2h3"/><path d="M3 3v13a2 2 0 0 0 2 2h3"/>',
  layers:        '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.18-9.43 4.27a2 2 0 0 1-1.66 0L2 12.18"/><path d="m22 17.18-9.43 4.27a2 2 0 0 1-1.66 0L2 17.18"/>',
  list_checks:   '<path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/><path d="M13 18h8"/>',
  alert_octagon: '<polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
  sun:           '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
  moon:          '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  calendar_days: '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/>',
  calendar:      '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
  history:       '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
  search:        '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  graph:         '<circle cx="12" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/><path d="M10.6 7.4 6.4 16.6"/><path d="m13.4 7.4 4.2 9.2"/>',
  settings:      '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.5a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
  terminal:      '<path d="m7 11 2-2-2-2"/><path d="M11 13h4"/><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>',
};

function typeIcon(type: string | undefined, size = 14): SVGElement | null {
  if (!type) return null;
  const key = String(type).toLowerCase();
  const paths = TYPE_ICONS[key] || TYPE_ICONS._default;
  return makeSvg(paths, size, { class: 'type-icon', 'data-type': key });
}

function makeSvg(
  paths: string,
  size: number,
  attrs: Record<string, string>,
): SVGElement {
  const svg = document.createElementNS(SVG_NS, 'svg');
  for (const [k, v] of Object.entries(attrs)) svg.setAttribute(k, v);
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('width', String(size));
  svg.setAttribute('height', String(size));
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '2');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.setAttribute('aria-hidden', 'true');
  svg.innerHTML = paths;
  return svg;
}

// Lucide panel-left / panel-right SVGs — the shapes the HTML cockpit
// uses for its sidebar toggles (matches cockpit.js). Chevron points
// inward when the pane is open ("click to close") and outward when
// collapsed ("click to open").
const PANEL_LEFT_CLOSE =
  '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
  + '<line x1="9" x2="9" y1="3" y2="21"/>'
  + '<path d="m16 15-3-3 3-3"/>';
const PANEL_LEFT_OPEN =
  '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
  + '<line x1="9" x2="9" y1="3" y2="21"/>'
  + '<path d="m13 15 3-3-3-3"/>';
const PANEL_RIGHT_CLOSE =
  '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
  + '<line x1="15" x2="15" y1="3" y2="21"/>'
  + '<path d="m8 9 3 3-3 3"/>';
const PANEL_RIGHT_OPEN =
  '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
  + '<line x1="15" x2="15" y1="3" y2="21"/>'
  + '<path d="m11 9-3 3 3 3"/>';

const RECENT_BUCKET_ICONS: Record<string, string> = {
  today:     GROUP_ICONS.sun,
  yesterday: GROUP_ICONS.moon,
  week:      GROUP_ICONS.calendar_days,
  month:     GROUP_ICONS.calendar,
  earlier:   GROUP_ICONS.history,
};

function groupIcon(mode: NavMode, group: NavGroupData): SVGElement | null {
  const key = String(group.key || '');
  if (key === 'pinned')    return makeSvg(GROUP_ICONS.star, 13, { class: 'group-icon' });
  if (key === 'docs-tree') return makeSvg(GROUP_ICONS.folder_tree, 13, { class: 'group-icon' });
  if (key.indexOf('rare:') === 0) return typeIcon(key.slice(5), 13);
  if (mode === 'features') return makeSvg(GROUP_ICONS.layers, 13, { class: 'group-icon' });
  if (mode === 'tasks')    return makeSvg(GROUP_ICONS.list_checks, 13, { class: 'group-icon', 'data-status': key });
  if (mode === 'issues')   return makeSvg(GROUP_ICONS.alert_octagon, 13, { class: 'group-icon', 'data-severity': key });
  if (mode === 'recent')   return makeSvg(RECENT_BUCKET_ICONS[key] || GROUP_ICONS.history, 13, { class: 'group-icon' });
  return null;
}

function statusChip(status: string | undefined): HTMLSpanElement | null {
  if (!status) return null;
  const span = document.createElement('span');
  span.className = 'status-chip';
  span.dataset.status = status.toLowerCase().replace(/\s+/g, '-');
  span.textContent = status;
  return span;
}

function navLineSpacer(): HTMLSpanElement {
  const s = document.createElement('span');
  s.className = 'nav-line-spacer';
  return s;
}

function appendIf<T extends Node>(parent: Node, child: T | null): void {
  if (child) parent.appendChild(child);
}

// ----- Item layout dispatcher

type ItemRenderer = (item: NavItem) => HTMLLIElement;

function pickItemRenderer(layout: string | undefined): ItemRenderer {
  if (layout === 'stacked') return navItemStacked;
  if (layout === 'compact') return navItemCompact;
  return navItem;
}

// ----- Default layout (Features / Tasks / Issues / Recent)
// row 1: [icon] [id] [spacer] [status]
// row 2: [title]
// row 3: [subtitle] (when present)

function navItem(item: NavItem): HTMLLIElement {
  const li = document.createElement('li');
  const rel = extractRel(item.url);
  if (rel) li.dataset.rel = rel;
  if (item.id) li.dataset.id = String(item.id);
  if (item.type) li.dataset.type = String(item.type);
  if (item.status) li.dataset.status = String(item.status);

  const card = document.createElement('div');
  card.className = 'nav-item';

  const line = document.createElement('div');
  line.className = 'nav-line';
  appendIf(line, typeIcon(item.type));
  if (item.id) {
    const idSpan = document.createElement('span');
    idSpan.className = 'nav-id mono';
    idSpan.textContent = item.id;
    line.appendChild(idSpan);
  }
  line.appendChild(navLineSpacer());
  // Agent chip (TASK-0164): a live session is touching this note.
  if (item.id && sessionTouchedIds.has(item.id)) {
    const chip = document.createElement('span');
    chip.className = 'nav-agent-chip';
    chip.textContent = 'agent';
    chip.title = 'A live agent session is working on this';
    line.appendChild(chip);
  }
  appendIf(line, statusChip(item.status));
  card.appendChild(line);

  if (item.title) {
    const titleEl = document.createElement('p');
    titleEl.className = 'nav-title';
    titleEl.textContent = item.title;
    titleEl.title = item.title;
    card.appendChild(titleEl);
  }
  if (item.subtitle) {
    const sub = document.createElement('p');
    sub.className = 'nav-subtitle';
    sub.textContent = item.subtitle;
    sub.title = item.subtitle;
    card.appendChild(sub);
  }

  if (rel) {
    card.addEventListener('click', (e) => {
      e.stopPropagation();
      void navigateTo(rel);
    });
  }
  li.appendChild(card);

  if (item.children && item.children.length) {
    const wrap = renderItemChildren(item);
    if (wrap) li.appendChild(wrap);
  }
  return li;
}

// ----- Stacked layout (Library mode pinned / rare types)

function navItemStacked(item: NavItem): HTMLLIElement {
  const li = document.createElement('li');
  const rel = extractRel(item.url);
  if (rel) li.dataset.rel = rel;
  if (item.id) li.dataset.id = String(item.id);
  if (item.type) li.dataset.type = String(item.type);
  if (item.status) li.dataset.status = String(item.status);

  const card = document.createElement('div');
  card.className = 'nav-item nav-item-stacked';

  const line = document.createElement('div');
  line.className = 'nav-line';
  appendIf(line, typeIcon(item.type));
  if (item.id) {
    const idSpan = document.createElement('span');
    idSpan.className = 'nav-id mono';
    idSpan.textContent = item.id;
    line.appendChild(idSpan);
  }
  line.appendChild(navLineSpacer());
  appendIf(line, statusChip(item.status));
  card.appendChild(line);

  if (item.title) {
    const titleEl = document.createElement('p');
    titleEl.className = 'nav-title-stacked';
    titleEl.textContent = item.title;
    titleEl.title = item.title;
    card.appendChild(titleEl);
  }
  if (item.subtitle) {
    const sub = document.createElement('p');
    sub.className = 'nav-subtitle-stacked mono';
    sub.textContent = item.subtitle;
    sub.title = item.subtitle;
    card.appendChild(sub);
  }

  if (rel) {
    card.addEventListener('click', (e) => { e.stopPropagation(); void navigateTo(rel); });
  }
  li.appendChild(card);
  return li;
}

// ----- Compact layout (Library Docs tree)

function navItemCompact(item: NavItem): HTMLLIElement {
  const li = document.createElement('li');
  const rel = extractRel(item.url);
  if (rel) li.dataset.rel = rel;
  if (item.id) li.dataset.id = String(item.id);
  if (item.type) li.dataset.type = String(item.type);
  if (item.status) li.dataset.status = String(item.status);

  const card = document.createElement('div');
  card.className = 'nav-item nav-item-compact' + (item.type ? ' has-type-icon' : '');
  appendIf(card, item.type ? typeIcon(item.type, 12) : null);
  const titleSpan = document.createElement('span');
  titleSpan.className = 'nav-title-compact';
  titleSpan.textContent = item.title || '';
  titleSpan.title = item.title || '';
  card.appendChild(titleSpan);

  if (rel) {
    card.addEventListener('click', (e) => { e.stopPropagation(); void navigateTo(rel); });
  }
  li.appendChild(card);
  return li;
}

// ----- Nested layout (requirements under features)

function navItemNested(item: NavItem): HTMLLIElement {
  const li = document.createElement('li');
  const rel = extractRel(item.url);
  if (rel) li.dataset.rel = rel;
  if (item.id) li.dataset.id = String(item.id);
  if (item.type) li.dataset.type = String(item.type);
  if (item.status) li.dataset.status = String(item.status);

  const card = document.createElement('div');
  card.className = 'nav-item nav-item-nested';

  const line = document.createElement('div');
  line.className = 'nav-line';
  appendIf(line, typeIcon(item.type, 12));
  if (item.id) {
    const idSpan = document.createElement('span');
    idSpan.className = 'nav-id mono';
    idSpan.textContent = item.id;
    line.appendChild(idSpan);
  }
  line.appendChild(navLineSpacer());
  appendIf(line, statusChip(item.status));
  card.appendChild(line);

  if (item.title) {
    const titleEl = document.createElement('p');
    titleEl.className = 'nav-title-nested';
    titleEl.textContent = item.title;
    titleEl.title = item.title;
    card.appendChild(titleEl);
  }

  if (rel) {
    card.addEventListener('click', (e) => { e.stopPropagation(); void navigateTo(rel); });
  }
  li.appendChild(card);
  return li;
}

function renderItemChildren(item: NavItem): HTMLDetailsElement | null {
  const kids = item.children || [];
  if (!kids.length) return null;
  const details = document.createElement('details');
  details.className = 'nav-item-children';
  const summary = document.createElement('summary');
  summary.className = 'nav-item-children-toggle';
  const chevron = document.createElement('span');
  chevron.className = 'nav-children-chevron';
  chevron.setAttribute('aria-hidden', 'true');
  summary.appendChild(chevron);
  const label = document.createElement('span');
  label.textContent = `${kids.length} requirement${kids.length === 1 ? '' : 's'}`;
  summary.appendChild(label);
  details.appendChild(summary);
  const list = document.createElement('ul');
  list.className = 'nav-item-children-list';
  for (const child of kids) list.appendChild(navItemNested(child));
  details.appendChild(list);
  return details;
}

// ----- Group + left-pane assembly

function renderNavGroup(group: NavGroupData, mode: NavMode): HTMLElement | null {
  // Apply hide-completed at the group level too: drop items + cascading
  // children that would all be filtered out.
  const visibleItems = (group.items || []).filter((it) => !isItemHidden(it));
  const visibleSubgroups: HTMLElement[] = [];
  for (const sub of group.subgroups || []) {
    const node = renderNavGroup(sub, mode);
    if (node) visibleSubgroups.push(node);
  }
  if (visibleItems.length === 0 && visibleSubgroups.length === 0) {
    // Whole group is empty after filtering — skip rendering entirely
    // so the user doesn't see ghost "Done" buckets when the filter
    // is on.
    if (hideCompleted) return null;
  }

  const details = document.createElement('details');
  const layoutClass = group.item_layout ? ` nav-group-${group.item_layout}` : '';
  details.className = `nav-group${layoutClass}`;
  (details as HTMLDetailsElement).open = group.default_open !== false;

  const summary = document.createElement('summary');
  summary.className = 'nav-group-header';
  const chevron = document.createElement('span');
  chevron.className = 'group-chevron';
  chevron.setAttribute('aria-hidden', 'true');
  summary.appendChild(chevron);
  const inner = document.createElement('span');
  inner.className = 'group-header-inner';
  appendIf(inner, groupIcon(mode, group));
  const labelSpan = document.createElement('span');
  labelSpan.textContent = group.label || group.key || '';
  inner.appendChild(labelSpan);
  summary.appendChild(inner);
  if (group.status) {
    const sp = document.createElement('span');
    sp.className = 'nav-group-spacer';
    summary.appendChild(sp);
    appendIf(summary, statusChip(group.status));
  }
  details.appendChild(summary);

  const body = document.createElement('div');
  body.className = 'group-body';
  const renderItem = pickItemRenderer(group.item_layout);
  const ul = document.createElement('ul');
  ul.className = 'nav-items';
  for (const item of visibleItems) ul.appendChild(renderItem(item));
  body.appendChild(ul);
  for (const sub of visibleSubgroups) body.appendChild(sub);
  details.appendChild(body);
  return details;
}

function extractRel(url: string | undefined): string | null {
  if (!url) return null;
  if (url.startsWith('/docs/')) return url.slice('/docs/'.length);
  return null;
}

// Initialise the in-workspace toolbar now that TYPE_ICONS / GROUP_ICONS
// are declared (avoids the temporal-dead-zone error that bit us once).
initNavToolbar();

// ----------------------------------------------------------------------
// Right pane (FEAT-0010 / TASK-0085)
// ----------------------------------------------------------------------

interface ContextItem {
  id?: string;
  title?: string;
  status?: string;
  url?: string;
  type?: string;
}

interface ContextGroup {
  type?: string;
  items?: ContextItem[];
}

interface ContextPayload {
  schema_version: number;
  platform: string;
  active?: { id?: string; title?: string; url?: string } | null;
  linked?: ContextGroup[];
  backlinks?: ContextGroup[];
}

const RIGHT_PANE_STORAGE_KEY = 'cockpit:right-pane-collapsed';

function loadStoredRightPane(): boolean {
  try {
    return localStorage.getItem(RIGHT_PANE_STORAGE_KEY) === '1';
  } catch {
    return false;
  }
}

function applyRightPaneState(collapsed: boolean, paint = true): void {
  appEl.classList.toggle('right-collapsed', collapsed);
  try { localStorage.setItem(RIGHT_PANE_STORAGE_KEY, collapsed ? '1' : '0'); }
  catch { /* ignore */ }
  // Sync the CSS variable so the top-bar's right zone tracks the
  // actual column width (collapsed = 28 px, otherwise the stored
  // splitter width).
  if (collapsed) {
    // Pane fully hidden; the top-bar-right's min-width keeps the
    // toggle button visible at the right edge of the toolbar.
    appEl.style.setProperty('--right-width', '0px');
  } else {
    const stored = loadStoredWidth('cockpit:right-width', 280);
    appEl.style.setProperty('--right-width', `${stored}px`);
  }
  if (paint) paintRightCollapse();
}

const LEFT_PANE_STORAGE_KEY = 'cockpit:left-collapsed';

function applyLeftPaneState(collapsed: boolean, paint = true): void {
  appEl.classList.toggle('left-collapsed', collapsed);
  try { localStorage.setItem(LEFT_PANE_STORAGE_KEY, collapsed ? '1' : '0'); }
  catch { /* ignore */ }
  if (collapsed) {
    appEl.style.setProperty('--nav-width', '0px');
  } else {
    const stored = loadStoredWidth('cockpit:nav-width', 240);
    appEl.style.setProperty('--nav-width', `${stored}px`);
  }
  if (paint) paintLeftCollapse();
}

function paintLeftCollapse(): void {
  const collapsed = appEl.classList.contains('left-collapsed');
  const paths = collapsed ? PANEL_LEFT_OPEN : PANEL_LEFT_CLOSE;
  leftPaneCollapseBtn.replaceChildren(makeSvg(paths, 16, { class: 'panel-left-icon' }));
  leftPaneCollapseBtn.title = collapsed ? 'Show navigator pane' : 'Hide navigator pane';
}

function paintRightCollapse(): void {
  const collapsed = appEl.classList.contains('right-collapsed');
  const paths = collapsed ? PANEL_RIGHT_OPEN : PANEL_RIGHT_CLOSE;
  rightPaneToggle.replaceChildren(makeSvg(paths, 16, { class: 'panel-right-icon' }));
  rightPaneToggle.title = collapsed ? 'Show context pane' : 'Hide context pane';
}

// Hydrate persisted state on launch (paint*Collapse repaint after
// TYPE_ICONS / PANEL_* are declared — those are below in source
// order, so the *_INITIAL paint happens inside initNavToolbar()).
applyRightPaneState(loadStoredRightPane(), /* paint */ false);

rightPaneToggle.addEventListener('click', () => {
  applyRightPaneState(!appEl.classList.contains('right-collapsed'));
});

// ----------------------------------------------------------------------
// Resizable splitters (FEAT-0009 / TASK-0096)
// ----------------------------------------------------------------------

const NAV_WIDTH_MIN = 180;
const NAV_WIDTH_MAX = 480;
const RIGHT_WIDTH_MIN = 200;
const RIGHT_WIDTH_MAX = 520;

function loadStoredWidth(key: string, fallback: number): number {
  try {
    const v = localStorage.getItem(key);
    if (v) {
      const n = parseInt(v, 10);
      if (Number.isFinite(n) && n > 0) return n;
    }
  } catch { /* ignore */ }
  return fallback;
}

function setNavWidth(px: number): void {
  const clamped = Math.max(NAV_WIDTH_MIN, Math.min(NAV_WIDTH_MAX, px));
  appEl.style.setProperty('--nav-width', `${clamped}px`);
  try { localStorage.setItem('cockpit:nav-width', String(clamped)); } catch { /* ignore */ }
}

function setRightWidth(px: number): void {
  const clamped = Math.max(RIGHT_WIDTH_MIN, Math.min(RIGHT_WIDTH_MAX, px));
  appEl.style.setProperty('--right-width', `${clamped}px`);
  try { localStorage.setItem('cockpit:right-width', String(clamped)); } catch { /* ignore */ }
}

// Apply persisted widths on launch.
setNavWidth(loadStoredWidth('cockpit:nav-width', 240));
setRightWidth(loadStoredWidth('cockpit:right-width', 280));

function attachSplitter(el: HTMLElement, axis: 'nav' | 'right'): void {
  el.addEventListener('mousedown', (downEv) => {
    downEv.preventDefault();
    el.classList.add('is-dragging');
    // Capture starting widths so the drag delta is stable even if the
    // cursor moves outside the splitter element during the drag.
    const navStart = parseInt(getComputedStyle(appEl).getPropertyValue('--nav-width'), 10) || 240;
    const rightStart = parseInt(getComputedStyle(appEl).getPropertyValue('--right-width'), 10) || 280;
    const startX = downEv.clientX;
    const onMove = (moveEv: MouseEvent): void => {
      const dx = moveEv.clientX - startX;
      if (axis === 'nav') setNavWidth(navStart + dx);
      else setRightWidth(rightStart - dx); // dragging RIGHT shrinks the right pane
    };
    const onUp = (): void => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      el.classList.remove('is-dragging');
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  });
}

attachSplitter($<HTMLDivElement>('#splitter-nav'), 'nav');
attachSplitter($<HTMLDivElement>('#splitter-right'), 'right');

async function loadRightPane(rel: string): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/context?this=${encodeURIComponent(rel)}`,
    );
    if (!resp.ok) {
      rightPaneContent.innerHTML = `<p class="meta">Context fetch failed: HTTP ${resp.status}</p>`;
      return;
    }
    const data = (await resp.json()) as ContextPayload;
    renderRightPane(data);
  } catch (err) {
    rightPaneContent.innerHTML = `<p class="meta">Context fetch failed: ${escapeHtml(String(err))}</p>`;
  }
}

// Stash the most recent payload so we can re-render when the hide-
// completed filter toggles without re-fetching.
let lastContextPayload: ContextPayload | null = null;

function renderRightPane(data: ContextPayload): void {
  lastContextPayload = data;
  const linked = data.linked || [];
  const backlinks = data.backlinks || [];
  rightPaneContent.innerHTML = '';
  const linkedNode = linked.length > 0 ? renderContextSection('Links from this note', linked) : null;
  const backlinksNode = backlinks.length > 0 ? renderContextSection('Backlinks', backlinks) : null;
  if (!linkedNode && !backlinksNode) {
    const msg = (linked.length === 0 && backlinks.length === 0)
      ? 'No links from or to this note.'
      : 'Everything linked here is completed (toggle the eye icon to show).';
    rightPaneContent.innerHTML = `<p class="meta">${msg}</p>`;
    return;
  }
  if (linkedNode) rightPaneContent.appendChild(linkedNode);
  if (backlinksNode) rightPaneContent.appendChild(backlinksNode);
}

function renderContextSection(heading: string, groups: ContextGroup[]): HTMLElement | null {
  const sectionChildren: HTMLElement[] = [];
  for (const group of groups) {
    const node = renderContextGroup(group);
    if (node) sectionChildren.push(node);
  }
  if (sectionChildren.length === 0) return null;
  const wrap = document.createElement('div');
  wrap.className = 'right-pane-section';
  const h = document.createElement('h3');
  h.textContent = heading;
  h.style.cssText = 'margin: 0 0 8px; font-size: 11px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: var(--text-faint);';
  wrap.appendChild(h);
  for (const node of sectionChildren) wrap.appendChild(node);
  return wrap;
}

function renderContextGroup(group: ContextGroup): HTMLElement | null {
  // FEAT-0014 / TASK-0099: right pane uses the same nav-item renderers
  // as the in-workspace nav. FEAT-0015: also obeys the hide-completed
  // filter so the right pane stays in sync with the left.
  const visible = (group.items || []).filter((it) => !isItemHidden(it));
  if (visible.length === 0 && hideCompleted) return null;
  const div = document.createElement('div');
  div.className = 'right-pane-group';
  const h = document.createElement('h3');
  h.textContent = pluralizeType(group.type) || '';
  div.appendChild(h);
  const ul = document.createElement('ul');
  ul.className = 'nav-items';
  for (const item of visible) {
    // Inject type from the group so type-icon renders even when the
    // server didn't echo it onto each item.
    const enriched: NavItem = { ...item, type: item.type || group.type };
    ul.appendChild(navItem(enriched));
  }
  div.appendChild(ul);
  return div;
}

function pluralizeType(t: string | undefined): string {
  if (!t) return '';
  // Mirror the cockpit's plural mapping (server.py INDEX_TYPE_PLURALS,
  // inverted).
  const map: Record<string, string> = {
    feature: 'Features', task: 'Tasks', requirement: 'Requirements',
    issue: 'Issues', risk: 'Risks', adr: 'Decisions', change: 'Changes',
    release: 'Releases', workflow: 'Workflows', test: 'Tests',
    phase: 'Phases', reference: 'References',
  };
  return map[t] || t.charAt(0).toUpperCase() + t.slice(1);
}

function refreshActiveNavRow(): void {
  // Drop any prior is-active, then add it to the row matching
  // `currentRel`. Stripping the fragment so #anchor nav doesn't
  // de-highlight the parent doc.
  const rel = currentRel ? stripFragment(currentRel) : null;
  wsNavContent.querySelectorAll<HTMLLIElement>('li.nav-item').forEach((li) => {
    li.classList.toggle('is-active', !!rel && li.dataset.rel === rel);
  });
}

// ----------------------------------------------------------------------
// Find in document (FEAT-0012 / TASK-0089)
// ----------------------------------------------------------------------

let findMarks: HTMLElement[] = [];
let findCurrentIndex = 0;

function clearFindMarks(): void {
  for (const mark of findMarks) {
    const parent = mark.parentNode;
    if (!parent) continue;
    while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
    parent.removeChild(mark);
    parent.normalize();
  }
  findMarks = [];
}

function runFind(query: string): void {
  clearFindMarks();
  findCurrentIndex = 0;
  if (!query) {
    findCount.textContent = '0 / 0';
    return;
  }
  const q = query.toLowerCase();
  // TreeWalker over docView's text nodes; skip empty / pure-whitespace.
  const walker = document.createTreeWalker(
    docView, NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        const text = node.nodeValue || '';
        if (!text || !text.toLowerCase().includes(q)) return NodeFilter.FILTER_REJECT;
        // Don't re-walk into an existing find-mark.
        let p: Node | null = node.parentNode;
        while (p && p !== docView) {
          if (p instanceof HTMLElement && p.classList.contains('find-match')) {
            return NodeFilter.FILTER_REJECT;
          }
          p = p.parentNode;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    },
  );
  const matches: Text[] = [];
  let n: Node | null;
  while ((n = walker.nextNode())) matches.push(n as Text);
  // Split + wrap each match. Iterate in reverse on each text node so
  // earlier matches don't invalidate the index of later ones inside the
  // same node.
  for (const textNode of matches) {
    const text = textNode.nodeValue || '';
    const lower = text.toLowerCase();
    const positions: number[] = [];
    let idx = lower.indexOf(q);
    while (idx >= 0) {
      positions.push(idx);
      idx = lower.indexOf(q, idx + q.length);
    }
    if (positions.length === 0) continue;
    // Walk positions backwards: splitText returns the trailing
    // fragment; we wrap the leading fragment of the trailing piece.
    let remaining = textNode;
    for (let i = positions.length - 1; i >= 0; i--) {
      const at = positions[i];
      const after = remaining.splitText(at + q.length);
      const matchNode = remaining.splitText(at);
      const mark = document.createElement('mark');
      mark.className = 'find-match';
      mark.textContent = matchNode.nodeValue || '';
      matchNode.parentNode?.replaceChild(mark, matchNode);
      findMarks.unshift(mark);
      // `after` becomes our `remaining` for the previous (earlier)
      // match within this same text node — but only `remaining` (the
      // surviving prefix) needs further splitting. We continue with
      // `remaining` which is now the prefix before this match.
      void after; // suppress unused-var
    }
  }
  if (findMarks.length === 0) {
    findCount.textContent = '0 / 0';
    return;
  }
  setFindCurrent(0);
}

function setFindCurrent(idx: number): void {
  for (const mark of findMarks) mark.classList.remove('is-current');
  findCurrentIndex = ((idx % findMarks.length) + findMarks.length) % findMarks.length;
  const cur = findMarks[findCurrentIndex];
  cur.classList.add('is-current');
  cur.scrollIntoView({ block: 'center', behavior: 'smooth' });
  findCount.textContent = `${findCurrentIndex + 1} / ${findMarks.length}`;
}

function openFindBar(): void {
  findBar.hidden = false;
  findInput.value = '';
  clearFindMarks();
  findCount.textContent = '0 / 0';
  findInput.focus();
}

function closeFindBar(): void {
  clearFindMarks();
  findBar.hidden = true;
  findInput.value = '';
}

findInput.addEventListener('input', () => {
  runFind(findInput.value.trim());
});

findInput.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { e.preventDefault(); closeFindBar(); }
  else if (e.key === 'Enter') {
    e.preventDefault();
    if (findMarks.length > 0) {
      setFindCurrent(findCurrentIndex + (e.shiftKey ? -1 : 1));
    }
  }
});
findPrevBtn.addEventListener('click', () => {
  if (findMarks.length > 0) setFindCurrent(findCurrentIndex - 1);
});
findNextBtn.addEventListener('click', () => {
  if (findMarks.length > 0) setFindCurrent(findCurrentIndex + 1);
});
findCloseBtn.addEventListener('click', closeFindBar);

// Global ⌘F / Ctrl+F opens. Clears stale marks when the centre
// doc is re-mounted via navigateTo (already calls clearFindMarks
// implicitly via the DOM replacement, but we belt-and-brace below).
document.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'f') {
    e.preventDefault();
    if (findBar.hidden) openFindBar();
    else closeFindBar();
  }
});

// ----------------------------------------------------------------------
// Native context menus (FEAT-0012 / TASK-0090)
// ----------------------------------------------------------------------

listEl.addEventListener('contextmenu', (e) => {
  const target = e.target as HTMLElement | null;
  const li = target?.closest('li.ws-square[data-id]') as HTMLLIElement | null;
  if (!li || !li.dataset.id) return;
  e.preventDefault();
  const ws = workspaces.find((w) => w.id === li.dataset.id);
  if (!ws) return;
  void cockpitApi.app.showContextMenu('rail', {
    workspaceId: ws.id,
    root: ws.root,
  });
});

// Shared row context menu: nav rows AND the right pane's linked /
// backlinks cards use the same nav-item markup, so both get the same
// menu (Open / Copy ID / Copy path / Reveal / Agent verbs).
function navRowContextMenu(e: MouseEvent): void {
  const target = e.target as HTMLElement | null;
  // The `nav-item` class is on the inner card div, not the <li> —
  // the li carries the data attributes (ISS-0005).
  const li = target?.closest('li[data-rel]') as HTMLLIElement | null;
  if (!li || !li.dataset.rel) return;
  e.preventDefault();
  const rel = li.dataset.rel;
  const id = li.querySelector('.nav-id')?.textContent || '';
  const activeWs = workspaces.find((w) => w.id === activeId);
  void cockpitApi.app.showContextMenu('nav-row', {
    id, rel,
    workspaceId: activeId || '',
    root: activeWs?.root || '',
    verbs: verbsForId(id, { type: li.dataset.type, status: li.dataset.status })
      .map((v) => ({ key: v.key, label: v.label })),
    currentAgent: loadDispatchAgent(),
  });
}

wsNavContent.addEventListener('contextmenu', navRowContextMenu);
rightPaneContent.addEventListener('contextmenu', navRowContextMenu);

docView.addEventListener('contextmenu', (e) => {
  const target = e.target as HTMLElement | null;
  const anchor = target?.closest('a') as HTMLAnchorElement | null;
  if (!anchor) return;
  const href = anchor.getAttribute('href') || '';
  const cls = classifyLink(href);
  if (cls.kind !== 'docs') return;
  e.preventDefault();
  const activeWs = workspaces.find((w) => w.id === activeId);
  const linkId = (anchor.textContent || '').match(/^((TASK|ISS|FEAT|REQ|PHASE|RISK)-\d+)/i)?.[1]?.toUpperCase()
    || (cls.rel.split('/').pop() || '').match(/^((TASK|ISS|FEAT|REQ|PHASE|RISK)-\d+)/i)?.[1]?.toUpperCase()
    || '';
  void cockpitApi.app.showContextMenu('doc-link', {
    id: linkId,
    rel: cls.rel,
    url: anchor.href || href,
    workspaceId: activeId || '',
    root: activeWs?.root || '',
    verbs: linkId ? verbsForId(linkId).map((v) => ({ key: v.key, label: v.label })) : [],
    currentAgent: loadDispatchAgent(),
  });
});

// ----------------------------------------------------------------------
// Drag-and-drop note (FEAT-0012 / TASK-0091)
// ----------------------------------------------------------------------

const dragOverlay = document.createElement('div');
dragOverlay.className = 'drop-overlay';
dragOverlay.hidden = true;
dragOverlay.textContent = 'Drop a .md note to navigate';
document.body.appendChild(dragOverlay);

let dragEnterDepth = 0;

document.addEventListener('dragenter', (e) => {
  if (e.dataTransfer && Array.from(e.dataTransfer.items).some((i) => i.kind === 'file')) {
    dragEnterDepth += 1;
    dragOverlay.hidden = false;
  }
});

document.addEventListener('dragleave', () => {
  dragEnterDepth -= 1;
  if (dragEnterDepth <= 0) {
    dragEnterDepth = 0;
    dragOverlay.hidden = true;
  }
});

document.addEventListener('dragover', (e) => {
  // Required to let the browser fire `drop`.
  if (e.dataTransfer?.items && Array.from(e.dataTransfer.items).some((i) => i.kind === 'file')) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  }
});

document.addEventListener('drop', async (e) => {
  dragEnterDepth = 0;
  dragOverlay.hidden = true;
  if (!e.dataTransfer || e.dataTransfer.files.length === 0) return;
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  // Electron exposes the absolute path on File objects in the
  // renderer; `path` is a non-standard property added by Electron.
  const absPath = (file as File & { path?: string }).path;
  if (!absPath) return;
  const result = await cockpitApi.app.resolveDroppedFile(absPath);
  switch (result.action) {
    case 'navigate': {
      if (result.workspaceId && result.workspaceId !== activeId) {
        await openWorkspace(result.workspaceId);
      }
      if (result.rel) void navigateTo(result.rel);
      break;
    }
    case 'offer-add-workspace': {
      showStatus(`That file is in ${result.root} — add it as a workspace? (Use Rescan to discover.)`);
      scheduleHide(4000);
      break;
    }
    case 'ignored':
    default: {
      showStatus(`Not a project-os note (${result.reason ?? 'unknown'}).`, 'error');
      scheduleHide(2500);
      break;
    }
  }
});

// ----------------------------------------------------------------------
// Status footer (FEAT-0009 / TASK-0094 + 0095)
// ----------------------------------------------------------------------

type SidecarStatus = 'idle' | 'spawning' | 'ready' | 'failed' | 'exited';

function setSidecarStatus(state: SidecarStatus, label?: string): void {
  sfSidecar.dataset.state = state;
  const text = label || `sidecar: ${state}`;
  sfSidecar.querySelector('.sf-label')!.textContent = text;
}

function refreshFooterPath(): void {
  sfPath.textContent = currentRel ? currentRel : '';
}

// The footer no longer carries an agent dot (FEAT-0031 / TASK-0148):
// agent state already reads from the rail dots, the agent strip, and
// the attention panel — one surface per scope. The footer keeps only
// sidecar-process health (#sf-sidecar). This shim keeps the former
// call sites cheap no-ops.
function refreshFooterAgent(): void { /* removed — see TASK-0148 */ }

sfPath.addEventListener('click', () => {
  if (!sfPath.textContent) return;
  void navigator.clipboard?.writeText(sfPath.textContent);
  const orig = sfPath.textContent;
  sfPath.textContent = 'copied';
  setTimeout(() => { sfPath.textContent = orig; refreshFooterPath(); }, 800);
});

document.querySelectorAll<HTMLButtonElement>('.sf-theme-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    const v = btn.dataset.theme as ThemePref | undefined;
    if (v === 'system' || v === 'light' || v === 'dark') setThemePref(v);
  });
});
refreshThemeButtons();

cockpitApi.app.onMenuDispatch((ev) => {
  switch (ev.action) {
    case 'navigate': {
      const rel = ev.rel as string | undefined;
      if (rel) void navigateTo(rel);
      break;
    }
    case 'switch-workspace': {
      const id = ev.workspaceId as string | undefined;
      if (id) void openWorkspace(id);
      break;
    }
    case 'agent-dispatch': {
      const id = (ev.id as string | undefined) || '';
      const rel = (ev.rel as string | undefined) || '';
      const verb = (ev.verb as string | undefined) || undefined;
      const wsId = (ev.workspaceId as string | undefined) || undefined;
      const agent = ev.agent === 'codex' ? 'codex' as const
        : ev.agent === 'claude' ? 'claude' as const : undefined;
      if (id || rel) void dispatchToAgent(id, rel, agent, verb, wsId);
      break;
    }
    case 'agent-set': {
      const agent = ev.agent === 'codex' ? 'codex' as const : 'claude' as const;
      saveDispatchAgent(agent);
      showStatus(`Dispatch agent: ${agent}`);
      break;
    }
  }
});

// ----------------------------------------------------------------------
// Quick-switch palette (FEAT-0012 / TASK-0088)
// ----------------------------------------------------------------------

interface QuickItem { id: string; title: string; rel: string; type: string; }

let quickCorpus: QuickItem[] = [];
let quickResults: QuickItem[] = [];
let quickSelectedIndex = 0;
// Verb mode (FEAT-0026 / TASK-0138): "refine TASK-0115" — a leading
// verb token filters to items whose type carries that verb and Enter
// dispatches instead of navigating.
let quickVerb: { key: string; label: string; types: string[] } | null = null;

function parseQuickVerb(query: string): { verb: typeof quickVerb; rest: string } {
  const m = query.match(/^(\S+)\s+(.*)$/);
  if (!m) return { verb: null, rest: query };
  const token = m[1].toLowerCase();
  const types: string[] = [];
  let label = '';
  let key = '';
  for (const [t, verbs] of Object.entries(agentActions)) {
    for (const v of verbs) {
      if (v.key.toLowerCase() === token || v.label.toLowerCase() === token) {
        types.push(t);
        key = v.key;
        label = v.label;
      }
    }
  }
  if (types.length === 0) return { verb: null, rest: query };
  return { verb: { key, label, types }, rest: m[2] };
}

function flattenNavItems(groups: NavGroupData[] | undefined, out: QuickItem[]): void {
  if (!groups) return;
  for (const group of groups) {
    for (const item of group.items || []) {
      const rel = extractRel(item.url) || '';
      if (rel) {
        // Items without an id (Docs-tree entries, references, plain
        // .md files) are still navigable — keep them in the corpus
        // so pasting a rel-path matches.
        out.push({
          id: item.id || rel,
          title: item.title || item.id || rel,
          rel,
          type: item.type || group.key || '',
        });
      }
      if (item.children) flattenNavItems([{ items: item.children }], out);
    }
    // Library mode (and any future grouped mode) nests deeply via
    // subgroups; walk those too so the corpus matches the whole tree.
    if (group.subgroups) flattenNavItems(group.subgroups, out);
  }
}

async function buildQuickCorpus(): Promise<void> {
  if (!sidecarBaseUrl) return;
  // Library mode is the broadest single fetch — every canonical type
  // (features, tasks, issues, requirements, ADRs, changes, refs)
  // plus rare items. Good-enough v1; no need to aggregate multi-mode.
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/nav?mode=library`);
    if (!resp.ok) return;
    const data = (await resp.json()) as NavPayload;
    const out: QuickItem[] = [];
    flattenNavItems(data.groups, out);
    // Some library groupings duplicate the same note (pinned + by-type);
    // dedupe by rel-path.
    const seen = new Set<string>();
    quickCorpus = out.filter((it) => seen.has(it.rel) ? false : (seen.add(it.rel), true));
  } catch {
    /* leave previous corpus in place on transient failures */
  }
}

function fuzzyScore(item: QuickItem, query: string): number {
  if (!query) return 1;
  const q = query.toLowerCase();
  const id = item.id.toLowerCase();
  const title = item.title.toLowerCase();
  const rel = item.rel.toLowerCase();
  if (id === q) return 1000;
  if (id.startsWith(q)) return 500;
  if (id.includes(q)) return 200;
  if (title.startsWith(q)) return 300;
  if (title.includes(q)) return 100;
  if (rel.includes(q)) return 50;
  return 0;
}

function refreshQuickResults(): void {
  const query = quickSwitchInput.value.trim();
  const parsed = parseQuickVerb(query);
  quickVerb = parsed.verb;
  const effectiveQuery = quickVerb ? parsed.rest : query;
  const pool = quickVerb
    ? quickCorpus.filter((it) => quickVerb!.types.includes((it.type || '').toLowerCase()))
    : quickCorpus;
  const scored = pool
    .map((it) => ({ it, score: fuzzyScore(it, effectiveQuery) }))
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 30);
  quickResults = scored.map((s) => s.it);
  quickSelectedIndex = 0;
  renderQuickResults();
}

function renderQuickResults(): void {
  quickSwitchResults.innerHTML = '';
  if (quickResults.length === 0) {
    const li = document.createElement('li');
    li.className = 'qs-empty';
    li.textContent = quickCorpus.length === 0
      ? '(corpus empty — pick a workspace first)'
      : 'No matches.';
    quickSwitchResults.appendChild(li);
    return;
  }
  quickResults.forEach((item, idx) => {
    const li = document.createElement('li');
    if (idx === quickSelectedIndex) li.classList.add('is-selected');
    if (quickVerb) {
      li.classList.add('is-action');
      const badge = document.createElement('span');
      badge.className = 'qs-action-badge';
      badge.textContent = `▶ ${quickVerb.label}`;
      li.prepend(badge);
    }
    const line1 = document.createElement('div');
    line1.className = 'qs-line-1';
    const idSpan = document.createElement('span');
    idSpan.className = 'qs-id';
    idSpan.textContent = item.id;
    line1.appendChild(idSpan);
    const titleSpan = document.createElement('span');
    titleSpan.className = 'qs-title';
    titleSpan.textContent = item.title;
    line1.appendChild(titleSpan);
    li.appendChild(line1);
    const path = document.createElement('div');
    path.className = 'qs-path';
    path.textContent = item.rel;
    li.appendChild(path);
    li.addEventListener('click', () => { quickSelectedIndex = idx; acceptQuickSwitch(); });
    li.addEventListener('mouseenter', () => {
      // TASK-0105: do NOT re-render the list here — that destroys
      // every <li> and breaks the click event (browsers only fire
      // 'click' when mousedown and mouseup hit the same node).
      // Toggle the highlight class in place instead.
      quickSelectedIndex = idx;
      quickSwitchResults.querySelectorAll<HTMLLIElement>('li').forEach((node, j) => {
        node.classList.toggle('is-selected', j === idx);
      });
    });
    quickSwitchResults.appendChild(li);
  });
}

function openQuickSwitch(): void {
  void buildQuickCorpus().then(() => {
    quickSwitchEl.hidden = false;
    quickSwitchInput.value = '';
    refreshQuickResults();
    quickSwitchInput.focus();
  });
}

function closeQuickSwitch(): void {
  quickSwitchEl.hidden = true;
}

function acceptQuickSwitch(): void {
  const item = quickResults[quickSelectedIndex];
  if (!item) return;
  const verb = quickVerb;
  closeQuickSwitch();
  if (verb && item.id) {
    void dispatchToAgent(item.id, item.rel, undefined, verb.key);
    return;
  }
  void navigateTo(item.rel);
}

quickSwitchInput.addEventListener('input', refreshQuickResults);
quickSwitchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { e.preventDefault(); closeQuickSwitch(); }
  else if (e.key === 'Enter') { e.preventDefault(); acceptQuickSwitch(); }
  else if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (!quickResults.length) return;
    quickSelectedIndex = (quickSelectedIndex + 1) % quickResults.length;
    renderQuickResults();
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    if (!quickResults.length) return;
    quickSelectedIndex = (quickSelectedIndex - 1 + quickResults.length) % quickResults.length;
    renderQuickResults();
  }
});
quickSwitchEl.addEventListener('click', (e) => {
  if (e.target === quickSwitchEl) closeQuickSwitch();
});
document.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'p') {
    e.preventDefault();
    if (quickSwitchEl.hidden) openQuickSwitch();
    else closeQuickSwitch();
  }
});

// ----------------------------------------------------------------------
// SSE soft-reload + tab-state heartbeat (FEAT-0010 / TASK-0086)
// ----------------------------------------------------------------------

let activeEventSource: EventSource | null = null;
let softReloadTimer: number | null = null;
let heartbeatTimer: number | null = null;
let tabId: string | null = null;

function getTabId(): string {
  if (tabId) return tabId;
  try {
    const stored = localStorage.getItem('cockpit:tab-id');
    if (stored) { tabId = stored; return stored; }
  } catch { /* ignore */ }
  // RFC4122-ish — sufficient for tab identity, not a security primitive.
  const generated = 'desktop-' + Math.random().toString(36).slice(2, 12) +
                    '-' + Date.now().toString(36);
  tabId = generated;
  try { localStorage.setItem('cockpit:tab-id', generated); } catch { /* ignore */ }
  return generated;
}

function attachSidecarEventStream(baseUrl: string): void {
  if (activeEventSource) {
    activeEventSource.close();
    activeEventSource = null;
  }
  // EventSource is the browser-standard SSE consumer. Available in
  // Electron renderers without any extra polyfill.
  const es = new EventSource(`${baseUrl}/_events`);
  es.addEventListener('file-changed', () => {
    scheduleSoftReload();
  });
  // Status transitions (FEAT-0036 / TASK-0162): live-migrate rows in the
  // Active nav mode and flash the changed item.
  es.addEventListener('cockpit:status-change', (e) => {
    try {
      const c = JSON.parse((e as MessageEvent).data) as { id?: string; to?: string };
      handleStatusChange(c);
    } catch { /* malformed — ignore */ }
  });
  // Hook-fed activity feed (FEAT-0019/0020): live strip + nav trail.
  es.addEventListener('cockpit:agent-activity', (e) => {
    try {
      handleAgentActivity(JSON.parse((e as MessageEvent).data) as AgentActivity);
    } catch { /* malformed activity event — ignore */ }
  });
  // Instant agent-state for the ACTIVE workspace (the cross-workspace
  // poller still covers the rest of the rail at 5s cadence).
  es.addEventListener('cockpit:agent-state', (e) => {
    try {
      const payload = JSON.parse((e as MessageEvent).data) as AgentStatePayload;
      if (activeId) {
        noteFinish(activeId, agentStates.get(activeId)?.state, payload);
        agentStates.set(activeId, payload);
        const li = listEl.querySelector<HTMLLIElement>(`li[data-id="${activeId}"]`);
        const ws = workspaces.find((w) => w.id === activeId);
        if (li && ws) applyAgentStateToSquare(li, ws);
        refreshFooterAgent();
        refreshAttention();
        void refreshAgentSnapshot();
        scheduleAck();  // seen-timer for the active workspace (TASK-0157)
        if (payload.state) cockpitApi.dispatch.poke(activeId, payload.state);
      }
    } catch { /* ignore */ }
  });
  // CLI `cockpit dispatch` requests (FEAT-0025 / TASK-0136).
  es.addEventListener('cockpit:dispatch-request', (e) => {
    try {
      handleDispatchRequest(JSON.parse((e as MessageEvent).data));
    } catch { /* ignore malformed */ }
  });
  // `cockpit:focus` stays on the main process's agent-focus bridge.
  es.onerror = () => {
    // EventSource auto-reconnects; nothing to do here. Closing the
    // stream on every transient error would loop.
  };
  activeEventSource = es;
}

function scheduleSoftReload(): void {
  if (softReloadTimer != null) window.clearTimeout(softReloadTimer);
  softReloadTimer = window.setTimeout(() => {
    softReloadTimer = null;
    // Re-fetch nav + right pane + centre. Centre uses {replace: true}
    // so the file-changed reload doesn't pollute history with a copy
    // of the same path.
    if (sidecarBaseUrl) {
      if (currentRel && currentRel.startsWith('~overview')) {
        // Overview refreshes in place — scroll survives, no history
        // churn, and the server-side stats cache makes it cheap
        // (FEAT-0023 / TASK-0130).
        void refreshOverviewInPlace();
        return;
      }
      void loadWsNav();
      if (currentRel && !currentRel.startsWith('~')) {
        void loadRightPane(currentRel);
        void navigateTo(currentRel, { replace: true });
      }
    }
  }, 150);
}

function startTabStateHeartbeat(): void {
  if (heartbeatTimer != null) window.clearInterval(heartbeatTimer);
  // Fire once immediately so the cockpit's state snapshot reflects
  // this tab right away.
  sendTabState();
  heartbeatTimer = window.setInterval(sendTabState, 15_000);
}

async function sendTabState(): Promise<void> {
  if (!sidecarBaseUrl || !currentRel) return;
  if (currentRel.startsWith('~')) return; // virtual pages have no docs URL
  const url = `/docs/${stripFragment(currentRel)}`;
  try {
    await fetch(`${sidecarBaseUrl}/api/cockpit/tab-state`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tab_id: getTabId(),
        url,
        following: isFollowing(activeId),
      }),
    });
  } catch {
    /* heartbeat is best-effort */
  }
}

// ----------------------------------------------------------------------
// Agent instrumentation surfaces (PHASE-007)
//   FEAT-0020: activity strip, needs-input inbox, live nav trail
//   FEAT-0021: task dispatch
//   FEAT-0022: session insight (overview section + CHG provenance)
// ----------------------------------------------------------------------

interface AgentActivity {
  event: string;
  session_id: string;
  agent: string;
  ts: string;
  state?: string;
  prompt?: string;
  tool?: string;
  file?: string;
  rel?: string;
  undocumented?: boolean;
  cost?: AgentCostSnapshot;
}

interface AgentCostSnapshot {
  total_cost_usd?: number;
  total_lines_added?: number;
  total_lines_removed?: number;
  used_percentage?: number;
  rate_limits?: Record<string, { used_percentage: number; resets_at?: string }>;
  captured_at?: string;
}

interface AgentSessionSlim {
  session_id: string;
  agent: string | null;
  started: string | null;
  ended: string | null;
  live: boolean;
  prompt_count: number;
  last_prompt: string | null;
  files: string[];
  docs_notes: string[];
  work_notes?: string[];
  cost: AgentCostSnapshot | null;
  chg_ids: string[];
  undocumented: boolean;
  transcript_path?: string | null;
  prompts?: { ts: string; text: string }[];
}

const agentStrip = $<HTMLDivElement>('#agent-strip');
const agentStripDot = $<HTMLSpanElement>('#agent-strip-dot');
const agentStripAgent = $<HTMLSpanElement>('#agent-strip-agent');
const agentStripText = $<HTMLSpanElement>('#agent-strip-text');
const agentStripUndoc = $<HTMLSpanElement>('#agent-strip-undoc');
const agentStripCtx = $<HTMLSpanElement>('#agent-strip-ctx');
const agentStripCost = $<HTMLSpanElement>('#agent-strip-cost');
const agentStripExpand = $<HTMLButtonElement>('#agent-strip-expand');
const agentStripDetail = $<HTMLDivElement>('#agent-strip-detail');
const attentionPanel = $<HTMLDivElement>('#ws-attention');

let stripSession: AgentSessionSlim | null = null;
let stripLastPrompt = '';

// ----- Activity strip (TASK-0118) -------------------------------------

function agentStateLabel(state: string | undefined): string {
  switch (state) {
    case 'busy': return 'working';
    case 'needs-input': return 'needs you';
    case 'waiting': return 'waiting for you';
    case 'idle': return 'idle';
    case 'done': return 'done';
    case 'error': return 'error';
    default: return state || '';
  }
}

function renderAgentStripCost(cost: AgentCostSnapshot | null | undefined): void {
  if (cost && typeof cost.used_percentage === 'number') {
    agentStripCtx.textContent = `ctx ${Math.round(cost.used_percentage)}%`;
    agentStripCtx.hidden = false;
    agentStripCtx.classList.toggle('meter-hot', cost.used_percentage >= 80);
  } else {
    agentStripCtx.hidden = true;
  }
  // Rate-limit budgets moved out of the session strip to the account
  // budget block in the left pane (FEAT-0035/TASK-0160) — the strip is
  // session-scoped only. Capture the freshest sample for that block.
  if (cost?.rate_limits) noteRateLimits(cost.rate_limits, cost.captured_at);
  if (cost && typeof cost.total_cost_usd === 'number') {
    agentStripCost.textContent = `$${cost.total_cost_usd.toFixed(2)}`;
    agentStripCost.hidden = false;
  } else {
    agentStripCost.hidden = true;
  }
}

function showAgentStrip(activity: AgentActivity | null, session: AgentSessionSlim | null): void {
  stripSession = session;
  // `session` may be live (session.live) or the most-recent ended one
  // (the snapshot's last_session fallback) so the files view persists
  // between runs. Only truly hide when there's no session to show and
  // nothing queued.
  if (!session) {
    // Keep the strip up while dispatches are queued — the chip is the
    // only visible handle on the queue (FEAT-0024 / TASK-0133).
    agentStrip.hidden = activeQueueItems.length === 0;
    agentStripDetail.hidden = true;
    agentStripExpand.setAttribute('aria-expanded', 'false');
    return;
  }
  const live = session.live;
  agentStrip.hidden = false;
  agentStrip.classList.toggle('is-ended', !live);
  const state = live
    ? (activity?.state || agentStates.get(activeId || '')?.state || 'busy')
    : 'idle';
  agentStripDot.dataset.state = state;
  // Prefer the live hook agent over a stale last_session agent so the
  // strip and rail dot never disagree (ISS-0012) — a one-off codex run
  // must not relabel a live claude workspace.
  agentStripAgent.textContent =
    activity?.agent || agentStates.get(activeId || '')?.agent || session.agent || 'agent';
  if (live && activity?.prompt) stripLastPrompt = activity.prompt;
  else if (session.last_prompt) stripLastPrompt = session.last_prompt;
  let detail = '';
  if (live && activity?.tool && activity?.file) {
    const short = (activity.rel || activity.file).split('/').pop() || activity.file;
    detail = `${activity.tool} · ${short}`;
  } else if (live && activity?.tool) {
    detail = activity.tool;
  }
  const label = live ? agentStateLabel(state) : 'last session';
  agentStripText.textContent = detail
    ? `${label} — ${detail}`
    : stripLastPrompt
      ? `${label} — ${stripLastPrompt}`
      : label;
  agentStripText.title = stripLastPrompt;
  agentStripUndoc.hidden = !((live && activity?.undocumented) || session.undocumented);
  renderAgentStripCost(session.cost || (live ? activity?.cost : undefined));
}

// Session "work" tab (TASK-0163): status boxes per docs note this
// session touched, filled live as the agent closes them.
const DONE_STATUSES = new Set(['done', 'merged', 'fixed', 'fulfilled', 'met', 'complete', 'verified', 'closed', 'passing', 'published', 'resolved']);
const workTransitions = new Map<string, string>();  // id -> latest status seen
let stripDetailTab: 'work' | 'files' = 'work';

function noteWorkTransition(c: { id?: string; to?: string }): void {
  if (c.id && typeof c.to === 'string') workTransitions.set(c.id, c.to);
  if (!agentStripDetail.hidden && stripDetailTab === 'work') renderAgentStripDetail();
}

function sessionWorkIds(): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  for (const n of stripSession?.work_notes ?? stripSession?.docs_notes ?? []) {
    const m = String(n).match(ID_RE);
    if (m && !seen.has(m[1])) { seen.add(m[1]); out.push(m[1]); }
  }
  return out;
}

function renderAgentStripDetail(): void {
  if (!stripSession) { agentStripDetail.hidden = true; return; }
  agentStripDetail.replaceChildren();
  const head = document.createElement('div');
  head.className = 'agent-detail-head';
  head.textContent = `session ${stripSession.session_id.slice(0, 8)} · ${stripSession.prompt_count} prompt${stripSession.prompt_count === 1 ? '' : 's'}`;
  agentStripDetail.appendChild(head);

  const workIds = sessionWorkIds();
  // Tab bar: work | files.
  const tabs = document.createElement('div');
  tabs.className = 'agent-detail-tabs';
  for (const [key, label] of [['work', 'work'], ['files', 'files']] as const) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'agent-detail-tab' + (stripDetailTab === key ? ' on' : '');
    b.textContent = label;
    b.addEventListener('click', () => { stripDetailTab = key; renderAgentStripDetail(); });
    tabs.appendChild(b);
  }
  agentStripDetail.appendChild(tabs);

  if (stripDetailTab === 'work') {
    const list = document.createElement('div');
    list.className = 'agent-detail-work';
    if (workIds.length === 0) {
      const e = document.createElement('div');
      e.className = 'agent-detail-empty';
      e.textContent = 'No documented work yet.';
      list.appendChild(e);
    }
    for (const id of workIds) {
      const status = workTransitions.get(id);
      const st = (status || '').toLowerCase();
      // A note the session is touching is "doing" until it goes done.
      const tier = DONE_STATUSES.has(st) ? 'done' : 'doing';
      const row = document.createElement('button');
      row.type = 'button';
      row.className = 'agent-detail-work-row';
      const box = document.createElement('span');
      box.className = 'work-box' + (tier ? ` ${tier}` : '');
      const idEl = document.createElement('span');
      idEl.className = 'work-id mono';
      idEl.textContent = id;
      row.append(box, idEl);
      if (status) {
        const stEl = document.createElement('span');
        stEl.className = 'work-status';
        stEl.textContent = status;
        row.appendChild(stEl);
      }
      row.addEventListener('click', () => {
        const notes = stripSession?.work_notes ?? stripSession?.docs_notes ?? [];
        const rel = notes.find((n) => String(n).includes(id));
        if (rel) void navigateTo(rel);
      });
      list.appendChild(row);
    }
    agentStripDetail.appendChild(list);
  } else {
    const list = document.createElement('ul');
    list.className = 'agent-detail-files';
    const files = stripSession.files.slice(-20).reverse();
    if (files.length === 0) {
      const li = document.createElement('li');
      li.className = 'agent-detail-empty';
      li.textContent = 'No files touched yet.';
      list.appendChild(li);
    }
    for (const f of files) {
      const li = document.createElement('li');
      const isDocs = !f.startsWith('/');
      if (isDocs) {
        const a = document.createElement('a');
        a.href = '#';
        a.textContent = f;
        a.addEventListener('click', (e) => { e.preventDefault(); void navigateTo(f); });
        li.appendChild(a);
      } else {
        li.textContent = f;
      }
      list.appendChild(li);
    }
    agentStripDetail.appendChild(list);
  }
  agentStripDetail.hidden = false;
}

// One shared fetch per hook-event burst feeds every agent surface —
// strip, Now card, sessions feed (TASK-0130 fix: was three fetches).
interface AgentSnap {
  activity?: AgentActivity | null;
  session?: AgentSessionSlim | null;
  last_session?: AgentSessionSlim | null;
  agent_state?: { state?: string } | null;
  // Freshest account-global usage across all sessions (TASK-0171).
  rate_limits?: Record<string, { used_percentage: number; resets_at?: string }>;
  rate_limits_at?: string;
}
let lastAgentSnap: AgentSnap | null = null;
let agentSnapTimer: number | null = null;

async function refreshAgentSnapshot(): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/state`);
    if (!resp.ok) return;
    lastAgentSnap = await resp.json() as AgentSnap;
    // Account-global usage: adopt the freshest reading across all of
    // this workspace's sessions (TASK-0171), through the adopt-if-newer
    // gate — so the real reading isn't masked by a later session that
    // lacked one.
    if (lastAgentSnap.rate_limits && lastAgentSnap.rate_limits_at) {
      noteRateLimits(lastAgentSnap.rate_limits, lastAgentSnap.rate_limits_at);
    }
    refreshSessionTouched();
    // Fall back to the most-recent (ended) session so the strip — and
    // its files view — persists between runs instead of vanishing.
    showAgentStrip(
      lastAgentSnap.activity ?? null,
      lastAgentSnap.session ?? lastAgentSnap.last_session ?? null,
    );
    if (!agentStripDetail.hidden) renderAgentStripDetail();
  } catch { /* agent surfaces are best-effort */ }
}

function scheduleAgentSnapshotRefresh(): void {
  if (agentSnapTimer != null) window.clearTimeout(agentSnapTimer);
  agentSnapTimer = window.setTimeout(() => {
    agentSnapTimer = null;
    void refreshAgentSnapshot();
  }, 300);
}

function handleAgentActivity(activity: AgentActivity): void {
  scheduleAgentSnapshotRefresh();
  if (activity.rel) flashAgentTouch(activity.rel);
}

// ----- Live nav trail (TASK-0120) --------------------------------------

const AGENT_TOUCH_DECAY_MS = 8_000;

function flashAgentTouch(rel: string): void {
  const roots: ParentNode[] = [wsNavContent, rightPaneContent];
  for (const root of roots) {
    root.querySelectorAll<HTMLElement>('li[data-rel]').forEach((li) => {
      if (li.dataset.rel !== rel) return;
      li.classList.add('agent-touched');
      const existing = li.querySelector('.agent-touched-chip');
      if (!existing) {
        const chip = document.createElement('span');
        chip.className = 'agent-touched-chip';
        chip.textContent = 'agent';
        li.appendChild(chip);
      }
      window.setTimeout(() => {
        li.classList.remove('agent-touched');
        li.querySelector('.agent-touched-chip')?.remove();
      }, AGENT_TOUCH_DECAY_MS);
    });
  }
}

// ----- Agent attention panel (FEAT-0030 / TASK-0147) -------------------
// Docked at the bottom of the nav pane. Answers "what needs me?" across
// all workspaces: needs-input (act now) then waiting (turn finished,
// review) rows, plus a one-line finished-today tally. Replaces the old
// top-bar bell + popover. Zero-height (hidden) when there's nothing.

interface AttentionEntry {
  workspaceId: string;
  name: string;
  kind: 'needs-input' | 'waiting';
  message: string;
  ts: string;
  cost?: number;   // only known for the active workspace (live session)
}

// Per-alert dismissal, keyed by (workspace, state-ts): a new state
// transition mints a fresh ts, so a dismissed alert reappears only when
// something genuinely new happens. Persisted, pruned after 24h.
const ATTENTION_DISMISS_KEY = 'cockpit.attention.dismissed';
let dismissedAlerts: Record<string, number> = loadDismissedAlerts();

function loadDismissedAlerts(): Record<string, number> {
  try {
    const raw = localStorage.getItem(ATTENTION_DISMISS_KEY);
    const obj = raw ? JSON.parse(raw) : {};
    const cutoff = Date.now() - 24 * 3600_000;
    const pruned: Record<string, number> = {};
    for (const [k, v] of Object.entries(obj)) {
      if (typeof v === 'number' && v > cutoff) pruned[k] = v;
    }
    return pruned;
  } catch { return {}; }
}

function alertKey(wsId: string, ts: string): string { return `${wsId}::${ts}`; }
function isAlertDismissed(wsId: string, ts: string): boolean {
  return alertKey(wsId, ts) in dismissedAlerts;
}
function dismissAlert(wsId: string, ts: string): void {
  dismissedAlerts[alertKey(wsId, ts)] = Date.now();
  try { localStorage.setItem(ATTENTION_DISMISS_KEY, JSON.stringify(dismissedAlerts)); }
  catch { /* storage full/unavailable — dismissal is best-effort */ }
  refreshAttention();
}

// Ephemeral "finished today" tally (interim until the ~agents fleet log,
// FEAT-0032): counts observed SessionEnd transitions (a real idle, not a
// decay timeout). Resets across a day boundary; rebuilt live, not
// persisted.
const finishedToday: number[] = []; // finish timestamps (ms)

function noteFinish(wsId: string, prev: string | undefined, next: AgentStatePayload | null): void {
  const wasActive = prev === 'busy' || prev === 'waiting' || prev === 'needs-input';
  const nowIdle = next?.state === 'idle' && !next.decayed_from;
  if (wasActive && nowIdle) finishedToday.push(Date.now());
}

function finishedTodayCount(): number {
  const start = new Date(); start.setHours(0, 0, 0, 0);
  const cutoff = start.getTime();
  while (finishedToday.length && finishedToday[0] < cutoff) finishedToday.shift();
  return finishedToday.length;
}

function attentionEntries(): AttentionEntry[] {
  const out: AttentionEntry[] = [];
  const activeCost = lastAgentSnap?.session?.cost?.total_cost_usd;
  for (const [wsId, state] of agentStates) {
    if (state.decayed_from) continue;
    if (state.state !== 'needs-input' && state.state !== 'waiting') continue;
    if (isAlertDismissed(wsId, state.ts || '')) continue;
    const ws = workspaces.find((w) => w.id === wsId);
    out.push({
      workspaceId: wsId,
      name: ws ? effectiveName(ws) : wsId,
      kind: state.state,
      message: state.message
        || (state.state === 'needs-input' ? 'needs your input' : 'turn finished — review'),
      ts: state.ts || '',
      cost: wsId === activeId && typeof activeCost === 'number' ? activeCost : undefined,
    });
  }
  // needs-input above waiting; within a tier, most-recent first.
  const rank = (k: string) => (k === 'needs-input' ? 0 : 1);
  out.sort((a, b) => rank(a.kind) - rank(b.kind) || (a.ts < b.ts ? 1 : -1));
  return out;
}

function buildAttentionRow(entry: AttentionEntry): HTMLElement {
  const row = document.createElement('div');
  row.className = `ws-attention-row kind-${entry.kind}`;
  if (isAlertAcked(entry.workspaceId, entry.ts)) row.classList.add('acked');
  const main = document.createElement('button');
  main.type = 'button';
  main.className = 'ws-attention-main';
  main.title = entry.kind === 'needs-input' ? 'Respond' : 'Review';
  const dot = document.createElement('span');
  dot.className = 'ws-attention-dot';
  const body = document.createElement('span');
  body.className = 'ws-attention-body';
  const name = document.createElement('span');
  name.className = 'ws-attention-name';
  name.textContent = entry.name;
  const msg = document.createElement('span');
  msg.className = 'ws-attention-msg';
  msg.textContent = entry.message;
  const metaBits = [fmtDuration(entry.ts || null, null)];
  if (typeof entry.cost === 'number') metaBits.push(`$${entry.cost.toFixed(2)}`);
  const meta = document.createElement('span');
  meta.className = 'ws-attention-meta';
  meta.textContent = metaBits.filter(Boolean).join(' · ');
  body.append(name, msg, meta);
  main.append(dot, body);
  main.addEventListener('click', () => {
    void (async () => {
      if (activeId !== entry.workspaceId) await openWorkspace(entry.workspaceId);
      showTerminal();
    })();
  });
  const dismiss = document.createElement('button');
  dismiss.type = 'button';
  dismiss.className = 'ws-attention-dismiss';
  dismiss.textContent = '✕';
  dismiss.title = 'Dismiss';
  dismiss.setAttribute('aria-label', `Dismiss ${entry.name}`);
  dismiss.addEventListener('click', (e) => {
    e.stopPropagation();
    dismissAlert(entry.workspaceId, entry.ts);
  });
  row.append(main, dismiss);
  return row;
}

// ----- Account budget block (FEAT-0035 / TASK-0160) --------------------
// The 5h/7d rate limits are account-scoped, so they live at the foot of
// the attention panel (left pane), not in the session strip. The
// freshest sample from any live session is authoritative.
interface RateWindow { used_percentage: number; resets_at?: string }
let latestRateLimits: Record<string, RateWindow> | null = null;
// Epoch ms of the currently-displayed reading. Rate limits are
// account-global, so we keep the FRESHEST reading from any source /
// workspace and never downgrade — switching projects can't change the
// number (TASK-0169).
let rateLimitsAsOf = 0;

// Persist the freshest account-global reading so the Usage block is
// visible immediately on launch and across workspace switches — it's an
// account fact, not a per-session one (TASK-0170).
const USAGE_KEY = 'cockpit:usage';
function persistUsage(): void {
  try {
    if (latestRateLimits) {
      localStorage.setItem(USAGE_KEY, JSON.stringify({ rl: latestRateLimits, at: rateLimitsAsOf }));
    }
  } catch { /* storage unavailable — in-memory only */ }
}
function loadPersistedUsage(): void {
  try {
    const raw = localStorage.getItem(USAGE_KEY);
    if (!raw) return;
    const obj = JSON.parse(raw) as { rl?: Record<string, RateWindow>; at?: number };
    if (obj.rl && typeof obj.at === 'number' && Number.isFinite(obj.at)) {
      latestRateLimits = obj.rl;
      rateLimitsAsOf = obj.at;
    }
  } catch { /* corrupt — ignore */ }
}

// Burn-rate samples per window (TASK-0161): a short ring of (ts, pct)
// so the block can project time-to-cap from the recent slope.
const BUDGET_SAMPLE_WINDOW_MS = 15 * 60_000;
const budgetSamples: Record<string, Array<[number, number]>> = {};

function recordBudgetSample(key: string, pct: number): void {
  const arr = budgetSamples[key] ?? (budgetSamples[key] = []);
  const now = Date.now();
  // Skip duplicate timestamps/values so a resent statusline doesn't
  // skew the slope.
  if (arr.length && arr[arr.length - 1][1] === pct && now - arr[arr.length - 1][0] < 1000) return;
  arr.push([now, pct]);
  const cutoff = now - BUDGET_SAMPLE_WINDOW_MS;
  while (arr.length && arr[0][0] < cutoff) arr.shift();
  if (arr.length > 60) arr.shift();
}

function adoptRateLimits(rl: Record<string, RateWindow>, capturedAtMs: number): void {
  // Only strictly-newer readings adopt: never downgrade, and don't
  // re-push identical-timestamp samples that would dilute the burn slope
  // while idle (review F1); NaN never poisons rateLimitsAsOf (F3).
  if (!Number.isFinite(capturedAtMs) || capturedAtMs <= rateLimitsAsOf) return;
  latestRateLimits = rl;
  rateLimitsAsOf = capturedAtMs;
  for (const key of ['five_hour', 'seven_day']) {
    const w = rl[key];
    if (w && typeof w.used_percentage === 'number') recordBudgetSample(key, w.used_percentage);
  }
  persistUsage();
  refreshAttention();
}

// Live statusline path (active workspace). A missing captured_at means
// "just arrived", so stamp it now.
function noteRateLimits(rl: Record<string, RateWindow>, capturedAt?: string): void {
  // A reading with no captured_at (only pre-change on-disk snapshots) is
  // of unknown freshness — treat it as oldest (0) so it can't downgrade
  // or falsely-freshen the account-global reading (review F2).
  const ms = capturedAt ? Date.parse(capturedAt) : 0;
  adoptRateLimits(rl, Number.isFinite(ms) ? ms : 0);
}

// Poll the fleet for the freshest account-global reading across all
// workspaces (TASK-0171) — a silent backstop; there is no on-demand
// refresh because the statusline is the only usage source (TASK-0172).
async function pollUsage(): Promise<void> {
  try {
    const payload = await cockpitApi.agents.fleet();
    let best: { rl: Record<string, RateWindow>; at: number } | null = null;
    for (const row of payload.rows) {
      if (!row.rateLimits) continue;
      const at = row.rateLimitsAt ? Date.parse(row.rateLimitsAt) : 0;
      if (!best || at > best.at) best = { rl: row.rateLimits, at };
    }
    if (best && best.at > 0) adoptRateLimits(best.rl, best.at);
  } catch { /* transient — keep the last reading */ }
  finally {
    // Always repaint so the "as of" age ticks even without new data.
    refreshAttention();
  }
}
// Show the last-known usage immediately on launch, then refresh from any
// live sidecar shortly after (TASK-0170).
loadPersistedUsage();
refreshAttention();
window.setInterval(() => { void pollUsage(); }, 120_000);
window.setTimeout(() => { void pollUsage(); }, 3_000);

function fmtMsShort(ms: number): string {
  const mins = Math.max(1, Math.round(ms / 60_000));
  if (mins < 60) return `${mins}m`;
  return `${Math.floor(mins / 60)}h ${mins % 60}m`;
}

function budgetRow(label: string, w: RateWindow): HTMLElement {
  const pct = Math.max(0, Math.min(100, w.used_percentage));
  const tier = pct >= 85 ? 'crit' : pct >= 60 ? 'warn' : '';
  const row = document.createElement('div');
  row.className = 'ws-budget-row';
  const lab = document.createElement('span');
  lab.className = 'ws-budget-label';
  lab.textContent = label;
  const track = document.createElement('span');
  track.className = 'ws-budget-track';
  const fill = document.createElement('span');
  fill.className = 'ws-budget-fill' + (tier ? ` ${tier}` : '');
  fill.style.width = `${pct}%`;
  track.appendChild(fill);
  const val = document.createElement('span');
  val.className = 'ws-budget-val' + (tier ? ` ${tier}` : '');
  val.textContent = `${Math.round(pct)}%`;
  row.append(lab, track, val);
  if (w.resets_at) {
    const d = new Date(w.resets_at);
    if (!Number.isNaN(d.getTime())) row.title = `resets ${d.toLocaleTimeString()}`;
  }
  return row;
}

function buildBudgetBlock(): HTMLElement | null {
  const rl = latestRateLimits;
  if (!rl) return null;
  const rows: HTMLElement[] = [];
  const five = rl.five_hour;
  const seven = rl.seven_day;
  if (five && typeof five.used_percentage === 'number') rows.push(budgetRow('5h', five));
  if (seven && typeof seven.used_percentage === 'number') rows.push(budgetRow('7d', seven));
  if (rows.length === 0) return null;
  const block = document.createElement('div');
  block.className = 'ws-budget';
  // Header: "Usage" + as-of freshness (TASK-0169; refresh button removed in TASK-0172).
  const head = document.createElement('div');
  head.className = 'ws-budget-head';
  const title = document.createElement('span');
  title.textContent = 'Usage';
  head.appendChild(title);
  const asOf = document.createElement('span');
  asOf.className = 'ws-budget-asof';
  if (rateLimitsAsOf > 0) {
    const ageMin = Math.floor((Date.now() - rateLimitsAsOf) / 60_000);
    asOf.textContent = ageMin < 1 ? 'just now' : `${ageMin}m ago`;
    if (ageMin >= 10) asOf.classList.add('stale');
    asOf.title = `Reading captured ${new Date(rateLimitsAsOf).toLocaleTimeString()}`;
  }
  head.appendChild(asOf);
  block.appendChild(head);
  for (const r of rows) block.appendChild(r);
  // Reset caption for the binding (5h) window.
  if (five?.resets_at) {
    const d = new Date(five.resets_at);
    if (!Number.isNaN(d.getTime())) {
      const cap = document.createElement('div');
      cap.className = 'ws-budget-reset';
      cap.textContent = `5h resets ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      const proj = budgetProjection('five_hour', five);
      if (proj) {
        const p = document.createElement('span');
        p.className = 'ws-budget-proj';
        p.textContent = ` · ${proj}`;
        cap.appendChild(p);
      }
      block.appendChild(cap);
    }
  }
  return block;
}

// Project time-to-cap from the recent burn slope (TASK-0161). Returns
// null when there's too little data, the slope is flat/negative, or the
// window resets before you'd hit the cap (the reset caption wins).
function budgetProjection(key: string, w: RateWindow): string | null {
  const arr = budgetSamples[key];
  if (!arr || arr.length < 3) return null;
  const first = arr[0];
  const last = arr[arr.length - 1];
  const dtMs = last[0] - first[0];
  const dPct = last[1] - first[1];
  if (dtMs < 60_000 || dPct <= 0.5) return null;   // too little data / flat
  const slope = dPct / dtMs;                         // % per ms
  const remaining = 100 - last[1];
  if (remaining <= 0) return null;
  const msToFull = remaining / slope;
  let resetMs = Infinity;
  if (w.resets_at) {
    const r = new Date(w.resets_at).getTime();
    if (!Number.isNaN(r)) resetMs = r - Date.now();
  }
  if (resetMs <= msToFull) return null;              // resets first — no alarm
  return `~${fmtMsShort(msToFull)} left at this rate`;
}

function refreshAttention(): void {
  const entries = attentionEntries();
  const finished = finishedTodayCount();
  const budget = buildBudgetBlock();
  if (entries.length === 0 && finished === 0 && !budget) {
    attentionPanel.hidden = true;
    attentionPanel.replaceChildren();
    return;
  }
  attentionPanel.replaceChildren();
  if (entries.length > 0) {
    const head = document.createElement('div');
    head.className = 'ws-attention-head';
    head.textContent = 'Needs you';
    attentionPanel.appendChild(head);
    for (const entry of entries) attentionPanel.appendChild(buildAttentionRow(entry));
  }
  if (finished > 0) {
    const foot = document.createElement('button');
    foot.type = 'button';
    foot.className = 'ws-attention-finished';
    foot.textContent = `${finished} finished today`;
    const arrow = document.createElement('span');
    arrow.className = 'ws-attention-arrow';
    arrow.textContent = 'sessions ›';
    foot.appendChild(arrow);
    foot.addEventListener('click', () => { void navigateTo('~agents'); });
    attentionPanel.appendChild(foot);
  }
  if (budget) attentionPanel.appendChild(budget);
  attentionPanel.hidden = false;
}

// ----- Seen-acknowledgement (TASK-0157) --------------------------------
// Pulse means "unseen"; static (colour kept) means "seen, still
// pending". Looking at a workspace — active tab, window focused,
// terminal visible for ACK_DELAY_MS — acknowledges its current alert
// without touching any state data. A new state transition mints a new
// ts, so the pulse resumes for genuinely new alerts.

const ACK_DELAY_MS = 2000;
const ackedAlerts = new Set<string>();
let ackTimer: number | null = null;

function isAlertAcked(wsId: string, ts: string): boolean {
  return ackedAlerts.has(alertKey(wsId, ts));
}

function pruneAckedAlerts(): void {
  // An acked key only matters while that exact (wsId, ts) is still the
  // live state — once the state moves on (new ts) the key is dead
  // weight. Keeps the set bounded to ~one entry per workspace.
  const live = new Set<string>();
  for (const [wsId, st] of agentStates) live.add(alertKey(wsId, st.ts || ''));
  for (const k of ackedAlerts) if (!live.has(k)) ackedAlerts.delete(k);
}

function attentionStateForAck(wsId: string): AgentStatePayload | null {
  const st = agentStates.get(wsId);
  if (!st || st.decayed_from) return null;
  if (st.state !== 'needs-input' && st.state !== 'waiting') return null;
  return st;
}

function repaintAckedActive(): void {
  if (!activeId) return;
  const li = listEl.querySelector<HTMLLIElement>(`li[data-id="${activeId}"]`);
  const ws = workspaces.find((w) => w.id === activeId);
  if (li && ws) applyAgentStateToSquare(li, ws);
  refreshAttention();
}

function scheduleAck(): void {
  if (ackTimer !== null) { clearTimeout(ackTimer); ackTimer = null; }
  if (!activeId || !document.hasFocus() || terminalPane.hidden) return;
  const st = attentionStateForAck(activeId);
  if (!st) return;
  const wsId = activeId;
  const key = alertKey(wsId, st.ts || '');
  if (ackedAlerts.has(key)) return;
  ackTimer = window.setTimeout(() => {
    ackTimer = null;
    // Re-check at fire time — focus/terminal/state may have changed.
    if (activeId !== wsId || !document.hasFocus() || terminalPane.hidden) return;
    const now = attentionStateForAck(wsId);
    if (!now || alertKey(wsId, now.ts || '') !== key) return;
    ackedAlerts.add(key);
    pruneAckedAlerts();
    repaintAckedActive();
  }, ACK_DELAY_MS);
}

window.addEventListener('focus', scheduleAck);
window.addEventListener('blur', () => {
  if (ackTimer !== null) { clearTimeout(ackTimer); ackTimer = null; }
});

document.getElementById('agent-strip-queue')?.addEventListener('click', (e) => {
  if (activeQueueItems.length === 0) return;
  if (!queuePopover.hidden) { queuePopover.hidden = true; return; }
  renderQueuePopover();
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
  queuePopover.style.left = `${Math.max(8, rect.right - 240)}px`;
  queuePopover.style.top = `${rect.top - 8}px`;
  queuePopover.style.transform = 'translateY(-100%)';
  queuePopover.hidden = false;
});

document.addEventListener('click', (e) => {
  if (queuePopover.hidden) return;
  const target = e.target as HTMLElement | null;
  const chip = document.getElementById('agent-strip-queue');
  if (target && !queuePopover.contains(target) && !(chip && chip.contains(target))) {
    queuePopover.hidden = true;
  }
});

agentStripExpand.addEventListener('click', () => {
  if (agentStripDetail.hidden) {
    renderAgentStripDetail();
    agentStripExpand.setAttribute('aria-expanded', 'true');
  } else {
    agentStripDetail.hidden = true;
    agentStripExpand.setAttribute('aria-expanded', 'false');
  }
});

// ----- Task dispatch (FEAT-0021 + FEAT-0024) -----------------------------

type DispatchAgent = 'claude' | 'codex';

interface AgentAction { key: string; label: string; prompt: string; default?: boolean; when?: string[] }
let agentActions: Record<string, AgentAction[]> = {};

async function loadAgentActions(): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/actions`);
    if (!resp.ok) return;
    const data = await resp.json() as { actions?: Record<string, AgentAction[]> };
    agentActions = data.actions || {};
  } catch { /* verbs fall back to the built-in implement/fix prompt */ }
}

const NOTE_TYPE_BY_PREFIX: Record<string, string> = {
  TASK: 'task', ISS: 'issue', FEAT: 'feature',
  REQ: 'requirement', PHASE: 'phase', RISK: 'risk',
};

function noteTypeOfId(id: string): string | null {
  const m = id.match(/^([A-Z]+)-\d/i);
  return m ? NOTE_TYPE_BY_PREFIX[m[1].toUpperCase()] ?? null : null;
}

function verbsForId(
  id: string, opts: { type?: string | null; status?: string | null } = {},
): AgentAction[] {
  // Prefer the row's own type (works for custom actions.yaml types);
  // the ID-prefix guess is the fallback (TASK-0139).
  const t = opts.type || noteTypeOfId(id);
  const verbs = t ? agentActions[t] || [] : [];
  const status = (opts.status || '').toLowerCase();
  if (!status) return verbs;
  // `when:` lists filter by lifecycle status (TASK-0137); entries
  // without one always show.
  return verbs.filter((v) => !v.when || v.when.includes(status));
}

function resolveVerb(id: string, verbKey?: string): AgentAction | null {
  const verbs = verbsForId(id);
  if (verbs.length === 0) return null;
  if (verbKey) return verbs.find((v) => v.key === verbKey) ?? null;
  return verbs.find((v) => v.default) ?? verbs[0];
}

function dispatchAgentKey(): string {
  return `cockpit:dispatch-agent:${activeId || 'default'}`;
}

function loadDispatchAgent(): DispatchAgent {
  try {
    const v = localStorage.getItem(dispatchAgentKey());
    if (v === 'codex') return 'codex';
  } catch { /* ignore */ }
  return 'claude';
}

function saveDispatchAgent(agent: DispatchAgent): void {
  try { localStorage.setItem(dispatchAgentKey(), agent); } catch { /* ignore */ }
}

function dispatchPrompt(id: string, rel: string): string {
  const noteRef = rel ? `docs/${rel}` : id;
  const isIssue = /^ISS-/i.test(id);
  const verb = isIssue ? `Fix ${id}` : `Work on ${id}`;
  return `${verb}. Read ${noteRef} first — the note is the spec — and follow the project-os lifecycle (preflight, implement, close-out).`;
}

// Dispatch runtime client (FEAT-0025 / TASK-0134). The queue and its
// delivery state machine live in the MAIN process (persisted,
// workspace-independent); this side builds prompts, invokes
// dispatch:execute, and renders queue state.

let activeQueueItems: QueuedDispatch[] = [];

function updateQueueChip(): void {
  const chip = document.getElementById('agent-strip-queue');
  if (!chip) return;
  chip.hidden = activeQueueItems.length === 0;
  chip.textContent = `queued ${activeQueueItems.length}`;
  chip.title = activeQueueItems
    .map((d) => `${d.verb ?? 'default'} ${d.id}`).join('\n') + '\n(click to manage)';
  if (activeQueueItems.length > 0) agentStrip.hidden = false;
  if (!queuePopover.hidden) renderQueuePopover();
}

async function refreshQueueItems(): Promise<void> {
  if (!activeId) { activeQueueItems = []; updateQueueChip(); return; }
  try {
    activeQueueItems = await cockpitApi.dispatch.list(activeId);
  } catch { activeQueueItems = []; }
  updateQueueChip();
}

cockpitApi.dispatch.onQueueChanged((ev) => {
  if (ev.workspaceId !== activeId) return;
  activeQueueItems = ev.items;
  updateQueueChip();
});

cockpitApi.dispatch.onDelivered((ev) => {
  const label = `${ev.item.verb ?? 'default'} ${ev.item.id}`;
  const suffix = ev.warning ? ` — ${ev.warning}` : '';
  if (ev.workspaceId === activeId) {
    showStatus(`Delivered ${label} (${ev.mode})${suffix}`);
    void refreshAgentSnapshot();
  }
});

function resolvedPrompt(id: string, rel: string, verbKey?: string): string {
  const verb = resolveVerb(id, verbKey);
  if (!verb) return dispatchPrompt(id, rel);
  return verb.prompt.replaceAll('{id}', id).replaceAll('{rel}', rel);
}

async function dispatchToAgent(
  id: string, rel: string, agent?: DispatchAgent, verbKey?: string,
  workspaceId?: string,
): Promise<void> {
  const wsId = workspaceId || activeId;
  if (!wsId) return;
  const chosen = agent || loadDispatchAgent();
  saveDispatchAgent(chosen);
  // Re-dispatch guard (TASK-0135): warn when this note's most recent
  // dispatch is still attached to a live session.
  const lastDispatch = currentDispatchHistory?.[0];
  if (
    lastDispatch && lastDispatch.live
    && currentFrontmatterId() === id
    && !window.confirm(
      `${id} was already dispatched (${lastDispatch.verb ?? 'default'}) to a live session. Dispatch again?`,
    )
  ) return;
  const item: QueuedDispatch = {
    id, rel, verb: verbKey, agent: chosen,
    prompt: resolvedPrompt(id, rel, verbKey),
    ts: new Date().toISOString(),
  };
  // For the on-screen workspace, make sure a terminal exists and has
  // had time to source the shell before main types into it.
  if (wsId === activeId) {
    const freshPty = !liveTerminals.has(wsId);
    showTerminal();
    await new Promise((r) => setTimeout(r, freshPty ? 600 : 150));
  }
  const res = await cockpitApi.dispatch.execute(wsId, item);
  if ('error' in res && res.error) {
    showStatus(`Dispatch failed: ${res.error}`, 'error');
    return;
  }
  const label = `${item.verb ?? 'default'} ${id}`;
  if (res.queued) {
    showStatus(`Queued ${label}${res.warning ? ` — ${res.warning}` : ''}`);
  } else {
    showStatus(`Dispatched ${label} (${res.delivered})${res.warning ? ` — ${res.warning}` : ''}`);
  }
}

// ---- queue popover ----

const queuePopover = document.createElement('div');
queuePopover.id = 'queue-popover';
queuePopover.className = 'queue-popover';
queuePopover.hidden = true;
document.body.appendChild(queuePopover);

function renderQueuePopover(): void {
  queuePopover.replaceChildren();
  if (activeQueueItems.length === 0) { queuePopover.hidden = true; return; }
  activeQueueItems.forEach((d, idx) => {
    const row = document.createElement('div');
    row.className = 'queue-row';
    const label = document.createElement('span');
    label.className = 'queue-row-label';
    label.textContent = `${d.verb ?? 'default'} · ${d.id}`;
    label.title = d.prompt;
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'queue-row-remove';
    remove.textContent = '×';
    remove.title = 'Remove from queue';
    remove.addEventListener('click', () => {
      if (!activeId) return;
      void cockpitApi.dispatch.remove(activeId, idx).then((items) => {
        activeQueueItems = items;
        updateQueueChip();
        renderQueuePopover();
      });
    });
    row.append(label, remove);
    queuePopover.appendChild(row);
  });
  const clear = document.createElement('button');
  clear.type = 'button';
  clear.className = 'queue-clear';
  clear.textContent = 'Clear all';
  clear.addEventListener('click', () => {
    if (!activeId) return;
    void cockpitApi.dispatch.clear(activeId).then(() => {
      activeQueueItems = [];
      updateQueueChip();
      queuePopover.hidden = true;
    });
  });
  queuePopover.appendChild(clear);
}

// ---- CLI dispatch-requests (FEAT-0025 / TASK-0136) ----

function handleDispatchRequest(rec: { id?: string; verb?: string; agent?: string }): void {
  if (!rec || typeof rec.id !== 'string' || !rec.id) return;
  const agent = rec.agent === 'codex' ? 'codex' as const
    : rec.agent === 'claude' ? 'claude' as const : undefined;
  // Resolve the note's rel via the quick-switch corpus when possible;
  // the prompt template tolerates a missing rel (falls back to the ID).
  const hit = quickCorpus.find((q) => q.id.toUpperCase() === rec.id!.toUpperCase());
  void dispatchToAgent(rec.id.toUpperCase(), hit?.rel || '', agent, rec.verb);
}

async function drainDispatchRequests(): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/dispatch-requests`);
    if (!resp.ok) return;
    const data = await resp.json() as { requests?: Array<{ id?: string; verb?: string; agent?: string }> };
    for (const rec of data.requests || []) handleDispatchRequest(rec);
  } catch { /* requests retry on next attach */ }
}

function isDispatchableId(id: string | undefined): boolean {
  return !!id && noteTypeOfId(id) !== null;
}

function currentFrontmatterId(): string | undefined {
  if (!currentRel || currentRel.startsWith('~')) return undefined;
  const name = currentRel.split('/').pop() || '';
  const m = name.match(/^((TASK|ISS|FEAT|REQ|PHASE|RISK)-\d+)/i);
  return m ? m[1].toUpperCase() : undefined;
}

// The top-bar ▶ was replaced by the doc header's verb buttons
// (FEAT-0026 / TASK-0140).

// ----- Session history in Overview (FEAT-0022 / TASK-0124 + TASK-0127) --

function fmtDuration(started: string | null, ended: string | null): string {
  if (!started) return '';
  const a = Date.parse(started);
  const b = ended ? Date.parse(ended) : Date.now();
  if (!Number.isFinite(a) || !Number.isFinite(b) || b < a) return '';
  const mins = Math.round((b - a) / 60_000);
  if (mins < 1) return '<1 min';
  if (mins < 60) return `${mins} min`;
  return `${Math.floor(mins / 60)}h ${mins % 60}m`;
}

function fmtSessionDate(ts: string | null): string {
  if (!ts) return '';
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return '';
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${mm}-${dd}`;
}

async function fetchSessions(): Promise<AgentSessionSlim[]> {
  if (!sidecarBaseUrl) return [];
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/sessions`);
    if (!resp.ok) return [];
    const data = await resp.json() as { sessions?: AgentSessionSlim[] };
    return data.sessions || [];
  } catch {
    return [];
  }
}

// ----- Recent activity feed (TASK-0127; sessions moved to ~agents in
// TASK-0178 — the overview is project-focused). --------------------------

function buildFeedsGrid(data: StatsPayload): HTMLElement {
  const grid = document.createElement('section');
  grid.className = 'ov-feeds ov-feeds-single';
  grid.append(buildRecentFeed(data.activity.recent));
  return grid;
}

// Per-project session history on the ~agents screen (TASK-0180 / ISS-0013):
// driven by the selected fleet row, sourced from that workspace's sidecar
// or its persisted .cockpit/sessions.json (via the agents:sessions IPC).
function buildAgentsSessionSection(workspaceId: string | null, name: string): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-feed ov-sessions-feed agents-sessions';
  const h = document.createElement('h3');
  h.textContent = name ? `Recent sessions — ${name}` : 'Recent sessions';
  wrap.appendChild(h);
  const body = document.createElement('div');
  body.className = 'ov-sessions-body';
  wrap.appendChild(body);
  if (workspaceId) void fillAgentsSessions(body, workspaceId);
  return wrap;
}

async function fillAgentsSessions(body: HTMLElement, workspaceId: string): Promise<void> {
  let sessions: AgentSessionSlim[] = [];
  try { sessions = await cockpitApi.agents.sessions(workspaceId); } catch { /* empty */ }
  sessions = [...sessions].sort((a, b) => (b.started || '').localeCompare(a.started || ''));
  if (sessions.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No sessions recorded for this project yet.';
    body.replaceChildren(empty);
    return;
  }
  // The ~session detail page reads the ACTIVE sidecar, so rows only
  // deep-link when the selected project is the active one.
  const navigable = workspaceId === activeId;
  const ul = document.createElement('ul');
  ul.className = 'ov-feed-list';
  for (const s of sessions.slice(0, 20)) ul.appendChild(buildSessionFeedRow(s, navigable));
  body.replaceChildren(ul);
}

function buildSessionFeedRow(s: AgentSessionSlim, navigable = true): HTMLLIElement {
  const li = document.createElement('li');
  const date = document.createElement('span');
  date.className = 'ov-feed-date';
  date.textContent = fmtSessionDate(s.started);
  const pill = document.createElement('span');
  pill.className = `ov-feed-type ov-agent-pill ov-agent-${(s.agent || 'agent').replace(/[^a-z0-9]/gi, '')}`;
  pill.textContent = s.agent || 'agent';
  const title = document.createElement('span');
  title.className = 'ov-feed-title';
  title.textContent = s.last_prompt || '(no prompt)';
  li.append(date, pill, title);
  const disp = (s as unknown as { dispatches?: Array<{ verb?: string; id: string }> }).dispatches;
  if (disp && disp.length > 0) {
    const chip = document.createElement('span');
    chip.className = 'ov-feed-tag ov-session-dispatch';
    chip.textContent = `← ${disp[0].verb ?? 'dispatch'} ${disp[0].id}`;
    li.appendChild(chip);
  }
  if (s.live) {
    const live = document.createElement('span');
    live.className = 'ov-session-live';
    live.textContent = 'live';
    li.appendChild(live);
  }
  const meta = document.createElement('span');
  meta.className = 'ov-feed-tag ov-session-row-meta';
  const dur = fmtDuration(s.started, s.ended);
  const cost = s.cost && typeof s.cost.total_cost_usd === 'number'
    ? `$${s.cost.total_cost_usd.toFixed(2)}` : '';
  meta.textContent = [dur, cost].filter(Boolean).join(' · ');
  if (s.live && s.started) meta.dataset.durStart = s.started;
  if (meta.textContent) li.appendChild(meta);
  if (s.undocumented) {
    const undoc = document.createElement('span');
    undoc.className = 'ov-session-undoc';
    undoc.textContent = 'undocumented';
    li.appendChild(undoc);
  }
  if (navigable) {
    li.style.cursor = 'pointer';
    li.title = `session ${s.session_id}`;
    li.addEventListener('click', () => {
      void navigateTo(`~session/${s.session_id}`);
    });
  } else {
    li.title = `session ${s.session_id} — open this project to view detail`;
  }
  return li;
}

// ----- Session detail virtual page (TASK-0127) --------------------------

async function renderSessionDetailPage(sessionId: string): Promise<boolean> {
  const sessions = await fetchSessions();
  const s = sessions.find((x) => x.session_id === sessionId);
  if (!s) {
    mountPlaceholder(`session ${sessionId}`);
    return false;
  }
  docView.classList.remove('overview-pane', 'agents-page');
  docView.replaceChildren();

  const head = document.createElement('header');
  head.className = 'session-page-head';
  const h1 = document.createElement('h1');
  h1.textContent = `${s.agent || 'agent'} session`;
  if (s.live) {
    const live = document.createElement('span');
    live.className = 'ov-session-live';
    live.textContent = 'live';
    h1.appendChild(live);
  }
  const meta = document.createElement('p');
  meta.className = 'session-page-meta';
  const parts = [
    s.session_id,
    s.started ? new Date(s.started).toLocaleString() : '',
    fmtDuration(s.started, s.ended),
    s.cost && typeof s.cost.total_cost_usd === 'number'
      ? `$${s.cost.total_cost_usd.toFixed(2)}` : '',
  ].filter(Boolean);
  meta.textContent = parts.join(' · ');
  head.append(h1, meta);
  if (s.undocumented) {
    const warn = document.createElement('p');
    warn.className = 'session-page-undoc';
    warn.textContent = 'Source files were edited this session without touching a TASK/ISS/CHG note.';
    head.appendChild(warn);
  }
  docView.appendChild(head);

  const section = (title: string): HTMLElement => {
    const sec = document.createElement('section');
    sec.className = 'session-page-section';
    const h = document.createElement('h2');
    h.textContent = title;
    sec.appendChild(h);
    docView.appendChild(sec);
    return sec;
  };

  if (s.prompts && s.prompts.length > 0) {
    const sec = section(`Prompts (${s.prompts.length})`);
    const ol = document.createElement('ol');
    for (const pr of s.prompts) {
      const li = document.createElement('li');
      li.textContent = pr.text;
      ol.appendChild(li);
    }
    sec.appendChild(ol);
  }

  if (s.files.length > 0) {
    const sec = section(`Files touched (${s.files.length})`);
    const ul = document.createElement('ul');
    for (const f of s.files) {
      const li = document.createElement('li');
      if (!f.startsWith('/')) {
        const a = document.createElement('a');
        a.href = '#';
        a.textContent = f;
        a.addEventListener('click', (e) => { e.preventDefault(); void navigateTo(f); });
        li.appendChild(a);
      } else {
        li.textContent = f;
      }
      ul.appendChild(li);
    }
    sec.appendChild(ul);
  }

  const detailDispatches = (s as unknown as { dispatches?: Array<{ verb?: string; id: string }> }).dispatches;
  if (detailDispatches && detailDispatches.length > 0) {
    const sec = section('Dispatched from');
    const pd = document.createElement('p');
    pd.className = 'meta';
    pd.textContent = detailDispatches
      .map((d) => `${d.verb ?? 'default'} ${d.id}`).join(', ');
    sec.appendChild(pd);
  }

  if (s.chg_ids.length > 0) {
    const sec = section('Produced changes');
    const ul = document.createElement('ul');
    for (const chg of s.chg_ids) {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = '#';
      a.textContent = chg;
      a.addEventListener('click', (e) => {
        e.preventDefault();
        void navigateTo(`changes/${chg}.md`);
      });
      li.appendChild(a);
      ul.appendChild(li);
    }
    sec.appendChild(ul);
  }

  if (s.transcript_path) {
    const sec = section('Transcript');
    const path = s.transcript_path;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'session-transcript-link';
    btn.textContent = path;
    btn.title = 'Reveal in Finder';
    btn.addEventListener('click', () => { void cockpitApi.app.revealInFinder(path); });
    sec.appendChild(btn);
  }

  docView.hidden = false;
  placeholder.hidden = true;
  docView.scrollTop = 0;
  return true;
}


// ----------------------------------------------------------------------
// Agents fleet screen (FEAT-0032 / TASK-0151) — cross-workspace mission
// control: one row per workspace, live state + session + cost + queue,
// with jump actions. Data comes from the main-process fleet proxy.
// ----------------------------------------------------------------------

interface FleetRow {
  workspaceId: string;
  name: string;
  root: string;
  state: string | null;
  message?: string;
  stateTs?: string;
  live: boolean;
  agent?: string;
  lastPrompt?: string;
  lastFile?: string;
  undocumented?: boolean;
  cost?: number;
  ctx?: number;
  fiveHourPct?: number;
  fiveHourResetsAt?: string;
  rateLimits?: Record<string, { used_percentage: number; resets_at?: string }>;
  rateLimitsAt?: string;
  dispatchOrigin?: string;
  queueDepth: number;
  sessionId?: string;
}
interface FleetPayload { rows: FleetRow[]; generatedAt: number; }

const FLEET_ATTENTION = new Set(['needs-input', 'waiting', 'busy']);

function fleetRank(r: FleetRow): number {
  const order: Record<string, number> = {
    'needs-input': 0, 'waiting': 1, 'busy': 2, 'error': 3,
    'done': 4, 'idle': 5,
  };
  return order[r.state ?? 'idle'] ?? 6;
}

// Selected project on the ~agents screen — drives the session-history
// section (TASK-0180). Persists across live rebuilds.
let agentsSelectedWs: string | null = null;

async function renderAgentsPage(preserveScroll = false): Promise<boolean> {
  let payload: FleetPayload;
  try {
    payload = await cockpitApi.agents.fleet();
  } catch {
    mountPlaceholder('agents');
    return false;
  }
  // Live-refresh rebuilds the whole list; keep the viewport where the
  // user left it so a peer workspace's state change doesn't yank the
  // headline fleet screen back to the top (review finding F1).
  const prevScroll = docView.scrollTop;
  docView.classList.remove('overview-pane', 'agents-page');
  docView.classList.add('agents-page');
  docView.replaceChildren();

  const rows = [...payload.rows].sort((a, b) =>
    fleetRank(a) - fleetRank(b) || a.name.localeCompare(b.name));
  const active = rows.filter((r) => r.state && FLEET_ATTENTION.has(r.state));
  const totalCost = rows.reduce((s, r) => s + (r.cost ?? 0), 0);
  const totalQueued = rows.reduce((s, r) => s + r.queueDepth, 0);
  const fiveHour = rows.map((r) => r.fiveHourPct).filter((p): p is number => typeof p === 'number');
  const budget = fiveHour.length ? Math.max(...fiveHour) : null;

  const head = document.createElement('header');
  head.className = 'agents-head';
  const h1 = document.createElement('h1');
  h1.textContent = 'Agents';
  const sub = document.createElement('span');
  sub.className = 'agents-head-sub';
  const bits = [
    `${active.length} active`,
    `${totalQueued} queued`,
    totalCost > 0 ? `$${totalCost.toFixed(2)} today` : null,
  ].filter(Boolean) as string[];
  sub.textContent = bits.join(' · ');
  head.append(h1, sub);
  if (budget !== null) {
    const rl = document.createElement('span');
    rl.className = 'agents-head-budget';
    if (budget >= 80) rl.classList.add('meter-hot');
    const reset = rows.find((r) => typeof r.fiveHourResetsAt === 'string')?.fiveHourResetsAt;
    rl.textContent = `5h limit ${Math.round(budget)}%`;
    if (reset) rl.title = `resets ${new Date(reset).toLocaleTimeString()}`;
    head.appendChild(rl);
  }
  docView.appendChild(head);

  // Which project's session history to show below (TASK-0180): the
  // selected fleet row, else the active workspace, else the top row.
  const has = (id: string | null): boolean => !!id && rows.some((r) => r.workspaceId === id);
  const selected = has(agentsSelectedWs) ? agentsSelectedWs
    : has(activeId) ? activeId
    : rows[0]?.workspaceId ?? null;

  const list = document.createElement('div');
  list.className = 'agents-list';
  for (const r of rows) {
    const el = buildFleetRow(r);
    if (r.workspaceId === selected) el.classList.add('is-selected');
    // Click the name to select this project's session history below
    // (the action buttons keep their own behaviour).
    const idcol = el.querySelector<HTMLElement>('.agents-row-id');
    if (idcol) {
      idcol.style.cursor = 'pointer';
      idcol.title = "Show this project's session history";
      idcol.addEventListener('click', () => {
        if (agentsSelectedWs === r.workspaceId) return;
        agentsSelectedWs = r.workspaceId;
        void renderAgentsPage(true);
      });
    }
    list.appendChild(el);
  }
  docView.appendChild(list);

  // Session history for the selected project (TASK-0180 / ISS-0013).
  const selName = rows.find((r) => r.workspaceId === selected)?.name ?? '';
  docView.appendChild(buildAgentsSessionSection(selected, selName));

  docView.hidden = false;
  placeholder.hidden = true;
  docView.scrollTop = preserveScroll ? prevScroll : 0;
  return true;
}

function buildFleetRow(r: FleetRow): HTMLElement {
  const row = document.createElement('div');
  row.className = 'agents-row';
  if (!r.state || r.state === 'idle') row.classList.add('is-dormant');

  const dot = document.createElement('span');
  dot.className = 'agents-row-dot';
  dot.dataset.state = r.state ?? 'idle';

  const idcol = document.createElement('div');
  idcol.className = 'agents-row-id';
  const name = document.createElement('span');
  name.className = 'agents-row-name';
  name.textContent = r.name;
  idcol.append(dot, name);

  const sess = document.createElement('div');
  sess.className = 'agents-row-sess';
  const line1 = document.createElement('span');
  line1.className = 'agents-row-line1';
  const stateLabel = r.state ? agentStateLabel(r.state) : 'idle';
  const elapsed = r.stateTs ? fmtDuration(r.stateTs, null) : '';
  const summary = r.live && r.lastPrompt ? ` — ${r.lastPrompt}`
    : r.message ? ` — ${r.message}`
    : r.lastPrompt ? ` — ${r.lastPrompt}` : '';
  line1.textContent = `${r.agent || 'agent'} · ${stateLabel}${elapsed ? ' ' + elapsed : ''}${summary}`;
  const line2 = document.createElement('span');
  line2.className = 'agents-row-line2';
  const l2 = [];
  if (r.lastFile) l2.push(`last: ${r.lastFile}`);
  if (r.dispatchOrigin) l2.push(`from ${r.dispatchOrigin}`);
  if (r.queueDepth > 0) l2.push(`queue ${r.queueDepth}`);
  line2.textContent = l2.join(' · ');
  if (r.undocumented) {
    const u = document.createElement('span');
    u.className = 'agents-row-undoc';
    u.textContent = 'undocumented';
    line2.append(' ', u);
  }
  sess.append(line1, line2);

  const meters = document.createElement('div');
  meters.className = 'agents-row-meters';
  const mbits = [];
  if (typeof r.ctx === 'number') mbits.push(`ctx ${Math.round(r.ctx)}%`);
  if (typeof r.cost === 'number') mbits.push(`$${r.cost.toFixed(2)}`);
  meters.textContent = mbits.join(' · ');

  const acts = document.createElement('div');
  acts.className = 'agents-row-acts';
  const primaryLabel = r.state === 'needs-input' ? 'respond'
    : r.state === 'waiting' ? 'review' : 'terminal';
  const termBtn = document.createElement('button');
  termBtn.type = 'button';
  termBtn.className = 'agents-btn primary';
  termBtn.textContent = primaryLabel;
  termBtn.addEventListener('click', () => {
    void (async () => {
      if (activeId !== r.workspaceId) await openWorkspace(r.workspaceId);
      showTerminal();
    })();
  });
  acts.appendChild(termBtn);
  if (r.sessionId) {
    const sessBtn = document.createElement('button');
    sessBtn.type = 'button';
    sessBtn.className = 'agents-btn';
    sessBtn.textContent = 'session';
    sessBtn.addEventListener('click', () => {
      void (async () => {
        if (activeId !== r.workspaceId) await openWorkspace(r.workspaceId);
        void navigateTo(`~session/${r.sessionId}`);
      })();
    });
    acts.appendChild(sessBtn);
  }

  row.append(idcol, sess, meters, acts);
  return row;
}


// ----------------------------------------------------------------------
// Overview scopes (FEAT-0023 / TASK-0129 + TASK-0130)
// ----------------------------------------------------------------------

// ----- Left pane: scope list -------------------------------------------

function buildScopeRow(
  label: string, target: string, current: boolean,
  pct: number | null,
): HTMLElement {
  const row = document.createElement('button');
  row.type = 'button';
  row.className = 'scope-row' + (current ? ' current' : '');
  const name = document.createElement('span');
  name.className = 'scope-name';
  name.textContent = label;
  row.appendChild(name);
  if (pct != null) {
    const bar = document.createElement('span');
    bar.className = 'scope-bar';
    const fill = document.createElement('span');
    fill.style.width = `${Math.round(pct)}%`;
    bar.appendChild(fill);
    const pctEl = document.createElement('span');
    pctEl.className = 'scope-pct';
    pctEl.textContent = `${Math.round(pct)}%`;
    row.append(bar, pctEl);
  }
  row.addEventListener('click', () => {
    if (currentRel === target) return;
    void navigateTo(target);
  });
  return row;
}

function renderOverviewScopePane(): void {
  if (currentNavMode !== 'overview') return;
  wsNavPlaceholder.hidden = true;
  wsNavContent.hidden = false;
  const wrap = document.createElement('div');
  wrap.className = 'scope-pane';
  const h = document.createElement('h4');
  h.className = 'scope-heading';
  h.textContent = 'Scope';
  wrap.appendChild(h);
  wrap.appendChild(buildScopeRow('⌂ Project', '~overview', overviewScope === null, null));
  const phases = (scopePhaseList || []).filter((p) => /^PHASE-/i.test(p.key));
  if (phases.length > 0) {
    const ph = document.createElement('h4');
    ph.className = 'scope-heading';
    ph.textContent = 'Phases';
    wrap.appendChild(ph);
    for (const p of phases) {
      const total = p.tasks.done + p.tasks.in_progress + p.tasks.backlog;
      const pct = total > 0 ? (p.tasks.done / total) * 100 : 0;
      wrap.appendChild(buildScopeRow(
        p.title, `~overview/${p.key}`, overviewScope === p.key, pct,
      ));
    }
  }
  wsNavContent.replaceChildren(wrap);
}

// ----- Centre: scoped dashboard ----------------------------------------

function buildScopedHeader(data: StatsPayload): HTMLElement {
  const scope = data.scope!;
  const head = document.createElement('header');
  head.className = 'scoped-head';
  const crumb = document.createElement('a');
  crumb.href = '#';
  crumb.className = 'scoped-crumb';
  crumb.textContent = 'Overview';
  crumb.addEventListener('click', (e) => {
    e.preventDefault();
    void navigateTo('~overview');
  });
  const sep = document.createElement('span');
  sep.className = 'scoped-sep';
  sep.textContent = '▸';
  const title = document.createElement('h2');
  title.className = 'scoped-title';
  title.textContent = `${scope.id} · ${scope.title}`;
  head.append(crumb, sep, title);
  appendIf(head, statusChip(scope.status));
  const open = document.createElement('a');
  open.href = '#';
  open.className = 'scoped-open-note';
  open.textContent = 'open note ↗';
  open.addEventListener('click', (e) => {
    e.preventDefault();
    void navigateTo(scope.rel);
  });
  head.appendChild(open);
  return head;
}

function buildScopedFeatures(p: StatsPhase): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section';
  wrap.innerHTML = '<h3>Features in this phase</h3>';
  if (p.features.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No features assigned to this phase yet.';
    wrap.appendChild(empty);
  }
  for (const feat of p.features) {
    const row = document.createElement('div');
    row.className = 'scoped-feat';
    const name = document.createElement('a');
    name.href = '#';
    name.className = 'scoped-feat-name';
    name.textContent = `${feat.id ?? ''} ${feat.title}`.trim();
    if (feat.rel) {
      name.addEventListener('click', (e) => {
        e.preventDefault();
        void navigateTo(feat.rel!);
      });
      name.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const fid = feat.id || '';
        void cockpitApi.app.showContextMenu('nav-row', {
          id: fid, rel: feat.rel || '',
          workspaceId: activeId || '', root: '',
          verbs: verbsForId(fid, { type: 'feature', status: feat.status })
            .map((v) => ({ key: v.key, label: v.label })),
          currentAgent: loadDispatchAgent(),
        });
      });
    }
    const sqs = document.createElement('span');
    sqs.className = 'scoped-feat-sqs';
    for (const c of feat.children) sqs.appendChild(makePhaseSquare(c, false));
    if (feat.children.length === 0) {
      const none = document.createElement('span');
      none.className = 'ov-phase-empty';
      none.textContent = '(no children)';
      sqs.appendChild(none);
    }
    row.append(name, sqs);
    appendIf(row, statusChip(feat.status));
    wrap.appendChild(row);
  }
  if (p.loose.length > 0) {
    const row = document.createElement('div');
    row.className = 'scoped-feat scoped-loose';
    const name = document.createElement('span');
    name.className = 'scoped-feat-name';
    name.textContent = 'Loose items';
    const sqs = document.createElement('span');
    sqs.className = 'scoped-feat-sqs';
    for (const c of p.loose) sqs.appendChild(makePhaseSquare(c, false));
    row.append(name, sqs);
    wrap.appendChild(row);
  }
  return wrap;
}

function buildScopedTiles(data: StatsPayload): HTMLElement {
  const grid = document.createElement('section');
  grid.className = 'ov-feeds';

  const exit = document.createElement('section');
  exit.className = 'ov-section';
  exit.innerHTML = '<h3>Exit criteria</h3>';
  const criteria = data.exit_criteria || [];
  if (criteria.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No exit criteria recorded in the phase note.';
    exit.appendChild(empty);
  } else {
    const ul = document.createElement('ul');
    ul.className = 'scoped-exit-list';
    for (const c of criteria) {
      const li = document.createElement('li');
      li.className = c.done ? 'done' : '';
      li.textContent = `${c.done ? '☑' : '☐'} ${c.text}`;
      ul.appendChild(li);
    }
    exit.appendChild(ul);
  }

  const act = document.createElement('section');
  act.className = 'ov-section ov-feed';
  act.innerHTML = '<h3>Activity in this phase</h3>';
  const recent = data.activity.recent;
  if (recent.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No recorded activity yet.';
    act.appendChild(empty);
  } else {
    const ul = document.createElement('ul');
    // Scoped rows carry only date + type + title (no id/tag cells), so
    // they use a 3-column template — otherwise the title lands in the
    // fixed id column and truncates early (TASK-0173). The type cell is
    // always emitted (empty when absent) to keep placement deterministic.
    ul.className = 'ov-feed-list ov-feed-scoped';
    for (const r of recent.slice(0, 8)) {
      const li = document.createElement('li');
      const typeTag = r.type
        ? `<span class="ov-feed-type ov-feed-type-${escapeHtml(r.type)}">${escapeHtml(r.type)}</span>`
        : '<span class="ov-feed-type ov-feed-type-empty"></span>';
      li.innerHTML = `<span class="ov-feed-date">${escapeHtml(r.date)}</span>${typeTag}<span class="ov-feed-title">${escapeHtml(r.title)}</span>`;
      li.style.cursor = 'pointer';
      li.addEventListener('click', () => { if (r.rel) void navigateTo(r.rel); });
      ul.appendChild(li);
    }
    act.appendChild(ul);
  }

  grid.append(exit, act);
  return grid;
}

function renderScopedOverview(data: StatsPayload): void {
  docView.classList.add('overview-pane');
  const parts: HTMLElement[] = [buildScopedHeader(data), buildHero(data.hero)];
  const p = data.phases[0];
  if (p) parts.push(buildScopedFeatures(p));
  parts.push(buildScopedTiles(data));
  docView.replaceChildren(...parts);
  docView.hidden = false;
  placeholder.hidden = true;
  refreshFooterPath();
}

// ----- Right pane: Now column + scope context ---------------------------


async function renderOverviewRightPane(scopeRel: string | null): Promise<void> {
  // Overview right pane is project-focused (TASK-0178): agent state lives
  // on the rail, strip, attention inbox, and the ~agents screen — not here.
  rightPaneContent.replaceChildren();
  if (scopeRel && sidecarBaseUrl) {
    try {
      const resp = await fetch(
        `${sidecarBaseUrl}/api/cockpit/context?this=${encodeURIComponent(scopeRel)}`,
      );
      if (!resp.ok) return;
      const data = (await resp.json()) as ContextPayload;
      // Guard: user may have navigated away while we fetched.
      if (!currentRel || !currentRel.startsWith('~overview/')) return;
      const linked = renderContextSection('Linked', data.linked || []);
      if (linked) rightPaneContent.appendChild(linked);
      const back = renderContextSection('Backlinks', data.backlinks || []);
      if (back) rightPaneContent.appendChild(back);
    } catch { /* context is best-effort */ }
    return;
  }
  // Project scope: pinned notes as quick jumps.
  const pins = activeId ? loadPinned(activeId) : [];
  if (pins.length > 0) {
    const h = document.createElement('h4');
    h.className = 'scope-heading';
    h.textContent = 'Pinned';
    rightPaneContent.appendChild(h);
    const ul = document.createElement('ul');
    ul.className = 'ov-feed-list';
    for (const rel of pins) {
      const li = document.createElement('li');
      li.textContent = rel.split('/').pop() || rel;
      li.title = rel;
      li.style.cursor = 'pointer';
      li.addEventListener('click', () => void navigateTo(rel));
      ul.appendChild(li);
    }
    rightPaneContent.appendChild(ul);
  }
}

// ----- Lifecycle: in-place refresh + live-duration tick (TASK-0130) -----

async function refreshOverviewInPlace(): Promise<void> {
  if (!currentRel || !currentRel.startsWith('~overview')) return;
  const scroll = docView.scrollTop;
  const ok = await renderOverviewPage(overviewScope);
  if (ok) docView.scrollTop = scroll;
}

function updateLiveDurations(): void {
  const session = lastAgentSnap?.session;
  document.querySelectorAll<HTMLElement>('[data-dur-start]').forEach((el) => {
    const start = el.dataset.durStart;
    if (!start) return;
    const dur = fmtDuration(start, null);
    if (!dur) return;
    // Session feed rows carry "dur · $cost" — preserve the cost part.
    const cost = el.textContent?.includes('$')
      ? el.textContent.slice(el.textContent.indexOf('$')) : '';
    el.textContent = cost ? `${dur} · ${cost}` : dur;
  });
}

window.setInterval(updateLiveDurations, 30_000);


// ----------------------------------------------------------------------
// Settings popover (FEAT-0027 / TASK-0142)
// ----------------------------------------------------------------------

const settingsBtn = $<HTMLButtonElement>('#settings-toggle');
const settingsPopover = $<HTMLDivElement>('#settings-popover');
const settingExternalHook = $<HTMLInputElement>('#setting-external-hook');
const settingsStatus = $<HTMLParagraphElement>('#settings-status');

function settingsFeedback(text: string, isError = false): void {
  settingsStatus.textContent = text;
  settingsStatus.hidden = !text;
  settingsStatus.classList.toggle('is-error', isError);
}

async function openSettingsPopover(): Promise<void> {
  try {
    const s = await cockpitApi.settings.get();
    settingExternalHook.checked = s.externalHook === true;
  } catch { /* leave unchecked */ }
  settingsFeedback('');
  const rect = settingsBtn.getBoundingClientRect();
  settingsPopover.style.left = `${rect.right + 8}px`;
  settingsPopover.style.bottom = `${Math.max(8, window.innerHeight - rect.bottom)}px`;
  settingsPopover.hidden = false;
  settingsBtn.setAttribute('aria-expanded', 'true');
}

function closeSettingsPopover(): void {
  settingsPopover.hidden = true;
  settingsBtn.setAttribute('aria-expanded', 'false');
}

settingsBtn.addEventListener('click', () => {
  if (settingsPopover.hidden) void openSettingsPopover();
  else closeSettingsPopover();
});

document.addEventListener('click', (e) => {
  if (settingsPopover.hidden) return;
  const target = e.target as HTMLElement | null;
  if (target && !settingsPopover.contains(target) && !settingsBtn.contains(target)) {
    closeSettingsPopover();
  }
});

settingExternalHook.addEventListener('change', () => {
  const want = settingExternalHook.checked;
  settingExternalHook.disabled = true;
  void cockpitApi.settings.set({ externalHook: want }).then((res) => {
    settingExternalHook.disabled = false;
    if (!res.ok) {
      settingExternalHook.checked = res.settings.externalHook;
      settingsFeedback(res.error || 'Failed to update setting', true);
      return;
    }
    settingsFeedback(want
      ? 'Hook installed in ~/.claude/settings.json — new Claude sessions will signal state.'
      : 'Hook removed from ~/.claude/settings.json.');
  });
});

