# Feature Specification: Best-in-Class SEO + GEO with One-Commit Publishing

**Feature Branch**: `002-seo-geo-publish`

**Created**: 2026-06-29

**Status**: Ready for Planning

**Input**: User description: "Elevate the site to best-in-class SEO and GEO, and make publishing a single-commit action. Audit and complete on-page SEO and structured data; maximize machine-readability and citation-friendliness for AI assistants; fix every SEO defect currently noted in PROJECT_CONTEXT.md (notably the stale committed homepage Field-notes region whose dangling seed-post links would 404, and any sitemap/canonical/lastmod inaccuracy); and automate the publish pipeline so the author edits and commits exactly one Markdown note and the build/CI updates every derived artifact with no second manual edit and no stale committed links. All changes stay static, build-time, deterministic, GitHub-Pages-only, and visually faithful to the existing design and portfolio."

## Overview

This site (an Obsidian-vault-driven static blog grafted onto a hand-built portfolio, hosted on
GitHub Pages) already generates SEO-complete static HTML. This feature takes it from *complete*
to *best-in-class* for two audiences — traditional search engines (SEO) and AI/generative
engines (GEO) — and closes the remaining publishing-automation gap so that adding or changing a
post is a single-commit action whose every downstream artifact is regenerated automatically and
correctly, with no source file ever left holding a link to something that no longer exists.

The work is an audit-and-complete pass plus a small set of new build-time machine-readable
surfaces. It introduces no backend, no client-side content rendering, and no runtime dependency;
it does not restyle the design or alter the portfolio outside its one managed region.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One-commit publishing with always-correct derived artifacts (Priority: P1)

The author writes or edits exactly one Markdown note under the content directory and commits it.
On the next build, every derived artifact updates to match — the post page, the blog index, the
sitemap, the syndication feed, the AI-facing `llms.txt`, and the homepage "Field notes" section —
with no second file to edit by hand. Critically, no committed source file is left pointing at a
post that does not exist: the homepage region in the committed source never carries
post-specific links that can rot into 404s between builds.

**Why this priority**: This is the product promise and the home of the single known live defect
(the committed homepage region still links to three deleted seed posts that would 404 if served
raw). If publishing needs a second manual edit, or the source can drift into dangling links, the
system is neither safe nor "best-in-class". Everything else builds on a trustworthy pipeline.

**Independent Test**: Add one new note and rebuild; confirm the new post appears in the page set,
index, sitemap, feed, `llms.txt`, and homepage notes with no other edits. Delete a note and
rebuild; confirm no artifact — and no committed source file — references the removed slug.

**Acceptance Scenarios**:

1. **Given** a new valid note is committed, **When** the site is built, **Then** the post page,
   blog index card, sitemap entry, feed entry, `llms.txt` entry, and homepage "Field notes" card
   all appear, and no other source file required editing.
2. **Given** a post is removed or its slug changes, **When** the site is built, **Then** no
   generated page, sitemap, feed, `llms.txt`, or homepage region links to the old slug, **and**
   no committed source file links to the old slug either.
3. **Given** the committed source is inspected directly (without building), **When** its internal
   links are checked, **Then** none point to a nonexistent blog page.

---

### User Story 2 - Best-in-class crawlability and rich-result eligibility (Priority: P2)

A search engine crawls the site without executing JavaScript and finds every page fully formed:
unique and accurate titles and descriptions, correct canonicals, complete social-card metadata,
an accurate sitemap with truthful last-modified dates, and valid structured data rich enough to
qualify for enhanced results (article, breadcrumb, and a unified author/site identity).

**Why this priority**: Ranking and rich results are the reason the site is static. Completing and
validating structured data and fixing any sitemap/canonical/lastmod inaccuracy is high-leverage
and low-risk, and it directly serves the owner's goal of being found for senior Android roles.

