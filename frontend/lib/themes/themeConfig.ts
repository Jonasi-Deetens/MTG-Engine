// Theme configuration system
// Defines semantic color structure for all themes

export type Theme = 'light' | 'dark' | 'sakura' | 'neon' | 'nier';

export interface ThemeColors {
  background: {
    primary: string;      // Main page background
    secondary: string;    // Card backgrounds, panels
    tertiary: string;     // Nested elements
  };
  foreground: {
    primary: string;      // Main text
    secondary: string;    // Secondary text
    muted: string;        // Placeholder, hints
  };
  border: {
    default: string;      // Default borders
    hover: string;       // Hover state borders
    focus: string;       // Focus state borders
  };
  accent: {
    primary: string;     // Primary accent (amber/yellow)
    secondary: string;   // Secondary accent
    hover: string;       // Accent hover state
  };
  status: {
    success: string;
    warning: string;
    error: string;
    info: string;
  };
  card: {
    background: string;
    border: string;
    hover: string;
  };
  input: {
    background: string;
    border: string;
    text: string;
    placeholder: string;
  };
  button: {
    primary: {
      bg: string;
      text: string;
      hover: string;
    };
    secondary: {
      bg: string;
      text: string;
      hover: string;
    };
    outline: {
      border: string;
      text: string;
      hover: string;
    };
    ghost: {
      text: string;
      hover: string;
    };
  };
}

