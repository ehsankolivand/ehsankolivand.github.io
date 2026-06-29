# Research: Android-Engineer Positioning, Deep-Citability & Portfolio Performance

Phase 0 decisions, each with rationale and (where relevant) a primary source. Every decision serves
the objective and the constitution; all were resolved autonomously (unattended run).

## R1 — Grounded identity enrichment: `knowsAbout` mirrored from the portfolio

**Decision**: Add `knowsAbout` (and keep `jobTitle`) to the blog's *full* author Person node — the one
already emitted on post pages (`BlogPosting.author`) and the index (`Blog.author`) — sourcing the list
**verbatim** from the portfolio's `Person.knowsAbout`. Keep referencing the portfolio person by stable
`@id` (`…/#person`); do **not** create a second entity, and do **not** mirror the portfolio's prose
`description`/`address`/`seeks` (those stay canonical in the portfolio and merge via `@id`).

**Rationale**: `knowsAbout` is a valid schema.org `Person` property whose range is Text/Thing/URL and
which expresses "a topic that is known about — suggesting possible expertise" (schema.org). The
positioning failure mode (US1) is a *single post read in isolation*: an engine that does not also fetch
the portfolio sees only Python developer-tooling content. Emitting the grounded Android skill list on
every post — under the same `@id` as the portfolio — makes each post self-describe its author as a
Senior Android Engineer whose expertise *includes* dev-tooling/code-generation, so the tooling posts
read as an Android engineer's tooling work. The portfolio's list already contains the bridge topics
**"Spec-driven development"** and **"Agentic code generation"**, so no new claim is needed.

**Primary source**: schema.org/knowsAbout — domain includes `Person`; range Text/Thing/URL; "suggests
possible expertise". Google rich-results docs treat `knowsAbout`/`sameAs` as standard E-E-A-T identity
signals (no special rich result, but consumed for entity understanding).

**Grounding**: The exact list is copied from `index.html` JSON-LD `Person.knowsAbout` (read directly):
Android development, Kotlin, Jetpack Compose, MVI, MVVM, Clean Architecture, Multi-module architecture,
Coroutines, Dagger/Hilt, Server-Driven UI, Android TV, Spec-driven development, Agentic code
generation. The verifier asserts equality, so the two can never drift and nothing is fabricated.

**Alternatives rejected**: (a) `@id`-only reference — fails the isolation case (relies on the engine
fetching the portfolio). (b) Inventing tooling-specific skills ("Python", "CLI tooling") — would be
fabrication unless present in the portfolio; the portfolio's existing bridge topics suffice. (c)
Duplicating the full Person (description/address/seeks) into the blog — needless divergence risk; `@id`
merge already pulls those in for engines that fetch both.

## R2 — Section-level heading anchors: readable deterministic slugs

**Decision**: Every rendered body heading (h2–h4) gets an `id` = GitHub-style slug of its text:
lowercase, Unicode NFKD→ASCII fold, runs of non-alphanumerics → single hyphen, trimmed. Collisions
within a page get a deterministic numeric suffix (`-1`, `-2`, …) in document order. A heading whose
text yields an empty slug (symbols/emoji only) falls back to `section-<n>` (n = 1-based heading index).
Anchors are invisible (just an `id`); no hover affordance (Clarification).

**Rationale**: Readable, citable, deterministic, collision-free, and consistent with the project's
existing `content.slugify()` (NFKD fold). Stable across rebuilds because it depends only on heading
text + document order, never on `today()` or hashing of volatile input. Matches the de-facto
convention (GitHub/most static generators) so links look natural. Invisible-`id`-only honors Principle
III (the locked design has no heading-link UI).

**Alternatives rejected**: opaque content hash (stable but unreadable, poor for citation); visible "#"
hover link (invents UI, violates design fidelity); client-side anchor JS (violates Principle I —
content/links must be in static HTML).

## R3 — Portfolio font optimization: delete unused non-Latin `@font-face` subsets

**Decision**: Remove the 32 `@font-face` rules whose `unicode-range` is one of the four non-Latin
subsets the page never renders (Cyrillic, Cyrillic-ext, Greek, Vietnamese), keeping Latin + Latin-ext
(22 faces). Performed once, offline, by deleting whole `@font-face` blocks inside a marker-delimited
zone; committed to source. ~242 KB decoded / ~323 KB of base64 source removed from the 1.08 MB page.

**Rationale (authoritative)**: Per MDN, the `unicode-range` descriptor means "if the page doesn't use
any character in this range, the font is not downloaded; if it uses at least one, the whole font is
downloaded" — and therefore **deleting an `@font-face` rule whose range matches no codepoint on the
page does not change rendering** (the browser never downloaded it). So removing the non-Latin subsets
is provably non-visual *and* cuts the served HTML weight (the base64 is inlined, so it ships on every
visit regardless of the download behavior — deletion is a pure win for transfer/parse/LCP).

