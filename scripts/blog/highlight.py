"""Vendored, stdlib-only, deterministic syntax highlighter (feature 004).

Tokenizes fenced code into semantic classed spans at BUILD TIME. No third-party
library, no client-side highlighter (Constitution II/I). Security-by-construction:
every character is HTML-escaped exactly once and every CSS class comes from a fixed,
CLOSED vocabulary (never derived from author text) — see
specs/004-technical-writing-canvas/contracts/highlighter.md.

Public API:
    resolve_lang(tag)  -> canonical language id | None
    tokenize(code,lang) -> (list[(class|None, text)], recognized: bool)   # coverage: join==code
    emit_html(tokens, emphasized_lines) -> str                            # inline | block-line mode
    highlight_code(code, lang_tag, emphasized_lines) -> (content_html, recognized, lang)
"""
from __future__ import annotations
import html
import re

# Closed token-kind CSS class vocabulary (styled in templates/blog/assets/blog.css).
TOKEN_CLASSES = (
    "tok-comment", "tok-keyword", "tok-string", "tok-number", "tok-function",
    "tok-type", "tok-builtin", "tok-operator", "tok-tag", "tok-attr", "tok-meta",
)


# --------------------------------------------------------------------------- #
# Engine: one ordered-alternation scanner shared by every language.
# A rule is (kind, pattern) where kind is a final CSS class, None (plain text),
# or "_name" (an identifier to post-classify against the language's word sets).
# Patterns MUST use only NON-CAPTURING groups so m.lastgroup is the matched rule.
# --------------------------------------------------------------------------- #
def _build(rules, kw=(), types=(), builtins=(), cap_is_type=False, ci=False):
    parts, kinds = [], []
    for i, (kind, pat) in enumerate(rules):
        parts.append(f"(?P<g{i}>{pat})")
        kinds.append(kind)
    master = re.compile("|".join(parts))
    return {
        "master": master, "kinds": kinds,
        "kw": frozenset(kw), "types": frozenset(types), "builtins": frozenset(builtins),
        "cap_is_type": cap_is_type, "ci": ci,
    }


def _is_call(code: str, end: int) -> bool:
    """True if the next non-space character after `end` is '(' (function-call/def context)."""
    j = end
    n = len(code)
    while j < n and code[j] in " \t":
        j += 1
    return j < n and code[j] == "("


def tokenize(code: str, lang: str | None):
    """Tokenize `code` for canonical `lang`. Returns (tokens, recognized).
    INVARIANT: "".join(text for _cls, text in tokens) == code (exact coverage)."""
    spec = _LANGS.get(lang) if lang else None
    if spec is None:
        return ([(None, code)] if code else []), False
    master, kinds = spec["master"], spec["kinds"]
    kw, types, builtins = spec["kw"], spec["types"], spec["builtins"]
    cap_is_type, ci = spec["cap_is_type"], spec["ci"]
    tokens = []
    pos, n = 0, len(code)
    while pos < n:
        m = master.match(code, pos)
        if m is None or m.end() == pos:
            tokens.append((None, code[pos]))   # no rule (or zero-width) -> one plain char
            pos += 1
            continue
        text = m.group()
        kind = kinds[int(m.lastgroup[1:])]
        if kind == "_name":
            probe = text.upper() if ci else text
            if probe in kw:
                cls = "tok-keyword"
            elif probe in types:
                cls = "tok-type"
            elif probe in builtins:
                cls = "tok-builtin"
            elif _is_call(code, m.end()):
                cls = "tok-function"
            elif cap_is_type and text[:1].isupper():
                cls = "tok-type"
            else:
                cls = None
            tokens.append((cls, text))
        else:
            tokens.append((kind, text))   # kind is a tok-* class or None
        pos = m.end()
    return tokens, True


