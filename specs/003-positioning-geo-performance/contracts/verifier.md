# Contract: New Definition-of-Done Verifier Assertions

`scripts/verify_build.py` gains the assertions below. Baseline = **163** checks, 0 failures; coverage
MUST grow and never regress. Every assertion fails the build loudly on violation. (FR-017.)

## Identity grounding & exactness (parse portfolio `index.html` JSON-LD once)

Extract the portfolio `Person` node from `index.html` (`@id == config.PERSON_ID`). Then:

- **V-ID1**: `config.AUTHOR_SAMEAS == portfolio Person.sameAs` (exact list + order). *(carried-fix #2 —
  locks the unified-identity profile links.)*
- **V-ID2**: `config.AUTHOR_KNOWS_ABOUT == portfolio Person.knowsAbout` (exact list + order).
- **V-ID3**: `config.AUTHOR_ROLE == portfolio Person.jobTitle`.
- **V-ID4**: `config.PERSON_ID == portfolio Person.@id` and `config.WEBSITE_ID == portfolio WebSite.@id`.
- **V-ID5**: bridge topics "Spec-driven development" and "Agentic code generation" ∈
  `config.AUTHOR_KNOWS_ABOUT` (positioning anchor present).

## Per-page grounded identity emission

For each post page and the index:

- **V-ID6**: the canonical author node carries `jobTitle == config.AUTHOR_ROLE`.
- **V-ID7**: the canonical author node carries `knowsAbout == config.AUTHOR_KNOWS_ABOUT`.
- **V-ID8**: the canonical author node `@id == config.PERSON_ID` (already checked on posts in 002 —
  extend to assert `jobTitle`+`knowsAbout` co-present so each post self-describes the Android identity).

## Author / locale consistency (carried-fix #3, FR-013-class)

For each post page (and index where applicable):

- **V-LC1**: `<meta name="author" content="Ehsan Kolivand">` present and == `config.AUTHOR_NAME`.
- **V-LC2**: JSON-LD `inLanguage == config.LOCALE` (posts already; assert index `Blog.inLanguage` too).
- **V-LC3**: `og:locale == config.OG_LOCALE` on every page.

## Per-post tag → keyword + article:tag (carried-fix #3, FR-013-class)

For each post **with tags**:

- **V-TAG1**: `<meta name="keywords">` present and contains every tag.
- **V-TAG2**: an `<meta property="article:tag" content="…">` present for **each** tag.
- **V-TAG3**: JSON-LD `BlogPosting.keywords` present and contains every tag.
- (Posts with no tags are exempt — graceful, matches the data model.)

## Heading anchors (FR-009..FR-011)

For each post page:

- **V-HA1**: every body heading (`<h2|h3|h4 … id="…">`) has a non-empty `id`.
- **V-HA2**: all heading ids on the page are unique.
- **V-HA3**: ids are deterministic — recomputing the slug allocator from the post's body headings
  reproduces exactly the ids present in the built HTML.
- **V-HA4**: exactly one `<h1>` (already checked) and the `<h1>` has no anchor id added.

## Empty-category graceful degradation (FR-006)

- **V-CAT1**: every declared category (incl. empty Compose/Architecture) appears as a nav entry
  (`data-cat="…"`) on the index (extends the existing nav check to assert empties too).
- **V-CAT2**: when a category has zero posts, the index still renders valid (no token leak, the
  empty-state marker `// no notes published yet` present iff the grid is empty) — i.e. no broken list.

## Font fidelity (FR-012..FR-014) — runs against the committed baseline

- **V-FZ1**: if `index.html` present → `PORTFOLIO-FONTS:START/END` markers present once, in order, and
  `assets/portfolio-fonts/index.baseline.html` present. *(If the font change was deferred and markers
  were not added, V-FZ\* are reported as "font optimization not applied" and skipped — see prove-or-
  defer; the deferral path keeps the suite green.)*
- **V-FZ2**: outside-zone byte-equality: `outside(index.html) == outside(baseline)`.
- **V-FZ3**: every `@font-face` block in the current zone is a verbatim substring of the baseline zone
  (only whole removals).
- **V-FZ4**: `cover_cur ⊆ cover_base` (unicode-ranges only removed, never added/edited).
- **V-FZ5**: glyph coverage: `∀ c ∈ V (codepoints in index.html minus base64): c ∈ cover_base ⟹ c ∈
  cover_cur`.
- **V-FZ6** (report, not fail): byte savings (baseline size − current size) printed for visibility.

## Notes

- All new checks are deterministic and offline (no network, no `today()`), consistent with the
  existing verifier discipline.
- The portfolio JSON-LD parse is tolerant: if `index.html` is absent (blog-only build), identity-vs-
  portfolio checks (V-ID1..V-ID5, V-FZ*) print a NOTE and skip, exactly as the existing portfolio
  comparison does — the per-page emission checks (V-ID6..V-ID8) still run.
- Target: net **+** checks over 163 (expected on the order of +30–45 depending on post/category count).
