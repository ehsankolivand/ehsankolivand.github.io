# Feature Specification: Android-Engineer Positioning, Deep-Citability & Portfolio Performance

**Feature Branch**: `003-positioning-geo-performance`

**Created**: 2026-06-29

**Status**: Draft

**Input**: User description: "Sharpen the site's positioning and finish the deferred GEO/performance work, building on 002. (a) Positioning: enrich the canonical Person identity with grounded skill/topic signals (jobTitle, knowsAbout/occupation, and the relationship between the Android-engineering identity and the code-generation tooling content) derived from what actually appears in the portfolio and existing posts — so search and AI engines resolve the Python-tooling writing as an Android engineer's tooling work, not a separate Python identity — and ensure the taxonomy is ready for future Android/architecture posts and degrades gracefully while those categories are empty; invent no blog content. (b) Deep-citability: add stable, deterministic anchor ids to post headings so AI assistants and readers can link to a precise section, with no visual redesign. (c) Performance: cut the portfolio's largest weight — the inlined, mostly-unused font-face data on the highest-traffic page — via a one-time offline subset whose result is committed, adding no CI/runtime dependency, gated by a fidelity proof. (d) Inherited fixes: ratify the v1.2.0 constitution amendment, verify the unified-identity sameAs values are exactly correct, tighten verifier coverage for author/locale/article-tag signals, and correct stale spec Status fields. All changes stay static, build-time, deterministic, GitHub-Pages-only, design-faithful, and grounded — no fabricated content or capabilities."

## Overview

The site (an Obsidian-vault-driven static blog grafted onto a hand-built portfolio on GitHub
Pages) is already SEO/GEO-complete and publishes in one commit (feature 002). It is, however,
*ambiguous about who its author is*: the three published posts are all Python developer-tooling
write-ups, so a search or AI engine reading the blog in isolation could mistake the author for a
"Python developer" rather than what he is — a **Senior Android Engineer who builds code-generation
tooling on the side**. The portfolio already states the Android identity richly; the blog does not
yet carry enough grounded identity signal to make engines resolve the two as one person and read
the tooling posts as *an Android engineer's* tooling work.

This feature sharpens that positioning and finishes two pieces of high-value work deferred from
002, then closes the gaps the 002 review surfaced. It is an enrichment-and-completion pass, not a
redesign or a content drive. Concretely it (a) enriches the **one canonical author identity** with
grounded skill/topic signals sourced verbatim from the portfolio and the existing posts, and makes
the category taxonomy ready for future Android/architecture writing while degrading gracefully
today; (b) makes every post **deep-citable** by giving each heading a stable, invisible anchor a
reader or AI assistant can link to; (c) **lightens the highest-traffic page** by removing the
demonstrably-unused font subsets inlined in the portfolio, one time, offline, gated by a fidelity
proof; and (d) ratifies the constitution amendment, locks the unified-identity values exactly,
hardens the Definition-of-Done verifier, and corrects stale spec status metadata.

It introduces no backend, no client-side content rendering, and no new runtime or CI dependency; it
writes **zero** blog posts and fabricates **zero** claims; it does not restyle the design; and it
touches the portfolio source only within the one new, fidelity-proven, non-visual font-data zone
sanctioned by the constitution (v1.3.0).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The site reads unambiguously as a Senior Android Engineer's home (Priority: P1)

A search engine or AI assistant that lands on any blog post — even one of the Python developer-tooling
posts, read in isolation — can resolve the author to **one** canonical identity that is explicitly a
*Senior Android Engineer* with a grounded skill set, and therefore reads the tooling write-ups as an
Android engineer's tooling work rather than as the output of a separate "Python developer". The
author identity carried by the blog is the *same* entity as the portfolio's (same stable identifier),
and it carries the same grounded job title, skills/topics, and profile links — none invented.

**Why this priority**: This is the headline objective. The blog's content mix currently under-signals
the owner's actual profession; correcting the identity signal (without fabricating posts) is the
highest-leverage change for how engines and assistants describe him, and it directly serves his goal
of being found and correctly summarized as a senior Android engineer. Everything grounded here
already exists in the portfolio or the posts.

**Independent Test**: Fetch any post page with scripting disabled; resolve its author structured data
and confirm it references the portfolio's canonical person (same identifier) and carries a Senior
Android Engineer job title plus a grounded skills/topics list that matches the portfolio's verbatim;
confirm none of the asserted skills/claims are absent from the portfolio or posts.

**Acceptance Scenarios**:

