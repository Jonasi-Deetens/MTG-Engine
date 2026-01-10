'use client';

// Theme context for managing theme state across the application

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { Theme, defaultTheme } from '@/lib/themes/themeConfig';

interface ThemeContextType {
  currentTheme: Theme;
  setTheme: (theme: Theme) => void;
  availableThemes: Theme[];
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = 'mtg-engine-theme';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [currentTheme, setCurrentThemeState] = useState<Theme>(defaultTheme);
  const [mounted, setMounted] = useState(false);

  const availableThemes: Theme[] = ['light', 'dark', 'angel'];

  // Apply theme to document
  const applyTheme = useCallback((theme: Theme) => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', theme);
    }
  }, []);

  // Load theme from localStorage or use default - apply immediately to prevent flash
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedTheme = localStorage.getItem(THEME_STORAGE_KEY) as Theme | null;
      const initialTheme = storedTheme && availableThemes.includes(storedTheme) 
        ? storedTheme 
        : defaultTheme;
      
      // Apply theme immediately before React renders to prevent flash
      applyTheme(initialTheme);
      setCurrentThemeState(initialTheme);
      setMounted(true);
    }
  }, [applyTheme, availableThemes]);

  // Set theme and persist to localStorage
  const setTheme = useCallback((theme: Theme) => {
    if (availableThemes.includes(theme)) {
      setCurrentThemeState(theme);
      applyTheme(theme);
      if (typeof window !== 'undefined') {
        localStorage.setItem(THEME_STORAGE_KEY, theme);
      }
    }
  }, [availableThemes, applyTheme]);

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return <>{children}</>;
  }

  return (
    <ThemeContext.Provider
      value={{
        currentTheme,
        setTheme,
        availableThemes,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

