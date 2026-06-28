"""Per-page SEO/GEO head construction: meta, canonical, Open Graph, Twitter, JSON-LD.

Every post page carries complete, consistent metadata fed from frontmatter
(Constitution Principle V). Reuses the existing favicons/manifest and one absolute URL.
"""
from __future__ import annotations
import json
import html

from . import config


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def _favicons_and_manifest() -> list[str]:
    return [
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        '<link rel="icon" href="/favicon.ico" sizes="any">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="manifest" href="/site.webmanifest">',
        f'<meta name="theme-color" content="{config.THEME_COLOR}">',
    ]


def _common(lines: list[str]) -> list[str]:
    # preload the display fonts (latin Space Grotesk 700 for the hero + Manrope 400 for body)
    # so the woff2 isn't discovered only after CSS parse (reduces FOUT / LCP delay).
    lines.append('<link rel="preload" href="/blog/assets/fonts/cd62414e-f827-4a9e-9096-c4e987c5e31d.woff2"'
                 ' as="font" type="font/woff2" crossorigin>')
    lines.append('<link rel="preload" href="/blog/assets/fonts/e088d297-3e2c-443b-99f1-1773b8dcf254.woff2"'
                 ' as="font" type="font/woff2" crossorigin>')
    # stylesheet + reduced-motion-safe no-JS reveal fallback (keeps content visible
    # without JavaScript; reveal animation is JS progressive enhancement only).
    lines.append('<link rel="stylesheet" href="/blog/assets/blog.css">')
    lines.append('<noscript><style>[data-reveal]{opacity:1!important;transform:none!important;'
                 'filter:none!important;}</style></noscript>')
    return lines


def _jsonld(obj) -> str:
    payload = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return f'<script type="application/ld+json">{payload}</script>'


def head_for_post(post, base_url: str, category_label: str) -> str:
    title = f"{post.title} — {config.SITE_BRAND}"
    desc = post.excerpt
    canonical = post.canonical
    if post.image:
        image_abs = config.abs_url(base_url, config.media_url(post.image))
    else:
        image_abs = config.abs_url(base_url, config.DEFAULT_OG_IMAGE)
    keywords = ", ".join(post.tags)

    L: list[str] = []
    L.append(f"<title>{_esc(title)}</title>")
    L.append(f'<meta name="description" content="{_esc(desc)}">')
    L.append(f'<meta name="author" content="{_esc(config.AUTHOR_NAME)}">')
    if keywords:
        L.append(f'<meta name="keywords" content="{_esc(keywords)}">')
    L.append('<meta name="robots" content="index, follow, max-image-preview:large">')
    L.append(f'<link rel="canonical" href="{_esc(canonical)}">')
    # Open Graph
    L.append('<meta property="og:type" content="article">')
    L.append(f'<meta property="og:title" content="{_esc(post.title)}">')
    L.append(f'<meta property="og:description" content="{_esc(post.og_description)}">')
    L.append(f'<meta property="og:url" content="{_esc(canonical)}">')
    L.append(f'<meta property="og:image" content="{_esc(image_abs)}">')
    L.append(f'<meta property="og:site_name" content="{_esc(config.SITE_NAME)}">')
    L.append(f'<meta property="og:locale" content="{config.OG_LOCALE}">')
    L.append(f'<meta property="article:published_time" content="{post.date.isoformat()}">')
    L.append(f'<meta property="article:modified_time" content="{post.updated.isoformat()}">')
    L.append(f'<meta property="article:section" content="{_esc(category_label)}">')
    for tag in post.tags:
        L.append(f'<meta property="article:tag" content="{_esc(tag)}">')
    # Twitter
    L.append('<meta name="twitter:card" content="summary_large_image">')
    L.append(f'<meta name="twitter:title" content="{_esc(post.title)}">')
    L.append(f'<meta name="twitter:description" content="{_esc(post.og_description)}">')
    L.append(f'<meta name="twitter:image" content="{_esc(image_abs)}">')
    L += _favicons_and_manifest()
    _common(L)
    # JSON-LD BlogPosting
    L.append(_jsonld({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.excerpt,
        "image": image_abs,
        "datePublished": post.date.isoformat(),
        "dateModified": post.updated.isoformat(),
        "author": {"@type": "Person", "name": config.AUTHOR_NAME,
                   "jobTitle": config.AUTHOR_ROLE, "url": config.abs_url(base_url, "/")},
        "publisher": {"@type": "Person", "name": config.AUTHOR_NAME},
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "articleSection": category_label,
        "keywords": keywords,
        "inLanguage": config.LOCALE,
    }))
    return "\n".join(L)


def head_for_index(posts, base_url: str) -> str:
    title = config.SITE_NAME
    desc = config.BLOG_TAGLINE
    canonical = config.abs_url(base_url, config.BLOG_PATH)
    image_abs = config.abs_url(base_url, config.DEFAULT_OG_IMAGE)

    L: list[str] = []
    L.append(f"<title>{_esc(title)}</title>")
    L.append(f'<meta name="description" content="{_esc(desc)}">')
    L.append(f'<meta name="author" content="{_esc(config.AUTHOR_NAME)}">')
    L.append('<meta name="robots" content="index, follow, max-image-preview:large">')
    L.append(f'<link rel="canonical" href="{_esc(canonical)}">')
    L.append('<meta property="og:type" content="website">')
    L.append(f'<meta property="og:title" content="{_esc(title)}">')
    L.append(f'<meta property="og:description" content="{_esc(desc)}">')
    L.append(f'<meta property="og:url" content="{_esc(canonical)}">')
    L.append(f'<meta property="og:image" content="{_esc(image_abs)}">')
    L.append(f'<meta property="og:site_name" content="{_esc(config.SITE_NAME)}">')
    L.append(f'<meta property="og:locale" content="{config.OG_LOCALE}">')
    L.append('<meta name="twitter:card" content="summary_large_image">')
    L.append(f'<meta name="twitter:title" content="{_esc(title)}">')
    L.append(f'<meta name="twitter:description" content="{_esc(desc)}">')
    L.append(f'<meta name="twitter:image" content="{_esc(image_abs)}">')
    L += _favicons_and_manifest()
    _common(L)
    blog_posts = [{
        "@type": "BlogPosting",
        "headline": p.title,
        "url": p.canonical,  # honor per-post canonical override (consistent with og:url)
        "datePublished": p.date.isoformat(),
        "author": {"@type": "Person", "name": config.AUTHOR_NAME},
    } for p in posts]
    L.append(_jsonld({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Blog",
                "@id": canonical,
                "name": config.SITE_NAME,
                "url": canonical,
                "description": desc,
                "inLanguage": config.LOCALE,
                "author": {"@type": "Person", "name": config.AUTHOR_NAME,
                           "jobTitle": config.AUTHOR_ROLE},
                "blogPost": blog_posts,
            },
            {
                "@type": "WebSite",
                "name": config.SITE_NAME,
                "url": config.abs_url(base_url, "/"),
            },
        ],
    }))
    return "\n".join(L)