1. **Given** any post page fetched without JavaScript, **When** its author identity is resolved,
   **Then** it references one canonical person (the portfolio's identifier), states the Senior
   Android Engineer job title, and lists grounded areas of expertise that appear verbatim in the
   portfolio — establishing the post as an Android engineer's writing.
2. **Given** the blog's and the portfolio's structured data, **When** the author's profile links are
   compared, **Then** they are byte-for-byte identical (same set of external profiles) so the two
   surfaces describe exactly one entity, not two look-alikes.
3. **Given** the published posts are all developer-tooling topics, **When** an engine builds a topic
   profile of the author, **Then** the identity signal frames that tooling expertise as part of an
   Android engineer's skill set (the code-generation/dev-tooling topics co-occur with the Android
   engineering skills under one person), with no claim that is not grounded in existing material.

---

### User Story 2 - Future Android/architecture writing is structurally ready, and empty categories degrade gracefully (Priority: P2)

The category taxonomy already declares Android-relevant sections (Compose, Architecture) that have no
posts yet. The site presents those empty sections without broken or misleading UI, and the moment a
future Android or architecture note is added, every derived surface (navigation, index, structured
data, feed, machine indexes, homepage notes) picks it up with no structural change — proving the
positioning scaffold is real, not cosmetic.

**Why this priority**: The positioning claim ("an Android engineer who writes") must be structurally
credible: the site has to be *ready* for Android/architecture content and not look broken while those
categories are empty. This is low-risk scaffolding that makes US1 durable, but it depends on the
identity work landing first.

**Independent Test**: With the current content (no Compose/Architecture posts), confirm every declared
category renders a valid, non-broken navigation/empty state and no surface emits a dangling or empty-
list error; then (in a throwaway check) add a single Architecture note and confirm it flows into all
derived surfaces with no other edit.

**Acceptance Scenarios**:

1. **Given** a declared category with zero posts, **When** the blog index and navigation render,
   **Then** the category appears as a valid, selectable filter with a graceful empty state and no
   broken markup, dangling link, or error.
2. **Given** the taxonomy is ready for Android/architecture topics, **When** a future note in such a
   category is committed and the site is built, **Then** it appears across all derived surfaces with
   no structural change and no edit beyond that one note.
3. **Given** no fabricated content is permitted, **When** the published set is inspected, **Then** it
   contains exactly the posts the author wrote — the feature adds structure, never posts.

---

### User Story 3 - Any heading in a post is precisely deep-linkable for citation (Priority: P3)

A reader or an AI assistant that wants to cite a specific section of a post can link directly to that
heading with a stable URL fragment, instead of linking to the whole page. The anchors are
deterministic (the same heading yields the same fragment on every build), collision-free within a
page, and invisible by default so the locked visual design is unchanged.

**Why this priority**: Section-level deep links are a concrete GEO/citation win — they let assistants
attribute a claim to an exact passage and let readers share precise references — and they are cheap
and design-neutral. They depend only on the rendering pipeline, not on the identity work, but they
rank below positioning because positioning is the primary objective.

**Independent Test**: Build the site; for each post, confirm every body heading carries a stable,
unique fragment identifier; rebuild and confirm the identifiers are byte-identical; load a post at a
heading fragment and confirm the browser scrolls to that heading with no visual change to the page.

**Acceptance Scenarios**:

1. **Given** any post with multiple headings, **When** the post page is built, **Then** every body
   heading carries a fragment identifier that is unique within the page and derived deterministically
   from the heading text.
2. **Given** two builds of identical content, **When** the heading identifiers are compared, **Then**
   they are byte-identical between builds (stable across rebuilds).
3. **Given** a post page opened at a heading fragment, **When** it renders, **Then** the page looks
   exactly as before (no new visible affordance is forced; any optional hover affordance is minimal
   and design-faithful) and the target heading is navigable.

---

### User Story 4 - The highest-traffic page is measurably lighter, with proven fidelity (Priority: P3)

The portfolio homepage — the highest-traffic page — inlines a large block of web-font data, most of
which covers writing systems the page never displays. That dead weight is removed one time so the
page is materially smaller and faster, while a deterministic, offline proof guarantees the page looks
exactly the same: every character the page actually renders keeps its font coverage, and nothing
other than the unused font data changes.

