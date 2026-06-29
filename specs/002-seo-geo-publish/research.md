# Research: SEO + GEO + One-Commit Publishing

Phase 0 decisions. Format per decision: **Decision / Rationale / Alternatives considered**. The
Technical Context had no open `NEEDS CLARIFICATION` markers (the spec's Clarifications resolved
them); this file records the design decisions and grounds the structured-data/feed choices in
primary sources.

## Primary sources consulted (2026-06-29)

- **Google Search Central — Article structured data**: *no required properties; recommended* =
  `author` (Person/Organization, with `name` and `url`), `datePublished`/`dateModified` (ISO 8601),
  `headline`, `image`. Author best practice: use `Person`, include `url` **or** `sameAs` linking to
  a page that uniquely identifies the author. → Confirms enriching `BlogPosting` and unifying the
  author entity via `@id` + `sameAs` is correct and sufficient (no over-markup needed).
- **llmstxt.org — llms.txt format**: required H1 site/project name; optional blockquote summary;
  optional free markdown; zero-or-more `H2` "file list" sections whose items are
  `- [name](url): optional notes`. → Confirms appending a `## Writing` H2 list of
  `- [Title](abs-url): summary` items is spec-conformant.
- (Background, stable as of knowledge cutoff) **Atom — RFC 4287**: feed requires `id`, `title`,
  `updated`; each `entry` requires `id`, `title`, `updated`. **Sitemaps protocol**: `lastmod`
  reflects last modification; values are W3C dates. Both inform the deterministic builders below.

## D1. Fix the stale committed homepage region — neutralize, not refresh

**Decision**: Replace the *content between* the portfolio's `<!--LATEST-NOTES:*-->` markers in the
committed `index.html` with a **post-link-free** fallback: the existing "Field notes" section shell
(eyebrow, heading, dek) + a single "Read all notes → `/blog/`" link, plus an HTML comment noting the
build injects live cards. The build continues to regenerate the full region (3 live cards) for the
deployed `_site/index.html`.

**Rationale**: Constitution VII forbids the *build* writing the repo source homepage, so the source
region cannot be auto-refreshed. A link-free committed region can never rot into a `/blog/<slug>/`
404 between builds (the central live defect), stays valid even if served raw (it links only to
`/blog/`, which always exists), and is fully replaced for production anyway. Pairs with a new
verifier assertion (D8) to make the invariant permanent.

