import { useEffect, useState } from 'react'
import {
  ApiError,
  listDemoProfiles,
  listSoilSamples,
  loadDemoProfile,
  submitManualEntry,
} from '../services/api'
import { ManualSoilForm } from '../components/ManualSoilForm'
import { SoilSampleResult } from '../components/SoilSampleResult'
import { CameraObservation } from '../components/CameraObservation'
import { SpectralUpload } from '../components/SpectralUpload'
import { saveLastSample } from '../utils/storage'
import type { DemoProfileSummary, ManualSoilEntry, SoilSample } from '../types/soil'

type Tab = 'demo' | 'manual' | 'camera' | 'spectral'

export function Soil() {
  const [tab, setTab] = useState<Tab>('demo')
  const [demoProfiles, setDemoProfiles] = useState<DemoProfileSummary[]>([])
  const [recentSamples, setRecentSamples] = useState<SoilSample[]>([])
  const [result, setResult] = useState<SoilSample | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listDemoProfiles().then(setDemoProfiles).catch(() => {})
    listSoilSamples().then(setRecentSamples).catch(() => {})
  }, [])

  async function handleLoadDemo(key: string) {
    setSubmitting(true)
    setError(null)
    try {
      const sample = await loadDemoProfile(key)
      setResult(sample)
      saveLastSample(sample)
      setRecentSamples((prev) => [sample, ...prev])
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load demo profile.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleManualSubmit(entry: ManualSoilEntry) {
    setSubmitting(true)
    setError(null)
    try {
      const sample = await submitManualEntry(entry)
      setResult(sample)
      saveLastSample(sample)
      setRecentSamples((prev) => [sample, ...prev])
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not submit soil sample.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-4 p-4">
      <header>
        <h1 className="text-xl font-bold text-leaf-700">Soil Analysis</h1>
        <p className="text-sm text-soil-500">Enter a lab result, or try a demo sample</p>
      </header>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <button
          onClick={() => setTab('demo')}
          className={`rounded-md py-2 text-sm font-medium ${
            tab === 'demo' ? 'bg-leaf-600 text-white' : 'border border-soil-100 text-soil-700'
          }`}
        >
          Demo
        </button>
        <button
          onClick={() => setTab('manual')}
          className={`rounded-md py-2 text-sm font-medium ${
            tab === 'manual' ? 'bg-leaf-600 text-white' : 'border border-soil-100 text-soil-700'
          }`}
        >
          Manual
        </button>
        <button
          onClick={() => setTab('camera')}
          className={`rounded-md py-2 text-sm font-medium ${
            tab === 'camera' ? 'bg-leaf-600 text-white' : 'border border-soil-100 text-soil-700'
          }`}
        >
          Camera
        </button>
        <button
          onClick={() => setTab('spectral')}
          className={`rounded-md py-2 text-sm font-medium ${
            tab === 'spectral' ? 'bg-leaf-600 text-white' : 'border border-soil-100 text-soil-700'
          }`}
        >
          Spectral
        </button>
      </div>

      {tab === 'demo' && (
        <div className="space-y-2">
          <p className="rounded-md border-l-4 border-l-leaf-600 bg-white p-2 text-xs text-soil-700">
            Sample dataset — not a real-time soil measurement. Illustrative values for teaching
            and demo purposes.
          </p>
          {demoProfiles.map((p) => (
            <div
              key={p.key}
              className="flex items-center justify-between rounded-lg border border-soil-100 bg-white p-3 shadow-sm"
            >
              <div>
                <p className="text-sm font-semibold text-soil-700">{p.label}</p>
                <p className="text-xs text-soil-500">{p.description}</p>
              </div>
              <button
                onClick={() => handleLoadDemo(p.key)}
                disabled={submitting}
                className="shrink-0 rounded-md bg-leaf-600 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-50"
              >
                Load
              </button>
            </div>
          ))}
        </div>
      )}

      {tab === 'manual' && (
        <ManualSoilForm onSubmit={handleManualSubmit} submitting={submitting} />
      )}

      {tab === 'camera' && <CameraObservation />}

      {tab === 'spectral' && <SpectralUpload />}

      {error && <p className="text-sm text-red-600">{error}</p>}

      {result && (
        <div>
          <h2 className="mb-2 text-sm font-semibold text-soil-700">Result</h2>
          <SoilSampleResult sample={result} />
        </div>
      )}

      {recentSamples.length > 0 && (
        <section>
          <h2 className="mb-2 text-sm font-semibold text-soil-700">Recent samples</h2>
          <ul className="divide-y divide-soil-100 rounded-lg border border-soil-100 bg-white">
            {recentSamples.slice(0, 8).map((s) => (
              <li key={s.id} className="p-3">
                <button
                  onClick={() => {
                    setResult(s)
                    saveLastSample(s)
                  }}
                  className="w-full text-left text-sm text-soil-700 hover:text-leaf-600"
                >
                  {s.farm_name ?? `Sample #${s.id}`}
                  {s.texture_class && ` · ${s.texture_class}`}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
