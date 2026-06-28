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
# table cells reuse the design's existing tokens (block-code panel grays + mono headers)
TABLE_TH_STYLE = ("padding:11px 16px; font-family:'JetBrains Mono',monospace; font-size:11.5px; "
                  "letter-spacing:.04em; color:#EDF2EF; background:rgba(255,255,255,0.02); "
                  "border-bottom:1px solid rgba(255,255,255,0.08);")
TABLE_TD_STYLE = "padding:11px 16px; border-bottom:1px solid rgba(255,255,255,0.06); vertical-align:top;"


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
_SAFE_URL_SCHEMES = ("http", "https", "mailto")


def _is_safe_url(url: str) -> bool:
    """Allow-list link schemes: http/https/mailto plus schemeless (relative/anchor/query)
    URLs. Everything else (javascript:, data:, vbscript:, …) is unsafe. Browsers strip
    leading C0 control chars + whitespace before reading the scheme, so strip the same
    first to defeat `\\x01javascript:`-style bypasses."""
    u = re.sub(r"^[\x00-\x20]+", "", url)
    u = re.sub(r"[\t\n\r]", "", u)
    m = re.match(r"^([a-zA-Z][a-zA-Z0-9+.\-]*):", u)
    if not m:
        return True  # relative / anchor / query / protocol-relative — no scheme to abuse
    return m.group(1).lower() in _SAFE_URL_SCHEMES


def _anchor(url: str, label_html: str) -> str:
    if not _is_safe_url(url):
        return label_html  # neutralize unsafe scheme: keep the text, drop the link
    external = url.startswith("http://") or url.startswith("https://")
    rel = ' target="_blank" rel="noopener"' if external else ""
    return f'<a href="{esc_attr(url)}"{rel} style="{LINK_STYLE}">{label_html}</a>'


def _inline_image(alt: str, url: str) -> str:
    """An inline (mid-text) image. Absolute http(s) URLs are used as-is; a relative author
    path is resolved to its /blog/assets/media/ URL. Unsafe schemes fall back to alt text."""
    u = url.strip()
    if not _is_safe_url(u):
        return esc(alt)
    if not (u.startswith("http://") or u.startswith("https://")):
        u = config.media_url(u)
    return (f'<img src="{esc_attr(u)}" alt="{esc_attr(alt)}" loading="lazy" decoding="async" '
            'style="max-width:100%; height:auto; border-radius:6px; vertical-align:middle;">')


def _emphasis(text: str) -> str:
    """Bold-italic, then bold, then italic. Operates on already-escaped text (and survives
    NUL placeholders). Bold uses a non-greedy run so a single inner '*'/'_' is allowed
    (e.g. ``**a*b**``); the ``***``/``___`` rule runs first so triple spans don't mis-pair."""
    bold = r'<strong style="color:#EDF2EF; font-weight:700;">\1</strong>'
    bolditalic = r'<strong style="color:#EDF2EF; font-weight:700;"><em>\1</em></strong>'
    text = re.sub(r"\*\*\*([^*]+)\*\*\*", bolditalic, text)
    text = re.sub(r"___([^_]+)___", bolditalic, text)
    text = re.sub(r"\*\*(.+?)\*\*", bold, text)
    text = re.sub(r"__(.+?)__", bold, text)
    text = re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_([^_\s][^_]*?)_(?!\w)", r"<em>\1</em>", text)
    return text


