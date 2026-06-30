"""Unit tests for the Atom feed builder (scripts/blog/feed.py).

BUG-010: each entry's <id>/<link> must use the post canonical (honoring a frontmatter
`canonical:` override), consistent with og:url / JSON-LD url. Stdlib only.
"""
import datetime as dt
import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from blog import feed, config  # noqa: E402


def _post(slug="x", canonical=None):
    url = f"/blog/{slug}/"
    return SimpleNamespace(
        url=url, slug=slug,
        canonical=canonical or config.abs_url("https://site.test/", url),
        title="T", date=dt.date(2026, 1, 2), updated=dt.date(2026, 1, 2),
        excerpt="E", tags=[],
    )


class TestFeedCanonical(unittest.TestCase):
    def test_entry_uses_canonical_override(self):
        xml = feed.build_feed([_post(canonical="https://external.example/post")], "https://site.test/")
        self.assertIn("<id>https://external.example/post</id>", xml)
        self.assertIn('href="https://external.example/post"', xml)

    def test_entry_default_canonical(self):
        xml = feed.build_feed([_post()], "https://site.test/")
        self.assertIn("<id>https://site.test/blog/x/</id>", xml)


if __name__ == "__main__":
    unittest.main()
