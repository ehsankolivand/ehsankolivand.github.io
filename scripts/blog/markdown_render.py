"""In-house, stdlib-only Markdown renderer keyed to the design's block vocabulary.

Maps Markdown to the exact design block partials (paragraph, h2, code+caption, quote,
list, image). No syntax highlighting, no client JS (Clarification / FR-013). All text
and attributes are HTML-escaped.
"""
from __future__ import annotations
import re
import html
import unicodedata
from pathlib import Path
from functools import lru_cache

from . import config
from . import highlight

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


# Render-scoped footnote context: set by render() for the current post, read by render_inline.
# None outside a render() call (so render_inline used standalone treats `[^id]` as literal text).
_CURRENT_FN = None


# --------------------------------------------------------------------------- #
# Inline rendering
# --------------------------------------------------------------------------- #
_SAFE_URL_SCHEMES = ("http", "https", "mailto")


def _is_safe_url(url: str) -> bool:
    """Allow-list link schemes: http/https/mailto plus schemeless (relative/anchor/query)
    URLs. Everything else (javascript:, data:, vbscript:, …) is unsafe. Browsers strip C0
    control chars + whitespace when reading a URL's scheme, so strip the same first: leading
    controls/space AND every EMBEDDED C0 control + DEL (which html.escape would not remove).
    This defeats both `\\x01javascript:` (leading) and `java\\x00script:` (embedded) scheme
    smuggling — without an embedded-control strip the scheme regex would miss the `:` and the
    URL would be misclassified as a harmless relative link, then emitted with a raw NUL that a
    NUL-stripping browser reassembles into `javascript:`."""
    u = re.sub(r"^[\x00-\x20]+", "", url)
    u = re.sub(r"[\x00-\x1f\x7f]", "", u)  # all C0 controls + DEL, anywhere (subsumes \t\n\r)
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
    # footnote references [^id]: only when the current render has a matching definition; stashed
    # after inline code (so `[^x]` inside code stays literal) and before escaping. Undefined refs
    # are left as literal text (no dangling anchor — Constitution VIII).
    if _CURRENT_FN is not None:
        text = re.sub(
            r"\[\^([^\]]+)\]",
            lambda m: keep(_footnote_ref(m.group(1))) if m.group(1) in _CURRENT_FN.defs else m.group(0),
            text)
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
# Heading anchors (deterministic, collision-free section ids for deep-citability)
# --------------------------------------------------------------------------- #
_TAG_RE = re.compile(r"<[^>]+>")
_SLUG_NONWORD = re.compile(r"[^a-z0-9]+")


def _visible_text(inline_html: str) -> str:
    """Visible text of rendered inline HTML: drop tags, unescape entities. Used so a heading
    slug reflects the words a reader sees (e.g. a link's label, not its URL)."""
    return html.unescape(_TAG_RE.sub("", inline_html))


def heading_slug(text: str) -> str:
    """GitHub-style slug of a heading's visible text: NFKD->ASCII fold (so 'Café'->'cafe',
    Turkish 'ş'->'s'), lowercase, every run of non-alphanumerics -> single '-', trimmed.
    Returns '' for symbol/emoji-only text (the caller assigns a stable `section-<n>` id).
    Deterministic and stable across builds (depends only on the heading text)."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return _SLUG_NONWORD.sub("-", ascii_text.lower()).strip("-")


def _alloc_heading_id(visible: str, ordinal: int, used: set, counts: dict) -> str:
    """Assign one heading a unique, deterministic id within a post. `used` (all ids so far) and
    `counts` (per-base suffix counter) are post-scoped state. Repeats of the same base get
    '-1','-2',… in document order; an empty slug falls back to 'section-<ordinal>'. The while-loop
    guarantees global uniqueness even if a suffixed id collides with another heading's base."""
    base = heading_slug(visible) or f"section-{ordinal}"
    n = counts.get(base, 0)
    hid = base
    while hid in used:
        n += 1
        hid = f"{base}-{n}"
    counts[base] = n
    used.add(hid)
    return hid


# --------------------------------------------------------------------------- #
# Callouts / admonitions (Obsidian `> [!kind]` form) + footnotes (`[^id]` / `[^id]:`)
# --------------------------------------------------------------------------- #
# Synonyms collapse to one of five canonical kinds; unknown -> note (graceful degradation).
_CALLOUT_SYNONYMS = {
    "note": "note", "info": "note", "abstract": "note", "summary": "note", "quote": "note", "cite": "note",
    "tip": "tip", "success": "tip", "hint": "tip", "check": "tip", "done": "tip",
    "warning": "warning", "warn": "warning", "attention": "warning",
    "important": "important",
    "caution": "caution", "danger": "caution", "error": "caution", "bug": "caution", "failure": "caution", "fail": "caution",
}
# (visible label, aria-hidden glyph) — glyphs are decorative; the label conveys meaning.
_CALLOUT_META = {
    "note": ("Note", "ℹ"),        # information sign
    "tip": ("Tip", "✓"),          # check mark
    "warning": ("Warning", "⚠"),  # warning sign
    "important": ("Important", "★"),  # star
    "caution": ("Caution", "‼"),  # double exclamation
}


