// What the draft home window shows, as pure functions (FEAT-0160).
//
// The window has three areas: what is owed across every project, where a
// phase stands, and what each project's agent is doing. Everything that
// decides what a row says lives here, so it can be tested without a window.
//
// Like `deep-link.ts`, this file declares no imports and no exports: it is
// loaded as a plain `<script>` before home.js, so its functions are globals.
// The node suite reads the built file and evaluates it.

interface HomeOwedGroup {
  kind?: string;
  verb?: string;
  noun?: string;
  label?: string;
  count?: number;
  items?: Array<{ id?: string; title?: string; rel?: string; verb?: string; url?: string }>;
}

interface HomeOwedRow {
  workspaceId: string;
  project: string;
  projectId: string;
  verb: string;
  /** The note's ID, or '' for something owed that has no note (a push). */
  id: string;
  title: string;
  /** Path under docs/, or '' when there is no note to open. */
  rel: string;
  /** For a row with no note: the page where the act is done, such as
   *  `~history` for commits to push. '' when the sidecar names none. */
  page: string;
  /** How many things this one row stands for: 1 for a note, the number of
   *  commits for a push. The picture draws the number beside the mark. */
  count: number;
}

/** The order the list reads in: decisions first, housekeeping last. A verb
 *  the list does not know sorts after the ones it does, never out of sight. */
const HOME_VERB_ORDER = ['Decide', 'Accept', 'Approve', 'Run', 'Confirm', 'Triage', 'Push', 'Deploy'];

/** One row per thing owed that has a note. Things with no note of their own
 *  (commits to push or deploy) are one row for the whole group, carrying the
 *  group's own label: seventy-three commits are one act, not seventy-three. */
function homeOwedRows(
  ws: { workspaceId: string; project: string; projectId: string },
  groups: HomeOwedGroup[],
): HomeOwedRow[] {
  const rows: HomeOwedRow[] = [];
  for (const g of groups || []) {
    const verb = String(g.verb || '');
    const items = Array.isArray(g.items) ? g.items : [];
    const noted = items.filter((it) => it && it.rel);
    const loose = items.length - noted.length;
    for (const it of noted) {
      rows.push({
        ...ws,
        verb: String(it.verb || verb),
        id: String(it.id || ''),
        title: String(it.title || it.id || ''),
        rel: String(it.rel || ''),
        page: '',
        count: 1,
      });
    }
    const unlisted = items.length === 0 ? Number(g.count || 0) : loose;
    if (unlisted > 0) {
      const whole = noted.length === 0 && g.label;
      const page = String(items.find((it) => it && !it.rel && it.url)?.url || '');
      rows.push({
        ...ws, verb, id: '', rel: '', page: page.startsWith('~') ? page : '', count: unlisted,
        title: whole ? String(g.label) : `${verb} ${unlisted} ${String(g.noun || 'more')}`.trim(),
      });
    }
  }
  return rows;
}

/** The part of a `cockpit://` link after the project, for a row. A note ID
 *  the link parser recognises is sent as the ID, so the present window
 *  locates the note itself. Anything else is sent as its path, which a
 *  link writes from the repository root, so `docs/` goes in front. Empty
 *  means "open the project and nothing more". */
function homeLinkTarget(id: string, rel: string, page?: string): string {
  if (/^[A-Za-z]+-\d+$/.test(id || '')) return id.toUpperCase();
  const dotted = (p: string): boolean => p.split('/').some((seg) => seg === '..' || seg === '.');
  if (rel) return dotted(rel) ? '' : `docs/${rel.replace(/^\/+/, '')}`;
  // No note: one of the present window's own pages, which all start with `~`.
  if (page && page.startsWith('~') && !dotted(page)) return page;
  return '';
}

function homeSortOwed(rows: HomeOwedRow[]): HomeOwedRow[] {
  const rank = (v: string): number => {
    const i = HOME_VERB_ORDER.indexOf(v);
    return i === -1 ? HOME_VERB_ORDER.length : i;
  };
  return rows.slice().sort((a, b) =>
    rank(a.verb) - rank(b.verb)
    || a.project.localeCompare(b.project)
    || a.id.localeCompare(b.id));
}

interface HomePhaseIn {
  key?: string;
  title?: string;
  status?: string | null;
  rel?: string;
  tasks?: { done?: number; in_progress?: number; backlog?: number };
  waiting?: number;
  features?: Array<{ id?: string; title?: string; status?: string; bucket?: string }>;
  /** Exit criteria. Null or absent means they were not read. */
  exit?: Array<{ text?: string; done?: boolean }> | null;
  focus?: boolean;
}

