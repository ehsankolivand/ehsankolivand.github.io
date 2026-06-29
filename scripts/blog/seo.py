"""Per-page SEO/GEO head construction: meta, canonical, Open Graph, Twitter, JSON-LD.

Every post page carries complete, consistent metadata fed from frontmatter
(Constitution Principle V). Identity is unified with the portfolio via stable @id
anchors (#person / #website) so engines merge the portfolio and blog into one entity
(Constitution Principle VIII). Reuses the existing favicons/manifest and one absolute URL.
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
    # Atom feed autodiscovery (Constitution VIII — machine-readable syndication surface).
    lines.append(f'<link rel="alternate" type="application/atom+xml" '
                 f'title="{_esc(config.SITE_NAME)}" href="{config.BLOG_FEED_PATH}">')
    # stylesheet + reduced-motion-safe no-JS reveal fallback (keeps content visible
    # without JavaScript; reveal animation is JS progressive enhancement only).
    lines.append('<link rel="stylesheet" href="/blog/assets/blog.css">')
    lines.append('<noscript><style>[data-reveal]{opacity:1!important;transform:none!important;'
                 'filter:none!important;}</style></noscript>')
    return lines


def _jsonld(obj) -> str:
    payload = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return f'<script type="application/ld+json">{payload}</script>'


def _author_node(base_url: str, full: bool) -> dict:
    """The canonical author Person. `full` adds url/jobTitle/sameAs; otherwise a lean
    @id+name reference. The @id MUST equal the portfolio's #person so engines merge them."""
    node = {"@type": "Person", "@id": config.PERSON_ID, "name": config.AUTHOR_NAME}
    if full:
        node["url"] = config.abs_url(base_url, "/")
        node["jobTitle"] = config.AUTHOR_ROLE
        node["sameAs"] = list(config.AUTHOR_SAMEAS)
    return node


def _post_image(post, base_url: str):
    """Return (absolute image url, width, height, alt) for OG/Twitter/JSON-LD.

    Image covers use measured intrinsic dimensions + the cover alt; an explicit `image:`
    frontmatter (no image cover) uses the standard 1200x630 OG size; otherwise the site
    default social image with a site-identity alt."""
    if post.cover.kind == "image":
        src = post.image or post.cover.src
        return (config.abs_url(base_url, config.media_url(src)),
                post.cover.width, post.cover.height, post.cover.alt or post.title)
    if post.image:
        return (config.abs_url(base_url, config.media_url(post.image)), 1200, 630, post.title)
    return (config.abs_url(base_url, config.DEFAULT_OG_IMAGE), 1200, 630, config.SITE_NAME)


def _breadcrumb(trail: list[tuple[str, str]]) -> dict:
    """trail = [(name, absolute_url), ...] -> a schema.org BreadcrumbList node (no @context;
    callers add it when the node is emitted standalone rather than inside an @graph)."""
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(trail)
        ],
    }


def head_for_post(post, base_url: str, category_label: str) -> str:
    title = f"{post.title} — {config.SITE_BRAND}"
    desc = post.excerpt
    canonical = post.canonical
    image_abs, img_w, img_h, img_alt = _post_image(post, base_url)
    keywords = ", ".join(post.tags)
    home = config.abs_url(base_url, "/")
    blog = config.abs_url(base_url, config.BLOG_PATH)

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
    L.append(f'<meta property="og:image:width" content="{img_w}">')
    L.append(f'<meta property="og:image:height" content="{img_h}">')
    L.append(f'<meta property="og:image:alt" content="{_esc(img_alt)}">')
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
    L.append(f'<meta name="twitter:image:alt" content="{_esc(img_alt)}">')
    L += _favicons_and_manifest()
    _common(L)
    # JSON-LD: BlogPosting (first, so the verifier's first-script check still validates it)
    blogposting = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.excerpt,
        "url": canonical,
        "image": image_abs,
        "datePublished": post.date.isoformat(),
        "dateModified": post.updated.isoformat(),
        "author": _author_node(base_url, full=True),
        "publisher": _author_node(base_url, full=False),
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "isPartOf": {"@type": "Blog", "@id": blog},
        "articleSection": category_label,
        "wordCount": post.word_count,
        "inLanguage": config.LOCALE,
    }
    if keywords:
        blogposting["keywords"] = keywords
    if post.read_minutes:
        blogposting["timeRequired"] = f"PT{post.read_minutes}M"
    L.append(_jsonld(blogposting))
    # JSON-LD: BreadcrumbList (Home -> Field Notes -> post), emitted standalone (+@context)
    breadcrumb = {"@context": "https://schema.org",
                  **_breadcrumb([("Home", home), ("Field Notes", blog), (post.title, canonical)])}
    L.append(_jsonld(breadcrumb))
    return "\n".join(L)


def head_for_index(posts, base_url: str) -> str:
    title = config.SITE_NAME
    desc = config.BLOG_TAGLINE
    canonical = config.abs_url(base_url, config.BLOG_PATH)
    home = config.abs_url(base_url, "/")
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
    L.append('<meta property="og:image:width" content="1200">')
    L.append('<meta property="og:image:height" content="630">')
    L.append(f'<meta property="og:image:alt" content="{_esc(config.SITE_NAME)}">')
    L.append(f'<meta property="og:site_name" content="{_esc(config.SITE_NAME)}">')
    L.append(f'<meta property="og:locale" content="{config.OG_LOCALE}">')
    L.append('<meta name="twitter:card" content="summary_large_image">')
    L.append(f'<meta name="twitter:title" content="{_esc(title)}">')
    L.append(f'<meta name="twitter:description" content="{_esc(desc)}">')
    L.append(f'<meta name="twitter:image" content="{_esc(image_abs)}">')
    L.append(f'<meta name="twitter:image:alt" content="{_esc(config.SITE_NAME)}">')
    L += _favicons_and_manifest()
    _common(L)
    blog_posts = [{
        "@type": "BlogPosting",
        "headline": p.title,
        "url": p.canonical,  # honor per-post canonical override (consistent with og:url)
        "datePublished": p.date.isoformat(),
        "author": {"@id": config.PERSON_ID},
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
                "author": _author_node(base_url, full=True),
                "isPartOf": {"@type": "WebSite", "@id": config.WEBSITE_ID},
                "blogPost": blog_posts,
            },
            {
                "@type": "WebSite",
                "@id": config.WEBSITE_ID,
                "name": config.SITE_NAME,
                "url": config.abs_url(base_url, "/"),
                "publisher": {"@id": config.PERSON_ID},
            },
            _breadcrumb([("Home", home), ("Field Notes", canonical)]),
        ],
    }))
    return "\n".join(L)
