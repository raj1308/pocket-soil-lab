import { useState } from 'react'
import { searchLocation, ApiError } from '../services/api'
import { getCurrentPosition } from '../hooks/useGeolocation'
import type { Location } from '../types/weather'

interface LocationPickerProps {
  onSelect: (location: Location) => void
}

export function LocationPicker({ onSelect }: LocationPickerProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Location[]>([])
  const [status, setStatus] = useState<'idle' | 'loading' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (query.trim().length < 2) return
    setStatus('loading')
    setError(null)
    try {
      const found = await searchLocation(query.trim())
      setResults(found)
      setStatus('idle')
      if (found.length === 0) setError('No matching locations found.')
    } catch (err) {
      setStatus('error')
      setError(err instanceof ApiError ? err.message : 'Search failed.')
    }
  }

  async function handleUseGps() {
    setStatus('loading')
    setError(null)
    try {
      const pos = await getCurrentPosition()
      onSelect({ name: 'Current location', latitude: pos.latitude, longitude: pos.longitude })
      setStatus('idle')
    } catch (err) {
      setStatus('error')
      setError(err instanceof Error ? err.message : 'Could not get location.')
    }
  }

  return (
    <div className="space-y-2 rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={handleUseGps}
          className="rounded-md bg-leaf-600 px-3 py-2 text-sm font-medium text-white active:bg-leaf-700"
        >
          📍 Use my location
        </button>
        <form onSubmit={handleSearch} className="flex flex-1 gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search city or village"
            className="min-w-0 flex-1 rounded-md border border-soil-100 px-3 py-2 text-sm"
          />
          <button
            type="submit"
            className="rounded-md border border-soil-100 px-3 py-2 text-sm font-medium text-soil-700"
          >
            Search
          </button>
        </form>
      </div>

      {status === 'loading' && <p className="text-sm text-soil-500">Working…</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {results.length > 0 && (
        <ul className="divide-y divide-soil-100">
          {results.map((r, i) => (
            <li key={i}>
              <button
                type="button"
                onClick={() => {
                  onSelect(r)
                  setResults([])
                  setQuery('')
                }}
                className="w-full py-2 text-left text-sm text-soil-700 hover:text-leaf-600"
              >
                {r.name}
                {r.admin1 ? `, ${r.admin1}` : ''} {r.country ? `· ${r.country}` : ''}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
