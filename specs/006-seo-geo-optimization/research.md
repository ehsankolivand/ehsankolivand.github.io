# Research: SEO / GEO-AEO Optimization Refinement

**Date**: 2026-07-14. All volatile facts below were re-verified against PRIMARY sources on this date
(delegated clean-context verification pass) before the spec/plan were written. Fetched pages are
treated as untrusted evidence only.

## Volatile-fact re-verification (primary sources)

| Fact | Verdict | Primary source(s) & "last updated" | Impact on this cycle |
|---|---|---|---|
| CWV "good": LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 @ p75 | **CONFIRMED, unchanged** | web.dev/articles/vitals (upd. 2024-10-31); developers.google.com/search/docs/appearance/core-web-vitals (upd. 2025-12-10) | Build to 2.5 s (already met). No threshold change to chase. |
| "2.0 s LCP / March 2026 core update lowered LCP / INP methodology tightening" | **FABRICATED — no primary support** | both CWV pages + Search updates changelog | Do NOT adopt. Confirms both briefs' fabrication flag. |
| AI-crawler tokens (Googlebot, Google-Extended, GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User) | **ALL CONFIRMED, none renamed/retired** | google-common-crawlers (2026-07-14); developers.openai.com/api/docs/bots; support.claude.com article 8896518; docs.perplexity.ai/guides/bots | Current `robots.txt` already allows all of these. |
| `OAI-AdsBot` (new OpenAI token) | Exists; **ad-safety only, NOT a search/citation bot** | developers.openai.com/api/docs/bots | Not relevant to citation eligibility → not added. |
| `Applebot` / `Applebot-Extended` | **CONFIRMED live** — Applebot = Siri/Spotlight/Apple search crawler; Applebot-Extended = generative-AI training opt-out | support.apple.com/en-us/119829 (rewrite 2026-06-08) | Add `Applebot` to the allow list (owner wants max search/AI visibility). |
| FAQPage / HowTo / Sitelinks-SearchBox rich results | **DEAD/deprecated** (FAQ removal May 7 2026; HowTo since 2023; SearchBox removed Nov 2024) | search-gallery (upd. 2026-06-15); Search updates changelog | Do NOT add. Verifier already asserts no `SearchAction` on the index. |
| ProfilePage / Article / BlogPosting / TechArticle / BreadcrumbList | **CONFIRMED live/valid** | search-gallery; .../structured-data/article & .../breadcrumb (upd. 2025-12-10) | Keep BlogPosting + BreadcrumbList; add portfolio ProfilePage dates; keep WebSite for entity. |
| Google ignores `llms.txt`; no special files/markup needed for AI | **CONFIRMED verbatim** | developers.google.com/search/docs/fundamentals/ai-optimization-guide (upd. 2026-07-10) | Keep `llms.txt` as non-load-bearing discovery only. |
| Any Google core/spam update June 27 – July 14 2026 | **None in-window** | status.search.google.com ranking history; Search updates changelog | No new ranking-behavior change to account for. |

**Net**: nothing in the briefs is overturned; the plan is consistent with re-verified primary sources.

## Implementation-approach decisions

### D1 — Blog byline as a real author anchor
- **Decision**: In `templates/blog/article.html`, wrap the existing byline name text
  ("Ehsan Kolivand") in `<a href="/" ...>` styled to inherit the current appearance
  (`color:inherit; text-decoration:none`), with a subtle, compositor-safe hover only.
- **Rationale**: Brief-two §3 (E-E-A-T) wants a visible byline that links to the author page; the
  portfolio is that page (`Person.url = "/"`). A real anchor also satisfies Principle I (crawlable)
  and adds an internal link from every post to the entity home. The `Person.url` in JSON-LD already
  points to `/`, so this makes the visible layer match the structured layer.
- **Alternatives rejected**: A new `/about/` page (out of scope — the portfolio IS the author page);
  linking to `/blog/` (wrong target — that is the collection, not the author entity).
