export interface ColorStats {
  meanR: number
  meanG: number
  meanB: number
  meanH: number
  meanS: number
  meanV: number
  brightness: number
  histogram: { bin: number; r: number; g: number; b: number }[]
}

function rgbToHsv(r: number, g: number, b: number): [number, number, number] {
  const rn = r / 255
  const gn = g / 255
  const bn = b / 255
  const max = Math.max(rn, gn, bn)
  const min = Math.min(rn, gn, bn)
  const delta = max - min
  let h = 0
  if (delta !== 0) {
    if (max === rn) h = 60 * (((gn - bn) / delta) % 6)
    else if (max === gn) h = 60 * ((bn - rn) / delta + 2)
    else h = 60 * ((rn - gn) / delta + 4)
  }
  if (h < 0) h += 360
  const s = max === 0 ? 0 : delta / max
  const v = max
  return [h, s * 100, v * 100]
}

const BIN_COUNT = 16

/** Analyzes pixel data from a canvas — mean RGB/HSV, brightness, and a
 * per-channel histogram. Deliberately returns ONLY visual/colour statistics —
 * never a soil chemistry value. See master spec Part 5 Mode 3. */
export function analyzeImageData(imageData: ImageData): ColorStats {
  const { data } = imageData
  const pixelCount = data.length / 4
  let sumR = 0
  let sumG = 0
  let sumB = 0
  let sumH = 0
  let sumS = 0
  let sumV = 0
  const histR = new Array(BIN_COUNT).fill(0)
  const histG = new Array(BIN_COUNT).fill(0)
  const histB = new Array(BIN_COUNT).fill(0)
  const binSize = 256 / BIN_COUNT

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i]
    const g = data[i + 1]
    const b = data[i + 2]
    sumR += r
    sumG += g
    sumB += b
    const [h, s, v] = rgbToHsv(r, g, b)
    sumH += h
    sumS += s
    sumV += v
    histR[Math.min(BIN_COUNT - 1, Math.floor(r / binSize))]++
    histG[Math.min(BIN_COUNT - 1, Math.floor(g / binSize))]++
    histB[Math.min(BIN_COUNT - 1, Math.floor(b / binSize))]++
  }

  const histogram = Array.from({ length: BIN_COUNT }, (_, i) => ({
    bin: Math.round(i * binSize),
    r: Math.round((histR[i] / pixelCount) * 1000) / 10,
    g: Math.round((histG[i] / pixelCount) * 1000) / 10,
    b: Math.round((histB[i] / pixelCount) * 1000) / 10,
  }))

  const meanR = sumR / pixelCount
  const meanG = sumG / pixelCount
  const meanB = sumB / pixelCount

  return {
    meanR: Math.round(meanR),
    meanG: Math.round(meanG),
    meanB: Math.round(meanB),
    meanH: Math.round(sumH / pixelCount),
    meanS: Math.round(sumS / pixelCount),
    meanV: Math.round(sumV / pixelCount),
    brightness: Math.round(((meanR + meanG + meanB) / 3 / 255) * 100),
    histogram,
  }
}

export function loadImageToCanvas(
  file: File,
): Promise<{ canvas: HTMLCanvasElement; imageData: ImageData }> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const url = URL.createObjectURL(file)
    img.onload = () => {
      const canvas = document.createElement('canvas')
      // Downscale for analysis speed — colour statistics don't need full resolution.
      const maxDim = 400
      const scale = Math.min(1, maxDim / Math.max(img.width, img.height))
      canvas.width = Math.round(img.width * scale)
      canvas.height = Math.round(img.height * scale)
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('Canvas not supported'))
        return
      }
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      URL.revokeObjectURL(url)
      resolve({ canvas, imageData })
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('Could not load image'))
    }
    img.src = url
  })
}
