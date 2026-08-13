/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        saffron: {
          50: '#fff9ed',
          100: '#ffefd4',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
        },
        emerald: {
          500: '#10b981',
          600: '#059669',
          700: '#047857',
        },
        govnavy: {
          800: '#0f172a',
          900: '#090d16',
          950: '#030712'
        }
      }
    },
  },
  plugins: [],
}
