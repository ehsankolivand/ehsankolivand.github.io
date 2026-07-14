# Data Model: SEO / GEO-AEO Optimization Refinement

This feature adds no persistent storage and no new content entities. The "data" is the structured
metadata each page exposes to crawlers/AI engines. Below are the entities this cycle touches and the
invariants that must hold.

## Entity: Canonical Identity (unchanged this cycle)

The single professional identity shared verbatim by the portfolio and the blog generator.

| Field | Value / source | Invariant |
|---|---|---|
| Person `@id` | `https://ehsankolivand.github.io/#person` (`config.PERSON_ID` == portfolio) | Equal in both places; unchanged this cycle |
| WebSite `@id` | `https://ehsankolivand.github.io/#website` (`config.WEBSITE_ID` == portfolio) | Equal in both places; unchanged this cycle |
| `name` | "Ehsan Kolivand" (`config.AUTHOR_NAME`) | Consistent across surfaces |
| `jobTitle` | "Senior Android Engineer" (`config.AUTHOR_ROLE`) | Verifier asserts blog == portfolio |
| `knowsAbout` | 13-item list (`config.AUTHOR_KNOWS_ABOUT`) | Verifier asserts blog == portfolio, verbatim & ordered |
| `sameAs` | GitHub, LinkedIn, Telegram (`config.AUTHOR_SAMEAS`) | Verifier asserts blog == portfolio |

**Rule**: This cycle changes NO identity field. Any future change requires editing `config.py` and
`index.html` together (verifier's identity-equality checks enforce this).

## Entity: Per-Post Structured-Data Graph (modified)

The set of JSON-LD nodes emitted in each post page `<head>`, in order.

| Position | Node | Status | Key fields |
|---|---|---|---|
| 1 (first script) | `BlogPosting` | unchanged | headline, description, url==canonical, image, datePublished, dateModified, author→#person (full), publisher→#person (lean), mainEntityOfPage, isPartOf Blog, articleSection, wordCount, inLanguage, keywords?, timeRequired? |
| 2 | `BreadcrumbList` | unchanged | 3 items: Home → Field Notes → post (ends at post canonical) |
| 3 (NEW) | `WebSite` | **added** | `@id`==WEBSITE_ID, name, url==home, publisher→{@id: PERSON_ID} |

**Invariants**:
- `BlogPosting` MUST remain the first `application/ld+json` script (verifier reads the first script).
- The new `WebSite` node MUST reuse `config.WEBSITE_ID` and reference `config.PERSON_ID` (no new
  identity).
- All three nodes parse as valid JSON-LD (verifier's `_all_jsonld` returns non-None).

## Entity: Visible Author Byline (modified)

The author row rendered on each post page.

| Field | Before | After |
|---|---|---|
| Name element | text node "Ehsan Kolivand" inside a `<div>` | same text wrapped in `<a href="/">` (crawlable anchor to author/entity page) |
| Appearance | Space Grotesk 600, `#EDF2EF` | identical (anchor uses `color:inherit; text-decoration:none`) |
| Role line | "Senior Android Engineer · Istanbul" | unchanged |

**Invariant**: appearance visually unchanged; the anchor is a real server-rendered `<a>` (Principle
I); target is `/` (the canonical `Person.url`).

## Entity: Portfolio `<head>` Metadata (modified — additive)

| Field | Status | Value |
|---|---|---|
| Atom autodiscovery `<link rel="alternate">` | **added** | `type="application/atom+xml"`, `href="/blog/feed.xml"` |
| `<meta name="robots">` | **added** | `content="index, follow, max-image-preview:large"` |
| ProfilePage `dateCreated` | **added** | fixed date constant |
| ProfilePage `dateModified` | **added** | fixed date constant |
| Google-Fonts `preconnect` ×2 | **removed** | (dead hints; nothing loads from Google) |
| Person/WebSite/ProfilePage `@id`s, `sameAs`, `knowsAbout`, `jobTitle` | unchanged | identity intact |
| Marker zones (LATEST-NOTES, PORTFOLIO-FONTS) | unchanged | present, paired exactly once |
| `<h1>` count | unchanged | exactly one |
| Robot hooks (`data-reactor`/`data-chase`/`data-logo`/`data-cursor`/`data-parallax`) | unchanged | present |

## Entity: robots.txt (modified — additive)

| Field | Status |
|---|---|
| `Applebot` `Allow: /` | **added** |
| All existing search/AI-citation tokens | unchanged |
| `Sitemap:` declaration | unchanged (verifier asserts it references the sitemap URL) |

## Entity: Discovery Surfaces (unchanged behavior; must stay consistent)

`sitemap.xml`, Atom `feed.xml`, `llms.txt` regenerate deterministically from Obsidian content +
config. No structural change this cycle; they must remain canonical/trailing-slash consistent and
carry accurate `lastmod`.
