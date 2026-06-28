<!-- SPECKIT START -->
Active feature: Obsidian-Vault-Driven Blog (`001-obsidian-blog`).
Plan: `specs/001-obsidian-blog/plan.md` (read this first for tech stack, structure, and design-extraction approach).
Constitution: `.specify/memory/constitution.md` (7 non-negotiable principles — SEO-static generation, GitHub Pages only, design fidelity, Obsidian single source, per-page SEO/GEO, a11y+CWV, non-destructive to portfolio).
Stack: Python 3.11+ static generator (PyYAML + an in-house, stdlib-only Markdown renderer — no Markdown library) rendering Obsidian markdown into design templates extracted from the bundled blog design; deploys to GitHub Pages via Actions. Author surface: `content/blog/`. Design source: `templates/blog/`. Never edit generated HTML or the portfolio `index.html`.
<!-- SPECKIT END -->
