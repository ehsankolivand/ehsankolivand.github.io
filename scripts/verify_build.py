#!/usr/bin/env python3
"""Definition-of-Done verifier for the generated site.

Asserts the success criteria on the built _site/: content + SEO in static HTML, single
<h1>, valid JSON-LD, complete index links + sitemap, no template tokens, and the
portfolio index.html byte-identical to the repo copy OUTSIDE the managed "Field notes"
region (the <!--LATEST-NOTES:*--> markers, which the build regenerates from the latest
posts). Exit non-zero on any failure.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blog import config, content  # noqa: E402

TOKEN_RE = re.compile(r"\{\{[A-Za-z_][^}]*\}\}|<sc-(?:if|for)\b")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="_site")
    ap.add_argument("--repo-root", default=str(config.REPO_ROOT))
    ap.add_argument("--base-url", default=config.DEFAULT_BASE_URL)
    args = ap.parse_args(argv)

    out = Path(args.out).resolve()
    repo = Path(args.repo_root).resolve()
    errors: list[str] = []
    checks = 0

    def ok(cond, msg):
        nonlocal checks
        checks += 1
        if not cond:
            errors.append(msg)

    cats = content.load_categories(config.CONTENT_DIR / "categories.yml")
    posts = content.load_posts(config.CONTENT_DIR, cats, args.base_url, include_drafts=False)
    cat_labels = {c.name: c.label for c in cats}

    # ---- per-post checks ----
    for p in posts:
        page = out / "blog" / p.slug / "index.html"
        ok(page.exists(), f"missing post page: {page}")
        if not page.exists():
            continue
        h = page.read_text(encoding="utf-8")
        ok(h.count("<h1") == 1, f"{p.slug}: expected exactly one <h1> (found {h.count('<h1')})")
        ok(p.title.split(" — ")[0][:24] in h or _esc_in(p.title, h), f"{p.slug}: title not in page")
        ok("<title>" in h, f"{p.slug}: missing <title>")
        ok('name="description"' in h, f"{p.slug}: missing meta description")
        ok('rel="canonical"' in h and p.slug + "/" in h, f"{p.slug}: missing/incorrect canonical")
        ok('property="og:title"' in h and 'property="og:url"' in h and 'property="og:image"' in h,
           f"{p.slug}: missing Open Graph tags")
        ok('name="twitter:card"' in h, f"{p.slug}: missing Twitter card")
        ok(cat_labels[p.category] in h, f"{p.slug}: category chip label missing")
        ok(p.display_date() in h, f"{p.slug}: date missing")
        ok(p.read_time in h, f"{p.slug}: read time missing")
        ok(not TOKEN_RE.search(h), f"{p.slug}: unresolved template tokens present")
        # JSON-LD parses and is a BlogPosting with required fields
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        ok(bool(m), f"{p.slug}: no JSON-LD")
        if m:
            try:
                obj = json.loads(m.group(1))
                ok(obj.get("@type") == "BlogPosting", f"{p.slug}: JSON-LD @type != BlogPosting")
                for fld in ("headline", "author", "datePublished", "articleSection"):
                    ok(bool(obj.get(fld)), f"{p.slug}: JSON-LD missing {fld}")
            except json.JSONDecodeError as e:
                ok(False, f"{p.slug}: JSON-LD invalid: {e}")
        # rendered body content present, scoped to the body container so the dek <p>
        # can't satisfy it (every body block partial carries data-reveal)
        mbody = re.search(r"<!-- body blocks -->(.*?)<!-- end / signature -->", h, re.S)
        ok(bool(mbody) and "data-reveal" in mbody.group(1),
           f"{p.slug}: no rendered body content in the body container")
        # related "more notes" resolve to real anchors when declared
        if p.related:
            for r in p.related:
                ok(f'href="/blog/{r.slug}/"' in h, f"{p.slug}: more-notes link to {r.slug} missing")

    # ---- index ----
    idx = out / "blog" / "index.html"
    ok(idx.exists(), "missing blog index")
    if idx.exists():
        hi = idx.read_text(encoding="utf-8")
        ok(hi.count("<h1") == 1, f"index: expected one <h1> (found {hi.count('<h1')})")
        ok(not TOKEN_RE.search(hi), "index: unresolved template tokens present")
        for p in posts:
            ok(f'href="/blog/{p.slug}/"' in hi, f"index: missing crawlable link to {p.slug}")
        for c in cats:
            ok(f'data-cat="{c.name}"' in hi, f"index: missing category nav entry {c.name}")

    # ---- sitemap ----
    sm = out / "sitemap.xml"
    ok(sm.exists(), "missing sitemap.xml")
    if sm.exists():
        hs = sm.read_text(encoding="utf-8")
        ok(config.abs_url(args.base_url, "/") in hs, "sitemap: homepage missing")
        for p in posts:
            ok(config.abs_url(args.base_url, p.url) in hs, f"sitemap: {p.slug} missing")

    # ---- portfolio: unchanged OUTSIDE the managed "Field notes" section; ----
    # ---- inside, the latest 3 posts + a /blog/ link are present. ----
    # Stays consistent with build_blog.py, which injects only when index.html exists,
    # carries both markers, AND there are posts — and otherwise prints a NOTE and
    # succeeds. Verify mirrors that tolerance (and never crashes on an absent index).
    START, END = "<!--LATEST-NOTES:START-->", "<!--LATEST-NOTES:END-->"
    out_idx_path, repo_idx_path = out / "index.html", repo / "index.html"
    if not repo_idx_path.exists():
        print("  NOTE: repo index.html absent; skipping portfolio comparison")
    elif not out_idx_path.exists():
        ok(False, "portfolio index.html present in repo but missing from output")
    else:
        out_idx = out_idx_path.read_text(encoding="utf-8")
        repo_idx = repo_idx_path.read_text(encoding="utf-8")

        def strip_region(s: str) -> str:
            i, j = s.find(START), s.find(END)
            return (s[:i] + s[j + len(END):]) if (i != -1 and j != -1) else s

        ok(strip_region(out_idx) == strip_region(repo_idx),
           "portfolio index.html changed OUTSIDE the managed notes section")
        m = re.search(re.escape(START) + r"(.*?)" + re.escape(END), out_idx, re.S)
        if m and posts:
            region = m.group(1)
            for p in posts[:3]:
                ok(f'href="/blog/{p.slug}/"' in region, f"homepage: missing latest-post card link to {p.slug}")
            ok('href="/blog/"' in region, "homepage: missing 'Read all notes' link to /blog/")
            ok(region.count("data-homenote") >= min(3, len(posts)),
               "homepage: expected 3 note cards in the section")
        elif posts and not m:
            print("  NOTE: index.html has no LATEST-NOTES markers; homepage notes not injected (build tolerates this)")

    # ---- assets ----
    ok((out / "blog/assets/blog.css").exists(), "missing blog.css")
    ok((out / "blog/assets/blog.js").exists(), "missing blog.js")
    fonts = list((out / "blog/assets/fonts").glob("*.woff2")) if (out / "blog/assets/fonts").exists() else []
    ok(len(fonts) >= 1, "missing self-hosted fonts")
    ok((out / ".nojekyll").exists(), "missing .nojekyll")
    # required SEO/branding companions (Constitution V/VII)
    for name in config.ROOT_REQUIRED:
        ok((out / name).exists(), f"missing required root companion file: {name}")

    # ---- report ----
    print(f"verify_build: {checks} checks, {len(errors)} failure(s)")
    if errors:
        for e in errors:
            print("  FAIL:", e)
        return 1
    print(f"  OK: {len(posts)} posts verified, portfolio intact, SEO + content static, sitemap complete.")
    return 0


def _esc_in(title: str, h: str) -> bool:
    import html as _h
    return _h.escape(title, quote=True) in h or _h.escape(title, quote=False) in h


if __name__ == "__main__":
    raise SystemExit(main())
