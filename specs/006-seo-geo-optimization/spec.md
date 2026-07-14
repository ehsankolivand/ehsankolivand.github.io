# Feature Specification: SEO / GEO-AEO Optimization Refinement (Portfolio + Blog)

**Feature Branch**: `006-seo-geo-optimization` (work stays on `main`)

**Created**: 2026-07-14

**Status**: Draft

**Input**: User description: refinement cycle applying re-verified recommendations from `research/seo-brief.md` and `research/seo-brif-two.md` to both site surfaces, at the highest quality the constitution (v1.5.0) allows, leaving `main` green.

## Context & Framing

The site is a zero-backend personal site on GitHub Pages with two surfaces built by one Python
generator: a hand-authored portfolio `index.html` and an Obsidian-driven blog. Prior features
(002 SEO/GEO publish, 003 positioning/GEO/performance) already made both surfaces
schema-rich, entity-consistent, and Core-Web-Vitals-clean; the Definition-of-Done verifier
enforces 594 checks. **This is a refinement cycle, not a rebuild** — it closes the small, specific
gaps that remain between the current output and the two research briefs, whose recommendations
(with confidence labels and explicit "do not attempt" lists) are the authoritative baseline.

The briefs' load-bearing volatile facts were re-verified against primary Google/vendor sources on
2026-07-14 before this spec: Core Web Vitals thresholds are unchanged (LCP ≤ 2.5 s, INP ≤ 200 ms,
CLS ≤ 0.1 at p75); the "2.0 s LCP / March 2026 core update" claim remains fabricated with zero
primary support; the AI-crawler user-agent tokens are all confirmed (the new `OAI-AdsBot` is
ad-safety only, not a citation crawler; `Applebot`/`Applebot-Extended` are live); FAQPage, HowTo,
and the Sitelinks Search Box rich results are dead; ProfilePage, Article/BlogPosting/TechArticle,
and BreadcrumbList are live; and Google states verbatim that it ignores `llms.txt` and needs no
special files or markup for AI features.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — An AI answer engine cites a blog post as an Android engineer's first-hand work (Priority: P1)

When an AI answer engine (ChatGPT/Claude/Perplexity/Google AI Overviews) retrieves a single blog
post URL at query time, that page alone should let the engine resolve *who* wrote it, *what* they
do, and that the post is part of one coherent professional identity — without also having to crawl
the index or portfolio. Today a post page links the author only inside JSON-LD (`author.@id`) and
shows a text-only byline; it does not carry the site-level `WebSite` entity node, and the visible
byline is not a followable link to the author's home page.

**Why this priority**: AI citation is passage/page-level and pulls individual post URLs; making each
post self-contained for entity resolution and adding a real author link is the highest-leverage
GEO + E-E-A-T improvement available, and it is squarely inside Principles I/V/VIII.

**Independent Test**: Build the site; open any `/blog/<slug>/index.html`; confirm (a) the visible
byline "Ehsan Kolivand" is a real `<a href="/">` crawlable anchor to the author/entity page, and
(b) the page's JSON-LD contains a `WebSite` node whose `@id` equals the canonical `#website` and
whose `publisher`/author resolves to the canonical `#person`, while `BlogPosting` remains the first
`ld+json` script. The verifier passes with 0 failures.

**Acceptance Scenarios**:

1. **Given** a rendered post page, **When** a crawler reads only that page, **Then** it finds a
   `BlogPosting` (first script) authored by `#person`, a `BreadcrumbList` ending at the post
   canonical, and a `WebSite` node keyed to `#website` referencing `#person` — one unified entity.
2. **Given** a rendered post page, **When** a user or crawler follows the visible byline, **Then**
   it navigates to the portfolio home (`/`), the canonical `Person.url`, via a real anchor (not
   script-dependent), with the byline's appearance unchanged.

### User Story 2 — A search/AI crawler discovers the freshness feed and full crawl directives from the portfolio (Priority: P2)

A crawler landing on the portfolio home page should be able to auto-discover the site's Atom feed
and read complete robots/preview directives, exactly as it can on every blog page. Today the
portfolio `<head>` omits the Atom autodiscovery `<link>` and the `robots` meta that the blog pages
carry, and its ProfilePage node lacks the recommended `dateCreated`/`dateModified` freshness
signals.

**Why this priority**: Per-page SEO/GEO completeness (Principle V) and machine-readable discovery
(Principle VIII) should hold on *every* page, including the highest-traffic one. These are additive,
design-neutral, identity-preserving head items.

**Independent Test**: Build; open `_site/index.html`; confirm it contains the Atom autodiscovery
`<link rel="alternate" type="application/atom+xml">`, `<meta name="robots" content="index, follow,
max-image-preview:large">`, and a ProfilePage carrying `dateCreated` + `dateModified`; confirm the
`#person`/`#website` `@id`s, both marker zones, the single `<h1>`, and every robot hook are intact,
and the portfolio stays byte-identical outside these sanctioned additions. Verifier passes.

