# Tasks: Best-in-Class SEO + GEO with One-Commit Publishing

**Feature**: `002-seo-geo-publish` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

**Inputs**: plan.md, spec.md (US1–US4), data-model.md, contracts/{structured-data,feed,llms-txt,
verifier}.md, research.md, quickstart.md, constitution.md (v1.2.0).

**Tests**: No separate unit-test framework (project convention). The post-build verifier
(`scripts/verify_build.py`) is the Definition-of-Done gate; each story's verifier-assertion task is
its executable test. Determinism + portfolio-intactness are validated via quickstart.

**Conventions**: `[P]` = parallelizable (different file, no incomplete dep). `[USn]` = user story.
All paths are repo-relative.

---

## Phase 1: Setup

- [ ] T001 Confirm green baseline on branch `002-seo-geo-publish`: run `python scripts/build_blog.py --out _site` then `python scripts/verify_build.py --out _site` and record the baseline (expected: 90 checks, 0 failures, 3 posts).

## Phase 2: Foundational (blocking prerequisites for US1–US4)

- [ ] T002 Add canonical-identity + artifact constants to `scripts/blog/config.py`: `PERSON_ID` (`<base>#person`), `WEBSITE_ID` (`<base>#website`), `AUTHOR_SAMEAS` (GitHub/LinkedIn/Telegram, mirroring the portfolio), `BLOG_FEED_PATH` (`/blog/feed.xml`), and `LLMS_SRC` (repo-root `llms.txt`). Reuse existing `abs_url`.
- [ ] T003 Add derived-value helpers to `scripts/blog/content.py` (pure, no validation change): `Post.word_count` (reuse the read-time tokenizer), `Post.read_minutes` (int parsed from `read_time`), and ISO date access (`date.isoformat()`/`updated.isoformat()` — add `@property` or helpers). Keep deterministic.

## Phase 3: User Story 1 — One-commit publishing + no dangling links (P1) 🎯 MVP

**Goal**: The committed source can never carry a dangling `/blog/<slug>/` link, and the build
regenerates every derived artifact from content. Fixes the live stale-homepage defect and locks it.

**Independent test**: `grep -E "spec-driven-android|custom-layouts-compose|mvi-that-scales" index.html`
returns nothing; build leaves repo `index.html` unmodified while `_site/index.html` shows live
cards; verifier fails if any committed/built page links to a nonexistent post.

- [ ] T004 [US1] Neutralize the committed managed region in `index.html` — **inside the `<!--LATEST-NOTES:START-->`/`<!--LATEST-NOTES:END-->` markers only** — replacing the three seed-post cards with a post-link-free fallback (keep the eyebrow "04 — Writing", the `#notes-h` heading, the dek, the section styles/noscript, and a single `data-morelink` "Read all notes → /blog/" button) plus an HTML comment noting the build injects live cards. Do **not** touch a single byte outside the markers.
- [ ] T005 [US1] Rebuild and confirm: `_site/index.html` managed region is regenerated with the latest 3 live post cards, and `git diff -- index.html` shows **only** changes inside the markers (repo source homepage otherwise byte-identical). (Manual check; encoded by T006 + existing verifier.)
- [ ] T006 [US1] Add "no dangling internal links" assertions to `scripts/verify_build.py`: (a) repo `index.html` contains none of the 3 stale seed slugs and every `/blog/<slug>/` href in it resolves to a current published post; (b) every `/blog/<slug>/` href in each built blog page and in `_site/index.html` resolves to a built post page. (Contract: verifier.md §18–19.)

**Checkpoint**: US1 independently testable. (Full US1 acceptance also lists feed + llms.txt
surfaces — delivered in US3; see Dependencies.)

## Phase 4: User Story 2 — Crawlability + rich-result eligibility (P2)

**Goal**: Every page carries complete, unique metadata; valid, enriched, identity-unified structured
data (article + breadcrumb); accurate canonical/sitemap/lastmod.

**Independent test**: Each page validates as correct structured data (zero errors), carries
og/twitter image metadata + a machine-readable `<time>`, and the sitemap lastmod equals each post's
modified date.

