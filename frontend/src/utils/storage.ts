import type { ForecastResponse, Location } from '../types/weather'

const LOCATION_KEY = 'pocket-soil-lab:last-location'
const FORECAST_KEY = 'pocket-soil-lab:last-forecast'

export function saveLocation(location: Location): void {
  try {
    localStorage.setItem(LOCATION_KEY, JSON.stringify(location))
  } catch {
    // localStorage unavailable (private mode, etc.) — not critical, just skip persistence
  }
}

export function loadLocation(): Location | null {
  try {
    const raw = localStorage.getItem(LOCATION_KEY)
    return raw ? (JSON.parse(raw) as Location) : null
  } catch {
    return null
  }
}

export function saveForecastCache(forecast: ForecastResponse): void {
  try {
    localStorage.setItem(FORECAST_KEY, JSON.stringify(forecast))
  } catch {
    // ignore
  }
}

export function loadForecastCache(): ForecastResponse | null {
  try {
    const raw = localStorage.getItem(FORECAST_KEY)
    return raw ? (JSON.parse(raw) as ForecastResponse) : null
  } catch {
    return null
  }
}
