import pytest

from app.services.fertilizer import (
    FertilizerRecommendation,
    classify_fertility,
    compute_product_quantities,
    estimate_cost,
    ha_to_acres,
    acres_to_ha,
    recommend_fertilizer,
)


def test_ha_to_acres_and_back():
    assert ha_to_acres(1) == pytest.approx(2.47105, rel=1e-4)
    assert acres_to_ha(ha_to_acres(3.5)) == pytest.approx(3.5, rel=1e-6)


def test_classify_fertility_boundaries():
    assert classify_fertility("available_nitrogen_kg_ha", 100) == "low"
    assert classify_fertility("available_nitrogen_kg_ha", 280) == "medium"
    assert classify_fertility("available_nitrogen_kg_ha", 560) == "medium"
    assert classify_fertility("available_nitrogen_kg_ha", 600) == "high"


def test_compute_product_quantities_no_double_counts_dap_nitrogen():
    # N=100, P2O5=50, K2O=50 kg/ha over 1 ha.
    q = compute_product_quantities(100, 50, 50, area_ha=1)
    # DAP alone supplies all the P2O5: 50 / 0.46 kg DAP
    assert q.dap_kg == pytest.approx(50 / 0.46, rel=1e-3)
    # That DAP already contributes some N; Urea should only make up the rest.
    n_from_dap = q.dap_kg * 0.18
    assert n_from_dap > 0
    assert q.urea_kg == pytest.approx((100 - n_from_dap) / 0.46, rel=1e-3)
    assert q.n_applied_kg == pytest.approx(100, abs=0.5)
    assert q.p2o5_applied_kg == pytest.approx(50, abs=0.5)
    assert q.mop_kg == pytest.approx(50 / 0.60, rel=1e-3)
    assert q.k2o_applied_kg == pytest.approx(50, abs=0.5)


def test_compute_product_quantities_scales_with_area():
    # Each call rounds its own output to 1 decimal, so compare the unrounded
    # relationship with a tolerance matching that rounding step, not exact equality.
    one_ha = compute_product_quantities(100, 50, 50, area_ha=1)
    two_ha = compute_product_quantities(100, 50, 50, area_ha=2)
    assert two_ha.urea_kg == pytest.approx(one_ha.urea_kg * 2, abs=0.2)
    assert two_ha.dap_kg == pytest.approx(one_ha.dap_kg * 2, abs=0.2)
    assert two_ha.mop_kg == pytest.approx(one_ha.mop_kg * 2, abs=0.2)


def test_compute_product_quantities_rejects_nonpositive_area():
    with pytest.raises(ValueError):
        compute_product_quantities(100, 50, 50, area_ha=0)


def test_estimate_cost_requires_all_three_prices():
    q = compute_product_quantities(100, 50, 50, area_ha=1)
    assert estimate_cost(q, None, 30, 20) is None
    assert estimate_cost(q, 6, 30, 20) is not None


def test_estimate_cost_is_sum_of_products():
    q = compute_product_quantities(100, 50, 50, area_ha=1)
    cost = estimate_cost(q, urea_price_per_kg=6, dap_price_per_kg=30, mop_price_per_kg=20)
    expected = q.urea_kg * 6 + q.dap_kg * 30 + q.mop_kg * 20
    assert cost == pytest.approx(expected, rel=1e-6)


def test_recommend_fertilizer_returns_guardrail_message_when_data_missing():
    result = recommend_fertilizer(
        crop_key="rice",
        area_ha=1,
        available_nitrogen_kg_ha=None,
        available_phosphorus_kg_ha=20,
        available_potassium_kg_ha=150,
    )
    assert isinstance(result, str)
    assert "Insufficient validated nutrient information" in result


def test_recommend_fertilizer_full_result_when_data_present():
    result = recommend_fertilizer(
        crop_key="rice",
        area_ha=2,
        available_nitrogen_kg_ha=150,  # low
        available_phosphorus_kg_ha=15,  # medium
        available_potassium_kg_ha=350,  # high
    )
    assert isinstance(result, FertilizerRecommendation)
    assert result.fertility_classes == {"nitrogen": "low", "phosphorus": "medium", "potassium": "high"}
    # rice base is (100, 50, 50); low->*1.25, medium->*1.0, high->*0.75
    assert result.adjusted_requirement_kg_ha == (125.0, 50.0, 37.5)
    assert result.estimated_cost is None  # no prices supplied


def test_recommend_fertilizer_rejects_unknown_crop():
    with pytest.raises(ValueError):
        recommend_fertilizer(
            crop_key="dragonfruit",
            area_ha=1,
            available_nitrogen_kg_ha=100,
            available_phosphorus_kg_ha=10,
            available_potassium_kg_ha=100,
        )
