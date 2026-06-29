#!/usr/bin/env python3
"""Build the deployable static site from Obsidian content + the extracted design.

Reads content/blog/*.md (+ categories.yml) and templates/blog/*, writes a complete
site to --out (default _site): portfolio + root companions copied verbatim, blog index
and one static page per post, regenerated sitemap, and .nojekyll. The copied portfolio
index.html has only its managed "Field notes" region (between the <!--LATEST-NOTES:*-->
markers) deterministically regenerated from the latest posts; everything outside that
region is byte-for-byte identical to source and the repo source file is never modified.

Deterministic: same inputs -> byte-identical outputs (Constitution: GitHub Pages only).
"""
from __future__ import annotations
import argparse
import re
import shutil
import struct
import sys
from pathlib import Path

# Markers in the portfolio index.html delimiting the auto-synced "Field notes" section.
HOME_NOTES_START = "<!--LATEST-NOTES:START-->"
HOME_NOTES_END = "<!--LATEST-NOTES:END-->"

sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow `import blog.*`

from blog import config, content, render, sitemap, feed, llms  # noqa: E402


# --------------------------------------------------------------------------- #
# Minimal stdlib image-dimension reader (PNG/JPEG/GIF) -> (w, h) or None
# --------------------------------------------------------------------------- #
def image_size(path: Path):
    try:
        data = path.read_bytes()
    except OSError:
        return None
    n = len(data)
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
            if n < 24:
                return None
            w, h = struct.unpack(">II", data[16:24])
            return int(w), int(h)
        if data[:3] == b"\xff\xd8\xff":  # JPEG
            i = 2
            while i + 1 < n:               # need data[i] and data[i+1]
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                              0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    if i + 9 > n:
                        return None
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return int(w), int(h)
                if i + 4 > n:
                    return None
                seg = struct.unpack(">H", data[i + 2:i + 4])[0]
                i += 2 + seg
            return None
        if data[:6] in (b"GIF87a", b"GIF89a"):
            if n < 10:
                return None
            w, h = struct.unpack("<HH", data[6:10])
            return int(w), int(h)
    except (struct.error, IndexError):
        return None
    return None


