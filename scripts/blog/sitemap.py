"""Regenerate sitemap.xml: homepage + blog index + every published post.

lastmod = updated || date (FR-019). Fully deterministic: dates come only from frontmatter
and the portfolio's own configured date — never from today().
"""
from __future__ import annotations
import datetime as dt
from . import config


def build_sitemap(posts, base_url: str, portfolio_lastmod: dt.date | None = None) -> str:
    home = config.abs_url(base_url, "/")
    blog = config.abs_url(base_url, config.BLOG_PATH)
    newest = max((p.updated for p in posts), default=None)   # None when there are no posts
    # homepage: its own date (the portfolio/SEO pass), advanced if a newer post now shows
    # in the field-notes section, but never regressed below it. /blog/ tracks the newest post.
    home_lastmod = portfolio_lastmod
    if newest and (home_lastmod is None or newest > home_lastmod):
        home_lastmod = newest
    rows = []

    def url(loc: str, lastmod: dt.date | None):
        rows.append("  <url>")
        rows.append(f"    <loc>{loc}</loc>")
        if lastmod:
            rows.append(f"    <lastmod>{lastmod.isoformat()}</lastmod>")
        rows.append("  </url>")

    url(home, home_lastmod)
    # /blog/ index is always rendered (even with zero posts, via _EMPTY_GRID), so it is always
    # listed; only its <lastmod> is conditional — `newest` is None when empty, which drops it.
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
