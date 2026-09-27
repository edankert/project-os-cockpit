// The release test page ([[FEAT-0155]]: TASK-0641, TASK-0642, TASK-0643).
//
// One platform's release test, drawn from the data upstream's generator
// prints (`release-test.py --json`, `TESTING.md` "The release test", rule 10)
// through `/api/cockpit/release-test`. The page works nothing out itself:
// sections, groups, numbers, start lines, setup and what changed all arrive
// in the payload. What it adds is recording results.
//
// **Results live in two places, as Edwin decided for step ticks on
// 2026-09-14 (FEAT-0150).** A tester records a result on each printed check;
// that is progress, kept in this browser per workspace. When every printed
// check that cites one test note has a result, the page writes ONE ledger
// event for that note: the most serious of its results, with their reasons.
// The ledger is the record; the browser is the place in the middle of it.
//
// Declares no imports and no exports: `renderer.ts` is loaded as a plain
// <script>, so this is loaded the same way and these become globals. The
// pure functions come first and touch no DOM, so the tests can run them from
// the built file.

interface RtExpected { text: string; tags: string[]; passed: string[] }
interface RtReadiness { kind: string; reason: string; issue: string; result: string }
interface RtCheck {
  number: number; action: string; expected: RtExpected[]; tags: string[];
  checks: string[]; preparation: boolean; start: string; start_again?: boolean;
  readiness: RtReadiness | null; timer: number; capture: string;
  compare_with: number[]; path: string;
  setup?: string; steps?: string; steps_heading?: boolean;
}
interface RtGroup { title: string; start: string; checks: RtCheck[] }
interface RtLine { change: string; title: string; text: string; short: boolean }
interface RtCapture {
  key: string; state: string; before: string; after: string; new: boolean;
  stale: string; stale_against: string;
}
interface RtScreen {
  id: string; title: string; parent: string; unresolved: boolean;
  lines: RtLine[]; captures: RtCapture[];
}
interface RtSection {
  number: number | null; name: string; slug: string; unplaced: boolean;
  count: number; owed: number; tests: string[]; bench_line: string;
  state: string; procedure: string; problems: string[];
  what_changed: RtScreen[]; nothing_changed: boolean;
  setup: { bench: string[]; before: string[]; later: Array<{ check: number; text: string }> };
  groups: RtGroup[]; omitted: number; progress: { done: number; total: number };
}
interface RtLedgerResult { result: string; reason: string; date: string }
interface RtPage {
  notes?: { total: number; owed: number };
  platform: string; release: string; version?: string; platforms?: string[];
  error: string; owed?: number; progress?: { done: number; total: number };
  notices?: string[]; warnings?: string[];
  what_changed?: {
    release: string; tag: string; problem: string; gallery: string;
    short_lines_problem: string; undeclared: string[]; any: boolean;
    screens: RtScreen[];
  };
  sections: RtSection[];
  results: Record<string, RtLedgerResult>;
}
interface RtMark { result: string; reason: string; at: string; note?: string }
type RtMarks = Record<string, RtMark>;

/** The seven results a ledger stores, in the order the page offers them. */
const RT_RESULTS = ['pass', 'fail', 'partial', 'question', 'blocked', 'na', 'excused'];
const RT_LABELS: Record<string, string> = {
  pass: 'Pass', fail: 'Fail', partial: 'Partial', question: 'Question',
  blocked: 'Blocked', na: 'N/A', excused: 'Excused',
};
/** What each result under "More" means, in the approved example's words. */
const RT_MORE: Array<[string, string]> = [
  ['partial', 'Some parts hold, some do not'],
  ['question', 'The check itself is unclear'],
  ['blocked', 'Cannot run it right now'],
  ['na', 'Does not exist on this platform'],
  ['excused', 'Skipped this release, by decision'],
];
/** How serious a result is, for the one result a test note gets from the
 *  results of its printed checks. A question outranks everything: nobody can
 *  say what the check expects. N/A ranks below pass, so a check that holds
 *  where it exists and does not exist elsewhere passes. */
const RT_RANK: Record<string, number> = {
  na: 0, pass: 1, excused: 2, partial: 3, blocked: 4, fail: 5, question: 6,
};

/** The most serious of several results. */
function rtWorst(results: string[]): string {
  let worst = '';
  for (const result of results) {
    if (!worst || (RT_RANK[result] ?? -1) > (RT_RANK[worst] ?? -1)) worst = result;
  }
  return worst;
}

/** Where a printed check's result is kept in this browser.
 *
 *  **By content, not by number.** A check's number depends on what the
 *  release still owes, so the same observation can be check 13 today and
 *  check 11 tomorrow. Its tags and its action identify it; a changed action
 *  or a changed set of tags is a different observation, and does not inherit
 *  a result. */
function rtCheckKey(page: RtPage, section: RtSection, check: RtCheck): string {
  return [page.release, page.platform, section.slug,
    [...rtAllTags(check)].sort().join(' '), check.action].join('|');
}

/** Every tag a printed check carries, owed or already passed. */
function rtAllTags(check: RtCheck): Set<string> {
  const out = new Set<string>(check.tags);
  for (const line of check.expected) {
    for (const tag of line.tags) out.add(tag);
    for (const tag of line.passed || []) out.add(tag);
  }
  return out;
}

/** Every printed check that records a result, with its section. */
function rtPrinted(page: RtPage): Array<{ section: RtSection; check: RtCheck }> {
  const out: Array<{ section: RtSection; check: RtCheck }> = [];
  for (const section of page.sections) {
    for (const group of section.groups) {
      for (const check of group.checks) {
        if (check.checks.length) out.push({ section, check });
      }
    }
  }
  return out;
}

/** The result each test note is ready to have written to the ledger.
 *
 *  A note is ready when every printed check citing it has a result in this
 *  browser, and every result but Pass has a reason. Its result is the most
 *  serious of theirs, and its reason names each printed check that said
 *  something. A note that is not ready is absent. */
function rtNoteResults(page: RtPage, marks: RtMarks): Record<string, RtMark> {
  const byNote = new Map<string, Array<{ check: RtCheck; mark: RtMark | undefined }>>();
  for (const { section, check } of rtPrinted(page)) {
    const mark = marks[rtCheckKey(page, section, check)];
    for (const note of check.checks) {
      if (!byNote.has(note)) byNote.set(note, []);
      byNote.get(note)!.push({ check, mark });
    }
  }
  const out: Record<string, RtMark> = {};
  for (const [note, rows] of byNote) {
    if (!rows.every((row) => row.mark
      && (row.mark.result === 'pass' || row.mark.reason.trim()))) continue;
    const result = rtWorst(rows.map((row) => row.mark!.result));
    const reasons = rows
      .filter((row) => row.mark!.result !== 'pass' && row.mark!.reason.trim())
      .map((row) => `check ${row.check.number}: ${row.mark!.reason.trim()}`);
    out[note] = { result, reason: reasons.join('; '), at: '' };
  }
  return out;
}

