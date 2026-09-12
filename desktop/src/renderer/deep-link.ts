// What a `cockpit://` link asks the window to open, as a pure function
// (ISS-0293).
//
// A link is `cockpit://<project>/<target>`. The project is a project id
// (`your-health`, what a `[[project#ID]]` link names) or the shell's own
// workspace id. The target is optional: a note ID (`FEAT-0107`), located the
// way a cross-repo link is, or a path under `docs/`, opened as it stands.
//
// **A design ID opens its note, like every other ID** (REQ-0064). Between
// 2026-09-11 and 2026-09-12 it opened the design bench instead, decided here
// by `designBenchTarget`; the bench is gone and so is the rule. The record of
// why is REQ-0062 and FEAT-0146, both superseded.
//
// Split out of renderer.ts so the parsing can be tested without a window,
// the same arrangement as `cache-temperature.ts`. Like that file, this one
// declares no imports and no exports: it is loaded as a plain `<script>`
// before renderer.js, so `parseCockpitLink` becomes a global. The node suite
// reads the built file and evaluates it.

interface CockpitLink {
  /** The host as written. Matched case-insensitively against both ids. */
  project: string;
  target:
    | { kind: 'none' }
    | { kind: 'note'; id: string }
    | { kind: 'path'; rel: string };
}

/** Null for anything that is not a well-formed cockpit link, and for a path
 *  with a `.` or `..` segment in it.
 *
 *  Parsed by hand, not with `URL`. The renderer's Chromium 128 reads no host
 *  from a URL whose scheme is not a web one: `new URL('cockpit://your-health/x')`
 *  gives an empty `host` and a `pathname` of `//your-health/x`. Node's `URL`
 *  gets it right, so a parser built on `URL` passed its node tests and returned
 *  null for every link in the window (ISS-0293). The handler this replaced read
 *  `u.host` the same way, so it had never switched a project either. */
function parseCockpitLink(url: string): CockpitLink | null {
  const scheme = 'cockpit://';
  if (typeof url !== 'string' || url.slice(0, scheme.length).toLowerCase() !== scheme) {
    return null;
  }
  let rest = url.slice(scheme.length);
  const query = rest.indexOf('?');
  const hash = rest.indexOf('#');
  // A fragment is kept and handed on: the doc pane scrolls to it.
  const fragment = hash >= 0 ? rest.slice(hash) : '';
  const cut = [query, hash].filter((i) => i >= 0);
  if (cut.length) rest = rest.slice(0, Math.min(...cut));
  const slash = rest.indexOf('/');
  const project = slash < 0 ? rest : rest.slice(0, slash);
  if (!project) return null;
  let path: string;
  try { path = decodeURIComponent(slash < 0 ? '' : rest.slice(slash + 1)); } catch { return null; }
  path = path.replace(/^\/+/, '').replace(/\/+$/, '');
  if (!path) return { project, target: { kind: 'none' } };
  if (/^[A-Za-z]+-\d+$/.test(path)) {
    return { project, target: { kind: 'note', id: path.toUpperCase() } };
  }
  if (path.split('/').some((segment) => segment === '..' || segment === '.')) return null;
  return { project, target: { kind: 'path', rel: path + fragment } };
}
