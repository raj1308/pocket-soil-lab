export interface FertilizerRequest {
  crop_key: string
  area_ha: number
  available_nitrogen_kg_ha?: number | null
  available_phosphorus_kg_ha?: number | null
  available_potassium_kg_ha?: number | null
  urea_price_per_kg?: number | null
  dap_price_per_kg?: number | null
  mop_price_per_kg?: number | null
}

export interface FertilizerResponse {
  sufficient_data: boolean
  message: string | null
  fertility_classes: Record<string, string> | null
  adjusted_requirement_kg_ha: { n: number; p2o5: number; k2o: number } | null
  urea_kg: number | null
  dap_kg: number | null
  mop_kg: number | null
  estimated_cost: number | null
  assumptions: string[]
  disclaimer: string | null
}
