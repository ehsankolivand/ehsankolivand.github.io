# Contract: Syntax Highlighter (`scripts/blog/highlight.py`)

Governs the vendored, stdlib-only, deterministic build-time highlighter. Every emitted character is HTML-escaped exactly once and every class name is from a fixed vocabulary. (FR-001..FR-006; Principles I/II/III/VI.)

## Public API

```python
resolve_lang(tag: str | None) -> str | None
    # case-insensitive alias resolution; returns a canonical language id if supported, else None.

tokenize(code: str, lang: str | None) -> tuple[list[tuple[str | None, str]], bool]
    # (tokens, recognized). recognized=False => tokens == [(None, code)] (or [] for "").
    # INVARIANT: "".join(text for _cls, text in tokens) == code   (exact, char-for-char)

emit_html(tokens: list[tuple[str | None, str]], emphasized_lines: frozenset[int]) -> str
    # escapes each token text exactly once; wraps classed tokens; honors line/inline mode.

highlight_code(code: str, lang_tag: str | None, emphasized_lines: frozenset[int]) -> tuple[str, bool, str | None]
    # convenience used by markdown_render: returns (content_html, recognized, canonical_lang).
```

## Token vocabulary (CLOSED — never author-derived)

| kind / class | color | role |
|---|---|---|
| `tok-comment` | `#66756F` (italic) | line/block comments |
| `tok-keyword` | `#34E6A0` | keywords, control flow |
| `tok-string` | `#E7D2A6` | string/char literals (incl. multi-line) |
| `tok-number` | `#b388ff` | numeric literals |
| `tok-function` | `#7DF0C2` | function/method names |
| `tok-type` | `#ffd166` | types, classes, annotations |
| `tok-builtin` | `#46a8e0` | builtins, constants (`true/false/null/None`) |
| `tok-operator` | `#9FB0AA` | operators/punctuation (subtle) |
| `tok-tag` | `#34E6A0` | markup element tags |
| `tok-attr` | `#ffd166` | markup attributes, data keys |
| `tok-meta` | `#9FB0AA` | decorators, preprocessor, shebang |

Plain text (kind `None`) carries no span and inherits the `<pre>` color (`#9FE9C8`) — so a fallback block looks identical to today.

## Scanner contract

- Each language = an **ordered** `list[(kind, regex)]` compiled (once, at import) into one master `(?P<kind>…)|…` pattern; **first** alternative to match at a position wins.
- At position `pos`: `m = master.match(code, pos)`; if `m`, emit `(class_for(m.lastgroup, m.group()), m.group())`, `pos = m.end()`; else emit `(None, code[pos])`, `pos += 1`.
- **Identifiers**: one `name` rule matches `[A-Za-z_][A-Za-z0-9_]*` (language-appropriate); the matched text is post-classified: in `KEYWORDS` → `tok-keyword`; in `TYPES` → `tok-type`; in `BUILTINS` → `tok-builtin`; followed by `(` (function call/def context) → `tok-function`; else plain.
- A rule may span newlines (block comment, triple-quoted string) — allowed; emission splits such tokens across line boxes when line-emphasis is active.

## emit_html contract

- Escape each token text with `html.escape(text, quote=False)` — **exactly once**.
- Classed token → `<span class="{kind}">{escaped}</span>`; plain token → `{escaped}`.
- `emphasized_lines` empty → **inline mode**: tokens joined; newlines stay literal `\n` (copy-friendly, today's flow).
- `emphasized_lines` non-empty → **line mode**: split the token stream at `\n` into lines; each line = `<span class="cl{ cl--hl if (1-based index) in emphasized_lines}">{line spans}</span>` with **no** literal `\n` between line spans (a trailing empty line/blank source line → an empty `<span class="cl"></span>`).

## Languages + aliases

Full tokenizers: **kotlin, java, python, bash**. Lighter tokenizers: **json, yaml, markup (xml/html), javascript, typescript, sql**. Aliases (case-insensitive): `kt`/`kts`→kotlin · `py`/`python3`→python · `sh`/`shell`/`zsh`/`console`/`shell-session`→bash · `js`/`jsx`→javascript · `ts`/`tsx`→typescript · `yml`→yaml · `html`/`xhtml`/`svg`/`xml`→markup. Unmapped tag → `resolve_lang` returns `None` → escape-only fallback (never an error).

## Invariants (test- + verifier-enforced)

1. **V-HL1**: `"".join(text for _c,text in tokenize(code,lang)[0]) == code` for every language and the fallback (total coverage; no char lost/duplicated).
2. **V-HL2**: `emit_html` output contains only `<span class="…">`/`</span>` markup (token spans + `cl`/`cl--hl` line spans) plus HTML-escaped text — no other tags, ever.
3. **V-HL3**: every emitted class name ∈ the 11 `tok-*` vocabulary ∪ {`cl`,`cl--hl`}; none derived from author text.
4. **V-HL4**: code containing `<`, `>`, `&`, `"`, `{{TOKEN}}`, `</span>`, `</pre>` renders as inert escaped text — no markup breakout, no token-substitution injection.
5. **V-HL5**: an unknown/`None` language → `recognized is False`, **zero** `tok-` spans, code present and escaped.
6. **V-HL6**: `tokenize`/`emit_html`/`highlight_code` are pure & deterministic — identical inputs → byte-identical output (no `today()`/network/randomness; ordered regex).
7. **V-HL7**: with line-emphasis, exactly the requested 1-based lines carry `cl--hl`; concatenating the line texts (sans spans) reproduces the source.
