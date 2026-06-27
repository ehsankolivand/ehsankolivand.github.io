"""Load and validate blog content: posts (Obsidian notes) and the category set.

Fails loud on invalid input (Constitution / FR-026): missing required frontmatter,
unknown category, duplicate slug, bad dates.
"""
from __future__ import annotations
import re
import math
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import config


class ContentError(Exception):
    """Raised on invalid content; message identifies the offending file."""


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    s = _SLUG_RE.sub("-", text.strip().lower()).strip("-")
    return s or "post"


def parse_frontmatter(raw: str, source: str) -> tuple[dict, str]:
    """Split a note into (frontmatter dict, markdown body)."""
    if not raw.startswith("---"):
        raise ContentError(f"{source}: missing YAML frontmatter (file must start with '---').")
    parts = raw.split("\n")
    # find the closing '---'
    end = None
    for i in range(1, len(parts)):
        if parts[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ContentError(f"{source}: frontmatter not closed with '---'.")
    fm_text = "\n".join(parts[1:end])
    body = "\n".join(parts[end + 1:])
    try:
        meta = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        raise ContentError(f"{source}: invalid YAML frontmatter: {e}")
    if not isinstance(meta, dict):
        raise ContentError(f"{source}: frontmatter must be a YAML mapping.")
    return meta, body


def _parse_date(value, source: str, label: str) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value.strip())
        except ValueError:
            pass
    raise ContentError(f"{source}: '{label}' must be a date as YYYY-MM-DD (got {value!r}).")


def display_date(d: dt.date) -> str:
    """Format like the design: 'Jun 18, 2026'."""
    return f"{d.strftime('%b')} {d.day:02d}, {d.year}"


def compute_read_time(body: str) -> str:
    words = len(re.findall(r"\w+", body))
    minutes = max(1, math.ceil(words / config.WORDS_PER_MINUTE))
    return f"{minutes} min"


# --------------------------------------------------------------------------- #
# Categories
# --------------------------------------------------------------------------- #
@dataclass
class Category:
    name: str
    label: str
    palette: str  # 'mint' | 'sand'


