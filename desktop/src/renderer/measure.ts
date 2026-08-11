// The measure view (FEAT-0068) — the tool whose absence cost PHASE-022 twelve
// rounds, every one beginning with hand-driven CDP measurement.
//
// **Not pixel diffing.** DES-0007 rejected it: pixels diff noisily and explain
// nothing. What a reader needs is *the box is 4px taller and the font is one
// step smaller*, which is a table of named properties.
//
// Scoped to **self and artefacts**, per the feature's out-of-scope line.
// Pointing the probe at an external app is its own phase with its own risk
// scan, and the code is shaped so growing it there is a visible change rather
// than a parameter.

/** The properties worth reading, grouped so the table reads by question:
 *  how big, what type, what colour, how much room. */
const MEASURE_GROUPS: ReadonlyArray<readonly [string, readonly string[]]> = [
  ['box', ['width', 'height', 'display', 'position', 'box-sizing', 'overflow']],
  ['type', ['font-family', 'font-size', 'font-weight', 'line-height', 'letter-spacing']],
  ['colour', ['color', 'background-color', 'border-color', 'opacity']],
  ['space', ['margin', 'padding', 'gap', 'border-width', 'border-radius']],
];

const MEASURE_PROPERTIES: readonly string[] =
  MEASURE_GROUPS.flatMap(([, props]) => props);

interface Metrics {
  label: string;
  selector: string;
  values: Record<string, string>;
}

/** Harvest one element's computed metrics.
 *
 *  `getComputedStyle` resolves everything — a `width` of `auto` comes back as
 *  the used pixel value — which is the whole point: a design question is about
 *  what the browser *did*, not what the stylesheet asked for.
 */
function harvest(el: Element, label: string): Metrics {
  const cs = getComputedStyle(el);
  const values: Record<string, string> = {};
  for (const prop of MEASURE_PROPERTIES) {
    values[prop] = cs.getPropertyValue(prop).trim();
  }
  // Box metrics from the rect rather than the style: `width` reports the
  // content box under `box-sizing: content-box`, and the question "how big is
  // this on screen" is about the border box.
  const rect = el.getBoundingClientRect();
  values.width = `${Math.round(rect.width * 100) / 100}px`;
  values.height = `${Math.round(rect.height * 100) / 100}px`;
  return { label, selector: describe(el), values };
}

/** A short, stable-enough description of an element for the table's header. */
function describe(el: Element): string {
  const tag = el.tagName.toLowerCase();
  const id = el.id ? `#${el.id}` : '';
  const cls = typeof el.className === 'string' && el.className
    ? `.${el.className.trim().split(/\s+/).slice(0, 2).join('.')}`
    : '';
  return `${tag}${id}${cls}`;
}

interface DiffRow {
  group: string;
  property: string;
  a: string;
  b: string;
  differs: boolean;
}

/** Both elements' metrics, in table order, with differences marked.
 *
 *  Every property is returned rather than only the differing ones: *what is
 *  the same* is half the answer when two surfaces look different, and a table
 *  that hid it would send the reader back to the inspector.
 */
function diff(a: Metrics, b: Metrics): DiffRow[] {
  const rows: DiffRow[] = [];
  for (const [group, props] of MEASURE_GROUPS) {
    for (const property of props) {
      const va = a.values[property] ?? '';
      const vb = b.values[property] ?? '';
      rows.push({ group, property, a: va, b: vb, differs: va !== vb });
    }
  }
  return rows;
}

/** The markdown table PHASE-022's issues used as evidence.
 *
 *  Differences only, because that is what an issue cites. The full table lives
 *  on screen; an issue quoting forty identical rows would bury its own point.
 */
function toMarkdown(a: Metrics, b: Metrics, rows: DiffRow[]): string {
  const differing = rows.filter((r) => r.differs);
  const head = `| property | ${a.label} (\`${a.selector}\`) | ${b.label} (\`${b.selector}\`) |`;
  const sep = '|---|---|---|';
  if (!differing.length) {
    return `${head}\n${sep}\n| — | _no differences across ${rows.length} measured properties_ | |`;
  }
  const body = differing
    .map((r) => `| \`${r.property}\` | ${r.a || '—'} | ${r.b || '—'} |`)
    .join('\n');
  return `${head}\n${sep}\n${body}`;
}

// Declared as globals, not exported: the renderer loads these as plain
// `<script src>` files rather than ES modules (no build step is the project's
// property), so a sibling reads them off the global scope exactly as
// `completed-work.ts` and `health-marks.ts` are read.