/** What one printed check shows: its own result here, or the ledger's.
 *
 *  The ledger's result shows when this browser has none for the check and
 *  every test note it cites has one: recorded on another machine, or before
 *  this page existed. */
function rtCheckState(page: RtPage, section: RtSection, check: RtCheck,
                      marks: RtMarks): { result: string; reason: string; source: string } {
  const mark = marks[rtCheckKey(page, section, check)];
  if (mark) return { result: mark.result, reason: mark.reason, source: 'here' };
  if (check.checks.length && check.checks.every((note) => page.results[note])) {
    const results = check.checks.map((note) => page.results[note]);
    return {
      result: rtWorst(results.map((r) => r.result)),
      reason: results.map((r) => r.reason).filter(Boolean).join('; '),
      source: 'ledger',
    };
  }
  return { result: '', reason: '', source: '' };
}

/** A section's counts: printed checks with a result, of those that take one. */
function rtSectionTally(page: RtPage, section: RtSection, marks: RtMarks):
    { done: number; total: number; counts: Record<string, number> } {
  const counts: Record<string, number> = {};
  let done = 0;
  let total = 0;
  for (const group of section.groups) {
    for (const check of group.checks) {
      if (!check.checks.length) continue;
      total += 1;
      const state = rtCheckState(page, section, check, marks);
      if (state.result) {
        done += 1;
        counts[state.result] = (counts[state.result] || 0) + 1;
      }
    }
  }
  return { done, total, counts };
}

/** What asks for the owner: a result that is not a pass or an excusal, a
 *  declared readiness problem with no result yet, and a section whose
 *  procedure the validator refused.
 *
 *  **One entry per reason.** Several printed checks share a test note, so a
 *  Fail on the note shows on each of them with the same reason; those are
 *  one entry naming all their checks (Edwin's review, 2026-09-27). */
function rtNeedsYou(page: RtPage, marks: RtMarks):
    Array<{ section: RtSection; check: RtCheck | null; checks: number[]; result: string; text: string }> {
  const out: Array<{ section: RtSection; check: RtCheck | null; checks: number[]; result: string; text: string }> = [];
  const seen = new Map<string, { checks: number[] }>();
  for (const section of page.sections) {
    if (section.problems.length) {
      out.push({ section, check: null, checks: [], result: 'question',
        text: 'Its procedure no longer matches what the release owes, so its checks are printed one by one.' });
    }
    for (const group of section.groups) {
      for (const check of group.checks) {
        const state = rtCheckState(page, section, check, marks);
        let entry: { result: string; text: string } | null = null;
        if (['fail', 'question', 'blocked', 'partial'].includes(state.result)) {
          entry = { result: state.result, text: state.reason || check.action };
        } else if (!state.result && check.readiness) {
          //: A declared decision or missing setup asks for the owner before
          //: anyone can test the check ([[TASK-0642]]).
          entry = { result: check.readiness.result,
            text: `${check.readiness.reason}${check.readiness.issue ? ` (${check.readiness.issue})` : ''}` };
        }
        if (!entry) continue;
        const key = `${section.slug}|${entry.result}|${entry.text}`;
        const had = seen.get(key);
        if (had) { had.checks.push(check.number); continue; }
        const row = { section, check, checks: [check.number], ...entry };
        seen.set(key, row);
        out.push(row);
      }
    }
  }
  return out;
}

/** Where "Continue where you stopped" goes: the first check with no result,
 *  in the section last opened, else in the first section that has one. */
function rtContinue(page: RtPage, marks: RtMarks, lastSlug: string):
    { section: RtSection; check: RtCheck } | null {
  const order = [...page.sections];
  const last = order.findIndex((s) => s.slug === lastSlug);
  if (last > 0) order.unshift(...order.splice(last, 1));
  for (const section of order) {
    for (const group of section.groups) {
      for (const check of group.checks) {
        if (check.checks.length && !rtCheckState(page, section, check, marks).result) {
          return { section, check };
        }
      }
    }
  }
  return null;
}

/** Results the walk page saved, carried onto this page's checks.
 *
 *  The walk page kept a step's result under `release|platform|sitting|step
 *  content`, and the content held the step's tags. A section has the name
 *  its sitting had, so a saved result moves to the printed check in the same
 *  section with exactly the same tags. One that matches no check, or more
 *  than one, is dropped: it describes a step that no longer exists. Returns
 *  the new results and the old keys it read. */
function rtCarryWalkMarks(page: RtPage, old: Record<string, { verdict?: string; reason?: string }>):
    { marks: RtMarks; used: string[] } {
  const marks: RtMarks = {};
  const used: string[] = [];
  for (const [key, value] of Object.entries(old)) {
    const parts = key.split('|');
    if (parts.length < 4 || parts[0] !== page.release || parts[1] !== page.platform) continue;
    used.push(key);
    const sitting = parts[2];
    let tags: string[] = [];
    try {
      const sig = JSON.parse(parts.slice(3).join('|')) as { lines?: unknown[] };
      for (const line of sig.lines || []) {
        const pairs = Array.isArray(line) ? line[2] : [];
        for (const pair of Array.isArray(pairs) ? pairs : []) {
          if (Array.isArray(pair) && pair[0]) {
            tags.push(pair[1] ? `${pair[0]}.${pair[1]}` : String(pair[0]));
          }
        }
      }
    } catch { continue; }
    tags = [...new Set(tags)].sort();
    const result = String(value?.verdict || '');
    if (!tags.length || !RT_RESULTS.includes(result)) continue;
    const section = page.sections.find((s) => s.name === sitting);
    if (!section) continue;
    const matches = section.groups.flatMap((g) => g.checks).filter(
      (check) => [...rtAllTags(check)].sort().join(' ') === tags.join(' '));
    if (matches.length !== 1) continue;
    marks[rtCheckKey(page, section, matches[0])] = {
      result, reason: String(value?.reason || ''), at: '',
    };
  }
  return { marks, used };
}

/** The walk page's five browser storage keys, and the names they have now.
 *  Each is moved once, then the old key is removed ([[TASK-0639]]). */
const RT_RENAMED_KEYS: Array<[string, string]> = [
  ['walk-focus', 'release-test-focus'],
  ['walk-completed', 'release-test-completed'],
  ['walk-place', 'release-test-place'],
  ['walk-steps', 'release-test-walk-steps'],
  ['walk-evidence', 'release-test-evidence'],
];

/** Move each old key's value under its new name, once. A value already under
 *  the new name wins. The walk page's step results stay in
 *  `release-test-walk-steps` until `rtCarryWalkMarks` has carried them. */