def render_inline(text: str) -> str:
    """Render Markdown inline syntax (code, links, bold, italic) with escaping."""
    stash: dict[str, str] = {}

    def keep(html_fragment: str) -> str:
        key = f"\x00{len(stash)}\x00"
        stash[key] = html_fragment
        return key

    # inline code first (verbatim, escaped) so its contents aren't further processed
    text = re.sub(r"`([^`]+)`", lambda m: keep(f'<code style="{INLINE_CODE_STYLE}">{esc(m.group(1))}</code>'), text)
    # inline images before links so the leading '!' is consumed (not left as a stray char)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)",
                  lambda m: keep(_inline_image(m.group(1), m.group(2))), text)
    # links [label](url): url may be <bracketed> (allowing spaces); label renders emphasis
    text = re.sub(r"\[([^\]]+)\]\(\s*(?:<([^>]+)>|([^)\s]+))(?:\s+\"[^\"]*\")?\s*\)",
                  lambda m: keep(_anchor((m.group(2) or m.group(3)), _emphasis(esc(m.group(1))))), text)
    # autolinks <https://...> / <mailto:...> (before esc, which would mangle the angle brackets)
    text = re.sub(r"<((?:https?|mailto):[^>\s]+)>",
                  lambda m: keep(_anchor(m.group(1), esc(m.group(1)))), text)
    # escape the remaining literal text
    text = esc(text)
    # bold then italic
    text = _emphasis(text)
    # restore protected fragments in reverse insertion order: a later fragment (e.g. a
    # link) may embed an earlier placeholder (e.g. inline code in its label), so restoring
    # newest-first ensures those embedded placeholders are still resolved (no stray NUL).
    for key, frag in reversed(list(stash.items())):
        text = text.replace(key, frag)
    return text


# --------------------------------------------------------------------------- #
# Block rendering
# --------------------------------------------------------------------------- #
_TOKEN_RE = re.compile(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}")


def sub_tokens(template: str, tokens: dict) -> str:
    """Single-pass `{{TOKEN}}` substitution. One scan over the template, so a substituted
    value containing `{{OTHER}}` is never re-scanned (kills token-injection: author text
    like `{{BODY}}`/`{{CAPTION}}` can't hijack a later token). Unknown tokens are left
    intact so verify_build can still flag genuinely-unresolved ones."""
    return _TOKEN_RE.sub(lambda m: tokens.get(m.group(1), m.group(0)), template)


def _fill(partial_name: str, **tokens) -> str:
    return sub_tokens(_partial(partial_name), tokens)


def _code_block(code: str, caption: str) -> str:
    return _fill("block-code.html", CAPTION=esc(caption), CONTENT=esc(code))


