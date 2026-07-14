# Contract — Shared Fingerprint Token Layer

The single source of the "one shared fingerprint" (FR-003). The SAME token names and values are declared on both surfaces: blog in `templates/blog/assets/blog.css` scoped to `#blog-root`; portfolio in `index.html`'s `<style>` scoped to `#ek-root`. **Only existing palette hexes are named** — no new hue, no new colour system (FR-004, Principle III/VII).

## Colour tokens (name → existing hex → role)
| Token | Hex (existing) | Role | Discipline |
|---|---|---|---|
| `--paper` | `#07090A` | page stock | base surface |
| `--paper-2` | `#0C1512` | pressed panel | elevation via **lightness** + inset shadow, never glow |
| `--ink` | `#EDF2EF` | reading text | body/headline |
| `--muted` | `#9FB0AA` | secondary text | captions, dek |
| `--muted-2` | `#828D86` | tertiary text | folios, fine print (must clear 4.5:1) |
| `--signal` | `#34E6A0` | **live/interaction green** | links-hover, focus ring, active nav underline, HEAD/live marker, robot LED. **≤~3% viewport budget** |
| `--green-deep` | `#18A06A` | green ink rest | rules-active, link rest |
| `--green-deep-2` | `#1AA56E` | green ink alt | rule ticks |
| `--mint` | `#7DF0C2` | hover/active lift | text lift on hover only |
| `--sand` | `#E7D2A6` | **warm metadata/tint** | mono labels, folios, drop-cap, quote/footnote marks |
| `--sand-deep` | `#CBB07A` | metadata alt | dim folios, rule warm-tint (6–10% α) |
| `--sem-blue` | `#46a8e0` | semantic: note / info | syntax token + callout kind only |
| `--sem-yellow` | `#ffd166` | semantic: warning | syntax token + callout kind only |
| `--sem-purple` | `#b388ff` | semantic: important | syntax token + callout kind only |
| `--sem-coral` | `#ff8a80` | semantic: caution/error | syntax token + callout kind only |

**Contrast requirement**: all text tokens over their surface clear WCAG 4.5:1 (fixes the audited `#66756F` comment token ≈3.9:1 → lift toward `#7E8C85`/`#8A9A92`).

## Type tokens (within the 3 fixed fonts)
| Token | Value | Notes |
|---|---|---|
| `--font-display` | 'Space Grotesk' | headings, roman only |
| `--font-body` | 'Manrope' | body, ~66ch measure, lh 1.6 |
| `--font-mono` | 'JetBrains Mono' | functional-only (code/meta/labels) |
| `--text-h1` | `clamp(2.75rem,4vw + 1rem,4.25rem)` | wt 500, tracking −0.02em |
| `--text-h2` | `2rem` | wt 600 |
| `--text-h3` | `1.375rem` | wt 600 |
| `--text-body` | `clamp(1.0625rem,1.6vw,1.125rem)` | wt 400 (~360 optical on dark) |
| `--text-meta` | `0.8125rem` | mono folios, tabular-nums |

Rules: no `background-clip:text` on any heading; no italic headers; `font-variant-numeric: tabular-nums` on numeric columns/folios; curly quotes + em-dashes in copy.

## Spacing / rhythm tokens
`--space-3xs 4px · --space-2xs 8px · --space-xs 12px · --space-sm 16px · --space-md 24px · --space-lg 32px · --space-xl 48px · --space-2xl 72px · --space-3xl 112px · --space-4xl 160px` (4px base, ~1.25 modular). Baseline 8px. Section padding asymmetric (generous top / tighter bottom); majors separated by `--space-3xl`. Gutter-rail width ~`--space-2xl`.

## Motion tokens
`--ease-out cubic-bezier(.16,1,.3,1) · --ease-in cubic-bezier(.4,0,1,1) · --ease-in-out cubic-bezier(.65,0,.35,1)`; durations `--dur-1 120ms · --dur-2 220ms · --dur-3 420ms` (exits ×0.75). Rules: transform/opacity only; reveal = one load stagger (`--i*60ms`, cap ~500ms) + section-level scroll draw (once); hover ≤1px translate, no box-shadow glow on dark; focus ring instant; `prefers-reduced-motion` → ≤150ms opacity crossfade. **Glow is permitted only on live robot motion.**

## Invariants the verifier asserts
- No `@font-face` beyond the existing three families on either surface; no colour value outside the named token set's hexes appears as a *new* system (existing per-token hexes only).
- Blog token layer + fingerprint classes live only under `#blog-root` in `blog.css`; portfolio under `#ek-root` in its own `<style>`.
- Token names/values identical across both surfaces (the shared-fingerprint proof).
