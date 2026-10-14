// The draft home window's page (FEAT-0160).
//
// A board to read at a glance, not a page to read. One row per project: a
// mark for what its agent is doing, a mark per thing owed, and a bar per
// active phase with its features and exit criteria. The words are in the
// tooltips and in the present window, which every mark opens when chosen.
// No act happens here.
//
// Loaded as a plain `<script>` after home-model.js, like the present
// window's renderer. Everything is inside one function so nothing here
// becomes a global beside the model's functions.

interface HomeBridge {
  data(): Promise<unknown>;
  fleet(): Promise<unknown>;
  open(target: { projectId: string; target: string }): Promise<boolean>;
}
interface Window { cockpitHome?: HomeBridge; }

(() => {
  const bridge = window.cockpitHome;
  const REFRESH_MS = 15000;
  /** More marks of one kind than this become a "+n". */
  const MARKS_PER_VERB = 8;
  /** More features than this are drawn as one proportional bar. */
  const SEGMENTS_SHOWN = 18;
  const SVG_NS = 'http://www.w3.org/2000/svg';

  const AGENT_ICON: Record<HomeAgentWord, string> = {
    'working': 'a-working',
    'needs your answer': 'a-needs',
    'stuck': 'a-stuck',
    'finished its turn': 'a-finished',
    'quiet': 'a-quiet',
    'not open': 'a-closed',
  };
  const STATE_WORD = { done: 'done', now: 'in progress', next: 'not started' };

  const byId = (id: string): HTMLElement => document.getElementById(id) as HTMLElement;

  function make(tag: string, cls?: string, text?: string): HTMLElement {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  /** A button whose words are its tooltip and its accessible name. */
  function mark(cls: string, tip: string, onChoose?: () => void): HTMLButtonElement {
    const btn = make('button', cls) as HTMLButtonElement;
    btn.type = 'button';
    btn.title = tip;
    btn.setAttribute('aria-label', tip);
    if (onChoose) btn.addEventListener('click', onChoose);
    return btn;
  }

  function glyph(id: string): SVGElement {
    const svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('class', 'glyph');
    svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS(SVG_NS, 'use');
    use.setAttribute('href', `#${id}`);
    svg.append(use);
    return svg;
  }

  function applyTheme(): void {
    let saved: string | null = null;
    try { saved = localStorage.getItem('cockpit:theme'); } catch { /* no storage: follow the system */ }
    const dark = saved === 'dark'
      || (saved !== 'light' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  }

  function open(projectId: string, id: string, rel: string, page = ''): void {
    if (bridge) void bridge.open({ projectId, target: homeLinkTarget(id, rel, page) });
  }

  const shortTitle = (title: string): string => title.split(' — ')[0].trim();

  /** One mark per thing owed, grouped by verb in the order they are drawn. */
  function owedMarks(rows: HomeOwedRow[]): HTMLElement {
    const box = make('span', 'hr-owed');
    const seen = new Map<string, number>();
    for (const row of rows) {
      const n = (seen.get(row.verb) || 0) + 1;
      seen.set(row.verb, n);
      if (n > MARKS_PER_VERB) continue;
      const what = row.id ? `${row.id} ${shortTitle(row.title)}` : row.title;
      const btn = mark(`tok g-${homeVerbGlyph(row.verb)}`, row.id ? `${row.verb}: ${what}` : what,
        () => open(row.projectId, row.id, row.rel, row.page));
      btn.append(glyph(`g-${homeVerbGlyph(row.verb)}`));
      if (row.count > 1) btn.append(String(row.count));
      box.append(btn);
    }
    for (const [verb, n] of seen) {
      if (n <= MARKS_PER_VERB) continue;
      const more = make('span', `tok-more g-${homeVerbGlyph(verb)}`, `+${n - MARKS_PER_VERB}`);
      more.title = `${n - MARKS_PER_VERB} more to ${verb.toLowerCase()}. Open the project to list them.`;
      // Beside the last mark of its own kind, not at the end of the row.
      const last = Array.from(box.querySelectorAll(`.tok.g-${homeVerbGlyph(verb)}`)).pop();
      if (last) last.after(more); else box.append(more);
    }
    return box;
  }

  function phaseBar(projectId: string, a: HomePhaseAnswers): HTMLElement {
    const box = make('span', a.focus ? 'hp is-focus' : 'hp');
    const tip = `${a.key} · ${a.title}${a.focus ? ' (in focus)' : ''}\n${a.left}\n${a.criteria}`;
    const key = mark('hp-key', tip, () => open(projectId, a.key, a.rel));
    key.textContent = a.key.replace(/^PHASE-0*/, '') || a.key;
    box.append(key);

    if (a.segments.length <= SEGMENTS_SHOWN) {
      const segs = make('span', 'hp-segs');
      for (const s of a.segments) {
        segs.append(mark(`seg seg-${s.state}`, `${s.label} (${STATE_WORD[s.state]})`,
          () => open(projectId, s.id, '')));
      }
      box.append(segs);
    } else {
      // Too many to draw one by one: the same three states, to scale.
      const count = (state: string): number => a.segments.filter((s) => s.state === state).length;
      const bar = mark('hp-bar', tip, () => open(projectId, a.key, a.rel));
      for (const state of ['done', 'now', 'next']) {
        if (count(state) === 0) continue;
        const part = make('i', `seg-${state}`);
        part.style.flexGrow = String(count(state));
        bar.append(part);
      }
      box.append(bar, make('span', 'hp-num', `${count('done')}/${a.segments.length}`));
    }

    box.append(make('span', 'hp-flag'));
    const exit = make('span', 'hp-exit');
    if (a.exit === null) {
      const dot = make('i', 'ex ex-unread');
      dot.title = a.criteria;
      exit.append(dot);
    } else {
      for (const c of a.exit) {
        const dot = make('i', c.done ? 'ex ex-done' : 'ex');
        dot.title = `${c.text} (${c.done ? 'ticked' : 'not ticked yet'})`;
        exit.append(dot);
      }
      if (a.exit.length === 0) exit.title = a.criteria;
    }
    box.append(exit);
    return box;
  }

  function projectRow(r: HomeBoardRow): HTMLElement {
    const row = make('section', r.notRead ? 'hr is-unread' : 'hr');

    const agent = make('span', `hr-agent ${AGENT_ICON[r.word]}`);
    agent.title = r.detail ? `${r.word}: ${r.detail}` : r.word;
    agent.setAttribute('role', 'img');
    agent.setAttribute('aria-label', agent.title);
    agent.append(glyph(AGENT_ICON[r.word]));

    const head = make('div', 'hr-head');
    const name = mark('hr-name', `Open ${r.project} in the cockpit`, () => open(r.projectId, '', ''));
    name.textContent = r.project;
    head.append(name);
    if (r.owed.length > 0) head.append(owedMarks(r.owed));
    row.append(agent, head);

    if (r.notRead) {
      // Named as not read, with the last count where one exists. Never
      // drawn as a project that owes nothing.
      const note = make('div', 'hr-note',
        r.owedCount === null ? 'not read' : `not read · ${r.owedCount} owed at the last check`);
      note.title = `${r.project} was not read: ${r.notRead}.`;
      row.append(note);
      return row;
    }

    if (r.phases.length > 0 || r.release) {
      const phases = make('div', 'hr-phases');
      for (const a of r.phases) phases.append(phaseBar(r.projectId, a));
      if (r.release) {
        const rel = r.release;
        const btn = mark('hp-rel',
          `Release ${rel.version} (${rel.status}): ${rel.openTests} checks still open, ${rel.toSettle} to settle.`,
          () => open(r.projectId, rel.id, rel.rel));
        // The open ring is the same mark as an unticked exit criterion:
        // this many checks still stand between the version and shipping.
        btn.append(`v${rel.version}`, make('i', 'ex'), make('b', undefined, String(rel.openTests)));
        phases.append(btn);
      }
      row.append(phases);
    }
    return row;
  }

  /** The totals are also the key: each mark, how many, and its one word. */
  function renderTotals(rows: HomeBoardRow[], projects: Array<{ notRead?: string | null }>): void {
    const list = byId('home-totals');
    list.replaceChildren();
    const totals = homeVerbTotals(rows);
    if (totals.length === 0) {
      list.append(make('li', undefined, homeOwedEmptyText(projects)));
      return;
    }
    for (const t of totals) {
      const li = make('li', `g-${t.glyph}`);
      li.append(glyph(`g-${t.glyph}`), make('b', undefined, String(t.count)), t.verb);
      list.append(li);
    }
  }

  async function refresh(): Promise<void> {
    const asof = byId('home-asof');
    const now = (): string => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    if (!bridge) {
      asof.textContent = 'only works inside the cockpit';
      return;
    }
    try {
      const [data, fleet] = await Promise.all([bridge.data(), bridge.fleet()]);
      const projects = ((data as { projects?: Parameters<typeof homeBoard>[0] })?.projects) || [];
      const fleetRows = ((fleet as { rows?: Parameters<typeof homeBoard>[1] })?.rows) || [];
      const rows = homeBoard(projects, fleetRows);
      renderTotals(rows, projects);
      const board = byId('home-board');
      board.replaceChildren();
      if (rows.length === 0) board.append(make('p', 'home-empty', 'No project was found.'));
      for (const r of rows) board.append(projectRow(r));
      asof.textContent = now();
      asof.title = `Read at ${new Date().toLocaleTimeString()}. Refreshes every ${REFRESH_MS / 1000} seconds.`;
    } catch (err) {
      // Say that the board is old; never leave it looking current.
      asof.textContent = `not refreshed at ${now()}`;
      asof.title = `Could not refresh: ${String(err)}. What is shown is older.`;
    }
  }

  applyTheme();
  byId('home-refresh').addEventListener('click', () => { void refresh(); });
  window.addEventListener('focus', () => { applyTheme(); void refresh(); });
  window.setInterval(() => { void refresh(); }, REFRESH_MS);
  void refresh();
})();
