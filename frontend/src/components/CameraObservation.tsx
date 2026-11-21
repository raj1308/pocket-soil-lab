import { useRef, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { analyzeImageData, loadImageToCanvas, type ColorStats } from '../utils/imageAnalysis'

function hsvDescription(h: number, s: number, v: number): string {
  if (v < 25) return 'Very dark — check lighting, or soil may be genuinely dark (high organic matter, wet)'
  if (s < 15) return 'Low saturation (greyish) — could be dry, pale or overexposed'
  if (h < 30 || h >= 330) return 'Reddish hue — often associated with iron oxide-rich (well-drained, oxidized) soils'
  if (h < 60) return 'Orange/brown hue — common for many agricultural topsoils'
  if (h < 90) return 'Yellowish hue — may indicate goethite or certain parent materials'
  return 'Hue outside the typical reddish-brown soil range — verify lighting and sample'
}

export function CameraObservation() {
  const [preview, setPreview] = useState<string | null>(null)
  const [stats, setStats] = useState<ColorStats | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleFile(file: File) {
    setError(null)
    setAnalyzing(true)
    try {
      setPreview(URL.createObjectURL(file))
      const { imageData } = await loadImageToCanvas(file)
      setStats(analyzeImageData(imageData))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not analyze image.')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="space-y-3">
      <div className="rounded-md border-l-4 border-l-[#d03b3b] bg-white p-3 text-xs text-soil-700">
        <strong>Limitations:</strong> a phone photo cannot measure pH, nitrogen, phosphorus or
        potassium. This tool reports only visual colour characteristics (RGB/HSV, brightness,
        histogram) — never a chemistry value. Lighting, camera, and calibration all affect the
        result; treat this as a rough visual observation, not a lab measurement.
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) handleFile(file)
        }}
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        className="w-full rounded-md bg-leaf-600 py-2 text-sm font-medium text-white"
      >
        📷 Capture or upload a soil photo
      </button>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {analyzing && <p className="text-sm text-soil-500">Analyzing…</p>}

      {preview && (
        <img src={preview} alt="Soil sample preview" className="max-h-64 w-full rounded-md object-cover" />
      )}

      {stats && (
        <div className="space-y-3 rounded-lg border border-soil-100 bg-white p-4 shadow-sm">
          <div>
            <h3 className="text-sm font-semibold text-soil-700">Colour observation</h3>
            <p className="text-xs text-soil-500">Source: image-derived visual observation (not a lab or sensor measurement)</p>
          </div>

          <div className="flex items-center gap-3">
            <div
              className="h-12 w-12 shrink-0 rounded-md border border-soil-100"
              style={{ backgroundColor: `rgb(${stats.meanR}, ${stats.meanG}, ${stats.meanB})` }}
            />
            <div className="text-xs text-soil-700">
              <p>RGB: {stats.meanR}, {stats.meanG}, {stats.meanB}</p>
              <p>HSV: {stats.meanH}°, {stats.meanS}%, {stats.meanV}%</p>
              <p>Brightness: {stats.brightness}%</p>
            </div>
          </div>

          <p className="text-xs text-soil-700">{hsvDescription(stats.meanH, stats.meanS, stats.meanV)}</p>

          {stats.brightness < 20 && (
            <p className="rounded-md bg-soil-50 p-2 text-xs text-soil-500">
              ⚠ Image is quite dark overall — results may be unreliable. Try retaking in better light.
            </p>
          )}
          {stats.brightness > 90 && (
            <p className="rounded-md bg-soil-50 p-2 text-xs text-soil-500">
              ⚠ Image appears overexposed — results may be unreliable. Avoid direct glare/flash.
            </p>
          )}

          <div>
            <h4 className="mb-1 text-xs font-semibold text-soil-700">Colour histogram</h4>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={stats.histogram} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid vertical={false} stroke="#e1e0d9" />
                <XAxis dataKey="bin" tick={{ fontSize: 10, fill: '#898781' }} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: '#898781' }} width={30} tickLine={false} unit="%" />
                <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6 }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="r" fill="#e34948" name="Red" />
                <Bar dataKey="g" fill="#1baf7a" name="Green" />
                <Bar dataKey="b" fill="#2a78d6" name="Blue" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
