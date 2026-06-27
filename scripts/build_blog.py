#!/usr/bin/env python3
"""Build the deployable static site from Obsidian content + the extracted design.

Reads content/blog/*.md (+ categories.yml) and templates/blog/*, writes a complete
site to --out (default _site): portfolio + root companions copied verbatim, blog index
and one static page per post, regenerated sitemap, and .nojekyll.

Deterministic: same inputs -> byte-identical outputs (Constitution: GitHub Pages only).
"""
from __future__ import annotations
import argparse
import datetime as dt
import re
import shutil
import struct
import sys
from pathlib import Path

# Markers in the portfolio index.html delimiting the auto-synced "Field notes" section.
HOME_NOTES_START = "<!--LATEST-NOTES:START-->"
HOME_NOTES_END = "<!--LATEST-NOTES:END-->"

sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow `import blog.*`

from blog import config, content, render, sitemap  # noqa: E402


# --------------------------------------------------------------------------- #
# Minimal stdlib image-dimension reader (PNG/JPEG/GIF) -> (w, h) or None
# --------------------------------------------------------------------------- #
def image_size(path: Path):
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        w, h = struct.unpack(">II", data[16:24])
        return int(w), int(h)
    if data[:3] == b"\xff\xd8\xff":  # JPEG
        i = 2
        n = len(data)
        while i < n:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return int(w), int(h)
            seg = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + seg
        return None
    if data[:6] in (b"GIF87a", b"GIF89a"):
        w, h = struct.unpack("<HH", data[6:10])
        return int(w), int(h)
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
    if not (out / ".nojekyll").exists():
        (out / ".nojekyll").write_text("", encoding="utf-8")

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

    # image resolver for body images: public url + intrinsic dimensions (no CLS)
    def image_resolver(src: str, alt: str):
        url = config.media_url(src)
        rel = src.strip().lstrip("./")
        if rel.startswith("assets/"):
            rel = rel[len("assets/"):]
        size = image_size(src_assets / rel)
        w, h = size if size else (1200, 675)
        return url, w, h

    # 6. Render post pages
    for post in posts:
        page = render.render_article_page(post, cats, base_url, image_resolver)
        target = blog_out / post.slug / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")

    # 7. Render index
    (blog_out / "index.html").write_text(
        render.render_index_page(posts, cats, base_url), encoding="utf-8")

    # 8. Regenerate sitemap
    (out / "sitemap.xml").write_text(
        sitemap.build_sitemap(posts, base_url, today=dt.date.today()), encoding="utf-8")

    # 9. Report
    print(f"Built {len(posts)} post(s) into {out}")
    print(f"  categories: {', '.join(c.name for c in cats)}")
    print(f"  root files copied: {', '.join(copied)}")
    if missing:
        print(f"  WARNING: missing root companion files (skipped): {', '.join(missing)}")
    print(f"  blog index: {blog_out / 'index.html'}")
    for p in posts:
        print(f"    - /blog/{p.slug}/  ({p.category}, {p.read_time}, related={len(p.related)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
