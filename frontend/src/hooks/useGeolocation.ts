export interface GeolocationResult {
  latitude: number
  longitude: number
}

export function getCurrentPosition(): Promise<GeolocationResult> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by this browser.'))
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
      (err) => {
        const messages: Record<number, string> = {
          1: 'Location permission denied. Use manual search instead.',
          2: 'Location unavailable. Use manual search instead.',
          3: 'Location request timed out. Use manual search instead.',
        }
        reject(new Error(messages[err.code] ?? 'Could not get your location.'))
      },
      { enableHighAccuracy: false, timeout: 10000 },
    )
  })
}
