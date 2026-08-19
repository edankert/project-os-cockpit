// The validator-error row model (FEAT-0051 / TASK-0253).
//
// Split out of `renderer.ts` for the reason the PHASE-013 review made
// unarguable: a decision that lives inside a DOM function can only be
// guarded by grepping the built bundle, and a string-index guard
// survives the mutation that breaks the behaviour it names. This is
// pure — reports in, rows out — so it can be exercised directly.
//
// Declares no imports and no exports: `renderer.ts` is loaded as a
// plain <script>, not a module, so this is loaded the same way and
// these become globals. The node suite reads the built file and
// evaluates it, which is why the shape matters.

interface ValidationEntry {
  code: string;
  message: string;
  id?: string | null;
  rel?: string | null;
  url?: string | null;
}

interface ValidationReport {
  state?: string;
  errors?: ValidationEntry[];
  warnings?: ValidationEntry[];
  checked_at?: string;
  detail?: string;
}

/** Stable identity for one error, so a row can be tracked across
 *  reports and marked done rather than silently vanishing. The message
 *  is part of it: `METRICS` on two different counters is two problems. */
function validationKey(entry: ValidationEntry): string {
  return `${entry.code}\u0000${entry.message}`;
}

// Errors seen this session, and when each was resolved. A row that
// simply disappeared would mean the user sees a count change and never
// learns what changed — `METRICS` in particular clears within a second
// or two of `sync-snapshot.py` running at pre-commit. So a resolved row
// is MARKED done and lingers, which is what makes this panel a record
// of the session rather than a snapshot of this instant.
const validationSeen = new Map<string, ValidationEntry>();
const validationResolvedAt = new Map<string, number>();
const RESOLVED_LINGER_MS = 5 * 60_000;

/** Rows to draw: everything still failing, plus recently-fixed ones. */
interface ValidationRow {
  entry: ValidationEntry;
  done: boolean;
}

function validationRows(open_: ValidationEntry[], now: number): ValidationRow[] {
  const open = new Set(open_.map(validationKey));
  const rows: ValidationRow[] = [];
  for (const [key, entry] of validationSeen) {
    if (open.has(key)) { rows.push({ entry, done: false }); continue; }
    const at = validationResolvedAt.get(key);
    if (at !== undefined && now - at <= RESOLVED_LINGER_MS) rows.push({ entry, done: true });
  }
  // Unresolved first; a fixed row must never push a live one down.
  return rows.sort((a, b) => Number(a.done) - Number(b.done));
}

function noteValidationChange(report: ValidationReport | null, now: number): void {
  const open = new Set((report?.errors ?? []).map(validationKey));
  for (const entry of report?.errors ?? []) {
    const key = validationKey(entry);
    validationSeen.set(key, entry);
    validationResolvedAt.delete(key);      // came back — it is live again
  }
  for (const key of validationSeen.keys()) {
    if (!open.has(key) && !validationResolvedAt.has(key)) {
      validationResolvedAt.set(key, now);
    }
  }
  // Forget rows whose linger has expired, so a long session does not
  // accumulate every error it ever fixed.
  for (const [key, at] of Array.from(validationResolvedAt)) {
    if (now - at > RESOLVED_LINGER_MS) {
      validationResolvedAt.delete(key);
      validationSeen.delete(key);
    }
  }
}

function resetValidationRows(): void {
  validationSeen.clear();
  validationResolvedAt.clear();
}

/** A short human label for an error code. The code alone is accurate
 *  and opaque; the point of this panel is that a glance answers "what
 *  is this about". Unknown codes fall back to the code itself rather
 *  than to a guess. */
const VALIDATION_LABELS: Record<string, string> = {
  // Enumerated from `validate-docs.py`'s own emit sites rather than
  // invented, so a code the panel cannot name is a code the validator
  // gained — not one somebody forgot. An unknown code still renders,
  // showing itself; the fallback is deliberate, not a gap.
  'COUNTER': 'ID above the allocated counter',
  'METRICS': 'snapshot counts are behind',
  'LINK': 'link to a note that does not exist',
  'STATUS-VALUE': 'status is not in the allowed set',
  'ITEM-ID': 'snapshot entry names an ID the note does not',
  'ITEM-FILE': 'snapshot entry points at a missing file',
  'ITEM-TYPE': 'snapshot entry has the wrong type',
  'ITEM-STATUS': 'snapshot status disagrees with the note',
  'ITEM-SHAPE': 'snapshot entry is malformed',
  'SNAP-KEYS': 'snapshot is missing required keys',
  'SNAP-MISSING': 'no SNAPSHOT.yaml',
  'SNAP-PARSE': 'SNAPSHOT.yaml will not parse',
  'FOCUS': 'focus names something that is not there',
  'PARENT-BACKLINK': 'relationship declared on one end only',
  'SNAPSHOT-MEMBERSHIP': 'snapshot and note disagree on membership',
  'PHASE-CHILDREN': 'phase closed with unfinished work',
  'PHASE-BOXES': 'phase closed with unticked exit criteria',
  'REQ-BOXES': 'requirement closed with unticked criteria',
  'REQ-OWNER': 'requirement implements more than one feature',
  'REQ-STALE': 'requirement left behind by its feature',
  'FEATURE-REQ': 'feature done with a requirement unresolved',
  'REVIEW': 'terminal note without a review verdict',
  'DESIGN-ASSET': 'design note points at a missing artifact',
  'DEFER-HOME': 'deferred note in the wrong place',
  'DEFER-ORIGIN': 'deferred note with no origin',
  'DEFER-PARENT': 'deferred note with no parent',
  'DEFER-RETENTION': 'deferred note pruned from the snapshot',
  'DEFER-SCOPE': 'deferred note outside its scope',
  'STATUS-TABLE': "the validator's own tables disagree",
  // The acceptance ledger (ADR-0037). A verdict is an event, so the failures
  // are about an event that cannot be trusted rather than about a note.
  'LEDGER-PARSE': 'a ledger will not parse',
  'LEDGER-ENTRY': 'a verdict is missing part of what makes it one',
  'LEDGER-MARK': 'a verdict uses a mark nothing recognises',
  'LEDGER-REASON': 'a verdict left the gate without saying why',
  'LEDGER-EVIDENCE': 'evidence for a walk nobody recorded',
  'LEDGER-SEALED': 'a sealed ledger was edited',
};


function validationLabel(entry: ValidationEntry): string {
  return VALIDATION_LABELS[entry.code] ?? entry.code;
}