def _paragraphs(de_quoted_lines: list) -> list:
    """Group de-quoted lines into paragraph strings on blank-line boundaries (shared by
    blockquotes and callout bodies)."""
    paras, cur = [], []
    for ln in de_quoted_lines:
        if ln.strip() == "":
            if cur:
                paras.append(" ".join(x.strip() for x in cur).strip())
                cur = []
        else:
            cur.append(ln)
    if cur:
        paras.append(" ".join(x.strip() for x in cur).strip())
    return [p for p in paras if p]


def _callout(raw_kind: str, title_text: str, body_lines: list) -> str:
    """Render an Obsidian-style callout to a static, accessible labeled region."""
    kind = _CALLOUT_SYNONYMS.get(raw_kind.lower(), "note")
    label, icon = _CALLOUT_META[kind]
    body = "<br><br>".join(render_inline(p) for p in _paragraphs(body_lines))
    title = render_inline(title_text.strip()) if title_text.strip() else esc(label)
    return _fill("block-callout.html", KIND=kind, ARIA=esc_attr(f"{label} callout"),
                 ICON=icon, TITLE=title, BODY=body)


class _FnCtx:
    """Post-scoped footnote registry. `defs`/`slug_of` are fixed by render()'s pre-pass; `order`
    (reference order → visible numbers) and `ref_counts` (unique repeat-ref ids) fill during render."""
    __slots__ = ("defs", "slug_of", "order", "ref_counts")

    def __init__(self, defs, slug_of):
        self.defs = defs
        self.slug_of = slug_of
        self.order = []
        self.ref_counts = {}


def _footnote_ref(fid: str) -> str:
    ctx = _CURRENT_FN
    if fid not in ctx.order:
        ctx.order.append(fid)
    num = ctx.order.index(fid) + 1
    ctx.ref_counts[fid] = ctx.ref_counts.get(fid, 0) + 1
    slug = ctx.slug_of[fid]
    refid = f"fnref-{slug}" if ctx.ref_counts[fid] == 1 else f"fnref-{slug}-{ctx.ref_counts[fid]}"
    return (f'<sup class="fnref" id="{esc_attr(refid)}">'
            f'<a href="#fn-{esc_attr(slug)}" role="doc-noteref" aria-label="Footnote {num}">{num}</a></sup>')


_FN_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:\s?(.*)$")


def _extract_footnote_defs(lines: list):
    """Fence-aware extraction of `[^id]: definition` blocks. Returns (defs dict, kept lines) with
    the definition lines (+ simple indented continuations) removed from the body. `[^x]:` inside a
    fenced code block is left untouched (treated as code, not a definition)."""
    defs, kept = {}, []
    i, n = 0, len(lines)
    fence = None
    while i < n:
        line = lines[i]
        s = line.strip()
        if fence is not None:
            if s.startswith(fence):
                fence = None
            kept.append(line)
            i += 1
            continue
        if s.startswith("```") or s.startswith("~~~"):
            fence = s[:3]
            kept.append(line)
            i += 1
            continue
        md = _FN_DEF_RE.match(line)
        if md:
            fid = md.group(1)
            body = [md.group(2)]
            i += 1
            while i < n and lines[i].strip() != "" and lines[i][:1] in (" ", "\t"):
                body.append(lines[i].strip())
                i += 1
            defs[fid] = " ".join(body).strip()
            continue
        kept.append(line)
        i += 1
    return defs, kept


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


# Fenced-code info string -> (language, filename, emphasized lines, legacy caption). GFM superset:
# the first bare-word token is the language; title=/file=/filename="..." is the filename label;
# {1,3-5} are 1-based emphasized lines. If the first token is not a bare-word language token, the
# WHOLE info string is a legacy caption (no language, no highlighting). See contracts/code-block.md.
_INFO_LANG_RE = re.compile(r"^[A-Za-z0-9+#._-]+$")
_INFO_TITLE_RE = re.compile(r'(?:title|file|filename)\s*=\s*"([^"]*)"')
_INFO_BRACE_RE = re.compile(r"\{([0-9,\s\-]+)\}")


