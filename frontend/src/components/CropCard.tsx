import type { CropRecommendation } from '../types/crops'

const CONFIDENCE_STYLE: Record<string, string> = {
  high: 'bg-leaf-600',
  medium: 'bg-[#c98500]',
  low: 'bg-soil-500',
}

export function CropCard({ crop, rank }: { crop: CropRecommendation; rank: number }) {
  return (
    <div className="rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-soil-500">#{rank}</p>
          <h3 className="text-lg font-bold text-soil-900">{crop.name}</h3>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-leaf-700">{crop.score.toFixed(0)}</p>
          <span
            className={`rounded-full px-2 py-0.5 text-[10px] font-medium uppercase text-white ${CONFIDENCE_STYLE[crop.confidence]}`}
          >
            {crop.confidence} confidence
          </span>
        </div>
      </div>

      <dl className="mt-2 grid grid-cols-3 gap-2 text-xs text-soil-500">
        <div>
          <dt>Season</dt>
          <dd className="font-medium text-soil-700">{crop.season.replace(/_/g, ' ')}</dd>
        </div>
        <div>
          <dt>Duration</dt>
          <dd className="font-medium text-soil-700">
            {crop.duration_days_min}-{crop.duration_days_max}d
          </dd>
        </div>
        <div>
          <dt>Water need</dt>
          <dd className="font-medium text-soil-700">{crop.water_need}</dd>
        </div>
      </dl>

      {crop.reasons.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-semibold text-soil-700">Why this crop</p>
          <ul className="mt-1 list-inside list-disc text-xs text-soil-500">
            {crop.reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      {crop.limiting_factors.length > 0 && (
        <div className="mt-2">
          <p className="text-xs font-semibold text-soil-700">Limiting factors</p>
          <ul className="mt-1 list-inside list-disc text-xs text-red-600">
            {crop.limiting_factors.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      {crop.data_limitations.length > 0 && (
        <div className="mt-2 rounded-md bg-soil-50 p-2 text-xs text-soil-500">
          {crop.data_limitations.map((r, i) => (
            <p key={i}>⚠ {r}</p>
          ))}
        </div>
      )}
    </div>
  )
}
