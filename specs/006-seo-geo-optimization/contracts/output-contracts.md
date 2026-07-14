# Output Contracts: SEO / GEO-AEO Optimization Refinement

Verifiable assertions against the built `_site/` (and committed source where noted). Each maps to an
FR and is checkable with grep/inspection or the existing verifier. "PASS" = the whole suite
(`unittest` + `build` + `verify_build`) is green with ≥ 594 checks, 0 failures.

## C1 — Blog post byline anchor (FR-001)
For every `_site/blog/<slug>/index.html`:
- Contains an author-row anchor `<a href="/"` wrapping the visible name "Ehsan Kolivand".
- The anchor uses `color:inherit` and `text-decoration:none` (or equivalent) so appearance is
  unchanged.
- Existing checks still hold: exactly one `<h1>`, body content present, no unresolved tokens.

## C2 — Per-post `WebSite` JSON-LD node (FR-002)
For every `_site/blog/<slug>/index.html`:
- The FIRST `<script type="application/ld+json">` still parses to an object with
  `@type == "BlogPosting"` (verifier lines 142–147, 218 unaffected).
- Some `<script type="application/ld+json">` on the page parses to a `WebSite` object with
  `@id == "https://ehsankolivand.github.io/#website"` and `publisher.@id ==
  "https://ehsankolivand.github.io/#person"`.
- `_all_jsonld()` returns non-None (all blocks valid JSON); `BlogPosting` and `BreadcrumbList`
  assertions still pass.

## C3 — Portfolio head completeness (FR-003, FR-004, FR-005)
For `_site/index.html`:
- Contains `<link rel="alternate" type="application/atom+xml"` with `href="/blog/feed.xml"`.
- Contains `<meta name="robots" content="index, follow, max-image-preview:large">`.
- The ProfilePage JSON-LD node contains `"dateCreated"` and `"dateModified"` string dates.
- Person/WebSite/ProfilePage `@id`s, `sameAs`, `knowsAbout`, `jobTitle` unchanged;
  `#person"` and `#website"` still present (feature-005 verifier check).

## C4 — No dead resource hints (FR-006)
For `_site/index.html`:
- Zero occurrences of `fonts.googleapis.com` and `fonts.gstatic.com`.
- Rendering visually identical (manual/inspection); no `@font-face` change; PORTFOLIO-FONTS zone
  unchanged.

## C5 — robots.txt crawler completeness (FR-007)
For `_site/robots.txt` (and committed `robots.txt`):
- Contains an `Applebot` user-agent stanza with `Allow: /`.
- Still contains `Googlebot`, `OAI-SearchBot`, `ChatGPT-User`, `PerplexityBot`, `Perplexity-User`,
  `Claude-SearchBot`, `Claude-User`, `ClaudeBot`, `GPTBot`, `Google-Extended`.
- Still contains `Sitemap: https://ehsankolivand.github.io/sitemap.xml` (verifier asserts the
  sitemap URL is referenced).

## C6 — Determinism & identity integrity (FR-008, FR-009, FR-010)
- Two consecutive `python scripts/build_blog.py --out _site` runs produce byte-identical `_site/`
  (no `today()`; portfolio dates are fixed constants).
- `config.py` identity constants still equal the portfolio Person/WebSite JSON-LD (verifier identity
  checks pass — unchanged this cycle).
- Portfolio: both marker zones present & paired once; exactly one `<h1>`; robot hooks present;
  byte-identical to source outside the sanctioned additive head edits and the managed notes region.

## C7 — Gate integrity (FR-011)
- `scripts/verify_build.py` and `.specify/memory/constitution.md` are unmodified (no gate weakened,
  no principle amended).
- `python -m unittest discover -s tests` passes; `python scripts/verify_build.py --out _site` reports
  ≥ 594 checks, 0 failures.
