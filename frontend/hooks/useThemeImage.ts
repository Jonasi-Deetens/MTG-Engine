// Hook for using theme-based images with automatic fallback

import { useState, useEffect } from 'react';
import { getThemeImage } from '@/lib/utils/themeImages';
import { Theme, defaultTheme } from '@/lib/themes/themeConfig';

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
  // Initialize with theme-specific image path immediately
  const getInitialImagePath = (): string => {
    if (typeof document !== 'undefined') {
      const dataTheme = document.documentElement.getAttribute('data-theme') as Theme | null;
      let theme: Theme = defaultTheme;
      if (dataTheme === 'angel') {
        theme = 'light';
      } else if (dataTheme && ['light', 'dark'].includes(dataTheme)) {
        theme = dataTheme;
      } else if (typeof window !== 'undefined') {
        try {
          const storedTheme = localStorage.getItem('mtg-engine-theme') as Theme | null;
          if (storedTheme === 'angel') {
            theme = 'light';
          } else if (storedTheme && ['light', 'dark'].includes(storedTheme)) {
            theme = storedTheme;
          }
        } catch (e) {
          // Ignore
        }
      }
      return getThemeImage(imageName, theme, extension);
    }
    return getThemeImage(imageName, defaultTheme, extension);
  };

  const [imagePath, setImagePath] = useState(getInitialImagePath);
  const [currentTheme, setCurrentTheme] = useState<Theme>(defaultTheme);

  // Get initial theme from document or localStorage
  useEffect(() => {
    const getCurrentTheme = (): Theme => {
      if (typeof document !== 'undefined') {
        const dataTheme = document.documentElement.getAttribute('data-theme') as Theme | null;
        // Migrate 'angel' to 'light' if found
        if (dataTheme === 'angel') {
          return 'light';
        }
        if (dataTheme && ['light', 'dark'].includes(dataTheme)) {
          return dataTheme;
        }
      }
      if (typeof window !== 'undefined') {
        try {
          const storedTheme = localStorage.getItem('mtg-engine-theme') as Theme | null;
          // Migrate 'angel' to 'light' if found
          if (storedTheme === 'angel') {
            return 'light';
          }
          const availableThemes: Theme[] = ['light', 'dark'];
          if (storedTheme && availableThemes.includes(storedTheme)) {
            return storedTheme;
          }
        } catch (e) {
          // Ignore
        }
      }
      return defaultTheme;
    };

    const initialTheme = getCurrentTheme();
    setCurrentTheme(initialTheme);

    // Listen to data-theme attribute changes (MutationObserver)
    if (typeof document !== 'undefined') {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
            const newTheme = document.documentElement.getAttribute('data-theme') as Theme | null;
            // Migrate 'angel' to 'light' if found
            if (newTheme === 'angel') {
              setCurrentTheme('light');
            } else if (newTheme && ['light', 'dark'].includes(newTheme)) {
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
          const newTheme = e.newValue as Theme;
          // Migrate 'angel' to 'light' if found
          if (newTheme === 'angel') {
            setCurrentTheme('light');
          } else if (['light', 'dark'].includes(newTheme)) {
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
    
    // Only update if the path actually changed to prevent unnecessary reloads
    if (imagePath !== themeImage) {
      // Preload the new image before switching to prevent flickering
      const img = new Image();
      img.onload = () => {
        // Only update if theme hasn't changed while loading
        setImagePath((prevPath) => {
          const currentThemeImage = getThemeImage(imageName, currentTheme, extension);
          return currentThemeImage === themeImage ? themeImage : prevPath;
        });
      };
      img.onerror = () => {
        // Theme-specific image doesn't exist, but still use theme-specific path
        // This prevents flickering - let browser handle 404 gracefully
        setImagePath((prevPath) => {
          const currentThemeImage = getThemeImage(imageName, currentTheme, extension);
          return currentThemeImage === themeImage ? themeImage : prevPath;
        });
      };
      img.src = themeImage;
    }
  }, [currentTheme, imageName, extension]);

  return imagePath;
}

