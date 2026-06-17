/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,vue}"],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        'wafer-dark': '#0a1628',
        'wafer-cyan': '#00e5ff',
        'wafer-red': '#ff3d3d',
      },
      fontFamily: {
        mono: ['Rajdhani', 'monospace'],
        sans: ['Noto Sans SC', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
