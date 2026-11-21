import type { ForecastResponse, Location } from '../types/weather'
import type { SoilSample } from '../types/soil'

const LOCATION_KEY = 'pocket-soil-lab:last-location'
const FORECAST_KEY = 'pocket-soil-lab:last-forecast'
const SAMPLE_KEY = 'pocket-soil-lab:last-sample'

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

export function saveLastSample(sample: SoilSample): void {
  try {
    localStorage.setItem(SAMPLE_KEY, JSON.stringify(sample))
  } catch {
    // ignore
  }
}

export function loadLastSample(): SoilSample | null {
  try {
    const raw = localStorage.getItem(SAMPLE_KEY)
    return raw ? (JSON.parse(raw) as SoilSample) : null
  } catch {
    return null
  }
}
