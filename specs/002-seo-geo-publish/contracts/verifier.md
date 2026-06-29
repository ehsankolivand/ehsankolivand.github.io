# Contract: Verifier Expansion (Definition of Done)

New assertions added to `scripts/verify_build.py`. Each is one `ok(cond, msg)` check (the existing
counter). Baseline = 90 checks; target ≥ 110. The build MUST fail (exit ≠ 0) on any violation.

## Per-post (loop over published posts)

1. **Canonical exact**: `rel="canonical" href="<base>/blog/<slug>/"` appears verbatim.
2. **og:image complete**: `og:image:width`, `og:image:height`, `og:image:alt` all present.
3. **twitter:image:alt** present.
4. **Machine date**: `<time datetime="<date ISO>"` present and the ISO equals `post.date`.
5. **BlogPosting enriched**: parsed JSON-LD `BlogPosting` has `wordCount` (int > 0), `url` ==
   canonical, `author.@id` == `PERSON_ID`, `inLanguage`. (`timeRequired` present unless read-time
   unparseable.)
6. **BreadcrumbList**: a JSON-LD object of `@type` `BreadcrumbList` exists with 3 `itemListElement`
   entries ending at the post canonical.
7. **Feed autodiscovery**: `type="application/atom+xml"` link present in head.

## Index page

8. **Graph identity**: parsed index JSON-LD `@graph` contains a `WebSite` with `@id` == `WEBSITE_ID`
   and a `Blog` whose `author.@id` == `PERSON_ID`.
9. **BreadcrumbList** (2 items) present in the index graph.
10. **No SearchAction**: assert the index JSON-LD does **not** contain `"SearchAction"` (guards the
    deliberate exclusion).

## Sitemap correctness

11. Each post's sitemap `<url>` block has `<lastmod>` == `post.updated.isoformat()`.
12. Home `<lastmod>` == `max(PORTFOLIO_LASTMOD, newest updated)`; `/blog/` lastmod == newest updated
    (when posts exist).

## Feed (`_site/blog/feed.xml`)

13. Exists and parses with `xml.etree.ElementTree`.
14. Feed-level `id`, `title`, `updated` present; `updated` == `max(updated)` (or portfolio date).
15. Entry count == number of published posts; every post canonical appears as an entry `<id>`.

## llms.txt (`_site/llms.txt`)

16. Exists; contains the author H1 name (`# Ehsan Kolivand`) from the base.
17. Contains `## Writing` (when posts exist) and every published post's absolute URL.

## No dangling internal links (the central invariant)

18. **Committed source**: scan the **repo** `index.html` for `href="/blog/<slug>/"` occurrences;
    every referenced slug MUST be a current published post (the 3 stale seed slugs MUST be absent).
    Equivalently: the committed managed region MUST contain **zero** `/blog/<slug>/` links (it is
    neutralized) — assert the stale slugs `spec-driven-android`, `custom-layouts-compose`,
    `mvi-that-scales` do not appear anywhere in repo `index.html`, and that any `/blog/<slug>/`
    link present resolves to a real post.
19. **Built pages**: scan every built blog page + `_site/index.html` for `href="/blog/<slug>/"`;
    every slug MUST resolve to a built post page (no 404-bound internal links).

## Completeness guards (analyze C1/C2)

20. **robots → sitemap**: `_site/robots.txt` contains the absolute sitemap URL
    (`<base>/sitemap.xml`).
21. **Unique titles**: the set of built-page `<title>` strings has no duplicates (each post +
    index title is distinct).

## Preserved (regression guards — already present, keep)

- Exactly one `<h1>` per page; no unresolved template tokens; portfolio byte-identical outside the
  managed region; required root companions present; fonts/css/js present; index lists every post +
  category; per-post body content present pre-JS.

## Notes

- All checks are deterministic and offline (no network). JSON-LD parsed with `json.loads`; feed
  with `xml.etree.ElementTree`; sitemap by string/regex as today.
- Verifier loads posts the same way the build does (`content.load_posts(..., include_drafts=False)`),
  so the "expected" set always matches the published set.
