'use client';

// Theme switcher component for user theme selection

import { useTheme } from '@/context/ThemeContext';
import { Theme } from '@/lib/themes/themeConfig';
import { Moon, Sun, Sparkles } from 'lucide-react';

const themeIcons: Record<Theme, React.ComponentType<{ className?: string }>> = {
  light: Sun,
  dark: Moon,
  angel: Sparkles,
};

const themeLabels: Record<Theme, string> = {
  light: 'Light',
  dark: 'Dark',
  angel: 'Angel',
};

export function ThemeSwitcher() {
  const { currentTheme, setTheme, availableThemes } = useTheme();

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-[color:var(--theme-text-secondary)] mr-2">Theme:</span>
      <div className="flex gap-1 bg-[color:var(--theme-bg-secondary)] rounded-lg p-1 border border-[color:var(--theme-border-default)]">
        {availableThemes.map((theme) => {
          const Icon = themeIcons[theme];
          const isActive = currentTheme === theme;
          
          return (
            <button
              key={theme}
              onClick={() => setTheme(theme)}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors cursor-pointer
                ${isActive 
                  ? 'bg-[color:var(--theme-accent-primary)] text-white' 
                  : 'text-[color:var(--theme-text-secondary)] hover:bg-[color:var(--theme-card-hover)] hover:text-[color:var(--theme-text-primary)]'
                }
              `}
              title={`Switch to ${themeLabels[theme]} theme`}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{themeLabels[theme]}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

