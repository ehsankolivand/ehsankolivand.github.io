# Feature Specification: Obsidian-Vault-Driven Blog

**Feature Branch**: `001-obsidian-blog`

**Created**: 2026-06-27

**Status**: Draft

**Input**: User description: "Build an Obsidian-vault-driven blog for the personal site, generating static pages on GitHub Pages. The author writes each post as a single Obsidian markdown note with YAML frontmatter and commits it; on push the blog index plus a new static post page are generated — correctly categorized, SEO-complete, in the existing design, with related 'More notes' resolved from links the author placed at the end of the post."

## Overview

The personal site (`https://ehsankolivand.github.io/`) is a static, GitHub-Pages-hosted
portfolio. This feature adds a blog whose **only authoring surface is an Obsidian markdown
note**: the author writes one note with YAML frontmatter, optionally links a few related
posts at the bottom, commits, and pushes. From those notes the site produces a static blog
index and one static page per post, matching the **already-designed** blog look, complete
with per-page SEO/GEO metadata, and listed in `sitemap.xml`.

The defining product constraint: because the site has no backend and must rank in search
engines and be readable by AI assistants, **every post's content and metadata must be
present in the static HTML that is served** — never produced only by client-side script.

## Clarifications

### Session 2026-06-27

These ambiguities were resolved with best-practice defaults (no blocking questions remained
that lacked a reasonable default). Each decision materially affects the data model, renderer,
or build behavior.

- Q: How are code blocks rendered — token-level syntax highlighting, or the design's style?
  → A: Match the design exactly — preformatted monospace in the existing code-card (traffic-light
  header + caption + single mint code color); **no syntax-highlighting library and no client JS**
  for code, preserving design fidelity and Principle I.
- Q: How are image covers handled vs. the code-style cover?
  → A: Support both. A code-style cover (glyph + caption) is the design default; an image cover
  is a frontmatter image path that the build copies into `/blog/assets/media/` and renders with
  explicit width/height and alt text (no layout shift, Principle VI).
- Q: How is a post's slug / permalink determined and kept stable?
  → A: `slug = frontmatter.slug || kebab-case(title)`. The slug is the canonical, stable permalink
  (`/blog/<slug>/`); duplicate slugs are a hard build error (no silent overwrite).
- Q: What feeds `datePublished`, `dateModified`, and sitemap `lastmod`?
  → A: frontmatter `date` = `datePublished`; an optional frontmatter `updated` = `dateModified`
  (falls back to `date`); sitemap `lastmod` = `updated || date`.
- Q: Where does the author declare the canonical category set?
  → A: A single, documented categories-definition file in the content directory (an ordered list
  of `{ name, label }`); the index nav, post chips, and `articleSection` all derive from it. An
  "All" view is always shown first and is not part of that file.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publish a post from one Obsidian note (Priority: P1) 🎯 MVP

The author writes a single markdown note in their Obsidian vault with YAML frontmatter
(title, date, category, tags, excerpt, cover, optional slug/SEO/draft), writes the body in
normal markdown, commits, and pushes. The site then has a new static post page in the
existing design and the post appears on the blog index and in the sitemap.

**Why this priority**: This is the core promise of the feature and the smallest slice that
delivers value. Without it, nothing else matters. It alone is a usable product: the author
can publish.

**Independent Test**: Add one markdown note with valid frontmatter, run the build, and
confirm a static post page exists whose served HTML contains the post's title, body text,
and SEO tags, that it is reachable from the index, and that it is in `sitemap.xml` — all
without executing JavaScript.

**Acceptance Scenarios**:

1. **Given** a markdown note with complete frontmatter and a markdown body, **When** the
   build runs, **Then** a static post page is generated at the post's URL whose initial
   HTML contains the rendered body content, the title as a single `<h1>`, the category, the
   date, and the read time, in the existing post-page design.
2. **Given** that generated post page, **When** its raw HTML is inspected without running
   scripts, **Then** it contains a correct `<title>`, meta description, canonical URL,
   Open Graph tags, Twitter card tags, and Article/BlogPosting JSON-LD derived from the
   frontmatter.
3. **Given** the post was generated, **When** the build completes, **Then** the post is
   listed on the blog index and added to `sitemap.xml` with a `lastmod`.
4. **Given** a note whose frontmatter sets `draft: true`, **When** the build runs, **Then**
   the post is excluded from the index, post pages, and sitemap.
5. **Given** a note with no `readTime` in frontmatter, **When** the build runs, **Then** a
   read time is computed from the body and shown; **and** when `readTime` is provided it is
   used verbatim.

---

### User Story 2 - Browse and filter the index by category (Priority: P2)

A reader lands on the blog index and sees a featured post plus a grid of post cards (cover,
category, title, excerpt, date, read time). A top category navigation (an "All" view plus
the author-defined categories) lets them narrow the list. Every post link is a real,
crawlable link.