**Empirical pre-verification** (sandbox analysis of `index.html`, base64 payloads excluded): the only
non-ASCII codepoints the page renders are `—` `·` `é` `°` `…` `©` `↓` `→` `⌄` and assorted
symbols/emoji. Each is either covered by the retained **Latin** subset (em-dash, middle-dot, é, degree,
ellipsis, ©, ↓ all fall in Latin's `U+0000-00FF`/`U+2000-206F`/explicit ranges) or covered by **no**
subset at all (arrows `→`/`⌄`, emoji, misc symbols — they already render via system fonts). **None** is
covered exclusively by a dropped non-Latin subset. The verifier re-proves this at build time against
the committed baseline, so the safety does not rest on this one-time analysis.

**Drop set vs. keep set**: keep Latin (268 KB) + Latin-ext (170 KB) = full Latin-script coverage,
including European diacritics for the Europe-targeting portfolio; drop Cyrillic (88 KB) + Cyrillic-ext
(15 KB) + Greek (58 KB) + Vietnamese (79 KB) = ~242 KB decoded. (Sizes measured from base64 lengths.)

**Primary source**: MDN `@font-face`/`unicode-range` — segmentation semantics + "font is not
downloaded" guarantee.

**Alternatives rejected**: (a) re-subsetting woff2 glyph tables with `fonttools`/`pyftsubset` — would
shrink even the Latin faces but **adds a build/dev dependency** and risks altering rendered glyphs
(violates Principle II + the non-visual requirement). Pure whole-subset deletion needs no tooling and
is trivially provable. (b) Also dropping Latin-ext — saves another 170 KB but removes European diacritic
coverage the portfolio may use; the conceptual boundary "keep all Latin script" is lower-regret. (c)
Moving fonts to external files — changes the page's resource model and request count; out of scope and
riskier than deletion.

## R4 — Prove-or-defer safety architecture (committed baseline + offline verifier proof)

**Decision**: Wrap the font block in `<!--PORTFOLIO-FONTS:START/END-->` markers; commit the pre-change
`index.html` (markers present, all 54 faces) as `assets/portfolio-fonts/index.baseline.html`; the
verifier proves (a) glyph-coverage preservation and (b) outside-zone byte-equality + retained-faces-
verbatim, against that baseline. If unprovable, revert `index.html` to the baseline (deferral).

**Rationale**: The baseline is the recoverable original (Principle VII exception 2 requirement) *and*
the reference the proof diffs against — one artifact serves both, fully offline and deterministic. The
build never copies `assets/portfolio-fonts/` (not in `ROOT_COPY_ALLOWLIST`, not under a copied asset
tree), so the baseline never deploys. The proof runs only when the zone differs from the baseline, so a
deferred/untouched portfolio passes trivially (no false failure).

**Alternatives rejected**: git-history-only recoverability (not self-contained; a verifier can't diff
against history offline/deterministically); hashing the outside-zone (less transparent than a literal
baseline, and not "recoverable original").

## R5 — Empty-category graceful degradation: already handled, lock with a check

**Decision**: No generator change; add a verifier assertion. Confirm Compose/Architecture (declared,
empty) already render as valid nav entries with the existing `_EMPTY_GRID` / per-category empty path,
and that a future post flows through unchanged (the pipeline is fully data-driven from
`categories.yml`).

**Rationale**: `render.render_nav` emits every declared category as a real anchor regardless of post
count; `render_index_page` falls back to `_EMPTY_GRID` when a category/grid is empty; sitemap/feed/
llms only list real posts. So empty categories already degrade gracefully; the only gap is that no
verifier assertion *locks* it. Adding one makes the positioning scaffold durable (FR-006).

## R6 — Inherited verifier hardening (author/locale/article-tag) and sameAs exactness

**Decision**: Add explicit assertions that 002 left implicit: (1) blog `sameAs` exactly equals the
portfolio `Person.sameAs` (parsed from `index.html`); (2) `<meta name="author">`, JSON-LD author name,
`inLanguage`/`og:locale` are consistent across pages; (3) every post surfaces each tag as both a meta
keyword and an `article:tag`. These were correct in 002's output but rested on pre-existing behavior
with no guard.

**Rationale**: FR-013-class signals and the identity-unification benefit (FR-004/FR-017) must be
*enforced*, not assumed. The whole positioning payoff depends on `sameAs` being byte-exact; a silent
divergence would split the entity. Fail-loud is the project's discipline.

## R7 — Determinism, dependencies, and scope guards (unchanged posture)

**Decision**: All new logic is stdlib-only and deterministic; no `today()`; no backend; no client
content rendering; no new CI/runtime dependency; no restyle; no authored post. The font subset is a
one-off sandbox text edit, not a build step.

**Rationale**: Constitution I/II/III/IV and the determinism guardrail. The build remains "same content
in → byte-identical out", and CI still just builds + verifies + deploys.

## Out of scope (recorded)

- Authoring blog posts (Principle IV; owner writes content — scaffolding only).
- Backend-requiring features: on-site search, analytics, contact backends (Principle II).
- RTL/Persian edition (separate epic; the font subset deliberately keeps only Latin, consistent with
  the current single-locale site).
- Any visible redesign (Principle III); isolated renderer unit tests (consistent with 002 — the
  post-build verifier remains the single gate).
