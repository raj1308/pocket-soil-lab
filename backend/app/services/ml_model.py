"""Loads the trained SOC VisNIR model once and serves validated predictions.

Spectral CSV upload contract (master spec Part 5 Mode 2 / Part 6): the
uploaded wavelength grid must exactly match the grid the model was trained
on. We do not interpolate or resample a mismatched grid onto the model's
grid — per the course's own "spectral resolution vs. sampling interval"
lesson, resampling a coarser or differently-aligned instrument's spectrum
doesn't manufacture the missing information, so a mismatch is rejected with
an explanatory error rather than silently forced through the model.
"""
import json
import sys
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

# The saved model pipeline was pickled with its custom SNV/Savitzky-Golay
# transformer classes importable as a bare `preprocessing` module (see
# ml/scripts/03_train_evaluate.py's sys.path setup) — unpickling needs that
# same module path available here too, or joblib.load fails to resolve them.
PIPELINES_DIR = Path(__file__).resolve().parents[3] / "ml" / "pipelines"
if str(PIPELINES_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINES_DIR))

ARTIFACTS_DIR = Path(__file__).resolve().parents[3] / "ml" / "artifacts"
MODEL_VERSION = "soc-visnir-rf-v1"
REFLECTANCE_MIN, REFLECTANCE_MAX = -0.05, 1.2


class SpectrumValidationError(Exception):
    pass


class ModelNotAvailableError(Exception):
    pass


@lru_cache(maxsize=1)
def _load() -> tuple:
    model_path = ARTIFACTS_DIR / f"{MODEL_VERSION}.joblib"
    metadata_path = ARTIFACTS_DIR / f"{MODEL_VERSION}.metadata.json"
    if not model_path.exists() or not metadata_path.exists():
        raise ModelNotAvailableError(
            f"Model artifacts not found at {ARTIFACTS_DIR}. Run ml/scripts/03_train_evaluate.py first."
        )
    model = joblib.load(model_path)
    metadata = json.loads(metadata_path.read_text())
    return model, metadata


def get_metadata() -> dict:
    _, metadata = _load()
    return metadata


def validate_wavelength_grid(wavelengths: list[float]) -> None:
    _, metadata = _load()
    required = metadata["required_wavelength_grid"]
    if len(wavelengths) != len(required):
        raise SpectrumValidationError(
            f"Uploaded spectrum has {len(wavelengths)} wavelength points; this model requires "
            f"exactly {len(required)} points on a {metadata['wavelength_range_nm'][0]}-"
            f"{metadata['wavelength_range_nm'][1]}nm grid at {metadata['wavelength_step_nm']}nm "
            "steps. A finer or coarser grid is not resampled onto this one — interpolating "
            "doesn't manufacture spectral information the instrument didn't measure, so the "
            "upload is rejected rather than silently forced through the model. Please export your "
            "spectrum on the exact required grid."
        )
    mismatches = [
        (i, got, exp)
        for i, (got, exp) in enumerate(zip(wavelengths, required))
        if abs(got - exp) > 1e-6
    ]
    if mismatches:
        i, got, exp = mismatches[0]
        raise SpectrumValidationError(
            f"Wavelength grid doesn't match at position {i}: got {got}nm, expected {exp}nm. "
            f"This model requires an exact {metadata['wavelength_range_nm'][0]}-"
            f"{metadata['wavelength_range_nm'][1]}nm grid at {metadata['wavelength_step_nm']}nm "
            "steps, in ascending order."
        )


def validate_reflectance_values(sample_id: str, values: list[float]) -> None:
    arr = np.array(values, dtype=np.float64)
    if np.isnan(arr).any():
        raise SpectrumValidationError(f"Sample '{sample_id}' has missing (NaN) reflectance values.")
    out_of_range = (arr < REFLECTANCE_MIN) | (arr > REFLECTANCE_MAX)
    if out_of_range.any():
        raise SpectrumValidationError(
            f"Sample '{sample_id}' has reflectance values outside the plausible "
            f"[{REFLECTANCE_MIN}, {REFLECTANCE_MAX}] range (e.g. {arr[out_of_range][0]:.3f}). "
            "This model expects already dark/white-referenced reflectance "
            "(R = (I_sample - I_dark) / (I_white - I_dark)), not raw detector counts."
        )


def predict_organic_carbon(reflectance: list[float]) -> dict:
    model, metadata = _load()
    X = np.array(reflectance, dtype=np.float64).reshape(1, -1)
    pred_log = model.predict(X)
    pred = float(np.expm1(np.asarray(pred_log).ravel()[0]))
    pred = max(0.0, pred)

    best_model_metrics = metadata["model_comparison"][metadata["model_algorithm"]]
    return {
        "value": round(pred, 2),
        "unit": metadata["target_unit"],
        "model_version": metadata["model_version"],
        "method": (
            f"VisNIR spectroscopy, {metadata['model_algorithm']} regression "
            f"(trained on {metadata['dataset_source']})"
        ),
        "test_rmse": round(best_model_metrics["rmse"], 2),
        "test_r2": round(best_model_metrics["r2"], 3),
        "reliability_note": (
            "Held-out test R²={:.2f}, but a leave-one-dataset-out check found this model's "
            "accuracy varies substantially by how similar the sample is to its training data "
            "(R² ranged from -0.27 to 0.92 across held-out source datasets — see "
            "ml/evaluation/{}_report.md). Treat this as ML-predicted, not lab-equivalent."
        ).format(best_model_metrics["r2"], metadata["model_version"]),
    }
