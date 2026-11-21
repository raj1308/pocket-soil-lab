import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { DailyForecastDay } from '../types/weather'

function formatDay(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { weekday: 'short' })
}

export function RainfallChart({ daily }: { daily: DailyForecastDay[] }) {
  const data = daily.map((d) => ({
    date: d.date,
    probability: d.precipitation_probability_max_pct ?? 0,
  }))

  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold text-soil-700">Rainfall probability — 7 days</h3>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="#e1e0d9" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDay}
            tick={{ fontSize: 11, fill: '#898781' }}
            axisLine={{ stroke: '#c3c2b7' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#898781' }}
            width={40}
            axisLine={false}
            tickLine={false}
            domain={[0, 100]}
            unit="%"
          />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(0)}%`, 'Rain probability']}
            labelFormatter={formatDay}
            contentStyle={{ fontSize: 12, borderRadius: 6 }}
          />
          <Bar dataKey="probability" fill="#eb6834" radius={[4, 4, 0, 0]} maxBarSize={28} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
