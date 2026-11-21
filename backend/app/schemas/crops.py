from pydantic import BaseModel


class CropRecommendationRequest(BaseModel):
    texture_class: str | None = None
    ph: float | None = None
    organic_carbon_pct: float | None = None
    irrigation_available: bool = False
    expected_season_temp_c: float | None = None
    expected_season_rainfall_mm: float | None = None
    season_filter: str | None = None


class CropRecommendationOut(BaseModel):
    key: str
    name: str
    score: float
    confidence: str
    reasons: list[str]
    limiting_factors: list[str]
    season: str
    duration_days_min: int
    duration_days_max: int
    water_need: str
    data_limitations: list[str]


class CropRecommendationResponse(BaseModel):
    recommendations: list[CropRecommendationOut]
    disclaimer: str = (
        "Rule-based suitability estimate from configured agronomic ranges — not a "
        "replacement for your state agricultural department's package of practices. "
        "Seasonal climate inputs, if provided, are regional estimates you supplied, "
        "not a measured forecast."
    )
