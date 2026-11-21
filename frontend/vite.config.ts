import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: false, // we ship a hand-written public/manifest.json instead
      includeAssets: ['icon.svg', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png'],
      workbox: {
        // Only the app shell (JS/CSS/HTML/icons) is precached. API responses are
        // never cached by the service worker — the app already has its own
        // explicit, visibly-labeled offline cache (localStorage) for weather and
        // soil data, so a silent SW-level cache would risk serving stale data
        // without the "cached" label the UI relies on.
        globPatterns: ['**/*.{js,css,html,svg,png,ico}'],
        navigateFallback: '/offline.html',
        navigateFallbackDenylist: [/^\/api\//],
      },
    }),
  ],
  server: {
    port: 5173,
  },
})
