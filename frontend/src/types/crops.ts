export interface CropRecommendation {
  key: string
  name: string
  score: number
  confidence: 'high' | 'medium' | 'low'
  reasons: string[]
  limiting_factors: string[]
  season: string
  duration_days_min: number
  duration_days_max: number
  water_need: string
  data_limitations: string[]
}

export interface CropRecommendationResponse {
  recommendations: CropRecommendation[]
  disclaimer: string
}

export interface CropRecommendationRequest {
  texture_class?: string | null
  ph?: number | null
  organic_carbon_pct?: number | null
  irrigation_available?: boolean
  expected_season_temp_c?: number | null
  expected_season_rainfall_mm?: number | null
  season_filter?: string | null
}
