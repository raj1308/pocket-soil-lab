import { useEffect, useState } from 'react'
import { getHealth, ApiError } from '../services/api'

type BackendStatus = 'checking' | 'online' | 'offline'

export function Home() {
  const [status, setStatus] = useState<BackendStatus>('checking')
  const [version, setVersion] = useState<string | null>(null)

  useEffect(() => {
    getHealth()
      .then((health) => {
        setStatus('online')
        setVersion(health.version)
      })
      .catch((err) => {
        setStatus('offline')
        if (err instanceof ApiError) console.error(err.message)
      })
  }, [])

  return (
    <div className="space-y-4 p-4">
      <header>
        <h1 className="text-2xl font-bold text-leaf-700">Pocket Soil Lab AI</h1>
        <p className="text-sm text-soil-500">Soil health, weather & crop decision support</p>
      </header>

      <div className="rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
        <h2 className="text-sm font-semibold text-soil-700">Backend connection</h2>
        {status === 'checking' && <p className="text-sm text-soil-500">Checking…</p>}
        {status === 'online' && (
          <p className="text-sm text-leaf-600">Connected — API version {version}</p>
        )}
        {status === 'offline' && (
          <p className="text-sm text-red-600">
            Backend unreachable. Start it with <code>uvicorn app.main:app --reload</code> in{' '}
            <code>backend/</code>.
          </p>
        )}
      </div>

      <section className="rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
        <h2 className="text-sm font-semibold text-soil-700">Coming in later phases</h2>
        <ul className="mt-2 list-inside list-disc text-sm text-soil-500">
          <li>Location + live weather (Phase 2)</li>
          <li>Soil sample entry &amp; recent report summary (Phase 3)</li>
          <li>Crop recommendation cards (Phase 4)</li>
        </ul>
      </section>
    </div>
  )
}
