"""Fertilizer dose calculation — deliberately conservative (master spec Part 9).

Scope and honesty notes, read before touching the numbers below:

- Crop nutrient requirements (`CROP_NPK_REQUIREMENT_KG_HA`) are generic, widely
  taught Indian agronomy figures (N-P2O5-K2O kg/ha under irrigated conditions).
  They are illustrative teaching figures, NOT an official state package of
  practices — the API response says so every time, and callers must not
  present them as precise/official.
- Soil-test fertility classes (`classify_fertility`) use commonly published
  general thresholds for the alkaline-KMnO4 N / Olsen P / ammonium-acetate K
  methods (matching this project's course material) — again illustrative
  thresholds, not a specific state lab's exact cutoffs.
- The Low/Medium/High -> dose adjustment (+25% / unchanged / -25%) is a
  standard simplified extension-teaching heuristic, not a precision
  recommendation. This is stated in the output, not just this comment.
- Elemental <-> oxide conversions (P2O5->P, K2O->K) and fertilizer product
  compositions (Urea, DAP, MOP) use standard, well-established chemistry
  constants, not estimates.
- If available N/P/K are missing, the module refuses to guess a dose and
  returns the exact guardrail message the master spec specifies.
"""

from dataclasses import dataclass

# N-P2O5-K2O kg/ha, generic irrigated-condition figures for teaching/demo use.
CROP_NPK_REQUIREMENT_KG_HA: dict[str, tuple[float, float, float]] = {
    "rice": (100, 50, 50),
    "wheat": (120, 60, 40),
    "maize": (120, 60, 40),
    "potato": (150, 80, 100),
    "mustard": (80, 40, 40),
    "groundnut": (25, 50, 75),
    "chickpea": (20, 40, 20),
    "pigeon_pea": (25, 50, 30),
    "green_gram": (20, 40, 20),
    "soybean": (30, 60, 40),
}

# Illustrative general fertility thresholds (kg/ha), matching the alkaline-KMnO4
# (N), Olsen (P), ammonium-acetate (K) methods used elsewhere in this project.
FERTILITY_THRESHOLDS_KG_HA = {
    "available_nitrogen_kg_ha": {"low": 280, "high": 560},
    "available_phosphorus_kg_ha": {"low": 10, "high": 25},
    "available_potassium_kg_ha": {"low": 110, "high": 280},
}

FERTILITY_ADJUSTMENT = {"low": 1.25, "medium": 1.0, "high": 0.75}

# Standard nutrient composition of common fertilizer products.
UREA_N_FRACTION = 0.46
DAP_N_FRACTION = 0.18
DAP_P2O5_FRACTION = 0.46
MOP_K2O_FRACTION = 0.60

# Standard oxide<->elemental conversion factors.
P2O5_TO_P = 0.4364
K2O_TO_K = 0.8301


def ha_to_acres(ha: float) -> float:
    return ha * 2.47105


def acres_to_ha(acres: float) -> float:
    return acres / 2.47105


def classify_fertility(property_key: str, value: float) -> str:
    thresholds = FERTILITY_THRESHOLDS_KG_HA[property_key]
    if value < thresholds["low"]:
        return "low"
    if value > thresholds["high"]:
        return "high"
    return "medium"


@dataclass
class ProductQuantities:
    urea_kg: float
    dap_kg: float
    mop_kg: float
    n_applied_kg: float
    p2o5_applied_kg: float
    k2o_applied_kg: float


def compute_product_quantities(
    n_required_kg_ha: float, p2o5_required_kg_ha: float, k2o_required_kg_ha: float, area_ha: float
) -> ProductQuantities:
    """Convert a N-P2O5-K2O requirement (kg/ha) into Urea/DAP/MOP masses for
    the given area, applying DAP first (to meet P2O5) and crediting its N
    contribution against the N requirement before topping up with Urea — this
    avoids double-counting nitrogen that DAP already supplies."""
    if area_ha <= 0:
        raise ValueError("area_ha must be positive")

    n_total = n_required_kg_ha * area_ha
    p2o5_total = p2o5_required_kg_ha * area_ha
    k2o_total = k2o_required_kg_ha * area_ha

    dap_kg = p2o5_total / DAP_P2O5_FRACTION if p2o5_total > 0 else 0.0
    n_from_dap = dap_kg * DAP_N_FRACTION
    n_remaining = max(0.0, n_total - n_from_dap)
    urea_kg = n_remaining / UREA_N_FRACTION if n_remaining > 0 else 0.0
    mop_kg = k2o_total / MOP_K2O_FRACTION if k2o_total > 0 else 0.0

    n_applied = n_from_dap + urea_kg * UREA_N_FRACTION
    p2o5_applied = dap_kg * DAP_P2O5_FRACTION
    k2o_applied = mop_kg * MOP_K2O_FRACTION

    return ProductQuantities(
        urea_kg=round(urea_kg, 1),
        dap_kg=round(dap_kg, 1),
        mop_kg=round(mop_kg, 1),
        n_applied_kg=round(n_applied, 1),
        p2o5_applied_kg=round(p2o5_applied, 1),
        k2o_applied_kg=round(k2o_applied, 1),
    )