**Acceptance Scenarios**:

1. **Given** the built portfolio page, **When** a crawler parses its `<head>`, **Then** it finds
   feed autodiscovery, a large-image-preview robots directive, and ProfilePage freshness dates,
   matching the completeness of blog pages.
2. **Given** the built portfolio page, **When** the verifier compares it to source, **Then** it
   confirms marker zones present-and-paired-once, identity `@id`s unchanged, one `<h1>`, and robots
   present — 0 failures.

### User Story 3 — Crawlers reach the site fast and cleanly, and the confirmed crawler set is complete (Priority: P3)

The portfolio should not waste connections or leak requests to third parties it never uses, and the
site's robots policy should welcome every confirmed search/AI-citation crawler. Today the portfolio
opens two dead `preconnect` connections to Google Fonts hosts (all fonts are self-hosted and
inlined; nothing loads from Google), and `robots.txt` — while already allowing all the major
search/AI tokens — omits the confirmed-live `Applebot` search crawler.

**Why this priority**: A pure Core-Web-Vitals + privacy cleanup (Principle VI) and a small,
confirmed discovery completeness gain; both are low-risk and independent of the P1/P2 work.

**Independent Test**: Confirm the built portfolio no longer references `fonts.googleapis.com` or
`fonts.gstatic.com`; confirm `robots.txt` allows `Applebot` and still declares the sitemap and all
prior tokens; confirm no visual/functional regression and the verifier passes.

**Acceptance Scenarios**:

1. **Given** the built portfolio, **When** the browser parses `<head>`, **Then** there are no
   `preconnect`/connection hints to Google Fonts hosts, and rendering is visually identical.
2. **Given** `robots.txt`, **When** a crawler reads it, **Then** `Applebot` is allowed, the sitemap
   is declared, and every previously-allowed search/AI-citation token is still present.

### Edge Cases

- **Zero posts**: With no published posts, per-post additions do not run; the portfolio head
  additions and robots/preconnect changes still apply and the build stays green (build already
  tolerates an empty blog).
- **First-script contract**: Adding a `WebSite` node to posts must not displace `BlogPosting` as the
  first `application/ld+json` script (the verifier reads the first script as the `BlogPosting`).
- **Identity drift**: No identity fact (name, role, `@id`s, `sameAs`, `knowsAbout`) changes this
  cycle; if any structured-data identity value were ever touched, it must change in both
  `scripts/blog/config.py` and portfolio `index.html` together, or the verifier's identity-equality
  checks fail by design.
- **Determinism**: Any date added to the portfolio (ProfilePage `dateCreated`/`dateModified`) must
  be a fixed constant, never `today()`, to keep the build byte-deterministic.
- **Byte-identity check**: Because the build copies `index.html` and only rewrites the LATEST-NOTES
  region, portfolio-source edits are reflected in the build and the verifier's "unchanged outside
  the managed notes region" check still holds (it compares built vs. source).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every generated blog post page MUST render its visible author byline as a real,
  crawlable anchor to the author/entity page (`/`), with the byline's visual appearance unchanged
  (color/weight/spacing preserved; no new color or font).
- **FR-002**: Every generated blog post page MUST include a `WebSite` structured-data node whose
  `@id` equals the canonical `#website` and which references the canonical `#person`, so each post
  URL carries the unified single-entity graph — WITHOUT displacing `BlogPosting` as the first
  `application/ld+json` script on the page.
- **FR-003**: The portfolio `<head>` MUST include Atom feed autodiscovery
  (`<link rel="alternate" type="application/atom+xml">`) pointing at the generated blog feed, matching
  the autodiscovery already present on blog pages.
- **FR-004**: The portfolio `<head>` MUST include a `robots` meta directive granting index/follow and
  large image preview, at parity with blog pages.
- **FR-005**: The portfolio ProfilePage structured-data node MUST carry `dateCreated` and
  `dateModified` freshness signals, sourced from a fixed, deterministic date constant.
- **FR-006**: The portfolio MUST NOT emit resource hints (`preconnect`/`dns-prefetch`) or any request
  to `fonts.googleapis.com` or `fonts.gstatic.com`, since no resource loads from them.
- **FR-007**: `robots.txt` MUST allow the `Applebot` crawler, continue to allow every previously
  allowed search/AI-citation crawler token, and continue to declare the sitemap URL.
- **FR-008**: All changes MUST regenerate deterministically through the generator, templates, config,
  robots source, or additive/design-neutral portfolio-head edits — same inputs produce byte-identical
  output; no change may hand-edit generated HTML.
- **FR-009**: The JSON-LD identity constants in `scripts/blog/config.py` MUST remain equal to the
  portfolio `index.html` Person/WebSite JSON-LD after this cycle (this cycle introduces no identity
  fact changes; the `WebSite` node added to posts reuses the existing `#website`/`#person` `@id`s).
