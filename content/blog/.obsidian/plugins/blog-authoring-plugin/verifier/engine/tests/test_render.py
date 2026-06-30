"""Unit tests for template rendering helpers (scripts/blog/render.py).

BUG-016: the static category nav href must percent-encode the category name so it matches
the hash blog.js writes/reads via encode/decodeURIComponent; `data-cat` keeps the raw name.
Stdlib only.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from blog import render  # noqa: E402
from blog.content import Category  # noqa: E402


class TestNavCategoryEncoding(unittest.TestCase):
    def test_multiword_category_href_is_percent_encoded(self):
        nav = render.render_nav([Category(name="Server Driven", label="Server Driven", palette="mint")])
        self.assertIn("#cat=Server%20Driven", nav)        # href matches encodeURIComponent
        self.assertIn('data-cat="Server Driven"', nav)    # data-cat stays the raw name
        self.assertNotIn("#cat=Server Driven", nav)        # the raw (broken) form is gone

    def test_special_char_category_encoded(self):
        nav = render.render_nav([Category(name="A&B", label="A&B", palette="mint")])
        self.assertIn("#cat=A%26B", nav)

    def test_simple_category_unchanged(self):
        nav = render.render_nav([Category(name="Compose", label="Compose", palette="mint")])
        self.assertIn("#cat=Compose", nav)


if __name__ == "__main__":
    unittest.main()
