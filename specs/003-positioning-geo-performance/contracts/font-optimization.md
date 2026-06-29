# Contract: Portfolio Font Optimization (sanctioned zone + fidelity proof)

The one-time, non-visual removal of unused font subsets from the portfolio `index.html`, gated by a
deterministic offline fidelity proof. (FR-012..FR-014; Constitution v1.3.0 Principle VII exception 2,
Principle VI; prove-or-defer.)

## Sanctioned zone

- Markers `<!--PORTFOLIO-FONTS:START-->` and `<!--PORTFOLIO-FONTS:END-->` wrap the inlined
  `@font-face` block (the `<style>` containing the 54 base64 woff2 faces) in `index.html`.
- Only bytes **between** the markers may change, and only by deleting whole `@font-face { … }` rules
  (with their preceding `/* subset */` comment). No edits to any retained face.

## Recoverable baseline (never served)

- `assets/portfolio-fonts/index.baseline.html` = a verbatim copy of `index.html` taken **after** the
  markers are added but **before** any face is removed (all 54 faces intact).
- Not in `config.ROOT_COPY_ALLOWLIST` and not under any copied asset tree → the build never deploys
  it. It is the recoverable original *and* the proof reference.
- Deferral = `index.html` left byte-identical to this baseline (markers may be present; zero faces
  removed).

## Drop set (when landed)

- Remove the 32 `@font-face` rules whose `unicode-range` equals one of the four non-Latin subsets:
  - Cyrillic-ext `U+0460-052F, U+1C80-1C8A, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F`
  - Cyrillic `U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116`
  - Greek `U+0370-0377, U+037A-037F, U+0384-038A, U+038C, U+038E-03A1, U+03A3-03FF`
  - Vietnamese `U+0102-0103, U+0110-0111, …, U+1EA0-1EF9, U+20AB`
- Keep the 22 Latin + Latin-ext faces (full Latin-script coverage).
- Identification is by `unicode-range` value (robust); the `/* subset */` comments corroborate.

## Procedure (offline, in sandbox — no CI/runtime dependency)

1. Add the two markers around the font `<style>` block in `index.html`.
2. Copy `index.html` → `assets/portfolio-fonts/index.baseline.html`.
3. Delete the 32 non-Latin `@font-face` rules (and their `/* … */` label comments) inside the zone.
4. Build + run the verifier; if the fidelity proof passes, keep the change; else revert step 3
   (restore `index.html` from the baseline) and record deferral.

## Fidelity proof (verifier, deterministic + offline)

Given `cur = index.html`, `base = assets/portfolio-fonts/index.baseline.html`:

- **Markers**: both files contain `START` then `END` exactly once, in order.
- **(b) Outside-zone integrity**: `outside(cur) == outside(base)` byte-for-byte, where `outside(x)` =
  `x` with the `START…END` span removed. AND every `@font-face { … }` block in `zone(cur)` appears as
  an exact substring of `zone(base)` (only whole removals, never edits to a kept face).
- **(a) Glyph coverage**: let `V` = the set of codepoints appearing in `cur` with the
  `url(data:font/woff2;base64,…)` payloads stripped (a conservative superset of rendered text). Parse
  `unicode-range`s from `zone(base)` → `cover_base`, from `zone(cur)` → `cover_cur`. Assert
  `cover_cur ⊆ cover_base` (only removals) and `∀ c ∈ V: c ∈ cover_base ⟹ c ∈ cover_cur` (no rendered,
  originally-covered codepoint loses coverage).
- **Applicability**: if `zone(cur) == zone(base)` (deferred/untouched), the proof passes trivially and
  is reported as "font optimization: not applied".

## Invariants (verifier-enforced)

1. If `index.html` is present, the `PORTFOLIO-FONTS` markers and the baseline file are both present
   and well-formed (or the whole font change is absent — markers may still be added; baseline present).
2. Outside-zone byte-equality vs. baseline (this is *in addition to* the existing "portfolio
   byte-identical outside the Field-notes region" check, against `_site` — here it is the committed
   source vs. its baseline).
3. Glyph coverage preserved for every rendered, originally-covered codepoint.
4. `cover_cur ⊆ cover_base` and retained faces verbatim in baseline (only whole-subset removals).
5. The original is recoverable (baseline present and equals `index.html` with the removed faces
   re-inserted is *not* asserted byte-for-byte, but the baseline IS the full original and is committed).
