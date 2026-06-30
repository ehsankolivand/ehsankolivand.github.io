"""Unit tests for the build verifier's unresolved-template-token scan (scripts/verify_build.py).

BUG-011: the scan must flag a genuinely-unfilled design slot (e.g. `{{TITLE}}`) and the bundle's
`<sc-if>`/`<sc-for>` runtime directives, but must NOT flag legitimate author interpolation content
(`{{user}}`, `{{count}}`, `{{ctx.value}}`) that the renderer intentionally preserves verbatim.
Stdlib only.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import verify_build as V  # noqa: E402


class TestTokenScan(unittest.TestCase):
    def test_real_template_slot_is_flagged(self):
        # These slots really exist in templates/blog/**, so an unfilled one is a DoD failure.
        self.assertTrue(V._TEMPLATE_TOKENS, "expected a non-empty template-token vocabulary")
        self.assertIn("TITLE", V._TEMPLATE_TOKENS)
        self.assertTrue(V.TOKEN_RE.search("<h1>{{TITLE}}</h1>"))
        self.assertTrue(V.TOKEN_RE.search("{{BODY}}"))

    def test_author_interpolation_is_not_flagged(self):
        for s in ("{{user}}", "{{count}}", "{{ msg }}", "{{ctx.value}}", "{{i18nKey}}", "a {{x}} b"):
            self.assertIsNone(V.TOKEN_RE.search(s), s)

    def test_sc_runtime_directive_is_flagged(self):
        self.assertTrue(V.TOKEN_RE.search('<sc-if cond="x">'))
        self.assertTrue(V.TOKEN_RE.search("<sc-for item>"))


if __name__ == "__main__":
    unittest.main()