function rtMigrateStorage(store: Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>,
                          workspaceId: string): string[] {
  const moved: string[] = [];
  for (const [from, to] of RT_RENAMED_KEYS) {
    const oldKey = `cockpit:${from}:${workspaceId}`;
    const newKey = `cockpit:${to}:${workspaceId}`;
    const value = store.getItem(oldKey);
    if (value === null) continue;
    if (store.getItem(newKey) === null) {
      //: A saved place is an address, and the old address is `~walk`.
      store.setItem(newKey, from === 'walk-place'
        ? value.replace(/^~walk(?=\/|$)/, '~release-test') : value);
    }
    store.removeItem(oldKey);
    moved.push(from);
  }
  return moved;
}

/** `~walk` and `~walk/<platform>`, the old addresses, as the new ones. */
function rtAddressFor(rel: string): string {
  return rel.replace(/^~walk(?=\/|$)/, '~release-test');
}

// ------------------------------------------------------------------- storage

function rtMarksKey(workspaceId: string): string {
  return `cockpit:release-test-results:${workspaceId}`;
}
function rtPlaceKey(workspaceId: string): string {
  return `cockpit:release-test-place:${workspaceId}`;
}

function rtLoadMarks(): RtMarks {
  if (!activeId) return {};
  try {
    const parsed = JSON.parse(localStorage.getItem(rtMarksKey(activeId)) || '{}') as unknown;
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {};
    const out: RtMarks = {};
    for (const [key, value] of Object.entries(parsed as Record<string, RtMark>)) {
      if (value && RT_RESULTS.includes(value.result)) {
        out[key] = { result: value.result, reason: String(value.reason || ''), at: String(value.at || '') };
      }
    }
    return out;
  } catch { return {}; }
}

function rtSaveMarks(marks: RtMarks): boolean {
  if (!activeId) return false;
  try {
    localStorage.setItem(rtMarksKey(activeId), JSON.stringify(marks));
    return true;
  } catch { return false; }
}

/** Once per page load: rename the walk page's keys, and carry its saved step
 *  results onto this page's checks for this release and platform. */
function rtAdoptSavedState(page: RtPage): void {
  if (!activeId) return;
  try {
    rtMigrateStorage(localStorage, activeId);
    const key = `cockpit:release-test-walk-steps:${activeId}`;
    const raw = localStorage.getItem(key);
    if (!raw) return;
    const old = JSON.parse(raw) as Record<string, { verdict?: string; reason?: string }>;
    const { marks, used } = rtCarryWalkMarks(page, old);
    const current = rtLoadMarks();
    for (const [k, v] of Object.entries(marks)) if (!current[k]) current[k] = v;
    rtSaveMarks(current);
    for (const k of used) delete old[k];
    if (Object.keys(old).length) localStorage.setItem(key, JSON.stringify(old));
    else localStorage.removeItem(key);
  } catch { /* browser storage unavailable: nothing to carry */ }
}

// ---------------------------------------------------------------------- page

let rtPage: RtPage | null = null;
/** Which sections' Setup the tester opened, for this session. */
const rtSetupOpen = new Set<string>();

/** `~release-test[/<platform>[/<section>]]`. */
async function renderReleaseTestPage(platform: string, slug: string): Promise<boolean> {
  if (!sidecarBaseUrl) return false;
  const params = new URLSearchParams();
  if (platform) params.set('platform', platform);
  let page: RtPage;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/release-test?${params}`);
    const body = await resp.json().catch(() => null) as (RtPage & { error?: string }) | null;
    if (!resp.ok || !body) {
      rtShow(rtNotice('release-test-refusal',
        `No release test for ${platform || 'this repository'}: ${body?.error || 'the sidecar did not answer'}.`));
      return true;
    }
    page = body;
  } catch { return false; }
  rtPage = page;
  if (Array.isArray(page.platforms)) ledgerPlatforms = page.platforms;
  if (page.error) {
    rtShow(rtNotice('release-test-refusal', page.error));
    return true;
  }
  rtAdoptSavedState(page);
  if (currentNavMode !== 'tests') {
    //: The landing suppression `renderChecksPage` documents (ISS-0193):
    //: switching views would otherwise land Tests on its own first page.
    suppressLandingOnce = true;
    setNavMode('tests');
  }
  const section = slug ? page.sections.find((s) => s.slug === slug) : undefined;
  if (slug && !section) {
    rtShow(rtNotice('release-test-refusal',
      `This release test has no section "${slug}" on ${page.platform}. It owes nothing there now, or the section was renamed.`));
    return true;
  }
  if (section && activeId) {
    try { localStorage.setItem(rtPlaceKey(activeId), section.slug); } catch { /* storage off */ }
  }
  rtShow(section ? rtBuildSection(page, section) : rtBuildOverview(page));
  rtRefreshPane(page, rtLoadMarks());
  return true;
}

/** The Tests pane's rows for this platform, redrawn from the results here.
 *
 *  The pane is built by the server from the ledger, which hears of a test
 *  note only when all its printed checks have a result. So the rows for the
 *  platform being tested are updated here after every result, and the pane
 *  and the page never disagree ([[TASK-0641]], [[TASK-0643]]). */
function rtRefreshPane(page: RtPage, marks: RtMarks): void {
  let done = 0;
  let total = 0;
  for (const section of page.sections) {
    const t = rtSectionTally(page, section, marks);
    done += t.done;
    total += t.total;
    const li = document.querySelector<HTMLElement>(
      `li[data-rel="${CSS.escape(rtAddress(page, section))}"]`);
    if (!li) continue;
    const dot = li.querySelector('.rt-dot');
    if (dot) dot.className = `rt-dot ${rtDotState(t)}`;
    rtSetNavBar(li, t.done, t.total);
  }
  const row = document.querySelector<HTMLElement>(`li[data-rel="${CSS.escape(rtAddress(page))}"]`);
  if (row) {
    rtSetNavBar(row, done, total);
    rtSetNavNeeds(row, rtNeedsYou(page, marks).length);
    //: The platform being read always shows its sections in the pane.
    const kids = row.querySelector<HTMLElement>(':scope > .nav-children');
    if (kids?.hidden) {
      kids.hidden = false;
      row.querySelector(':scope > .nav-item .nav-row-toggle')?.setAttribute('aria-expanded', 'true');
    }
  }
}

/** The platform row's count of what the overview's Needs you lists
 *  ([[TASK-0642]]). The pane's own "Needs you" group stays the badge's list of
 *  owed test notes; a result on a printed check lives in this browser until
 *  its test note is complete, so the server cannot count it. The count sits
 *  on the platform row instead, in the badge's shape, and goes at zero. */
function rtSetNavNeeds(li: HTMLElement, n: number): void {
  const item = li.querySelector<HTMLElement>(':scope > .nav-item');
  if (!item) return;
  let badge = item.querySelector<HTMLElement>(':scope .rt-nav-needs');
  if (!n) { badge?.remove(); return; }
  if (!badge) {
    badge = rtEl('span', 'mode-badge rt-nav-needs');
    const title = item.querySelector('.nav-title');
    if (title) title.after(badge); else item.appendChild(badge);
  }
  badge.textContent = String(n);
  badge.title = `${n} need${n === 1 ? 's' : ''} you: open the overview's Needs you list`;
}

