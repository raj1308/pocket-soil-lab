export interface SpectralModelInfo {
  model_version: string
  target_property: string
  wavelength_range_nm: [number, number]
  wavelength_step_nm: number
  n_wavelength_points: number
  csv_format: string
}

export interface SpectralPrediction {
  sample_id: string
  organic_carbon_pct: number
  unit: string
  model_version: string
  method: string
  test_rmse: number
  test_r2: number
  reliability_note: string
}

export interface SpectralPredictionResponse {
  predictions: SpectralPrediction[]
  model_metadata: Record<string, string>
}
