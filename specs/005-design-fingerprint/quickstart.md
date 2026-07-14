# Quickstart — Build, Verify, Re-Audit, Exercise Robots

Validation guide proving the redesign works end-to-end and stays in-bounds. Run from repo root.

## Prerequisites
- Python 3.11+ (stdlib + PyYAML per `requirements.txt`). No new dependency is introduced.

## 1. Renderer unit tests (must stay green)
```bash
python -m unittest discover -s tests
```
Expected: OK, all tests pass (baseline 71; may increase as markup-shape tests are added). Any RED = fix the renderer, never disable a test.

## 2. Build the site
```bash
python scripts/build_blog.py
```
Expected: builds `_site/` deterministically; the portfolio homepage `_site/index.html` has its `LATEST-NOTES` region regenerated; `_site/blog/**`, `feed.xml`, `llms.txt`, `sitemap.xml` present.

## 3. Definition-of-Done verifier (must pass, incl. new in-bounds checks)
```bash
python scripts/verify_build.py
```
Expected: all checks pass (baseline 318 + new fingerprint checks). The new checks assert: no new `@font-face`/colour system on either surface; blog fingerprint CSS only under `#blog-root`; both portfolio marker zones present + paired; canonical Person/WebSite `@id` + per-page SEO intact; exactly one `<h1>` per page; every protected robot behaviour hook present on both surfaces.

## 4. Re-run the slop audit (acceptance oracle for SC-001/002)
- `hallmark audit templates/blog` and `hallmark audit index.html` → expect no slop-gate failures; the Slop-Tell Ledger items absent.
- `python3 /Users/ehsankolivans/.claude/plugins/marketplaces/ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max/scripts/search.py "editorial technical developer blog dark" --design-system` → confirm no-emoji-icons / contrast / minimal-glow checks pass.

## 5. Exercise the robots (acceptance oracle for SC-005)
Open `_site/index.html` (portfolio) and `_site/blog/index.html` + a post in a browser and confirm each still reacts:
- Portfolio: scroll fast (reactor shouts + speed lines), move cursor (magnetic ring), tap the logo several times (party/confetti easter egg), watch the chase gag + android mascot, hover cards.
- Blog: scroll (reactor + grad-cap follow), hero companion blinks/bobs, article shows the robot author-avatar, cursor is magnetic, links ripple.
- Toggle OS "reduce motion" → spatial motion collapses to crossfade; robots settle; nothing animates indefinitely. No horizontal scroll at 320/375/414/768px.

## 6. Design-decision evidence (SC-003)
The per-surface, per-dimension before→after record lives in [plan.md](./plan.md) §Design Decisions (D1–D6) and the [token contract](./contracts/fingerprint-token-layer.md); the shared token layer (same names/values on both surfaces) is the one-fingerprint proof.

## Done when
Steps 1–3 green, step 4 shows no slop-gate failures, step 5 shows every robot still reactive, and the Constitution Check in plan.md passes.