def copytree(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build the Obsidian-driven blog.")
    ap.add_argument("--out", default="_site")
    ap.add_argument("--base-url", default=config.DEFAULT_BASE_URL)
    ap.add_argument("--drafts", action="store_true", help="include draft posts (local preview only)")
    args = ap.parse_args(argv)

    base_url = args.base_url
    out = Path(args.out).resolve()
    # Safety: step 2 below rmtree's `out`. Refuse to delete the repo root / an ancestor or any
    # directory that holds source, so a misconfig like `--out .` can't recursively wipe the project.
    if out == config.REPO_ROOT or out in config.REPO_ROOT.parents:
        raise SystemExit(f"ERROR: refusing to build into {out} (repo root or an ancestor); "
                         "use a dedicated build dir like _site.")
    if out.exists():
        source_markers = [m for m in (".git", "scripts", "templates", "content", "specs")
                          if (out / m).exists()]
        if source_markers:
            raise SystemExit(f"ERROR: refusing to delete {out} — it looks like a source directory "
                             f"(contains {', '.join(source_markers)}); use a build dir like _site.")
    blog_out = out / "blog"
    media_out = blog_out / "assets" / "media"

    # 1. Load + validate content (fails loud on errors)
    cats = content.load_categories(config.CONTENT_DIR / "categories.yml")
    posts = content.load_posts(config.CONTENT_DIR, cats, base_url, include_drafts=args.drafts)

    # 2. Fresh output dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    # 3. Copy root companion files verbatim (portfolio untouched — Principle VII)
    copied = []
    missing = []
    for name in config.ROOT_COPY_ALLOWLIST:
        src = config.REPO_ROOT / name
        if src.exists():
            shutil.copy2(src, out / name)
            copied.append(name)
        else:
            missing.append(name)
    # .nojekyll: single source of truth — always written (not in the copy allowlist) so
    # Pages serves files verbatim even if the repo root lacks it.
    (out / ".nojekyll").write_text("", encoding="utf-8")
    required_missing = [n for n in config.ROOT_REQUIRED if n in missing]
    if required_missing:
        raise SystemExit(
            "ERROR: missing required root companion file(s): " + ", ".join(required_missing) +
            " (Constitution V/VII: robots.txt, site.webmanifest, the favicon set, and "
            "og-image.png MUST be reused). Add them to the repo root before building."
        )

    # 3b. Auto-sync the homepage "Field notes" section (latest 3 posts) between markers.
    idx_path = out / "index.html"
    if idx_path.exists():
        html = idx_path.read_text(encoding="utf-8")
        if HOME_NOTES_START in html and HOME_NOTES_END in html:
            if posts:
                section = render.render_home_notes(posts, cats)
                region = HOME_NOTES_START + "\n    " + section + "\n    " + HOME_NOTES_END
                html = re.sub(re.escape(HOME_NOTES_START) + r".*?" + re.escape(HOME_NOTES_END),
                              lambda _m: region, html, count=1, flags=re.S)
                idx_path.write_text(html, encoding="utf-8")
                print("  homepage: refreshed Field-notes section with latest 3 posts")
        else:
            print("  NOTE: index.html has no LATEST-NOTES markers; homepage notes not injected")

    # 4. Copy design assets (css, js, fonts) -> /blog/assets/
    copytree(config.TEMPLATE_ASSETS_DIR, blog_out / "assets")

    # 5. Copy author media (covers + body images) -> /blog/assets/media/
    src_assets = config.CONTENT_DIR / "assets"
    if src_assets.exists():
        copytree(src_assets, media_out)

    # image resolver for body images: public url + intrinsic dimensions (no CLS).
    # Fails loud if the src resolves outside the copied content/blog/assets/ tree (a path
    # that would otherwise 404 in production with no build error).
    def image_resolver(src: str, alt: str):
        url = config.media_url(src)
        rel = src.strip().lstrip("./")
        if rel.startswith("assets/"):
            rel = rel[len("assets/"):]
        src_path = src_assets / rel
        if not src_path.is_file():
            raise content.ContentError(
                f"body image '{src}' not found under content/blog/assets/ "
                f"(expected file: assets/{rel}). Author images must live in content/blog/assets/."
            )
        size = image_size(src_path)
        # Fallback for unmeasurable formats (svg/webp/avif): match Cover's default and
        # seo._post_image's 1200x630 so intrinsic dims are consistent site-wide (BUG-008).
        w, h = size if size else (1200, 630)
        return url, w, h

    # 5b. Measure image covers (like body images) for accurate intrinsic dimensions;
    #     keep frontmatter/default dims if the format is unmeasurable (svg/webp/avif).
    for post in posts:
        if post.cover.kind == "image":
            rel = post.cover.src.strip().lstrip("./")
            if rel.startswith("assets/"):
                rel = rel[len("assets/"):]
            size = image_size(src_assets / rel)
            if size:
                post.cover.width, post.cover.height = size

    # 6. Render post pages
    for post in posts:
        page = render.render_article_page(post, cats, base_url, image_resolver)
        target = blog_out / post.slug / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")

    # 7. Render index
    (blog_out / "index.html").write_text(
        render.render_index_page(posts, cats, base_url), encoding="utf-8")

    # 8. Regenerate sitemap (deterministic: dates from frontmatter + configured portfolio date)
    (out / "sitemap.xml").write_text(
        sitemap.build_sitemap(posts, base_url, portfolio_lastmod=config.PORTFOLIO_LASTMOD),
        encoding="utf-8")

    # 8b. Generate the Atom syndication feed (machine-readable surface — Principle VIII)
    (blog_out / "feed.xml").write_text(
        feed.build_feed(posts, base_url, portfolio_lastmod=config.PORTFOLIO_LASTMOD),
        encoding="utf-8")

    # 8c. Generate llms.txt: committed identity base + derived post list (NOT copied verbatim —
    # it is a build artifact so a single-note commit updates the AI-facing index; Principle VIII).
    base_llms = (config.LLMS_SRC.read_text(encoding="utf-8")
                 if config.LLMS_SRC.exists() else f"# {config.AUTHOR_NAME}\n")
    (out / "llms.txt").write_text(llms.build_llms(base_llms, posts, base_url), encoding="utf-8")

    # 9. Report
    print(f"Built {len(posts)} post(s) into {out}")
    print(f"  categories: {', '.join(c.name for c in cats)}")
    print(f"  root files copied: {', '.join(copied)}")
    if missing:
        print(f"  WARNING: missing root companion files (skipped): {', '.join(missing)}")
    print(f"  blog index: {blog_out / 'index.html'}")
    print(f"  feed: {blog_out / 'feed.xml'}  ({len(posts)} entries)")
    print(f"  llms.txt: {out / 'llms.txt'}  (generated: identity base + {len(posts)} posts)")
    for p in posts:
        print(f"    - /blog/{p.slug}/  ({p.category}, {p.read_time}, related={len(p.related)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
