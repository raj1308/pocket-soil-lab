/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        soil: {
          50: '#f8f5f0',
          100: '#eee5d8',
          500: '#8a5a2e',
          700: '#5c3a1e',
          900: '#2e1d10',
        },
        leaf: {
          50: '#f1f8f0',
          500: '#4a7c3a',
          600: '#3b6430',
          700: '#2d4d24',
        },
      },
    },
  },
  plugins: [],
}