**Why this priority**: Page weight on the most-visited page is a direct Core Web Vitals and
first-impression cost, and the unused font subsets are the single largest, safest target. It is
ranked alongside deep-linking (both are high-value completions) but gated strictly: it is the only
change that edits the portfolio source outside a managed region, so it ships **only** if its fidelity
is proven, and is otherwise deferred with the rest of the feature still delivered.

**Independent Test**: Measure the portfolio page size before and after; confirm a meaningful
reduction; run the offline fidelity proof and confirm (a) every codepoint the page renders that had
font coverage still has it, and (b) the page is byte-identical outside the sanctioned font-data zone;
confirm no new CI or runtime dependency was introduced.

**Acceptance Scenarios**:

1. **Given** the portfolio page, **When** its served size is measured before and after, **Then** the
   page is meaningfully smaller (the unused font subsets are gone) and no visible change occurs.
2. **Given** the optimized page, **When** the fidelity proof runs offline, **Then** it confirms every
   rendered codepoint retains the font coverage it had originally and that nothing outside the
   sanctioned font-data zone changed; the original font data remains recoverable.
3. **Given** the fidelity proof cannot be satisfied, **When** the feature ships, **Then** the fonts
   are left untouched (deferred with a recorded reason) and every other part of the feature still
   ships — the build and verifier stay green.

---

### User Story 5 - Inherited 002 gaps are closed and the quality gate is hardened (Priority: P4)

The maintainer can trust that the governance and quality scaffolding is correct and self-defending:
the v1.2.0 constitution amendment is finalized, the unified-identity profile links are confirmed
exactly correct and locked against drift, the Definition-of-Done verifier asserts the
identity/locale/article-tag signals that 002 left leaning on pre-existing behavior, and the spec
status metadata reflects reality (implemented features are not still labeled "Draft").

**Why this priority**: These are correctness, safety, and hygiene fixes carried over from the 002
review. They are low-risk and high-certainty, and they make US1's identity benefit durable (a drifted
profile link silently splits the identity), but they are supporting work, so they rank last.

**Independent Test**: Confirm the constitution amendment is finalized with a correct Sync Impact
Report and version; confirm the verifier fails loudly if the blog's profile links diverge from the
portfolio's, if author/locale signals are inconsistent, or if a post is missing its tag/keyword
signals; confirm no implemented spec is still labeled "Draft".

**Acceptance Scenarios**:

1. **Given** the blog and portfolio author profile links, **When** the verifier runs, **Then** it
   asserts they match exactly and fails the build if any value diverges.
2. **Given** any post page, **When** the verifier runs, **Then** it asserts the author, content
   language/locale, and per-post tag/keyword + article-tag signals are present and consistent, and
   fails on any omission.
3. **Given** the prior feature specs, **When** their status is read, **Then** implemented features are
   marked as implemented (not "Draft"/"Ready for Planning"), and this feature's status reflects its
   real progress.

### Edge Cases

- **Empty Android/architecture categories**: Declared categories with no posts MUST render a valid,
  selectable, gracefully-empty state across navigation, index, and any structured data — never a
  broken list or dangling link. The identity signal MUST remain valid and grounded even though those
  categories are empty (no claim of posts that do not exist).
- **Heading-text collisions within a post**: Two headings with the same text MUST still yield
  distinct, deterministic fragment identifiers (a stable disambiguation), so anchors stay unique and
  reproducible.
- **A heading whose text has no usable characters for an identifier** (e.g. punctuation/emoji only):
  The system MUST still produce a stable, unique, deterministic fragment rather than an empty one.
- **A future post in a currently-empty category**: MUST flow into every derived surface with no
  structural change and no edit beyond that one note (proves the scaffold).
- **Font fidelity cannot be proven**: The font optimization MUST be deferred (fonts untouched, reason
  recorded) while the rest of the feature ships; the build and verifier stay green.
- **A rendered character covered only by a font subset proposed for removal**: MUST block that
  removal (prove-or-defer) so no visible glyph ever loses coverage.
- **Identity drift**: If the blog's author profile links or job title diverge from the portfolio's,
  the verifier MUST fail loudly rather than silently ship two competing identities.
- **No posts / drafts only**: Every surface (identity signals, anchors, feed, `llms.txt`, homepage
  region) MUST still degrade gracefully, exactly as today.

## Requirements *(mandatory)*

### Functional Requirements

**Positioning & grounded identity (Principle V, VIII)**

- **FR-001**: The blog's author identity MUST be expressed as the **one** canonical person shared with
  the portfolio (same stable identifier), never a second look-alike entity.
