"""Unit tests for the in-house Markdown renderer (scripts/blog/markdown_render.py).

The security-sensitive renderer's first isolated test coverage (feature 004): HTML escaping,
the URL-scheme allow-list, token-injection resistance, inline markup, nested lists, GFM table
edge cases, fenced code + highlighting + filename + line-emphasis + fallback, callouts, footnotes,
and heading-anchor determinism. Stdlib unittest only. (FR-004, FR-007..FR-019; contract V-* ids.)
"""
import html
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from blog import markdown_render as M  # noqa: E402


def _img(src, alt):
    return ("/blog/assets/media/" + src.lstrip("./"), 800, 600)


def render(md):
    return M.render(md, _img)


class TestEscaping(unittest.TestCase):
    def test_paragraph_escapes_html(self):
        out = render("a < b & c > d")
        self.assertIn("a &lt; b &amp; c &gt; d", out)
        self.assertNotIn("&amp;lt;", out)  # escaped exactly once

    def test_raw_html_is_escaped_not_passed_through(self):
        out = render("<script>alert(1)</script>")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_code_block_escapes(self):
        out = render("```\n<a> & </b>\n```")
        self.assertIn("&lt;a&gt;", out)
        self.assertIn("&amp;", out)
        self.assertNotIn("<a>", out)


class TestUrlAllowList(unittest.TestCase):
    def test_javascript_url_neutralized(self):
        out = render("[x](javascript:alert(1))")
        self.assertNotIn("javascript:", out)
        self.assertNotIn("<a ", out)        # link dropped, label kept
        self.assertIn("x", out)

    def test_data_url_neutralized(self):
        out = render("[x](data:text/html,<script>)")
        self.assertNotIn('href="data:', out)

    def test_control_char_scheme_bypass_neutralized(self):
        out = render("[x](\x01javascript:alert(1))")
        self.assertNotIn("javascript:alert", out.replace("\x01", ""))
        self.assertNotIn("<a ", out)

    def test_embedded_control_char_scheme_bypass_neutralized(self):
        # BUG-004: a non-whitespace C0 control embedded *inside* the scheme (NUL, SOH, DEL —
        # the controls the link parser's [^)\s]+ does NOT swallow, so they reach the classifier)
        # must not let `java\x00script:` slip through as a "schemeless" (safe) URL.
        for ctrl in ("\x00", "\x01", "\x7f"):
            payload = f"java{ctrl}script:alert(1)"
            self.assertFalse(M._is_safe_url(payload), repr(payload))   # classifier rejects it
            out = render(f"[x]({payload})")
            self.assertNotIn("<a ", out, repr(payload))               # link dropped, label kept
            self.assertNotIn(ctrl, out)                                # no raw control char emitted
            self.assertIn("x", out)

    def test_vbscript_neutralized(self):
        self.assertNotIn("<a ", render("[x](vbscript:msgbox(1))"))

    def test_safe_urls_kept(self):
        for url in ("https://example.com", "http://x.io/p", "mailto:a@b.com", "/blog/x/", "#anchor"):
            out = render(f"[x]({url})")
            self.assertIn(f'href="{html.escape(url, quote=True)}"', out, url)


class TestTokenInjection(unittest.TestCase):
    def test_token_literal_in_paragraph(self):
        out = render("a {{BODY}} b {{CAPTION}} c")
        self.assertIn("{{BODY}}", out)
        self.assertIn("{{CAPTION}}", out)

    def test_token_literal_in_code_fallback(self):
        self.assertIn("{{BODY}}", render("```\n{{BODY}}\n```"))

    def test_token_literal_in_callout_and_cell(self):
        self.assertIn("{{BODY}}", render("> [!note] t\n> {{BODY}}"))
        self.assertIn("{{BODY}}", render("| h |\n|---|\n| {{BODY}} |"))


class TestInline(unittest.TestCase):
    def test_bold_italic_code(self):
        out = render("**b** _i_ `c` ***bi***")
        self.assertIn("<strong", out)
        self.assertIn("<em>", out)
        self.assertIn("<code", out)

    def test_link_with_emphasis_label(self):
        out = render("[**bold**](https://x.io)")
        self.assertIn('href="https://x.io"', out)
        self.assertIn("<strong", out)

    def test_inline_image_resolves(self):
        out = render("text ![alt](pic.png) more")
        self.assertIn("/blog/assets/media/pic.png", out)
        self.assertIn('alt="alt"', out)

    def test_autolink(self):
        self.assertIn('href="https://x.io"', render("see <https://x.io>"))


