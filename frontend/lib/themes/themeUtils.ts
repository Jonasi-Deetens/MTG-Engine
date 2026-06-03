// Theme utility functions for type-safe color access

import { Theme, ThemeColors, themes } from './themeConfig';

/**
 * Get a theme color by path
 * @param theme - The theme to get colors from
 * @param path - Dot-separated path to the color (e.g., 'background.primary', 'button.primary.bg')
 */
export function getThemeColor(theme: Theme, path: string): string {
  const parts = path.split('.');
  let value: any = themes[theme];
  
  for (const part of parts) {
    if (value && typeof value === 'object' && part in value) {
      value = value[part];
    } else {
      console.warn(`Theme color path not found: ${path}`);
      return '';
    }
  }
  
  return typeof value === 'string' ? value : '';
}

/**
 * Get button variant colors
 */
export function getButtonVariant(theme: Theme, variant: 'primary' | 'secondary' | 'outline' | 'ghost'): {
  bg?: string;
  text: string;
  hover?: string;
  border?: string;
} {
  const buttonColors = themes[theme].button;
  
  switch (variant) {
    case 'primary':
      return {
        bg: buttonColors.primary.bg,
        text: buttonColors.primary.text,
        hover: buttonColors.primary.hover,
      };
    case 'secondary':
      return {
        bg: buttonColors.secondary.bg,
        text: buttonColors.secondary.text,
        hover: buttonColors.secondary.hover,
      };
    case 'outline':
      return {
        text: buttonColors.outline.text,
        border: buttonColors.outline.border,
        hover: buttonColors.outline.hover,
      };
    case 'ghost':
      return {
        text: buttonColors.ghost.text,
        hover: buttonColors.ghost.hover,
      };
    default:
      return {
        text: themes[theme].foreground.primary,
      };
  }
}

/**
 * Get card variant colors
 */
export function getCardVariant(theme: Theme, variant: 'default' | 'elevated' | 'bordered' = 'default'): {
  bg: string;
  border: string;
  hover?: string;
} {
  const cardColors = themes[theme].card;
  
  switch (variant) {
    case 'elevated':
      return {
        bg: cardColors.background,
        border: cardColors.border,
        hover: cardColors.hover,
      };
    case 'bordered':
      return {
        bg: cardColors.background,
        border: cardColors.border,
      };
    default:
      return {
        bg: cardColors.background,
        border: cardColors.border,
      };
  }
}

/**
 * Get status color
 */
export function getStatusColor(theme: Theme, status: 'success' | 'warning' | 'error' | 'info'): string {
  return themes[theme].status[status];
}