**Independent Test**: Fetch each page with scripting disabled; validate every page's structured
data against schema.org/Google rich-results expectations with zero errors; confirm the sitemap
lists exactly the live URLs with last-modified dates equal to each post's own modified date.

**Acceptance Scenarios**:

1. **Given** any page is fetched without JavaScript, **When** its head is inspected, **Then** it
   carries a unique title, a unique meta description, a correct canonical URL, Open Graph tags
   (including image dimensions and image alt text), and Twitter card tags.
2. **Given** any post page, **When** its structured data is validated, **Then** it contains a
   valid article entity with headline, author, publish/modified dates, image, section, and
   keywords, plus a valid breadcrumb trail, and references one canonical author identity.
3. **Given** the sitemap, **When** it is compared to the live page set, **Then** it lists the
   homepage, the blog index, and every published post — and only those — each with an accurate
   last-modified date, and the homepage's date never regresses below the portfolio's own date.

---

### User Story 3 - AI/generative engines can read and cite the site (GEO) (Priority: P3)

An AI assistant fetching the site (or fetching its `llms.txt`) can extract, attribute, and cite
its content reliably: all human-readable content and metadata are present in the served HTML
before any script runs; each page has a clean heading hierarchy and semantic landmarks; a concise
machine-readable summary and machine-readable dates are available; a syndication feed and an
`llms.txt` enumerate the posts; and the author is represented as one consistent entity across the
portfolio and the blog rather than two look-alikes.

**Why this priority**: Generative engines are an increasingly important discovery and citation
path, and the constraints that make a site citable (static content, clean semantics, stable
identity, machine indexes) are cheap to add and reinforce the SEO work. They depend on a correct
pipeline (US1) and complete page metadata (US2).

**Independent Test**: With scripting disabled, confirm full body text and metadata are in the
HTML; confirm a feed and an `llms.txt` exist and list every post with title, URL, and summary;
confirm the author entity in blog structured data resolves to the same identity as the portfolio.

**Acceptance Scenarios**:

1. **Given** any post page fetched without JavaScript, **When** its body is read, **Then** the
   full post text, title, dek, dates, and links are present in the static markup.
2. **Given** the site, **When** an assistant looks for machine indexes, **Then** it finds a
   syndication feed and an `llms.txt`, each listing every published post with a title, an
   absolute URL, and a one-line summary.
3. **Given** the blog's and portfolio's structured data, **When** the author is resolved, **Then**
   both reference the same canonical person identity (same stable identifier), not two separate
   entities.

---

### User Story 4 - Accessible, fast, layout-stable pages (Priority: P4)

A human reader — including one using a keyboard or a screen reader, or who prefers reduced motion —
gets pages that are accessible and fast: meaningful alt text, correct landmarks and a single page
title, keyboard-operable controls, sufficient contrast, motion that respects their preference, and
no layout shift as covers load.

**Why this priority**: Accessibility and Core Web Vitals are both user-facing quality and ranking
signals, and the constitution makes them non-negotiable. This pass must preserve them and improve
them where the SEO/GEO changes touch the same markup, never regress them.

**Independent Test**: Audit each page for one `<h1>`, landmarks, alt text, focus operability,
reduced-motion behavior, and intrinsic image dimensions; confirm no regression against the current
build.

**Acceptance Scenarios**:

1. **Given** any generated page, **When** it is audited, **Then** it has exactly one `<h1>`,
   `header`/`nav`/`main` landmarks, alt text on meaningful images, and decorative graphics marked
   as hidden from assistive tech.
2. **Given** a reader who prefers reduced motion, **When** they open a page, **Then** content is
   visible without animation and no motion is forced.
3. **Given** a cover image, **When** the page loads, **Then** the space it will occupy is reserved
   from intrinsic dimensions so no layout shift occurs.

### Edge Cases

- **No posts / drafts only**: The homepage region, blog index, sitemap, feed, and `llms.txt`
  MUST degrade gracefully (valid, post-free output) rather than emit broken or dangling markup.
