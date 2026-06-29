# Contract: Structured Data (JSON-LD)

All structured data is emitted in the served static HTML head by `scripts/blog/seo.py`. Identity is
unified with the portfolio via stable `@id`. JSON-LD is compact (`separators=(",",":")`,
`ensure_ascii=False`) and MUST parse.

Canonical anchors (from `config.py`): `PERSON_ID = <base>#person`, `WEBSITE_ID = <base>#website`,
`AUTHOR_SAMEAS = [github, linkedin, telegram]`.

## Post page — two scripts

### 1. `BlogPosting`

```jsonc
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "<post.title>",
  "description": "<post.excerpt>",
  "url": "<canonical>",
  "image": "<image_abs>",                  // measured cover, else /og-image.png
  "datePublished": "<date ISO>",
  "dateModified": "<updated ISO>",
  "author":    {"@type":"Person","@id":"<PERSON_ID>","name":"Ehsan Kolivand","url":"<base>/","sameAs":[…AUTHOR_SAMEAS]},
  "publisher": {"@type":"Person","@id":"<PERSON_ID>","name":"Ehsan Kolivand"},
  "mainEntityOfPage": {"@type":"WebPage","@id":"<canonical>"},
  "isPartOf": {"@type":"Blog","@id":"<base>/blog/"},
  "articleSection": "<category label>",
  "keywords": "<tags joined by ', '>",     // omit field if no tags
  "wordCount": <int>,
  "timeRequired": "PT<minutes>M",
  "inLanguage": "en"
}
```

Rules: `author.@id` and `publisher.@id` MUST equal `PERSON_ID`. `url` MUST equal the canonical.
`timeRequired` minutes parsed from `read_time`; if unpar.seable, omit `timeRequired` (never emit
`PT0M`). `wordCount` > 0.

### 2. `BreadcrumbList`

```jsonc
{
  "@context":"https://schema.org","@type":"BreadcrumbList",
  "itemListElement":[
    {"@type":"ListItem","position":1,"name":"Home","item":"<base>/"},
    {"@type":"ListItem","position":2,"name":"Field Notes","item":"<base>/blog/"},
    {"@type":"ListItem","position":3,"name":"<post.title>","item":"<canonical>"}
  ]
}
```

May be emitted as a second `<script type="application/ld+json">`, or folded into a single `@graph`
with the `BlogPosting`. Either is valid; the verifier checks for a `BreadcrumbList` type and 3 items.

## Index page — one `@graph`

```jsonc
{
  "@context":"https://schema.org",
  "@graph":[
    {"@type":"Blog","@id":"<base>/blog/","name":"<SITE_NAME>","url":"<base>/blog/",
     "description":"<tagline>","inLanguage":"en",
     "author":{"@type":"Person","@id":"<PERSON_ID>","name":"Ehsan Kolivand","sameAs":[…]},
     "isPartOf":{"@type":"WebSite","@id":"<WEBSITE_ID>"},
     "blogPost":[ {"@type":"BlogPosting","headline":…,"url":<canonical>,"datePublished":…,
                   "author":{"@id":"<PERSON_ID>"}} … ]},
    {"@type":"WebSite","@id":"<WEBSITE_ID>","url":"<base>/","name":"<SITE_NAME>",
     "publisher":{"@id":"<PERSON_ID>"}},
    {"@type":"BreadcrumbList","itemListElement":[
       {"@type":"ListItem","position":1,"name":"Home","item":"<base>/"},
       {"@type":"ListItem","position":2,"name":"Field Notes","item":"<base>/blog/"}]}
  ]
}
```

Rules: no `SearchAction` (no search endpoint). `WebSite.@id` MUST equal `WEBSITE_ID` so it merges
with the portfolio's `WebSite`. Empty blog → `blogPost: []` (valid).

## Head social metadata (both page types)

- `og:image:width`, `og:image:height` = image intrinsic dims (covers) or `1200`/`630` (default).
- `og:image:alt` = cover alt (image covers) or `"Ehsan Kolivand — Field Notes"` (default image).
- `twitter:image:alt` = same value as `og:image:alt`.
- `<link rel="alternate" type="application/atom+xml" title="…" href="/blog/feed.xml">` (feed
  autodiscovery) on every blog page.

## Non-negotiables

- No fabricated properties (Principle V / FR-018): no `SearchAction`, no Twitter handle.
- Every emitted block MUST be valid JSON and reference `PERSON_ID`/`WEBSITE_ID` where identity
  appears.
