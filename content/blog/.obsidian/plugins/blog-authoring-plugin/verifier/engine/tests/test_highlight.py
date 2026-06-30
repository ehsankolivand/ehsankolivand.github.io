"""Unit tests for the vendored syntax highlighter (scripts/blog/highlight.py).

Covers: total coverage (no char lost), per-language tokenization, the escape-only fallback,
HTML escaping / breakout resistance, determinism, alias resolution, and line-emphasis emission.
Stdlib unittest only. (FR-001..FR-006, FR-019; contract invariants V-HL1..V-HL7.)
"""
import html
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from blog import highlight as H  # noqa: E402

SAMPLES = {
    "kotlin": 'fun main() {\n    val x = "hi" // c\n    println(x)\n}',
    "java": 'class A {\n    int x = 0xFF; // hex\n    String s = "y";\n}',
    "python": 'def f(a):\n    """doc"""\n    return [i for i in range(a)]  # ok',
    "bash": 'sudo ./install.sh --token <TOK>\nexport X="$HOME/bin"  # note',
    "json": '{"a": 1, "b": [true, null], "c": "x"}',
    "yaml": "name: demo\nlist:\n  - a\n  - b  # c",
    "markup": '<div class="a" id=x>hi</div><!-- c -->',
    "javascript": 'const f = (x) => `t${x}`; // c\nlet n = 1.5;',
    "typescript": 'interface P { id: number }\nconst f = (x: string): void => {};',
    "sql": "SELECT id, name FROM users WHERE id = 1; -- c",
}


class TestCoverage(unittest.TestCase):
    def test_total_coverage_every_language(self):
        """V-HL1: concatenating token texts reproduces the source exactly (no char lost/dup)."""
        for lang, code in SAMPLES.items():
            toks, recognized = H.tokenize(code, H.resolve_lang(lang))
            self.assertTrue(recognized, lang)
            self.assertEqual("".join(t for _c, t in toks), code, f"coverage broke for {lang}")

    def test_coverage_with_tricky_chars(self):
        tricky = 'a<b && c>d "x\\ny" /* */ #!end {{T}}'
        for lang in SAMPLES:
            toks, _ = H.tokenize(tricky, H.resolve_lang(lang))
            self.assertEqual("".join(t for _c, t in toks), tricky, lang)

    def test_empty_code(self):
        toks, recognized = H.tokenize("", "python")
        self.assertEqual(toks, [])
        self.assertTrue(recognized)


class TestClassification(unittest.TestCase):
    def _classes(self, lang, code):
        toks, _ = H.tokenize(code, H.resolve_lang(lang))
        return {c for c, _t in toks if c}

    def test_python_tokens(self):
        cls = self._classes("python", SAMPLES["python"])
        self.assertIn("tok-keyword", cls)   # def/return/for/in
        self.assertIn("tok-comment", cls)   # # ok
        self.assertIn("tok-string", cls)    # """doc"""

    def test_kotlin_tokens(self):
        cls = self._classes("kotlin", SAMPLES["kotlin"])
        self.assertIn("tok-keyword", cls)   # fun/val
        self.assertIn("tok-string", cls)
        self.assertIn("tok-comment", cls)

    def test_json_keys_vs_values(self):
        toks, _ = H.tokenize(SAMPLES["json"], "json")
        self.assertIn("tok-attr", {c for c, _t in toks})      # "a"/"b"/"c" keys
        self.assertIn("tok-builtin", {c for c, _t in toks})   # true/null

    def test_sql_case_insensitive_keywords(self):
        upper = {c for c, _t in H.tokenize("SELECT * FROM t", "sql")[0]}
        lower = {c for c, _t in H.tokenize("select * from t", "sql")[0]}
        self.assertIn("tok-keyword", upper)
        self.assertIn("tok-keyword", lower)


class TestFallback(unittest.TestCase):
    def test_unknown_language_escape_only(self):
        """V-HL5: unknown language -> recognized False, single plain token, zero tok- spans."""
        code = 'whatever <x> & {{Y}}'
        toks, recognized = H.tokenize(code, H.resolve_lang("xyzlang"))
        self.assertFalse(recognized)
        self.assertEqual(toks, [(None, code)])
        out, rec, lang = H.highlight_code(code, "xyzlang")
        self.assertFalse(rec)
        self.assertIsNone(lang)
        self.assertNotIn("tok-", out)
        self.assertIn("&lt;x&gt;", out)
        self.assertIn("&amp;", out)

    def test_none_language(self):
        toks, recognized = H.tokenize("plain text", None)
        self.assertFalse(recognized)
        self.assertEqual(toks, [(None, "plain text")])