/** Empty, half, full, or red when a result there needs the owner. */
function rtDotState(t: { done: number; total: number; counts: Record<string, number> }): string {
  if (t.counts.fail || t.counts.question || t.counts.blocked) return 'bad';
  if (t.total && t.done === t.total) return 'done';
  return t.done ? 'part' : 'empty';
}

function rtSetNavBar(li: HTMLElement, done: number, total: number): void {
  const fill = li.querySelector<HTMLElement>(':scope > .nav-item .nav-row-progress i, :scope > .nav-row-progress i');
  if (fill) fill.style.width = `${total ? Math.round(100 * done / total) : 0}%`;
  const bar = fill?.parentElement;
  if (bar) bar.title = `${done} of ${total} have a result`;
  //: The row's title carries its count, "Android · 25/355"; keep it true.
  const title = li.querySelector<HTMLElement>(':scope > .nav-item .nav-title');
  if (title) title.textContent = title.textContent!.replace(/ · \d+\/\d+( checks)?$/, (_m, unit) => ` · ${done}/${total}${unit || ''}`);
}

/** Scroll a check into view and focus its first result button, as Continue
 *  and Needs you do ([[TASK-0642]]). */
function rtFocusCheck(id: string): void {
  const row = document.getElementById(id);
  if (!row) return;
  row.scrollIntoView({ block: 'center' });
  row.querySelector<HTMLButtonElement>('.rt-marks button')?.focus({ preventScroll: true });
}

function rtShow(node: HTMLElement): void {
  clearDocPageClasses();
  rightPaneContent.replaceChildren();
  docView.replaceChildren(node);
  docView.hidden = false;
  placeholder.hidden = true;
}

function rtEl<K extends keyof HTMLElementTagNameMap>(
  tag: K, cls = '', text = ''): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text) node.textContent = text;
  return node;
}

/** Inline Markdown a check note uses: `**bold**`, `*italic*` and `code`. */
function rtInline(text: string): DocumentFragment {
  const out = document.createDocumentFragment();
  const re = /(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`)/g;
  let at = 0;
  for (const m of text.matchAll(re)) {
    if ((m.index ?? 0) > at) out.appendChild(document.createTextNode(text.slice(at, m.index)));
    const token = m[0];
    if (token.startsWith('**')) out.appendChild(rtEl('b', '', token.slice(2, -2)));
    else if (token.startsWith('`')) out.appendChild(rtEl('code', '', token.slice(1, -1)));
    else out.appendChild(rtEl('i', '', token.slice(1, -1)));
    at = (m.index ?? 0) + token.length;
  }
  if (at < text.length) out.appendChild(document.createTextNode(text.slice(at)));
  return out;
}

function rtNotice(cls: string, text: string): HTMLElement {
  const wrap = rtEl('div', `rt-page ${cls}`);
  wrap.appendChild(rtEl('p', 'rt-notice', text));
  return wrap;
}

function rtAddress(page: RtPage, section?: RtSection): string {
  const base = `~release-test/${encodeURIComponent(page.platform)}`;
  return section ? `${base}/${encodeURIComponent(section.slug)}` : base;
}

function rtPlatformName(platform: string): string {
  return ({ ios: 'iOS', macos: 'macOS', ipados: 'iPadOS' } as Record<string, string>)[platform]
    || (platform.charAt(0).toUpperCase() + platform.slice(1));
}

function rtEyebrow(page: RtPage, extra = ''): HTMLElement {
  const bits = ['Release test', rtPlatformName(page.platform)];
  if (page.version) bits.push(`v${page.version}`);
  if (extra) bits.push(extra);
  return rtEl('span', 'rt-eyebrow', bits.join(' · '));
}

function rtBar(done: number, total: number): HTMLElement {
  const bar = rtEl('span', 'rt-bar');
  const fill = rtEl('i');
  fill.style.width = `${total ? (100 * done / total) : 0}%`;
  bar.appendChild(fill);
  return bar;
}

function rtTally(counts: Record<string, number>): HTMLElement {
  const tally = rtEl('div', 'rt-tally');
  for (const result of RT_RESULTS) {
    if (!counts[result]) continue;
    const chip = rtEl('span', '', `${counts[result]} ${RT_LABELS[result]}`);
    chip.dataset.mark = result;
    tally.appendChild(chip);
  }
  return tally;
}

// ------------------------------------------------------------ the overview

