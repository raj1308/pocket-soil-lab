import asyncio
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.weather import (
    Advisory,
    CurrentConditions,
    DailyForecastDay,
    ForecastResponse,
    GeocodeResult,
    HourlyForecastPoint,
)

CACHE_TTL_SECONDS = 15 * 60

# Open-Meteo's free tier rate-limits by source IP, and Render's free tier shares
# outbound IPs across many unrelated apps -- so a 429 here is often shared-tenant
# congestion rather than this app's own traffic. A short retry-with-backoff gives
# that congestion a chance to clear within one request instead of failing immediately.
_RETRYABLE_STATUS_CODES = {429, 502, 503, 504}
_RETRY_DELAYS_SECONDS = (1.0, 2.5, 5.0)


async def _get_with_retry(client: httpx.AsyncClient, url: str, params: dict[str, Any]) -> httpx.Response:
    last_exc: httpx.HTTPError | None = None
    for attempt, delay in enumerate((0.0, *_RETRY_DELAYS_SECONDS)):
        if delay:
            await asyncio.sleep(delay)
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as exc:
            last_exc = exc
            if exc.response.status_code not in _RETRYABLE_STATUS_CODES:
                raise
        except httpx.HTTPError as exc:
            last_exc = exc
    assert last_exc is not None
    raise last_exc

# In-memory cache keyed by rounded (lat, lon) — adequate for a single-process dev/demo
# deployment; a multi-worker production deployment would need a shared cache (e.g. Redis)
# instead, noted here rather than built since it's out of scope for this project's scale.
_forecast_cache: dict[tuple[float, float], dict[str, Any]] = {}


class WeatherServiceError(Exception):
    pass


def _cache_key(lat: float, lon: float) -> tuple[float, float]:
    return (round(lat, 2), round(lon, 2))


