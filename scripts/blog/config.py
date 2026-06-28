"""Site-wide configuration constants for the blog generator.

One consistent absolute site URL and one consistent author identity are used
everywhere (Constitution Principle V).
"""
from __future__ import annotations
import datetime
import pathlib

# Repo root = two levels up from this file (scripts/blog/config.py -> repo)
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CONTENT_DIR = REPO_ROOT / "content" / "blog"
TEMPLATES_DIR = REPO_ROOT / "templates" / "blog"
PARTIALS_DIR = TEMPLATES_DIR / "partials"
TEMPLATE_ASSETS_DIR = TEMPLATES_DIR / "assets"

# Canonical site identity (matches the deployed portfolio + SEO files).
DEFAULT_BASE_URL = "https://ehsankolivand.github.io/"
BLOG_PATH = "/blog/"                      # root-absolute
BLOG_MEDIA = "/blog/assets/media/"        # copied author images (covers + body)

AUTHOR_NAME = "Ehsan Kolivand"
AUTHOR_ROLE = "Senior Android Engineer"
SITE_BRAND = "Ehsan.kolivand"              # short brand/wordmark (post <title> suffix)
SITE_NAME = f"{SITE_BRAND} — Field Notes"  # full site name (index <title>, og:site_name)
BLOG_TAGLINE = (
    "Long-form notes on Jetpack Compose, clean architecture, and building agentic "
    "dev tooling that actually ships — from seven years in fintech, banking & crypto."
)
DEFAULT_OG_IMAGE = "/og-image.png"        # site default social image
THEME_COLOR = "#34E6A0"
LOCALE = "en"                              # BCP-47 language tag (JSON-LD inLanguage)
OG_LOCALE = "en_US"                        # Open Graph expects language_TERRITORY

WORDS_PER_MINUTE = 220                     # read-time basis

# Homepage's own last-modified date (the portfolio/SEO pass), used for the `/` sitemap
# entry so it is independent of blog content and never regresses below the portfolio's
# own date. Advanced automatically if a newer post appears in the homepage field-notes.
PORTFOLIO_LASTMOD = datetime.date(2026, 6, 27)

# Root companion files copied verbatim into the deployable site (Principle VII).
# index.html (the portfolio) is copied byte-for-byte and never modified.
ROOT_COPY_ALLOWLIST = [
    "index.html",
    "robots.txt",
    "site.webmanifest",
    "llms.txt",
    "favicon.ico",
    "favicon.svg",
    "apple-touch-icon.png",
    "icon-192.png",
    "icon-512.png",
    "og-image.png",
]
# Note: .nojekyll is NOT copied here — it is always written by the build (single source of
# truth) so it exists for GitHub Pages even if the repo root lacks it.

# Subset of the allowlist the deployed site MUST ship (Constitution V/VII: reuse the
# existing robots, manifest, favicon set, and social image). A missing one fails the
# build/verify rather than silently degrading SEO/branding. (.nojekyll is auto-written;
# index.html/llms.txt are tolerated-if-absent so the blog can build standalone.)
ROOT_REQUIRED = [
    "robots.txt",
    "site.webmanifest",
    "favicon.ico",
    "favicon.svg",
    "apple-touch-icon.png",
    "icon-192.png",
    "icon-512.png",
    "og-image.png",
]

# Tag palette (mirrors the design's _tagStyle). Categories may override via
# `palette: mint|sand` in categories.yml; default below preserves the design.
PALETTES = {
    "mint": {
        "color": "#34E6A0",
        "bg": "rgba(52,230,160,0.10)",
        "border": "rgba(52,230,160,0.28)",
        "dot": "#34E6A0",
    },
    "sand": {
        "color": "#E7D2A6",
        "bg": "rgba(231,210,166,0.10)",
        "border": "rgba(231,210,166,0.26)",
        "dot": "#E7D2A6",
    },
}
DEFAULT_MINT_CATEGORIES = {"Tooling", "Compose"}


def abs_url(base_url: str, path: str) -> str:
    """Join base URL + root-absolute path into one absolute URL (no double slash)."""
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def media_url(src: str) -> str:
    """Map a content-relative author image path to its public /blog/assets/media/ URL."""
    s = src.strip().lstrip("./")
    if s.startswith("assets/"):
        s = s[len("assets/"):]
    return BLOG_MEDIA + s