function rtBuildOverview(page: RtPage): HTMLElement {
  const marks = rtLoadMarks();
  const wrap = rtEl('div', 'rt-page rt-overview');
  const head = rtEl('header', 'rt-head');
  head.appendChild(rtEyebrow(page));
  head.appendChild(rtEl('h1', '', `Test ${page.version ? `v${page.version}` : page.release} on ${rtPlatformName(page.platform)}`));
  let done = 0;
  let total = 0;
  const counts: Record<string, number> = {};
  const tallies = new Map<string, ReturnType<typeof rtSectionTally>>();
  for (const section of page.sections) {
    const t = rtSectionTally(page, section, marks);
    tallies.set(section.slug, t);
    done += t.done;
    total += t.total;
    for (const [k, v] of Object.entries(t.counts)) counts[k] = (counts[k] || 0) + v;
  }
  const progress = rtEl('div', 'rt-progress');
  progress.appendChild(rtEl('span', '', `${done} of ${total} checks have a result`));
  //: Split by result colour, as the approved example is ([[TASK-0642]]).
  const bar = rtEl('span', 'rt-bar rt-bar-split');
  for (const result of RT_RESULTS) {
    if (!counts[result]) continue;
    const part = rtEl('i');
    part.dataset.mark = result;
    part.style.width = `${total ? (100 * counts[result] / total) : 0}%`;
    part.title = `${counts[result]} ${RT_LABELS[result]}`;
    bar.appendChild(part);
  }
  progress.appendChild(bar);
  head.appendChild(progress);
  head.appendChild(rtTally(counts));
  if (page.notes) {
    //: The acceptance page counts test notes, not printed checks, so the
    //: number it shows is given here too, under its own name.
    head.appendChild(rtEl('p', 'rt-legend',
      `${page.notes.owed} of ${page.notes.total} test notes still owed. A test note has one or more of the checks below; it stops being owed when every one of its checks has a result other than Fail, Question or Blocked. The Acceptance tests page counts the same test notes, plus automated ones.`));
  }
  wrap.appendChild(head);

  let last = '';
  try { last = (activeId && localStorage.getItem(rtPlaceKey(activeId))) || ''; } catch { /* storage off */ }
  const next = rtContinue(page, marks, last);
  const cont = rtEl('button', 'rt-continue');
  cont.type = 'button';
  if (next) {
    cont.appendChild(rtEl('small', '', done ? 'Continue where you stopped' : 'Start'));
    cont.appendChild(rtEl('b', '', next.section.name));
    cont.appendChild(rtEl('span', 'rt-next', `Check ${next.check.number}: ${next.check.action.replace(/\*\*/g, '')}`));
    cont.appendChild(rtEl('span', 'rt-arrow', '→'));
    cont.addEventListener('click', () => {
      void navigateTo(rtAddress(page, next.section) + `#rt-check-${next.check.number}`);
    });
  }
  //: When every check has a result there is nowhere to continue to, and the
  //: button is hidden rather than disabled ([[TASK-0642]]).
  if (next) wrap.appendChild(cont);

  const needs = rtNeedsYou(page, marks);
  if (needs.length) {
    const sec = rtEl('section', 'rt-block');
    sec.appendChild(rtEl('h2', '', 'Needs you'));
    const list = rtEl('div', 'rt-attention');
    for (const item of needs) {
      const row = rtEl('button', 'rt-att');
      row.type = 'button';
      const kind = rtEl('span', 'rt-kind', RT_LABELS[item.result] || item.result);
      kind.dataset.mark = item.result;
      row.appendChild(kind);
      row.appendChild(rtEl('span', 'rt-att-text', item.text.replace(/\*\*/g, '')));
      row.appendChild(rtEl('span', 'rt-where', !item.check ? item.section.name
        : `${item.section.name} · ${item.checks.length > 1 ? 'checks' : 'check'} ${item.checks.join(', ')}`));
      row.addEventListener('click', () => {
        void navigateTo(rtAddress(page, item.section)
          + (item.check ? `#rt-check-${item.check.number}` : ''));
      });
      list.appendChild(row);
    }
    sec.appendChild(list);
    wrap.appendChild(sec);
  }

  const secs = rtEl('section', 'rt-block');
  secs.appendChild(rtEl('h2', '', 'Sections'));
  secs.appendChild(rtEl('p', 'rt-legend', 'Pick any section. The line under each name is what it needs on the bench.'));
  const list = rtEl('div', 'rt-sections');
  for (const section of page.sections) {
    const t = tallies.get(section.slug)!;
    const row = rtEl('button', 'rt-sec');
    row.type = 'button';
    const dot = rtEl('span', 'rt-dot');
    if (t.total && t.done === t.total) dot.classList.add(t.counts.fail ? 'bad' : 'done');
    else if (t.done) dot.classList.add('part');
    row.appendChild(dot);
    row.appendChild(rtEl('span', 'rt-name', section.name));
    row.appendChild(rtBar(t.done, t.total));
    row.appendChild(rtEl('span', 'rt-n', `${t.done}/${t.total}`));
    row.appendChild(rtEl('span', 'rt-bench', section.bench_line || 'Nothing extra'));
    row.addEventListener('click', () => { void navigateTo(rtAddress(page, section)); });
    list.appendChild(row);
  }
  secs.appendChild(list);
  wrap.appendChild(secs);

  const changed = page.what_changed;
  if (changed) {
    const sec = rtEl('section', 'rt-block');
    sec.appendChild(rtEl('h2', '', `What changed on ${rtPlatformName(page.platform)}`));
    if (changed.problem) sec.appendChild(rtEl('p', 'rt-warn', `No release to compare against: ${changed.problem}.`));
    else if (changed.tag) sec.appendChild(rtEl('p', 'rt-legend', `Compared against ${changed.release || 'the last release'}, tagged ${changed.tag}. Each section starts with the changes to its own screens.`));
    if (changed.short_lines_problem) sec.appendChild(rtEl('p', 'rt-legend', `Short lines not used: ${changed.short_lines_problem}.`));
    if (changed.undeclared.length) sec.appendChild(rtEl('p', 'rt-legend', `Listed on every platform, because they declare no platforms: ${changed.undeclared.join(', ')}.`));
    if (changed.screens.length) {
      sec.appendChild(rtEl('p', 'rt-legend', 'No section tests these changed screens. Open them and look at them too:'));
      sec.appendChild(rtBuildScreens(changed.screens));
    }
    wrap.appendChild(sec);
  }
  for (const text of [...(page.notices || []), ...(page.warnings || [])]) {
    wrap.appendChild(rtEl('p', 'rt-legend', text));
  }
  return wrap;
}

// ---------------------------------------------------------- what changed

function rtCaptureSrc(rel: string): string {
  const inside = rel.replace(/^docs\//, '');
  if (!inside || !sidecarBaseUrl) return '';
  return `${sidecarBaseUrl}/framed/${inside.split('/').map(encodeURIComponent).join('/')}`;
}

function rtBuildScreens(screens: RtScreen[]): HTMLElement {
  const wrap = rtEl('div', 'rt-changes');
  for (const screen of screens) {
    const card = rtEl('div', screen.parent ? 'rt-screen rt-child' : 'rt-screen');
    card.appendChild(rtEl('h3', '', screen.title));
    if (screen.unresolved) card.appendChild(rtEl('p', 'rt-warn', 'No surface note carries this id, so nobody can tell which screen to open.'));
    if (screen.lines.length) {
      const ul = rtEl('ul');
      for (const line of screen.lines) {
        const li = rtEl('li');
        li.appendChild(rtInline(line.text || 'That change names this screen and says nothing about it.'));
        li.title = line.title || line.change;
        ul.appendChild(li);
      }
      card.appendChild(ul);
    }
    const shots = rtEl('div', 'rt-shots');
    for (const capture of screen.captures) {
      for (const [src, label, cls] of [
        [capture.before, 'Last release', 'before'],
        [capture.after, capture.new ? 'New' : (capture.stale ? `Captured ${capture.stale}` : 'Now'),
          capture.new ? 'new' : (capture.stale ? 'stale' : 'now')],
      ] as Array<[string, string, string]>) {
        if (!src) continue;
        const fig = rtEl('figure');
        const open = rtEl('button', 'rt-shot');
        open.type = 'button';
        const img = rtEl('img');
        img.src = rtCaptureSrc(src);
        img.alt = `${screen.title}, ${label.toLowerCase()}`;
        img.loading = 'lazy';
        open.appendChild(img);
        open.addEventListener('click', () => rtEnlarge(img.src, `${screen.title} · ${capture.state || capture.key} · ${label}`));
        fig.appendChild(open);
        const cap = rtEl('figcaption');
        cap.appendChild(rtEl('span', `rt-tag ${cls}`, label));
        cap.appendChild(document.createTextNode(` ${capture.state || capture.key}`));
        fig.appendChild(cap);
        shots.appendChild(fig);
      }
      if (capture.stale) {
        card.appendChild(rtEl('p', 'rt-stale',
          `The picture ${capture.key} was captured on ${capture.stale}, before ${capture.stale_against}, so it cannot show it. Capture it again.`));
      }
    }
    if (shots.childElementCount) card.appendChild(shots);
    wrap.appendChild(card);
  }
  return wrap;
}

/** One screenshot, enlarged with its caption. Escape or a click closes it. */
function rtEnlarge(src: string, caption: string): void {
  const dialog = rtEl('dialog', 'rt-enlarged');
  const img = rtEl('img');
  img.src = src;
  img.alt = caption;
  dialog.appendChild(img);
  dialog.appendChild(rtEl('p', '', caption));
  dialog.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => dialog.remove());
  document.body.appendChild(dialog);
  dialog.showModal();
}

