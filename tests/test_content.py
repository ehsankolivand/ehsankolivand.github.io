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


class TestExtractRelated(unittest.TestCase):
    def test_trailing_rule_with_no_related_block_is_preserved(self):
        # BUG-007: a post ending in a bare `---` with no related block keeps it in the body.
        body, slugs = content.extract_related("Para one.\n\nPara two.\n\n---\n")
        self.assertIn("---", body)
        self.assertEqual(slugs, [])

    def test_related_block_with_separator_delimiter_is_extracted(self):
        body, slugs = content.extract_related("Body text.\n\n---\n\n- [[post-a]]\n- [[post-b]]\n")
        self.assertEqual(slugs, ["post-a", "post-b"])
        self.assertNotIn("post-a", body)
        self.assertNotIn("---", body)   # the delimiter separator is consumed with the block

    def test_related_heading_block_is_extracted(self):
        body, slugs = content.extract_related("Body text.\n\n## Related\n- [[x]]\n")
        self.assertEqual(slugs, ["x"])
        self.assertNotIn("Related", body)


class TestImageValidation(unittest.TestCase):
    def test_missing_relative_image_fails_loud(self):
        # BUG-002: a code-cover post with a content-relative image: that doesn't exist must fail
        # the build (no silent 404 og:image) with a file-identifying message.
        with self.assertRaises(ContentError) as cm:
            _load("image: assets/definitely-missing.png\n")
        msg = str(cm.exception)
        self.assertIn("my-post.md", msg)
        self.assertIn("definitely-missing.png", msg)

    def test_absolute_image_url_is_allowed(self):
        # An absolute http(s) image: is a valid override and is NOT validated as a local file.
        post = _load("image: https://cdn.example.com/social.png\n")
        self.assertEqual(post.image, "https://cdn.example.com/social.png")


if __name__ == "__main__":
    unittest.main()
