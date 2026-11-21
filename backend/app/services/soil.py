"""Soil sample validation and USDA texture classification.

Texture boundaries per USDA NRCS Soil Survey Manual (2017), Chapter 3 — the
standard 12-class textural triangle. Cross-referenced against UC ANR's soil
texture reference and standard soil-texture-calculator implementations.
Classes are checked tightest-constraint-first; exact-boundary ties resolve in
the order below. This is a decision-tree approximation of the triangle, not a
scan of the official printed chart, so results may differ from the chart in
rare cases exactly on a boundary line.
"""


def classify_usda_texture(sand_pct: float, silt_pct: float, clay_pct: float) -> str | None:
    total = sand_pct + silt_pct + clay_pct
    if total < 95 or total > 105:
        return None  # doesn't sum close enough to 100% to classify reliably

    # Normalize to exactly 100 so boundary comparisons are consistent even if
    # the entered percentages are off by a rounding point or two.
    scale = 100 / total
    sand, silt, clay = sand_pct * scale, silt_pct * scale, clay_pct * scale

    if clay >= 40:
        if silt >= 40:
            return "silty clay"
        if sand <= 45:
            return "clay"
        return "sandy clay"  # clay>=40, sand>45 — boundary case, sand-dominant clay

    if clay >= 35 and sand > 45:
        return "sandy clay"

    if 27 <= clay < 40:
        if sand > 20:
            return "clay loam"
        return "silty clay loam"

    if 20 <= clay < 35 and silt < 28 and sand > 45:
        return "sandy clay loam"

    if silt >= 80 and clay < 12:
        return "silt"

    if (silt >= 50 and 12 <= clay < 27) or (50 <= silt < 80 and clay < 12):
        return "silt loam"

    if 7 <= clay < 27 and 28 <= silt < 50 and sand <= 52:
        return "loam"

    if (7 <= clay < 20 and sand > 52) or (clay < 7 and silt < 50 and (silt + 2 * clay) >= 30):
        return "sandy loam"

    if sand >= 85 and (silt + 1.5 * clay) < 15:
        return "sand"

    if clay < 15 and 70 <= sand <= 91 and (silt + 2 * clay) < 30:
        return "loamy sand"

    # Falls in a gap between the simplified rules above (can happen very close
    # to a triangle vertex) — texture class left unset rather than guessed.
    return None


def validate_texture_sum(sand: float | None, silt: float | None, clay: float | None) -> list[str]:
    warnings: list[str] = []
    if sand is not None and silt is not None and clay is not None:
        total = sand + silt + clay
        if total < 95 or total > 105:
            warnings.append(
                f"Sand + silt + clay = {total:.1f}%, which is not close to 100%. "
                "Texture classification was skipped; double-check these values."
            )
    return warnings


def validate_ph(ph: float | None) -> list[str]:
    if ph is not None and (ph < 3 or ph > 10):
        return [
            f"pH {ph} is outside the typical range for agricultural soils (3-10). "
            "Value accepted as entered, but please double-check it."
        ]
    return []
