from datetime import date

from pydantic import BaseModel, Field, field_validator


class ManualSoilEntryRequest(BaseModel):
    farm_name: str | None = None
    sampling_date: date | None = None
    sampling_depth_cm: float | None = Field(default=None, ge=0, le=200)
    farm_area_ha: float | None = Field(default=None, gt=0)
    crop_history: str | None = None
    irrigation_availability: str | None = None
    notes: str | None = None

    ph: float | None = Field(default=None, ge=0, le=14)
    organic_carbon_pct: float | None = Field(default=None, ge=0, le=20)
    available_nitrogen_kg_ha: float | None = Field(default=None, ge=0)
    available_phosphorus_kg_ha: float | None = Field(default=None, ge=0)
    available_potassium_kg_ha: float | None = Field(default=None, ge=0)
    sand_pct: float | None = Field(default=None, ge=0, le=100)
    silt_pct: float | None = Field(default=None, ge=0, le=100)
    clay_pct: float | None = Field(default=None, ge=0, le=100)
    ec_ds_m: float | None = Field(default=None, ge=0, le=50)
    moisture_pct: float | None = Field(default=None, ge=0, le=100)

    @field_validator("ph")
    @classmethod
    def warn_unusual_ph(cls, v: float | None) -> float | None:
        # 0-14 is physically valid; 3-10 covers virtually all agricultural soils.
        # Outside that is accepted but flagged as unusual by the service layer, not rejected here.
        return v


class MeasurementOut(BaseModel):
    property: str
    value: float
    unit: str
    method: str | None
    source_type: str
    uncertainty: str | None
    reliability: str


class SoilSampleOut(BaseModel):
    id: int
    farm_name: str | None
    sampling_date: date | None
    sampling_depth_cm: float | None
    farm_area_ha: float | None
    crop_history: str | None
    irrigation_availability: str | None
    notes: str | None
    source_type: str
    texture_class: str | None
    measurements: list[MeasurementOut]
    warnings: list[str] = []

    model_config = {"from_attributes": True}


class DemoSoilProfile(BaseModel):
    key: str
    label: str
    description: str
    data_label: str = "Sample dataset — not a real-time soil measurement."
    entry: ManualSoilEntryRequest
