# Checklist: Positioning / GEO / Performance / Accessibility — "Unit Tests for English"

**Purpose**: Validate that the spec + plan + contracts unambiguously, completely, and testably cover
the four threads. Each item is a quality gate on the *requirements*, not the implementation. Checked
items passed review; each cites where it is satisfied.

## Positioning (Android engineer who builds code-gen tooling)

- [x] CHK001 — Is "resolve as one canonical Senior Android Engineer, not a separate Python identity"
  stated as a testable outcome? (spec US1, SC-001) ✔
- [x] CHK002 — Is every asserted identity signal (jobTitle, each skill, each profile link) required to
  be **grounded verbatim** in existing material, with a no-fabrication rule? (FR-002, FR-005, SC-002) ✔
- [x] CHK003 — Is the *bridge* between Android engineering and the tooling posts made explicit and
  grounded (the portfolio's "Spec-driven development" + "Agentic code generation")? (plan §Grounding,
  contracts/identity V-ID5) ✔
- [x] CHK004 — Is the single-entity requirement (same stable `@id`, no second Person) unambiguous and
  testable on both post pages and the index? (FR-001, contracts/identity 1–6) ✔
- [x] CHK005 — Is the isolation case (a single tooling post read without fetching the portfolio)
  covered by requiring per-page emission of the grounded signals? (spec US1 Independent Test, V-ID6/7) ✔
- [x] CHK006 — Is "invent no blog content; add structure only" stated and measurable? (FR-005, SC-004) ✔

## Taxonomy readiness & graceful degradation

- [x] CHK007 — Are empty declared categories (Compose, Architecture) required to render as valid,
  crawlable, non-broken nav entries with a graceful empty state? (FR-006, edge case, V-CAT1/2) ✔
- [x] CHK008 — Is "a future post flows into every derived surface with no other edit" specified and
  testable? (FR-007, US2 scenario 2) ✔
- [x] CHK009 — Is it required that identity/taxonomy stay valid while categories are empty (no claim of
  nonexistent content)? (FR-008, US2 scenario 3) ✔

## Deep-citability (heading anchors)

- [x] CHK010 — Is "every body heading carries a unique, deterministic id" stated with a clear scope
  (body h2–h4, never the `<h1>`)? (FR-009, FR-011, contracts/heading-anchors) ✔
- [x] CHK011 — Is determinism (byte-identical ids across rebuilds) an explicit, testable requirement?
  (FR-010, SC-005) ✔
- [x] CHK012 — Are collision and empty-slug edge cases (same-text headings; symbol-only headings)
  specified with deterministic resolutions? (spec edge cases, contracts slug algorithm) ✔
- [x] CHK013 — Is "no visual redesign / invisible by default / present in static HTML" required
  (Principle I + III)? (FR-011, Clarification 2) ✔

## Performance (font optimization, prove-or-defer)

- [x] CHK014 — Is the target (remove unused subsets from the highest-traffic page, no visual change, no
  new dependency) stated measurably? (FR-012, SC-006) ✔
- [x] CHK015 — Is the sanctioned, marker-delimited zone + recoverable baseline + "byte-identical
  outside the zone" specified? (FR-013, contracts/font-optimization, Constitution v1.3.0 VII) ✔
- [x] CHK016 — Is the fidelity proof defined precisely (glyph-coverage preservation + outside-zone
  integrity), deterministic and offline? (FR-014, contracts/font-optimization, V-FZ1–5) ✔
- [x] CHK017 — Is **prove-or-defer** explicit: ship only if proven, else defer with reason and ship the
  rest green? (FR-014, SC-006, US4 scenario 3, edge case) ✔
- [x] CHK018 — Is "the change is non-visual because the page renders no codepoint covered only by a
  dropped subset" grounded in evidence (empirical + MDN semantics)? (research R3) ✔

## Accessibility & Core Web Vitals

- [x] CHK019 — Is "exactly one `<h1>` preserved" maintained while adding heading ids? (FR-011, V-HA4) ✔
- [x] CHK020 — Is "no a11y regression; no CLS; reduced-motion/contrast/landmarks unchanged" preserved,
  and is the font change framed as a CWV *improvement*? (plan Constitution Check VI, FR-018) ✔
- [x] CHK021 — Do heading ids improve (never harm) in-page navigation/citation for AT users? (plan VI) ✔

## Grounded structured data & GEO honesty

- [x] CHK022 — Is all structured data required to be valid and free of fabricated claims (consistent
  with 002's no-SearchAction / no-fake-handle posture)? (FR-002, FR-005, FR-018) ✔
- [x] CHK023 — Are author/locale consistency and per-post tag→keyword + article:tag required and
  verifier-enforced (the 002 near-misses)? (FR-017, contracts/verifier V-LC*/V-TAG*) ✔

## Inherited fixes & governance

- [x] CHK024 — Is constitution finalization (v1.2.0 ratified + correctness + any needed amendment with
  Sync Impact Report) a tracked requirement? (FR-015, SC-008) ✔
- [x] CHK025 — Is "no implemented spec left labeled pre-implementation; 003 status honest" required?
  (FR-016, SC-008) ✔
- [x] CHK026 — Is `sameAs` exact-match vs the portfolio required and verifier-enforced (identity won't
  silently split)? (FR-004, SC-003, V-ID1) ✔

## Cross-cutting (constitution-wide)

- [x] CHK027 — Is determinism / static / GitHub-Pages-only / no-new-dependency / no-client-rendering
  asserted across all threads? (FR-018, SC-009) ✔
- [x] CHK028 — Is the Definition-of-Done verifier required to grow beyond 163 checks and gate the whole
  feature? (FR-017, SC-010) ✔
- [x] CHK029 — Are all four out-of-scope items (no authored posts, no backend, no RTL, no redesign)
  stated with reasons? (spec Assumptions / Out of scope) ✔

## Result

**29/29 reviewed and satisfied.** No gaps requiring spec/plan edits. The spec and contracts are
testable, grounded, and bounded; ready for `/speckit-tasks`.