class TestSecurity(unittest.TestCase):
    def test_escaped_exactly_once(self):
        """V-HL4: <,>,& escaped once; no double-escape."""
        out, _r, _l = H.highlight_code("a < b & c > d", "python")
        self.assertIn("&lt;", out)
        self.assertIn("&amp;", out)
        self.assertIn("&gt;", out)
        self.assertNotIn("&amp;lt;", out)  # not double-escaped

    def test_no_markup_breakout(self):
        """V-HL2/V-HL4: author </span>, </pre>, < become inert escaped text."""
        out, _r, _l = H.highlight_code('x = "</span></pre><script>"', "python")
        self.assertNotIn("</script>", out)
        self.assertIn("&lt;/span&gt;", out)
        self.assertIn("&lt;script&gt;", out)
        # the ONLY tags present are our span tags
        for tag in re.findall(r"</?([a-zA-Z]+)", out):
            self.assertEqual(tag, "span")

    def test_token_injection_inert(self):
        """{{TOKEN}} in code cannot survive as an adjacent {{...}} pair sub_tokens would match."""
        out, _r, _l = H.highlight_code("y = {{BODY}}", "python")
        self.assertFalse(re.search(r"\{\{[A-Za-z_]\w*\}\}", out),
                         "an intact {{TOKEN}} pair leaked into highlighted output")
        # fallback path keeps it literal (single-pass substitution makes it safe downstream)
        out2, _r2, _l2 = H.highlight_code("{{BODY}}", "xyzlang")
        self.assertEqual(out2, "{{BODY}}")

    def test_only_closed_class_vocabulary(self):
        """V-HL3: every emitted class is in the fixed vocabulary."""
        allowed = set(H.TOKEN_CLASSES) | {"cl", "cl--hl"}
        for lang, code in SAMPLES.items():
            out = H.emit_html(H.tokenize(code, H.resolve_lang(lang))[0], frozenset({1, 2}))
            for cls in re.findall(r'class="([^"]+)"', out):
                for token in cls.split():
                    self.assertIn(token, allowed, f"{lang}: unexpected class {token}")


class TestDeterminism(unittest.TestCase):
    def test_tokenize_is_pure(self):
        """V-HL6: identical inputs -> identical output."""
        for lang, code in SAMPLES.items():
            a = H.highlight_code(code, lang, frozenset({1}))
            b = H.highlight_code(code, lang, frozenset({1}))
            self.assertEqual(a, b, lang)


class TestEmit(unittest.TestCase):
    def test_inline_mode_preserves_newlines_and_copy(self):
        code = "a = 1\nb = 2"
        out = H.emit_html(H.tokenize(code, "python")[0], frozenset())
        self.assertNotIn('class="cl"', out)              # no line wrappers in inline mode
        recovered = html.unescape(re.sub(r"<[^>]+>", "", out))
        self.assertEqual(recovered, code)                # copy fidelity

    def test_line_mode_emphasis(self):
        """V-HL7: requested lines get cl--hl; line texts reconstruct the source."""
        code = "a\nb\nc"
        out = H.emit_html(H.tokenize(code, "python")[0], frozenset({2}))
        self.assertEqual(out.count('class="cl"'), 2)     # lines 1 and 3 (line 2 is "cl cl--hl")
        self.assertEqual(out.count("cl--hl"), 1)         # line 2
        lines = re.findall(r'<span class="cl[^"]*">(.*?)</span>', out)
        recovered = "\n".join(html.unescape(re.sub(r"<[^>]+>", "", ln)) for ln in lines)
        self.assertEqual(recovered, code)

    def test_blank_line_preserved_in_line_mode(self):
        code = "a\n\nc"
        out = H.emit_html(H.tokenize(code, "python")[0], frozenset({1}))
        self.assertEqual(out.count('class="cl'), 3)      # three line boxes incl. the blank


class TestAliases(unittest.TestCase):
    def test_aliases(self):
        cases = {
            "kt": "kotlin", "kts": "kotlin", "py": "python", "PYTHON": "python",
            "sh": "bash", "Shell": "bash", "zsh": "bash", "js": "javascript",
            "ts": "typescript", "yml": "yaml", "html": "markup", "XML": "markup",
        }
        for tag, canon in cases.items():
            self.assertEqual(H.resolve_lang(tag), canon, tag)

    def test_unknown_and_empty(self):
        self.assertIsNone(H.resolve_lang("brainfuck"))
        self.assertIsNone(H.resolve_lang(""))
        self.assertIsNone(H.resolve_lang(None))


if __name__ == "__main__":
    unittest.main()
