"""Transparent, rule-based crop suitability scoring.

Deliberately NOT a black-box ML classifier (see master spec Part 8): every
score is traceable to named, tunable ranges in `crop_catalog.py`. The 7-day
weather forecast is never used as a stand-in for growing-season climate
(Jenny's equation of soil formation — soil/climate suitability needs seasonal
climatology, not a week's forecast); seasonal climate inputs here are either
omitted (texture/pH/OC-only scoring) or user-supplied regional estimates,
explicitly labeled as such.
"""

from dataclasses import dataclass, field

from app.services.crop_catalog import CROPS, SCORING_WEIGHTS


@dataclass
class CropScore:
    key: str
    name: str
    score: float
    confidence: str
    reasons: list[str] = field(default_factory=list)
    limiting_factors: list[str] = field(default_factory=list)
    season: str = ""
    duration_days: tuple[int, int] = (0, 0)
    water_need: str = ""
    data_limitations: list[str] = field(default_factory=list)


def _triangular_score(value: float, low: float, high: float, slack: float) -> float:
    """100 inside [low, high], linearly decaying to 0 over `slack` units outside."""
    if low <= value <= high:
        return 100.0
    if value < low:
        deficit = low - value
    else:
        deficit = value - high
    if deficit >= slack:
        return 0.0
    return 100.0 * (1 - deficit / slack)


def _texture_score(texture_class: str | None, crop: dict) -> tuple[float | None, str]:
    if texture_class is None:
        return None, "Soil texture unknown (sand/silt/clay not provided or didn't sum to 100%)"
    if texture_class in crop["texture_pref"]:
        return 100.0, f"Texture '{texture_class}' is preferred for this crop"
    if texture_class in crop["texture_tolerant"]:
        return 60.0, f"Texture '{texture_class}' is tolerated but not ideal for this crop"
    return 25.0, f"Texture '{texture_class}' is outside this crop's typical preference"


def _ph_score(ph: float | None, crop: dict) -> tuple[float | None, str]:
    if ph is None:
        return None, "Soil pH not provided"
    low, high = crop["ph_range"]
    score = _triangular_score(ph, low, high, slack=1.5)
    if score >= 100:
        return score, f"pH {ph} is within this crop's preferred range ({low}-{high})"
    if score >= 70:
        return score, f"pH {ph} is close to this crop's preferred range ({low}-{high})"
    return score, f"pH {ph} is outside this crop's preferred range ({low}-{high})"


def _organic_carbon_score(oc: float | None) -> tuple[float | None, str]:
    if oc is None:
        return None, "Organic carbon not provided"
    if oc < 0.5:
        return 40.0, f"Organic carbon {oc}% is low — may limit nutrient supply for any crop"
    if oc < 0.75:
        return 70.0, f"Organic carbon {oc}% is medium"
    return 100.0, f"Organic carbon {oc}% is good for general fertility"


def _climate_score(
    expected_temp_c: float | None,
    expected_rainfall_mm: float | None,
    irrigation_available: bool,
    crop: dict,
) -> tuple[float | None, str]:
    if expected_temp_c is None or expected_rainfall_mm is None:
        return None, "Growing-season climate not provided (a 7-day forecast is not a substitute)"
    low, high = crop["temp_range_c"]
    temp_score = _triangular_score(expected_temp_c, low, high, slack=5)
    min_rain = crop["min_rainfall_mm_season"]
    if expected_rainfall_mm >= min_rain:
        rain_score = 100.0
    elif irrigation_available:
        rain_score = max(50.0, 100.0 * expected_rainfall_mm / min_rain)
    else:
        rain_score = 100.0 * expected_rainfall_mm / min_rain
    combined = (temp_score + rain_score) / 2
    note = (
        f"Estimated season temperature {expected_temp_c}°C and rainfall {expected_rainfall_mm}mm "
        f"vs. this crop's typical needs ({low}-{high}°C, {min_rain}mm+)"
    )
    return combined, note


def score_crops(
    *,
    texture_class: str | None,
    ph: float | None,
    organic_carbon_pct: float | None,
    irrigation_available: bool = False,
    expected_season_temp_c: float | None = None,
    expected_season_rainfall_mm: float | None = None,
    season_filter: str | None = None,
) -> list[CropScore]:
    results: list[CropScore] = []

    for crop in CROPS:
        if season_filter and season_filter not in crop["season"]:
            continue

        tex_score, tex_reason = _texture_score(texture_class, crop)
        ph_score, ph_reason = _ph_score(ph, crop)
        oc_score, oc_reason = _organic_carbon_score(organic_carbon_pct)
        climate_score, climate_reason = _climate_score(
            expected_season_temp_c, expected_season_rainfall_mm, irrigation_available, crop
        )

        components = {
            "texture": tex_score,
            "ph": ph_score,
            "organic_carbon": oc_score,
            "season_climate": climate_score,
        }
        available = {k: v for k, v in components.items() if v is not None}
        if not available:
            continue
        weight_sum = sum(SCORING_WEIGHTS[k] for k in available)
        final_score = sum(SCORING_WEIGHTS[k] * v for k, v in available.items()) / weight_sum

        n_missing = len(components) - len(available)
        confidence = "high" if n_missing == 0 else "medium" if n_missing == 1 else "low"

        reasons: list[str] = []
        limiting: list[str] = []
        for comp_score, comp_reason in [
            (tex_score, tex_reason),
            (ph_score, ph_reason),
            (oc_score, oc_reason),
            (climate_score, climate_reason),
        ]:
            if comp_score is None:
                continue
            (reasons if comp_score >= 70 else limiting).append(comp_reason)

        data_limitations = [
            r for r in [tex_reason, ph_reason, oc_reason, climate_reason] if "not provided" in r
        ]
        if crop["requires_irrigation_if_dry"] and not irrigation_available:
            data_limitations.append(
                "This crop typically needs irrigation if seasonal rainfall falls short — "
                "verify irrigation availability before planting"
            )

        results.append(
            CropScore(
                key=crop["key"],
                name=crop["name"],
                score=round(final_score, 1),
                confidence=confidence,
                reasons=reasons,
                limiting_factors=limiting,
                season=crop["season"],
                duration_days=tuple(crop["duration_days"]),
                water_need=crop["water_need"],
                data_limitations=data_limitations,
            )
        )

    results.sort(key=lambda r: r.score, reverse=True)
    return results
