from pydantic import BaseModel


class GeocodeResult(BaseModel):
    name: str
    admin1: str | None = None
    country: str | None = None
    latitude: float
    longitude: float
    timezone: str


class CurrentConditions(BaseModel):
    time: str
    temperature_c: float
    relative_humidity_pct: float | None = None
    precipitation_mm: float | None = None
    wind_speed_kmh: float | None = None
    wind_direction_deg: float | None = None


class DailyForecastDay(BaseModel):
    date: str
    temp_max_c: float
    temp_min_c: float
    precipitation_sum_mm: float | None = None
    precipitation_probability_max_pct: float | None = None
    wind_speed_max_kmh: float | None = None
    shortwave_radiation_sum_mj: float | None = None
    et0_fao_evapotranspiration_mm: float | None = None


class HourlyForecastPoint(BaseModel):
    time: str
    temperature_c: float
    precipitation_probability_pct: float | None = None
    relative_humidity_pct: float | None = None


class Advisory(BaseModel):
    severity: str  # "info" | "caution" | "warning"
    title: str
    message: str


class ForecastResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    source: str = "Open-Meteo forecast API"
    retrieved_at: str
    is_cached: bool
    current: CurrentConditions | None = None
    hourly: list[HourlyForecastPoint]
    daily: list[DailyForecastDay]
    advisories: list[Advisory]
    disclaimer: str = (
        "Forecast data from Open-Meteo; not a measurement. Accuracy decreases with lead time. "
        "This is weather, not growing-season climate — do not use a 7-day forecast as a substitute "
        "for seasonal climatology when assessing long-term crop suitability."
    )