async def geocode(query: str, count: int = 5) -> list[GeocodeResult]:
    params = {"name": query, "count": count, "language": "en", "format": "json"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await _get_with_retry(client, f"{settings.open_meteo_geocoding_url}/search", params)
        except httpx.HTTPError as exc:
            raise WeatherServiceError(f"Geocoding request failed: {exc}") from exc
    payload = resp.json()
    results = payload.get("results") or []
    return [
        GeocodeResult(
            name=r["name"],
            admin1=r.get("admin1"),
            country=r.get("country"),
            latitude=r["latitude"],
            longitude=r["longitude"],
            timezone=r.get("timezone", "UTC"),
        )
        for r in results
    ]


def _build_advisories(daily: list[DailyForecastDay], hourly: list[HourlyForecastPoint]) -> list[Advisory]:
    advisories: list[Advisory] = []

    next_48h = hourly[:48]
    heavy_rain_hours = [h for h in next_48h if (h.precipitation_probability_pct or 0) >= 70]
    if heavy_rain_hours:
        advisories.append(
            Advisory(
                severity="warning",
                title="Possible heavy rainfall ahead",
                message=(
                    f"{len(heavy_rain_hours)} of the next 48 forecast hours show rainfall "
                    "probability of 70% or higher. Consider delaying fertilizer application "
                    "and checking field drainage."
                ),
            )
        )

    next_3_days = daily[:3]
    hot_days = [d for d in next_3_days if d.temp_max_c >= 38]
    if hot_days:
        advisories.append(
            Advisory(
                severity="caution",
                title="High-temperature stress risk",
                message=(
                    f"Forecast max temperature reaches {max(d.temp_max_c for d in hot_days):.1f}°C "
                    "in the next few days. Heat-sensitive crops/growth stages may need extra irrigation "
                    "or shade; verify against your crop's specific heat-stress thresholds."
                ),
            )
        )

    waterlog_risk_days = [d for d in next_3_days if (d.precipitation_sum_mm or 0) >= 40]
    if waterlog_risk_days:
        advisories.append(
            Advisory(
                severity="warning",
                title="Possible waterlogging risk",
                message=(
                    "Forecast rainfall exceeds 40mm on at least one of the next 3 days. "
                    "Fields with poor drainage may be at risk of waterlogging — avoid heavy irrigation "
                    "around these dates."
                ),
            )
        )

    fertilizer_caution_days = [d for d in next_3_days if (d.precipitation_probability_max_pct or 0) >= 60]
    if fertilizer_caution_days:
        advisories.append(
            Advisory(
                severity="caution",
                title="Fertilizer timing caution",
                message=(
                    "Rain probability is 60% or higher on at least one of the next 3 days — applying "
                    "fertilizer shortly before heavy rain risks runoff and nutrient loss. Consider "
                    "timing application for a drier window."
                ),
            )
        )

    if not advisories:
        advisories.append(
            Advisory(
                severity="info",
                title="No notable weather risks flagged",
                message=(
                    "Based on the current forecast, none of the configured rainfall/heat/waterlogging "
                    "thresholds are triggered for the next few days. This is not a guarantee — always "
                    "verify against the full forecast before field operations."
                ),
            )
        )

    return advisories


async def get_forecast(lat: float, lon: float) -> ForecastResponse:
    key = _cache_key(lat, lon)
    now = datetime.now(timezone.utc)
    cached = _forecast_cache.get(key)
    if cached and (now - cached["fetched_at"]).total_seconds() < CACHE_TTL_SECONDS:
        response = cached["response"].model_copy(update={"is_cached": True})
        return response

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m",
        "daily": (
            "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,"
            "wind_speed_10m_max,shortwave_radiation_sum,et0_fao_evapotranspiration"
        ),
        "hourly": "temperature_2m,precipitation_probability,relative_humidity_2m",
        "timezone": "auto",
        "forecast_days": 7,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await _get_with_retry(client, f"{settings.open_meteo_base_url}/forecast", params)
        except httpx.HTTPError as exc:
            if cached:
                stale = cached["response"].model_copy(update={"is_cached": True})
                return stale
            raise WeatherServiceError(f"Weather forecast request failed: {exc}") from exc

    payload = resp.json()

    current_block = payload.get("current")
    current = None
    if current_block:
        current = CurrentConditions(
            time=current_block["time"],
            temperature_c=current_block["temperature_2m"],
            relative_humidity_pct=current_block.get("relative_humidity_2m"),
            precipitation_mm=current_block.get("precipitation"),
            wind_speed_kmh=current_block.get("wind_speed_10m"),
            wind_direction_deg=current_block.get("wind_direction_10m"),
        )

    daily_block = payload["daily"]
    daily = [
        DailyForecastDay(
            date=daily_block["time"][i],
            temp_max_c=daily_block["temperature_2m_max"][i],
            temp_min_c=daily_block["temperature_2m_min"][i],
            precipitation_sum_mm=daily_block.get("precipitation_sum", [None] * len(daily_block["time"]))[i],
            precipitation_probability_max_pct=daily_block.get(
                "precipitation_probability_max", [None] * len(daily_block["time"])
            )[i],
            wind_speed_max_kmh=daily_block.get("wind_speed_10m_max", [None] * len(daily_block["time"]))[i],
            shortwave_radiation_sum_mj=daily_block.get(
                "shortwave_radiation_sum", [None] * len(daily_block["time"])
            )[i],
            et0_fao_evapotranspiration_mm=daily_block.get(
                "et0_fao_evapotranspiration", [None] * len(daily_block["time"])
            )[i],
        )
        for i in range(len(daily_block["time"]))
    ]

    hourly_block = payload["hourly"]
    hourly = [
        HourlyForecastPoint(
            time=hourly_block["time"][i],
            temperature_c=hourly_block["temperature_2m"][i],
            precipitation_probability_pct=hourly_block.get(
                "precipitation_probability", [None] * len(hourly_block["time"])
            )[i],
            relative_humidity_pct=hourly_block.get(
                "relative_humidity_2m", [None] * len(hourly_block["time"])
            )[i],
        )
        for i in range(len(hourly_block["time"]))
    ]

    response = ForecastResponse(
        latitude=payload["latitude"],
        longitude=payload["longitude"],
        timezone=payload.get("timezone", "UTC"),
        retrieved_at=now.isoformat(),
        is_cached=False,
        current=current,
        hourly=hourly,
        daily=daily,
        advisories=_build_advisories(daily, hourly),
    )

    _forecast_cache[key] = {"response": response, "fetched_at": now}
    return response