// -------------------------------------------------------------- a section

function rtBuildSection(page: RtPage, section: RtSection): HTMLElement {
  const marks = rtLoadMarks();
  const wrap = rtEl('div', 'rt-page rt-section');
  const named = page.sections.filter((s) => !s.unplaced).length;
  const head = rtEl('header', 'rt-head');
  head.appendChild(rtEyebrow(page, section.number ? `Section ${section.number} of ${named}` : 'Unplaced'));
  head.appendChild(rtEl('h1', '', section.name));
  const meta = rtEl('div', 'rt-meta');
  meta.appendChild(rtEl('span', '', `${section.count} checks`));
  meta.appendChild(rtEl('span', '', `${section.owed} test ${section.owed === 1 ? 'note' : 'notes'}`));
  if (section.bench_line) meta.appendChild(rtEl('span', '', section.bench_line));
  head.appendChild(meta);
  const back = rtEl('button', 'rt-link', `← ${rtPlatformName(page.platform)} overview`);
  back.type = 'button';
  back.addEventListener('click', () => { void navigateTo(rtAddress(page)); });
  head.appendChild(back);
  wrap.appendChild(head);

  if (section.what_changed.length) {
    const sec = rtEl('section', 'rt-block');
    sec.appendChild(rtEl('h2', '', page.what_changed?.tag
      ? `What changed since ${page.what_changed.tag}` : 'What changed'));
    sec.appendChild(rtBuildScreens(section.what_changed));
    wrap.appendChild(sec);
  } else if (section.nothing_changed) {
    wrap.appendChild(rtEl('p', 'rt-legend', 'Nothing changed on the screens this section tests.'));
  }

  const setup = section.setup;
  if (setup.bench.length || setup.before.length || setup.later.length) {
    const details = rtEl('details', 'rt-setup');
    //: Folded by default ([[TASK-0643]]); once opened it stays open while the
    //: page is redrawn after a result, so the page does not jump.
    details.open = rtSetupOpen.has(`${page.platform}|${section.slug}`);
    details.addEventListener('toggle', () => {
      const key = `${page.platform}|${section.slug}`;
      if (details.open) rtSetupOpen.add(key); else rtSetupOpen.delete(key);
    });
    const summary = rtEl('summary');
    summary.appendChild(rtEl('h2', '', 'Setup'));
    const parts: string[] = [];
    if (setup.bench.length) parts.push(`${setup.bench.length} ${setup.bench.length === 1 ? 'thing' : 'things'} on the bench`);
    if (setup.before.length) parts.push(`${setup.before.length} ${setup.before.length === 1 ? 'step' : 'steps'} before you start`);
    if (setup.later.length) parts.push(`${setup.later.length} later`);
    summary.appendChild(rtEl('span', '', parts.join(' · ')));
    details.appendChild(summary);
    const body = rtEl('div', 'rt-setup-body');
    if (setup.bench.length) {
      const col = rtEl('div');
      col.appendChild(rtEl('h3', '', 'On the bench'));
      const ul = rtEl('ul');
      for (const item of setup.bench) { const li = rtEl('li'); li.appendChild(rtInline(item)); ul.appendChild(li); }
      col.appendChild(ul);
      body.appendChild(col);
    }
    if (setup.before.length) {
      const col = rtEl('div');
      col.appendChild(rtEl('h3', '', 'Before you start'));
      const ol = rtEl('ol');
      for (const item of setup.before) { const li = rtEl('li'); li.appendChild(rtInline(item)); ol.appendChild(li); }
      col.appendChild(ol);
      body.appendChild(col);
    }
    if (setup.later.length) {
      const later = rtEl('div', 'rt-later');
      later.appendChild(rtEl('h3', '', 'Later'));
      const ul = rtEl('ul');
      for (const item of setup.later) {
        const li = rtEl('li');
        li.appendChild(rtEl('b', '', `Check ${item.check}: `));
        li.appendChild(rtInline(item.text));
        ul.appendChild(li);
      }
      later.appendChild(ul);
      body.appendChild(later);
    }
    details.appendChild(body);
    wrap.appendChild(details);
  }

  if (section.problems.length) {
    const warn = rtEl('div', 'rt-warn');
    warn.appendChild(rtEl('p', '', 'This section has a procedure and it no longer matches what the release owes. Each owed check is shown on its own instead:'));
    const ul = rtEl('ul');
    for (const problem of section.problems) ul.appendChild(rtEl('li', '', problem));
    warn.appendChild(ul);
    wrap.appendChild(warn);
  }

  const checks = rtEl('section', 'rt-block');
  checks.appendChild(rtEl('h2', '', 'Checks'));
  const tally = rtSectionTally(page, section, marks);
  const progress = rtEl('div', 'rt-progress');
  progress.appendChild(rtEl('span', 'rt-count', `${tally.done} of ${tally.total} have a result`));
  progress.appendChild(rtBar(tally.done, tally.total));
  checks.appendChild(progress);
  checks.appendChild(rtTally(tally.counts));
  for (const group of section.groups) {
    const box = rtEl('div', 'rt-group');
    if (group.title || group.start) {
      const gh = rtEl('div', 'rt-group-head');
      if (group.title) gh.appendChild(rtEl('h3', '', group.title));
      if (group.start) {
        const start = rtEl('p', 'rt-start');
        start.appendChild(rtEl('b', '', 'Start: '));
        start.appendChild(rtInline(group.start));
        gh.appendChild(start);
      }
      box.appendChild(gh);
    }
    for (const check of group.checks) box.appendChild(rtBuildCheck(page, section, check, marks));
    checks.appendChild(box);
  }
  wrap.appendChild(checks);

  const nav = rtEl('div', 'rt-pager');
  const at = page.sections.indexOf(section);
  for (const [other, label] of [[page.sections[at - 1], '← '], [page.sections[at + 1], '→ ']] as Array<[RtSection | undefined, string]>) {
    if (!other) continue;
    const link = rtEl('button', 'rt-link', label === '← ' ? `← ${other.name}` : `${other.name} →`);
    link.type = 'button';
    link.addEventListener('click', () => { void navigateTo(rtAddress(page, other)); });
    nav.appendChild(link);
  }
  wrap.appendChild(nav);
  return wrap;
}