- **Draft posts**: A draft MUST be excluded from **every** derived surface — post page, blog
  index, sitemap, feed, `llms.txt`, and homepage region — exactly as it is excluded today, so no
  unpublished content leaks into a machine-readable surface.
- **A post with an image cover**: Social/structured-data image metadata MUST use the cover's real
  intrinsic dimensions and alt text; a post without an image cover MUST fall back to the site
  default social image with correct default dimensions and alt text.
- **The homepage lacks the managed markers, or is absent**: The build MUST tolerate this (no
  crash) and still produce a correct site; the verifier MUST mirror that tolerance.
- **A note declares a related link to a missing post**: The build MUST warn and omit it rather
  than emit a dangling link.
- **A post's modified date equals or precedes its publish date**: dates surfaced to engines MUST
  remain self-consistent (modified ≥ published) and deterministic.

## Requirements *(mandatory)*

### Functional Requirements

**Publishing automation & source integrity (Principle VIII, IV, VII)**

- **FR-001**: Publishing or updating a post MUST require editing/committing exactly one Markdown
  note; no second source file may need manual editing for the change to fully propagate.
- **FR-002**: Every derived artifact — post pages, blog index, `sitemap.xml`, the syndication
  feed, `llms.txt`, and the homepage "Field notes" region — MUST regenerate automatically from
  content at build time.
- **FR-003**: No committed source file (including the portfolio homepage) may contain an internal
  link to a blog page that does not exist; the committed homepage region MUST NOT carry
  post-specific links that can become 404s between builds.
- **FR-004**: The portfolio homepage MUST remain byte-identical to its source outside the single
  managed "Field notes" region; the build MUST never modify the committed source homepage.
- **FR-005**: The build MUST remain deterministic — identical content produces byte-identical
  output, with all dates drawn from frontmatter or configured constants (never the current date).

**Crawlability & indexability (Principle I, V)**

- **FR-006**: Every page's full human-readable content and metadata MUST be present in the served
  HTML before any script runs; no content, link, or metadata may depend on client-side rendering.
- **FR-007**: `sitemap.xml` MUST list the homepage, blog index, and every published post (and only
  live URLs), each with a last-modified date equal to that resource's own modified date; the
  homepage entry's date MUST NOT regress below the portfolio's configured date.
- **FR-008**: Every page MUST declare a correct canonical URL using the one canonical site origin.
- **FR-009**: `robots.txt` MUST keep the whole site crawlable, explicitly welcome major search and
  AI citation/training agents, and point to the sitemap.
- **FR-010**: All internal links and category navigation MUST appear as real anchors in the static
  HTML, and none may resolve to a nonexistent page.

**Metadata completeness & uniqueness (Principle V)**

- **FR-011**: Every page MUST carry a unique, descriptive `<title>` and a unique meta description.
- **FR-012**: Every page MUST carry complete Open Graph metadata including image, image
  dimensions, and image alt text, and complete Twitter card metadata including image alt text.
- **FR-013**: Every page MUST declare author, content language, and locale consistently; posts
  MUST surface their tags as keywords and article tags.
- **FR-014**: Identity MUST be consistent everywhere: one canonical absolute URL and one author
  identity ("Ehsan Kolivand", Senior Android Engineer, Istanbul), matching the portfolio.

**Structured data (Principle V, VIII)**

- **FR-015**: Each post page MUST embed a valid article entity (headline, description, image,
  publish date, modified date, author, section from category, keywords from tags, language) and a
  valid breadcrumb trail (home → blog → post).
- **FR-016**: The blog index MUST embed a valid blog + website structured-data graph listing the
  posts, plus a breadcrumb trail (home → blog).
- **FR-017**: Blog structured data MUST reference the portfolio's canonical author (Person) and
  site (WebSite) by stable identifier so engines resolve the portfolio and blog as one entity.
