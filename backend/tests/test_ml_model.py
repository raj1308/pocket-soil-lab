import pytest

from app.services.ml_model import (
    SpectrumValidationError,
    get_metadata,
    predict_organic_carbon,
    validate_reflectance_values,
    validate_wavelength_grid,
)


def test_model_metadata_loads():
    metadata = get_metadata()
    assert metadata["model_version"] == "soc-visnir-rf-v1"
    assert len(metadata["required_wavelength_grid"]) == 1076


def test_validate_wavelength_grid_accepts_correct_grid():
    metadata = get_metadata()
    validate_wavelength_grid(metadata["required_wavelength_grid"])  # should not raise


def test_validate_wavelength_grid_rejects_wrong_length():
    with pytest.raises(SpectrumValidationError, match="requires exactly"):
        validate_wavelength_grid([350, 352, 354])


def test_validate_wavelength_grid_rejects_misaligned_grid():
    metadata = get_metadata()
    shifted = [w + 1 for w in metadata["required_wavelength_grid"]]
    with pytest.raises(SpectrumValidationError, match="doesn't match"):
        validate_wavelength_grid(shifted)


def test_validate_reflectance_values_rejects_nan():
    with pytest.raises(SpectrumValidationError, match="missing"):
        validate_reflectance_values("sample_x", [0.1, float("nan"), 0.2])


def test_validate_reflectance_values_rejects_raw_counts():
    with pytest.raises(SpectrumValidationError, match="plausible"):
        validate_reflectance_values("sample_x", [0.1, 5000.0, 0.2])


def test_validate_reflectance_values_accepts_normal_range():
    validate_reflectance_values("sample_x", [0.0, 0.5, 1.0])  # should not raise


def test_predict_organic_carbon_returns_nonnegative_value():
    metadata = get_metadata()
    n = len(metadata["required_wavelength_grid"])
    result = predict_organic_carbon([0.1] * n)
    assert result["value"] >= 0
    assert result["unit"] == "%"
    assert result["model_version"] == "soc-visnir-rf-v1"
