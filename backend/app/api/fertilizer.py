from fastapi import APIRouter, HTTPException

from app.schemas.fertilizer import FertilizerRequest, FertilizerResponse
from app.services.fertilizer import CROP_NPK_REQUIREMENT_KG_HA, recommend_fertilizer

router = APIRouter(prefix="/api/fertilizer", tags=["fertilizer"])


@router.post("/recommend", response_model=FertilizerResponse)
def recommend(req: FertilizerRequest) -> FertilizerResponse:
    if req.crop_key not in CROP_NPK_REQUIREMENT_KG_HA:
        raise HTTPException(status_code=400, detail=f"Unknown crop: {req.crop_key}")
    if req.area_ha <= 0:
        raise HTTPException(status_code=400, detail="area_ha must be positive")

    result = recommend_fertilizer(
        crop_key=req.crop_key,
        area_ha=req.area_ha,
        available_nitrogen_kg_ha=req.available_nitrogen_kg_ha,
        available_phosphorus_kg_ha=req.available_phosphorus_kg_ha,
        available_potassium_kg_ha=req.available_potassium_kg_ha,
        urea_price_per_kg=req.urea_price_per_kg,
        dap_price_per_kg=req.dap_price_per_kg,
        mop_price_per_kg=req.mop_price_per_kg,
    )

    if isinstance(result, str):
        return FertilizerResponse(sufficient_data=False, message=result)

    return FertilizerResponse(
        sufficient_data=True,
        fertility_classes=result.fertility_classes,
        adjusted_requirement_kg_ha={
            "n": result.adjusted_requirement_kg_ha[0],
            "p2o5": result.adjusted_requirement_kg_ha[1],
            "k2o": result.adjusted_requirement_kg_ha[2],
        },
        urea_kg=result.quantities.urea_kg,
        dap_kg=result.quantities.dap_kg,
        mop_kg=result.quantities.mop_kg,
        estimated_cost=result.estimated_cost,
        assumptions=result.assumptions,
        disclaimer=result.disclaimer,
    )
