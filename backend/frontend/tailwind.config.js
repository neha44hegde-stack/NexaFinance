/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          green: '#1a472a',
          greenLight: '#2d5a3d',
          cream: '#f5f0e8',
          card: '#ffffff',
          accent: '#e8a87c',
        }
      },
      fontFamily: {
        serif: ['Playfair Display', 'serif'],
      }
    },
  },
  plugins: [],
}