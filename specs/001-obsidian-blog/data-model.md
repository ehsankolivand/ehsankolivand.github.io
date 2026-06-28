# Phase 1 Data Model: Obsidian-Vault-Driven Blog

The data model is filesystem-based: Markdown notes + one categories file are the inputs; the
generator builds in-memory entities and emits static HTML. No database.

## Entity: Post

One Obsidian note in `content/blog/*.md` = one Post = one page at `/blog/<slug>/`.

| Field | Source | Type | Required | Default / Derivation | Validation |
|-------|--------|------|----------|----------------------|------------|
| `title` | frontmatter | string | **yes** | — | non-empty; becomes the page `<h1>` |
| `date` | frontmatter | date `YYYY-MM-DD` | **yes** | — | parseable date; = `datePublished` |
| `updated` | frontmatter | date `YYYY-MM-DD` | no | = `date` | parseable; >= `date`; = `dateModified` |
| `category` | frontmatter | string | **yes** | — | MUST be a `name` in `categories.yml` |
| `tags` | frontmatter | string[] | no | `[]` | becomes JSON-LD `keywords` + meta keywords |
| `excerpt` / `description` | frontmatter | string | **yes** | — | non-empty; used as dek + meta description + OG/Twitter description |
| `cover` | frontmatter | object | no | code cover from title initial | see Cover sub-model |
| `slug` | frontmatter | string | no | `kebab-case(title)` | URL-safe; unique across posts (collision = error) |
| `readTime` | frontmatter | string | no | computed `"N min"` (R6) | free text when provided |
| `canonical` | frontmatter | URL | no | `https://ehsankolivand.github.io/blog/<slug>/` | absolute URL |
| `socialDescription` / `ogDescription` | frontmatter | string | no | = `excerpt` | used for OG/Twitter when differing from meta |
| `draft` | frontmatter | bool | no | `false` | `true` excludes from index, pages, sitemap |
| `image` | frontmatter (or `cover.src`) | path | no | none → OG falls back to `og-image.png` | resolvable file under content assets |
| `body` | markdown after frontmatter | markdown | **yes** | — | rendered to design body blocks (R3) |
| `relatedLinks` | end-of-body links | string[] | no | `[]` | resolved to Posts (R7); unresolved → warning |

### Sub-model: Cover

```yaml
cover:
  type: code            # "code" (default) | "image"
  glyph: "{ }"          # code cover: short glyph shown large (type: code)
  caption: "// cover: spec -> generators"   # code cover caption (type: code)
  src: assets/x.png     # image cover path (type: image), copied to /blog/assets/media/
  alt: "Module graph"   # image cover alt text (type: image; required when type: image)
  width: 1200           # image intrinsic width  (type: image; for no-CLS)
  height: 630           # image intrinsic height (type: image; for no-CLS)
```

- Shorthand: a bare string `cover: "{ }"` is treated as a code cover glyph; `cover: assets/x.png`
  (a path) is treated as an image cover.

### Derived (computed) fields

- `tagStyle` — mint palette for `Tooling`/`Compose`, sand palette otherwise (mirrors the design's
  `_tagStyle`), used for the category chip colors.
- `url` — `"/blog/<slug>/"` (root-absolute) and `absoluteUrl` — base + url.
- `displayDate` — `date` formatted like the design (`"Jun 18, 2026"`).
- `featured` — the most recent non-draft post (index view) per design (first post is featured).

### Lifecycle / state

- **Draft** (`draft: true`): excluded everywhere. **Published** (`draft` absent/false): listed
  on index, has a page, in sitemap. **Removed** (note deleted or set to draft): drops from index
  and sitemap on next build. Re-publishing an edited note updates the page and `lastmod`.

## Entity: Category

Declared in `content/blog/categories.yml` (ordered).

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | the value posts use in `category:`; unique; stable key |
| `label` | string | no (default `name`) | display text in nav + chips |
| `palette` | `mint` \| `sand` | no | overrides the chip color; default is mint for `Tooling`/`Compose`, sand otherwise; any other value is a build error |

- Order in the file = order in the index navigation (after the always-present "All").
- The set defines the legal `category` values for Posts.

## Entity: Site config (constant)

| Field | Value |
|-------|-------|
| `baseUrl` | `https://ehsankolivand.github.io/` |
| `blogBase` | `/blog/` |
| `authorName` | `Ehsan Kolivand` |
| `authorRole` | `Senior Android Engineer` |
| `authorLocation` | `Istanbul` |
| `siteName` | `Ehsan.log — Field Notes` |
| `defaultOgImage` | `/og-image.png` |
| `locale` | `en` |

## Entity: Blog index (generated)

Aggregates published Posts: one featured Post (most recent) + a grid of the rest, plus the
category navigation derived from Category set. Output: `_site/blog/index.html`.

## Relationships

- Post **belongs to exactly one** Category (`Post.category` → `Category.name`).
- Post **references zero or more** Posts via `relatedLinks` (resolved to Posts → more-notes cards).
- Blog index **aggregates** all published Posts and **renders** the Category set.
- Site config **applies to** every generated page.

## Validation summary (build MUST enforce — fail loud)

1. Required frontmatter present (`title`, `date`, `category`, `excerpt`/`description`, body).
2. `category` ∈ categories.yml names.
3. `slug` unique across all posts.
4. `date`/`updated` parse; `updated >= date`.
5. Image cover `src` resolves; `alt` present when `type: image`.
6. Related links resolve (else warning, not failure).
7. No unresolved template tokens in output; exactly one `<h1>` per page.
