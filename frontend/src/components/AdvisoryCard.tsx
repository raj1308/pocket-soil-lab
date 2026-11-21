import type { Advisory } from '../types/weather'

const SEVERITY_STYLES: Record<Advisory['severity'], { border: string; icon: string; label: string }> = {
  info: { border: 'border-l-leaf-600', icon: 'ℹ️', label: 'Info' },
  caution: { border: 'border-l-[#c98500]', icon: '⚠️', label: 'Caution' },
  warning: { border: 'border-l-[#d03b3b]', icon: '⛔', label: 'Warning' },
}

export function AdvisoryCard({ advisory }: { advisory: Advisory }) {
  const style = SEVERITY_STYLES[advisory.severity]
  return (
    <div className={`rounded-md border-l-4 ${style.border} bg-white p-3 shadow-sm`}>
      <div className="flex items-center gap-2 text-sm font-semibold text-soil-700">
        <span aria-hidden="true">{style.icon}</span>
        <span>{advisory.title}</span>
        <span className="ml-auto text-xs font-normal uppercase text-soil-500">{style.label}</span>
      </div>
      <p className="mt-1 text-sm text-soil-500">{advisory.message}</p>
    </div>
  )
}