- **Fidelity guard**: appearance must be visually identical; no new color/font; verifier's blog
  design-fidelity checks (#blog-root tokens, no new `@font-face`) unaffected because the change is an
  inline anchor in a template, not a CSS class.

### D2 — `WebSite` node on each post, without displacing `BlogPosting`
- **Decision**: In `scripts/blog/seo.py head_for_post()`, append a third standalone
  `application/ld+json` script containing a `WebSite` node (`@id = config.WEBSITE_ID`, `name`,
  `url`, `publisher = {@id: PERSON_ID}`), AFTER the existing `BlogPosting` (first) and
  `BreadcrumbList` (second) scripts.
- **Rationale**: Brief-two §2 asset A recommends the per-post graph include `WebSite`; it makes each
  crawlable post URL self-contained for entity resolution (matches the index and portfolio). Keeping
  `BlogPosting` as the FIRST script preserves the verifier's first-script contract
  (`verify_build.py` lines 142/218 read the first `ld+json` as the `BlogPosting`).
- **Alternatives rejected**: Wrapping the post's nodes in a single `@graph` (would move
  `@type` off the first script's top level and break the verifier's `obj.get("@type") ==
  "BlogPosting"` assertion); emitting `WebSite` before `BlogPosting` (same breakage).
- **Identity guard**: reuses existing `config.WEBSITE_ID`/`PERSON_ID` (already equal to the portfolio
  `@id`s), so no identity fact changes and no `config.py`/portfolio desync is possible.
- **`_all_jsonld` compatibility**: the verifier flattens all `ld+json` and finds nodes by `@type`;
  an additional `WebSite` object is inert to every existing assertion.

### D3 — Portfolio head completeness (additive, design-neutral)
- **Decision**: Add to `index.html <head>`, without altering identity `@id`s: (a) Atom autodiscovery
  `<link rel="alternate" type="application/atom+xml" title="..." href="/blog/feed.xml">`;
  (b) `<meta name="robots" content="index, follow, max-image-preview:large">`; (c) ProfilePage
  `"dateCreated"` and `"dateModified"` set to a fixed date constant (the portfolio's own last-update
  date — `2026-07-14`, aligned with this pass) so the build stays deterministic.
- **Rationale**: Principle V (completeness on every page) + VIII (discovery). These match what blog
  pages already emit. `max-image-preview:large` lets Search/AI show large previews.
- **Alternatives rejected**: `knowsLanguage`/other new Person facts (no-fabrication); generating the
  portfolio head via the build (Principle VII — the build must copy `index.html` verbatim).
- **Determinism guard**: dates are literal constants in source HTML, never `today()`.

### D4 — Remove dead Google-Fonts preconnects
- **Decision**: Delete the two lines
  `<link rel="preconnect" href="https://fonts.googleapis.com">` and
  `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">` from `index.html`.
- **Rationale**: Confirmed (grep) that no stylesheet/script/font loads from those hosts — all fonts
  are self-hosted and inlined in the PORTFOLIO-FONTS zone. The preconnects open unused TLS
  connections (minor CWV waste) and leak a request to Google (privacy). Removal is non-visual.
- **Guard**: nothing references the hosts, so removal cannot regress LCP; verifier's byte-identity
  check compares built vs. source (both carry the edit) and passes.

### D5 — Add `Applebot` to `robots.txt`
- **Decision**: Add an `Applebot` `Allow: /` stanza; keep every existing token stanza and the
  `Sitemap:` declaration.
- **Rationale**: Applebot feeds Siri/Spotlight/Apple search and Apple Intelligence citations; adding
  it extends search/AI-citation visibility, consistent with the owner's max-visibility posture.
- **Guard**: `robots.txt` is a committed root companion (copied verbatim); the verifier asserts it
  references the sitemap URL — that line is preserved.

## Risks & mitigations

- **First-script contract** (D2): mitigated by appending `WebSite` last and keeping `BlogPosting`
  first; covered by an added unit test and by re-running the verifier.
- **Design fidelity of the byline anchor** (D1): mitigated by inheriting color and removing
  underline; visually identical; verified by inspecting a built post page.
- **Portfolio byte-identity** (D3/D4): the build copies `index.html`; the verifier compares built vs.
  source outside the notes region, so source edits pass by construction; marker zones and `@id`s are
  left untouched.
- **Determinism** (D3): fixed date constants only.
