"""Unit tests for SEO/JSON-LD head construction (scripts/blog/seo.py).

Focused on the one escaping context json.dumps does not cover: embedding JSON-LD inside a
`<script>` element. Author-controlled strings (post title/excerpt/tags) must not be able to
break out of the script block with `</script>` / `<!--` / `<script` (BUG-001). Stdlib only.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from blog import seo  # noqa: E402

_OPEN = '<script type="application/ld+json">'
_CLOSE = "</script>"


class TestJsonLdScriptSafety(unittest.TestCase):
    def _inner(self, html_str):
        self.assertTrue(html_str.startswith(_OPEN))
        self.assertTrue(html_str.endswith(_CLOSE))
        return html_str[len(_OPEN):-len(_CLOSE)]

    def test_no_script_breakout(self):
        hostile = "Escaping </script> and <!-- and <script> & ampersand"
        out = seo._jsonld({"headline": hostile})
        # exactly one opening + one closing tag: no early termination
        self.assertEqual(out.count("<script"), 1)
        self.assertEqual(out.count("</script>"), 1)
        inner = self._inner(out)
        # no raw `<` survives in the payload -> no </script>, <!--, or <script can break out
        self.assertNotIn("<", inner)
        self.assertNotIn(">", inner)
        # still valid JSON that round-trips to the exact original text
        self.assertEqual(json.loads(inner)["headline"], hostile)

    def test_ampersand_and_unicode_round_trip(self):
        obj = {"description": "fintech, banking & crypto — seven years"}
        inner = self._inner(seo._jsonld(obj))
        self.assertNotIn("&", inner)               # escaped to &
        self.assertEqual(json.loads(inner), obj)   # decodes back losslessly (incl. the em dash)

    def test_plain_content_unaffected(self):
        inner = self._inner(seo._jsonld({"k": "List of T, no specials"}))
        self.assertEqual(json.loads(inner), {"k": "List of T, no specials"})


if __name__ == "__main__":
    unittest.main()
