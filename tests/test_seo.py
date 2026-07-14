"""Unit tests for SEO/JSON-LD head construction (scripts/blog/seo.py).

Focused on the one escaping context json.dumps does not cover: embedding JSON-LD inside a
`<script>` element. Author-controlled strings (post title/excerpt/tags) must not be able to
break out of the script block with `</script>` / `<!--` / `<script` (BUG-001). Stdlib only.
"""
import datetime
import json
import os
import re
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from blog import config, seo  # noqa: E402


def _post(image="", kind="code", src="", alt="", title="A Post"):
    return SimpleNamespace(
        image=image, title=title,
        cover=SimpleNamespace(kind=kind, src=src, alt=alt, width=1200, height=630),
    )

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


class TestPostImage(unittest.TestCase):
    def test_absolute_image_url_passes_through(self):
        # BUG-002: an absolute image: must NOT be run through media_url (which would mangle it
        # into /blog/assets/media/https://...).
        url, w, h, alt = seo._post_image(_post(image="https://cdn.example.com/x.png"), "https://site/")
        self.assertEqual(url, "https://cdn.example.com/x.png")
        self.assertEqual((w, h), (1200, 630))

    def test_relative_image_maps_to_media(self):
        url, *_ = seo._post_image(_post(image="assets/pic.png"), "https://site/")
        self.assertEqual(url, "https://site/blog/assets/media/pic.png")

    def test_no_image_uses_site_default(self):
        url, *_ = seo._post_image(_post(), "https://site/")
        self.assertTrue(url.endswith("/og-image.png"))


def _full_post(base_url="https://ehsankolivand.github.io/"):
    """A complete fake Post sufficient for head_for_post() (feature 006 per-post graph test)."""
    d = datetime.date(2026, 7, 1)
    return SimpleNamespace(
        title="A Post Title", excerpt="A concise excerpt.", og_description="A concise excerpt.",
        canonical=base_url + "blog/a-post-title/", tags=["kotlin", "compose"],
        date=d, updated=d, word_count=800, read_minutes=4, image="",
        cover=SimpleNamespace(kind="code", src="", alt="", width=1200, height=630),
    )


class TestPostEntityGraph(unittest.TestCase):
    """Feature 006: every post carries the unified single-entity graph — a WebSite node keyed to
    the canonical #website with a #person publisher — WITHOUT displacing BlogPosting as the first
    ld+json script the verifier reads (contract C2)."""

    def _blocks(self, html_str):
        return [json.loads(b) for b in
                re.findall(r'<script type="application/ld\+json">(.*?)</script>', html_str, re.S)]

    def test_blogposting_is_first_script(self):
        head = seo.head_for_post(_full_post(), "https://ehsankolivand.github.io/", "Compose")
        blocks = self._blocks(head)
        self.assertGreaterEqual(len(blocks), 3)
        self.assertEqual(blocks[0].get("@type"), "BlogPosting")  # verifier reads the first script

    def test_website_node_present_and_unified(self):
        head = seo.head_for_post(_full_post(), "https://ehsankolivand.github.io/", "Compose")
        blocks = self._blocks(head)
        website = next((b for b in blocks if b.get("@type") == "WebSite"), None)
        self.assertIsNotNone(website, "post is missing the WebSite JSON-LD node")
        self.assertEqual(website["@id"], config.WEBSITE_ID)
        self.assertEqual(website["publisher"]["@id"], config.PERSON_ID)

    def test_author_and_website_share_person_identity(self):
        head = seo.head_for_post(_full_post(), "https://ehsankolivand.github.io/", "Compose")
        blocks = self._blocks(head)
        blogposting = blocks[0]
        website = next(b for b in blocks if b.get("@type") == "WebSite")
        # one Person across author + publisher across both nodes = a single unified entity
        self.assertEqual(blogposting["author"]["@id"], config.PERSON_ID)
        self.assertEqual(website["publisher"]["@id"], config.PERSON_ID)

    def test_all_ld_json_blocks_are_valid(self):
        # every emitted JSON-LD block parses (no breakout / no malformed graph)
        head = seo.head_for_post(_full_post(), "https://ehsankolivand.github.io/", "Compose")
        types = [b.get("@type") for b in self._blocks(head)]
        self.assertEqual(types, ["BlogPosting", "BreadcrumbList", "WebSite"])


if __name__ == "__main__":
    unittest.main()