- **FR-018**: All embedded structured data MUST be syntactically valid and free of fabricated
  claims (no properties asserting capabilities the static site does not have).

**GEO / machine-readable surfaces (Principle VIII)**

- **FR-019**: The build MUST generate a standards-compliant syndication feed listing every
  published post with title, link, identifier, publish/updated dates, summary, and author; the
  feed-level updated date MUST be deterministic (derived from post dates).
- **FR-020**: Blog pages MUST advertise the feed via a feed-autodiscovery link in the head.
- **FR-021**: The build MUST generate an `llms.txt` that, in addition to the site/author summary,
  enumerates every published post with its title, absolute URL, and a one-line summary.
- **FR-022**: Each page MUST use clean semantic landmarks and a correct heading hierarchy (exactly
  one `<h1>`), and surface key dates in a machine-readable form.

**Performance & accessibility (Principle VI)**

- **FR-023**: Cover and body images MUST declare intrinsic dimensions so no cumulative layout
  shift occurs; the primary display fonts MUST be preloaded.
- **FR-024**: Every page MUST preserve accessibility: meaningful alt text, decorative graphics
  hidden from assistive tech, keyboard-operable controls, sufficient contrast, and motion gated on
  the reduced-motion preference. No accessibility regression against the current build is allowed.

**Verification (Workflow gate)**

- **FR-025**: The post-build verifier MUST assert every new invariant above — valid new structured
  data (breadcrumb, unified identity), feed present and well-formed and complete, `llms.txt`
  present and complete, no dangling internal links in committed source or built output, and
  canonical/last-modified correctness — and MUST fail the build on any violation. Verifier
  coverage MUST expand beyond, and never regress below, the current check count.

### Key Entities *(include if feature involves data)*

- **Post**: One authored Markdown note → one page at `/blog/<slug>/`. Carries the metadata that
  feeds every derived surface (title, dates, category/section, tags/keywords, excerpt/summary,
  cover with optional intrinsic image, canonical, social description). No new authoring fields are
  required by this feature.
- **Derived artifacts**: The sitemap, the syndication feed, `llms.txt`, the per-page structured-
  data graph, and the homepage "Field notes" region — all generated from Posts, none authored by
  hand.
- **Canonical identity**: The single author (Person) and site (WebSite) entity, defined by the
  portfolio and referenced by the blog via a stable identifier.
- **Managed homepage region**: The single bounded section of the portfolio the build may
  regenerate; in committed source it MUST stay free of post-specific (rot-prone) links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Publishing a new post requires editing/committing exactly **one** file; after a
  build, **100%** of derived surfaces (post page, blog index, sitemap, feed, `llms.txt`, homepage
  notes) reflect it with **zero** additional manual edits.
- **SC-002**: **Zero** internal links — in any committed source file or any built page — resolve
  to a nonexistent page (the known stale-homepage defect reaches zero and stays zero).
- **SC-003**: **100%** of pages expose complete, unique titles and descriptions and embed
  structured data that validates with **zero** errors.
- **SC-004**: **100%** of published posts appear in the sitemap, the feed, and `llms.txt`, each
  with an accurate last-modified/updated date; the sitemap contains **no** stale or extra URLs.
- **SC-005**: **100%** of post body content and page metadata is present in the served HTML before
  any script runs (verifiable with scripting disabled).
- **SC-006**: Every page has exactly **one** `<h1>`, semantic landmarks, alt text on meaningful
  images, and **zero** layout shift from covers (intrinsic dimensions always present).
- **SC-007**: The portfolio homepage is **byte-identical** to its prior source outside the single
  managed region.
- **SC-008**: The build is deterministic — identical content yields **byte-identical** output on
  repeat runs.
- **SC-009**: The author resolves to **one** identity across portfolio and blog structured data
  (single stable identifier), not two.
