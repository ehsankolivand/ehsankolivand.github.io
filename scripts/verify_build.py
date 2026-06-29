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
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blog import config, content  # noqa: E402

TOKEN_RE = re.compile(r"\{\{[A-Za-z_][^}]*\}\}|<sc-(?:if|for)\b")
_LINK_SLUG_RE = re.compile(r'href="/blog/([^"/]+)/"')  # captures <slug> from /blog/<slug>/ links


def _all_jsonld(h):
    """All JSON-LD objects on a page, flattening any @graph. Returns None on a parse error."""
    out = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if isinstance(obj, dict) and "@graph" in obj:
            out.extend(obj["@graph"])
        elif isinstance(obj, list):
            out.extend(obj)
        else:
            out.append(obj)
    return out


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

        # ---- feature 002: enriched per-page SEO/GEO ----
        canon = config.abs_url(args.base_url, p.url)
        ok(f'rel="canonical" href="{canon}"' in h, f"{p.slug}: canonical not exact ({canon})")
        ok('property="og:image:width"' in h and 'property="og:image:height"' in h
           and 'property="og:image:alt"' in h, f"{p.slug}: incomplete og:image metadata")
        ok('name="twitter:image:alt"' in h, f"{p.slug}: missing twitter:image:alt")
        ok(f'<time datetime="{p.date.isoformat()}"' in h,
           f"{p.slug}: missing/incorrect <time datetime> (expected {p.date.isoformat()})")
        ok('type="application/atom+xml"' in h, f"{p.slug}: missing Atom feed autodiscovery link")
        objs = _all_jsonld(h)
        ok(objs is not None, f"{p.slug}: a JSON-LD block failed to parse")
        if objs:
            bp = next((o for o in objs if o.get("@type") == "BlogPosting"), None)
            ok(bp is not None, f"{p.slug}: no BlogPosting JSON-LD")
            if bp:
                ok(isinstance(bp.get("wordCount"), int) and bp["wordCount"] > 0,
                   f"{p.slug}: BlogPosting wordCount missing/zero")
                ok(bp.get("url") == canon, f"{p.slug}: BlogPosting url != canonical")
                ok(isinstance(bp.get("author"), dict) and bp["author"].get("@id") == config.PERSON_ID,
                   f"{p.slug}: BlogPosting author.@id != PERSON_ID (identity not unified)")
                ok(bp.get("inLanguage") == config.LOCALE, f"{p.slug}: BlogPosting inLanguage missing")
            bc = next((o for o in objs if o.get("@type") == "BreadcrumbList"), None)
            ok(bc is not None, f"{p.slug}: no BreadcrumbList JSON-LD")
            if bc:
                items = bc.get("itemListElement", [])
                ok(len(items) == 3, f"{p.slug}: breadcrumb should have 3 items (got {len(items)})")
                ok(bool(items) and items[-1].get("item") == canon,
                   f"{p.slug}: breadcrumb does not end at the post canonical")
        # image-cover posts must carry intrinsic dimensions (no CLS); code covers have no <img>
        if p.cover.kind == "image":
            ok("width=" in h and "height=" in h, f"{p.slug}: image cover missing intrinsic dimensions")

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
        # ---- feature 002: index structured-data graph identity ----
        iobjs = _all_jsonld(hi)
        ok(iobjs is not None, "index: a JSON-LD block failed to parse")
        if iobjs:
            ws = next((o for o in iobjs if o.get("@type") == "WebSite"), None)
            ok(ws is not None and ws.get("@id") == config.WEBSITE_ID,
               "index: WebSite @id != WEBSITE_ID (identity not unified with portfolio)")
            blog = next((o for o in iobjs if o.get("@type") == "Blog"), None)
            ok(blog is not None and isinstance(blog.get("author"), dict)
               and blog["author"].get("@id") == config.PERSON_ID, "index: Blog.author.@id != PERSON_ID")
            ibc = next((o for o in iobjs if o.get("@type") == "BreadcrumbList"), None)
            ok(ibc is not None and len(ibc.get("itemListElement", [])) == 2,
               "index: missing 2-item BreadcrumbList")
        ok("SearchAction" not in hi, "index: SearchAction must be omitted (no search endpoint)")

    # ---- sitemap ----
    sm = out / "sitemap.xml"
    ok(sm.exists(), "missing sitemap.xml")
    if sm.exists():
        hs = sm.read_text(encoding="utf-8")
        ok(config.abs_url(args.base_url, "/") in hs, "sitemap: homepage missing")
        for p in posts:
            ok(config.abs_url(args.base_url, p.url) in hs, f"sitemap: {p.slug} missing")
        # ---- feature 002: lastmod correctness ----
        for p in posts:
            loc = config.abs_url(args.base_url, p.url)
            m = re.search(re.escape(f"<loc>{loc}</loc>") + r"\s*<lastmod>([0-9-]+)</lastmod>", hs)
            ok(bool(m) and m.group(1) == p.updated.isoformat(),
               f"sitemap: {p.slug} lastmod != updated ({p.updated.isoformat()})")
        newest = max((p.updated for p in posts), default=None)
        if newest:
            home_loc = config.abs_url(args.base_url, "/")
            mh = re.search(re.escape(f"<loc>{home_loc}</loc>") + r"\s*<lastmod>([0-9-]+)</lastmod>", hs)
            expected = max(config.PORTFOLIO_LASTMOD, newest).isoformat()
            ok(bool(mh) and mh.group(1) == expected,
               f"sitemap: home lastmod != max(portfolio, newest) ({expected})")

    # ---- feature 002: Atom feed ----
    feed_path = out / "blog" / "feed.xml"
    ok(feed_path.exists(), "missing blog/feed.xml")
    if feed_path.exists():
        try:
            froot = ET.parse(feed_path).getroot()
            ns = {"a": "http://www.w3.org/2005/Atom"}
            fid, ftitle, fupd = (froot.find("a:id", ns), froot.find("a:title", ns),
                                 froot.find("a:updated", ns))
            ok(fid is not None and ftitle is not None and fupd is not None,
               "feed: missing required feed-level id/title/updated")
            entries = froot.findall("a:entry", ns)
            ok(len(entries) == len(posts), f"feed: {len(entries)} entries != {len(posts)} posts")
            entry_ids = {e.find("a:id", ns).text for e in entries if e.find("a:id", ns) is not None}
            for p in posts:
                ok(config.abs_url(args.base_url, p.url) in entry_ids,
                   f"feed: missing entry id for {p.slug}")
            newest = max((p.updated for p in posts), default=None)
            if newest and fupd is not None:
                ok(fupd.text == newest.isoformat() + "T00:00:00Z",
                   "feed: feed-level updated != max(post updated)")
        except ET.ParseError as e:
            ok(False, f"feed: not well-formed XML: {e}")

    # ---- feature 002: generated llms.txt ----
    llms_path = out / "llms.txt"
    ok(llms_path.exists(), "missing generated llms.txt")
    if llms_path.exists():
        lt = llms_path.read_text(encoding="utf-8")
        first_line = lt.splitlines()[0] if lt.splitlines() else ""
        ok(config.AUTHOR_NAME in first_line, "llms.txt: missing author H1 from the base")
        if posts:
            ok("## Writing" in lt, "llms.txt: missing '## Writing' section")
            for p in posts:
                ok(config.abs_url(args.base_url, p.url) in lt,
                   f"llms.txt: missing post URL for {p.slug}")

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

    # ---- feature 002: no dangling internal links (committed source + built pages) ----
    valid_slugs = {p.slug for p in posts}
    SEED = {"spec-driven-android", "custom-layouts-compose", "mvi-that-scales"}
    repo_idx = repo / "index.html"
    if repo_idx.exists():
        rtext = repo_idx.read_text(encoding="utf-8")
        repo_slugs = set(_LINK_SLUG_RE.findall(rtext))
        ok(not (SEED & repo_slugs),
           f"committed index.html still links to a deleted seed post: {sorted(SEED & repo_slugs)}")
        for s in sorted(repo_slugs):
            ok(s in valid_slugs, f"committed index.html links to nonexistent post /blog/{s}/")
    built_pages = (list((out / "blog").glob("*/index.html"))
                   + [out / "blog" / "index.html", out / "index.html"])
    for pg in built_pages:
        if not pg.exists():
            continue
        for s in sorted(set(_LINK_SLUG_RE.findall(pg.read_text(encoding="utf-8")))):
            ok(s in valid_slugs,
               f"{pg.relative_to(out)} links to nonexistent post /blog/{s}/")

    # ---- feature 002: robots references the sitemap (C1) ----
    robots = out / "robots.txt"
    if robots.exists():
        ok(config.abs_url(args.base_url, "/sitemap.xml") in robots.read_text(encoding="utf-8"),
           "robots.txt does not reference the sitemap URL")

    # ---- feature 002: unique <title> across built blog pages (C2) ----
    titles = []
    for pg in (sorted((out / "blog").glob("*/index.html")) + [out / "blog" / "index.html"]):
        if pg.exists():
            mt = re.search(r"<title>(.*?)</title>", pg.read_text(encoding="utf-8"), re.S)
            if mt:
                titles.append(mt.group(1))
    ok(len(titles) == len(set(titles)), "duplicate <title> among built blog pages")

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
