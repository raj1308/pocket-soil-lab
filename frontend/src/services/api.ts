import type { HealthResponse } from '../types'
import type { ForecastResponse, GeocodeResult } from '../types/weather'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {}

async function request<T>(path: string): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`)
  } catch {
    throw new ApiError('Could not reach the backend. Is it running?')
  }
  if (!response.ok) {
    throw new ApiError(`Backend returned ${response.status} for ${path}`)
  }
  return response.json() as Promise<T>
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health')
}

export function searchLocation(query: string): Promise<GeocodeResult[]> {
  return request<GeocodeResult[]>(`/api/weather/geocode?q=${encodeURIComponent(query)}`)
}

export function getForecast(latitude: number, longitude: number): Promise<ForecastResponse> {
  return request<ForecastResponse>(
    `/api/weather/forecast?latitude=${latitude}&longitude=${longitude}`,
  )
}
