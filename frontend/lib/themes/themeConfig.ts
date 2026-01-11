// Theme configuration system
// Defines semantic color structure for all themes

export type Theme = 'light' | 'dark';

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

