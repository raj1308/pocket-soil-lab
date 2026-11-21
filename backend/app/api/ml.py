import io

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.ml import SpectralPrediction, SpectralPredictionResponse
from app.services.ml_model import (
    ModelNotAvailableError,
    SpectrumValidationError,
    get_metadata,
    predict_organic_carbon,
    validate_reflectance_values,
    validate_wavelength_grid,
)

router = APIRouter(prefix="/api/soil", tags=["ml"])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5MB — a 1076-row spectral CSV is a few hundred KB at most


@router.get("/spectra/model-info")
def model_info() -> dict:
    try:
        metadata = get_metadata()
    except ModelNotAvailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "model_version": metadata["model_version"],
        "target_property": metadata["target_property"],
        "wavelength_range_nm": metadata["wavelength_range_nm"],
        "wavelength_step_nm": metadata["wavelength_step_nm"],
        "n_wavelength_points": len(metadata["required_wavelength_grid"]),
        "csv_format": (
            "First column header 'wavelength_nm' with one row per wavelength on the exact "
            f"{metadata['wavelength_range_nm'][0]}-{metadata['wavelength_range_nm'][1]}nm grid at "
            f"{metadata['wavelength_step_nm']}nm steps, ascending. One additional column per "
            "sample (header = sample name), values = dark/white-referenced reflectance (0-1)."
        ),
    }


@router.post("/spectra/predict", response_model=SpectralPredictionResponse)
async def predict_spectra(file: UploadFile = File(...)) -> SpectralPredictionResponse:
    try:
        metadata = get_metadata()
    except ModelNotAvailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    if df.empty or df.shape[1] < 2:
        raise HTTPException(
            status_code=400,
            detail="CSV must have a 'wavelength_nm' column plus at least one sample column.",
        )

    first_col = df.columns[0]
    if first_col.strip().lower() not in ("wavelength_nm", "wavelength", "wavelength(nm)"):
        raise HTTPException(
            status_code=400,
            detail=f"First column must be named 'wavelength_nm' (got '{first_col}').",
        )

    try:
        wavelengths = df[first_col].astype(float).tolist()
        validate_wavelength_grid(wavelengths)
    except (SpectrumValidationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    predictions: list[SpectralPrediction] = []
    for sample_col in df.columns[1:]:
        try:
            values = df[sample_col].astype(float).tolist()
            validate_reflectance_values(sample_col, values)
            result = predict_organic_carbon(values)
        except SpectrumValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        predictions.append(
            SpectralPrediction(
                sample_id=str(sample_col),
                organic_carbon_pct=result["value"],
                unit=result["unit"],
                model_version=result["model_version"],
                method=result["method"],
                test_rmse=result["test_rmse"],
                test_r2=result["test_r2"],
                reliability_note=result["reliability_note"],
            )
        )

    return SpectralPredictionResponse(
        predictions=predictions,
        model_metadata={
            "model_version": metadata["model_version"],
            "training_date": metadata["training_date"],
            "dataset_source": metadata["dataset_source"],
        },
    )
