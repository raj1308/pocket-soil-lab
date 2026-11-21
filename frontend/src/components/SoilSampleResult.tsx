import { Link } from 'react-router-dom'
import { sourceLabel, type SoilSample } from '../types/soil'

const PROPERTY_LABELS: Record<string, string> = {
  ph: 'pH',
  organic_carbon_pct: 'Organic carbon',
  available_nitrogen_kg_ha: 'Available N',
  available_phosphorus_kg_ha: 'Available P',
  available_potassium_kg_ha: 'Available K',
  sand_pct: 'Sand',
  silt_pct: 'Silt',
  clay_pct: 'Clay',
  ec_ds_m: 'Electrical conductivity',
  moisture_pct: 'Moisture',
}

export function SoilSampleResult({ sample }: { sample: SoilSample }) {
  return (
    <div className="space-y-3 rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-soil-700">{sample.farm_name ?? `Sample #${sample.id}`}</h3>
          <p className="text-xs text-soil-500">
            {sourceLabel(sample.source_type)}
            {sample.texture_class && ` · Texture: ${sample.texture_class}`}
          </p>
        </div>
        <Link
          to="/crops"
          className="rounded-md bg-leaf-600 px-3 py-1.5 text-xs font-medium text-white"
        >
          Get crop recommendations →
        </Link>
      </div>

      {sample.warnings.length > 0 && (
        <div className="rounded-md border-l-4 border-l-[#c98500] bg-soil-50 p-2 text-xs text-soil-700">
          {sample.warnings.map((w, i) => (
            <p key={i}>{w}</p>
          ))}
        </div>
      )}

      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs uppercase text-soil-500">
            <th className="pb-1">Property</th>
            <th className="pb-1">Value</th>
            <th className="pb-1">Method</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-soil-100">
          {sample.measurements.map((m) => (
            <tr key={m.property}>
              <td className="py-1 text-soil-700">{PROPERTY_LABELS[m.property] ?? m.property}</td>
              <td className="py-1 text-soil-900">
                {m.value} {m.unit}
              </td>
              <td className="py-1 text-xs text-soil-500">{m.method ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
