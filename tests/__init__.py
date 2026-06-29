"""Renderer unit-test package (feature 004). Stdlib unittest only — no third-party dependency.

Puts the generator's `scripts/` dir on sys.path so tests can `from blog import ...`, matching how
build_blog.py / verify_build.py import the package. Run: `python -m unittest discover -s tests`.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_ROOT, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
