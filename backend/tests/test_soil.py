import pytest

from app.services.demo_soil_profiles import DEMO_PROFILES
from app.services.soil import classify_usda_texture, validate_ph, validate_texture_sum


@pytest.mark.parametrize(
    "sand,silt,clay,expected",
    [
        (90, 5, 5, "sand"),
        (20, 35, 45, "clay"),
        (40, 40, 20, "loam"),
        (55, 30, 15, "sandy loam"),
        (50, 25, 25, "sandy clay loam"),
        (10, 50, 40, "silty clay"),
        (85, 10, 5, "loamy sand"),
        (10, 85, 5, "silt"),
    ],
)
def test_classify_usda_texture_known_points(sand, silt, clay, expected):
    assert classify_usda_texture(sand, silt, clay) == expected


def test_classify_usda_texture_rejects_bad_sum():
    assert classify_usda_texture(50, 50, 50) is None  # sums to 150%


def test_classify_usda_texture_tolerates_small_rounding_error():
    # Sums to 101% — should still classify, just normalized first.
    assert classify_usda_texture(40, 41, 20) == "loam"


def test_validate_texture_sum_flags_bad_total():
    warnings = validate_texture_sum(50, 50, 50)
    assert len(warnings) == 1
    assert "100%" in warnings[0]


def test_validate_texture_sum_silent_when_fine():
    assert validate_texture_sum(40, 40, 20) == []


def test_validate_texture_sum_silent_when_incomplete():
    assert validate_texture_sum(40, None, None) == []


def test_validate_ph_flags_unusual_values():
    assert validate_ph(2.0) != []
    assert validate_ph(11.0) != []
    assert validate_ph(6.5) == []


def test_all_demo_profiles_classify_to_a_texture():
    """Guards against silently shipping a demo profile whose sand/silt/clay
    don't sum close enough to 100% to classify."""
    for profile in DEMO_PROFILES:
        e = profile["entry"]
        cls = classify_usda_texture(e["sand_pct"], e["silt_pct"], e["clay_pct"])
        assert cls is not None, f"{profile['label']} failed to classify"