export const themes: Record<Theme, ThemeColors> = {
  light: {
    background: {
      primary: '#fefcf8',   // angel.white
      secondary: '#f5f0e8', // angel.cream
      tertiary: '#e0d8cc',  // lighter cream
    },
    foreground: {
      primary: '#1a1a1a',  // dark slate
      secondary: '#4a4a4a', // medium slate
      muted: '#7a7a7a',     // light slate
    },
    border: {
      default: '#fbbf24',   // amber-400 - visible amber border
      hover: '#f59e0b',     // amber-500 - amber on hover
      focus: '#f59e0b',     // amber-500 - amber focus
    },
    accent: {
      primary: '#f59e0b',  // amber-500 - primary amber accent
      secondary: '#fbbf24', // amber-400 - secondary amber
      hover: '#d97706',     // amber-600 - darker amber on hover
    },
    status: {
      success: '#22c55e',  // green-500
      warning: '#eab308',   // amber-500
      error: '#ef4444',     // red-500
      info: '#3b82f6',      // blue-500
    },
    card: {
      background: '#ffffff',
      border: '#fbbf24',    // amber-400 - visible amber border
      hover: '#fef3c7',     // amber-100 - very light amber hover
    },
    input: {
      background: '#ffffff',
      border: '#fbbf24',    // amber-400 - visible amber border
      text: '#1a1a1a',     // dark slate
      placeholder: '#94a3b8', // slate-400
    },
    button: {
      primary: {
        bg: '#f59e0b',      // amber-500 - amber button
        text: '#ffffff',
        hover: '#d97706',   // amber-600 - darker amber hover
      },
      secondary: {
        bg: '#fef3c7',      // amber-100 - light amber background
        text: '#1a1a1a',    // dark slate
        hover: '#fde68a',   // amber-200 - amber hover
      },
      outline: {
        border: '#f59e0b',  // amber-500 - amber border
        text: '#f59e0b',    // amber-500 - amber text
        hover: '#d97706',   // amber-600 - darker amber hover
      },
      ghost: {
        text: '#4a4a4a',     // medium slate
        hover: '#fef3c7',   // amber-100 - light amber hover
      },
    },
  },
  sakura: {
    background: {
      primary: '#fffafc',   // softer white with subtle pink tint
      secondary: '#f9f2f6', // muted blush
      tertiary: '#f3e6ee',  // pale rose
    },
    foreground: {
      primary: '#1a1a1a',   // dark slate
      secondary: '#4a4a4a', // medium slate
      muted: '#7a7a7a',     // light slate
    },
    border: {
      default: '#f4a3c0',   // soft pink
      hover: '#f08ab0',     // stronger pink
      focus: '#f08ab0',     // stronger pink
    },
    accent: {
      primary: '#f08ab0',   // sakura pink
      secondary: '#f4a3c0', // soft pink
      hover: '#e56a98',     // deeper pink
    },
    status: {
      success: '#22c55e',  // green-500
      warning: '#eab308',  // amber-500
      error: '#ef4444',    // red-500
      info: '#3b82f6',     // blue-500
    },
    card: {
      background: '#ffffff',
      border: '#f4a3c0',    // soft pink
      hover: '#fde6f0',     // very light pink hover
    },
    input: {
      background: '#ffffff',
      border: '#f4a3c0',    // soft pink
      text: '#1a1a1a',     // dark slate
      placeholder: '#94a3b8', // slate-400
    },
    button: {
      primary: {
        bg: '#f08ab0',      // sakura pink
        text: '#ffffff',
        hover: '#e56a98',   // deeper pink hover
      },
      secondary: {
        bg: '#fde6f0',      // light pink background
        text: '#1a1a1a',    // dark slate
        hover: '#f9cfe0',   // slightly stronger pink
      },
      outline: {
        border: '#f08ab0',  // sakura pink border
        text: '#f08ab0',    // sakura pink text
        hover: '#e56a98',   // deeper pink hover
      },
      ghost: {
        text: '#4a4a4a',     // medium slate
        hover: '#fde6f0',   // light pink hover
      },
    },
  },
  neon: {
    background: {
      primary: '#0b0f1a',   // deep navy
      secondary: '#111827', // slate-900
      tertiary: '#1f2937',  // slate-800
    },
    foreground: {
      primary: '#f8fafc',  // slate-50
      secondary: '#cbd5f5', // cool light
      muted: '#94a3b8',     // slate-400
    },
    border: {
      default: '#22d3ee',   // cyan-400
      hover: '#a855f7',     // purple-500
      focus: '#22d3ee',     // cyan-400
    },
    accent: {
      primary: '#22d3ee',  // cyan-400
      secondary: '#a855f7', // purple-500
      hover: '#f472b6',     // pink-400
    },
    status: {
      success: '#22c55e',  // green-500
      warning: '#f59e0b',  // amber-500
      error: '#ef4444',    // red-500
      info: '#38bdf8',     // sky-400
    },
    card: {
      background: '#0f172a', // slate-900
      border: '#22d3ee',     // cyan-400
      hover: '#111827',      // slate-900
    },
    input: {
      background: '#0f172a', // slate-900
      border: '#22d3ee',     // cyan-400
      text: '#f8fafc',      // slate-50
      placeholder: '#64748b', // slate-500
    },
    button: {
      primary: {
        bg: '#22d3ee',      // cyan-400
        text: '#0b0f1a',    // deep navy
        hover: '#0ea5e9',   // sky-500
      },
      secondary: {
        bg: '#1f2937',      // slate-800
        text: '#f8fafc',    // slate-50
        hover: '#334155',   // slate-700
      },
      outline: {
        border: '#a855f7',  // purple-500
        text: '#a855f7',    // purple-500
        hover: '#f472b6',   // pink-400
      },
      ghost: {
        text: '#cbd5f5',     // cool light
        hover: '#111827',   // slate-900
      },
    },
  },
  nier: {
    background: {
      primary: '#dad4bb',
      secondary: '#e1dbc6',
      tertiary: '#d2c9ab',
    },
    foreground: {
      primary: '#454138',
      secondary: '#5a564b',
      muted: '#7a7464',
    },
    border: {
      default: '#9c9787',
      hover: '#9c9787',
      focus: '#9c9787',
    },
    accent: {
      primary: '#9c9787',
      secondary: '#7a7464',
      hover: '#6f6a5d',
    },
    status: {
      success: '#2f7d5f',
      warning: '#b38a3a',
      error: '#8b4049',
      info: '#4a6a7f',
    },
    card: {
      background: '#e8e4d4',
      border: '#9c9787',
      hover: '#ded7c1',
    },
    input: {
      background: '#c4bea5',
      border: '#9c9787',
      text: '#454138',
      placeholder: '#7a7464',
    },
    button: {
      primary: {
        bg: '#454138',
        text: '#dad4bb',
        hover: '#35312a',
      },
      secondary: {
        bg: '#c4bea5',
        text: '#454138',
        hover: '#b6b09a',
      },
      outline: {
        border: '#9c9787',
        text: '#454138',
        hover: '#6f6a5d',
      },
      ghost: {
        text: '#7a7464',
        hover: '#cfc7ad',
      },
    },
  },
  dark: {
    background: {
      primary: '#0a0a0a',   // very dark gray (slightly lighter than pure black)
      secondary: '#1a1a1a',  // dark gray
      tertiary: '#2a2a2a',   // medium dark gray
    },
    foreground: {
      primary: '#f1f5f9',   // white/light gray
      secondary: '#cbd5e1', // light gray
      muted: '#94a3b8',     // muted gray
    },
    border: {
      default: '#e5e7eb',   // bright whitish gray
      hover: '#f3f4f6',     // lighter gray on hover
      focus: '#e5e7eb',     // bright whitish gray focus
    },
    accent: {
      primary: '#e5e7eb',   // bright whitish gray
      secondary: '#f3f4f6', // lighter gray
      hover: '#d1d5db',     // slightly darker gray on hover
    },
    status: {
      success: '#10b981',   // green-500
      warning: '#f59e0b',   // amber-500
      error: '#ef4444',     // red-500
      info: '#3b82f6',      // blue-500
    },
    card: {
      background: '#0a0a0a', // very dark gray
      border: '#e5e7eb',     // bright whitish gray border
      hover: '#1a1a1a',      // slightly lighter on hover
    },
    input: {
      background: '#0a0a0a', // very dark gray
      border: '#e5e7eb',     // bright whitish gray border
      text: '#f1f5f9',      // white text
      placeholder: '#64748b', // muted gray
    },
    button: {
      primary: {
        bg: '#e5e7eb',      // bright whitish gray button
        text: '#0a0a0a',    // dark text for contrast
        hover: '#d1d5db',   // slightly darker gray on hover
      },
      secondary: {
        bg: '#1a1a1a',      // dark gray
        text: '#f1f5f9',    // white text
        hover: '#2a2a2a',   // lighter gray on hover
      },
      outline: {
        border: '#e5e7eb',  // bright whitish gray border
        text: '#e5e7eb',    // bright whitish gray text
        hover: '#d1d5db',   // slightly darker gray on hover
      },
      ghost: {
        text: '#cbd5e1',    // light gray
        hover: '#1a1a1a',   // dark gray hover
      },
    },
  },
};

export const defaultTheme: Theme = 'light';

