import { useState } from 'react'
import { ApiError, recommendFertilizer } from '../services/api'
import type { CropRecommendation } from '../types/crops'
import type { FertilizerResponse } from '../types/fertilizer'
import type { SoilSample } from '../types/soil'
import { measurementValue } from '../types/soil'

interface FertilizerCalculatorProps {
  sample: SoilSample
  recommendations: CropRecommendation[]
}

export function FertilizerCalculator({ sample, recommendations }: FertilizerCalculatorProps) {
  const [cropKey, setCropKey] = useState(recommendations[0]?.key ?? '')
  const [area, setArea] = useState(String(sample.farm_area_ha ?? 1))
  const [ureaPrice, setUreaPrice] = useState('')
  const [dapPrice, setDapPrice] = useState('')
  const [mopPrice, setMopPrice] = useState('')
  const [result, setResult] = useState<FertilizerResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleCalculate(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const response = await recommendFertilizer({
        crop_key: cropKey,
        area_ha: parseFloat(area) || 1,
        available_nitrogen_kg_ha: measurementValue(sample, 'available_nitrogen_kg_ha'),
        available_phosphorus_kg_ha: measurementValue(sample, 'available_phosphorus_kg_ha'),
        available_potassium_kg_ha: measurementValue(sample, 'available_potassium_kg_ha'),
        urea_price_per_kg: ureaPrice ? parseFloat(ureaPrice) : null,
        dap_price_per_kg: dapPrice ? parseFloat(dapPrice) : null,
        mop_price_per_kg: mopPrice ? parseFloat(mopPrice) : null,
      })
      setResult(response)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not calculate fertilizer dose.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
      <h2 className="text-sm font-semibold text-soil-700">Fertilizer calculator</h2>
      <form onSubmit={handleCalculate} className="mt-2 space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <label className="text-xs text-soil-700">
            Crop
            <select
              value={cropKey}
              onChange={(e) => setCropKey(e.target.value)}
              className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1.5 text-sm"
            >
              {recommendations.map((c) => (
                <option key={c.key} value={c.key}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          <label className="text-xs text-soil-700">
            Area (ha)
            <input
              type="number"
              step="0.1"
              value={area}
              onChange={(e) => setArea(e.target.value)}
              className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1.5 text-sm"
            />
          </label>
        </div>

        <details className="text-xs text-soil-500">
          <summary className="cursor-pointer text-soil-700">
            Fertilizer prices (optional, for cost estimate)
          </summary>
          <div className="mt-2 grid grid-cols-3 gap-2">
            <label>
              Urea (₹/kg)
              <input
                type="number"
                value={ureaPrice}
                onChange={(e) => setUreaPrice(e.target.value)}
                className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1 text-sm"
              />
            </label>
            <label>
              DAP (₹/kg)
              <input
                type="number"
                value={dapPrice}
                onChange={(e) => setDapPrice(e.target.value)}
                className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1 text-sm"
              />
            </label>
            <label>
              MOP (₹/kg)
              <input
                type="number"
                value={mopPrice}
                onChange={(e) => setMopPrice(e.target.value)}
                className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1 text-sm"
              />
            </label>
          </div>
        </details>

        <button
          type="submit"
          disabled={loading || !cropKey}
          className="w-full rounded-md bg-leaf-600 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? 'Calculating…' : 'Calculate fertilizer dose'}
        </button>
      </form>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      {result && !result.sufficient_data && (
        <p className="mt-3 rounded-md border-l-4 border-l-[#d03b3b] bg-soil-50 p-3 text-sm text-soil-700">
          {result.message}
        </p>
      )}

      {result && result.sufficient_data && (
        <div className="mt-3 space-y-2">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="rounded-md bg-soil-50 p-2">
              <p className="text-lg font-bold text-soil-900">{result.urea_kg}</p>
              <p className="text-xs text-soil-500">kg Urea</p>
            </div>
            <div className="rounded-md bg-soil-50 p-2">
              <p className="text-lg font-bold text-soil-900">{result.dap_kg}</p>
              <p className="text-xs text-soil-500">kg DAP</p>
            </div>
            <div className="rounded-md bg-soil-50 p-2">
              <p className="text-lg font-bold text-soil-900">{result.mop_kg}</p>
              <p className="text-xs text-soil-500">kg MOP</p>
            </div>
          </div>
          {result.fertility_classes && (
            <p className="text-xs text-soil-500">
              Fertility status — N: {result.fertility_classes.nitrogen}, P:{' '}
              {result.fertility_classes.phosphorus}, K: {result.fertility_classes.potassium}
            </p>
          )}
          {result.estimated_cost !== null && (
            <p className="text-sm font-medium text-soil-700">
              Estimated cost: ₹{result.estimated_cost.toFixed(0)}
            </p>
          )}
          <div className="rounded-md bg-soil-50 p-2 text-xs text-soil-500">
            {result.assumptions.map((a, i) => (
              <p key={i}>• {a}</p>
            ))}
          </div>
          <p className="text-xs text-soil-500">{result.disclaimer}</p>
        </div>
      )}
    </div>
  )
}
