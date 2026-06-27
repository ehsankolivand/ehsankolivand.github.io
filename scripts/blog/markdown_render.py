"""In-house, stdlib-only Markdown renderer keyed to the design's block vocabulary.

Maps Markdown to the exact design block partials (paragraph, h2, code+caption, quote,
list, image). No syntax highlighting, no client JS (Clarification / FR-013). All text
and attributes are HTML-escaped.
"""
from __future__ import annotations
import re
import html
from pathlib import Path
from functools import lru_cache

from . import config

LINK_STYLE = "color:#34E6A0; text-decoration:none; border-bottom:1px solid rgba(52,230,160,0.4);"
INLINE_CODE_STYLE = ("font-family:'JetBrains Mono',monospace; font-size:0.92em; "
                     "background:rgba(52,230,160,0.10); color:#9FE9C8; padding:1px 6px; border-radius:6px;")


@lru_cache(maxsize=None)
def _partial(name: str) -> str:
    return (config.PARTIALS_DIR / name).read_text(encoding="utf-8").rstrip("\n")


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def esc_attr(text: str) -> str:
    return html.escape(text, quote=True)


# --------------------------------------------------------------------------- #
# Inline rendering
# --------------------------------------------------------------------------- #
def _anchor(url: str, label_html: str) -> str:
    external = url.startswith("http://") or url.startswith("https://")
    rel = ' target="_blank" rel="noopener"' if external else ""
    return f'<a href="{esc_attr(url)}"{rel} style="{LINK_STYLE}">{label_html}</a>'


def render_inline(text: str) -> str:
    """Render Markdown inline syntax (code, links, bold, italic) with escaping."""
    stash: dict[str, str] = {}

    def keep(html_fragment: str) -> str:
        key = f"\x00{len(stash)}\x00"
        stash[key] = html_fragment
        return key

    # inline code first (verbatim, escaped) so its contents aren't further processed
    text = re.sub(r"`([^`]+)`", lambda m: keep(f'<code style="{INLINE_CODE_STYLE}">{esc(m.group(1))}</code>'), text)
    # links [label](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)",
                  lambda m: keep(_anchor(m.group(2), esc(m.group(1)))), text)
    # escape the remaining literal text
    text = esc(text)
    # bold then italic
    text = re.sub(r"\*\*([^*]+)\*\*", r'<strong style="color:#EDF2EF; font-weight:700;">\1</strong>', text)
    text = re.sub(r"__([^_]+)__", r'<strong style="color:#EDF2EF; font-weight:700;">\1</strong>', text)
    text = re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_([^_\s][^_]*?)_(?!\w)", r"<em>\1</em>", text)
    # restore protected fragments
    for key, frag in stash.items():
        text = text.replace(key, frag)
    return text


# --------------------------------------------------------------------------- #
# Block rendering
# --------------------------------------------------------------------------- #
def _fill(partial_name: str, **tokens) -> str:
    out = _partial(partial_name)
    for k, v in tokens.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def _code_block(code: str, caption: str) -> str:
    return _fill("block-code.html", CAPTION=esc(caption), CONTENT=esc(code))


def _image(alt: str, src: str, image_resolver) -> str:
    if not src.strip():
        # design's placeholder caption box
        return _fill("block-img-placeholder.html", CAPTION=esc(alt))
    url, width, height = image_resolver(src.strip(), alt)
    caption_html = ""
    if alt.strip():
        caption_html = _fill("block-img-caption.html", CAPTION=esc(alt))
    return _fill("block-img.html", SRC=esc_attr(url), ALT=esc_attr(alt),
                 WIDTH=str(width), HEIGHT=str(height), CAPTION=caption_html)


_BLOCK_STARTERS = (
    re.compile(r"^(```|~~~)"),
    re.compile(r"^#{1,6}\s+"),
    re.compile(r"^>"),
    re.compile(r"^([-*+]\s+|\d+\.\s+)"),
    re.compile(r"^([-*_])\1\1+$"),
    re.compile(r"^!\[[^\]]*\]\([^)]*\)\s*$"),
)


def _is_block_start(s: str) -> bool:
    return any(p.match(s) for p in _BLOCK_STARTERS)


def render(markdown_text: str, image_resolver) -> str:
    """Render a Markdown body to a string of concatenated design block partials."""
    lines = markdown_text.split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        if s == "":
            i += 1
            continue
        # fenced code: caption = info string
        mfence = re.match(r"^(```|~~~)(.*)$", s)
        if mfence:
            fence = mfence.group(1)
            caption = mfence.group(2).strip()
            i += 1
            buf: list[str] = []
            while i < n and not lines[i].strip().startswith(fence):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            out.append(_code_block("\n".join(buf), caption))
            continue
        # heading -> design h2
        mh = re.match(r"^#{1,6}\s+(.*)$", s)
        if mh:
            out.append(_fill("block-h2.html", CONTENT=render_inline(mh.group(1).strip())))
            i += 1
            continue
        # thematic break -> skip
        if re.match(r"^([-*_])\1\1+$", s):
            i += 1
            continue
        # blockquote
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            text = " ".join(x.strip() for x in buf).strip()
            out.append(_fill("block-quote.html", CONTENT=render_inline(text)))
            continue
        # list
        if re.match(r"^([-*+]\s+|\d+\.\s+)", s):
            items = []
            while i < n and re.match(r"^([-*+]\s+|\d+\.\s+)", lines[i].strip()):
                item = re.sub(r"^([-*+]\s+|\d+\.\s+)", "", lines[i].strip())
                items.append(_fill("block-list-item.html", CONTENT=render_inline(item)))
                i += 1
            items_html = "\n          ".join(items)
            out.append(_fill("block-list.html", ITEMS="          " + items_html))
            continue
        # image-only paragraph
        mi = re.match(r"^!\[([^\]]*)\]\(([^)]*)\)\s*$", s)
        if mi:
            out.append(_image(mi.group(1), mi.group(2), image_resolver))
            i += 1
            continue
        # paragraph
        buf = [line]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if nxt == "" or _is_block_start(nxt):
                break
            buf.append(lines[i])
            i += 1
        text = " ".join(x.strip() for x in buf).strip()
        out.append(_fill("block-p.html", CONTENT=render_inline(text)))
    return "\n        ".join(out)


def plain_text(markdown_text: str) -> str:
    """Strip markdown to plain text (for read-time / fallbacks)."""
    t = re.sub(r"`{1,3}[^`]*`{1,3}", " ", markdown_text)
    t = re.sub(r"[#>*_\[\]()!`]", " ", t)
    return re.sub(r"\s+", " ", t).strip()