def emit_html(tokens, emphasized_lines=frozenset()) -> str:
    """Escape each token exactly once and wrap classed tokens. Two modes:
    no emphasis -> inline (literal newlines, copy-friendly); emphasis -> block-line spans."""
    def esc(t):  # exactly once; quote=False keeps it identical to the existing code path
        return html.escape(t, quote=False)

    if not emphasized_lines:
        out = []
        for cls, text in tokens:
            out.append(f'<span class="{cls}">{esc(text)}</span>' if cls else esc(text))
        return "".join(out)

    # block-line mode: split tokens at newlines so multi-line tokens distribute across lines.
    lines = [[]]
    for cls, text in tokens:
        parts = text.split("\n")
        for k, part in enumerate(parts):
            if k > 0:
                lines.append([])
            if part:
                lines[-1].append(f'<span class="{cls}">{esc(part)}</span>' if cls else esc(part))
    out = []
    for idx, frags in enumerate(lines, start=1):
        hl = " cl--hl" if idx in emphasized_lines else ""
        out.append(f'<span class="cl{hl}">{"".join(frags)}</span>')
    return "".join(out)


def resolve_lang(tag: str | None) -> str | None:
    if not tag:
        return None
    key = ALIASES.get(tag.strip().lower(), tag.strip().lower())
    return key if key in _LANGS else None


def highlight_code(code: str, lang_tag: str | None, emphasized_lines=frozenset()):
    """Convenience used by markdown_render: (content_html, recognized, canonical_lang)."""
    lang = resolve_lang(lang_tag)
    tokens, recognized = tokenize(code, lang)
    return emit_html(tokens, emphasized_lines), recognized, lang


# --------------------------------------------------------------------------- #
# Shared rule fragments (all NON-capturing).
# --------------------------------------------------------------------------- #
_WS = (None, r"\s+")
_NUM_C = (r"\b(?:0[xX][0-9a-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|\d[\d_]*\.?\d*(?:[eE][+-]?\d+)?[fFlLuU]*)\b")
_STR_DQ = r'"(?:\\.|[^"\\\n])*"'
_STR_SQ = r"'(?:\\.|[^'\\\n])*'"
_OP = r"[-+*/%=<>!&|^~?:.,;@]+|[()\[\]{}]"


# --------------------------------------------------------------------------- #
# Language rule tables + word sets.
# --------------------------------------------------------------------------- #
_KOTLIN_KW = """as as? break by catch class companion constructor continue crossinline
 data delegate do dynamic else enum expect external false field file finally for fun get if import
 in infix init inline inner interface internal is lateinit noinline object open operator out override
 package private protected public reified return sealed set super suspend tailrec this throw try
 typealias typeof val var vararg when where while abstract actual annotation const final""".split()
_KOTLIN_TYPES = """Int Long Short Byte Float Double Boolean Char String Unit Any Nothing Array List
 MutableList Map MutableMap Set MutableSet Sequence Pair Triple Result Flow""".split()
_KOTLIN_BUILTINS = "true false null it this super println print listOf mapOf setOf require check".split()

_JAVA_KW = """abstract assert boolean break byte case catch char class const continue default do double
 else enum extends final finally float for goto if implements import instanceof int interface long
 native new package private protected public return short static strictfp super switch synchronized
 this throw throws transient try void volatile while var record sealed permits yield""".split()
_JAVA_TYPES = """String Integer Long Double Float Boolean Character Object List Map Set ArrayList HashMap
 HashSet Optional Stream Exception RuntimeException""".split()
_JAVA_BUILTINS = "true false null this super System out println print".split()

_PY_KW = """and as assert async await break class continue def del elif else except finally for from
 global if import in is lambda nonlocal not or pass raise return try while with yield match case""".split()
_PY_TYPES = """int float complex bool str bytes bytearray list tuple dict set frozenset object type
 Exception ValueError TypeError KeyError IndexError RuntimeError""".split()
_PY_BUILTINS = """True False None self cls print len range enumerate zip map filter open input super
 isinstance hasattr getattr setattr property staticmethod classmethod""".split()

_BASH_KW = "if then else elif fi case esac for select while until do done in function time coproc".split()
_BASH_BUILTINS = """echo cd read export source alias unalias set unset local return exit eval exec printf
 test true false sudo apt apt-get systemctl service curl wget git docker chmod chown mkdir rm cp mv ln""".split()

_JS_KW = """break case catch class const continue debugger default delete do else export extends finally
 for function if import in instanceof let new return super switch this throw try typeof var void while
 with yield async await of static get set""".split()
