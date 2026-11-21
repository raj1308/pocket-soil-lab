import type { HealthResponse } from '../types'
import type { ForecastResponse, GeocodeResult } from '../types/weather'
import type { DemoProfileSummary, ManualSoilEntry, SoilSample } from '../types/soil'
import type { CropRecommendationRequest, CropRecommendationResponse } from '../types/crops'
import type { FertilizerRequest, FertilizerResponse } from '../types/fertilizer'
import type { SpectralModelInfo, SpectralPredictionResponse } from '../types/ml'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init)
  } catch {
    throw new ApiError('Could not reach the backend. Is it running?')
  }
  if (!response.ok) {
    let detail = ''
    try {
      const body = await response.json()
      detail = body.detail ? `: ${JSON.stringify(body.detail)}` : ''
    } catch {
      // response body wasn't JSON — ignore
    }
    throw new ApiError(`Backend returned ${response.status} for ${path}${detail}`)
  }
  return response.json() as Promise<T>
}

function postJson<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
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

export function listDemoProfiles(): Promise<DemoProfileSummary[]> {
  return request<DemoProfileSummary[]>('/api/soil/demo')
}

export function loadDemoProfile(key: string): Promise<SoilSample> {
  return postJson<SoilSample>(`/api/soil/demo/${key}`, {})
}

export function submitManualEntry(entry: ManualSoilEntry): Promise<SoilSample> {
  return postJson<SoilSample>('/api/soil/manual', entry)
}

export function listSoilSamples(): Promise<SoilSample[]> {
  return request<SoilSample[]>('/api/soil/samples')
}

export function getSoilSample(id: number): Promise<SoilSample> {
  return request<SoilSample>(`/api/soil/samples/${id}`)
}

export function recommendCrops(
  req: CropRecommendationRequest,
): Promise<CropRecommendationResponse> {
  return postJson<CropRecommendationResponse>('/api/crops/recommend', req)
}

export function recommendFertilizer(req: FertilizerRequest): Promise<FertilizerResponse> {
  return postJson<FertilizerResponse>('/api/fertilizer/recommend', req)
}

export function getSpectralModelInfo(): Promise<SpectralModelInfo> {
  return request<SpectralModelInfo>('/api/soil/spectra/model-info')
}

export function predictFromSpectra(file: File): Promise<SpectralPredictionResponse> {
  const formData = new FormData()
  formData.append('file', file)
  return request<SpectralPredictionResponse>('/api/soil/spectra/predict', {
    method: 'POST',
    body: formData,
  })
}