class TestLists(unittest.TestCase):
    def test_unordered_and_ordered(self):
        self.assertIn("<ul", render("- a\n- b"))
        self.assertIn("<ol", render("1. a\n2. b"))

    def test_marker_switch_splits_runs(self):
        out = render("- a\n1. b")  # BUG-034: ul then ol
        self.assertIn("<ul", out)
        self.assertIn("<ol", out)

    def test_nested_indentation(self):
        out = render("- a\n    - b\n    - c")
        self.assertGreaterEqual(out.count("<ul"), 2)  # nested list


class TestTables(unittest.TestCase):
    def test_alignment(self):
        out = render("| L | C | R |\n|:--|:-:|--:|\n| 1 | 2 | 3 |")
        self.assertIn("text-align:left", out)
        self.assertIn("text-align:center", out)
        self.assertIn("text-align:right", out)

    def test_empty_cell_and_inline_markup(self):
        out = render("| a | b |\n|---|---|\n| `x` | |")
        self.assertIn("<code", out)            # inline code in a cell
        self.assertIn("<td", out)

    def test_escaped_pipe(self):
        out = render("| a | b |\n|---|---|\n| x \\| y | z |")
        self.assertIn("x | y", out)            # escaped pipe is literal, not a column split

    def test_ragged_rows(self):
        out = render("| a | b |\n|---|---|\n| 1 |\n| 1 | 2 | 3 |")
        # short row -> still well-formed; long row -> extra cell dropped (header count)
        self.assertEqual(out.count("<tr>"), 3)  # header + 2 body rows

    def test_single_column(self):
        out = render("| H |\n|---|\n| v |")
        self.assertIn("<table", out)
        self.assertIn(">v<", out.replace(" ", ""))

    def test_class_hook(self):
        self.assertIn('class="mdtable"', render("| a |\n|---|\n| 1 |"))

    def test_pipe_paragraph_above_dashes_is_not_a_table(self):
        # BUG-003: a paragraph containing `|` directly above a `---` thematic break has a
        # header/delimiter cell-count mismatch (2 vs 1), so it must NOT become a 1-column
        # table; the prose stays a paragraph and the rule does not silently disappear.
        out = render("Use the a | b operator here.\n---\n\nNext para.")
        self.assertNotIn("<table", out)
        self.assertIn("Use the a", out)
        self.assertIn("Next para.", out)

    def test_borderless_table_with_matching_delimiter_still_recognized(self):
        # Guard against over-correcting BUG-003: a borderless table (header 2 == delimiter 2).
        out = render("a | b\n--- | ---\n1 | 2")
        self.assertIn("<table", out)
        self.assertIn(">1<", out.replace(" ", ""))


class TestCodeBlocks(unittest.TestCase):
    def test_highlight_known_language(self):
        out = render("```python\ndef f():\n    return 1\n```")
        self.assertIn("tok-keyword", out)

    def test_unknown_language_fallback(self):
        out = render("```nope\nx<y\n```")
        self.assertNotIn("tok-", out)
        self.assertIn("x&lt;y", out)

    def test_filename_label(self):
        out = render('```python title="app/main.py"\nx = 1\n```')
        self.assertIn("app/main.py", out)

    def test_line_emphasis(self):
        out = render("```python {2}\na = 1\nb = 2\nc = 3\n```")
        self.assertEqual(out.count("cl--hl"), 1)
        self.assertIn("cl--hl", out)

    def test_legacy_caption_preserved(self):
        out = render("```// build.gradle.kts\nplugins {}\n```")
        self.assertIn("// build.gradle.kts", out)
        self.assertNotIn("tok-", out)  # not a language -> no highlighting

    def test_plain_fence_escape_only(self):
        out = render("```\n<x>\n```")
        self.assertIn("&lt;x&gt;", out)
        self.assertNotIn("tok-", out)

    def test_copy_fidelity_inline_mode(self):
        code = "a = 1\nb = 2"
        out = render(f"```python\n{code}\n```")
        pre = re.search(r"<pre[^>]*>(.*?)</pre>", out, re.S).group(1)
        self.assertEqual(html.unescape(re.sub(r"<[^>]+>", "", pre)), code)


