# BUG_AUDIT.md

> Autonomous line-by-line code audit of the personal-site repo (portfolio + Obsidian-driven static blog generator).
> **Date:** 2026-06-29.
> **Status:** COMPLETE.
> **Summary:** 16 findings — Critical: 0 · High: 1 · Medium: 5 · Low: 10 (+ 4 minor nits). The current committed content builds green (verifier passes); every finding below is **latent** — triggered by specific content/frontmatter or input shapes not present in the 3 committed posts — except the documentation/consistency items, which are present now.

This file is a worklist of confirmed bugs/defects found by reading the codebase. Nothing else in the repo is modified by this audit. Each item: **What / Why it's a bug / Where / Severity / Suggested fix.**

---

## Critical

_(none found — the build is green on current content and no defect breaks the build, corrupts output, or is a remotely-exploitable hole on the committed posts; the closest, BUG-001, is in High.)_

## High

- [x] **BUG-001 — JSON-LD string fields can break out of the `<script>` block (`</script>` / `<` injection).** _Fixed: `seo._jsonld` now escapes `<`/`>`/`&` to JSON `\uXXXX` escapes after `json.dumps`, so author text can't terminate the script element; the JSON stays valid and round-trips through `json.loads`. Regression test: `tests/test_seo.py::TestJsonLdScriptSafety` (3 cases)._
  - **What**: `seo._jsonld()` serializes JSON-LD with `json.dumps(obj, ensure_ascii=False, separators=(",", ":"))` and embeds the result directly in `<script type="application/ld+json">{payload}</script>`. `json.dumps` does NOT escape `<`, `>`, or `/`. Any author-controlled string that ends up in JSON-LD (`headline`/`post.title`, `description`/`excerpt`, `keywords`/tags) containing the substring `</script>` (or `<!--`, `<script`) terminates the script element early.
  - **Why it's a bug**: Violates the stated invariant "full HTML escaping … injection of unescaped content into HTML/XML (feed, sitemap, JSON-LD)." A post titled e.g. `Escaping </script> in templates` injects raw markup into `<head>` / produces invalid JSON-LD. In practice the verifier's `_all_jsonld` regex stops at the first `</script>` → JSON parse fails → the build is failed with a confusing "JSON-LD failed to parse" message, so a legitimate technical title becomes an unpublishable post. (Plain `<` like `List<T>` is fine; only the `</script`-style sequence triggers it.)
  - **Where**: `scripts/blog/seo.py:47-49` (`_jsonld`); reached from `head_for_post` (`blogposting`, `breadcrumb`) and `head_for_index` (`@graph`).
  - **Severity**: High — injection vector explicitly in scope; breaks output validity / fails the build on realistic technical content.
  - **Suggested fix**: After `json.dumps`, escape the HTML-sensitive sequences for `<script>` context, e.g. `payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")` (and optionally ` `/` `). This keeps valid JSON-LD while preventing element breakout.

## Medium

- [x] **BUG-002 — `image:` frontmatter is never validated to exist; broken `og:image`/JSON-LD image ships silently.** _Fixed: `load_post` now calls `_require_media_file` for a content-relative `image:` (fail loud on a 404, like covers/body images), while an absolute http(s) URL is allowed; `seo._post_image` emits an absolute `image:` verbatim instead of mangling it through `media_url`. Regression tests: `test_content.py::TestImageValidation` + `test_seo.py::TestPostImage`._
  - **What**: `load_post` validates only image *cover* `src` via `_require_media_file`. A standalone `image:` frontmatter key (used by `seo._post_image`) is taken verbatim with no existence check. `_post_image` also runs it through `config.media_url()`, so an absolute URL (`image: https://cdn/x.png`) is mangled into `/blog/assets/media/https://cdn/x.png`.
  - **Why it's a bug**: A code-cover post with `image: assets/missing.png` (or an image-cover post overriding `image:`) ships `og:image`/`twitter:image`/JSON-LD `image` pointing at a 404, with no build error — defeating the project's "fail loud on missing media" guarantee (the `_require_media_file` docstring explicitly warns a missing file "would ship a broken `<img>` and a broken og:image silently"). The verifier does not catch it.
  - **Where**: `scripts/blog/content.py:361` (`image = ...` unvalidated) and `scripts/blog/seo.py:68-80` (`_post_image`); contrast `content.py:344-345` which validates `cover.src`.
  - **Severity**: Medium — wrong/broken social+SEO output under a specific but realistic frontmatter; silent.
  - **Suggested fix**: When `image:` is a content-relative path (not http/https), call `_require_media_file(image, source, "image")` in `load_post`; reject or pass through absolute URLs explicitly instead of running them through `media_url`.

