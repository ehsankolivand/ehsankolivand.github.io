"""Regenerate sitemap.xml: homepage + blog index + every published post.

lastmod = updated || date (FR-019). Deterministic ordering.
"""
from __future__ import annotations
import datetime as dt
from . import config


def build_sitemap(posts, base_url: str, today: dt.date | None = None) -> str:
    home = config.abs_url(base_url, "/")
    blog = config.abs_url(base_url, config.BLOG_PATH)
    # homepage lastmod: newest content date if any, else today (passed in for determinism)
    newest = max((p.updated for p in posts), default=today)
    rows = []

    def url(loc: str, lastmod: dt.date | None):
        rows.append("  <url>")
        rows.append(f"    <loc>{loc}</loc>")
        if lastmod:
            rows.append(f"    <lastmod>{lastmod.isoformat()}</lastmod>")
        rows.append("  </url>")

    url(home, newest)
    url(blog, newest)
    for p in posts:                       # already sorted newest-first
        url(config.abs_url(base_url, p.url), p.updated)

    body = "\n".join(rows)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )
