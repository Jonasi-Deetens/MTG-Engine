// Theme configuration system
// Defines semantic color structure for all themes

export type Theme = 'light' | 'dark' | 'angel';

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
      primary: '#ffffff',
      secondary: '#f8f9fa',
      tertiary: '#f1f3f5',
    },
    foreground: {
      primary: '#1e293b',    // slate-800
      secondary: '#475569',  // slate-600
      muted: '#64748b',      // slate-500
    },
    border: {
      default: '#e2e8f0',    // slate-200
      hover: '#cbd5e1',     // slate-300
      focus: '#f59e0b',     // amber-500
    },
    accent: {
      primary: '#f59e0b',   // amber-500
      secondary: '#fbbf24', // amber-400
      hover: '#d97706',     // amber-600
    },
    status: {
      success: '#10b981',   // green-500
      warning: '#f59e0b',   // amber-500
      error: '#ef4444',     // red-500
      info: '#3b82f6',      // blue-500
    },
    card: {
      background: '#ffffff',
      border: '#e2e8f0',    // slate-200
      hover: '#f1f5f9',     // slate-100
    },
    input: {
      background: '#ffffff',
      border: '#e2e8f0',    // slate-200
      text: '#1e293b',      // slate-800
      placeholder: '#94a3b8', // slate-400
    },
    button: {
      primary: {
        bg: '#f59e0b',      // amber-500 - only for primary actions
        text: '#ffffff',
        hover: '#d97706',   // amber-600
      },
      secondary: {
        bg: '#f1f5f9',      // slate-100 - neutral background
        text: '#1e293b',    // slate-800
        hover: '#e2e8f0',   // slate-200 - neutral hover
      },
      outline: {
        border: '#e2e8f0',  // slate-200 - neutral border
        text: '#475569',    // slate-600 - neutral text
        hover: '#f1f5f9',   // slate-100 - neutral hover
      },
      ghost: {
        text: '#475569',    // slate-600
        hover: '#f1f5f9',   // slate-100
      },
    },
  },
  dark: {
    background: {
      primary: '#0f172a',   // slate-900
      secondary: '#1e293b', // slate-800
      tertiary: '#334155',  // slate-700
    },
    foreground: {
      primary: '#f1f5f9',   // slate-100
      secondary: '#cbd5e1', // slate-300
      muted: '#94a3b8',     // slate-400
    },
    border: {
      default: '#334155',   // slate-700
      hover: '#475569',     // slate-600
      focus: '#f59e0b',     // amber-500
    },
    accent: {
      primary: '#f59e0b',   // amber-500
      secondary: '#fbbf24', // amber-400
      hover: '#fcd34d',     // amber-300
    },
    status: {
      success: '#10b981',   // green-500
      warning: '#f59e0b',   // amber-500
      error: '#ef4444',     // red-500
      info: '#3b82f6',      // blue-500
    },
    card: {
      background: '#1e293b', // slate-800
      border: '#334155',     // slate-700
      hover: '#334155',     // slate-700
    },
    input: {
      background: '#1e293b', // slate-800
      border: '#334155',     // slate-700
      text: '#f1f5f9',      // slate-100
      placeholder: '#64748b', // slate-500
    },
    button: {
      primary: {
        bg: '#f59e0b',      // amber-500
        text: '#ffffff',
        hover: '#d97706',   // amber-600
      },
      secondary: {
        bg: '#334155',      // slate-700
        text: '#f1f5f9',    // slate-100
        hover: '#475569',   // slate-600
      },
      outline: {
        border: '#f59e0b',  // amber-500
        text: '#f59e0b',    // amber-500
        hover: '#f59e0b',   // amber-500
      },
      ghost: {
        text: '#cbd5e1',    // slate-300
        hover: '#334155',   // slate-700
      },
    },
  },
  angel: {
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
};

export const defaultTheme: Theme = 'angel';

