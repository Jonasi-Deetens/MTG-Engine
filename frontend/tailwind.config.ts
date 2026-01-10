import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  safelist: [
    // Ensure theme border color classes are always generated
    'border-theme-card-border',
    'border-theme-input-border',
    'border-theme-border-default',
    'border-theme-border-hover',
    'border-theme-border-focus',
    'hover:border-theme-border-hover',
    'hover:border-theme-card-border',
  ],
  theme: {
    extend: {
      colors: {
        // Theme colors (use CSS variables for dynamic theming)
        theme: {
          bg: {
            primary: 'var(--theme-bg-primary)',
            secondary: 'var(--theme-bg-secondary)',
            tertiary: 'var(--theme-bg-tertiary)',
          },
          text: {
            primary: 'var(--theme-text-primary)',
            secondary: 'var(--theme-text-secondary)',
            muted: 'var(--theme-text-muted)',
          },
          border: {
            default: 'var(--theme-border-default)',
            hover: 'var(--theme-border-hover)',
            focus: 'var(--theme-border-focus)',
          },
          accent: {
            primary: 'var(--theme-accent-primary)',
            secondary: 'var(--theme-accent-secondary)',
            hover: 'var(--theme-accent-hover)',
          },
          status: {
            success: 'var(--theme-status-success)',
            warning: 'var(--theme-status-warning)',
            error: 'var(--theme-status-error)',
            info: 'var(--theme-status-info)',
          },
          card: {
            bg: 'var(--theme-card-bg)',
            border: 'var(--theme-card-border)',
            hover: 'var(--theme-card-hover)',
          },
          input: {
            bg: 'var(--theme-input-bg)',
            border: 'var(--theme-input-border)',
            text: 'var(--theme-input-text)',
            placeholder: 'var(--theme-input-placeholder)',
          },
          button: {
            'primary-bg': 'var(--theme-button-primary-bg)',
            'primary-text': 'var(--theme-button-primary-text)',
            'primary-hover': 'var(--theme-button-primary-hover)',
            'secondary-bg': 'var(--theme-button-secondary-bg)',
            'secondary-text': 'var(--theme-button-secondary-text)',
            'secondary-hover': 'var(--theme-button-secondary-hover)',
            'outline-border': 'var(--theme-button-outline-border)',
            'outline-text': 'var(--theme-button-outline-text)',
            'outline-hover': 'var(--theme-button-outline-hover)',
            'ghost-text': 'var(--theme-button-ghost-text)',
            'ghost-hover': 'var(--theme-button-ghost-hover)',
          },
        },
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
        // Angel theme colors (Elesh Norn white-yellow) - kept for specific use cases
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
      borderColor: {
        'theme': {
          'card-border': 'var(--theme-card-border)',
          'input-border': 'var(--theme-input-border)',
          'border-default': 'var(--theme-border-default)',
          'border-hover': 'var(--theme-border-hover)',
          'border-focus': 'var(--theme-border-focus)',
        },
      },
    },
  },
  plugins: [],
};

export default config;