_JS_BUILTINS = """true false null undefined NaN Infinity this console Math JSON Object Array String Number
 Boolean Promise Map Set Symbol document window require module exports""".split()

_TS_KW = _JS_KW + """interface type enum namespace declare public private protected readonly implements
 abstract as keyof infer is satisfies override""".split()
_TS_TYPES = "string number boolean any unknown never void object symbol bigint Record Partial Readonly Array".split()

_SQL_KW = """SELECT FROM WHERE INSERT UPDATE DELETE CREATE DROP ALTER TABLE INDEX VIEW INTO VALUES SET
 JOIN INNER LEFT RIGHT OUTER FULL ON AS AND OR NOT NULL IS IN LIKE BETWEEN GROUP BY ORDER HAVING LIMIT
 OFFSET DISTINCT UNION ALL PRIMARY KEY FOREIGN REFERENCES DEFAULT CONSTRAINT UNIQUE CHECK CASE WHEN THEN
 ELSE END BEGIN COMMIT ROLLBACK TRANSACTION WITH RETURNING""".split()
_SQL_TYPES = """INT INTEGER BIGINT SMALLINT DECIMAL NUMERIC FLOAT REAL DOUBLE CHAR VARCHAR TEXT DATE TIME
 TIMESTAMP BOOLEAN BLOB SERIAL UUID JSON JSONB""".split()
_SQL_BUILTINS = "COUNT SUM AVG MIN MAX COALESCE NOW CURRENT_TIMESTAMP CAST TRUE FALSE".split()

