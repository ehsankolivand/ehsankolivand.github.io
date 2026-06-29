"""Unit tests for content loading/validation (scripts/blog/content.py).

Focused on fail-loud frontmatter validation that must name the offending file rather than
dying on a bare Python traceback (Constitution: fail loud with a file-identifying message).
Stdlib only (tempfile + unittest).
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from blog import content  # noqa: E402
from blog.content import Category, ContentError  # noqa: E402

CATS = [Category(name="Tooling", label="Tooling", palette="mint")]
_FM = "---\ntitle: T\ndate: 2026-01-01\ncategory: Tooling\nexcerpt: E\n{extra}---\nBody text.\n"


def _load(extra: str):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "my-post.md"
        p.write_text(_FM.format(extra=extra), encoding="utf-8")
        return content.load_post(p, CATS, "https://example.com/")


class TestTagsValidation(unittest.TestCase):
    def test_int_scalar_raises_file_identifying_error(self):
        # BUG-005: `tags: 5` used to crash with `TypeError: 'int' object is not iterable`.
        with self.assertRaises(ContentError) as cm:
            _load("tags: 5\n")
        msg = str(cm.exception)
        self.assertIn("tags", msg)
        self.assertIn("my-post.md", msg)   # file-identifying

    def test_bool_scalar_raises(self):
        with self.assertRaises(ContentError):
            _load("tags: true\n")

    def test_list_tags_ok(self):
        self.assertEqual(_load("tags: [compose, ui]\n").tags, ["compose", "ui"])

    def test_comma_string_tags_ok(self):
        self.assertEqual(_load('tags: "a, b ,c"\n').tags, ["a", "b", "c"])

    def test_absent_tags_ok(self):
        self.assertEqual(_load("").tags, [])


if __name__ == "__main__":
    unittest.main()
