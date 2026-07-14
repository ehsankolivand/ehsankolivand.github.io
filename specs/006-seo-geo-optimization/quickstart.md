# Quickstart / Validation Guide: SEO / GEO-AEO Optimization Refinement

Prove the feature end-to-end. Run from the repo root.

## Prerequisites
```bash
pip install -r requirements.txt        # PyYAML only (already installed)
```

## Build + full gate (the acceptance bar)
```bash
python -m unittest discover -s tests               # 107 tests → OK
python scripts/build_blog.py --out _site           # deterministic build
python scripts/verify_build.py --out _site         # Definition-of-Done → 0 failures, ≥594 checks
```
Expected: all three green. This is SC-001 / C7.

## Targeted contract checks

### C1 — byline anchor (a post)
```bash
grep -o '<a href="/"[^>]*>Ehsan Kolivand</a>' _site/blog/telegram-topic-export-markdown-jsonl/index.html
```
Expected: one match (the visible byline is now a real anchor to `/`).

### C2 — per-post WebSite node + BlogPosting first
```bash
python - <<'PY'
import re, json, pathlib
p = pathlib.Path("_site/blog/telegram-topic-export-markdown-jsonl/index.html").read_text()
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', p, re.S)
first = json.loads(blocks[0]); assert first["@type"] == "BlogPosting", first["@type"]
types = [json.loads(b).get("@type") for b in blocks]
ws = [json.loads(b) for b in blocks if json.loads(b).get("@type") == "WebSite"][0]
assert ws["@id"].endswith("/#website") and ws["publisher"]["@id"].endswith("/#person")
print("OK: first =", first["@type"], "| nodes =", types, "| WebSite/publisher unified")
PY
```
Expected: `OK: first = BlogPosting | nodes = ['BlogPosting', 'BreadcrumbList', 'WebSite'] | WebSite/publisher unified`.

### C3 — portfolio head completeness
```bash
grep -c 'rel="alternate" type="application/atom+xml"' _site/index.html          # 1
grep -c 'name="robots" content="index, follow, max-image-preview:large"' _site/index.html   # 1
grep -c '"dateModified"' _site/index.html                                        # >=1 (ProfilePage)
```

### C4 — no dead Google-Fonts hints
```bash
grep -c 'fonts.googleapis.com\|fonts.gstatic.com' _site/index.html               # 0
```

### C5 — robots.txt Applebot + sitemap
```bash
grep -A1 -i '^User-agent: Applebot' _site/robots.txt                             # Allow: /
grep -c 'Sitemap: https://ehsankolivand.github.io/sitemap.xml' _site/robots.txt  # 1
```

### C6 — determinism
```bash
python scripts/build_blog.py --out _site_a >/dev/null
python scripts/build_blog.py --out _site_b >/dev/null
diff -r _site_a _site_b && echo "DETERMINISTIC" ; rm -rf _site_a _site_b
```
Expected: `DETERMINISTIC` (no diff).

### C7 — gate integrity
```bash
git diff --name-only -- scripts/verify_build.py .specify/memory/constitution.md
```
Expected: empty (neither the verifier nor the constitution was modified).

## Independent verification pass
After the gate is green, a clean-context subagent audits every generated page's `<head>` meta and
JSON-LD against the briefs and reports discrepancies by file/line (see the feature summary). Fixes
and final judgment stay with the implementer.
