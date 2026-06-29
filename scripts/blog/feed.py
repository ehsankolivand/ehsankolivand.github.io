"""Generate a deterministic Atom 1.0 feed listing every published post.

A standards-compliant syndication / GEO surface (Constitution Principle VIII). Stdlib-only
and fully deterministic: every timestamp is a post date at UTC midnight and the feed-level
<updated> is max(post.updated) (or the portfolio date when empty) — never today() (RFC 4287).
"""
from __future__ import annotations
import datetime as dt
import html

from . import config


def _ts(d: dt.date) -> str:
    """RFC 3339 timestamp at UTC midnight (deterministic; dates come only from frontmatter)."""
    return d.isoformat() + "T00:00:00Z"


def _esc(s) -> str:
    return html.escape(str(s), quote=True)


def build_feed(posts, base_url: str, portfolio_lastmod: dt.date | None = None) -> str:
    blog_url = config.abs_url(base_url, config.BLOG_PATH)
    feed_url = config.abs_url(base_url, config.BLOG_FEED_PATH)
    home = config.abs_url(base_url, "/")
    newest = max((p.updated for p in posts), default=None)  # None when empty
    updated = newest or portfolio_lastmod or dt.date(1970, 1, 1)

    rows = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f"  <title>{_esc(config.SITE_NAME)}</title>",
        f"  <subtitle>{_esc(config.BLOG_TAGLINE)}</subtitle>",
        f"  <id>{_esc(blog_url)}</id>",
        f'  <link rel="alternate" type="text/html" href="{_esc(blog_url)}"/>',
        f'  <link rel="self" type="application/atom+xml" href="{_esc(feed_url)}"/>',
        f"  <updated>{_ts(updated)}</updated>",
        f"  <author><name>{_esc(config.AUTHOR_NAME)}</name><uri>{_esc(home)}</uri></author>",
    ]
    for p in posts:  # already newest-first
        url = config.abs_url(base_url, p.url)
        rows.append("  <entry>")
        rows.append(f"    <title>{_esc(p.title)}</title>")
        rows.append(f"    <id>{_esc(url)}</id>")
        rows.append(f'    <link rel="alternate" type="text/html" href="{_esc(url)}"/>')
        rows.append(f"    <published>{_ts(p.date)}</published>")
        rows.append(f"    <updated>{_ts(p.updated)}</updated>")
        rows.append(f"    <summary>{_esc(p.excerpt)}</summary>")
        for tag in p.tags:
            rows.append(f'    <category term="{_esc(tag)}"/>')
        rows.append(f"    <author><name>{_esc(config.AUTHOR_NAME)}</name></author>")
        rows.append("  </entry>")
    rows.append("</feed>")
    return "\n".join(rows) + "\n"
