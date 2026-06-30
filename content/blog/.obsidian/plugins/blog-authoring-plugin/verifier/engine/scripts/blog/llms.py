"""Generate llms.txt = committed identity base + a derived "## Writing" post list.

Single-source publishing (Constitution Principle VIII): the human-authored root llms.txt is
the identity/profile base; the build appends one markdown link per published post so the
AI-facing index updates automatically when a note is committed. Idempotent + deterministic
and conformant with the llms.txt convention (H2 file list of `[name](url): notes`).
"""
from __future__ import annotations
import re

from . import config

# Match a build-managed "## Writing" section: from its heading to the next H2 or EOF.
_WRITING_RE = re.compile(r"\n*^##\s+Writing\b.*?(?=^\#\#\s|\Z)", re.S | re.I | re.M)


def _strip_writing(base: str) -> str:
    """Remove any pre-existing "## Writing" section so re-runs never stack duplicates."""
    return _WRITING_RE.sub("\n", base).rstrip() + "\n"


def build_llms(base_text: str, posts, base_url: str) -> str:
    base = _strip_writing(base_text) if base_text.strip() else (base_text or "")
    if not posts:
        return base.rstrip() + "\n"
    blog = config.abs_url(base_url, config.BLOG_PATH)
    lines = [base.rstrip(), "", "## Writing", "",
             f"Latest field notes (full archive at {blog}):", ""]
    for p in posts:  # already newest-first
        url = config.abs_url(base_url, p.url)
        summary = " ".join(p.excerpt.split())  # collapse any internal whitespace to one line
        lines.append(f"- [{p.title}]({url}): {summary}")
    return "\n".join(lines) + "\n"