- **FR-002**: That author identity MUST carry grounded professional signals — at minimum a Senior
  Android Engineer job title and a list of areas of expertise/skills — sourced **verbatim** from what
  the portfolio already asserts; no skill, title, or topic may be introduced that is not already
  present in the portfolio or the existing posts.
- **FR-003**: The identity signals MUST frame the published developer-tooling/code-generation writing
  as part of an Android engineer's skill set (the tooling topics co-occur with the Android
  engineering skills under one person), so engines resolve the posts as an Android engineer's tooling
  work rather than a separate "Python developer" identity.
- **FR-004**: The blog's author profile links (the external `sameAs` profile set) MUST be **exactly**
  equal to the portfolio's — same URLs, same order — so the unified-identity benefit is not lost to a
  divergent or stale link.
- **FR-005**: No blog content may be fabricated. The feature MUST add identity/topic **structure**
  only; the published post set MUST remain exactly what the author wrote.

**Taxonomy readiness & graceful degradation (Principle I, VI, VIII)**

- **FR-006**: Every declared category — including Android-relevant ones with zero posts (e.g. Compose,
  Architecture) — MUST render as a valid, crawlable, selectable navigation entry with a graceful
  empty state and no broken markup, dangling link, or error.
- **FR-007**: A future post in any declared category MUST flow into every derived surface (navigation,
  index, post page, sitemap, feed, `llms.txt`, homepage notes, structured data) with no structural
  change and no edit beyond that one note.
- **FR-008**: The taxonomy and identity signals MUST stay valid and grounded while categories are
  empty (no assertion of content that does not exist).

**Section-level deep-citability (Principle I, V, VI, VIII)**

- **FR-009**: Every body heading on every post page MUST carry a fragment identifier that is unique
  within that page and derived **deterministically** from the heading text (same heading → same
  identifier on every build).
- **FR-010**: Heading fragment identifiers MUST be byte-stable across rebuilds of identical content
  (no build-to-build churn), and collision-free even when two headings share the same text.
- **FR-011**: Heading anchors MUST be present in the served static HTML (no client-side generation)
  and MUST NOT alter the locked visual design: invisible by default, with at most a minimal,
  design-faithful optional affordance (or none). Exactly one `<h1>` per page is preserved; anchors
  apply to body headings, not the title.

**Highest-traffic-page performance (Principle VI, VII)**

- **FR-012**: The portfolio's inlined font data MUST be reduced by removing the font subsets the page
  does not render, cutting the served weight of the highest-traffic page, with **no** new CI or
  runtime dependency and **no** visual change.
- **FR-013**: The font optimization MUST occur within a single sanctioned, marker-delimited font-data
  zone in the portfolio source (constitution v1.3.0, Principle VII exception 2); everything outside
  that zone MUST stay byte-for-byte identical to its committed baseline, and the original font data
  MUST remain recoverable.
- **FR-014**: The font optimization MUST be gated by a deterministic, offline fidelity proof that
  asserts (a) every codepoint the portfolio renders that had web-font coverage in the original still
  has it (no visible glyph regresses), and (b) nothing outside the sanctioned font-data zone changed.
  If the proof cannot pass, the optimization MUST be **deferred** (fonts untouched, reason recorded)
  and the rest of the feature still shipped (**prove-or-defer**).

**Inherited fixes & governance (Principle VII, VIII, Workflow gate)**

- **FR-015**: The constitution amendment governing machine-readable discovery/single-source publishing
  (Principle VIII, v1.2.0) MUST be finalized — Sync Impact Report and template propagation confirmed
  correct, any incompleteness corrected — and any new amendment required by this feature (the
  performance-only font-data exception) MUST follow proper versioning with a Sync Impact Report.
- **FR-016**: Implemented prior-feature specs MUST NOT be labeled with a pre-implementation status
  ("Draft"/"Ready for Planning"); their status MUST reflect that they are implemented, and this
  feature's status MUST reflect its real progress.

**Verification (Workflow gate)**

- **FR-017**: The Definition-of-Done verifier MUST assert every new invariant in this feature and fail
  the build on any violation: (a) grounded identity signals present and valid on post and index pages
  (canonical person reference, Senior Android Engineer job title, grounded skills list) with no
  fabricated value; (b) the blog `sameAs` profile set exactly equals the portfolio's; (c) author and
  content-language/locale consistency across pages; (d) per-post tag→keyword and `article:tag` signal
  presence; (e) deterministic, unique, present heading anchors on post pages; and (f) when the font
  optimization is applied, the font-fidelity proof (codepoint coverage preserved + nothing outside the
  sanctioned zone changed). Verifier coverage MUST grow beyond, and never regress below, the post-002
  baseline check count.