- [ ] T007 [US2] In `scripts/blog/seo.py`, unify identity: post `author`/`publisher` reference `PERSON_ID` (with `author.sameAs = AUTHOR_SAMEAS`, `author.url`, `name`, `jobTitle`); index graph `WebSite.@id = WEBSITE_ID`, `Blog.author.@id = PERSON_ID`, `Blog.isPartOf = {WebSite @id}`. (Contract: structured-data.md.)
- [ ] T008 [US2] In `scripts/blog/seo.py`, add a `BreadcrumbList` to the post head (Home → Field Notes → post) and to the index graph (Home → Field Notes). 3 / 2 items respectively.
- [ ] T009 [US2] In `scripts/blog/seo.py`, enrich post `BlogPosting`: add `url` (= canonical), `wordCount` (>0), `timeRequired` (`PT{read_minutes}M`, omit if unparseable), `isPartOf` (Blog `@id`); keep `inLanguage`, `articleSection`, `keywords` (omit when no tags), `mainEntityOfPage`, `image`, dates.
- [ ] T010 [US2] In `scripts/blog/seo.py`, add `og:image:width`/`og:image:height`/`og:image:alt` + `twitter:image:alt` to both post and index heads (measured cover dims + cover alt for image covers; `1200`/`630` + "Ehsan Kolivand — Field Notes" for the default image).
- [ ] T011 [US2] Add a machine-readable date: in `templates/blog/article.html` wrap the date in `<time datetime="{{DATE_ISO}}">{{DATE}}</time>` (identical inline styling) and pass `DATE_ISO=post.date.isoformat()` from `scripts/blog/render.py::render_article_page`.
- [ ] T012 [US2] Add US2 verifier assertions to `scripts/verify_build.py`: canonical exact; og/twitter image meta present; `<time datetime>` equals post date; `BlogPosting` has `wordCount`/`url`/`author.@id == PERSON_ID`/`inLanguage`; `BreadcrumbList` present (3 items, ends at canonical); index graph has `WebSite @id == WEBSITE_ID` + `Blog.author.@id == PERSON_ID` + breadcrumb (2 items) + **no** `SearchAction`; sitemap lastmod == post `updated` and home lastmod == `max(PORTFOLIO_LASTMOD, newest)`. **Plus two analyze-surfaced DoD guards (C1, C2):** `_site/robots.txt` references the sitemap URL, and every built page `<title>` is unique. (Contract: verifier.md §1–12.)

**Checkpoint**: US2 independently testable and complete on its own.

## Phase 5: User Story 3 — GEO machine-readable surfaces (P3)

**Goal**: A standards-compliant Atom feed and an enriched `llms.txt` list every post; pages advertise
the feed; identity is unified across surfaces.

**Independent test**: `feed.xml` parses as Atom and has one entry per post; `llms.txt` has a
`## Writing` list of every post URL; blog page heads carry a feed-autodiscovery link.

- [ ] T013 [P] [US3] Create `scripts/blog/feed.py` with `build_feed(posts, base_url, portfolio_lastmod) -> str` producing a deterministic Atom 1.0 feed (feed `id/title/subtitle/updated/author/link self+alternate`; per-entry `id`=canonical, `title`, `link`, `published`, `updated`, `summary`, `category` per tag, `author`). All timestamps `<date>T00:00:00Z`; feed `updated`=`max(updated)` or portfolio date when empty; XML-escape via `html.escape`. (Contract: feed.md.)
- [ ] T014 [P] [US3] Create `scripts/blog/llms.py` with `build_llms(base_text, posts, base_url) -> str`: strip any prior `## Writing` block from `base_text`, then append a `## Writing` section listing `- [title](abs_url): excerpt` newest-first (omit the section when no posts). Idempotent + deterministic. (Contract: llms-txt.md.)
- [ ] T015 [US3] Wire outputs in `scripts/build_blog.py`: after rendering posts/index, write `_site/blog/feed.xml` from `feed.build_feed(...)` and `_site/llms.txt` from `llms.build_llms(read(LLMS_SRC), posts, base_url)`. Remove `llms.txt` from the verbatim `ROOT_COPY_ALLOWLIST` copy path (now generated) while keeping its tolerated-if-absent semantics; update related comments.
- [ ] T016 [US3] In `scripts/blog/seo.py::_common`, add the feed-autodiscovery link `<link rel="alternate" type="application/atom+xml" title="…Field Notes" href="/blog/feed.xml">` to every blog page head.
- [ ] T017 [US3] Add US3 verifier assertions to `scripts/verify_build.py`: `_site/blog/feed.xml` exists, parses via `xml.etree.ElementTree`, has feed `id/title/updated`, entry count == published-post count, every post canonical appears as an entry `id`; `_site/llms.txt` exists, contains the author H1 name and (when posts exist) `## Writing` + every post absolute URL; feed-autodiscovery link present on a post page. (Contract: verifier.md §13–17.)