def load_categories(path: Path) -> list[Category]:
    if not path.exists():
        raise ContentError(
            f"{path}: categories.yml is required (declares the canonical category set, "
            "ordering, and labels). Create it before building."
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ContentError(f"{path}: categories.yml must be a non-empty YAML list of mappings.")
    cats: list[Category] = []
    seen: set[str] = set()
    for entry in data:
        if isinstance(entry, str):
            entry = {"name": entry}
        if not isinstance(entry, dict) or "name" not in entry:
            raise ContentError(f"{path}: each category needs a 'name' (got {entry!r}).")
        name = str(entry["name"]).strip()
        if name in seen:
            raise ContentError(f"{path}: duplicate category name '{name}'.")
        seen.add(name)
        label = str(entry.get("label", name)).strip()
        palette = entry.get("palette")
        if palette not in (None, "mint", "sand"):
            raise ContentError(f"{path}: category '{name}' palette must be 'mint' or 'sand'.")
        if palette is None:
            palette = "mint" if name in config.DEFAULT_MINT_CATEGORIES else "sand"
        cats.append(Category(name=name, label=label, palette=palette))
    return cats


def tag_style(category: Category) -> dict:
    return config.PALETTES[category.palette]


# --------------------------------------------------------------------------- #
# Related-link extraction (end-of-post "More notes")
# --------------------------------------------------------------------------- #
_WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
_MDLINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_RELATED_HEADING = re.compile(r"^#{1,6}\s*(related|more notes|keep reading)\b", re.I)


def _link_to_slug(target: str) -> str:
    t = target.strip()
    t = t.split("#")[0]
    t = re.sub(r"^\.?/?", "", t)
    t = re.sub(r"^blog/", "", t)
    t = t.rstrip("/")
    t = re.sub(r"\.md$", "", t)
    t = t.rsplit("/", 1)[-1]   # final path segment
    return slugify(t) if t else ""


def extract_related(body: str) -> tuple[str, list[str]]:
    """Strip a trailing block of related links and return (body_without_block, slugs)."""
    lines = body.rstrip().split("\n")
    collected: list[str] = []
    cut = len(lines)
    i = len(lines) - 1
    while i >= 0:
        line = lines[i].strip()
        if line == "":
            i -= 1
            continue
        if line in ("---", "***", "___"):
            cut = i
            i -= 1
            continue
        if _RELATED_HEADING.match(line):
            cut = i
            i -= 1
            continue
        # a link-bearing line (list item or bare): only treat as related if it is
        # essentially just link(s).
        bullet = re.sub(r"^[-*+]\s+", "", line)
        bullet = re.sub(r"^\d+\.\s+", "", bullet)
        targets = _WIKILINK.findall(bullet) + _MDLINK.findall(bullet)
        stripped = _WIKILINK.sub("", bullet)
        stripped = _MDLINK.sub("", stripped).strip()
        if targets and stripped == "":
            collected.extend(targets)
            cut = i
            i -= 1
            continue
        break  # first non-related line from the bottom
    collected.reverse()
    slugs = [s for s in (_link_to_slug(t) for t in collected) if s]
    new_body = "\n".join(lines[:cut]).rstrip() + "\n"
    return new_body, slugs


# --------------------------------------------------------------------------- #
# Posts
# --------------------------------------------------------------------------- #
@dataclass
class Cover:
    kind: str = "code"          # 'code' | 'image'
    glyph: str = "{ }"
    caption: str = ""
    src: str = ""               # content-relative path for image covers
    alt: str = ""
    width: int = 1200
    height: int = 630


@dataclass
class Post:
    source: Path
    title: str
    date: dt.date
    updated: dt.date
    category: str
    tags: list[str]
    excerpt: str
    slug: str
    cover: Cover
    read_time: str
    canonical: str
    og_description: str
    image: str                  # content-relative path or "" (for social/JSON-LD)
    draft: bool
    body: str                   # markdown body with related block stripped
    related_slugs: list[str] = field(default_factory=list)
    related: list["Post"] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"{config.BLOG_PATH}{self.slug}/"

    def display_date(self) -> str:
        return display_date(self.date)


def _parse_cover(meta_cover, source: str) -> Cover:
    if meta_cover is None:
        return Cover(kind="code", glyph="{ }", caption="")
    if isinstance(meta_cover, str):
        s = meta_cover.strip()
        # a path-like string -> image cover; otherwise a code glyph
        if "/" in s or re.search(r"\.(png|jpe?g|webp|gif|svg|avif)$", s, re.I):
            return Cover(kind="image", src=s, alt="")
        return Cover(kind="code", glyph=s, caption="")
    if isinstance(meta_cover, dict):
        kind = str(meta_cover.get("type", "code")).strip()
        if kind == "image":
            src = str(meta_cover.get("src", "")).strip()
            if not src:
                raise ContentError(f"{source}: image cover requires 'src'.")
            alt = str(meta_cover.get("alt", "")).strip()
            if not alt:
                raise ContentError(f"{source}: image cover requires 'alt' (accessibility/SEO).")
            return Cover(
                kind="image", src=src, alt=alt,
                width=int(meta_cover.get("width", 1200)),
                height=int(meta_cover.get("height", 630)),
            )
        return Cover(
            kind="code",
            glyph=str(meta_cover.get("glyph", "{ }")),
            caption=str(meta_cover.get("caption", "")),
        )
    raise ContentError(f"{source}: invalid 'cover' value.")


def load_post(path: Path, categories: list[Category], base_url: str) -> Post:
    source = path.name
    meta, raw_body = parse_frontmatter(path.read_text(encoding="utf-8"), source)

    def req(key, *alts):
        for k in (key, *alts):
            if meta.get(k) not in (None, ""):
                return meta[k]
        raise ContentError(f"{source}: required frontmatter '{key}' is missing.")

    title = str(req("title")).strip()
    date = _parse_date(req("date"), source, "date")
    updated_raw = meta.get("updated")
    updated = _parse_date(updated_raw, source, "updated") if updated_raw else date
    if updated < date:
        raise ContentError(f"{source}: 'updated' ({updated}) is before 'date' ({date}).")

    category = str(req("category")).strip()
    cat_names = {c.name for c in categories}
    if category not in cat_names:
        raise ContentError(
            f"{source}: category '{category}' is not declared in categories.yml "
            f"(known: {', '.join(sorted(cat_names))})."
        )

    excerpt = str(req("excerpt", "description")).strip()
    tags = meta.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    tags = [str(t).strip() for t in tags]

    slug = str(meta.get("slug") or slugify(title)).strip()
    if slug != slugify(slug):
        slug = slugify(slug)

    cover = _parse_cover(meta.get("cover"), source)
    if not cover.caption and cover.kind == "code":
        cover.caption = f"// {category.lower()} · {slug}"

    read_time = str(meta.get("readTime") or compute_read_time(raw_body)).strip()
    draft = bool(meta.get("draft", False))

    canonical = str(meta.get("canonical") or config.abs_url(base_url, f"{config.BLOG_PATH}{slug}/")).strip()
    og_description = str(meta.get("ogDescription") or meta.get("socialDescription") or excerpt).strip()

    image = str(meta.get("image") or (cover.src if cover.kind == "image" else "")).strip()

    body, related_slugs = extract_related(raw_body)

    return Post(
        source=path, title=title, date=date, updated=updated, category=category,
        tags=tags, excerpt=excerpt, slug=slug, cover=cover, read_time=read_time,
        canonical=canonical, og_description=og_description, image=image, draft=draft,
        body=body, related_slugs=related_slugs,
    )


def load_posts(content_dir: Path, categories: list[Category], base_url: str,
               include_drafts: bool = False) -> list[Post]:
    posts: list[Post] = []
    for path in sorted(content_dir.glob("*.md")):
        if path.name.lower() in ("readme.md",):
            continue
        post = load_post(path, categories, base_url)
        if post.draft and not include_drafts:
            continue
        posts.append(post)

    # unique slugs
    by_slug: dict[str, Post] = {}
    for p in posts:
        if p.slug in by_slug:
            raise ContentError(
                f"Duplicate slug '{p.slug}' in {p.source.name} and {by_slug[p.slug].source.name}."
            )
        by_slug[p.slug] = p

    # newest first (stable: by date desc, then slug for determinism)
    posts.sort(key=lambda p: (p.date, p.slug), reverse=True)

    # resolve related links
    title_index = {slugify(p.title): p for p in posts}
    for p in posts:
        resolved: list[Post] = []
        for s in p.related_slugs:
            target = by_slug.get(s) or title_index.get(s)
            if target and target is not p:
                resolved.append(target)
            else:
                print(f"WARNING: {p.source.name}: related link '{s}' did not resolve to a post.")
        # de-dup while preserving order
        seen = set()
        p.related = [t for t in resolved if not (t.slug in seen or seen.add(t.slug))]
    return posts
