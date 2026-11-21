export interface Measurement {
  property: string
  value: number
  unit: string
  method: string | null
  source_type: string
  uncertainty: string | null
  reliability: string
}

export interface SoilSample {
  id: number
  farm_name: string | null
  sampling_date: string | null
  sampling_depth_cm: number | null
  farm_area_ha: number | null
  crop_history: string | null
  irrigation_availability: string | null
  notes: string | null
  source_type: string
  texture_class: string | null
  measurements: Measurement[]
  warnings: string[]
}

export interface DemoProfileSummary {
  key: string
  label: string
  description: string
}

export interface ManualSoilEntry {
  farm_name?: string
  sampling_date?: string
  sampling_depth_cm?: number
  farm_area_ha?: number
  crop_history?: string
  irrigation_availability?: string
  notes?: string
  ph?: number
  organic_carbon_pct?: number
  available_nitrogen_kg_ha?: number
  available_phosphorus_kg_ha?: number
  available_potassium_kg_ha?: number
  sand_pct?: number
  silt_pct?: number
  clay_pct?: number
  ec_ds_m?: number
  moisture_pct?: number
}

const SOURCE_LABELS: Record<string, string> = {
  manually_entered: 'Manually entered',
  demonstration_data: 'Demonstration data',
  laboratory_measured: 'Laboratory measured',
  sensor_measured: 'Sensor measured',
  ml_predicted: 'ML predicted',
  regional_estimate: 'Regional estimate',
}

export function sourceLabel(sourceType: string): string {
  return SOURCE_LABELS[sourceType] ?? sourceType
}

export function measurementValue(sample: SoilSample, property: string): number | null {
  return sample.measurements.find((m) => m.property === property)?.value ?? null
}