INSUFFICIENT_DATA_MESSAGE = (
    "Insufficient validated nutrient information for an exact fertilizer recommendation. "
    "Please enter a recent soil-test result."
)


@dataclass
class FertilizerRecommendation:
    crop_key: str
    area_ha: float
    fertility_classes: dict[str, str]
    adjusted_requirement_kg_ha: tuple[float, float, float]
    quantities: ProductQuantities
    estimated_cost: float | None
    assumptions: list[str]
    disclaimer: str


def recommend_fertilizer(
    *,
    crop_key: str,
    area_ha: float,
    available_nitrogen_kg_ha: float | None,
    available_phosphorus_kg_ha: float | None,
    available_potassium_kg_ha: float | None,
    urea_price_per_kg: float | None = None,
    dap_price_per_kg: float | None = None,
    mop_price_per_kg: float | None = None,
) -> FertilizerRecommendation | str:
    """Returns a FertilizerRecommendation, or the guardrail message (str) when
    the soil-test inputs required for a dose are missing."""
    if crop_key not in CROP_NPK_REQUIREMENT_KG_HA:
        raise ValueError(f"Unknown crop: {crop_key}")
    if (
        available_nitrogen_kg_ha is None
        or available_phosphorus_kg_ha is None
        or available_potassium_kg_ha is None
    ):
        return INSUFFICIENT_DATA_MESSAGE

    n_class = classify_fertility("available_nitrogen_kg_ha", available_nitrogen_kg_ha)
    p_class = classify_fertility("available_phosphorus_kg_ha", available_phosphorus_kg_ha)
    k_class = classify_fertility("available_potassium_kg_ha", available_potassium_kg_ha)

    base_n, base_p2o5, base_k2o = CROP_NPK_REQUIREMENT_KG_HA[crop_key]
    adj_n = base_n * FERTILITY_ADJUSTMENT[n_class]
    adj_p2o5 = base_p2o5 * FERTILITY_ADJUSTMENT[p_class]
    adj_k2o = base_k2o * FERTILITY_ADJUSTMENT[k_class]

    quantities = compute_product_quantities(adj_n, adj_p2o5, adj_k2o, area_ha)
    cost = estimate_cost(quantities, urea_price_per_kg, dap_price_per_kg, mop_price_per_kg)

    assumptions = [
        f"Base requirement for {crop_key} ({base_n}-{base_p2o5}-{base_k2o} kg/ha N-P2O5-K2O) is a "
        "generic irrigated-condition teaching figure, not an official state package of practices.",
        f"Soil fertility classed as N:{n_class}, P:{p_class}, K:{k_class} against general "
        "published thresholds for these test methods, then the base requirement was adjusted "
        "+25%/unchanged/-25% — a simplified extension heuristic, not a precision rate.",
    ]
    if cost is None:
        assumptions.append("No fertilizer prices supplied — cost estimate omitted.")

    return FertilizerRecommendation(
        crop_key=crop_key,
        area_ha=area_ha,
        fertility_classes={"nitrogen": n_class, "phosphorus": p_class, "potassium": k_class},
        adjusted_requirement_kg_ha=(round(adj_n, 1), round(adj_p2o5, 1), round(adj_k2o, 1)),
        quantities=quantities,
        estimated_cost=cost,
        assumptions=assumptions,
        disclaimer=(
            "Illustrative fertilizer guidance for a classroom decision-support demo — verify "
            "against your state agricultural department's package of practices before field use."
        ),
    )


def estimate_cost(
    quantities: ProductQuantities,
    urea_price_per_kg: float | None,
    dap_price_per_kg: float | None,
    mop_price_per_kg: float | None,
) -> float | None:
    if urea_price_per_kg is None or dap_price_per_kg is None or mop_price_per_kg is None:
        return None
    return round(
        quantities.urea_kg * urea_price_per_kg
        + quantities.dap_kg * dap_price_per_kg
        + quantities.mop_kg * mop_price_per_kg,
        2,
    )