**Why this priority**: The index is how readers and crawlers discover posts. It is required
for the blog to function as a blog, but it depends on posts existing (US1).

**Independent Test**: With several posts across categories, build the site and confirm the
index's served HTML lists every non-draft post as a real anchor, shows a featured post plus
a grid, and that selecting a category narrows the visible posts to that category, with "All"
showing everything.

**Acceptance Scenarios**:

1. **Given** several non-draft posts, **When** the index is generated, **Then** its initial
   HTML contains a featured post and a grid where each card shows cover, category, title,
   excerpt, date, and read time, and links to the post via a real anchor.
2. **Given** the category navigation, **When** a reader selects a category, **Then** only
   posts in that category remain visible and "All" restores the full list — implemented as
   progressive enhancement layered on already-present, crawlable links.
3. **Given** the canonical category list is declared by the author, **When** the author adds
   or reorders a category, **Then** the index navigation reflects that change without any
   code edit.

---

### User Story 3 - Related "More notes" from author-placed links (Priority: P3)

At the end of a post's markdown the author links a few other posts (Obsidian wikilinks
`[[...]]` or markdown links). On build, those links are resolved to the referenced posts and
rendered as the "More notes" related-post cards on that post's page, using the existing card
design. When the author links nothing, the section degrades gracefully (it is omitted or
falls back without error).

**Why this priority**: It enriches navigation and dwell time but the blog is fully usable
without it; it depends on posts and the post page (US1).

**Independent Test**: Author a post that links two existing posts at the bottom, build, and
confirm the post page's "More notes" section shows exactly those two posts as cards linking
to them; remove the links and confirm the section degrades gracefully with no broken markup.

**Acceptance Scenarios**:

1. **Given** a post whose body ends with links to other posts, **When** the build runs,
   **Then** the "More notes" section on that post shows cards for exactly the referenced,
   existing posts (in the author's order), each a real link.
2. **Given** a related link that does not resolve to an existing post, **When** the build
   runs, **Then** the build does not emit a broken card and surfaces the unresolved link as
   a warning rather than failing silently.
3. **Given** a post with no related links, **When** the build runs, **Then** the page omits
   or gracefully degrades the "More notes" section with valid markup.

---

### User Story 4 - Author-defined categories (Priority: P3)

The author declares the canonical category set — its membership, ordering, and display
labels — in a single documented place in the vault. The site's category navigation, the
per-post category chips, and the `articleSection` metadata all derive from that declaration.
A post assigns itself to exactly one category via frontmatter.

**Why this priority**: It keeps categories author-driven (a constitution requirement) but is
a refinement of US2's browsing; the blog can ship with the current four categories first.

**Independent Test**: Change the category declaration note (add a category, reorder, rename
a label), build, and confirm the navigation order/labels update and a post assigned to the
new category is filed correctly — with no change to build code.

**Acceptance Scenarios**:

1. **Given** the category declaration in the vault, **When** the build runs, **Then** the
   index navigation lists the categories in the declared order with the declared labels,
   plus the "All" view first.
2. **Given** a post whose frontmatter category is not in the declared set, **When** the
   build runs, **Then** the build surfaces a clear error/warning rather than silently
   mis-filing the post.

---

### Edge Cases

- **Missing required frontmatter** (e.g., no title or no category): the build fails with a
  clear, actionable message identifying the offending file, rather than producing a broken
  page.
- **Duplicate or colliding slugs**: the build detects the collision and reports it rather
  than overwriting one post with another.
- **Special characters / non-ASCII in titles, excerpts, and code**: rendered and escaped
  correctly in both visible HTML and metadata (no broken JSON-LD or attributes).
- **Cover variants**: a post may use an image cover (path) or a code-style cover (a glyph +
  caption matching the existing design); both render in the correct design slot.
- **Empty blog** (no posts yet): the index builds without error and shows an empty/′no
  posts′ state without breaking the design.
- **Missing or empty `categories.yml`**: the build fails with a clear, actionable message
  (the category set is required to validate posts and render the navigation), rather than
  producing an index with no categories or mis-filing posts.
- **Reading-progress and animations** on a very short or very long post behave correctly and
  respect reduced-motion preferences.
- **Re-publishing an edited post**: rebuilding updates the page and the sitemap `lastmod`
  appropriately, without creating duplicate entries.
- **Unpublishing** (deleting a note or setting `draft: true`): the post is removed from the
  index and sitemap on the next build.

## Requirements *(mandatory)*

### Functional Requirements

**Authoring & content source**

- **FR-001**: The system MUST treat Obsidian markdown notes with YAML frontmatter in a
  designated content directory as the single source of blog content.
- **FR-002**: Frontmatter MUST support: title, publication date, exactly one category, tags,
  a short description/excerpt, a cover (image path OR code-style cover glyph + caption), an
  optional slug, an optional `updated` date (drives `dateModified`/`lastmod`), optional SEO
  fields (canonical, social/OG description), an optional read time, and an optional draft flag.
- **FR-003**: The post body MUST be authored as normal markdown; the author MUST NOT have to
  edit any generated HTML.
- **FR-004**: The system MUST never require hand-editing of generated output; generated HTML
  is a build artifact only.

**Categories**

- **FR-005**: The canonical category list (membership, order, display labels) MUST be
  author-declarable from a single documented place in the vault; it MUST NOT be hardcoded
  where the author cannot change it.
- **FR-006**: Each post MUST belong to exactly one category, assigned via frontmatter; a
  category outside the declared set MUST cause a clear build error/warning.
- **FR-007**: The index MUST provide an "All" view plus a navigation entry per declared
  category, in the declared order.

**Blog index**

- **FR-008**: The index MUST render, in static HTML, a featured post plus a grid of post
  cards; each card MUST show cover, category, title, excerpt, date, and read time and link
  to the full post via a real anchor present in the static HTML.
- **FR-009**: Category filtering MUST be available as progressive enhancement over the
  already-present, crawlable links (filtering MUST NOT be the only way links exist).
- **FR-010**: The index MUST exclude draft posts.

**Post page**

- **FR-011**: Each post MUST render into the existing post-page design including: a
  back-to-all-notes link, a category chip, date, read time, the title (single `<h1>`), the
  excerpt, the cover, the author block (name, role, location), a reading-progress indicator,
  the rendered post body, and a "More notes" section.
- **FR-012**: Read time MUST be computed from the content when not provided in frontmatter,
  and taken from frontmatter when provided.
- **FR-013**: The rendered body MUST support the design's content block types (paragraphs,
  section headings, code blocks with a caption, blockquotes, lists, and image/figure
  blocks) styled exactly as in the existing design. Code blocks MUST render as preformatted
  monospace in the existing code-card style with NO token-level syntax-highlighting library
  and no client-side JavaScript for code.

