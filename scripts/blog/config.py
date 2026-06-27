"""Site-wide configuration constants for the blog generator.

One consistent absolute site URL and one consistent author identity are used
everywhere (Constitution Principle V).
"""
from __future__ import annotations
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
BLOG_ASSETS = "/blog/assets/"
BLOG_MEDIA = "/blog/assets/media/"        # copied author images (covers + body)

AUTHOR_NAME = "Ehsan Kolivand"
AUTHOR_ROLE = "Senior Android Engineer"
AUTHOR_LOCATION = "Istanbul"
SITE_NAME = "Ehsan.log — Field Notes"
BLOG_TAGLINE = (
    "Long-form notes on Jetpack Compose, clean architecture, and building agentic "
    "dev tooling that actually ships — from seven years in fintech, banking & crypto."
)
DEFAULT_OG_IMAGE = "/og-image.png"        # site default social image
THEME_COLOR = "#34E6A0"
LOCALE = "en"
TWITTER_HANDLE = ""                        # none; omit twitter:site if empty

WORDS_PER_MINUTE = 220                     # read-time basis

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
    ".nojekyll",
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
