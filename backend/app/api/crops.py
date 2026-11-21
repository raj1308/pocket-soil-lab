from fastapi import APIRouter

from app.schemas.crops import CropRecommendationOut, CropRecommendationRequest, CropRecommendationResponse
from app.services.crop_catalog import CROPS
from app.services.crop_recommendation import score_crops

router = APIRouter(prefix="/api/crops", tags=["crops"])


@router.get("/catalog")
def get_catalog() -> list[dict]:
    return [{"key": c["key"], "name": c["name"], "season": c["season"]} for c in CROPS]


@router.post("/recommend", response_model=CropRecommendationResponse)
def recommend(req: CropRecommendationRequest) -> CropRecommendationResponse:
    scores = score_crops(
        texture_class=req.texture_class,
        ph=req.ph,
        organic_carbon_pct=req.organic_carbon_pct,
        irrigation_available=req.irrigation_available,
        expected_season_temp_c=req.expected_season_temp_c,
        expected_season_rainfall_mm=req.expected_season_rainfall_mm,
        season_filter=req.season_filter,
    )
    top = scores[:3]
    return CropRecommendationResponse(
        recommendations=[
            CropRecommendationOut(
                key=s.key,
                name=s.name,
                score=s.score,
                confidence=s.confidence,
                reasons=s.reasons,
                limiting_factors=s.limiting_factors,
                season=s.season,
                duration_days_min=s.duration_days[0],
                duration_days_max=s.duration_days[1],
                water_need=s.water_need,
                data_limitations=s.data_limitations,
            )
            for s in top
        ]
    )
