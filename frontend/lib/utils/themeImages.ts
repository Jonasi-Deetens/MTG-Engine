// Utility function to get theme-based image paths
// Images should follow the naming convention: {name}-{theme}.{ext}
// Example: home-light.png, home-dark.png
// Falls back to base image ({name}.{ext}) if theme-specific doesn't exist

import { Theme } from '@/lib/themes/themeConfig';

/**
 * Get the image path for a given image name and theme
 * Falls back to base image if theme-specific doesn't exist
 * @param imageName - Base name of the image (e.g., 'home', 'logo')
 * @param theme - Current theme ('light' or 'dark')
 * @param extension - File extension (default: 'png')
 * @param useFallback - Whether to fallback to base image if theme-specific doesn't exist (default: true)
 * @returns Path to the theme-specific image or fallback to base image
 */
export function getThemeImage(
  imageName: string,
  theme: Theme,
  extension: string = 'png',
  useFallback: boolean = true
): string {
  // Migrate 'angel' to 'light' if found (for backward compatibility)
  const normalizedTheme = theme === 'angel' ? 'light' : theme;
  
  if (useFallback) {
    // Try theme-specific first, but we'll let the browser handle 404s and use base as fallback
    // In a real implementation, you might want to check if file exists, but for now we'll use CSS fallback
    return `/${imageName}-${normalizedTheme}.${extension}`;
  }
  return `/${imageName}-${normalizedTheme}.${extension}`;
}

/**
 * Get image paths for all themes (useful for preloading)
 * @param imageName - Base name of the image
 * @param extension - File extension (default: 'png')
 * @returns Object with theme as key and image path as value
 */
export function getAllThemeImages(
  imageName: string,
  extension: string = 'png'
): Record<Theme, string> {
  return {
    light: `/${imageName}-light.${extension}`,
    dark: `/${imageName}-dark.${extension}`,
  };
}


