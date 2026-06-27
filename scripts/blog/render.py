"""Render content into the extracted design templates/partials.

The bundle's runtime placeholders are filled here; all design markup/styles come from
templates/blog/* unchanged (Constitution Principle III). Cards, nav, and post links are
real <a> anchors present in the static HTML (Principle I).
"""
from __future__ import annotations
from functools import lru_cache

from . import config
from . import seo
from .content import tag_style, Post, Category
from .markdown_render import render as render_markdown, esc, esc_attr


@lru_cache(maxsize=None)
def _tpl(name: str) -> str:
    return (config.TEMPLATES_DIR / name).read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def _partial(name: str) -> str:
    return (config.PARTIALS_DIR / name).read_text(encoding="utf-8").rstrip("\n")


def _fill(text: str, **tokens) -> str:
    for k, v in tokens.items():
        text = text.replace("{{" + k + "}}", v)
    return text


# --------------------------------------------------------------------------- #
# Shell / navigation
# --------------------------------------------------------------------------- #
def render_nav(categories: list[Category], active: str = "All") -> str:
    items = []
    # "All" first, then declared categories in order
    entries = [("All", "All", config.BLOG_PATH)]
    for c in categories:
        entries.append((c.name, c.label, f"{config.BLOG_PATH}#cat={c.name}"))
    for name, label, href in entries:
        on = (name == active)
        color = "#34E6A0" if on else "#9FB0AA"
        bg = "rgba(52,230,160,0.08)" if on else "transparent"
        items.append(_fill(_partial("nav-item.html"),
                           HREF=esc_attr(href), CAT=esc_attr(name),
                           COLOR=color, BG=bg, LABEL=esc(label)))
    return "\n      ".join(items)


def assemble(head: str, main: str, categories: list[Category], active: str = "All") -> str:
    page = _tpl("base.html")
    page = page.replace("{{HEAD}}", head)
    page = page.replace("{{NAV_ITEMS}}", render_nav(categories, active))
    page = page.replace("{{MAIN}}", main)
    return page


# --------------------------------------------------------------------------- #
# Covers / cards
# --------------------------------------------------------------------------- #
def render_cover(post: Post, context: str) -> str:
    """context: 'article' or 'featured'."""
    if post.cover.kind == "image":
        name = "cover-image.html" if context == "article" else "cover-featured-image.html"
        return _fill(_partial(name),
                     SRC=esc_attr(config.media_url(post.cover.src)),
                     ALT=esc_attr(post.cover.alt),
                     WIDTH=str(post.cover.width), HEIGHT=str(post.cover.height))
    name = "cover-code.html" if context == "article" else "cover-featured-code.html"
    return _fill(_partial(name), GLYPH=esc(post.cover.glyph), CAPTION=esc(post.cover.caption))


def _card_tokens(post: Post, cats_by_name: dict[str, Category]) -> dict:
    cat = cats_by_name[post.category]
    style = tag_style(cat)
    return dict(
        URL=esc_attr(post.url), CAT=esc_attr(post.category),
        TAG_BG=style["bg"], TAG_BORDER=style["border"], TAG_COLOR=style["color"], DOT=style["dot"],
        TAG_LABEL=esc(cat.label), TITLE=esc(post.title), DEK=esc(post.excerpt),
        DATE=esc(post.display_date()), READ_TIME=esc(post.read_time),
    )


def render_featured(post: Post, cats_by_name: dict[str, Category]) -> str:
    tpl = _partial("featured-card.html")
    tpl = tpl.replace("{{COVER}}", render_cover(post, "featured"))
    return _fill(tpl, **_card_tokens(post, cats_by_name))


def render_grid_card(post: Post, cats_by_name: dict[str, Category]) -> str:
    return _fill(_partial("grid-card.html"), **_card_tokens(post, cats_by_name))


def render_more_note(post: Post, cats_by_name: dict[str, Category]) -> str:
    cat = cats_by_name[post.category]
    return _fill(_partial("more-note.html"),
                 URL=esc_attr(post.url), TITLE=esc(post.title),
                 TAG_LABEL=esc(cat.label), READ_TIME=esc(post.read_time))


def render_more_notes_section(related: list[Post], cats_by_name: dict[str, Category]) -> str:
    if not related:
        return ""  # gracefully omit (FR-015)
    cards = "\n          ".join(render_more_note(p, cats_by_name) for p in related)
    return _fill(_partial("more-notes-section.html"), MORE_NOTES=cards)


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #
_EMPTY_GRID = (
    '<p style="grid-column:1/-1; font-family:\'JetBrains Mono\',monospace; color:#66756F; '
    'font-size:14px;">// no notes published yet — check back soon.</p>'
)


def render_home_notes(posts: list[Post], categories: list[Category], limit: int = 3) -> str:
    """Render the portfolio homepage 'Field notes' section: the latest N posts as
    blog-style cards (each linking to its post) + a 'Read all notes' link to /blog/.
    Returns the <section> HTML to inject between the homepage markers."""
    cats_by_name = {c.name: c for c in categories}
    top = posts[:limit]
    cards = "\n        ".join(
        render_grid_card(p, cats_by_name).replace(
            '<a data-card="" data-ripple=""', '<a data-card="" data-homenote="" data-ripple=""', 1)
        for p in top
    )
    return _fill(_partial("home-notes-section.html"), CARDS=cards)


def render_index_page(posts: list[Post], categories: list[Category], base_url: str) -> str:
    cats_by_name = {c.name: c for c in categories}
    main = _tpl("index.html")
    if posts:
        featured_html = render_featured(posts[0], cats_by_name)
        grid_posts = posts[1:]
        grid_html = "\n        ".join(render_grid_card(p, cats_by_name) for p in grid_posts) or _EMPTY_GRID
    else:
        featured_html = ""
        grid_html = _EMPTY_GRID
    main = main.replace("{{FEATURED}}", featured_html).replace("{{GRID}}", grid_html)
    head = seo.head_for_index(posts, base_url)
    return assemble(head, main, categories, active="All")


def render_article_page(post: Post, categories: list[Category], base_url: str, image_resolver) -> str:
    cats_by_name = {c.name: c for c in categories}
    cat = cats_by_name[post.category]
    style = tag_style(cat)
    body_html = render_markdown(post.body, image_resolver)
    main = _tpl("article.html")
    main = _fill(
        main,
        TAG_BG=style["bg"], TAG_BORDER=style["border"], TAG_COLOR=style["color"],
        TAG_LABEL=esc(cat.label), DATE=esc(post.display_date()), READ_TIME=esc(post.read_time),
        TITLE=esc(post.title), DEK=esc(post.excerpt),
        COVER=render_cover(post, "article"),
        BODY=body_html,
        MORE_NOTES_SECTION=render_more_notes_section(post.related, cats_by_name),
    )
    head = seo.head_for_post(post, base_url, cat.label)
    return assemble(head, main, categories, active=post.category)
