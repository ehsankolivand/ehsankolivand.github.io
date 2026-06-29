# Quickstart: Build, Verify, and the Font-Subset Procedure (feature 003)

## Build + verify (unchanged commands)

```bash
pip install -r requirements.txt
python scripts/build_blog.py --out _site          # add --drafts for local draft preview
python scripts/verify_build.py --out _site         # Definition-of-Done gate (exit non-zero on fail)
python -m http.server -d _site 8080                # preview http://localhost:8080/blog/
```

A green run prints `verify_build: <N> checks, 0 failure(s)` with **N > 163** (post-002 baseline).

## What changed (feature 003)

- **Identity**: every post page and the blog index now emit `knowsAbout` (the portfolio's grounded
  Android skill list, incl. "Spec-driven development" + "Agentic code generation") + `jobTitle` on the
  canonical author node referenced by `#person`. → engines read the tooling posts as a Senior Android
  Engineer's work, not a separate Python identity.
- **Deep-links**: every body heading carries a stable, invisible `id` (GitHub-style slug). Link to a
  section with `…/blog/<slug>/#<heading-id>`. No visual change.
- **Performance**: the portfolio homepage dropped the unused non-Latin font subsets (~323 KB of base64
  source) — *if* the fidelity proof passed (else deferred; see below). No visual change either way.
- **Inherited fixes**: constitution finalized at v1.3.0; 001/002 spec status set to Implemented;
  verifier hardened (sameAs exactness, author/locale, article:tag, anchors, font fidelity).

## Font-subset procedure (one-time, offline — no CI/runtime dependency)

This is the only edit to portfolio source, inside the sanctioned `PORTFOLIO-FONTS` zone.

1. **Mark the zone**: add `<!--PORTFOLIO-FONTS:START-->` immediately before, and
   `<!--PORTFOLIO-FONTS:END-->` immediately after, the `<style>` block holding the 54 `@font-face`
   rules in `index.html`.
2. **Snapshot the baseline**: copy `index.html` → `assets/portfolio-fonts/index.baseline.html` (full
   original, recoverable; never served).
3. **Subset**: delete the 32 `@font-face` rules whose `unicode-range` is Cyrillic / Cyrillic-ext /
   Greek / Vietnamese (and their `/* subset */` label comments). Keep Latin + Latin-ext.
4. **Prove**: `python scripts/build_blog.py --out _site && python scripts/verify_build.py --out _site`.
   The verifier proves (a) every rendered codepoint keeps its coverage and (b) nothing outside the zone
   changed vs. the baseline. If it fails → **defer**: restore `index.html` from the baseline (or `git
   checkout` it), record the reason; the rest of the feature still ships green.

## Validate the positioning by hand (optional)

```bash
# author identity on a post (should show jobTitle + knowsAbout + #person @id):
grep -o '"jobTitle":"[^"]*"' _site/blog/*/index.html | head
grep -o '"knowsAbout":\[[^]]*\]' _site/blog/telegram-topic-export-markdown-jsonl/index.html
# heading ids present:
grep -oE '<h[234] id="[^"]+"' _site/blog/telegram-topic-export-markdown-jsonl/index.html | head
# portfolio lighter (bytes): compare to the baseline
wc -c index.html assets/portfolio-fonts/index.baseline.html
```

## Publish (unchanged — single commit)

Add/edit one note under `content/blog/` and push to `main`. CI builds, verifies, deploys. A new
Android/Architecture note flows into every surface (nav, index, sitemap, feed, llms.txt, homepage
notes, structured data) with no other edit — proving the positioning scaffold.
