/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0D1117",
        panel: "#161B22",
        panel2: "#1C2128",
        border: "#30363D",
        cyan: "#2DD4BF",
        amber: "#F5A623",
        red: "#EF4444",
        textprimary: "#E6EDF3",
        textmuted: "#8B949E",
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(0%)" },
          "100%": { transform: "translateY(100%)" },
        },
      },
      animation: {
        scan: "scan 1.8s linear infinite",
      },
    },
  },
  plugins: [],
};
