"""Unit tests for build-tool helpers (scripts/build_blog.py).

Covers the two build-time nits: copytree must skip OS/editor stray files, and image_size's
JPEG scanner must tolerate standalone markers (RST/SOI/EOI/TEM) and 0xFF fill bytes before
the SOF segment. Stdlib only (tempfile + struct).
"""
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import build_blog as B  # noqa: E402


def _jpeg(width: int, height: int, prefix: bytes = b"") -> bytes:
    """A minimal JPEG: SOI + optional marker prefix + SOF0(height,width) + EOI."""
    soi = b"\xff\xd8"
    sof = b"\xff\xc0" + struct.pack(">H", 17) + b"\x08" + struct.pack(">HH", height, width) + b"\x03" + b"\x00" * 9
    return soi + prefix + sof + b"\xff\xd9"


class TestImageSizeJPEG(unittest.TestCase):
    def _measure(self, data: bytes):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "i.jpg"
            p.write_bytes(data)
            return B.image_size(p)

    def test_basic_jpeg(self):
        self.assertEqual(self._measure(_jpeg(200, 100)), (200, 100))

    def test_standalone_markers_and_fill_bytes_before_sof(self):
        # FF FF (fill) + FF D0 (RST0, standalone, no length) + an APP0 segment, then SOF.
        prefix = b"\xff\xff" + b"\xff\xd0" + b"\xff\xe0\x00\x04\x12\x34"
        self.assertEqual(self._measure(_jpeg(640, 480, prefix)), (640, 480))


class TestStrayFileFilter(unittest.TestCase):
    def test_skips_os_and_editor_cruft(self):
        for name in (".DS_Store", "Thumbs.db", "desktop.ini", "notes.swp", "blog.css~"):
            self.assertTrue(B._is_stray(name), name)

    def test_keeps_real_assets(self):
        for name in ("blog.css", "blog.js", "font.woff2", "cover.png", "a.md"):
            self.assertFalse(B._is_stray(name), name)

    def test_copytree_excludes_stray(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / "src", Path(tmp) / "dst"
            (src / "sub").mkdir(parents=True)
            (src / "keep.css").write_text("x")
            (src / ".DS_Store").write_text("junk")
            (src / "sub" / "Thumbs.db").write_text("junk")
            (src / "sub" / "keep.js").write_text("y")
            B.copytree(src, dst)
            self.assertTrue((dst / "keep.css").exists())
            self.assertTrue((dst / "sub" / "keep.js").exists())
            self.assertFalse((dst / ".DS_Store").exists())
            self.assertFalse((dst / "sub" / "Thumbs.db").exists())


if __name__ == "__main__":
    unittest.main()
