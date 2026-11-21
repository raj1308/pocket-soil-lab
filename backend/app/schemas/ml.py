from pydantic import BaseModel


class SpectralPrediction(BaseModel):
    sample_id: str
    organic_carbon_pct: float
    unit: str
    model_version: str
    method: str
    test_rmse: float
    test_r2: float
    reliability_note: str


class SpectralPredictionResponse(BaseModel):
    predictions: list[SpectralPrediction]
    model_metadata: dict
