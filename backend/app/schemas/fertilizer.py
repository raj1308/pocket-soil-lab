from pydantic import BaseModel


class FertilizerRequest(BaseModel):
    crop_key: str
    area_ha: float
    available_nitrogen_kg_ha: float | None = None
    available_phosphorus_kg_ha: float | None = None
    available_potassium_kg_ha: float | None = None
    urea_price_per_kg: float | None = None
    dap_price_per_kg: float | None = None
    mop_price_per_kg: float | None = None


class FertilizerResponse(BaseModel):
    sufficient_data: bool
    message: str | None = None
    fertility_classes: dict[str, str] | None = None
    adjusted_requirement_kg_ha: dict[str, float] | None = None
    urea_kg: float | None = None
    dap_kg: float | None = None
    mop_kg: float | None = None
    estimated_cost: float | None = None
    assumptions: list[str] = []
    disclaimer: str | None = None