def parse_info_string(info: str):
    info = (info or "").strip()
    if not info:
        return None, None, frozenset(), None
    first = info.split()[0]
    if not _INFO_LANG_RE.match(first):
        return None, None, frozenset(), info  # legacy caption (prose / `//path` / `key=val` lead)
    rest = info[len(first):]
    filename = None
    mt = _INFO_TITLE_RE.search(rest)
    if mt:
        filename = mt.group(1)
    emphasized: set[int] = set()
    mb = _INFO_BRACE_RE.search(rest)
    if mb:
        for part in mb.group(1).split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, _, b = part.partition("-")
                if a.strip().isdigit() and b.strip().isdigit():
                    lo, hi = int(a), int(b)
                    emphasized.update(range(min(lo, hi), max(lo, hi) + 1))
            elif part.isdigit():
                emphasized.add(int(part))
    return first, filename, frozenset(emphasized), None


def _code_block(code: str, language, filename, emphasized, caption) -> str:
    # highlight (or escape-only fallback) -> CONTENT; title-bar label precedence:
    # filename -> legacy caption -> language token -> "" (preserves the pre-004 caption behavior).
    content, _recognized, _lang = highlight.highlight_code(code, language, emphasized)
    label = filename or caption or language or ""
    return _fill("block-code.html", CAPTION=esc(label), CONTENT=content)


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


def _split_row(row: str) -> list:
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", row)]


_SEP_CELL = re.compile(r"^:?-+:?$")


def _is_table_sep(line: str) -> bool:
    """A GFM table delimiter row: every pipe-split cell matches `:?-+:?`. Split-and-check (not one
    monolithic regex) so SINGLE-column tables (`|---|`) and ragged separators are recognized (FR-013)."""
    cells = _split_row(line)
    return bool(cells) and all(_SEP_CELL.match(c.strip()) for c in cells)


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
    global _CURRENT_FN
    lines = markdown_text.split("\n")
    out: list[str] = []
    # post-scoped heading-anchor state: deterministic, collision-free section ids (one render()
    # call == one post body, so ids are unique within a page and stable across builds).
    used_ids: set[str] = set()
    base_counts: dict[str, int] = {}
    heading_ordinal = 0
    # footnotes: extract definitions (fence-aware), reserve collision-free ids in the SAME used_ids
    # set the heading allocator uses (so a heading and a footnote can never share an id), then expose
    # a render-scoped context that render_inline reads to turn `[^id]` into a superscript link.
    fn_defs, lines = _extract_footnote_defs(lines)
    fn_slug: dict[str, str] = {}
    for idx, fid in enumerate(fn_defs, start=1):
        slug = heading_slug(fid) or f"fn{idx}"
        cand, k = slug, 0
        while f"fn-{cand}" in used_ids or f"fnref-{cand}" in used_ids:
            k += 1
            cand = f"{slug}-{k}"
        used_ids.add(f"fn-{cand}")
        used_ids.add(f"fnref-{cand}")
        fn_slug[fid] = cand
    _CURRENT_FN = _FnCtx(fn_defs, fn_slug)
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
            language, filename, emphasized, caption = parse_info_string(mfence.group(2))
            i += 1
            buf: list[str] = []
            while i < n and not lines[i].strip().startswith(fence):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            out.append(_code_block("\n".join(buf), language, filename, emphasized, caption))
            continue
        # heading -> design heading style at the correct semantic level (never <h1>,
        # which is reserved for the post title): #/## -> h2, ### -> h3, ####+ -> h4.
        mh = re.match(r"^(#{1,6})\s+(.*)$", s)
        if mh:
            level = max(2, min(len(mh.group(1)), 4))
            inline = render_inline(mh.group(2).strip())
            heading_ordinal += 1
            hid = _alloc_heading_id(_visible_text(inline), heading_ordinal, used_ids, base_counts)
            out.append(_fill("block-h2.html", TAG=f"h{level}", ID=esc_attr(hid), CONTENT=inline))
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
            # Obsidian callout? First de-quoted line `[!kind] optional title` -> labeled region.
            mco = re.match(r"^\[!([A-Za-z]+)\]\s*(.*)$", buf[0]) if buf else None
            if mco:
                out.append(_callout(mco.group(1), mco.group(2), buf[1:]))
                continue
            content = "<br><br>".join(render_inline(p) for p in _paragraphs(buf))
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
        if "|" in s and i + 1 < n and _is_table_sep(lines[i + 1]):
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
    # Footnotes section: referenced + defined notes in reference order. Definitions render with the
    # footnote context OFF (a nested `[^x]` in a definition stays literal — no self-mutation).
    order = list(_CURRENT_FN.order)
    _CURRENT_FN = None
    if order:
        items = []
        for fid in order:
            slug = fn_slug[fid]
            def_html = render_inline(fn_defs[fid])
            items.append(
                f'<li id="fn-{esc_attr(slug)}" class="footnotes__item">{def_html} '
                f'<a href="#fnref-{esc_attr(slug)}" class="fn-back" role="doc-backlink" '
                f'aria-label="Back to content">↩</a></li>')
        out.append(_fill("block-footnotes.html", ITEMS="\n        ".join(items)))
    return "\n        ".join(out)
