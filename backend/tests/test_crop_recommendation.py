from app.services.crop_recommendation import score_crops


def test_missing_all_inputs_returns_no_scores():
    results = score_crops(texture_class=None, ph=None, organic_carbon_pct=None)
    assert results == []


def test_rice_favoured_for_clay_kharif_soil():
    results = score_crops(
        texture_class="clay",
        ph=6.5,
        organic_carbon_pct=0.7,
        irrigation_available=True,
        expected_season_temp_c=28,
        expected_season_rainfall_mm=1200,
        season_filter="kharif",
    )
    assert results[0].key == "rice"
    assert results[0].confidence == "high"


def test_season_filter_excludes_non_matching_crops():
    results = score_crops(texture_class="loam", ph=6.5, organic_carbon_pct=0.7, season_filter="rabi")
    assert all("rabi" in r.season for r in results)
    assert not any(r.key == "rice" for r in results)  # rice is kharif-only


def test_confidence_reflects_missing_inputs():
    full = score_crops(
        texture_class="loam",
        ph=6.5,
        organic_carbon_pct=0.7,
        expected_season_temp_c=25,
        expected_season_rainfall_mm=600,
    )
    partial = score_crops(texture_class="loam", ph=6.5, organic_carbon_pct=0.7)
    assert full[0].confidence == "high"
    assert partial[0].confidence == "medium"


def test_scores_are_sorted_descending():
    results = score_crops(texture_class="loam", ph=6.8, organic_carbon_pct=0.75)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_extreme_mismatched_inputs_score_low_not_crash():
    results = score_crops(texture_class="sand", ph=9.5, organic_carbon_pct=0.05)
    assert all(0 <= r.score <= 100 for r in results)
