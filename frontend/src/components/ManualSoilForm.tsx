import { useState } from 'react'
import type { ManualSoilEntry } from '../types/soil'

interface Field {
  key: keyof ManualSoilEntry
  label: string
  type: 'number' | 'text' | 'date'
  step?: string
  unit?: string
}

const FIELDS: Field[] = [
  { key: 'farm_name', label: 'Farm / field name', type: 'text' },
  { key: 'sampling_date', label: 'Sampling date', type: 'date' },
  { key: 'sampling_depth_cm', label: 'Sampling depth', type: 'number', unit: 'cm' },
  { key: 'farm_area_ha', label: 'Farm area', type: 'number', unit: 'ha' },
  { key: 'ph', label: 'pH', type: 'number', step: '0.1' },
  { key: 'organic_carbon_pct', label: 'Organic carbon', type: 'number', step: '0.01', unit: '%' },
  { key: 'available_nitrogen_kg_ha', label: 'Available N', type: 'number', unit: 'kg/ha' },
  { key: 'available_phosphorus_kg_ha', label: 'Available P (Olsen)', type: 'number', unit: 'kg/ha' },
  { key: 'available_potassium_kg_ha', label: 'Available K', type: 'number', unit: 'kg/ha' },
  { key: 'sand_pct', label: 'Sand', type: 'number', unit: '%' },
  { key: 'silt_pct', label: 'Silt', type: 'number', unit: '%' },
  { key: 'clay_pct', label: 'Clay', type: 'number', unit: '%' },
  { key: 'ec_ds_m', label: 'Electrical conductivity', type: 'number', step: '0.01', unit: 'dS/m' },
  { key: 'moisture_pct', label: 'Soil moisture', type: 'number', unit: '%' },
]

interface ManualSoilFormProps {
  onSubmit: (entry: ManualSoilEntry) => void
  submitting: boolean
}

export function ManualSoilForm({ onSubmit, submitting }: ManualSoilFormProps) {
  const [values, setValues] = useState<Record<string, string>>({})
  const [irrigation, setIrrigation] = useState('unknown')

  const sand = parseFloat(values.sand_pct ?? '')
  const silt = parseFloat(values.silt_pct ?? '')
  const clay = parseFloat(values.clay_pct ?? '')
  const textureEntered = !isNaN(sand) && !isNaN(silt) && !isNaN(clay)
  const textureSum = textureEntered ? sand + silt + clay : null
  const textureSumBad = textureSum !== null && Math.abs(textureSum - 100) > 5

  function handleChange(key: string, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const entry: ManualSoilEntry = { irrigation_availability: irrigation }
    for (const field of FIELDS) {
      const raw = values[field.key]
      if (raw === undefined || raw === '') continue
      if (field.type === 'number') {
        const n = parseFloat(raw)
        if (!isNaN(n)) (entry as Record<string, unknown>)[field.key] = n
      } else {
        ;(entry as Record<string, unknown>)[field.key] = raw
      }
    }
    onSubmit(entry)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
      <div className="grid grid-cols-2 gap-3">
        {FIELDS.map((field) => (
          <label key={field.key} className="col-span-2 text-xs text-soil-700 sm:col-span-1">
            {field.label} {field.unit && <span className="text-soil-500">({field.unit})</span>}
            <input
              type={field.type}
              step={field.step}
              value={values[field.key] ?? ''}
              onChange={(e) => handleChange(field.key, e.target.value)}
              className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1.5 text-sm"
            />
          </label>
        ))}
        <label className="col-span-2 text-xs text-soil-700">
          Irrigation availability
          <select
            value={irrigation}
            onChange={(e) => setIrrigation(e.target.value)}
            className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1.5 text-sm"
          >
            <option value="unknown">Unknown</option>
            <option value="available">Available</option>
            <option value="none">Not available (rainfed)</option>
          </select>
        </label>
        <label className="col-span-2 text-xs text-soil-700">
          Crop history
          <input
            type="text"
            value={values.crop_history ?? ''}
            onChange={(e) => handleChange('crop_history', e.target.value)}
            className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1.5 text-sm"
          />
        </label>
      </div>

      {textureSumBad && (
        <p className="text-xs text-red-600">
          Sand + silt + clay = {textureSum?.toFixed(1)}%, not close to 100%. You can still submit,
          but texture classification will be skipped.
        </p>
      )}

      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-md bg-leaf-600 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {submitting ? 'Submitting…' : 'Submit soil sample'}
      </button>
    </form>
  )
}
