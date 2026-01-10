'use client';

// Theme switcher component for user theme selection

import { useTheme } from '@/context/ThemeContext';
import { Theme } from '@/lib/themes/themeConfig';
import { Moon, Sun } from 'lucide-react';
import { Select, SelectOption } from './Select';

const themeIcons: Record<Theme, React.ComponentType<{ className?: string }>> = {
  light: Sun,
  dark: Moon,
};

const themeLabels: Record<Theme, string> = {
  light: 'Light',
  dark: 'Dark',
};

export function ThemeSwitcher() {
  const { currentTheme, setTheme, availableThemes } = useTheme();

  const options: SelectOption[] = availableThemes.map((theme) => ({
    value: theme,
    label: themeLabels[theme],
    icon: themeIcons[theme],
  }));

  return (
    <Select
      options={options}
      value={currentTheme}
      onChange={(value) => setTheme(value as Theme)}
      placeholder="Select theme"
      className="w-full"
    />
  );
}

