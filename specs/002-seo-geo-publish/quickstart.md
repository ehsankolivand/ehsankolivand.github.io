# Quickstart: Validate SEO + GEO + One-Commit Publishing

Run + validation guide proving the feature end-to-end. Implementation details live in `tasks.md`;
the exact output shapes live in `contracts/`.

## Prerequisites

```bash
pip install -r requirements.txt        # PyYAML==6.0.1 (only dep)
python3 --version                      # 3.11+ (CI pins 3.12.7)
```

## Build & verify (the Definition-of-Done gate)

```bash
python scripts/build_blog.py --out _site
python scripts/verify_build.py --out _site      # MUST exit 0; checks ≥ 110, 0 failures
python -m http.server -d _site 8080             # preview http://localhost:8080/blog/
```

## Scenario A — One-commit publishing (US1 / SC-001, SC-004)

1. Add one note `content/blog/<something>.md` (valid frontmatter + body). Build.
2. Confirm, with **no other edits**, the new post appears in all derived surfaces:
   ```bash
   ls _site/blog/<slug>/index.html                                   # post page
   grep -q "/blog/<slug>/" _site/blog/index.html                     # index card
   grep -q "/blog/<slug>/" _site/sitemap.xml                         # sitemap
   grep -q "/blog/<slug>/" _site/blog/feed.xml                       # feed entry
   grep -q "/blog/<slug>/" _site/llms.txt                            # llms.txt entry
   grep -q "/blog/<slug>/" _site/index.html                          # homepage Field-notes (built)
   ```
3. Remove the note, rebuild, and confirm the slug appears in **none** of the above — and not in the
   committed source either: `grep -c "/blog/<slug>/" index.html` → expect related slugs absent.

## Scenario B — No dangling committed links (US1 / SC-002) — the central defect

```bash
# The committed portfolio source must NOT reference the deleted seed posts:
grep -E "spec-driven-android|custom-layouts-compose|mvi-that-scales" index.html   # expect: no matches
# The committed managed region must carry no post-specific links (neutralized):
#   only "/blog/" may appear inside the LATEST-NOTES markers.
```
`verify_build.py` asserts this (assertions 18–19); it fails the build if any committed or built page
links to a nonexistent post.

## Scenario C — Crawlability & rich results (US2 / SC-003, SC-005)

```bash
# Content + metadata present without JS (grep the static HTML):
P=_site/blog/<slug>/index.html
grep -q '<link rel="canonical" href="https://ehsankolivand.github.io/blog/<slug>/"' "$P"
grep -q 'property="og:image:width"' "$P" && grep -q 'property="og:image:alt"' "$P"
grep -q 'name="twitter:image:alt"' "$P"
grep -q '<time datetime="' "$P"
# JSON-LD validity + identity + breadcrumb (uses python):
python - "$P" <<'PY'
import sys, re, json
h=open(sys.argv[1]).read()
blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
objs=[json.loads(b) for b in blocks]                      # must all parse
flat=[o for b in objs for o in (b.get("@graph",[b]) if isinstance(b,dict) else b)]
assert any(o.get("@type")=="BlogPosting" and o["author"]["@id"].endswith("#person") for o in flat)
assert any(o.get("@type")=="BreadcrumbList" for o in flat)
assert not any("SearchAction" in json.dumps(o) for o in flat)
print("JSON-LD OK")
PY
```

## Scenario D — GEO surfaces (US3 / SC-004, SC-009)

```bash
# Feed is well-formed Atom and lists every post:
python -c "import xml.etree.ElementTree as T; T.parse('_site/blog/feed.xml'); print('feed parses')"
grep -c "<entry>" _site/blog/feed.xml                 # == number of published posts
# llms.txt lists posts under ## Writing:
grep -q "^## Writing" _site/llms.txt
# Author identity is unified (same #person id in blog and portfolio):
grep -q "#person" _site/blog/<slug>/index.html && grep -q "#person" _site/index.html
```

## Scenario E — A11y / CWV preserved (US4 / SC-006)

```bash
grep -c "<h1" "$P"                                    # exactly 1
grep -q 'width=' "$P"                                 # cover carries intrinsic dims (no CLS)
# determinism: two builds are byte-identical
python scripts/build_blog.py --out _site_a >/dev/null && python scripts/build_blog.py --out _site_b >/dev/null
diff -r _site_a _site_b && echo "deterministic" ; rm -rf _site_a _site_b
```

## Pass criteria

- `verify_build.py` exits 0 with ≥ 110 checks.
- Scenarios A–E all hold.
- `git diff` of the built vs source `index.html` differs **only** inside the `LATEST-NOTES` markers
  (portfolio intact, Principle VII / SC-007).