interface HomePhaseAnswers {
  key: string;
  title: string;
  status: string;
  rel: string;
  done: number;
  now: Array<{ id: string; label: string }>;
  next: Array<{ id: string; label: string }>;
  /** The open work, as one sentence. */
  left: string;
  /** What the phase's own exit criteria say, as one sentence. */
  criteria: string;
  /** The exit criteria not yet ticked: what still stands between the phase
   *  and finished. */
  stands: string[];
  focus: boolean;
  /** One mark per feature for the picture, in reading order: finished,
   *  in progress, not started. */
  segments: Array<{ id: string; label: string; state: 'done' | 'now' | 'next' }>;
  /** One mark per exit criterion. Null when they were not read. */
  exit: Array<{ text: string; done: boolean }> | null;
  tasks: { done: number; now: number; next: number };
}

/** The phases worth showing first: the active ones. A planned phase is
 *  work nobody has started, so it is counted, not listed. */
function homeActivePhases(phases: HomePhaseIn[]): HomePhaseIn[] {
  return (phases || []).filter((p) => p && p.status === 'active');
}

function homePlannedCount(phases: HomePhaseIn[]): number {
  return (phases || []).filter((p) => p && p.status === 'planned' && p.key !== 'PHASE-999').length;
}

const homeShort = (id: string | undefined, title: string | undefined): string => {
  // A title is often "Name — the long explanation". The name is enough here.
  const name = String(title || '').split(' — ')[0].split(' -- ')[0].trim();
  return id ? `${id} ${name}`.trim() : name;
};

/** The four questions for one phase: what is done, what is happening now,
 *  what is next, and what still stands between it and finished. */
function homePhaseAnswers(p: HomePhaseIn): HomePhaseAnswers {
  const features = Array.isArray(p.features) ? p.features : [];
  const inBucket = (b: string) => features.filter((f) => f.bucket === b);
  const open = (p.tasks?.in_progress || 0) + (p.tasks?.backlog || 0);
  const waiting = p.waiting || 0;
  let left: string;
  if (open === 0 && inBucket('in_progress').length === 0 && inBucket('backlog').length === 0) {
    left = 'No task or feature is open.';
  } else if (open === 0) {
    // Features are open and nobody has written their tasks: "0 tasks open"
    // would read as nearly finished, which is the opposite of the truth.
    left = 'Features are still open, and no task is written for them yet.';
  } else {
    const parts = [`${open} ${open === 1 ? 'task' : 'tasks'} still open`];
    if (waiting > 0) parts.push(`${waiting} waiting on you`);
    left = parts.join(', ') + '.';
  }
  // The exit criteria are the phase's own definition of finished. Three
  // different facts must not read alike: not read, none written, all ticked.
  const exit = Array.isArray(p.exit) ? p.exit : null;
  const stands = (exit || []).filter((c) => !c.done).map((c) => String(c.text || ''));
  let criteria: string;
  if (exit === null) criteria = 'Its exit criteria were not read.';
  else if (exit.length === 0) criteria = 'The phase note lists no exit criteria.';
  else if (stands.length === 0) {
    criteria = exit.length === 1 ? 'Its one exit criterion is ticked.' : `All ${exit.length} exit criteria are ticked.`;
  } else {
    criteria = `${stands.length} of ${exit.length} exit ${exit.length === 1 ? 'criterion' : 'criteria'} not ticked yet:`;
  }
  const seg = (state: 'done' | 'now' | 'next', bucket: string) => inBucket(bucket)
    .map((f) => ({ id: String(f.id || ''), label: homeShort(f.id, f.title), state }));
  return {
    segments: [...seg('done', 'done'), ...seg('now', 'in_progress'), ...seg('next', 'backlog')],
    exit: exit === null ? null : exit.map((c) => ({ text: String(c.text || ''), done: c.done === true })),
    tasks: { done: p.tasks?.done || 0, now: p.tasks?.in_progress || 0, next: p.tasks?.backlog || 0 },
    criteria,
    stands,
    focus: p.focus === true,
    key: String(p.key || ''),
    title: String(p.title || '').split(' — ')[0].trim(),
    status: String(p.status || ''),
    rel: String(p.rel || ''),
    done: inBucket('done').length,
    now: inBucket('in_progress').map((f) => ({ id: String(f.id || ''), label: homeShort(f.id, f.title) })),
    next: inBucket('backlog').map((f) => ({ id: String(f.id || ''), label: homeShort(f.id, f.title) })),
    left,
  };
}

/** What the Needs you area says when it has no row. A project that was not
 *  read is counted out loud: "nothing needs you" is only ever said about
 *  the projects somebody actually read. */
function homeOwedEmptyText(projects: Array<{ notRead?: string | null }>): string {
  const all = (projects || []).length;
  const unread = (projects || []).filter((p) => p && p.notRead).length;
  if (all === 0) return 'No project was found.';
  if (unread === all) return 'No project could be read, so nothing is known about what is owed.';
  if (unread === 0) return 'Nothing needs you.';
  const read = all - unread;
  return `Nothing needs you in the ${read} ${read === 1 ? 'project' : 'projects'} that ${read === 1 ? 'was' : 'were'} read. `
    + `${unread} ${unread === 1 ? 'was' : 'were'} not read.`;
}

