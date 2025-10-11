/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'health-green': '#10B981',
        'health-yellow': '#F59E0B',
        'health-red': '#EF4444',
      }
    },
  },
  plugins: [],
}