class TestParseInfoString(unittest.TestCase):
    def test_language_only(self):
        self.assertEqual(M.parse_info_string("python"), ("python", None, frozenset(), None))

    def test_filename_and_lines(self):
        lang, fn, em, cap = M.parse_info_string('kotlin title="A.kt" {2,4-5}')
        self.assertEqual((lang, fn, cap), ("kotlin", "A.kt", None))
        self.assertEqual(em, frozenset({2, 4, 5}))

    def test_legacy_caption(self):
        self.assertEqual(M.parse_info_string("// a caption"), (None, None, frozenset(), "// a caption"))

    def test_empty(self):
        self.assertEqual(M.parse_info_string(""), (None, None, frozenset(), None))


class TestCallouts(unittest.TestCase):
    def test_known_kind(self):
        out = render("> [!warning] Heads up\n> Be careful.")
        self.assertIn('class="callout callout--warning"', out)
        self.assertIn('role="note"', out)
        self.assertIn("Heads up", out)
        self.assertIn("Be careful.", out)

    def test_synonym_maps_to_canonical(self):
        self.assertIn("callout--tip", render("> [!success] Nice\n> body"))
        self.assertIn("callout--caution", render("> [!danger] X\n> body"))

    def test_unknown_kind_degrades_to_note(self):
        self.assertIn("callout--note", render("> [!bogus] X\n> body"))

    def test_plain_blockquote_not_a_callout(self):
        out = render("> just a quote")
        self.assertNotIn("callout", out)
        self.assertIn("pquote", out)  # refined blockquote class

    def test_callout_body_inline_markup(self):
        out = render("> [!note] t\n> see **bold** and `code`")
        self.assertIn("<strong", out)
        self.assertIn("<code", out)


class TestFootnotes(unittest.TestCase):
    def test_defined_reference(self):
        out = render("Claim.[^1]\n\n[^1]: The supporting note.")
        self.assertIn('class="fnref"', out)
        self.assertIn('id="fnref-1"', out)
        self.assertIn('id="fn-1"', out)
        self.assertIn('href="#fn-1"', out)
        self.assertIn("The supporting note.", out)
        self.assertIn('class="fn-back"', out)
        self.assertIn('role="doc-endnotes"', out)

    def test_undefined_reference_is_literal(self):
        out = render("No def here.[^x]")
        self.assertIn("[^x]", out)
        self.assertNotIn('href="#fn-x"', out)  # no dangling anchor

    def test_unreferenced_definition_omitted(self):
        out = render("Body with no ref.\n\n[^1]: orphan note.")
        self.assertNotIn("doc-endnotes", out)

    def test_duplicate_reference_unique_ids(self):
        out = render("A[^1] then B[^1].\n\n[^1]: note")
        self.assertIn('id="fnref-1"', out)
        self.assertIn('id="fnref-1-2"', out)

    def test_named_id_and_numbering_by_reference_order(self):
        out = render("First[^b] second[^a].\n\n[^a]: A\n[^b]: B")
        # numbering follows reference order: ^b is 1, ^a is 2
        self.assertRegex(out, r'href="#fn-b"[^>]*>1<')
        self.assertRegex(out, r'href="#fn-a"[^>]*>2<')

    def test_footnote_in_code_is_literal(self):
        out = render("```\n[^1]: not a def\n```\n\nx")
        self.assertIn("[^1]: not a def", out)  # untouched inside the code fence

    def test_deterministic(self):
        md = "X[^1] Y[^2].\n\n[^1]: one\n[^2]: two"
        self.assertEqual(render(md), render(md))


class TestHeadingAnchors(unittest.TestCase):
    def test_slug_determinism(self):
        out = render("## Hello World")
        self.assertIn('id="hello-world"', out)

    def test_uniqueness_suffix(self):
        out = render("## Dup\n\ntext\n\n## Dup")
        self.assertIn('id="dup"', out)
        self.assertIn('id="dup-1"', out)

    def test_symbol_only_fallback(self):
        out = render("## +++")
        self.assertRegexpMatches(out, r'id="section-\d+"') if hasattr(self, "assertRegexpMatches") \
            else self.assertRegex(out, r'id="section-\d+"')

    def test_no_h1_in_body(self):
        self.assertNotIn("<h1", render("# Top heading\n\nbody"))

    def test_footnote_id_vs_heading_id_no_collision(self):
        out = render("## Fn 1\n\nText[^1].\n\n[^1]: note")
        ids = re.findall(r'id="([^"]+)"', out)
        self.assertEqual(len(ids), len(set(ids)), f"duplicate ids: {ids}")


if __name__ == "__main__":
    unittest.main()
