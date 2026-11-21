from fastapi import APIRouter, HTTPException, Query

from app.schemas.weather import ForecastResponse, GeocodeResult
from app.services.weather import WeatherServiceError, geocode, get_forecast

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/geocode", response_model=list[GeocodeResult])
async def search_location(q: str = Query(min_length=2)) -> list[GeocodeResult]:
    try:
        return await geocode(q)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/forecast", response_model=ForecastResponse)
async def forecast(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
) -> ForecastResponse:
    try:
        return await get_forecast(latitude, longitude)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