**Related posts**

- **FR-014**: The system MUST resolve author-placed end-of-post links (Obsidian wikilinks or
  markdown links) to referenced posts and render them as "More notes" cards in the existing
  card design, preserving the author's order.
- **FR-015**: When no related links are present, the "More notes" section MUST degrade
  gracefully (omitted or safe fallback) without broken markup.
- **FR-016**: A related link that does not resolve MUST be reported as a warning, not
  rendered as a broken card.

**SEO / GEO**

- **FR-017**: Every generated post page MUST include a correct `<title>`, meta description,
  canonical URL, Open Graph tags, and Twitter card tags fed from frontmatter.
- **FR-018**: Every generated post page MUST include Article/BlogPosting JSON-LD with
  headline, author, datePublished, dateModified, image, description, articleSection (from
  category), and keywords (from tags). When a post has only a code-style cover (no image),
  the social/Open Graph/JSON-LD `image` MUST fall back to the site default (`og-image.png`),
  so every page still carries a valid image reference.
- **FR-019**: Every published post MUST be added to `sitemap.xml` with an appropriate
  `lastmod`; drafts MUST NOT appear.
- **FR-020**: The system MUST reuse the existing `robots.txt`, `site.webmanifest`, and
  favicon set, and MUST use one consistent absolute site URL everywhere; author identity
  MUST be consistent with the rest of the site.
- **FR-021**: All post content and metadata MUST be present in the initial served HTML
  (no client-only rendering of any content, link, or metadata a crawler needs).

**Build & deploy**

- **FR-022**: A build step MUST read the markdown notes and render the index and post pages
  into the existing design templates and write static HTML plus an updated sitemap.
- **FR-023**: The build MUST run automatically in continuous integration on push to the main
  branch and deploy the static output to GitHub Pages.
- **FR-024**: A `.nojekyll` file MUST be present so files are served verbatim.
- **FR-025**: The build MUST NOT modify or regenerate the existing portfolio (`index.html`)
  or its prior SEO work, and MUST NOT overwrite unrelated files. The sole exception is the
  managed "Field notes" region of the deployed homepage (between the `<!--LATEST-NOTES:START-->`
  / `<!--LATEST-NOTES:END-->` markers), which the build deterministically regenerates from the
  latest posts; everything outside that region stays byte-for-byte unchanged and the repo source
  `index.html` is never written to.
- **FR-026**: The build MUST fail with clear, actionable messages on invalid input (missing
  required frontmatter, unknown category, slug collisions) rather than producing broken
  output; it MUST NOT disable a feature to silence an error.

**Accessibility & performance**

- **FR-027**: Each generated page MUST have exactly one `<h1>`, semantic landmarks, and
  meaningful alt text (decorative mascots marked `aria-hidden`); links/controls MUST be
  keyboard-operable.
