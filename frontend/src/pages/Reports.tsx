import { useEffect, useState } from 'react'
import { listSoilSamples } from '../services/api'
import { SoilSampleResult } from '../components/SoilSampleResult'
import { sourceLabel, type SoilSample } from '../types/soil'

export function Reports() {
  const [samples, setSamples] = useState<SoilSample[]>([])
  const [selected, setSelected] = useState<number[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listSoilSamples()
      .then(setSamples)
      .finally(() => setLoading(false))
  }, [])

  function toggleSelect(id: number) {
    setSelected((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id)
      if (prev.length >= 2) return [prev[1], id]
      return [...prev, id]
    })
  }

  const selectedSamples = samples.filter((s) => selected.includes(s.id))

  return (
    <div className="space-y-4 p-4">
      <style>{`
        @media print {
          nav { display: none !important; }
          .no-print { display: none !important; }
        }
      `}</style>

      <header className="no-print">
        <h1 className="text-xl font-bold text-leaf-700">Reports</h1>
        <p className="text-sm text-soil-500">
          Saved soil samples. Select up to two to compare, or print/save one as a PDF.
        </p>
      </header>

      {loading && <p className="no-print text-sm text-soil-500">Loading…</p>}

      {!loading && samples.length === 0 && (
        <p className="no-print rounded-md border border-soil-100 bg-white p-4 text-sm text-soil-500">
          No saved samples yet. Go to Soil Analysis to load a demo sample or submit a manual entry.
        </p>
      )}

      {!loading && samples.length > 0 && (
        <ul className="no-print divide-y divide-soil-100 rounded-lg border border-soil-100 bg-white">
          {samples.map((s) => (
            <li key={s.id} className="flex items-center gap-3 p-3">
              <input
                type="checkbox"
                checked={selected.includes(s.id)}
                onChange={() => toggleSelect(s.id)}
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-soil-700">
                  {s.farm_name ?? `Sample #${s.id}`}
                </p>
                <p className="text-xs text-soil-500">
                  {sourceLabel(s.source_type)}
                  {s.texture_class && ` · ${s.texture_class}`}
                  {s.sampling_date && ` · ${s.sampling_date}`}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}

      {selectedSamples.length > 0 && (
        <div>
          <div className="no-print mb-2 flex justify-end">
            <button
              onClick={() => window.print()}
              className="rounded-md bg-leaf-600 px-3 py-1.5 text-xs font-medium text-white"
            >
              🖨 Print / Save as PDF
            </button>
          </div>
          <div className={selectedSamples.length === 2 ? 'grid gap-4 sm:grid-cols-2' : ''}>
            {selectedSamples.map((s) => (
              <SoilSampleResult key={s.id} sample={s} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