- [x] **BUG-003 — False-positive GFM table: a text line containing `|` followed by a dash-run line is parsed as a table.** _Fixed: the table trigger now also requires the delimiter row's cell count to equal the header row's (GFM's explicit rule), so a paragraph with a `|` directly above a `---` thematic break (2 cells vs 1) is no longer misparsed as a 1-column table. Single-column (1==1), borderless (2==2), and bordered tables still match. Regression tests added (`test_pipe_paragraph_above_dashes_is_not_a_table`, `test_borderless_table_with_matching_delimiter_still_recognized`)._
  - **What**: The table trigger is `"|" in s and _is_table_sep(lines[i+1])`. `_is_table_sep` accepts any line whose pipe-split cells all match `^:?-+:?$`, including a bare `---`/`----` (single "column"). It never checks that the delimiter column count matches the header column count (GFM requires this). So a normal paragraph line that happens to contain `|`, immediately followed (no blank line) by a thematic break `---`, is misrendered as a 1-column-delimiter table.
  - **Why it's a bug**: Wrong output — a paragraph + horizontal rule (or a setext-ish `---`) silently becomes a malformed table; the intended `<hr>`/paragraph is lost. Diverges from GFM, which would not treat mismatched column counts as a table.
  - **Where**: `scripts/blog/markdown_render.py:567` (trigger) + `:419-423` (`_is_table_sep`); `_SEP_CELL` at `:416`.
  - **Severity**: Medium — realistic content (any line with a literal `|` directly above a dashes line) renders incorrectly.
  - **Suggested fix**: Require the delimiter row's cell count to equal the header row's cell count before treating it as a table (and/or require ≥2 columns, matching common GFM implementations).

- [x] **BUG-004 — URL-scheme allow-list can be bypassed by an embedded NUL/control char (`java\x00script:`).** _Fixed: `_is_safe_url` now strips every embedded C0 control + DEL (`[\x00-\x1f\x7f]`, subsuming the old `\t\n\r` removal) before scheme detection, in addition to the leading-control/space trim — so `java\x00script:` is reassembled to `javascript:` and rejected. Regression test added (`test_embedded_control_char_scheme_bypass_neutralized`); existing `javascript:`/`data:`/`vbscript:` tests still pass._
  - **What**: `_is_safe_url` strips only *leading* `\x00-\x20` and removes `\t\n\r` from anywhere, then tests the scheme. An embedded NUL/other C0 control in the middle of the scheme (e.g. `java\x00script:alert(1)`) is not removed, so the scheme regex fails to match → the URL is treated as schemeless/"safe" and emitted as an `href`. `html.escape` does not strip the NUL. Browsers that strip embedded NULs from URLs would then see `javascript:`.
  - **Why it's a bug**: Defeats the renderer's stated security-by-construction allow-list (the very `javascript:` neutralization the unit tests assert). Author-trusted lowers real-world impact, but it is a genuine hole against the documented invariant and the code already aims to defeat the leading-control variant.
  - **Where**: `scripts/blog/markdown_render.py:51-61` (`_is_safe_url`).
  - **Severity**: Medium — security-by-construction gap; exploitability depends on browser NUL handling + a hand-crafted/pasted control char in source.
  - **Suggested fix**: Strip/forbid all C0 control chars (`[\x00-\x1f\x7f]`) anywhere in the URL before scheme detection, or reject URLs containing them.

- [x] **BUG-005 — `tags:` as a non-list, non-string scalar raises an unhandled `TypeError` instead of `ContentError`.** _Fixed: `load_post` now branches explicitly on str/list and raises a file-identifying `ContentError` for any other type (`tags: 5`, `tags: true`), while still treating falsy values as no tags. Regression tests: `tests/test_content.py::TestTagsValidation` (5 cases)._
  - **What**: In `load_post`, `tags = meta.get("tags") or []`; if `tags` is truthy and not a `str`, it is iterated: `[str(t).strip() for t in tags]`. A scalar like `tags: 5` (int) or `tags: true` is truthy and non-iterable → `TypeError: 'int' object is not iterable`.
  - **Why it's a bug**: Violates "fail loud with a file-identifying message." Instead of a clean `ContentError` naming the file, the build dies with a bare Python traceback that doesn't identify the offending note.
  - **Where**: `scripts/blog/content.py:334-337`.
  - **Severity**: Medium — ungraceful crash on malformed (but plausible) frontmatter; no file context.
  - **Suggested fix**: Coerce/validate: if not a list or str, raise `ContentError(f"{source}: 'tags' must be a list or comma-separated string")`.

- [x] **BUG-011 — Author content containing a literal `{{TOKEN}}` triggers a false "unresolved template tokens" build failure.** _Fixed: `verify_build.TOKEN_RE` is now scoped to the real template-slot vocabulary (the `{{NAME}}` tokens that actually appear in `templates/blog/**`, computed at load), so an unfilled slot like `{{TITLE}}` still fails but author interpolation (`{{user}}`, `{{count}}`, `{{ctx.value}}`) renders without tripping it. The `<sc-if>`/`<sc-for>` directive scan is unchanged. Regression test: `tests/test_verify_token_scan.py`._
  - **What**: The renderer deliberately keeps author-written `{{word...}}` literal (single-pass substitution / anti-injection — see `sub_tokens` and `tests/test_markdown_render.py::TestTokenInjection`). But the verifier scans every built page with `TOKEN_RE = r"\{\{[A-Za-z_][^}]*\}\}|..."` and fails on any match (`ok(not TOKEN_RE.search(h), "...unresolved template tokens present")`). So a post that legitimately contains `{{user}}`, `{{count}}`, etc. (Handlebars/Mustache/Angular-style interpolation — realistic for a dev-tooling blog) renders correctly but then fails verification.
  - **Why it's a bug**: Direct contradiction between two shipped components: the renderer (and its own unit tests) treat `{{...}}` as valid literal content, while the verifier rejects it — failing the build with a misleading "unresolved template tokens" message on correct content. The verifier's own fixture (`verify_build.py:532`) even asserts `{{BODY}}` survives rendering, yet `:114` rejects it on a real page. (Note: the trigger requires no space after `{{` — `{{ msg }}` is safe, `{{msg}}` is not.)
  - **Where**: `scripts/verify_build.py:22` (`TOKEN_RE`), `:114` and `:224` (the checks) vs `scripts/blog/markdown_render.py:293-298` (`sub_tokens`, intentional literal preservation).
  - **Severity**: Medium — false-positive build failure on realistic author content; confusing diagnostic; renderer is correct.
  - **Suggested fix**: Make the verifier check for stray tokens only against the known template-token set (the tokens the build actually substitutes), or scan the templates/partials pre-fill rather than the final page, so author-authored `{{...}}` literals don't trip it.

## Low

- [ ] **BUG-006 — `display_date()` zero-pads the day (`Jun 08, 2026`).** _Not a bug (misreported): the canonical design source `Ehsan Koolivand - Blog.html` itself uses zero-padded days (`Apr 02, 2026`, `Jun 02, 2026`, `May 06, 2026`), so `{d.day:02d}` faithfully reproduces the design. Switching to `{d.day}` ("Jun 8") would DIVERGE from the design and violate Principle III (design fidelity). No code change._
  - **What**: `display_date` formats with `{d.day:02d}`, producing a leading zero for single-digit days ("Jun 08, 2026"), whereas the documented/design format is "Jun 8, 2026"-style.
  - **Why it's a bug**: Minor visual inconsistency with the design bundle and the docstring's own example (`'Jun 18, 2026'`); affects the chip date, JSON-LD-adjacent display, sitemap is unaffected. Only manifests for days 1–9.
  - **Where**: `scripts/blog/content.py:75-77` (`display_date`).
  - **Severity**: Low — cosmetic; only single-digit days.
  - **Suggested fix**: Use `{d.day}` (no padding) to match "Jun 8, 2026".

- [x] **BUG-007 — `extract_related` strips a legitimate trailing thematic break (`---`).** _Fixed: a trailing separator is now consumed only once a real related block (links/heading) has been found below it; a bare trailing `---` with no related block is preserved in the body. Regression tests: `test_content.py::TestExtractRelated` (3 cases). (Note: the reported visible loss of an `<hr>` doesn't actually occur today — `render()` skips thematic breaks — but the extraction is now correct and future-proofed.)_
  - **What**: Scanning from the bottom, a trailing `---`/`***`/`___` line sets `cut = i` and is removed even when there is no related-links block beneath/above it. A post that intentionally ends with a horizontal rule loses it.
  - **Why it's a bug**: Silent content loss (a trailing `<hr>` disappears from the rendered post). Edge-case but real.
  - **Where**: `scripts/blog/content.py:160-163` (the `if line in ("---", "***", "___")` branch inside `extract_related`).
  - **Severity**: Low — uncommon authoring pattern; non-destructive to meaning.
  - **Suggested fix**: Only consume separators when an actual related block (heading or link-only lines) is found; otherwise leave a trailing rule intact.

- [x] **BUG-008 — Inconsistent default image dimensions (1200×675 vs 1200×630).** _Fixed: the body-image fallback in `build_blog.image_resolver` now uses `1200×630`, matching `Cover` defaults and `seo._post_image`. No committed content uses the unmeasurable-image path, so current output is unchanged (build still byte-identical)._
  - **What**: `build_blog.image_resolver` falls back to `(1200, 675)` for unmeasurable body images, while `content.Cover` defaults and `seo._post_image` use `1200×630`.
  - **Why it's a bug**: Inconsistent intrinsic dimensions for unmeasurable formats (svg/webp/avif) → minor layout/aspect mismatch and inconsistent metadata; not deterministic-breaking but sloppy.
  - **Where**: `scripts/build_blog.py:176` vs `scripts/blog/content.py:209-210` and `scripts/blog/seo.py:79-80`.
  - **Severity**: Low — only affects unmeasurable image formats.
  - **Suggested fix**: Pick one default (e.g. 1200×630) everywhere.

- [x] **BUG-009 — Misleading sitemap comment: `/blog/` is always emitted, not "omitted when there are no posts."** _Fixed (comment + doc, no behavior change): the code is correct — `/blog/` is always rendered (even empty) so it belongs in the sitemap; only its `<lastmod>` is conditional. Corrected the inline comment in `sitemap.py` and the PROJECT_CONTEXT references. Wrapping `url(blog, …)` in `if posts:` was rejected because it would drop a real, always-generated page._
  - **What**: `url(blog, newest)` is called unconditionally; only the `<lastmod>` is conditional (`if lastmod:`). The inline comment "# omitted when there are no posts" and PROJECT_CONTEXT §11.5 ("sitemap omits /blog/") describe behavior the code does not implement.
  - **Why it's a bug**: Code/doc inconsistency; if the documented intent (omit `/blog/` when empty) is correct, this is also a latent logic gap.
  - **Where**: `scripts/blog/sitemap.py:30` (and `:13`, `:31`).
  - **Severity**: Low — `/blog/` index is always generated, so listing it is acceptable; this is primarily a doc/intent mismatch.
  - **Suggested fix**: Fix the comment, or wrap `url(blog, newest)` in `if posts:` to match the documented behavior.

- [ ] **BUG-010 — Atom entry `id`/`link` ignore a per-post `canonical` override (inconsistent with JSON-LD/`og:url`).**
  - **What**: `feed.build_feed` uses `config.abs_url(base_url, p.url)` for each entry's `<id>` and `<link>`, while `seo.py` uses `post.canonical` (which honors a frontmatter `canonical:` override) for `og:url`/JSON-LD `url`.
  - **Why it's a bug**: If an author sets a custom `canonical:`, the feed advertises a different URL than the canonical/OG/JSON-LD, a minor cross-surface inconsistency.
  - **Where**: `scripts/blog/feed.py:42,45,46` vs `scripts/blog/seo.py:98,116,143`.
  - **Severity**: Low — only triggers when `canonical:` is overridden (no committed post does).
  - **Suggested fix**: Use `p.canonical` for the entry `<id>`/`<link>` (or document the divergence).

- [ ] **BUG-012 — A paragraph immediately after a table that contains a `|` is absorbed as a table row.** _Not a bug (GFM-conformant): traced against the GFM/cmark-gfm reference — a table continues on every non-blank line until a blank line or another block structure (GFM example 279 absorbs even a no-pipe `bar` line as a row). A pipe-bearing prose line directly under a table is absorbed as a row by GFM too, and there is no syntactic way to distinguish a borderless body row (`1 | 2`) from prose-with-a-pipe — which is precisely why GFM requires the blank-line boundary the committed content already uses. "Fixing" it would diverge from GFM and break borderless/ragged tables (which have tests). No code change._
  - **What**: The table body loop continues while `lines[i].strip() and "|" in lines[i]`. A normal paragraph placed directly under a table (no blank line) that happens to contain a `|` is consumed as an extra table row instead of starting a paragraph.
  - **Why it's a bug**: Wrong output — prose gets pulled into the table. Same root cause family as BUG-003 (no blank-line boundary / loose table heuristics).
  - **Where**: `scripts/blog/markdown_render.py:572-574`.
  - **Severity**: Low — requires no blank line after the table and a `|` in the following line.
  - **Suggested fix**: End the table at a line that is not itself pipe-delimited in table shape, or require a blank line / treat a line with no leading-or-trailing pipe context as prose.

- [ ] **BUG-013 — Author guide (`content/blog/README.md`) is stale for feature 004 and references deleted seed posts.**
  - **What**: The README still says fenced code blocks use "the text after the backticks is the code-card caption" and never documents 004's syntax highlighting (a bare-word first token is now the language, e.g. ` ```kotlin `, with optional `title="…"` filename + `{n}` line-emphasis). It also uses deleted seed slugs (`mvi-that-scales`, `spec-driven-android`) in its related-links example.
  - **Why it's a bug**: The single author-facing guide misdescribes current behavior — an author following it won't know they can request highlighting, and may be surprised that ` ```python ` now shows a "python" label. The example slugs point at posts that no longer exist.
  - **Where**: `content/blog/README.md:32-41` (code-fence description/example), `:48-49` (seed slugs).
  - **Severity**: Low — documentation drift; not served, doesn't affect the build.
  - **Suggested fix**: Update the code-fence section to document the info-string (language / `title=` / `{n}`) and replace the seed-slug example with current slugs.

- [ ] **BUG-014 — `h3`/`h4` body headings render with the identical visual style to `h2`.**
  - **What**: All body headings are filled through one partial (`block-h2.html`) that hardcodes the h2 style; only the semantic tag varies (`<h2>`/`<h3>`/`<h4>`). So `###`/`####` have correct semantics but no visual size/weight hierarchy.
  - **Why it's a bug**: Readers get no visual sub-heading distinction; a long post's structure is flattened visually. (May be an accepted limitation of the single-heading-style design, hence Low.)
  - **Where**: `scripts/blog/markdown_render.py:525` (one partial for all levels) + `templates/blog/partials/block-h2.html`.
  - **Severity**: Low — cosmetic/hierarchy; semantics + anchors are still correct.
  - **Suggested fix**: Add level-scaled styles (e.g. via `font-size` per `h2/h3/h4` in `blog.css` under `#blog-root`) or distinct partials.

- [ ] **BUG-015 — Index hero hardcodes a "New · Spec-driven Android" badge for a non-existent post.**
  - **What**: The blog index template's hero shows a static badge `New · Spec-driven Android`. There is no such post (`spec-driven-android` is a known *deleted* seed slug), so the badge advertises content that does not exist.
  - **Why it's a bug**: Misleading/stale UI copy; the "New ·" framing implies a recent post that can't be opened.
  - **Where**: `templates/blog/index.html:7`.
  - **Severity**: Low — cosmetic; static marketing text, not a link.
  - **Suggested fix**: Make the badge generic ("New · Field notes") or drive it from the latest post; remove the dangling topic reference.

- [ ] **BUG-016 — `nav-item` category links are not URL-encoded (latent).**
  - **What**: `render_nav` builds hrefs as `"/blog/#cat=" + c.name` with no percent-encoding, while the JS writes the same hash with `encodeURIComponent(f)`. For a category name containing a space or special char the static href would be malformed and inconsistent with the JS-written hash.
  - **Why it's a bug**: Latent — current categories (Compose/Architecture/Tooling/Crypto) are single words, so it doesn't trigger today, but a multi-word category would ship a broken/inconsistent anchor.
  - **Where**: `scripts/blog/render.py:40` vs `templates/blog/assets/blog.js:118`.
  - **Severity**: Low — latent; only with non-simple category names.
  - **Suggested fix**: URL-encode the category in the href to match the JS.

### Minor nits (non-blocking, noted for completeness)

- **Wordmark casing inconsistency**: `config.SITE_BRAND`/`base.html` use `Ehsan.kolivand` (lower-case `k`), while `site.webmanifest` `short_name` is `Ehsan.Kolivand` (capital `K`). Cosmetic branding drift.
- **CI concurrency**: `.github/workflows/deploy.yml` puts both `build` and `deploy` in one `pages` group with `cancel-in-progress: true`; GitHub's recommended Pages pattern uses `cancel-in-progress: false` for the deploy so an in-flight deployment isn't interrupted by a new push. Low risk (the next run redeploys).
- **`copytree` would copy stray `.DS_Store`/editor files** if any ever appear under `templates/blog/assets/` or `content/blog/assets/` (no filter); none present today.
- **`image_size` JPEG scanner** doesn't special-case standalone markers (RST/`0xD0-0xD9`); a non-standard JPEG could mis-measure (best-effort, build-time only; no committed image content exercises it).

---

## Coverage log

**Read end-to-end (every line):**
- Generator: `scripts/build_blog.py`, `scripts/verify_build.py`, `scripts/blog/__init__.py`, `config.py`, `content.py`, `markdown_render.py`, `render.py`, `seo.py`, `sitemap.py`, `feed.py`, `llms.py`, `highlight.py`.
- Tests: `tests/__init__.py`, `tests/test_markdown_render.py`, `tests/test_highlight.py`.
- Templates: `templates/blog/base.html`, `index.html`, `article.html`, and all 24 partials (`block-h2/-code/-callout/-footnotes/-table/-quote/-p/-list/-list-item/-olist/-olist-item/-img/-img-caption/-img-placeholder`, `grid-card`, `featured-card`, `home-notes-section`, `more-note`, `more-notes-section`, `nav-item`, `cover-code`, `cover-image`, `cover-featured-code`, `cover-featured-image`).
- Assets: `templates/blog/assets/blog.css`, `templates/blog/assets/blog.js`.
- Content: `content/blog/categories.yml`, the 3 posts (`ankivoice-…`, `speakloop-…`, `telegram-…`), `content/blog/README.md`.
- Config/CI/companions: `.github/workflows/deploy.yml`, `requirements.txt`, `robots.txt`, `llms.txt` (root), `site.webmanifest`, `.gitignore`.

**Read for all logic/markup-bearing parts (not the inlined base64 font blobs):** `index.html` (the 738 KB portfolio) — verified: `LATEST-NOTES` + `PORTFOLIO-FONTS` markers, the neutralized Field-notes region, the `[data-reveal]` IntersectionObserver reveal path (lines ~1094-1107) that animates the build-injected cards, the JSON-LD `@graph` (Person/WebSite `@id`, `jobTitle`, `knowsAbout`, `sameAs` — all match `config`), `<h1>` count (1), and that no `/blog/<slug>/` links exist in source. The remainder is inlined woff2 base64 + static design markup with no build logic.

**Intentionally not line-read (out of "code that can break" scope, reviewed only as reference):** Spec Kit artifacts under `specs/**` and `.specify/**` (specs, plans, contracts, checklists, and the `.specify/scripts/bash/*.sh` Spec Kit workflow helpers — these are authoring/governance tooling, not part of the deployed site build); binary assets (favicons, icons, `og-image.png`, `*.woff2`); `assets/portfolio-fonts/index.baseline.html` (a non-served data artifact, but the verifier logic that consumes it was read); generated `_site/**` (build output); `__pycache__/*.pyc`; the untracked `Ehsan Koolivand - Blog.html` design bundle. None could read as fully; all were deliberately skipped as non-load-bearing for site correctness.

## Confidence notes

- **Most confident**: the renderer/SEO/highlighter findings (BUG-001 JSON-LD `</script>`, BUG-003/BUG-012 table heuristics, BUG-004 URL allow-list, BUG-011 `{{}}` verifier contradiction, BUG-005 `tags` crash) — traced directly in source against call sites and the unit tests/verifier, and the security claims cross-checked against what `json.dumps`/`html.escape` actually do. BUG-002 (`image:` unvalidated) verified by following the field from `content.load_post` into `seo._post_image` and confirming no existence check.
- **Confident**: the determinism review (no `today()`/wall-clock; dict/JSON key order and sorts are stable; set usage is membership-only) — I found no determinism violation, consistent with the project's stated byte-identical-rebuild property.
- **Less certain (severity, not existence)**: BUG-001 and BUG-011 both currently surface as *verifier build failures* rather than shipped-bad-output for the committed content, so their real-world blast radius depends on whether `verify_build.py` is always run (CI does). I rated by root cause (missing escaping / overly-broad token scan). The Low cosmetic items (BUG-014 heading hierarchy, BUG-015 hero badge) may be deliberate design choices.
- **Did not dynamically execute** the build/tests in this audit (static reading only); findings are from code tracing. The repo's own report (verifier 318 checks green on current content) is consistent with all findings being latent rather than currently-firing.
- **Not re-verified**: byte-level fidelity of the untracked design bundle vs the extracted templates, and the exact contents of `specs/**` (treated as reference, not ground truth, per the audit brief).
