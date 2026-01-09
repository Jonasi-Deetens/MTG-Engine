import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // MTG mana colors
        mana: {
          white: "#f9faf4",
          blue: "#0e68ab",
          black: "#150b00",
          red: "#d3202a",
          green: "#00733e",
          colorless: "#cac5c0",
        },
        // Fantasy theme colors
        fantasy: {
          dark: "#1a1a2e",
          darker: "#16213e",
          gold: "#d4af37",
          amber: "#f4a460",
        },
        // Angel theme colors (Elesh Norn white-yellow)
        angel: {
          white: "#fefcf8",
          cream: "#f5f0e8",
          gold: "#d4af37",
          yellow: "#f4d03f",
          amber: "#f4a460",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        heading: ["var(--font-cinzel)", "serif"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};

export default config;