- **FR-018**: The build MUST remain deterministic (identical content → byte-identical output, all
  dates from frontmatter/constants, never the current date), static, and GitHub-Pages-only; no
  backend, no client-side content rendering, and no new runtime/CI dependency may be introduced.

### Key Entities *(include if feature involves data)*

- **Canonical author identity**: The single Person entity defined by the portfolio and referenced by
  the blog via a stable identifier. This feature enriches the signals the blog carries about it (job
  title, areas of expertise, profile links) using only grounded values; it does not create a second
  identity.
- **Category (taxonomy entry)**: A declared blog section. Some (Compose, Architecture) are Android-
  relevant and currently empty; they must render gracefully and be ready to receive content. No new
  authoring field is introduced.
- **Heading anchor**: A deterministic, unique, invisible fragment identifier attached to each body
  heading of a post, derived from the heading text — a new derived attribute of rendered content, not
  an authored field.
- **Sanctioned font-data zone**: The single marker-delimited region of the portfolio source whose
  inlined font data may be optimized once, non-visually, with a recoverable baseline and a fidelity
  proof. Everything outside it is immutable to this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: **100%** of post pages and the blog index carry author structured data that references
  the one canonical person (single stable identifier) and states the Senior Android Engineer job
  title with a grounded areas-of-expertise list — **zero** pages present a second or "Python
  developer"-only identity.
- **SC-002**: **100%** of the asserted identity signals (job title, every skill/topic, every profile
  link) are grounded — each appears verbatim in the portfolio or the existing posts; **zero**
  fabricated values.
- **SC-003**: The blog's author profile-link set equals the portfolio's **exactly** (same values, same
  order); the verifier fails if they ever diverge.
- **SC-004**: **Zero** blog posts are added, removed, or fabricated by this feature; declared empty
  categories render with **zero** broken/dangling markup.
- **SC-005**: **100%** of post body headings carry a unique, deterministic fragment identifier;
  identifiers are **byte-identical** across two builds of identical content (**zero** churn).
- **SC-006**: The portfolio page's served size is **meaningfully reduced** (target: at least the full
  weight of the unused non-Latin font subsets removed) **or** the optimization is explicitly deferred
  with a recorded reason — and in either case the page is **byte-identical** outside the sanctioned
  font-data zone and visually unchanged.
- **SC-007**: When applied, the font optimization passes an offline proof that **every** rendered
  codepoint retains its original coverage (**zero** glyph regressions) and **nothing** outside the
  sanctioned zone changed; the original font data is recoverable.
- **SC-008**: The constitution is finalized at a correct version with a complete Sync Impact Report,
  and **zero** implemented specs remain labeled with a pre-implementation status.
- **SC-009**: The build stays deterministic — identical content yields **byte-identical** output on
  repeat runs — with **no** new runtime/CI dependency and **no** client-rendered content.
- **SC-010**: The Definition-of-Done verifier passes with **0** failures and **more** checks than the
  post-002 baseline (163), covering every criterion above.

## Assumptions

- **Hosting & stack unchanged**: GitHub Pages only, no backend, no database, no paid service, no new
  runtime/CI dependency; the existing static generator and CI remain the delivery mechanism.
- **Design & portfolio fidelity**: The blog design and the portfolio are reproduced, not restyled; the
  portfolio source is touched only within the one new, non-visual, fidelity-proven font-data zone.
- **Single content source**: Posts remain authored as Obsidian Markdown notes with frontmatter; no new
  required authoring field is introduced; heading anchors and identity signals are derived, not
  authored.
- **Grounded identity, verbatim from the portfolio**: The canonical person is "Ehsan Kolivand", Senior
  Android Engineer, Istanbul, at `https://ehsankolivand.github.io/`. The job title and areas-of-
  expertise the blog asserts are taken verbatim from the portfolio's existing structured data (which
  already lists Android development, Kotlin, Jetpack Compose, MVI, MVVM, Clean/Multi-module
  architecture, Coroutines, Dagger/Hilt, Server-Driven UI, Android TV, **Spec-driven development**,
  and **Agentic code generation** — the last two being the grounded bridge between the Android
  identity and the code-generation tooling posts). Nothing beyond what the portfolio/posts already
  assert is introduced.