- **FR-010**: The portfolio's non-marker regions MUST stay intact and both marker zones
  (LATEST-NOTES, PORTFOLIO-FONTS) MUST remain present and paired exactly once; every page MUST keep
  exactly one `<h1>`; the robot characters and their reactive animations MUST remain present on both
  surfaces; `prefers-reduced-motion` MUST stay honored.
- **FR-011**: No constitution amendment and no weakening/relaxing of any `scripts/verify_build.py`
  check may be used to land any requirement; if a brief recommendation cannot be met inside the
  current gates it MUST be recorded as out-of-scope-by-constraint, not forced.

### Key Entities

- **Canonical Person / WebSite identity**: One `Person` (`#person`) and one `WebSite` (`#website`),
  shared verbatim between the portfolio and the blog generator config; the anchor that makes search
  and AI engines merge both surfaces into a single entity.
- **Per-post structured-data graph**: The set of JSON-LD nodes on each post URL — `BlogPosting`
  (first), `BreadcrumbList`, and (new) `WebSite` — that lets a single post page stand alone for
  entity resolution.
- **Machine-readable discovery surfaces**: `sitemap.xml`, the Atom feed (`/blog/feed.xml`),
  `llms.txt`, and `robots.txt` — all build-generated or committed-and-copied, all consistent with
  one canonical base URL and trailing-slash policy.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `python -m unittest discover -s tests`, `python scripts/build_blog.py --out _site`, and
  `python scripts/verify_build.py --out _site` all pass locally, with the verifier reporting ≥ 594
  checks and 0 failures.
- **SC-002**: 100% of generated blog post pages present a real crawlable author-byline anchor to `/`
  and a `WebSite` JSON-LD node keyed to `#website`, while `BlogPosting` remains the first `ld+json`
  script on every post.
- **SC-003**: The portfolio page carries Atom autodiscovery, a large-image-preview `robots` meta, and
  ProfilePage `dateCreated`/`dateModified`, and contains zero references to Google Fonts hosts.
- **SC-004**: Every generated page still has exactly one `<h1>`, a trailing-slash self-referencing
  canonical, complete meta + Open Graph + Twitter tags, and valid JSON-LD whose identity `@id`s
  resolve to one `Person` and one `WebSite` across the portfolio and the blog.
- **SC-005**: `sitemap.xml` lists only canonical, 200-status URLs with accurate `lastmod`;
  `robots.txt` allows the confirmed crawler tokens (including `Applebot`) and declares the sitemap;
  every internal link, byline, and navigation target is a real crawlable anchor with no dangling
  targets.
- **SC-006**: Re-running the build twice from the same inputs produces byte-identical output
  (determinism preserved), and the portfolio is byte-identical to source outside the sanctioned
  additive head edits and the managed notes region.

## Assumptions

- The two research briefs in `research/` are the authoritative baseline; their confidence labels and
  "do not attempt" lists govern scope (gitignored reference material, never deployed or linked).
- The portfolio `index.html` IS the canonical author/"about" page (`Person.url = "/"`); no separate
  `/about/` page is needed, so the blog byline links to `/`.
- At ~6 posts (well below the "few thousand URLs" crawl-budget threshold), dedicated crawlable
  tag/archive/pagination pages are unnecessary; all posts are already real anchors on the index and
  in the sitemap, and category filtering is client-side hash-based with no thin stub pages — which
  the brief prefers at this scale.
- The site owner wants maximum search + AI-citation visibility (existing robots allows all major AI
  bots; `Applebot` is added in the same spirit); training-bot posture is unchanged this cycle.
- All work stays on `main`; the safepoint before this cycle is already committed and pushed.

## Out of Scope — by constraint (recorded, deliberately not implemented)

- **TechArticle `@type` for tutorial posts**: the verifier hard-requires `@type == "BlogPosting"` on
  post JSON-LD; switching type would require weakening a gate. Not done.
- **FAQPage / HowTo / Sitelinks-SearchBox schema**: deprecated/dead rich results and on the briefs'
  do-not-attempt list. Not added.
- **Dedicated crawlable tag/archive/pagination pages**: not needed at this scale; would create thin
  pages the brief warns against. Not created.
- **A separate `/about/` author page**: the portfolio is the canonical author page. Not created.
- **Answer-first heading rewrites / new Person factual claims (e.g. `knowsLanguage`)**:
  editorial/content-side and subject to no-fabrication; this cycle optimizes the machinery and
  existing content, not the authoring pipeline. Not done.
- **Treating `llms.txt` as a ranking/citation lever**: kept as non-load-bearing machine-readable
  discovery only, consistent with Google's stated position.
- **Any backend, dynamic rendering, analytics endpoint, new runtime/build/CI dependency, paid tool,
  new font family, new color system, or client-rendered content**: forbidden by the constitution;
  not attempted.