**Checkpoint**: US3 independently testable; completes US1's full acceptance (all 6 derived surfaces).

## Phase 6: User Story 4 — Accessibility + CWV preserved (P4)

**Goal**: No a11y/CWV regression; semantics improved by `<time>` only.

**Independent test**: Each page keeps exactly one `<h1>`, landmarks, alt text, intrinsic cover dims,
reduced-motion reveal, and decorative `aria-hidden`; the `<time>` swap changes no visual styling.

- [ ] T018 [US4] Add/confirm regression-guard assertions in `scripts/verify_build.py`: exactly one `<h1>` per page (existing); cover `width=`/`height=` present (no CLS); `<noscript>` reduced-motion reveal present in head; the `<time>` element carries the same surrounding inline styles (no `<span>`→`<time>` style drift). Keep the existing landmark/h1/token guards.
- [ ] T019 [US4] Confirm font preloads (2 woff2) and required CSS/JS assets are still emitted and unchanged (existing verifier asset checks cover this — extend the comment to note CWV intent). `scripts/verify_build.py`.

## Phase 7: Polish & Cross-Cutting

- [ ] T020 Run the full gate: `python scripts/build_blog.py --out _site` + `python scripts/verify_build.py --out _site`; iterate until green with **≥ 110 checks, 0 failures**.
- [ ] T021 Run quickstart Scenarios A–E (`quickstart.md`): one-commit publish round-trip, no-dangling-links grep, JSON-LD validity script, feed/llms checks, and a two-build determinism `diff -r` (byte-identical). Confirm `git diff -- index.html` differs only inside the managed markers.
- [ ] T022 [P] Tidy `scripts/blog/config.py` comments + `ROOT_COPY_ALLOWLIST`/`ROOT_REQUIRED` notes so they reflect `llms.txt` now being generated (not copied verbatim); ensure no stale guidance remains.
- [ ] T023 Update `PROJECT_CONTEXT.md` to reflect every change (new modules `feed.py`/`llms.py`, structured-data unification, feed/llms surfaces, neutralized homepage region, expanded verifier, constitution v1.2.0, the 002 spec folder, resolved + any new known issues), preserving its confidence-tagged format. *(Executed in cycle Phase 10.)*

---

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002–T003)** must complete before any story.
- **US1 (T004–T006)** is the MVP and depends only on Foundational. Its *core* test (no dangling
  links, regenerate existing artifacts) is independent; its *full* spec acceptance (which also lists
  feed + llms.txt) is completed once **US3** lands.
- **US2 (T007–T012)** depends on Foundational (config identity, content helpers). Independent of US1/US3.
- **US3 (T013–T017)** depends on Foundational. T013 and T014 are `[P]` (separate new files);
  T015–T017 depend on them.
- **US4 (T018–T019)** depends on US2's `<time>` change (T011) for the style-drift guard; otherwise
  independent.
- **Polish (T020–T023)** runs after all stories.

## Parallel Opportunities

- T013 (`feed.py`) and T014 (`llms.py`) — separate new modules, run together.
- Across stories, the three verifier-assertion tasks (T006/T012/T017) edit the same file
  (`verify_build.py`) and so are **not** mutually `[P]`; sequence them (US1 → US2 → US3).
- T002 and T003 touch different files (`config.py`, `content.py`) and can run together.

## Implementation Strategy

- **MVP = US1** (the headline defect fix + publishing integrity). Ship-able and testable alone.
- Then **US2** (rich results) and **US3** (GEO surfaces) — highest external SEO/GEO leverage.
- **US4** is mostly regression-guarding the above.
- Keep the build green after each story (`build_blog.py` + `verify_build.py`); never weaken a
  principle to silence a failure (Constitution Governance).

## Total

23 tasks — Setup 1 (T001), Foundational 2 (T002–T003), US1 3 (T004–T006), US2 6 (T007–T012),
US3 5 (T013–T017), US4 2 (T018–T019), Polish 4 (T020–T023; T023 runs in cycle Phase 10). Verifier
grows from 90 to ≥ 110 checks.