_LANGS = {
    "kotlin": _build([
        ("tok-comment", r"//[^\n]*"), ("tok-comment", r"/\*[\s\S]*?\*/"),
        ("tok-string", r'"""[\s\S]*?"""'), ("tok-string", r'(?:[bBfFrRuU]{0,2})' + _STR_DQ),
        ("tok-string", _STR_SQ), ("tok-number", _NUM_C),
        ("tok-meta", r"@[A-Za-z_][\w.]*"),
        ("_name", r"[A-Za-z_]\w*"), ("tok-operator", _OP), _WS,
    ], _KOTLIN_KW, _KOTLIN_TYPES, _KOTLIN_BUILTINS, cap_is_type=True),

    "java": _build([
        ("tok-comment", r"//[^\n]*"), ("tok-comment", r"/\*[\s\S]*?\*/"),
        ("tok-string", _STR_DQ), ("tok-string", _STR_SQ), ("tok-number", _NUM_C),
        ("tok-meta", r"@[A-Za-z_][\w.]*"),
        ("_name", r"[A-Za-z_$][\w$]*"), ("tok-operator", _OP), _WS,
    ], _JAVA_KW, _JAVA_TYPES, _JAVA_BUILTINS, cap_is_type=True),

    "python": _build([
        ("tok-comment", r"#[^\n]*"),
        ("tok-string", r"(?:[rRbBfFuU]{0,2})'''[\s\S]*?'''"),
        ("tok-string", r'(?:[rRbBfFuU]{0,2})"""[\s\S]*?"""'),
        ("tok-string", r"(?:[rRbBfFuU]{0,2})" + _STR_DQ),
        ("tok-string", r"(?:[rRbBfFuU]{0,2})" + _STR_SQ),
        ("tok-number", _NUM_C), ("tok-meta", r"@[A-Za-z_][\w.]*"),
        ("_name", r"[A-Za-z_]\w*"), ("tok-operator", _OP), _WS,
    ], _PY_KW, _PY_TYPES, _PY_BUILTINS),

    "bash": _build([
        ("tok-comment", r"#[^\n]*"),
        ("tok-string", r'"(?:\\.|[^"\\])*"'), ("tok-string", r"'[^']*'"),
        ("tok-builtin", r"\$\{[^}]*\}|\$[A-Za-z_]\w*|\$[0-9@*#?!$-]"),
        ("tok-number", r"\b\d+\b"),
        ("_name", r"[A-Za-z_][\w-]*"), ("tok-operator", r"[|&;<>()\[\]{}=!]+"), _WS,
    ], _BASH_KW, (), _BASH_BUILTINS),

    "json": _build([
        ("tok-attr", r'"(?:\\.|[^"\\])*"(?=\s*:)'), ("tok-string", r'"(?:\\.|[^"\\])*"'),
        ("tok-number", r"-?\b\d[\d.eE+-]*\b"), ("tok-builtin", r"\b(?:true|false|null)\b"),
        ("tok-operator", r"[{}\[\],:]"), _WS,
    ]),

    "yaml": _build([
        ("tok-comment", r"#[^\n]*"),
        ("tok-attr", r"[A-Za-z_][\w.-]*(?=:(?:\s|$))"),
        ("tok-string", r'"(?:\\.|[^"\\])*"'), ("tok-string", r"'(?:''|[^'])*'"),
        ("tok-number", r"\b\d[\d.eE+-]*\b"),
        ("tok-builtin", r"\b(?:true|false|null|yes|no|on|off)\b"),
        ("tok-meta", r"^---$|^\.\.\.$|&[A-Za-z0-9_]+|\*[A-Za-z0-9_]+"),
        ("tok-operator", r"[:\-\[\]{}|>,]"), _WS, (None, r"[^\s#:]+"),
    ]),

    "markup": _build([
        ("tok-comment", r"<!--[\s\S]*?-->"),
        ("tok-meta", r"<!\[CDATA\[[\s\S]*?\]\]>|<![^>]*>|<\?[\s\S]*?\?>"),
        ("tok-tag", r"</?[A-Za-z][\w:-]*"),
        ("tok-attr", r"[A-Za-z_:][\w:.-]*(?=\s*=)"),
        ("tok-string", r'"[^"]*"|\'[^\']*\''),
        ("tok-tag", r"/?>"), ("tok-operator", r"="), _WS, (None, r"[^<>\s=]+"),
    ]),

    "javascript": _build([
        ("tok-comment", r"//[^\n]*"), ("tok-comment", r"/\*[\s\S]*?\*/"),
        ("tok-string", r"`(?:\\.|[^`\\])*`"), ("tok-string", _STR_DQ), ("tok-string", _STR_SQ),
        ("tok-number", _NUM_C), ("tok-meta", r"@[A-Za-z_][\w.]*"),
        ("_name", r"[A-Za-z_$][\w$]*"), ("tok-operator", _OP), _WS,
    ], _JS_KW, (), _JS_BUILTINS, cap_is_type=True),

    "typescript": _build([
        ("tok-comment", r"//[^\n]*"), ("tok-comment", r"/\*[\s\S]*?\*/"),
        ("tok-string", r"`(?:\\.|[^`\\])*`"), ("tok-string", _STR_DQ), ("tok-string", _STR_SQ),
        ("tok-number", _NUM_C), ("tok-meta", r"@[A-Za-z_][\w.]*"),
        ("_name", r"[A-Za-z_$][\w$]*"), ("tok-operator", _OP), _WS,
    ], _TS_KW, _TS_TYPES, _JS_BUILTINS, cap_is_type=True),

    "sql": _build([
        ("tok-comment", r"--[^\n]*"), ("tok-comment", r"/\*[\s\S]*?\*/"),
        ("tok-string", r"'(?:''|[^'])*'"), ("tok-string", r'"(?:[^"]*)"'),
        ("tok-number", r"\b\d[\d.]*\b"),
        ("_name", r"[A-Za-z_]\w*"), ("tok-operator", r"[-+*/%=<>!]+|[(),.;]"), _WS,
    ], _SQL_KW, _SQL_TYPES, _SQL_BUILTINS, ci=True),
}

# Case-insensitive language aliases -> canonical id.
ALIASES = {
    "kt": "kotlin", "kts": "kotlin", "kotlin-script": "kotlin",
    "py": "python", "python3": "python",
    "sh": "bash", "shell": "bash", "zsh": "bash", "console": "bash", "shell-session": "bash",
    "js": "javascript", "jsx": "javascript", "node": "javascript",
    "ts": "typescript", "tsx": "typescript",
    "yml": "yaml",
    "html": "markup", "xhtml": "markup", "svg": "markup", "xml": "markup",
}