function rtBuildCheck(page: RtPage, section: RtSection, check: RtCheck, marks: RtMarks): HTMLElement {
  const row = rtEl('div', 'rt-check');
  row.id = `rt-check-${check.number}`;
  if (check.start) {
    const start = rtEl('p', 'rt-start rt-start-again');
    start.appendChild(rtEl('b', '', check.start_again ? 'Start again: ' : 'Start: '));
    start.appendChild(rtInline(check.start));
    row.appendChild(start);
  }
  row.appendChild(rtEl('span', 'rt-num', String(check.number)));
  const act = rtEl('p', 'rt-do');
  if (check.path) {
    const link = rtEl('button', 'rt-link');
    link.type = 'button';
    link.appendChild(rtInline(check.action));
    link.addEventListener('click', () => { void navigateTo(check.path.replace(/^docs\//, '')); });
    act.appendChild(link);
  } else {
    act.appendChild(rtInline(check.action));
  }
  row.appendChild(act);
  if (check.timer) row.appendChild(rtBuildTimer(check.timer));
  if (check.setup !== undefined) {
    if (check.setup) {
      const p = rtEl('p', 'rt-note-part');
      p.appendChild(rtEl('b', '', 'Setup: '));
      p.appendChild(rtInline(check.setup));
      row.appendChild(p);
    }
    if (check.steps) {
      const p = rtEl('pre', 'rt-note-part', check.steps);
      row.appendChild(p);
    }
  }
  if (check.preparation) {
    row.classList.add('rt-muted');
    row.appendChild(rtEl('p', 'rt-hint', 'Preparation for a later check. Nothing to record.'));
  }
  for (const line of check.expected) {
    const p = rtEl('p', 'rt-expect');
    p.appendChild(rtInline(line.text));
    row.appendChild(p);
  }
  if (!check.expected.length && !check.preparation) {
    row.appendChild(rtEl('p', 'rt-hint', `The note states no expected result for ${rtPlatformName(page.platform)}.`));
  }
  if (check.tags.length) row.appendChild(rtEl('span', 'rt-tid', check.tags.join(' ')));
  if (check.readiness) {
    const r = check.readiness;
    //: Greyed until someone decides: it cannot be done as written, and it
    //: can still be given any result ([[TASK-0643]]).
    row.classList.add('rt-muted');
    row.appendChild(rtEl('p', 'rt-flag',
      `${r.reason}${r.issue ? ` (${r.issue})` : ''} Suggested: ${RT_LABELS[r.result] || r.result}.`));
  }
  if (check.capture) row.appendChild(rtBuildCaptureNote(page, section, check, marks));
  if (check.compare_with.length) {
    row.appendChild(rtEl('p', 'rt-hint', `Compare with what you kept at check ${check.compare_with.join(', ')}.`));
  }
  if (check.checks.length) rtBuildMarks(page, section, check, row, marks);
  return row;
}

/** A timer the tester starts. It counts down and never sets a result. */
function rtBuildTimer(seconds: number): HTMLElement {
  const button = rtEl('button', 'rt-timer', `⏱ Start ${seconds} s timer`);
  button.type = 'button';
  let handle = 0;
  button.addEventListener('click', () => {
    if (handle) {
      window.clearInterval(handle);
      handle = 0;
      button.textContent = `⏱ Start ${seconds} s timer`;
      return;
    }
    let left = seconds;
    button.textContent = `⏱ ${left} s — stop`;
    handle = window.setInterval(() => {
      left -= 1;
      if (left <= 0) {
        window.clearInterval(handle);
        handle = 0;
        button.textContent = `⏱ ${seconds} s up`;
        return;
      }
      button.textContent = `⏱ ${left} s — stop`;
    }, 1000);
  });
  return button;
}

/** Where a check asks the tester to keep what they saw for a later
 *  comparison: a note kept with the check's result here (REQ-0069). */
function rtBuildCaptureNote(page: RtPage, section: RtSection, check: RtCheck,
                            marks: RtMarks): HTMLElement {
  const wrap = rtEl('div', 'rt-capture');
  wrap.appendChild(rtEl('span', 'rt-hint', `Keep what you see: ${check.capture}`));
  const box = rtEl('input', 'rt-reason');
  box.placeholder = 'What you saw';
  box.setAttribute('aria-label', `What you saw at check ${check.number}`);
  const key = rtCheckKey(page, section, check);
  box.value = rtLoadNotes()[key] || marks[key]?.note || '';
  box.addEventListener('change', () => {
    const notes = rtLoadNotes();
    notes[key] = box.value;
    rtSaveNotes(notes);
  });
  wrap.appendChild(box);
  //: A picture of what was seen, filed under the check's first test note
  //: as `docs/attachments/<TST>/…png` ([[TASK-0643]]; the walk page's
  //: evidence upload, ported). Its path is kept with the note.
  const owner = check.checks[0] || '';
  if (owner) {
    const row = rtEl('div', 'rt-capture-pic');
    const shown = rtEl('span', 'rt-hint');
    const setShown = (rel: string) => {
      shown.textContent = rel ? `Picture filed at docs/${rel}` : '';
    };
    setShown(rtLoadNotes()[`${key}#png`] || '');
    const pick = rtEl('input');
    pick.type = 'file';
    pick.accept = 'image/png';
    pick.setAttribute('aria-label', `Attach a PNG of what you saw at check ${check.number}`);
    pick.addEventListener('change', async () => {
      const file = pick.files?.[0];
      pick.value = '';
      if (!file) return;
      const rel = await rtAttachPicture(page, check, owner, file);
      if (!rel) return;
      const notes = rtLoadNotes();
      notes[`${key}#png`] = rel;
      rtSaveNotes(notes);
      setShown(rel);
    });
    row.append(rtEl('span', 'rt-hint', 'Picture:'), pick, shown);
    wrap.appendChild(row);
  }
  return wrap;
}

/** File a PNG as evidence under a test note; the path it was filed at, or
 *  '' after saying why not. Only a PNG under 8 MB is sent, the server's own
 *  limit (`note_writes.MAX_ATTACHMENT_BYTES`). */
async function rtAttachPicture(page: RtPage, check: RtCheck, owner: string,
                               file: File): Promise<string> {
  if (file.size > 8 * 1024 * 1024 || !file.name.toLowerCase().endsWith('.png')) {
    showStatus('Choose a PNG smaller than 8 MB.', 'error');
    return '';
  }
  try {
    const bytes = new Uint8Array(await file.arrayBuffer());
    let binary = '';
    for (let at = 0; at < bytes.length; at += 8192)
      binary += String.fromCharCode(...bytes.subarray(at, at + 8192));
    const caption = `${owner}, release test check ${check.number} `
      + `(${check.tags.join(', ')}), ${page.platform}, ${page.release}`;
    const response = await postJson('/api/notes/attach', {
      id: owner, png_base64: btoa(binary), caption, actor: 'user:edwin',
    });
    const rel = String((response.result as { rel?: string } | undefined)?.rel || '');
    if (!rtSafeAttachment(rel, owner)) throw new Error('the reply named no safe file path');
    showStatus('Picture filed with the check.', 'info');
    scheduleHide(3000);
    return rel;
  } catch (error) {
    showStatus(`Could not file the picture: ${error instanceof Error ? error.message : String(error)}`, 'error');
    return '';
  }
}

/** A filed picture's path is `attachments/<owner>/<name>.png` and nothing else. */
function rtSafeAttachment(rel: string, owner: string): boolean {
  return rel.startsWith(`attachments/${owner}/`)
    && /^attachments\/[A-Za-z0-9-]+\/[A-Za-z0-9-]+\.png$/.test(rel);
}

function rtNotesKey(workspaceId: string): string {
  return `cockpit:release-test-notes:${workspaceId}`;
}
function rtLoadNotes(): Record<string, string> {
  if (!activeId) return {};
  try {
    const parsed = JSON.parse(localStorage.getItem(rtNotesKey(activeId)) || '{}') as unknown;
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed)
      ? parsed as Record<string, string> : {};
  } catch { return {}; }
}
function rtSaveNotes(notes: Record<string, string>): void {
  if (!activeId) return;
  try { localStorage.setItem(rtNotesKey(activeId), JSON.stringify(notes)); } catch { /* storage off */ }
}

/** Pass, Fail and More, and the reason box every result but Pass needs. */
function rtBuildMarks(page: RtPage, section: RtSection, check: RtCheck,
                      row: HTMLElement, marks: RtMarks): void {
  const state = rtCheckState(page, section, check, marks);
  if (state.result) row.dataset.mark = state.result;
  const box = rtEl('div', 'rt-marks');
  const pass = rtEl('button', state.result === 'pass' ? 'on' : '', 'Pass');
  const fail = rtEl('button', state.result === 'fail' ? 'on' : '', 'Fail');
  const other = state.result && state.result !== 'pass' && state.result !== 'fail';
  const more = rtEl('button', other ? 'on' : '', `${other ? RT_LABELS[state.result] : 'More'} ▾`);
  for (const b of [pass, fail, more]) { b.type = 'button'; box.appendChild(b); }
  if (state.source === 'ledger') {
    box.title = 'Recorded in the ledger. Mark it again here to record a new result.';
  }
  pass.addEventListener('click', () => { void rtRecord(page, section, check, 'pass'); });
  fail.addEventListener('click', () => { void rtRecord(page, section, check, 'fail'); });
  more.addEventListener('click', (event) => {
    event.stopPropagation();
    const open = box.querySelector('.rt-menu');
    if (open) { open.remove(); return; }
    const menu = rtEl('div', 'rt-menu');
    menu.setAttribute('role', 'menu');
    for (const [result, meaning] of RT_MORE) {
      const item = rtEl('button');
      item.type = 'button';
      item.setAttribute('role', 'menuitem');
      item.appendChild(rtEl('b', '', RT_LABELS[result]));
      item.appendChild(rtEl('span', '',
        meaning + (check.readiness?.result === result ? ' (suggested)' : '')));
      item.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.remove();
        void rtRecord(page, section, check, result);
      });
      menu.appendChild(item);
    }
    box.appendChild(menu);
    (menu.querySelector('button') as HTMLButtonElement | null)?.focus();
    document.addEventListener('click', () => menu.remove(), { once: true });
    menu.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { e.stopPropagation(); menu.remove(); more.focus(); }
    });
  });
  row.appendChild(box);
  if (state.result && state.result !== 'pass' && state.source === 'here') {
    const reason = rtEl('input', 'rt-reason');
    reason.placeholder = 'Reason (required)';
    reason.value = state.reason;
    reason.classList.toggle('missing', !state.reason.trim());
    reason.addEventListener('input', () => reason.classList.toggle('missing', !reason.value.trim()));
    reason.addEventListener('change', () => {
      void rtRecord(page, section, check, state.result, reason.value);
    });
    row.appendChild(reason);
  } else if (state.reason && state.source === 'ledger') {
    row.appendChild(rtEl('p', 'rt-hint', `Recorded: ${state.reason}`));
  }
}

