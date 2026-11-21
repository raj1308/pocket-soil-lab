export interface GeocodeResult {
  name: string
  admin1: string | null
  country: string | null
  latitude: number
  longitude: number
  timezone: string
}

export interface CurrentConditions {
  time: string
  temperature_c: number
  relative_humidity_pct: number | null
  precipitation_mm: number | null
  wind_speed_kmh: number | null
  wind_direction_deg: number | null
}

export interface DailyForecastDay {
  date: string
  temp_max_c: number
  temp_min_c: number
  precipitation_sum_mm: number | null
  precipitation_probability_max_pct: number | null
  wind_speed_max_kmh: number | null
  shortwave_radiation_sum_mj: number | null
  et0_fao_evapotranspiration_mm: number | null
}

export interface HourlyForecastPoint {
  time: string
  temperature_c: number
  precipitation_probability_pct: number | null
  relative_humidity_pct: number | null
}

export interface Advisory {
  severity: 'info' | 'caution' | 'warning'
  title: string
  message: string
}

export interface ForecastResponse {
  latitude: number
  longitude: number
  timezone: string
  source: string
  retrieved_at: string
  is_cached: boolean
  current: CurrentConditions | null
  hourly: HourlyForecastPoint[]
  daily: DailyForecastDay[]
  advisories: Advisory[]
  disclaimer: string
}

export interface Location {
  name: string
  admin1?: string | null
  country?: string | null
  latitude: number
  longitude: number
}