**Alternatives considered**: (a) *Refresh the committed region with the 3 current posts* — rejected:
re-introduces drift the next time posts change and would still 404 after any future deletion. (b)
*A pre-commit/CI hook that rewrites the source region* — rejected: violates VII ("repo source
index.html is never written to") and adds a non-deterministic, environment-dependent step. (c)
*Delete the section/markers* — rejected: loses the homepage→blog link path and the design's Writing
section.

## D2. Unify structured-data identity across portfolio and blog

**Decision**: Reference the portfolio's existing canonical nodes by `@id` everywhere the blog names
the author or site: author → `{"@type":"Person","@id":"https://ehsankolivand.github.io/#person",…}`
with `sameAs` (GitHub, LinkedIn, Telegram — mirroring the portfolio `Person.sameAs`); the index
`WebSite`/`Blog` references `…/#website` via `@id`/`isPartOf`. Add the constants to `config.py`.

**Rationale**: Google's author guidance is to link the author to a page/profile that uniquely
identifies them; reusing the portfolio's `#person`/`#website` `@id` lets engines merge the portfolio
and blog into one entity instead of two near-duplicates (a concrete GEO/knowledge-graph win).
`sameAs` adds robustness if a consumer doesn't resolve the cross-document `@id`.

**Alternatives considered**: Inline a fresh `Person` per page with no `@id` (current behavior) —
works but risks entity duplication. Emitting the full `Person` graph on blog pages — rejected as
redundant; `@id` + minimal fields + `sameAs` is the lean, recommended pattern.

## D3. Add BreadcrumbList; keep it structured-data-only (no visible breadcrumb)

**Decision**: Emit a `BreadcrumbList` JSON-LD on each post (`Home` → `Field Notes` (`/blog/`) →
post) and on the index (`Home` → `Field Notes`). Do **not** add a visible breadcrumb widget.

**Rationale**: Breadcrumbs are a well-supported rich result and a clear navigation signal for AI.
The post already has an on-page trail (the "← All notes" back-link + the Home nav item), so the
structured data reflects real navigation. A *visible* breadcrumb would alter the locked design
(Principle III) for marginal gain.

**Alternatives considered**: Visible breadcrumb UI — rejected on design-fidelity grounds. No
breadcrumb — rejected; it's cheap, valid, and citation-useful.

## D4. Syndication feed = Atom 1.0 at `/blog/feed.xml`, deterministic, stdlib-built

**Decision**: New `scripts/blog/feed.py` builds an Atom 1.0 feed by hand (escaped string building,
no dependency). Feed `id` = blog index URL; feed `title`/`subtitle` from config; feed `updated` =
`max(post.updated)` as an RFC 3339 timestamp at `T00:00:00Z` (deterministic, no `today()`); `author`
= canonical name. Each entry: `id` = post canonical URL, `title`, `link rel=alternate`, `published`
(date `T00:00:00Z`), `updated` (updated date `T00:00:00Z`), `summary` (excerpt), `category` (tags),
`author`. Output `_site/blog/feed.xml`. Empty-blog → a valid feed with no entries and `updated` =
the portfolio date.

**Rationale**: Atom mandates absolute dates and stable IDs, is XML-validatable, and is widely
consumed — the most rigorous, deterministic choice. Building by hand keeps the stdlib-only, no-feed-
library posture and full control over escaping/determinism.

**Alternatives considered**: RSS 2.0 (looser `pubDate` semantics, `lastBuildDate` tempts `today()`)
— rejected. JSON Feed (less consumed by SEO/feed tooling) — rejected. A feed library — rejected
(unnecessary dependency; the project renders Markdown and XML by hand already).

## D5. `llms.txt` becomes build-generated (base + appended post list)

**Decision**: New `scripts/blog/llms.py` reads the committed root `llms.txt` (the human-authored
identity/profile base) and appends a deterministic `## Writing` H2 section listing every published
post as `- [Title](absolute-url): one-line summary`, then writes the merged file to `_site/llms.txt`.
Remove `llms.txt` from the verbatim copy step (it is now generated). The committed `llms.txt` keeps
no post list (no drift) — but to be safe the builder strips any pre-existing build-managed block
before appending (idempotent).

**Rationale**: Makes `llms.txt` a derived artifact so a single-note commit updates it automatically
(Principle VIII), while the author still owns the identity prose. Conformant with the llms.txt
format (H2 file list of markdown links with notes).

**Alternatives considered**: Keep `llms.txt` static & hand-maintained — rejected: violates single-
commit publishing (a second manual edit per post). Fully generate it from config — rejected: loses
author-owned profile copy and duplicates portfolio identity text.

## D6. Complete social-image metadata; machine-readable date

**Decision**: Add `og:image:width`, `og:image:height`, `og:image:alt`, and `twitter:image:alt` to
post and index heads. For image covers use measured intrinsic dimensions + the cover `alt`; for
code-cover posts (no image) fall back to `/og-image.png` at its known `1200×630` with a site-identity
alt ("Ehsan Kolivand — Field Notes"). Wrap the on-page post date in `<time datetime="YYYY-MM-DD">`.

**Rationale**: Image dimensions + alt complete the social card (the portfolio already sets these),
and `<time>` gives engines an unambiguous machine date with zero visual change.

**Alternatives considered**: Skipping image dims — rejected (incomplete card, minor CLS risk on
share previews). Converting all dates site-wide to `<time>` — deferred to just the post publish date
to keep the template diff minimal and design-faithful.

## D7. Enrich `BlogPosting` with citation-useful fields

**Decision**: Add to each post's `BlogPosting`: `url` (= canonical), `wordCount` (from body),
`timeRequired` (ISO 8601 duration from read-time minutes, e.g. `PT5M`), `isPartOf`
(`{"@type":"Blog","@id": <blog index URL>}`), keep `inLanguage`, `articleSection`, `keywords`,
`mainEntityOfPage`, `image`, dates. `publisher` stays the canonical `Person` (`@id` `#person`).

**Rationale**: `wordCount`/`timeRequired` are concrete, citation-friendly facts; `isPartOf` ties the
post to the Blog entity. All derive from existing fields — no new authoring burden.

**Alternatives considered**: `articleBody` (full text in JSON-LD) — rejected as redundant (the full
body is already in the HTML; duplicating bloats every page).

## D8. Verifier expansion = the enforcement layer

**Decision**: Extend `scripts/verify_build.py` with assertions (detailed in
`contracts/verifier.md`): per-post breadcrumb + unified `@id`/`sameAs`; `og:image:width/height/alt` +
`twitter:image:alt`; `<time datetime>` present and equal to the post date; canonical == base+`/blog/
<slug>/`; sitemap `lastmod` == post `updated` and home lastmod == `max(portfolio, newest)`; feed
exists, parses as XML, has feed-level `id/title/updated` and one entry per post with required
fields; `_site/llms.txt` exists and lists every post URL; and **no committed source file (repo
`index.html`) nor any built page contains a `/blog/<slug>/` link to a non-existent post**.

**Rationale**: The constitution makes the verifier the Definition of Done; encoding the new
invariants there is what keeps them true under future change ("fail loud").

**Alternatives considered**: External validators (e.g., hitting Google's Rich Results API in CI) —
rejected: adds a network dependency and nondeterminism; structural assertions in-repo are
deterministic and offline.

## Out of scope (recorded decisions, not gaps)

- **Isolated unit tests** for the renderer/feed/llms modules — valuable but separate from this
  feature's DoD (the post-build verifier remains the gate). Candidate for a follow-up.
- **`SearchAction`** and **Twitter handle attribution** — intentionally excluded (no search
  endpoint; no public handle). See plan.md "deliberate scope exclusions".
- **Critical-CSS inlining / further render-blocking removal** — current single self-hosted stylesheet
  + 2 preloaded fonts already meet CWV goals; inlining risks design fidelity for marginal gain.
- **Committing the untracked design bundle** (`Ehsan Koolivand - Blog.html`) — orthogonal repo-
  hygiene item (noted in PROJECT_CONTEXT improvements), not part of SEO/GEO; left to the owner.