/** Record one printed check's result here, then write each test note that
 *  is now complete to the ledger, and draw the page again.
 *
 *  Choosing the result a check already has removes it, as the approved
 *  example does. A note already written keeps its ledger event: the ledger
 *  is a record and is never rewritten, and the next complete set of results
 *  writes a new event over it. */
async function rtRecord(page: RtPage, section: RtSection, check: RtCheck,
                        result: string, reason?: string): Promise<void> {
  const marks = rtLoadMarks();
  const key = rtCheckKey(page, section, check);
  const had = marks[key];
  if (had && had.result === result && reason === undefined) {
    delete marks[key];
  } else {
    marks[key] = { result, reason: reason ?? (had?.result === result ? had.reason : ''),
      at: new Date().toISOString() };
  }
  if (!rtSaveMarks(marks)) {
    showStatus('This browser would not save the result, so nothing was recorded.', 'error');
    scheduleHide(6000);
    return;
  }
  const ready = rtNoteResults(page, marks);
  let wrote = false;
  for (const note of check.checks) {
    const next = ready[note];
    if (!next) continue;
    const current = page.results[note];
    if (current && current.result === next.result && current.reason === next.reason) continue;
    const item = { id: note, tier: 1, number: '', section: '', area: '', name: note } as unknown as GateItem;
    const ok = await postCheckVerdict(item, page.platform, { verdict: next.result, reason: next.reason });
    if (ok) {
      page.results[note] = { result: next.result, reason: next.reason, date: '' };
      wrote = true;
    }
  }
  const scroll = docView.scrollTop;
  rtShow(rtBuildSection(page, section));
  docView.scrollTop = scroll;
  rtRefreshPane(page, rtLoadMarks());
  if (wrote) {
    showStatus(`Recorded ${check.checks.join(', ')} in the ${rtPlatformName(page.platform)} ledger.`, 'info');
    scheduleHide(4000);
  }
}
