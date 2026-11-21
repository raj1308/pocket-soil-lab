from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.soil import SoilMeasurement, SoilSample
from app.schemas.soil import ManualSoilEntryRequest, MeasurementOut, SoilSampleOut
from app.services.demo_soil_profiles import DEMO_PROFILES, MEASUREMENT_METHODS, MEASUREMENT_UNITS
from app.services.soil import classify_usda_texture, validate_ph, validate_texture_sum

router = APIRouter(prefix="/api/soil", tags=["soil"])

NUMERIC_FIELDS = [
    "ph",
    "organic_carbon_pct",
    "available_nitrogen_kg_ha",
    "available_phosphorus_kg_ha",
    "available_potassium_kg_ha",
    "sand_pct",
    "silt_pct",
    "clay_pct",
    "ec_ds_m",
    "moisture_pct",
]


def _build_sample(
    db: Session, entry: ManualSoilEntryRequest, source_type: str
) -> tuple[SoilSample, list[str]]:
    warnings = validate_texture_sum(entry.sand_pct, entry.silt_pct, entry.clay_pct)
    warnings += validate_ph(entry.ph)

    sample = SoilSample(
        farm_name=entry.farm_name,
        sampling_date=entry.sampling_date,
        sampling_depth_cm=entry.sampling_depth_cm,
        farm_area_ha=entry.farm_area_ha,
        crop_history=entry.crop_history,
        irrigation_availability=entry.irrigation_availability,
        notes=entry.notes,
        source_type=source_type,
    )
    db.add(sample)
    db.flush()

    for field in NUMERIC_FIELDS:
        value = getattr(entry, field)
        if value is None:
            continue
        db.add(
            SoilMeasurement(
                sample_id=sample.id,
                property=field,
                value=value,
                unit=MEASUREMENT_UNITS.get(field, ""),
                method=MEASUREMENT_METHODS.get(field),
                source_type=source_type,
                reliability="standard",
            )
        )
    db.commit()
    db.refresh(sample)
    return sample, warnings


def _to_out(sample: SoilSample, warnings: list[str] | None = None) -> SoilSampleOut:
    by_prop = {m.property: m for m in sample.measurements}
    texture_class = None
    if "sand_pct" in by_prop and "silt_pct" in by_prop and "clay_pct" in by_prop:
        texture_class = classify_usda_texture(
            by_prop["sand_pct"].value, by_prop["silt_pct"].value, by_prop["clay_pct"].value
        )
    return SoilSampleOut(
        id=sample.id,
        farm_name=sample.farm_name,
        sampling_date=sample.sampling_date,
        sampling_depth_cm=sample.sampling_depth_cm,
        farm_area_ha=sample.farm_area_ha,
        crop_history=sample.crop_history,
        irrigation_availability=sample.irrigation_availability,
        notes=sample.notes,
        source_type=sample.source_type,
        texture_class=texture_class,
        measurements=[
            MeasurementOut(
                property=m.property,
                value=m.value,
                unit=m.unit,
                method=m.method,
                source_type=m.source_type,
                uncertainty=m.uncertainty,
                reliability=m.reliability,
            )
            for m in sample.measurements
        ],
        warnings=warnings or [],
    )


@router.post("/manual", response_model=SoilSampleOut)
def submit_manual_entry(entry: ManualSoilEntryRequest, db: Session = Depends(get_db)) -> SoilSampleOut:
    sample, warnings = _build_sample(db, entry, source_type="manually_entered")
    return _to_out(sample, warnings)


@router.get("/samples", response_model=list[SoilSampleOut])
def list_samples(db: Session = Depends(get_db)) -> list[SoilSampleOut]:
    samples = db.query(SoilSample).order_by(SoilSample.created_at.desc()).all()
    return [_to_out(s) for s in samples]


@router.get("/samples/{sample_id}", response_model=SoilSampleOut)
def get_sample(sample_id: int, db: Session = Depends(get_db)) -> SoilSampleOut:
    sample = db.get(SoilSample, sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return _to_out(sample)


@router.get("/demo")
def list_demo_profiles() -> list[dict]:
    return [
        {"key": p["key"], "label": p["label"], "description": p["description"]} for p in DEMO_PROFILES
    ]


@router.post("/demo/{key}", response_model=SoilSampleOut)
def load_demo_profile(key: str, db: Session = Depends(get_db)) -> SoilSampleOut:
    profile = next((p for p in DEMO_PROFILES if p["key"] == key), None)
    if not profile:
        raise HTTPException(status_code=404, detail="Unknown demo profile")
    entry = ManualSoilEntryRequest(**profile["entry"])
    sample, warnings = _build_sample(db, entry, source_type="demonstration_data")
    return _to_out(sample, warnings)
