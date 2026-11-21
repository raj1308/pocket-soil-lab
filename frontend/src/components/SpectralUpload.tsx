import { useEffect, useRef, useState } from 'react'
import { ApiError, getSpectralModelInfo, predictFromSpectra } from '../services/api'
import type { SpectralModelInfo, SpectralPredictionResponse } from '../types/ml'

export function SpectralUpload() {
  const [modelInfo, setModelInfo] = useState<SpectralModelInfo | null>(null)
  const [result, setResult] = useState<SpectralPredictionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    getSpectralModelInfo()
      .then(setModelInfo)
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Model unavailable.'))
  }, [])

  async function handleFile(file: File) {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await predictFromSpectra(file)
      setResult(response)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not process spectral file.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-3">
      <div className="rounded-md border-l-4 border-l-leaf-600 bg-white p-3 text-xs text-soil-700">
        <strong>ML-predicted, not a lab measurement.</strong> This uses a VisNIR spectroscopy
        model trained on the OSSL public soil spectral library to estimate organic carbon only —
        it does not predict pH, nitrogen, phosphorus or potassium. Accuracy varies by how similar
        your sample is to the training data (see the model's evaluation report for the honest
        numbers, including a case where it failed on an unfamiliar region's soils).
      </div>

      {modelInfo && (
        <div className="rounded-lg border border-soil-100 bg-white p-3 text-xs text-soil-500">
          <p className="font-semibold text-soil-700">Required CSV format</p>
          <p className="mt-1">{modelInfo.csv_format}</p>
          <p className="mt-1">
            Model: {modelInfo.model_version} · {modelInfo.n_wavelength_points} wavelength points,{' '}
            {modelInfo.wavelength_range_nm[0]}-{modelInfo.wavelength_range_nm[1]}nm
          </p>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) handleFile(file)
        }}
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={loading || !modelInfo}
        className="w-full rounded-md bg-leaf-600 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {loading ? 'Processing…' : '📄 Upload spectral CSV'}
      </button>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {result && (
        <div className="space-y-2">
          {result.predictions.map((p) => (
            <div key={p.sample_id} className="rounded-lg border border-soil-100 bg-white p-3 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-soil-700">{p.sample_id}</p>
                <p className="text-lg font-bold text-leaf-700">
                  {p.organic_carbon_pct}
                  {p.unit} OC
                </p>
              </div>
              <p className="text-xs text-soil-500">{p.method}</p>
              <p className="text-xs text-soil-500">
                Test R²={p.test_r2}, RMSE={p.test_rmse}{p.unit}
              </p>
              <p className="mt-1 rounded-md bg-soil-50 p-2 text-xs text-soil-500">
                {p.reliability_note}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
