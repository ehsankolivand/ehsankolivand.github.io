# Contract: Atom 1.0 Feed (`/blog/feed.xml`)

Built by `scripts/blog/feed.py::build_feed(posts, base_url, portfolio_lastmod) -> str`. Written to
`_site/blog/feed.xml` by `build_blog.py`. Stdlib-only; every value HTML/XML-escaped; fully
deterministic (no `today()`).

## Document shape

```xml
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Ehsan.kolivand — Field Notes</title>
  <subtitle>…BLOG_TAGLINE…</subtitle>
  <id>https://ehsankolivand.github.io/blog/</id>
  <link rel="alternate" type="text/html" href="https://ehsankolivand.github.io/blog/"/>
  <link rel="self" type="application/atom+xml" href="https://ehsankolivand.github.io/blog/feed.xml"/>
  <updated>2026-06-28T00:00:00Z</updated>           <!-- max(post.updated); portfolio date if empty -->
  <author><name>Ehsan Kolivand</name><uri>https://ehsankolivand.github.io/</uri></author>
  <entry>
    <title>…post.title…</title>
    <id>https://ehsankolivand.github.io/blog/&lt;slug&gt;/</id>     <!-- = canonical -->
    <link rel="alternate" type="text/html" href="…canonical…"/>
    <published>2026-06-28T00:00:00Z</published>      <!-- post.date -->
    <updated>2026-06-28T00:00:00Z</updated>          <!-- post.updated -->
    <summary>…post.excerpt…</summary>
    <category term="…tag…"/>                          <!-- one per tag, optional -->
    <author><name>Ehsan Kolivand</name></author>
  </entry>
  …one entry per published post, newest-first…
</feed>
```

## Rules

- **Required Atom elements present**: feed-level `id`, `title`, `updated`; per-entry `id`, `title`,
  `updated`. (RFC 4287.)
- **Determinism**: all timestamps are `<post-date>T00:00:00Z` (UTC midnight). Feed `<updated>` =
  `max(p.updated for p in posts)` rendered the same way; when there are no posts, use
  `portfolio_lastmod`. Never call `today()`.
- **IDs are canonical post URLs** (stable, unique). Feed `<id>` = the blog index absolute URL.
- **Ordering** matches the site (newest-first; the input `posts` is already sorted).
- **Escaping**: titles/summaries/categories XML-escaped (`& < > "`). Reuse the same escaping as the
  HTML path (`html.escape`).
- **Empty blog**: a valid feed with zero `<entry>` elements and `<updated>` = portfolio date.
- **Drafts**: excluded (the build passes only published posts).

## Autodiscovery

`seo.py` adds to every blog page head:
`<link rel="alternate" type="application/atom+xml" title="Ehsan.kolivand — Field Notes" href="/blog/feed.xml">`.

## Verifier hooks (see verifier.md)

Feed exists; parses via `xml.etree.ElementTree`; has feed `id/title/updated`; entry count ==
published-post count; every post canonical appears as an entry `id`.
