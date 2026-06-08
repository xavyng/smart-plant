import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-dm-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        bg: "#080D16",
        surface: "#0C1220",
        card: "#0F1929",
        "card-hover": "#131F33",
        border: "#1A2A42",
        "border-light": "#223352",
        accent: "#3B82F6",
        "accent-dim": "#2563EB",
        teal: "#06B6D4",
        success: "#10B981",
        warning: "#F59E0B",
        danger: "#EF4444",
        violet: "#8B5CF6",
      },
    },
  },
  plugins: [],
};
export default config;
