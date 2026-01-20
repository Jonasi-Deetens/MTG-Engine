// Hook for using theme-based images with automatic fallback

import { useState, useEffect } from 'react';
import { getThemeImage } from '@/lib/utils/themeImages';
import { Theme, defaultTheme } from '@/lib/themes/themeConfig';

type ThemeWithLegacy = Theme | 'angel';

/**
 * Hook to get theme-based image with automatic fallback
 * Listens to theme changes via data-theme attribute on document
 * @param imageName - Base name of the image (e.g., 'home', 'logo')
 * @param extension - File extension (default: 'png')
 * @returns Current image path (theme-specific if exists, otherwise fallback)
 */
export function useThemeImage(
  imageName: string,
  extension: string = 'png'
): string {
  // Helper function to get current theme
  const getCurrentTheme = (): Theme => {
    if (typeof document !== 'undefined') {
      const dataTheme = document.documentElement.getAttribute('data-theme') as ThemeWithLegacy | null;
      // Migrate 'angel' to 'light' if found
      if (dataTheme === 'angel') {
        return 'light';
      }
      if (dataTheme && ['light', 'sakura', 'neon', 'dark'].includes(dataTheme)) {
        return dataTheme;
      }
    }
    if (typeof window !== 'undefined') {
      try {
        const storedTheme = localStorage.getItem('mtg-engine-theme') as ThemeWithLegacy | null;
        // Migrate 'angel' to 'light' if found
        if (storedTheme === 'angel') {
          return 'light';
        }
        const availableThemes: Theme[] = ['light', 'sakura', 'neon', 'dark'];
        if (storedTheme && availableThemes.includes(storedTheme)) {
          return storedTheme;
        }
      } catch (e) {
        // Ignore
      }
    }
    return defaultTheme;
  };

  // Use default theme during SSR/first render to avoid hydration mismatch
  const [imagePath, setImagePath] = useState(() =>
    getThemeImage(imageName, defaultTheme, extension)
  );
  const [currentTheme, setCurrentTheme] = useState<Theme>(defaultTheme);

  // Get initial theme from document or localStorage and update image immediately
  useEffect(() => {
    const initialTheme = getCurrentTheme();
    setCurrentTheme(initialTheme);
    
    // Immediately update image path if it's different
    const initialImagePath = getThemeImage(imageName, initialTheme, extension);
    if (imagePath !== initialImagePath) {
      setImagePath(initialImagePath);
    }

    // Listen to data-theme attribute changes (MutationObserver)
    if (typeof document !== 'undefined') {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
            const newTheme = document.documentElement.getAttribute('data-theme') as ThemeWithLegacy | null;
            // Migrate 'angel' to 'light' if found
            if (newTheme === 'angel') {
              setCurrentTheme('light');
            } else if (newTheme && ['light', 'sakura', 'neon', 'dark'].includes(newTheme)) {
              setCurrentTheme(newTheme);
            }
          }
        });
      });

      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme'],
      });

      // Also listen to storage events (when theme changes in another tab/window)
      const handleStorageChange = (e: StorageEvent) => {
        if (e.key === 'mtg-engine-theme' && e.newValue) {
          const newTheme = e.newValue as ThemeWithLegacy;
          // Migrate 'angel' to 'light' if found
          if (newTheme === 'angel') {
            setCurrentTheme('light');
          } else if (['light', 'sakura', 'neon', 'dark'].includes(newTheme)) {
            setCurrentTheme(newTheme);
          }
        }
      };

      window.addEventListener('storage', handleStorageChange);

      return () => {
        observer.disconnect();
        window.removeEventListener('storage', handleStorageChange);
      };
    }
  }, []);

  // Update image when theme changes (only when theme actually changes)
  useEffect(() => {
    // Get theme-specific image path
    const themeImage = getThemeImage(imageName, currentTheme, extension);
    
    // Always update to match current theme (handles navigation back to page)
    if (imagePath !== themeImage) {
      // Preload the new image before switching to prevent flickering
      const img = new Image();
      let cancelled = false;
      
      img.onload = () => {
        if (!cancelled) {
          setImagePath(themeImage);
        }
      };
      img.onerror = () => {
        // Theme-specific image doesn't exist, but still use theme-specific path
        // This prevents flickering - let browser handle 404 gracefully
        if (!cancelled) {
          setImagePath(themeImage);
        }
      };
      img.src = themeImage;
      
      return () => {
        cancelled = true;
      };
    }
  }, [currentTheme, imageName, extension, imagePath]);

  return imagePath;
}

