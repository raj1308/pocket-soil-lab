import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { HourlyForecastPoint } from '../types/weather'

function formatHour(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleTimeString(undefined, { hour: 'numeric' })
}

export function TemperatureChart({ hourly }: { hourly: HourlyForecastPoint[] }) {
  const data = hourly.slice(0, 24).map((h) => ({ time: h.time, temp: h.temperature_c }))

  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold text-soil-700">Temperature — next 24h</h3>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="tempFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2a78d6" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#2a78d6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke="#e1e0d9" />
          <XAxis
            dataKey="time"
            tickFormatter={formatHour}
            tick={{ fontSize: 11, fill: '#898781' }}
            interval={3}
            axisLine={{ stroke: '#c3c2b7' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#898781' }}
            width={40}
            axisLine={false}
            tickLine={false}
            unit="°"
            domain={['dataMin - 2', 'dataMax + 2']}
          />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(1)}°C`, 'Temperature']}
            labelFormatter={formatHour}
            contentStyle={{ fontSize: 12, borderRadius: 6 }}
          />
          <Area
            type="monotone"
            dataKey="temp"
            stroke="#2a78d6"
            strokeWidth={2}
            fill="url(#tempFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