type HomeAgentWord = 'working' | 'needs your answer' | 'finished its turn' | 'stuck' | 'quiet' | 'not open';

/** What a person needs to know about a session, in the shell's own states:
 *  `busy` is working, `needs-input` is blocked on an answer, `waiting` has
 *  finished its turn and sits at the prompt, `error` is stuck. Everything
 *  else is quiet. An unknown state reads as quiet, never as working: a wrong
 *  "working" hides a session that stopped. */
function homeAgentWord(state: string | null | undefined, live: boolean): HomeAgentWord {
  if (!live) return 'not open';
  switch (state) {
    case 'busy': return 'working';
    case 'needs-input': return 'needs your answer';
    case 'waiting': return 'finished its turn';
    case 'error': return 'stuck';
    default: return 'quiet';
  }
}

/** Sessions that want a person come first, then the working ones. */
function homeAgentRank(word: HomeAgentWord): number {
  return ['needs your answer', 'stuck', 'finished its turn', 'working', 'quiet', 'not open'].indexOf(word);
}

// ---- The picture (FEAT-0160, second cut) ---------------------------------
//
// Edwin, 2026-10-13, on the first cut: "It is too much text heavy instead we
// should be using diagrams or images to make this understable just by looking
// at, the text can be in the main application when opening the note." So the
// window is a board: one row per project, a mark per thing owed, a bar per
// active phase. The words live in tooltips and in the present window.

type HomeGlyph = 'decide' | 'accept' | 'approve' | 'run' | 'confirm' | 'triage' | 'push' | 'deploy' | 'other';

/** Which mark a verb is drawn with. A verb the board does not know gets the
 *  plain dot: it is still drawn, and its tooltip still names it. */
function homeVerbGlyph(verb: string): HomeGlyph {
  const key = String(verb || '').toLowerCase();
  return (['decide', 'accept', 'approve', 'run', 'confirm', 'triage', 'push', 'deploy'].includes(key)
    ? key : 'other') as HomeGlyph;
}

interface HomeBoardRow {
  workspaceId: string;
  project: string;
  projectId: string;
  word: HomeAgentWord;
  /** What the agent last said or was asked, for the tooltip. */
  detail: string;
  notRead: string | null;
  owed: HomeOwedRow[];
  /** For a project that was not read: the last background count, or null. */
  owedCount: number | null;
  phases: HomePhaseAnswers[];
  release: { id: string; version: string; status: string; rel: string; openTests: number; toSettle: number } | null;
}

/** One row per project, the ones that want a person first: by the agent's
 *  state, then by how much is owed, then by name. */
function homeBoard(
  projects: Array<{
    workspaceId: string; project: string; projectId: string; notRead?: string | null;
    owed?: HomeOwedGroup[]; owedCount?: number | null; phases?: HomePhaseIn[];
    release?: HomeBoardRow['release'];
  }>,
  fleet: Array<{ workspaceId: string; state?: string | null; live?: boolean; message?: string; lastPrompt?: string }>,
): HomeBoardRow[] {
  const rows = (projects || []).map((p): HomeBoardRow => {
    const f = (fleet || []).find((r) => r.workspaceId === p.workspaceId);
    return {
      workspaceId: p.workspaceId,
      project: p.project,
      projectId: p.projectId,
      word: f ? homeAgentWord(f.state, f.live === true) : (p.notRead ? 'not open' : 'quiet'),
      detail: String(f?.message || f?.lastPrompt || '').replace(/\s+/g, ' ').trim(),
      notRead: p.notRead || null,
      owed: homeSortOwed(homeOwedRows(
        { workspaceId: p.workspaceId, project: p.project, projectId: p.projectId }, p.owed || [])),
      owedCount: p.owedCount ?? null,
      phases: homeActivePhases(p.phases || []).map(homePhaseAnswers),
      release: p.release || null,
    };
  });
  return rows.sort((a, b) =>
    homeAgentRank(a.word) - homeAgentRank(b.word)
    || b.owed.length - a.owed.length
    || a.project.localeCompare(b.project));
}

/** How many marks of each kind are on the board, in the order they are
 *  drawn. A push counts once per project, as it is drawn once. */
function homeVerbTotals(rows: HomeBoardRow[]): Array<{ verb: string; glyph: HomeGlyph; count: number }> {
  const counts = new Map<string, number>();
  for (const r of rows || []) for (const o of r.owed) counts.set(o.verb, (counts.get(o.verb) || 0) + 1);
  const known = HOME_VERB_ORDER.filter((v) => counts.has(v));
  const extra = Array.from(counts.keys()).filter((v) => !HOME_VERB_ORDER.includes(v)).sort();
  return [...known, ...extra].map((verb) => ({ verb, glyph: homeVerbGlyph(verb), count: counts.get(verb) || 0 }));
}
