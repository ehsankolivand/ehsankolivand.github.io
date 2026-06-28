# Contract: Template ↔ Data Mapping

The templates are extracted verbatim from the design bundle (`<x-dc>` markup + inline styles).
The bundle's runtime placeholders are replaced by the generator. This contract pins how each
placeholder maps to Post/Category/Site data so design fidelity is preserved.

## base.html (head + shell)

Provides the document, `<head>` SEO slots, the body shell (ambient background, custom cursor,
scroll-reactor, `header` with `Ehsan.kolivand` wordmark + category `nav`), a `{{MAIN}}` slot, and a
deferred `<script src="/blog/assets/blog.js">`. Head slots filled per page:

| Slot | Source |
|------|--------|
| `<title>` | post: `"<title> — Ehsan.kolivand"`; index: `"Ehsan.kolivand — Field Notes"` |
| `<meta name="description">` | post: `excerpt`; index: blog tagline |
| `<link rel="canonical">` | `canonical` or derived absolute URL |
| `og:*` / `twitter:*` | title, description, url, image (cover image or site og-image), `og:type=article` for posts |
| JSON-LD | post: `BlogPosting` (see below); index: `Blog`/`CollectionPage` + `WebSite` |
| favicons / manifest / theme-color | reused from existing root files (`#34E6A0`) |
| category nav `<nav data-topcats>` | "All" + one `<a data-cat="<name>">` per `categories.yml` entry, in order |

## index.html (`<main>`)

| Placeholder (bundle) | Static replacement |
|----------------------|--------------------|
| hero copy | kept verbatim from design (static) |
| `<sc-if showFeatured>` featured card | the featured (most recent) post; `onclick` → real `<a href="/blog/<slug>/">`; fills tag, date, read time, title, dek, cover |
| `<sc-for gridPosts>` cards | one card per remaining published post; each an `<a href>` with `data-cat="<category>"`; fills tag, title, dek, date, read time, cover |
| `{{ catAll }}` etc. | nav anchors with `data-cat`; filtering handled by `blog.js` |
| footer | kept verbatim (identity "Ehsan Kolivand") |

## article.html (`<main>`)

| Placeholder | Static replacement |
|-------------|--------------------|
| back button `{{ goBack }}` | `<a href="/blog/">← All notes</a>` |
| `{{ current.tag }}` / date / read time | post category label / `displayDate` / read time |
| `<h1>{{ current.title }}</h1>` | the post title — the page's single `<h1>` |
| `{{ current.dek }}` | `excerpt` |
| author block | `Ehsan Kolivand` / `Senior Android Engineer · Istanbul` (static) |
| cover (`coverGlyph`/`coverCap`) | code cover (glyph+caption) OR `<img>` for image cover |
| `<sc-for current.blocks>` | rendered Markdown body blocks (p/h2/code/quote/list/img) per research R3 |
| end signature | kept verbatim |
| `<sc-for moreNotes>` cards | resolved related posts as more-notes cards (real `<a href>`); omitted if none |

## JSON-LD (post page)

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "<title>",
  "description": "<excerpt>",
  "image": "<absolute cover/og image>",
  "datePublished": "<date ISO>",
  "dateModified": "<updated|date ISO>",
  "author":    { "@type": "Person", "name": "Ehsan Kolivand", "jobTitle": "Senior Android Engineer" },
  "publisher": { "@type": "Person", "name": "Ehsan Kolivand" },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "<absolute post url>" },
  "articleSection": "<category label>",
  "keywords": "<tags joined>",
  "inLanguage": "en"
}
```

## Invariants

- No `{{ }}`, `<sc-if>`, or `<sc-for>` tokens survive into output (verifier-enforced).
- All inline styles and CSS classes from the design are preserved unchanged.
- Every navigational/post link is a real `<a href>` present in static HTML.
- Exactly one `<h1>` per page (post title on post pages; the hero `Field Notes.` heading on the
  index — the index hero `<h1>` is retained from the design and the post grid uses `<h3>` cards).