- **The tooling posts are evidence, not a separate identity**: The three published posts
  (offline interview practice, offline audio Anki decks, Telegram topic export) are Python
  developer-tooling write-ups that *demonstrate* the owner's tooling capability; the feature makes
  engines read them as an Android engineer's tooling work, without writing or implying any post.
- **Empty Android/architecture categories are intentional scaffolding**: Compose and Architecture are
  declared and empty by design; the feature ensures they degrade gracefully and are ready, without
  fabricating posts to fill them.
- **Font subsets are the safe performance target**: The portfolio renders Latin-script text only; the
  inlined Cyrillic/Cyrillic-ext/Greek/Vietnamese font subsets are unused and are the removal target.
  Latin coverage (including Latin-ext, for European names the Europe-targeting portfolio may add) is
  retained. The fidelity proof, not this assumption, is the gate.
- **Out of scope (with reason)**:
  - **Authoring any blog post** — the owner writes content; this feature prepares scaffolding only
    (Principle IV; no fabrication).
  - **Anything needing a backend** — on-site search, analytics, contact/email backends (Principle II,
    no backend).
  - **An RTL/Persian edition** — a separate epic (would require its own design/locale work; the font
    optimization deliberately retains only Latin coverage, consistent with the current single-locale
    site).
  - **Any visible redesign** — no restyle of the blog or portfolio; deep-link anchors are invisible
    and the font change is non-visual (Principle III, VII).

## Clarifications

### Session 2026-06-29

All questions were resolved autonomously (unattended Spec Kit run) toward the option that best serves
the objective and the constitution; each carries a one-line rationale.

- Q: Should the blog's author identity only *reference* the portfolio person, or also *mirror* the
  grounded job-title/skills into each page's author node? → A: **Reference by stable identifier AND
  mirror the grounded `jobTitle` + areas-of-expertise into the blog's author node.** *Rationale: the
  failure mode (US1) is a post read in isolation; the page must carry the Android-engineer signal
  itself rather than relying on an engine fetching the portfolio. Mirroring values that are taken
  verbatim from the portfolio reinforces the single-entity merge without fabricating anything.*
- Q: Heading deep-link affordance — invisible anchor id only, or add a visible on-hover "#"/¶ link? →
  A: **Invisible anchor id only; no visible affordance.** *Rationale: Principle III (design fidelity)
  — the locked design has no heading-link control; a stable `id` delivers full deep-linkability with
  zero visual change, while a hover "#" would invent UI the design never had.*
- Q: How are heading fragment identifiers derived, and how are same-text collisions disambiguated? →
  A: **Readable GitHub-style slug of the heading text (lowercase, ASCII-fold, non-alphanumerics →
  hyphens), with deterministic numeric suffixes (`-1`, `-2`, …) for repeats within a page; an
  all-symbol heading falls back to a stable `section-<n>` id.** *Rationale: human-readable + citable +
  deterministic + collision-free, reusing the project's existing `slugify` discipline; an opaque hash
  would be stable but unreadable and less useful for citation.*
- Q: How aggressive is the portfolio font subset — drop only non-Latin scripts, or also Latin-ext? →
  A: **Drop the four demonstrably-unused non-Latin subsets (Cyrillic, Cyrillic-ext, Greek, Vietnamese)
  and retain Latin + Latin-ext.** *Rationale: removes the unambiguous dead weight (the page renders
  no Cyrillic/Greek/Vietnamese) while keeping full Latin-script coverage — including the European
  diacritics a Europe-targeting portfolio may add — so the change is maximally safe; the fidelity
  proof, not this choice, is the gate.*
- Q: How is "nothing outside the font data changed" proven, and how is the original kept recoverable? →
  A: **Commit a one-time pre-optimization baseline of the portfolio (with the font-zone markers, full
  fonts) and have the verifier assert byte-equality outside the markers against that baseline + that
  every retained `@font-face` appears verbatim in it.** *Rationale: an explicit committed baseline
  makes the proof deterministic and fully offline and directly satisfies "keep the original font data
  recoverable", instead of relying on git archaeology; deferral simply means leaving the portfolio
  equal to the baseline.*

These decisions are reflected in the Functional Requirements and Assumptions above (identity mirroring
= FR-001/FR-002/FR-003; sameAs exactness = FR-004; heading anchors = FR-009/FR-010/FR-011; font drop
set + proof = FR-012/FR-013/FR-014). Deeper mechanics (exact schema.org properties, the slug function,
the marker text, and the verifier assertions) are specified in `plan.md` and the contracts.