- **FR-028**: Animations MUST be compositor-only and respect reduced-motion; pages MUST
  avoid cumulative layout shift.

### Key Entities *(include if feature involves data)*

- **Post**: One Obsidian note. Attributes: title, date (= datePublished), optional `updated`
  (= dateModified; falls back to date), category (one), tags (many), excerpt, cover (image
  path copied to `/blog/assets/media/` with width/height + alt, OR code-style glyph +
  caption), slug (= `frontmatter.slug || kebab-case(title)`, the stable permalink; duplicates
  are a build error), SEO overrides (canonical, social description), read time (provided or
  computed), draft flag, markdown body, and end-of-post related links. Produces one static
  post page at `/blog/<slug>/`.
- **Category**: A named grouping with a display label and an order position, declared by the
  author. Relationship: a Post belongs to exactly one Category; the index navigation and
  per-post chip derive from the Category set.
- **Related link**: An author-placed reference at the end of a post that resolves to another
  Post and becomes a "More notes" card. Many per post; each resolves to zero or one Post.
- **Blog index**: The generated listing page aggregating all non-draft Posts as a featured
  Post plus a grid, with category navigation.
- **Site metadata**: The shared, consistent identity and URL configuration (absolute site
  URL, author name/role/location, shared robots/manifest/favicons) applied to every page.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An author can publish a new post by editing/committing exactly one markdown
  note (plus, optionally, related links at its end) — no other file edits required — and the
  post appears on the index and as its own page after the automated build.
- **SC-002**: 100% of a published post's body text and its title, category, date, read time,
  and excerpt are present in the page's served HTML before any script runs (verifiable by
  inspecting raw HTML / disabling JavaScript).
- **SC-003**: 100% of generated post pages contain a valid title, meta description, canonical
  URL, Open Graph tags, Twitter card tags, and valid Article/BlogPosting structured data,
  and 100% of published posts appear in `sitemap.xml`.
- **SC-004**: The generated blog index and post pages are visually consistent with the
  existing design (same layout, colors, typography, mascots, and interactions); a reviewer
  comparing them to the design source finds no restyling.
- **SC-005**: The existing portfolio page (`index.html`) and its SEO companion files are
  byte-for-byte unchanged by the blog build, except for the managed "Field notes" region of
  `index.html` (between the `<!--LATEST-NOTES:*-->` markers), which is deterministically
  regenerated; the repo source files are never modified.
- **SC-006**: Adding a post that links N existing posts at its end produces a "More notes"
  section with exactly those N resolvable posts as cards; adding none produces a page with no
  broken "More notes" markup.
- **SC-007**: Changing the author-declared category set (add/reorder/relabel) updates the
  index navigation and post chips on the next build with no code change.
- **SC-008**: The build completes successfully in CI on push and the site is deployed to
  GitHub Pages with `.nojekyll` present; invalid content fails the build with a clear message
  instead of deploying broken pages.
- **SC-009**: One consistent absolute site URL is used across every canonical, Open Graph,
  sitemap, and JSON-LD reference (no mixed or relative-only canonical URLs).

## Assumptions

- The canonical site URL is `https://ehsankolivand.github.io/` (a GitHub user/org page
  served at the domain root), consistent with the existing portfolio and SEO files.
- The blog lives under `/blog/` (index at `/blog/`, posts at `/blog/<slug>/`) so it never
  collides with the existing portfolio at `/`.
- The existing design source (`Ehsan Koolivand - Blog.html`) is a client-rendered bundle;
  the real templates (markup, inline styles, CSS, fonts, interactions) are extracted from it
  and reused verbatim — the look is not redesigned.
- Author identity is standardized as "Ehsan Kolivand", Senior Android Engineer, Istanbul, to
  stay consistent with the deployed site and SEO files (the design bundle's placeholder
  "Koolivand" is corrected for site-wide consistency; this is content/data, not a restyle).
- The initial category set is Compose, Architecture, Tooling, and Crypto (with an "All"
  view), but the set is author-driven and changeable from the vault.
- The build runs with free tooling available in GitHub Actions; no backend, database, or
  paid service is introduced.
- Markdown follows common conventions (CommonMark-style) plus YAML frontmatter and Obsidian
  wikilinks; the design's content-block vocabulary (paragraph, heading, code+caption, quote,
  list, image+caption) is the supported rendering set.
- At least one real example post is authored as an Obsidian note to prove the end-to-end
  flow.

## Dependencies

- Reuses the existing root companion files: `robots.txt`, `sitemap.xml`,
  `site.webmanifest`, and the favicon set.
- Depends on the existing design source bundle as the design source of truth.
- Depends on GitHub Pages and GitHub Actions for hosting and CI deployment.
