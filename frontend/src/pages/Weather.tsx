import { useEffect, useState } from 'react'
import { getForecast, ApiError } from '../services/api'
import { AdvisoryCard } from '../components/AdvisoryCard'
import { LocationPicker } from '../components/LocationPicker'
import { TemperatureChart } from '../components/TemperatureChart'
import { RainfallChart } from '../components/RainfallChart'
import { loadForecastCache, loadLocation, saveForecastCache, saveLocation } from '../utils/storage'
import type { ForecastResponse, Location } from '../types/weather'

function formatDay(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' })
}

export function Weather() {
  const [location, setLocation] = useState<Location | null>(() => loadLocation())
  const [forecast, setForecast] = useState<ForecastResponse | null>(() => loadForecastCache())
  const [status, setStatus] = useState<'idle' | 'loading' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)
  const [offline, setOffline] = useState(false)

  useEffect(() => {
    if (!location) return
    let cancelled = false
    setStatus('loading')
    setError(null)
    getForecast(location.latitude, location.longitude)
      .then((data) => {
        if (cancelled) return
        setForecast(data)
        saveForecastCache(data)
        setOffline(false)
        setStatus('idle')
      })
      .catch((err) => {
        if (cancelled) return
        setStatus('error')
        setOffline(true)
        setError(err instanceof ApiError ? err.message : 'Could not load forecast.')
      })
    return () => {
      cancelled = true
    }
  }, [location])

  function handleSelectLocation(loc: Location) {
    setLocation(loc)
    saveLocation(loc)
  }

  return (
    <div className="space-y-4 p-4">
      <header>
        <h1 className="text-xl font-bold text-leaf-700">Weather</h1>
        <p className="text-sm text-soil-500">Live forecast from Open-Meteo</p>
      </header>

      <LocationPicker onSelect={handleSelectLocation} />

      {!location && (
        <p className="rounded-md border border-soil-100 bg-white p-4 text-sm text-soil-500">
          Choose a location above to see the forecast.
        </p>
      )}

      {status === 'loading' && !forecast && (
        <p className="text-sm text-soil-500">Loading forecast…</p>
      )}

      {error && !forecast && <p className="text-sm text-red-600">{error}</p>}

      {offline && forecast && (
        <div className="rounded-md border-l-4 border-l-[#c98500] bg-white p-3 text-sm text-soil-700">
          Showing the last cached forecast — could not reach the backend just now.
        </div>
      )}

      {forecast && (
        <>
          <div className="rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
            <div className="flex items-baseline justify-between">
              <div>
                {forecast.current && (
                  <p className="text-3xl font-bold text-soil-900">
                    {forecast.current.temperature_c.toFixed(1)}°C
                  </p>
                )}
                <p className="text-sm text-soil-500">
                  {location?.name}
                  {location?.admin1 ? `, ${location.admin1}` : ''}
                </p>
              </div>
              {forecast.current && (
                <div className="text-right text-sm text-soil-500">
                  <p>Humidity {forecast.current.relative_humidity_pct ?? '—'}%</p>
                  <p>Wind {forecast.current.wind_speed_kmh ?? '—'} km/h</p>
                </div>
              )}
            </div>
            <p className="mt-2 text-xs text-soil-500">
              {forecast.is_cached ? 'Cached forecast' : 'Live forecast'} · retrieved{' '}
              {new Date(forecast.retrieved_at).toLocaleTimeString()} · source: {forecast.source}
            </p>
          </div>

          <section className="rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
            <TemperatureChart hourly={forecast.hourly} />
          </section>

          <section className="rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
            <RainfallChart daily={forecast.daily} />
          </section>

          <section className="rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
            <h2 className="mb-2 text-sm font-semibold text-soil-700">7-day forecast</h2>
            <ul className="divide-y divide-soil-100">
              {forecast.daily.map((d) => (
                <li key={d.date} className="flex items-center justify-between py-2 text-sm">
                  <span className="w-24 text-soil-700">{formatDay(d.date)}</span>
                  <span className="text-soil-500">
                    💧 {d.precipitation_probability_max_pct?.toFixed(0) ?? '—'}%
                  </span>
                  <span className="text-soil-900">
                    {d.temp_max_c.toFixed(0)}° / {d.temp_min_c.toFixed(0)}°
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="space-y-2">
            <h2 className="text-sm font-semibold text-soil-700">Farming advisories</h2>
            {forecast.advisories.map((a, i) => (
              <AdvisoryCard key={i} advisory={a} />
            ))}
          </section>

          <p className="text-xs text-soil-500">{forecast.disclaimer}</p>
        </>
      )}
    </div>
  )
}