- **SC-010**: The Definition-of-Done verifier passes with **0** failures and **more** checks than
  the current baseline (90), covering every criterion above.

## Assumptions

- **Hosting & stack unchanged**: GitHub Pages only, no backend, no database, no paid service, no
  new runtime dependency; the existing static generator and CI remain the delivery mechanism.
- **Design & portfolio fidelity**: The existing blog design and the portfolio are reproduced, not
  restyled; the portfolio is touched only within its single managed region.
- **Single content source**: Posts remain authored as Obsidian Markdown notes with frontmatter;
  no new required authoring field is introduced (new surfaces derive from existing fields).
- **No on-site search endpoint exists** (static site, no backend), so a search-action claim in
  structured data is intentionally **out of scope** — asserting one would be a fabricated,
  non-functional capability.
- **No public X/Twitter handle is on record** for the author (the known profiles are GitHub,
  LinkedIn, Telegram), so a Twitter creator/site attribution is intentionally out of scope; the
  Twitter card itself (summary with large image) is kept.
- **Canonical identity** is "Ehsan Kolivand", Senior Android Engineer, Istanbul, at
  `https://ehsankolivand.github.io/`, matching the portfolio's existing structured data.
- **`llms.txt` is a best-effort GEO surface**: it is shipped as a low-cost citation aid with no
  assumed ranking guarantee, kept honest and accurate rather than relied upon as a lever.

## Clarifications

### Session 2026-06-29

All questions were resolved autonomously (unattended Spec Kit run) toward the option that best
serves SEO/GEO and the constitution; each carries a one-line rationale.

- Q: Which syndication feed format? → A: **Atom 1.0** at `/blog/feed.xml`. *Rationale: strictest
  and most deterministic (mandatory absolute dates + stable entry IDs), XML-validatable, and
  broadly consumed; RSS 2.0 date semantics are looser and JSON Feed is less consumed by SEO/feed
  tooling.*
- Q: How does `llms.txt` stay current on publish without a second manual edit? → A: **The build
  generates it** — the human-authored portfolio/identity base is preserved and the build appends a
  deterministic "Writing / latest notes" section enumerating every post (title, absolute URL,
  one-line summary). *Rationale: keeps `llms.txt` a derived artifact (single-commit publishing,
  Principle VIII) while the author still owns the identity prose.*
- Q: How are the stale committed homepage links eliminated permanently? → A: **Neutralize the
  committed managed region to a post-link-free fallback** (section heading + dek + a single "Read
  all notes → `/blog/`" link); the build still fully regenerates the region with live post cards
  for deploy. *Rationale: Principle VII forbids the build writing the source homepage, so a
  link-free committed region is the only way to guarantee no dangling links between builds, and it
  stays valid even if served raw (it links only to `/blog/`, which always exists).*
- Q: Add a visible on-page breadcrumb, or breadcrumb structured data only? → A: **Structured-data
  breadcrumb only**; no new visible breadcrumb UI. *Rationale: a visible breadcrumb would alter the
  locked design (Principle III); the existing "← All notes" back-link and Home nav already express
  the trail, and the BreadcrumbList is independently valid.*
- Q: Include a WebSite SearchAction (sitelinks search box) in structured data? → A: **Omit it.**
  *Rationale: the static site has no search endpoint (Principle II, no backend); a SearchAction
  with a non-functional target would assert a capability the site does not have and is a
  structured-data defect (FR-018).*

These decisions are reflected in the Functional Requirements and Assumptions above (feed = FR-019/
FR-020; `llms.txt` = FR-021; committed-region neutralization = FR-003; breadcrumb = FR-015/FR-016;
SearchAction omission = FR-018 + Assumptions). Two further low-risk decisions are encoded directly
in the requirements rather than asked: machine-readable on-page dates via a semantic time element
(FR-022, zero visual change), and code-cover posts falling back to the default social image with
its known dimensions and a site-identity alt (FR-012).
