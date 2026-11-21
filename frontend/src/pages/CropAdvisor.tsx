import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError, recommendCrops } from '../services/api'
import { CropCard } from '../components/CropCard'
import { FertilizerCalculator } from '../components/FertilizerCalculator'
import { loadLastSample } from '../utils/storage'
import { measurementValue } from '../types/soil'
import type { CropRecommendationResponse } from '../types/crops'

export function CropAdvisor() {
  const sample = loadLastSample()
  const [irrigation, setIrrigation] = useState(
    sample?.irrigation_availability === 'available',
  )
  const [season, setSeason] = useState('')
  const [temp, setTemp] = useState('')
  const [rainfall, setRainfall] = useState('')
  const [result, setResult] = useState<CropRecommendationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const response = await recommendCrops({
        texture_class: sample?.texture_class ?? null,
        ph: sample ? measurementValue(sample, 'ph') : null,
        organic_carbon_pct: sample ? measurementValue(sample, 'organic_carbon_pct') : null,
        irrigation_available: irrigation,
        expected_season_temp_c: temp ? parseFloat(temp) : null,
        expected_season_rainfall_mm: rainfall ? parseFloat(rainfall) : null,
        season_filter: season || null,
      })
      setResult(response)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not get recommendations.')
    } finally {
      setLoading(false)
    }
  }

  if (!sample) {
    return (
      <div className="p-4">
        <h1 className="text-xl font-bold text-leaf-700">Crop Advisor</h1>
        <p className="mt-2 rounded-md border border-soil-100 bg-white p-4 text-sm text-soil-500">
          No soil sample loaded yet.{' '}
          <Link to="/soil" className="text-leaf-600 underline">
            Go to Soil Analysis
          </Link>{' '}
          and load a demo sample or enter one manually first.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-4">
      <header>
        <h1 className="text-xl font-bold text-leaf-700">Crop Advisor</h1>
        <p className="text-sm text-soil-500">
          Based on: {sample.farm_name ?? `Sample #${sample.id}`}
          {sample.texture_class && ` · ${sample.texture_class}`}
        </p>
      </header>

      <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
        <label className="flex items-center gap-2 text-sm text-soil-700">
          <input type="checkbox" checked={irrigation} onChange={(e) => setIrrigation(e.target.checked)} />
          Irrigation available
        </label>

        <label className="block text-xs text-soil-700">
          Season
          <select
            value={season}
            onChange={(e) => setSeason(e.target.value)}
            className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1.5 text-sm"
          >
            <option value="">Any</option>
            <option value="kharif">Kharif (monsoon)</option>
            <option value="rabi">Rabi (winter)</option>
            <option value="summer">Summer</option>
          </select>
        </label>

        <div className="rounded-md bg-soil-50 p-2 text-xs text-soil-500">
          Optional: your own estimate of this growing season's typical climate (not the 7-day
          weather forecast — a forecast is too short-term to represent a season).
        </div>
        <div className="grid grid-cols-2 gap-3">
          <label className="text-xs text-soil-700">
            Expected season temp (°C)
            <input
              type="number"
              value={temp}
              onChange={(e) => setTemp(e.target.value)}
              className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1.5 text-sm"
            />
          </label>
          <label className="text-xs text-soil-700">
            Expected season rainfall (mm)
            <input
              type="number"
              value={rainfall}
              onChange={(e) => setRainfall(e.target.value)}
              className="mt-1 w-full rounded-md border border-soil-100 px-2 py-1.5 text-sm"
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-leaf-600 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? 'Scoring…' : 'Get recommendations'}
        </button>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {result && (
        <div className="space-y-3">
          {result.recommendations.map((crop, i) => (
            <CropCard key={crop.key} crop={crop} rank={i + 1} />
          ))}
          <p className="text-xs text-soil-500">{result.disclaimer}</p>
          <FertilizerCalculator sample={sample} recommendations={result.recommendations} />
        </div>
      )}
    </div>
  )
}