def _image(alt: str, src: str, image_resolver) -> str:
    if not src.strip():
        # design's placeholder caption box
        return _fill("block-img-placeholder.html", CAPTION=esc(alt))
    url, width, height = image_resolver(src.strip(), alt)
    caption_html = ""
    img_alt = alt
    if alt.strip():
        caption_html = _fill("block-img-caption.html", CAPTION=esc(alt))
        img_alt = ""  # the visible figcaption already conveys this — avoid double SR read
    return _fill("block-img.html", SRC=esc_attr(url), ALT=esc_attr(img_alt),
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


_LIST_LINE = re.compile(r"^(\s*)([-*+]|\d+\.)\s+(.*)$")


def _emit_list_groups(nodes: list) -> str:
    """Emit sibling list nodes, splitting into separate <ul>/<ol> runs whenever the marker
    type changes (BUG-034). nodes: [(ordered: bool, content: str, children_html: str)]."""
    chunks: list[str] = []
    k = 0
    while k < len(nodes):
        ordered = nodes[k][0]
        items_html: list[str] = []
        num = 0
        while k < len(nodes) and nodes[k][0] == ordered:
            _, content, children_html = nodes[k]
            num += 1
            inner = render_inline(content)
            if children_html:
                inner += "\n          " + children_html
            if ordered:
                items_html.append(_fill("block-olist-item.html", NUM=str(num), CONTENT=inner))
            else:
                items_html.append(_fill("block-list-item.html", CONTENT=inner))
            k += 1
        body = "          " + "\n          ".join(items_html)
        chunks.append(_fill("block-olist.html" if ordered else "block-list.html", ITEMS=body))
    return "\n        ".join(chunks)


_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")


def _split_row(row: str) -> list:
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", row)]


def _table_aligns(sep_row: str) -> list:
    out = []
    for c in _split_row(sep_row):
        c = c.strip()
        out.append("center" if c.startswith(":") and c.endswith(":")
                   else "right" if c.endswith(":")
                   else "left" if c.startswith(":") else "")
    return out


def _render_table(header: list, body: list, aligns: list) -> str:
    def cell(tag: str, style: str, idx: int, text: str) -> str:
        a = aligns[idx] if idx < len(aligns) else ""
        return f'<{tag} style="{style} text-align:{a or "left"};">{render_inline(text)}</{tag}>'

    head = "<thead><tr>" + "".join(
        cell("th", TABLE_TH_STYLE, k, c) for k, c in enumerate(header)) + "</tr></thead>"
    rows = "".join(
        "<tr>" + "".join(cell("td", TABLE_TD_STYLE, k, r[k] if k < len(r) else "")
                         for k in range(len(header))) + "</tr>"
        for r in body)
    return _fill("block-table.html", HEAD=head, BODY=(f"<tbody>{rows}</tbody>" if rows else ""))


def _render_list_run(run: list) -> str:
    """Build nested <ul>/<ol> from a flat run of (indent, ordered, content) list lines:
    real <ol> semantics for ordered lists (BUG-008) and indentation-based nesting (BUG-009)."""
    pos = 0

    def parse(min_indent: int) -> str:
        nonlocal pos
        nodes: list = []
        while pos < len(run):
            indent, ordered, content = run[pos]
            if indent < min_indent:
                break
            pos += 1
            children_html = ""
            if pos < len(run) and run[pos][0] > indent:
                children_html = parse(indent + 1)  # anything deeper is a child
            nodes.append((ordered, content, children_html))
        return _emit_list_groups(nodes)

    return parse(run[0][0])


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
        # heading -> design heading style at the correct semantic level (never <h1>,
        # which is reserved for the post title): #/## -> h2, ### -> h3, ####+ -> h4.
        mh = re.match(r"^(#{1,6})\s+(.*)$", s)
        if mh:
            level = max(2, min(len(mh.group(1)), 4))
            out.append(_fill("block-h2.html", TAG=f"h{level}",
                             CONTENT=render_inline(mh.group(2).strip())))
            i += 1
            continue
        # thematic break -> skip
        if re.match(r"^([-*_])\1\1+$", s):
            i += 1
            continue
        # blockquote: strip every leading '>' level (no &gt; leak on nesting) and keep
        # paragraph breaks (blank de-quoted lines) inside the single styled blockquote.
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*(>\s?)+", "", lines[i]))
                i += 1
            paras, cur = [], []
            for ln in buf:
                if ln.strip() == "":
                    if cur:
                        paras.append(" ".join(x.strip() for x in cur).strip())
                        cur = []
                else:
                    cur.append(ln)
            if cur:
                paras.append(" ".join(x.strip() for x in cur).strip())
            content = "<br><br>".join(render_inline(p) for p in paras if p)
            out.append(_fill("block-quote.html", CONTENT=content))
            continue
        # list (ordered/unordered, nestable by indentation)
        if re.match(r"^([-*+]\s+|\d+\.\s+)", s):
            run = []
            while i < n:
                ml = _LIST_LINE.match(lines[i])
                if not ml:
                    break
                indent = len(ml.group(1).expandtabs(4))
                ordered = ml.group(2).endswith(".")
                run.append((indent, ordered, ml.group(3).rstrip()))
                i += 1
            out.append(_render_list_run(run))
            continue
        # image-only paragraph
        mi = re.match(r"^!\[([^\]]*)\]\(([^)]*)\)\s*$", s)
        if mi:
            out.append(_image(mi.group(1), mi.group(2), image_resolver))
            i += 1
            continue
        # GFM table: a header row of pipes immediately followed by a separator row
        if "|" in s and i + 1 < n and _TABLE_SEP.match(lines[i + 1].strip()):
            aligns = _table_aligns(lines[i + 1].strip())
            header = _split_row(s)
            i += 2
            body = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                body.append(_split_row(lines[i].strip()))
                i += 1
            out.append(_render_table(header, body, aligns))
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
